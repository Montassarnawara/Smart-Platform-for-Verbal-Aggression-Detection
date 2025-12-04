import joblib
import pandas as pd

# Charger pipeline
pipeline = joblib.load("danger_pipeline.pkl")

# Charger le fichier CSV
df = pd.read_csv("resultats_audio_test.csv")

# Sélectionner une ligne par ID (ex : ligne 25)
ligne = df.iloc[3]

# Nettoyer et créer env
ligne = ligne.drop(labels=["id", "titre", "moy_danger"], errors="ignore")
danger_val = ligne["Danger%"]
env = 3 if danger_val > 60 else 2 if danger_val >= 50 else 1
ligne["env"] = env

# Supprimer la cible
X = ligne.drop("Danger%").to_numpy().reshape(1, -1)

# Prédiction
pred = pipeline.predict(X)[0]

print(f"🟡 Réel : {danger_val:.2f}%")
print(f"🔵 Prédit : {pred:.2f}%")
