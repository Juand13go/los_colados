import pandas as pd
import ast
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "candidatos.csv")


TECHNICAL_SKILLS_WEIGHTS = {
    "Python": 10, "JavaScript": 8, "HTML": 6, "CSS": 6, "MySQL": 9,
    "React": 9, "Node.js": 8, "Docker": 7
}

SOFT_SKILLS_WEIGHTS = {
    "Comunicación": 5, "Trabajo en equipo": 6, "Adaptabilidad": 6,
    "Creatividad": 4, "Liderazgo": 7
}

PERSONAL_STRENGTHS_WEIGHTS = {
    "Liderazgo": 6, "Pensamiento Crítico": 7, "Adaptabilidad": 5,
    "Organización": 4, "Empatía": 4, "Autonomía": 3,
    "Proactividad": 5, "Comunicación": 4
}

LANGUAGES_WEIGHTS = {
    "Inglés": 5,
    "Español": 4,
    "Francés": 3,
    "Alemán": 3,
    "Portugués": 2
}


def preprocess_candidate_data(df):
    df["technical_skills"] = df["technical_skills"].apply(safe_eval)
    df["soft_skills"] = df["soft_skills"].apply(safe_eval)
    df["personal_strengths"] = df["personal_strengths"].apply(safe_eval)
    df["languages"] = df["languages"].apply(safe_eval)
    return df


def calculate_weighted_score(row):
    tech_score = sum(TECHNICAL_SKILLS_WEIGHTS.get(skill.strip(), 0) for skill in row["technical_skills"])
    soft_score = sum(SOFT_SKILLS_WEIGHTS.get(skill.strip(), 0) for skill in row["soft_skills"])
    strength_score = sum(PERSONAL_STRENGTHS_WEIGHTS.get(skill.strip(), 0) for skill in row["personal_strengths"])
    language_score = sum(LANGUAGES_WEIGHTS.get(lang.strip(), 0) for lang in row.get("languages", []))

    return (
        (tech_score * 0.5) +
        (soft_score * 0.2) +
        (strength_score * 0.2) +
        (language_score * 0.1) + 
        (row["interview_score"] * 2) +
        (row["technical_test_score"] * 0.1) +
        (row["icfes"] * 0.05)  
    )


def rank_candidates(csv_path=DATA_PATH):
    df = pd.read_csv(csv_path)
    df = preprocess_candidate_data(df)  
    df["total_score"] = df.apply(calculate_weighted_score, axis=1)
    return df.sort_values("total_score", ascending=False)


def safe_eval(val):
    try:
        return ast.literal_eval(val) if isinstance(val, str) else []
    except Exception:
        return []

def preprocess_candidate_data(df):
    df["technical_skills"] = df["technical_skills"].apply(safe_eval)
    df["soft_skills"] = df["soft_skills"].apply(safe_eval)
    df["personal_strengths"] = df["personal_strengths"].apply(safe_eval)
    return df

