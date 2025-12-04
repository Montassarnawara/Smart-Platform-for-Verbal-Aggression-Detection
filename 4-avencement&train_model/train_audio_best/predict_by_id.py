import pandas as pd
import joblib
import os

# === Configuration ===
id_a_tester = 7  # 🔁 Change ici l'id que tu veux tester
fichier_data = "resultats_audio_son_test.csv"
modele_path = "danger_model.pkl"
scaler_path = "scaler.pkl"

# === Charger modèle et scaler ===
model = joblib.load(modele_path)
scaler = joblib.load(scaler_path)

# === Charger les données ===
df = pd.read_csv(fichier_data)

# === Vérifier si l'ID existe ===
if id_a_tester not in df["id"].values:
    print(f"❌ ID {id_a_tester} non trouvé dans le fichier.")
    exit()

# === Sélection de la ligne à prédire ===
row = df[df["id"] == id_a_tester].copy()
X_row = row[["amplitude", "rms", "dB", "Peak", "StdDev", "Score"]]
y_real = row["Danger%"].values[0]

# === Normalisation et prédiction ===
X_scaled = scaler.transform(X_row)
y_pred = model.predict(X_scaled)[0]

# === Résultat ===
print(f"🔎 Résultat pour l'ID {id_a_tester} :")
print(f"   Danger% prédit : {y_pred:.2f}")
print(f"   Danger% réel   : {y_real:.2f}")
