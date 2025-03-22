from flask import Flask, request, jsonify, send_file
from flask_cors import CORS  # Importar CORS
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
from dotenv import load_dotenv
import os
import traceback  # Para capturar errores detallados
import csv
import unicodedata

# Cargar variables de entorno
load_dotenv()

# Verificar si las variables de entorno están configuradas
required_env_vars = ["APPWRITE_ENDPOINT", "APPWRITE_PROJECT_ID", "APPWRITE_API_KEY", "DATABASE_ID", "COLLECTION_ID"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise EnvironmentError(f"Faltan variables de entorno: {', '.join(missing_vars)}")

# Configurar Appwrite
client = Client()
client.set_endpoint(os.getenv("APPWRITE_ENDPOINT"))
client.set_project(os.getenv("APPWRITE_PROJECT_ID"))
client.set_key(os.getenv("APPWRITE_API_KEY"))

database = Databases(client)
database_id = os.getenv("DATABASE_ID")
collection_id = os.getenv("COLLECTION_ID")

# Inicializar Flask
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Permitir todas las peticiones

def normalize_text(text):
    if not isinstance(text, str):
        return text
    text = text.lower().strip()
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    return text

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API de Gestión de Candidatos está funcionando"}), 200

def map_education_level(level):
    education_map = {
        "1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
        "secundaria": 1, "tecnico": 2, "tecnologo": 3, "universitario": 4, "postgrado": 5
    }
    return education_map.get(str(level), 0)  # Convertimos a string para asegurar coincidencia

@app.route("/add_candidate", methods=["POST"])
def add_candidate():
    try:
        data = request.json  # Obtener datos del formulario
        
        print("🔹 Claves recibidas:", data.keys())  # Debugging adicional
        print("Datos recibidos:", data)  # Agregar print para depuración
        
        if not data:
            return jsonify({"error": "El cuerpo de la solicitud está vacío"}), 400
        
        required_fields = ["firstName", "lastName", "email", "phoneNumber", "gender", "birthDate", "educationLevel", "interviewScore", "technicalTestScore", "availability", "salaryExpectation", "companyInterest", "location", "experience", "workPreference"]
        
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        if missing_fields:
            return jsonify({"error": f"Faltan datos requeridos: {', '.join(missing_fields)}"}), 400
        
        print("🔹 Valor recibido de educationLevel:", data["educationLevel"])

        # Normalizar claves del diccionario
        normalized_data = {
            "first_name": normalize_text(data["firstName"]),
            "last_name": normalize_text(data["lastName"]),
            "email": data["email"],
            "phone_number": data["phoneNumber"],
            "gender": data["gender"],
            "birth_date": data["birthDate"],
            "education_level": str(map_education_level(data["educationLevel"])),
            "technical_skills": data.get("technicalSkills", []),
            "interview_score": data["interviewScore"],
            "technical_test_score": data["technicalTestScore"],
            "availability": data["availability"],
            "salary_expectation": data["salaryExpectation"],
            "company_interest": data["companyInterest"],
            "location": normalize_text(data["location"]),
            "experience": data["experience"],
            "soft_skills": data.get("softSkills", []),
            "work_preference": data["workPreference"]
        }
        
        # Verificar si el email o el número de celular ya existen en la base de datos
        existing_candidates = database.list_documents(database_id=database_id, collection_id=collection_id)
        for candidate in existing_candidates["documents"]:
            if candidate.get("email") == normalized_data["email"] or candidate.get("phone_number") == normalized_data["phone_number"]:
                return jsonify({"error": "El candidato ya está registrado con este correo electrónico o número de celular"}), 400

        # Insertar en Appwrite
        document = database.create_document(
            database_id=database_id,
            collection_id=collection_id,
            document_id=ID.unique(),
            data=normalized_data
        )

        return jsonify({"message": "Candidato agregado", "document": document}), 201

    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ ERROR en /add_candidate: {error_trace}")
        return jsonify({"error": "Error interno del servidor", "details": str(e)}), 500

@app.route("/export_candidates", methods=["GET"])
def export_candidates():
    try:
        # Obtener todos los documentos de Appwrite con paginación
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

        # Definir nombre del archivo CSV en la misma carpeta del script
        csv_filename = os.path.join(os.path.dirname(__file__), "candidatos.csv")
        
        # Guardar en un archivo CSV
        with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            
            # Escribir encabezados
            headers = ["first_name", "last_name", "email", "phone_number", "gender", "birth_date", "education_level", "technical_skills", "interview_score", "technical_test_score", "availability", "salary_expectation", "company_interest", "location", "experience", "soft_skills", "work_preference"]
            writer.writerow(headers)
            
            # Escribir filas con datos de candidatos
            for candidate in candidates:
                writer.writerow([
                    candidate.get("first_name", ""), candidate.get("last_name", ""), candidate.get("email", ""), candidate.get("phone_number", ""), candidate.get("gender", ""),
                    candidate.get("birth_date", ""), candidate.get("education_level", ""), ", ".join(candidate.get("technical_skills", [])), candidate.get("interview_score", ""), candidate.get("technical_test_score", ""), 
                    candidate.get("availability", ""), candidate.get("salary_expectation", ""), candidate.get("company_interest", ""), 
                    candidate.get("location", ""), candidate.get("experience", ""), ", ".join(candidate.get("soft_skills", [])), 
                    candidate.get("work_preference", "")
                ])
        
        return send_file(csv_filename, as_attachment=True)
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ ERROR en /export_candidates: {error_trace}")
        return jsonify({"error": "Error al exportar candidatos", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)










