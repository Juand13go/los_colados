import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import ast
from collections import Counter

# === Rutas ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(os.path.dirname(BASE_DIR), "data", "candidatos.csv")
PLOTS_DIR = os.path.join(BASE_DIR, "static", "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

def get_eda_summary():
    df = pd.read_csv(DATA_PATH)

    resumen = {
        "head": df.head().to_html(classes="table", border=0, index=False),
        "info": df.dtypes.to_frame("Tipo").reset_index().rename(columns={"index": "Columna"}).to_html(classes="table", border=0, index=False),
        "missing": df.isnull().sum().reset_index().rename(columns={"index": "Columna", 0: "Nulos"}).to_html(classes="table", border=0, index=False),
        "describe": df.describe().transpose().reset_index().rename(columns={"index": "Columna"}).to_html(classes="table", border=0, index=False),
        "educacion": df["education_level"].value_counts().reset_index().rename(columns={"index": "Nivel", "education_level": "Cantidad"}).to_html(classes="table", border=0, index=False),
        "genero": df["gender"].value_counts().reset_index().rename(columns={"index": "Género", "gender": "Cantidad"}).to_html(classes="table", border=0, index=False),
        "icfes": df["icfes"].describe().to_frame().reset_index().to_html(classes="table", border=0, index=False)
    }

    return resumen


# === Función 2: genera y guarda gráficos ===
def run_generate_plots():
    df = pd.read_csv(DATA_PATH)
    df["languages"] = df["languages"].fillna("").apply(ast.literal_eval)
    all_languages = [lang.strip() for sublist in df["languages"] for lang in sublist]
    language_counts = Counter(all_languages)

    # Experiencia
    plt.figure()
    df['experience'].hist(bins=15, color='skyblue', edgecolor='black')
    plt.title("Distribución de Experiencia (años)")
    plt.xlabel("Años de experiencia")
    plt.ylabel("Cantidad de candidatos")
    plt.grid(False)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "experiencia.png"))

    # Salario esperado
    plt.figure()
    sns.boxplot(x=df['salary_expectation'])
    plt.title("Distribución de Expectativa Salarial")
    plt.xlabel("Salario esperado")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "salario.png"))

    # Educación por género
    plt.figure(figsize=(8, 6))
    edu_gender = pd.crosstab(df['education_level'], df['gender'])
    edu_gender.plot(kind='bar', stacked=True, colormap='viridis')
    plt.title("Distribución de Nivel Educativo por Género")
    plt.xlabel("Nivel Educativo")
    plt.ylabel("Cantidad de Candidatos")
    plt.legend(title="Género")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "educacion_genero.png"))

    # Salario promedio por carrera
    plt.figure(figsize=(10, 6))
    df.dropna(subset=['career_interest', 'salary_expectation'], inplace=True)
    avg_salary = df.groupby('career_interest')['salary_expectation'].mean().sort_values()
    avg_salary.plot(kind='barh', color='teal')
    plt.title("Salario Promedio según Carrera de Interés")
    plt.xlabel("Salario Promedio")
    plt.ylabel("Carrera de Interés")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "salario_carrera.png"))

    # Idiomas
    plt.figure(figsize=(8, 5))
    sns.barplot(x=list(language_counts.values()), y=list(language_counts.keys()))
    plt.title("Distribución de Idiomas entre Candidatos")
    plt.xlabel("Cantidad")
    plt.ylabel("Idioma")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "idiomas.png"))

    # Puntaje ICFES
    plt.figure()
    df["icfes"].hist(bins=20, color="salmon", edgecolor="black")
    plt.title("Distribución de Puntajes ICFES")
    plt.xlabel("Puntaje ICFES")
    plt.ylabel("Cantidad de candidatos")
    plt.grid(False)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "icfes.png"))

    print("\n✅ Gráficos guardados en static/plots/")


def get_eda_dataframes():
    df = pd.read_csv(DATA_PATH)
    df["languages"] = df["languages"].fillna("").apply(ast.literal_eval)

    df_types = pd.DataFrame({
        "Columna": df.dtypes.index,
        "Tipo": df.dtypes.values
    })

    df_missing = pd.DataFrame({
        "Columna": df.columns,
        "Nulos": df.isnull().sum().values
    })

    df_describe = df.describe().T.reset_index().rename(columns={"index": "Columna"})

    return df.head(5), df_types, df_missing, df_describe
