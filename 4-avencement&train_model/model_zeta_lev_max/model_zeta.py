import pandas as pd
import joblib
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

# 1. Classes nécessaires
class AudioPreprocessor:
    def __init__(self, numeric_features, categorical_features):
        self.preprocessor = ColumnTransformer([
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])
    
    def transform(self, X):
        return self.preprocessor.transform(X)

class ModelWrapper:
    def __init__(self, preprocessor, model=None):
        self.preprocessor = preprocessor
        self.model = model
    
    def predict(self, X):
        if self.model is None:
            raise ValueError("Modèle non initialisé!")
        return self.model.predict(self.preprocessor.transform(X))

# 2. Chargeur sécurisé
def safe_load_models():
    try:
        slice_data = joblib.load('slice_models.pkl')
        file_data = joblib.load('file_models.pkl')
        
        # Vérification des modèles
        required_keys = {
            'slice': ['preprocessor', 'danger_model', 'moy_danger_model'],
            'file': ['preprocessor', 'max_model', 'moy_model', 'std_model']
        }
        
        for data, keys in [(slice_data, required_keys['slice']), 
                          (file_data, required_keys['file'])]:
            if not all(key in data for key in keys):
                missing = [k for k in keys if k not in data]
                raise ValueError(f"Fichier modèle corrompu. Clés manquantes: {missing}")
        
        return slice_data, file_data
    except Exception as e:
        print("ERREUR lors du chargement:", str(e))
        raise

# 3. Nettoyage des données
def clean_data(df, target_columns):
    """Supprime les lignes avec NaN dans les colonnes cibles"""
    initial_count = len(df)
    cleaned = df.dropna(subset=target_columns)
    if len(cleaned) < initial_count:
        print(f"Attention: {initial_count - len(cleaned)} lignes avec NaN supprimées")
    return cleaned

# 4. Pipeline principal
def main():
    try:
        # Chargement des données avec nettoyage
        details = clean_data(pd.read_csv('data_details.csv'), ['Danger%', 'moy_danger'])
        summary = clean_data(pd.read_csv('data_summary.csv'), ['danger_max', 'danger_moy', 'danger_std'])
        
        # Chargement des modèles
        slice_data, file_data = safe_load_models()
        
        # Initialisation des wrappers
        slice_models = {
            'Danger%': ModelWrapper(slice_data['preprocessor'], slice_data['danger_model']),
            'moy_danger': ModelWrapper(slice_data['preprocessor'], slice_data['moy_danger_model'])
        }
        
        file_models = {
            'danger_max': ModelWrapper(file_data['preprocessor'], file_data['max_model']),
            'danger_moy': ModelWrapper(file_data['preprocessor'], file_data['moy_model']),
            'danger_std': ModelWrapper(file_data['preprocessor'], file_data['std_model'])
        }
        
        # Préparation des données
        X_slice = details.drop(['Danger%', 'moy_danger', 'id', 'titre'], axis=1)
        X_file = summary.drop(['titre', 'danger_max', 'danger_moy', 'danger_std'], axis=1)
        
        # Prédictions
        predictions = {
            'slice': {
                'Danger%': slice_models['Danger%'].predict(X_slice),
                'moy_danger': slice_models['moy_danger'].predict(X_slice)
            },
            'file': {
                'danger_max': file_models['danger_max'].predict(X_file),
                'danger_moy': file_models['danger_moy'].predict(X_file),
                'danger_std': file_models['danger_std'].predict(X_file)
            }
        }
        
        # Visualisation améliorée
        def safe_plot(real, pred, title):
            """Gère les erreurs de visualisation"""
            try:
                plt.figure(figsize=(10, 6))
                plt.scatter(real, pred, alpha=0.5)
                plt.plot([real.min(), real.max()], [real.min(), real.max()], 'r--')
                plt.xlabel('Valeurs Réelles')
                plt.ylabel('Prédictions')
                
                # Calcul sécurisé des métriques
                try:
                    r2 = r2_score(real, pred)
                    mae = mean_absolute_error(real, pred)
                    plt.title(f"{title}\nR²={r2:.4f} | MAE={mae:.4f}")
                except Exception as e:
                    plt.title(f"{title}\n(Métriques indisponibles: {str(e)})")
                
                plt.grid()
                plt.show()
            except Exception as e:
                print(f"Échec de visualisation pour {title}: {str(e)}")
        
        print("\n=== ANALYSE TRANCHES ===")
        safe_plot(details['Danger%'], predictions['slice']['Danger%'], 'Danger% (Tranches)')
        safe_plot(details['moy_danger'], predictions['slice']['moy_danger'], 'moy_danger (Tranches)')
        
        print("\n=== ANALYSE FICHIERS ===")
        safe_plot(summary['danger_max'], predictions['file']['danger_max'], 'danger_max (Fichiers)')
        safe_plot(summary['danger_moy'], predictions['file']['danger_moy'], 'danger_moy (Fichiers)')
        safe_plot(summary['danger_std'], predictions['file']['danger_std'], 'danger_std (Fichiers)')
        
    except Exception as e:
        print("\nERREUR CRITIQUE:", str(e))
        print("Vérifiez que:")
        print("- Les fichiers de données sont au bon format")
        print("- Les modèles ont été correctement sauvegardés")
        print("- Aucune colonne essentielle ne manque")

if __name__ == "__main__":
    main()