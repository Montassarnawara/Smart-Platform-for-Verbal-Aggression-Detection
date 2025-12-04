import pandas as pd
import numpy as np
import random

# Charger les données originales
df = pd.read_csv("resultats_audio_test.csv")

# Générer 100 lignes synthétiques réparties sur 20 fichiers
new_rows = []
synthetic_titles = [f"synthetic_{i}.wav" for i in range(1, 21)]

for title in synthetic_titles:
    num_chunks = random.randint(3, 6)  # chaque fichier a 3 à 6 tranches de 5s
    danger_sum = 0

    for i in range(num_chunks):
        # ✅ Génération réaliste avec des distributions proches du vrai dataset
        rms = np.clip(np.random.normal(0.14, 0.03), 0.08, 0.25)
        db = 20 * np.log10(rms + 1e-6) + 100
        peak = np.clip(np.random.normal(0.85, 0.07), 0.65, 1.0)
        std = np.clip(np.random.normal(rms, 0.01), 0.02, 0.25)

        # Calcul du score et danger%
        score = 0.4 * db + 30 * peak + 20 * std
        danger = int(min(100, round(score)))
        danger_sum += danger

        # 🧠 Ajouter env selon la règle
        if danger > 70:
            env = random.choice([3, 4, 5])
        elif danger > 60:
            env = 3
        elif danger > 50:
            env = 2
        else:
            env = 1

        new_rows.append({
            "id": len(df) + len(new_rows) + 1,
            "titre": title,
            "rms": round(rms, 6),
            "dB": round(db, 4),
            "Peak": round(peak, 6),
            "StdDev": round(std, 6),
            "Score": round(score, 4),
            "Danger%": danger,
            "env": env,
            "moy_danger": 0  # temporaire
        })

# Convertir les nouvelles lignes en DataFrame
df_new = pd.DataFrame(new_rows)

# Calcul de moy_danger pour chaque fichier synthétique
for title in synthetic_titles:
    subset = df_new[df_new["titre"] == title]
    moy = subset["Danger%"].mean()
    df_new.loc[df_new["titre"] == title, "moy_danger"] = round(moy, 2)

# Fusionner données existantes + nouvelles
df_final = pd.concat([df, df_new], ignore_index=True)

# Sauvegarder le nouveau fichier
df_final.to_csv("data_ml_ready_test.csv", index=False)
print("✅ Données enrichies enregistrées dans : data_ml_ready.csv")
