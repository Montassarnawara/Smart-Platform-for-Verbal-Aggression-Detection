import joblib
import pandas as pd
import sys
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

# Définition nécessaire pour le chargement des modèles
class AudioPreprocessor:
    def __init__(self, numeric_features, categorical_features):
        self.numeric_features = numeric_features
        self.categorical_features = categorical_features
        self.preprocessor = ColumnTransformer([
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])
    
    def transform(self, X):
        return self.preprocessor.transform(X)

# Ajout de la classe au module principal
setattr(sys.modules['__main__'], "AudioPreprocessor", AudioPreprocessor)

def load_models():
    """Charge les modèles avec gestion des erreurs"""
    try:
        slice_models = joblib.load("slice_models.pkl")
        file_models = joblib.load("file_models.pkl")
        return slice_models, file_models
    except Exception as e:
        print(f"Erreur de chargement des modèles: {str(e)}")
        print("Vérifiez que:")
        print("- Les fichiers slice_models.pkl et file_models.pkl existent")
        print("- Toutes les classes nécessaires sont définies")
        raise

def prepare_input(features_row, preprocessor):
    """Prépare les données d'entrée pour la prédiction"""
    # Convertir en DataFrame si ce n'est pas déjà le cas
    if not isinstance(features_row, pd.DataFrame):
        features_row = pd.DataFrame([features_row])
    
    # Appliquer le prétraitement
    try:
        return preprocessor.transform(features_row)
    except Exception as e:
        print(f"Erreur lors du prétraitement: {str(e)}")
        raise

def predict_for_id(id, df_type='details'):
    """Prédit les valeurs pour un ID donné"""
    # Chargement des modèles
    try:
        slice_models, file_models = load_models()
    except:
        return

    # Chargement des données
    try:
        if df_type == 'details':
            df = pd.read_csv("data_details.csv")
            target_cols = ['Danger%', 'moy_danger']
            features = df.drop(columns=target_cols + ['id', 'titre'], errors='ignore')
            # Colonnes catégorielles attendues
            cat_cols = ['cri_type'] if 'cri_type' in features.columns else []
        else:
            df = pd.read_csv("data_summary.csv")
            target_cols = ['danger_max', 'danger_moy', 'danger_std']
            features = df.drop(columns=target_cols + ['titre'], errors='ignore')
            # Colonnes catégorielles attendues
            cat_cols = ['cri_type_dom'] if 'cri_type_dom' in features.columns else []
    except FileNotFoundError:
        print(f"Fichier data_{df_type}.csv introuvable")
        return

    # Trouver la ligne correspondante
    row = df[df['id'] == id] if 'id' in df.columns else df.iloc[[id]]
    if row.empty:
        print(f"ID {id} non trouvé dans data_{df_type}")
        return

    # Prétraitement
    features_row = features.loc[row.index[0]]
    
    # Ajout de 'env' si nécessaire
    if 'Danger%' in row.columns and 'env' not in features_row:
        danger_val = row['Danger%'].values[0]
        features_row['env'] = 3 if danger_val > 60 else 2 if danger_val >= 50 else 1
    
    # Conversion en DataFrame pour le prétraitement
    input_data = pd.DataFrame([features_row])
    
    # Prédiction
    try:
        if df_type == 'details':
            X = prepare_input(input_data, slice_models['preprocessor'])
            pred_danger = slice_models['danger_model'].predict(X)[0]
            pred_moy = slice_models['moy_danger_model'].predict(X)[0]
            
            print(f"\n🔍 Résultats pour ID {id} (tranche audio):")
            print(f"🟢 Danger% - Réel: {row['Danger%'].values[0]:.2f} | Prédit: {pred_danger:.2f}")
            print(f"🔵 moy_danger - Réel: {row['moy_danger'].values[0]:.2f} | Prédit: {pred_moy:.2f}")
        else:
            X = prepare_input(input_data, file_models['preprocessor'])
            pred_max = file_models['max_model'].predict(X)[0]
            pred_moy = file_models['moy_model'].predict(X)[0]
            pred_std = file_models['std_model'].predict(X)[0]
            
            print(f"\n🔍 Résultats pour ID {id} (fichier audio):")
            print(f"🔴 danger_max - Réel: {row['danger_max'].values[0]:.2f} | Prédit: {pred_max:.2f}")
            print(f"🟠 danger_moy - Réel: {row['danger_moy'].values[0]:.2f} | Prédit: {pred_moy:.2f}")
            print(f"🟢 danger_std - Réel: {row['danger_std'].values[0]:.2f} | Prédit: {pred_std:.2f}")
    except Exception as e:
        print(f"Erreur lors de la prédiction: {str(e)}")
        print("Vérifiez que les données d'entrée correspondent au format attendu par le modèle")

if __name__ == "__main__":
    # Exemples d'utilisation
    print("=== TEST DES MODELES ===")
    
    # Pour une tranche audio (data_details)
    predict_for_id(3, 'details')
    
    # Pour un fichier audio (data_summary)
    predict_for_id(1, 'summary')