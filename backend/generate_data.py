import random
import pandas as pd
import os
from faker import Faker
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
from appwrite_config import APPWRITE_ENDPOINT, APPWRITE_PROJECT_ID, APPWRITE_API_KEY, DATABASE_ID, COLLECTION_ID

# Inicializar Faker
fake = Faker()
Faker.seed(42)

# Configurar Appwrite
client = Client()
client.set_endpoint(APPWRITE_ENDPOINT)
client.set_project(APPWRITE_PROJECT_ID)
client.set_key(APPWRITE_API_KEY)

database = Databases(client)

niveles_educacion = ["bachillerato", "licenciatura", "maestria", "doctorado"]
habilidades_tecnicas = ["python", "javascript", "sql", "c++", "django", "react", "aws", "docker"]
habilidades_blandas = ["trabajoenequipo", "comunicacion", "liderazgo", "resoluciondeproblemas"]
disponibilidades = ["tiempocompleto", "tiempoparcial", "flexible"]
intereses_empresa = ["high", "medium", "low"]
preferencias_trabajo = ["remoto", "presencial", "hibrido"]

data = []
for _ in range(52):
    nombre = fake.first_name().lower()
    apellidos = fake.last_name().lower()
    genero = random.choice(["masculino", "femenino", "otro"])
    fecha_nacimiento = fake.date_of_birth(minimum_age=18, maximum_age=60).strftime("%Y-%m-%d")
    nivel_educacion = random.choice(niveles_educacion)
    habilidades_tecnicas_list = random.sample(habilidades_tecnicas, random.randint(1, 4))
    puntuacion_entrevista = round(random.uniform(1, 10), 1)
    puntuacion_prueba_tecnica = random.randint(0, 100)
    disponibilidad = random.choice(disponibilidades)
    expectativa_salarial = round(random.uniform(30000, 120000), 2)
    interes_empresa = random.choice(intereses_empresa)
    ubicacion = fake.city().lower()
    experiencia = random.randint(0, 20)
    habilidades_blandas_list = random.sample(habilidades_blandas, random.randint(1, 3))
    preferencia_trabajo = random.choice(preferencias_trabajo)

    data.append([
        nombre, apellidos, genero, fecha_nacimiento, nivel_educacion, 
        habilidades_tecnicas_list, puntuacion_entrevista, 
        puntuacion_prueba_tecnica, disponibilidad, expectativa_salarial,
        interes_empresa, ubicacion, experiencia, habilidades_blandas_list, preferencia_trabajo
    ])

    try:
        database.create_document(
            database_id=DATABASE_ID,
            collection_id=COLLECTION_ID,
            document_id=ID.unique(),
            data={
                "first_name": nombre,
                "last_name": apellidos,
                "gender": genero,
                "birth_date": fecha_nacimiento,
                "education_level": nivel_educacion,
                "technical_skills": habilidades_tecnicas_list,
                "interview_score": puntuacion_entrevista,
                "technical_test_score": puntuacion_prueba_tecnica,
                "availability": disponibilidad,
                "salary_expectation": expectativa_salarial,
                "company_interest": interes_empresa,
                "location": ubicacion,
                "experience": experiencia,
                "soft_skills": habilidades_blandas_list,
                "work_preference": preferencia_trabajo
            }
        )
    except Exception as e:
        print(f"Error al insertar documento: {e}")

df = pd.DataFrame(data, columns=[
    "first_name", "last_name", "gender", "birth_date", "education_level", 
    "technical_skills", "interview_score", "technical_test_score", 
    "availability", "salary_expectation", "company_interest", "location", 
    "experience", "soft_skills", "work_preference"
])

df.to_csv("data/candidatos.csv", index=False)
df.to_excel("data/candidatos.xlsx", index=False, engine='openpyxl')

print("Dataset generado y guardado en /data")
