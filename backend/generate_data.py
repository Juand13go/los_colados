import os
import random
import pandas as pd
from faker import Faker
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite_config import (
    APPWRITE_ENDPOINT, APPWRITE_PROJECT_ID, APPWRITE_API_KEY,
    DATABASE_ID, COLLECTION_ID
)
from appwrite.id import ID
from appwrite.query import Query
from export_powerbi import generate_powerbi_csv

fake = Faker()
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "candidatos.csv")

# Configurar Appwrite
client = Client()
client.set_endpoint(APPWRITE_ENDPOINT)
client.set_project(APPWRITE_PROJECT_ID)
client.set_key(APPWRITE_API_KEY)
database = Databases(client)

TECH_SKILLS = [
    "Python", "JavaScript", "TypeScript", "Java", "C#", "Go", "HTML", "CSS",
    "React", "Vue.js", "Angular", "Tailwind CSS", "Flask", "Django", "Node.js",
    "Express.js", "Spring Boot", "MySQL", "PostgreSQL", "MongoDB", "Firebase",
    "Git", "Docker", "GitHub Actions", "Jenkins", "Linux", "AWS", "GCP", "Azure",
    "REST API", "GraphQL", "Scrum", "Testing"
]
SOFT_SKILLS = [
    "Comunicación", "Trabajo en equipo", "Adaptabilidad", "Creatividad", "Liderazgo", "Empatía",
    "Resolución de conflictos", "Pensamiento crítico", "Toma de decisiones", "Gestión del tiempo",
    "Escucha activa", "Negociación", "Ética profesional"
]
STRENGTHS = [
    "Liderazgo", "Pensamiento Crítico", "Adaptabilidad", "Organización", "Empatía", "Autonomía",
    "Proactividad", "Comunicación", "Resiliencia", "Curiosidad", "Responsabilidad",
    "Orientación a resultados", "Capacidad de aprendizaje", "Perseverancia", "Visión estratégica", "Compromiso"
]
LANGUAGES = ["Inglés", "Español", "Francés", "Alemán", "Portugués"]
CAREER_INTERESTS = ["backend", "frontend", "datascience", "devops", "project", "design"]
SHORT_TERM_GOALS = ["lider_equipo", "especialista", "cambio_area", "crecer_empresa", "emprender"]

GENDERS = [("masculino", 1), ("femenino", 2), ("otro", 3)]
EDUCATION_LEVELS = [("secundaria", 1), ("tecnico", 2), ("tecnologo", 3), ("universitario", 4), ("postgrado", 5)]
AVAILABILITY = [("completo", 1), ("parcial", 2), ("flexible", 3)]
WORK_PREFERENCES = [("remoto", 1), ("hibrido", 2), ("presencial", 3)]

def generate_fake_candidates(n=1):
    for _ in range(n):
        try:
            gender = random.choice(GENDERS)
            education = random.choice(EDUCATION_LEVELS)
            availability = random.choice(AVAILABILITY)
            work_pref = random.choice(WORK_PREFERENCES)

            candidate = {
                "first_name": fake.first_name().lower(),
                "last_name": fake.last_name().lower(),
                "email": fake.unique.email().lower(),
                "phone_number": "+57" + fake.numerify(text='3#########'),
                "gender": str(gender[1]),
                "birth_date": fake.date_of_birth(minimum_age=18).isoformat(),
                "education_level": str(education[1]),
                "technical_skills": random.sample(TECH_SKILLS, k=random.randint(3, 6)),
                "interview_score": round(random.uniform(1.0, 10.0), 1),
                "technical_test_score": random.randint(0, 100),
                "availability": str(availability[1]),
                "salary_expectation": random.randint(2000000, 9000000),
                "location": fake.city().lower(),
                "experience": random.randint(0, 15),
                "soft_skills": random.sample(SOFT_SKILLS, k=random.randint(3, 5)),
                "languages": random.sample(LANGUAGES, k=random.randint(1, 5)),
                "personal_strengths": random.sample(STRENGTHS, k=random.randint(3, 5)),
                "work_preference": str(work_pref[1]),
                "career_interest": random.choice(CAREER_INTERESTS),
                "icfes": random.randint(200, 500),
                "short_term_goal": random.choice(SHORT_TERM_GOALS)
            }

            database.create_document(
                database_id=DATABASE_ID,
                collection_id=COLLECTION_ID,
                document_id=ID.unique(),
                data=candidate
            )

            print(f"✅ Candidato {candidate['email']} insertado.")
        except Exception as e:
            print(f"❌ Error al insertar candidato: {e}")


def sync_csv_with_appwrite():
    try:
        all_documents = []
        offset = 0
        limit = 100

        while True:
            response = database.list_documents(
                database_id=DATABASE_ID,
                collection_id=COLLECTION_ID,
                queries=[Query.limit(limit), Query.offset(offset)]
            )
            documents = response["documents"]
            if not documents:
                break
            all_documents.extend(documents)
            if len(documents) < limit:
                break
            offset += limit

        rows = []
        for doc in all_documents:
            if not all([
                doc.get("first_name"), doc.get("last_name"), doc.get("email"),
                doc.get("technical_skills"), doc.get("interview_score") is not None,
                doc.get("technical_test_score") is not None, doc.get("salary_expectation") is not None,
                doc.get("experience") is not None
            ]):
                continue

            rows.append({
                "first_name": doc.get("first_name", ""),
                "last_name": doc.get("last_name", ""),
                "email": doc.get("email", ""),
                "phone_number": doc.get("phone_number", ""),
                "gender": doc.get("gender", ""),
                "birth_date": doc.get("birth_date", ""),
                "education_level": doc.get("education_level", ""),
                "technical_skills": doc.get("technical_skills", ""),
                "interview_score": doc.get("interview_score", ""),
                "technical_test_score": doc.get("technical_test_score", ""),
                "availability": doc.get("availability", ""),
                "salary_expectation": doc.get("salary_expectation", ""),
                "location": doc.get("location", ""),
                "experience": doc.get("experience", ""),
                "soft_skills": doc.get("soft_skills", ""),
                "languages": doc.get("languages", ""),
                "work_preference": doc.get("work_preference", ""),
                "career_interest": doc.get("career_interest", ""),
                "personal_strengths": doc.get("personal_strengths", ""),
                "icfes": doc.get("icfes", ""),
                "short_term_goal": doc.get("short_term_goal", ""),
            })

        df = pd.DataFrame(rows)
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        df.to_csv(DATA_PATH, index=False)
        df.to_excel(DATA_PATH.replace(".csv", ".xlsx"), index=False, engine='openpyxl')
        print(f"✅ CSV actualizado con {len(rows)} candidatos válidos.")
    except Exception as e:
        import traceback
        print("❌ Error al sincronizar CSV:", traceback.format_exc())

def generate_and_sync(n=10):
    generate_fake_candidates(n=10)
    sync_csv_with_appwrite()
    generate_powerbi_csv()

if __name__ == "__main__":
    generate_and_sync(n=10)

