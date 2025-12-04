import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

# Chemin absolu vers le dossier du script
save_dir = os.path.dirname(os.path.abspath(__file__))

# Chargement des données
df = pd.read_csv("data_ml_ready.csv")
df = df.drop(columns=["id", "titre", "moy_danger"])
X = df.drop(columns=["Danger%"])
y = df["Danger%"]

# Normalisation
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split des données
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Modèle
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Évaluation
y_pred = model.predict(X_test)
print("MAE :", mean_absolute_error(y_test, y_pred))
print("RMSE :", np.sqrt(mean_squared_error(y_test, y_pred)))
print("R²   :", r2_score(y_test, y_pred))

# Sauvegarde dans le bon dossier
joblib.dump(model, os.path.join(save_dir, "danger_model.pkl"))
joblib.dump(scaler, os.path.join(save_dir, "scaler.pkl"))

# Graphe
plt.figure(figsize=(6, 6))
sns.scatterplot(x=y_test, y=y_pred)
plt.plot([0, 100], [0, 100], 'r--')
plt.xlabel("True Danger%")
plt.ylabel("Predicted Danger%")
plt.title("Prédiction vs Réalité")
plt.grid()
plt.show()
