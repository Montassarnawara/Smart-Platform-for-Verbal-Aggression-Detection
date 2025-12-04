import os
import pandas as pd
import matplotlib.pyplot as plt
import joblib
from sklearn.metrics import r2_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

# === Définition des classes nécessaires ===
class AudioPreprocessor:
    def __init__(self, numeric_features, categorical_features):
        self.preprocessor = ColumnTransformer([
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])
    
    def transform(self, X):
        return self.preprocessor.transform(X)

class ModelContainer:
    def __init__(self, preprocessor, model):
        self.preprocessor = preprocessor
        self.model = model
    
    def predict(self, X):
        return self.model.predict(self.preprocessor.transform(X))

# === Fonction principale ===
def load_and_compare_models(base_dir="."):
    """
    Charge et compare les modèles pour tranches et fichiers audio
    """
    # Vérification des fichiers
    required_files = {
        'slice_model': 'slice_models.pkl',
        'file_model': 'file_models.pkl',
        'details_data': 'data_details.csv',
        'summary_data': 'data_summary.csv'
    }
    
    missing = [f for f in required_files.values() if not os.path.exists(os.path.join(base_dir, f))]
    if missing:
        raise FileNotFoundError(f"Fichiers manquants: {', '.join(missing)}")

    # Chargement des données
    details = pd.read_csv(os.path.join(base_dir, 'data_details.csv')).dropna()
    summary = pd.read_csv(os.path.join(base_dir, 'data_summary.csv')).dropna()

    # Création de l'environnement pour le chargement
    global __main__
    setattr(__main__, "AudioPreprocessor", AudioPreprocessor)
    
    try:
        # Chargement des modèles
        slice_data = joblib.load(os.path.join(base_dir, 'slice_models.pkl'))
        file_data = joblib.load(os.path.join(base_dir, 'file_models.pkl'))
        
        # Reconstruction des wrappers
        slice_models = {
            'Danger%': ModelContainer(slice_data['preprocessor'], slice_data['danger_model']),
            'moy_danger': ModelContainer(slice_data['preprocessor'], slice_data['moy_danger_model'])
        }
        
        file_models = {
            'danger_max': ModelContainer(file_data['preprocessor'], file_data['max_model']),
            'danger_moy': ModelContainer(file_data['preprocessor'], file_data['moy_model']),
            'danger_std': ModelContainer(file_data['preprocessor'], file_data['std_model'])
        }
        
        # Prédictions
        X_slice = details.drop(['Danger%', 'moy_danger', 'id', 'titre'], axis=1, errors='ignore')
        X_file = summary.drop(['titre', 'danger_max', 'danger_moy', 'danger_std'], axis=1, errors='ignore')
        
        preds = {
            'slice': {k: m.predict(X_slice) for k, m in slice_models.items()},
            'file': {k: m.predict(X_file) for k, m in file_models.items()}
        }
        
        # Visualisation
        plt.figure(figsize=(15, 10))
        
        # Graphique pour les tranches
        plt.subplot(2, 1, 1)
        for target in ['Danger%', 'moy_danger']:
            plt.plot(details[target].to_numpy(), label=f"{target} réel", alpha=0.7)
            plt.plot(preds['slice'][target], label=f"{target} prédit", linestyle='--', alpha=0.7)
        plt.title(f"Comparaison Tranches (R² Danger%: {r2_score(details['Danger%'], preds['slice']['Danger%']):.4f})")
        plt.legend()
        plt.grid()
        
        # Graphique pour les fichiers
        plt.subplot(2, 1, 2)
        for target in ['danger_max', 'danger_moy', 'danger_std']:
            plt.plot(summary[target].to_numpy(), label=f"{target} réel", alpha=0.7)
            plt.plot(preds['file'][target], label=f"{target} prédit", linestyle='--', alpha=0.7)
        plt.title(f"Comparaison Fichiers (R² moy: {r2_score(summary['danger_moy'], preds['file']['danger_moy']):.4f})")
        plt.legend()
        plt.grid()
        
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        raise RuntimeError(f"Erreur lors de l'exécution: {str(e)}")

if __name__ == "__main__":
    # Création de l'espace de noms global nécessaire
    import __main__
    # __main__.AudioPreprocessor assignment removed to avoid error
    
    try:
        load_and_compare_models()
    except Exception as e:
        print(f"ERREUR: {str(e)}")
        print("Vérifiez que:")
        print("- Tous les fichiers requis sont présents")
        print("- Les modèles ont été exportés correctement")
        print("- Les données sont au bon format")