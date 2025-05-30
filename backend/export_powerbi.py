# backend/export_powerbi.py
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ORIGINAL_CSV = os.path.join(BASE_DIR, "data", "candidatos.csv")
POWERBI_CSV = os.path.join(BASE_DIR, "data", "candidatos_powerbi.csv")

def generate_powerbi_csv():
    df = pd.read_csv(ORIGINAL_CSV)

    # Convertir puntaje_total a número (por si viene como texto o NaN)
    df["puntaje_total"] = pd.to_numeric(df["puntaje_total"], errors="coerce").fillna(0)

    # Limpiar listas que están en formato string
    for col in ["technical_skills", "soft_skills", "languages", "personal_strengths"]:
        df[col] = df[col].fillna("").apply(lambda x: ", ".join(eval(x)) if isinstance(x, str) and x.startswith("[") else x)

    # Nuevas columnas numéricas
    df["num_habilidades_tecnicas"] = df["technical_skills"].apply(lambda x: len(str(x).split(",")) if x else 0)
    df["num_habilidades_blandas"] = df["soft_skills"].apply(lambda x: len(str(x).split(",")) if x else 0)
    df["num_idiomas"] = df["languages"].apply(lambda x: len(str(x).split(",")) if x else 0)
    df["score_promedio"] = (df["interview_score"] * 0.5 + df["technical_test_score"] * 0.5).round(1)

    df.to_csv(POWERBI_CSV, index=False)
    print("✅ Archivo candidatos_powerbi.csv actualizado")


if __name__ == "__main__":
    generate_powerbi_csv()
