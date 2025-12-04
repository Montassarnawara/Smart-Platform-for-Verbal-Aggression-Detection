# load_and_test_model.py
import os
import pandas as pd
import matplotlib.pyplot as plt
import joblib

# === 📁 Dossier du script
base_dir = os.path.dirname(os.path.abspath(__file__))

# === 💾 Chargement du pipeline complet
pipeline = joblib.load(os.path.join(base_dir, "danger_pipeline.pkl"))

# === 📊 Chargement des données
df = pd.read_csv(os.path.join(base_dir, "data_ml_ready.csv"))
df = df.drop(columns=["id", "titre", "moy_danger"], errors="ignore")
df = df.dropna()

# === 🔁 Ajout de la colonne 'env' si elle n'existe pas
if 'env' not in df.columns:
    df["env"] = df["Danger%"].apply(lambda d: 3 if d > 60 else 2 if d >= 50 else 1)

# === 📦 Séparation X et y
X = df.drop(columns=["Danger%"])
y = df["Danger%"]

# === 🔮 Prédiction
y_pred = pipeline.predict(X)

# === 📈 Graphe
plt.figure(figsize=(10, 5))
plt.plot(y.values, label="Danger réel", marker='o')
plt.plot(y_pred, label="Danger prédit", marker='x')
plt.xlabel("Index")
plt.ylabel("Danger %")
plt.title("📊 Comparaison Danger Réel vs Prédit")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
