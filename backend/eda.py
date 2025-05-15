import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Ruta al archivo CSV
data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "candidatos.csv")

# Leer el CSV
df = pd.read_csv(data_path)

# Mostrar las primeras filas
print("\n🔍 Primeros registros:")
print(df.head())

# Información general del DataFrame
print("\n📋 Información del DataFrame:")
df.info()

# Verificar valores nulos
print("\n❗ Valores nulos por columna:")
print(df.isnull().sum())

# Estadísticas descriptivas de variables numéricas
print("\n📊 Estadísticas descriptivas:")
print(df.describe())

# Distribución de nivel educativo
print("\n🎓 Distribución de nivel educativo:")
print(df['education_level'].value_counts())

# Distribución de género
print("\n⚧️ Distribución de género:")
print(df['gender'].value_counts())

print("\n📈 Distribución de puntajes ICFES:")
print(df["icfes"].describe())

# Distribución de idiomas
print("\n🗣️ Distribución de idiomas declarados:")
from collections import Counter
import ast

df["languages"] = df["languages"].fillna("").apply(ast.literal_eval)
all_languages = [lang.strip() for sublist in df["languages"] for lang in sublist]
language_counts = Counter(all_languages)

for lang, count in language_counts.items():
    print(f"{lang}: {count}")

# Histograma de experiencia
plt.figure()
df['experience'].hist(bins=15, color='skyblue', edgecolor='black')
plt.title("Distribución de Experiencia (años)")
plt.xlabel("Años de experiencia")
plt.ylabel("Cantidad de candidatos")
plt.grid(False)
plt.show()

# Boxplot de salario esperado
plt.figure()
sns.boxplot(x=df['salary_expectation'])
plt.title("Distribución de Expectativa Salarial")
plt.xlabel("Salario esperado")
plt.grid(True)
plt.show()

# Correlación entre puntajes y experiencia
print("\n🔗 Correlaciones relevantes:")
print(df[["interview_score", "technical_test_score", "experience", "salary_expectation"]].corr())

# Barras apiladas de nivel educativo por género
plt.figure(figsize=(8, 6))
edu_gender = pd.crosstab(df['education_level'], df['gender'])
edu_gender.plot(kind='bar', stacked=True, colormap='viridis')
plt.title("Distribución de Nivel Educativo por Género")
plt.xlabel("Nivel Educativo")
plt.ylabel("Cantidad de Candidatos")
plt.legend(title="Género")
plt.tight_layout()
plt.show()

# Salario promedio según carrera de interés
plt.figure(figsize=(10, 6))
df.dropna(subset=['career_interest', 'salary_expectation'], inplace=True)
avg_salary = df.groupby('career_interest')['salary_expectation'].mean().sort_values()
avg_salary.plot(kind='barh', color='teal')
plt.title("Salario Promedio según Carrera de Interés")
plt.xlabel("Salario Promedio")
plt.ylabel("Carrera de Interés")
plt.tight_layout()
plt.show()

plt.figure(figsize=(8,5))
sns.barplot(x=list(language_counts.values()), y=list(language_counts.keys()), palette="Blues_d")
plt.title("Distribución de Idiomas entre Candidatos")
plt.xlabel("Cantidad")
plt.ylabel("Idioma")
plt.tight_layout()
plt.show()

plt.figure()
df["icfes"].hist(bins=20, color="salmon", edgecolor="black")
plt.title("Distribución de Puntajes ICFES")
plt.xlabel("Puntaje ICFES")
plt.ylabel("Cantidad de candidatos")
plt.grid(False)
plt.show()
