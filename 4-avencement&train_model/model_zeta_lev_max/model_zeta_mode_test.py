import pandas as pd
import joblib
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

# Définition des classes nécessaires pour le chargement des modèles
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

class ModelContainer:
    def __init__(self, preprocessor, model):
        self.preprocessor = preprocessor
        self.model = model
    
    def predict(self, X):
        return self.model.predict(self.preprocessor.transform(X))

def load_models_and_predict():
    """Charge les modèles et données, puis calcule les prédictions"""
    try:
        # 1. Charger les données
        details = pd.read_csv('data_details.csv').dropna()
        summary = pd.read_csv('data_summary.csv').dropna()
        
        # 2. Charger les modèles avec gestion des dépendances
        import __main__
        setattr(__main__, 'AudioPreprocessor', AudioPreprocessor)
        
        slice_data = joblib.load('slice_models.pkl')
        file_data = joblib.load('file_models.pkl')
        
        # 3. Préparer les modèles
        slice_models = {
            'Danger%': ModelContainer(slice_data['preprocessor'], slice_data['danger_model']),
            'moy_danger': ModelContainer(slice_data['preprocessor'], slice_data['moy_danger_model'])
        }
        
        file_models = {
            'danger_max': ModelContainer(file_data['preprocessor'], file_data['max_model']),
            'danger_moy': ModelContainer(file_data['preprocessor'], file_data['moy_model']),
            'danger_std': ModelContainer(file_data['preprocessor'], file_data['std_model'])
        }
        
        # 4. Préparer les données d'entrée
        X_slice = details.drop(['Danger%', 'moy_danger', 'id', 'titre'], axis=1, errors='ignore')
        X_file = summary.drop(['titre', 'danger_max', 'danger_moy', 'danger_std'], axis=1, errors='ignore')
        
        # 5. Faire les prédictions
        results = {
            'details': details.copy(),
            'summary': summary.copy()
        }
        
        # Prédictions pour les tranches
        results['details']['Danger%_pred'] = slice_models['Danger%'].predict(X_slice)
        results['details']['moy_danger_pred'] = slice_models['moy_danger'].predict(X_slice)
        
        # Prédictions pour les fichiers
        results['summary']['danger_max_pred'] = file_models['danger_max'].predict(X_file)
        results['summary']['danger_moy_pred'] = file_models['danger_moy'].predict(X_file)
        results['summary']['danger_std_pred'] = file_models['danger_std'].predict(X_file)
        
        return results
        
    except Exception as e:
        print(f"Erreur: {str(e)}")
        return None

def display_results(results):
    """Affiche les résultats de manière claire"""
    if not results:
        return
    
    # Affichage des prédictions pour les tranches
    print("\n=== PRÉDICTIONS POUR LES TRANCHES ===")
    print(results['details'][['id', 'titre', 'Danger%', 'Danger%_pred', 'moy_danger', 'moy_danger_pred']].head())
    
    # Affichage des prédictions pour les fichiers
    print("\n=== PRÉDICTIONS POUR LES FICHIERS ===")
    print(results['summary'][['titre', 'danger_max', 'danger_max_pred', 
                            'danger_moy', 'danger_moy_pred']].head())
    
    # Visualisation
    plt.figure(figsize=(15, 6))
    
    # Graphique Danger%
    plt.subplot(1, 2, 1)
    plt.scatter(results['details']['Danger%'], results['details']['Danger%_pred'], alpha=0.5)
    plt.plot([0, 100], [0, 100], 'r--')
    plt.title(f"Danger% (R²={r2_score(results['details']['Danger%'], results['details']['Danger%_pred']):.3f})")
    plt.xlabel("Réel")
    plt.ylabel("Prédit")
    plt.grid()
    
    # Graphique danger_max
    plt.subplot(1, 2, 2)
    plt.scatter(results['summary']['danger_max'], results['summary']['danger_max_pred'], alpha=0.5)
    plt.plot([0, 100], [0, 100], 'r--')
    plt.title(f"danger_max (R²={r2_score(results['summary']['danger_max'], results['summary']['danger_max_pred']):.3f})")
    plt.xlabel("Réel")
    plt.ylabel("Prédit")
    plt.grid()
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Création de l'espace de noms global nécessaire
    import __main__
    setattr(__main__, 'AudioPreprocessor', AudioPreprocessor)
    
    print("Chargement des modèles et calcul des prédictions...")
    predictions = load_models_and_predict()
    
    if predictions is not None:
        display_results(predictions)
        print("\n✅ Prédictions terminées avec succès!")
        
        # Option: Sauvegarder les résultats
        save = input("Voulez-vous sauvegarder les résultats? (o/n) ").lower()
        if save == 'o':
            predictions['details'].to_csv('predictions_details.csv', index=False)
            predictions['summary'].to_csv('predictions_summary.csv', index=False)
            print("📁 Résultats sauvegardés dans predictions_details.csv et predictions_summary.csv")
    else:
        print("❌ Erreur lors du calcul des prédictions")