from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
from dotenv import load_dotenv
from ranking_utils import rank_candidates, DATA_PATH
from generate_data import sync_csv_with_appwrite
from os.path import join, dirname
from generate_data import generate_and_sync
from appwrite.query import Query 
from eda import run_generate_plots
from export_powerbi import generate_powerbi_csv
import os
import traceback
import csv
import unicodedata

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "candidatos.csv")


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def index():
    return render_template('index.html')

load_dotenv()

required_env_vars = ["APPWRITE_ENDPOINT", "APPWRITE_PROJECT_ID", "APPWRITE_API_KEY", "DATABASE_ID", "COLLECTION_ID"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise EnvironmentError(f"Faltan variables de entorno: {', '.join(missing_vars)}")

client = Client()
client.set_endpoint(os.getenv("APPWRITE_ENDPOINT"))
client.set_project(os.getenv("APPWRITE_PROJECT_ID"))
client.set_key(os.getenv("APPWRITE_API_KEY"))

database = Databases(client)
database_id = os.getenv("DATABASE_ID")
collection_id = os.getenv("COLLECTION_ID")

def normalize_text(text):
    if not isinstance(text, str):
        return text
    text = text.lower().strip()
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    return text

def map_education_level(level):
    education_map = {
        "1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
        "secundaria": 1, "tecnico": 2, "tecnologo": 3, "universitario": 4, "postgrado": 5
    }
    return education_map.get(str(level), 0)

def map_gender(gender):
    gender_map = {
        "masculino": 1,
        "femenino": 2,
        "otro": 3
    }
    return gender_map.get(normalize_text(gender), 0)

def map_availability(avail):
    availability_map = {
        "completo": 1,
        "parcial": 2,
        "flexible": 3
    }
    return availability_map.get(normalize_text(avail), 0)

def map_work_preference(pref):
    preference_map = {
        "remoto": 1,
        "hibrido": 2,
        "presencial": 3
    }
    return preference_map.get(normalize_text(pref), 0)

@app.route("/add_candidate", methods=["POST"])
def add_candidate():
    try:
        data = request.json

        print("🔹 Claves recibidas:", data.keys())
        print("Datos recibidos:", data)

        required_fields = [
            "firstName", "lastName", "email", "phoneNumber", "gender", "birthDate",
            "educationLevel", "interviewScore", "technicalTestScore", "availability",
            "salaryExpectation", "location", "experience",
            "workPreference", "icfes"
        ]

        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        if missing_fields:
            return jsonify({"error": f"Faltan datos requeridos: {', '.join(missing_fields)}"}), 400

        normalized_data = {
            "first_name": normalize_text(data["firstName"]),
            "last_name": normalize_text(data["lastName"]),
            "email": data["email"],
            "phone_number": data["phoneNumber"],
            "birth_date": data["birthDate"],
            "education_level": str(map_education_level(data["educationLevel"])),
            "technical_skills": data.get("technicalSkills", []),
            "interview_score": data["interviewScore"],
            "technical_test_score": data["technicalTestScore"],
            "salary_expectation": data["salaryExpectation"],
            "location": normalize_text(data["location"]),
            "experience": data["experience"],
            "soft_skills": data.get("softSkills", []),
            "languages": data.get("languages", []),
            "gender": str(map_gender(data["gender"])),
            "availability": str(map_availability(data["availability"])),
            "work_preference": str(map_work_preference(data["workPreference"])),
            "career_interest": data.get("careerInterest", ""),
            "personal_strengths": data.get("personalStrengths", []),
            "short_term_goal": data.get("shortTermGoal", ""),
            "icfes": data["icfes"]            

        }

        existing_candidates = database.list_documents(database_id=database_id, collection_id=collection_id)
        for candidate in existing_candidates["documents"]:
            if candidate.get("email") == normalized_data["email"] or candidate.get("phone_number") == normalized_data["phone_number"]:
                return jsonify({"error": "El candidato ya está registrado con este correo electrónico o número de celular"}), 400

        document = database.create_document(
            database_id=database_id,
            collection_id=collection_id,
            document_id=ID.unique(),
            data=normalized_data
        )

        sync_csv_with_appwrite()
        actualizar_puntaje_total_csv()
        generate_powerbi_csv()
        run_generate_plots()


        return jsonify({"message": "Candidato agregado", "document": document}), 201

    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ ERROR en /add_candidate: {error_trace}")
        return jsonify({"error": "Error interno del servidor", "details": str(e)}), 500

@app.route("/export_candidates", methods=["GET"])
def export_candidates():
    try:
        candidates = []
        queries = []
        page = 0
        limit = 100
        while True:
            documents = database.list_documents(database_id=database_id, collection_id=collection_id, queries=queries)
            candidates.extend(documents["documents"])
            if len(documents["documents"]) < limit:
                break
            page += 1

        csv_filename = os.path.join(os.path.dirname(__file__), "candidatos.csv")

        with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            headers = [
                "first_name", "last_name", "email", "phone_number", "gender", "birth_date", "education_level",
                "technical_skills", "interview_score", "technical_test_score", "availability", "salary_expectation", "location", "experience", "soft_skills", "languages", "work_preference", "icfes",
                "career_interest", "personal_strengths", "short_term_goal"
            ]
            writer.writerow(headers)

            for candidate in candidates:
                writer.writerow([
                    candidate.get("first_name", ""), candidate.get("last_name", ""), candidate.get("email", ""),
                    candidate.get("phone_number", ""), candidate.get("gender", ""), candidate.get("birth_date", ""),
                    candidate.get("education_level", ""), ", ".join(candidate.get("technical_skills", [])),
                    candidate.get("interview_score", ""), candidate.get("technical_test_score", ""),
                    candidate.get("availability", ""), candidate.get("salary_expectation", ""),
                    candidate.get("location", ""), candidate.get("icfes", ""),
                    candidate.get("experience", ""), ", ".join(candidate.get("soft_skills", [])),", ".join(candidate.get("languages", [])),
                    candidate.get("work_preference", ""), candidate.get("career_interest", ""),
                    ", ".join(candidate.get("personal_strengths", [])), candidate.get("short_term_goal", "")
                ])

        return send_file(csv_filename, as_attachment=True)
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ ERROR en /export_candidates: {error_trace}")
        return jsonify({"error": "Error al exportar candidatos", "details": str(e)}), 500

@app.route("/mejor_candidato", methods=["GET"])
def get_best_candidate():
    try:
        df = rank_candidates(join(dirname(__file__), "data", "candidatos.csv"))        
        best = df.iloc[0].fillna("").to_dict()  # <-- ESTE CAMBIO evita errores de NaN
        return jsonify({"mejor_candidato": best}), 200
    except Exception as e:
        return jsonify({"error": "Error al procesar ranking", "details": str(e)}), 500

@app.route("/ranking")
def ranking_page():
    try:
        df = rank_candidates(DATA_PATH)        
        df.fillna("", inplace=True)
        # top_candidates = df.to_dict(orient="records")
        top_candidates = df.head(10).to_dict(orient="records") # solo modificar el parentesis en caso de querer ver mas candidatos
        return render_template("ranking.html", candidates=top_candidates)
    except Exception as e:
        return f"<h1>Error al cargar ranking</h1><p>{e}</p>" 

@app.route("/generar_datos", methods=["POST"])
def generar_datos():
    try:
        generate_and_sync(n=10)         # 1. Generar e insertar candidatos
        sync_csv_with_appwrite()        # 2. Traer datos actualizados de Appwrite
        generate_powerbi_csv()
        actualizar_puntaje_total_csv()  # 3. Calcular puntaje y ordenar ranking
        run_generate_plots()
        return jsonify({"message": "✅ Datos generados y ranking actualizado"}), 200
    except Exception as e:
        return jsonify({"error": f"❌ Error al generar datos: {str(e)}"}), 500



@app.route("/admin")
def admin_page():
    return render_template("admin.html")


@app.route("/api/ranking")
def api_ranking():
    try:
        page = int(request.args.get("page", 1))
        per_page = 50
        df = rank_candidates("data/candidatos.csv")
        df = df.sort_values("total_score", ascending=False).reset_index(drop=True)

        start = (page - 1) * per_page
        end = start + per_page
        total_pages = (len(df) + per_page - 1) // per_page

        candidates = df.iloc[start:end].to_dict(orient="records")

        return jsonify({
            "page": page,
            "total_pages": total_pages,
            "candidates": candidates
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/actualizar_ranking", methods=["GET"])
def actualizar_ranking():
    try:
        sync_csv_with_appwrite()        # 1. Descargar últimos datos desde Appwrite
        actualizar_puntaje_total_csv()  # 2. Calcular puntaje_total y reordenar
        run_generate_plots()
        print("✅ Ranking actualizado correctamente.")
        return jsonify({"message": "Ranking actualizado correctamente"}), 200
    except Exception as e:
        print(f"❌ Error al actualizar el ranking: {str(e)}")
        return jsonify({"error": "Error al actualizar el ranking", "details": str(e)}), 500

def actualizar_puntaje_total_csv():
    import pandas as pd

    df = pd.read_csv(DATA_PATH)
    df["puntaje_total"] = (
        df["interview_score"] * 0.4 +
        df["technical_test_score"] * 0.4 +
        df["soft_skills"].apply(lambda x: len(x) if isinstance(x, list) else 0) * 0.2
    )
    df = df.sort_values(by="puntaje_total", ascending=False)
    df.to_csv(DATA_PATH, index=False)
    print("✅ puntaje_total actualizado en candidatos.csv")


@app.route("/actualizar_plots", methods=["POST"])
def actualizar_plots():
    try:        
        sync_csv_with_appwrite()
        actualizar_puntaje_total_csv()
        run_generate_plots()
        print("✅ Plots actualizados con éxito")
        return jsonify({"message": "✅ Plots actualizados con éxito"}), 200
    except Exception as e:
        return jsonify({"error": f"❌ Error al actualizar plots: {str(e)}"}), 500


@app.route("/eda")
def eda_summary():
    import eda  # asegúrate de tener eda.py en el mismo nivel que app.py
    head, types, missing, describe = eda.get_eda_dataframes()

    return render_template("eda.html", head=head.to_dict(orient="records"),
                                         types=types.to_dict(orient="records"),
                                         missing=missing.to_dict(orient="records"),
                                         describe=describe.to_dict(orient="records"))


@app.route("/eda/plots")
def eda_plots():
    plot_files = os.listdir(os.path.join(app.static_folder, "plots"))
    plot_files = [f for f in plot_files if f.endswith(".png")]
    return render_template("eda_plots.html", plots=plot_files)


@app.route("/verificar_existencia", methods=["POST"])
def verificar_existencia():
    try:
        data = request.get_json()
        email = data.get("email")
        phone = data.get("phoneNumber")

        queries = []
        if email:
            queries.append(Query.equal("email", email))
        if phone:
            queries.append(Query.equal("phone_number", phone))

        existing_docs = database.list_documents(
            database_id=database_id,
            collection_id=collection_id,
            queries=queries
        )

        emailExiste = any(doc.get("email") == email for doc in existing_docs["documents"])
        telefonoExiste = any(doc.get("phone_number") == phone for doc in existing_docs["documents"])

        return jsonify({
            "emailExiste": emailExiste,
            "telefonoExiste": telefonoExiste
        })

    except Exception as e:
        print(f"❌ Error al verificar existencia: {e}")
        return jsonify({"error": "Error al verificar existencia"}), 500

@app.route("/descargar_powerbi")
def descargar_powerbi():
    # from export_powerbi import generate_powerbi_csv
    # from flask import send_file
    # import os

    generate_powerbi_csv()

    powerbi_csv = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "candidatos_powerbi.csv")

    if not os.path.exists(powerbi_csv):
        return "❌ El archivo candidatos_powerbi.csv no fue generado correctamente.", 500

    return send_file(powerbi_csv, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)





















