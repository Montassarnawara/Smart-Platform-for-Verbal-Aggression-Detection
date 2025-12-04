import os
import pandas as pd
import matplotlib.pyplot as plt
import joblib

# Dossier du script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Charger modèle + scaler
model = joblib.load(os.path.join(base_dir, "danger_model.pkl"))
scaler = joblib.load(os.path.join(base_dir, "scaler.pkl"))

# Charger données
df = pd.read_csv(os.path.join(base_dir, "resultats_audio_son_test.csv"))
df = df.drop(columns=["id", "titre", "moy_danger"])
X = df.drop(columns=["Danger%"])
y = df["Danger%"]

# Normalisation
X_scaled = scaler.transform(X)

# Prédiction
y_pred = model.predict(X_scaled)

# Graphe simple
plt.figure(figsize=(10, 5))
plt.plot(y.values, label="Danger réel", marker='o')
plt.plot(y_pred, label="Danger prédit", marker='x')
plt.xlabel("Index")
plt.ylabel("Danger %")
plt.title("Comparaison Danger Réel vs Prédit")
plt.legend()
plt.grid()
plt.show()
