import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

# === 📁 Initialisation
save_dir = os.path.dirname(os.path.abspath(__file__))

# === 📊 Chargement des données
df = pd.read_csv("data_ml_ready.csv")

# 🧹 Nettoyage
df = df.drop(columns=["id", "titre", "moy_danger"], errors="ignore")
df = df.dropna()

# === ✅ Ajout de la colonne 'env'
def calcul_env(danger):
    if danger > 60:
        return 3
    elif danger >= 50:
        return 2
    else:
        return 1

df['env'] = df['Danger%'].apply(calcul_env)

# === 🎯 Séparation X / y
X = df.drop(columns=["Danger%"])
y = df["Danger%"]

# === 🔀 Split train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# === 🔁 Pipeline (scaler + modèle)
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("model", RandomForestRegressor(n_estimators=100, random_state=42))
])

# === ⚙️ Entraînement
pipeline.fit(X_train, y_train)

# === 📈 Prédiction
y_pred = pipeline.predict(X_test)

# === 📊 Évaluation
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("=== Évaluation du modèle ===")
print(f"MAE  : {mae:.2f}")
print(f"RMSE : {rmse:.2f}")
print(f"R²   : {r2:.2f}")

# === 💾 Sauvegarde du pipeline complet
joblib.dump(pipeline, os.path.join(save_dir, "danger_pipeline.pkl"))

# === 📉 Graphique
plot_df = pd.DataFrame({'y_test': y_test, 'y_pred': y_pred})
plt.figure(figsize=(6, 6))
sns.scatterplot(x='y_test', y='y_pred', data=plot_df)
plt.plot([0, 100], [0, 100], 'r--', label="Perfect Prediction")
plt.xlabel("True Danger%")
plt.ylabel("Predicted Danger%")
plt.title("🎯 Prédiction vs Réalité")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
