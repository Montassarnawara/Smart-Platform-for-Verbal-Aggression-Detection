import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GridSearchCV
import joblib
import warnings
warnings.filterwarnings('ignore')

# 1. Chargement et nettoyage des données
def load_and_prepare_data(details_path, summary_path):
    details = pd.read_csv(details_path)
    summary = pd.read_csv(summary_path)
    
    # Nettoyage des données
    details['cri'] = details['cri'].astype(int)
    details['cri_type'] = details['cri_type'].fillna('aucun')
    summary['cri_type_dom'] = summary['cri_type_dom'].fillna('aucun')
    
    # Suppression des NaN dans les targets
    summary = summary.dropna(subset=['danger_max', 'danger_moy', 'danger_std'])
    
    return {
        'slice_data': (details.drop(['Danger%', 'moy_danger', 'id', 'titre'], axis=1), 
                       details['Danger%'], 
                       details['moy_danger']),
        'file_data': (summary.drop(['titre', 'danger_max', 'danger_moy', 'danger_std'], axis=1),
                      summary['danger_max'],
                      summary['danger_moy'],
                      summary['danger_std'])
    }

# 2. Préprocesseurs communs
class AudioPreprocessor:
    def __init__(self, numeric_features, categorical_features):
        self.preprocessor = ColumnTransformer([
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])
    
    def fit_transform(self, X):
        return self.preprocessor.fit_transform(X)
    
    def transform(self, X):
        return self.preprocessor.transform(X)

# 3. Modèles de base
class BaseModel:
    def __init__(self, preprocessor):
        self.preprocessor = preprocessor
        self.model = None
    
    def train(self, X, y):
        X_processed = self.preprocessor.fit_transform(X)
        
        # Configuration simplifiée
        models = [
            ('GradientBoosting', GradientBoostingRegressor(
                n_estimators=200, learning_rate=0.1, max_depth=5, random_state=42)),
            ('RandomForest', RandomForestRegressor(
                n_estimators=100, max_depth=10, random_state=42))
        ]
        
        best_score = -np.inf
        best_model = None
        
        for name, model in models:
            model.fit(X_processed, y)
            y_pred = model.predict(X_processed)
            score = r2_score(y, y_pred)
            
            if score > best_score:
                best_score = score
                best_model = model
        
        self.model = best_model
        return self
    
    def predict(self, X):
        X_processed = self.preprocessor.transform(X)
        if self.model is None:
            raise ValueError("Model is not trained yet.")
        return self.model.predict(X_processed)
    
    def evaluate(self, X, y):
        y_pred = self.predict(X)
        return {
            'r2': r2_score(y, y_pred),
            'mae': mean_absolute_error(y, y_pred)
        }

# 4. Modèles pour tranches audio
class SliceModels:
    def __init__(self):
        self.preprocessor = AudioPreprocessor(
            numeric_features=['amplitude', 'rms', 'dB', 'Peak', 'Score', 'env',
                            'centroid_mean', 'bandwidth_mean', 'flatness_mean',
                            'mfcc_mean', 'pcen_mean', 'zcr_mean'],
            categorical_features=['cri_type']
        )
        self.danger_model = BaseModel(self.preprocessor)
        self.moy_danger_model = BaseModel(self.preprocessor)
    
    def train(self, X, y_danger, y_moy):
        print("\nEntraînement modèle Danger%...")
        self.danger_model.train(X, y_danger)
        print(f"Performance: {self.danger_model.evaluate(X, y_danger)}")
        
        print("\nEntraînement modèle moy_danger...")
        self.moy_danger_model.train(X, y_moy)
        print(f"Performance: {self.moy_danger_model.evaluate(X, y_moy)}")
    
    def predict(self, X):
        return {
            'Danger%': self.danger_model.predict(X),
            'moy_danger': self.moy_danger_model.predict(X)
        }
    
    def save(self, path):
        joblib.dump({
            'preprocessor': self.preprocessor,
            'danger_model': self.danger_model.model,
            'moy_danger_model': self.moy_danger_model.model
        }, path)
    
    @classmethod
    def load(cls, path):
        data = joblib.load(path)
        instance = cls()
        instance.preprocessor = data['preprocessor']
        instance.danger_model.model = data['danger_model']
        instance.moy_danger_model.model = data['moy_danger_model']
        return instance

# 5. Modèles pour fichiers audio
class FileModels:
    def __init__(self):
        self.preprocessor = AudioPreprocessor(
            numeric_features=['nb_tranches', 'nb_cris', 'env_moy', 'rms_moy', 
                            'peak_moy', 'centroid_moy', 'bandwidth_moy', 
                            'mfcc_moy', 'pcen_moy'],
            categorical_features=['cri_type_dom']
        )
        self.max_model = BaseModel(self.preprocessor)
        self.moy_model = BaseModel(self.preprocessor)
        self.std_model = BaseModel(self.preprocessor)
    
    def train(self, X, y_max, y_moy, y_std):
        print("\nEntraînement modèle danger_max...")
        self.max_model.train(X, y_max)
        print(f"Performance: {self.max_model.evaluate(X, y_max)}")
        
        print("\nEntraînement modèle danger_moy...")
        self.moy_model.train(X, y_moy)
        print(f"Performance: {self.moy_model.evaluate(X, y_moy)}")
        
        print("\nEntraînement modèle danger_std...")
        self.std_model.train(X, y_std)
        print(f"Performance: {self.std_model.evaluate(X, y_std)}")
    
    def predict(self, X):
        return {
            'danger_max': self.max_model.predict(X),
            'danger_moy': self.moy_model.predict(X),
            'danger_std': self.std_model.predict(X)
        }
    
    def save(self, path):
        joblib.dump({
            'preprocessor': self.preprocessor,
            'max_model': self.max_model.model,
            'moy_model': self.moy_model.model,
            'std_model': self.std_model.model
        }, path)
    
    @classmethod
    def load(cls, path):
        data = joblib.load(path)
        instance = cls()
        instance.preprocessor = data['preprocessor']
        instance.max_model.model = data['max_model']
        instance.moy_model.model = data['moy_model']
        instance.std_model.model = data['std_model']
        return instance

# 6. Pipeline principal
def main():
    # Chargement des données
    print("Chargement des données...")
    data = load_and_prepare_data('data_details.csv', 'data_summary.csv')
    
    # Entraînement modèles tranches
    print("\n=== ENTRAÎNEMENT MODÈLES TRANCHES ===")
    slice_models = SliceModels()
    slice_models.train(*data['slice_data'])
    slice_models.save('slice_models.pkl')
    
    # Entraînement modèles fichiers
    print("\n=== ENTRAÎNEMENT MODÈLES FICHIERS ===")
    file_models = FileModels()
    file_models.train(*data['file_data'])
    file_models.save('file_models.pkl')
    
    # Exemple de prédiction
    print("\n=== EXEMPLE DE PRÉDICTION ===")
    sample_slice = data['slice_data'][0].iloc[0:1]
    print("Prédiction tranche:", slice_models.predict(sample_slice))
    
    sample_file = data['file_data'][0].iloc[0:1]
    print("Prédiction fichier:", file_models.predict(sample_file))

if __name__ == "__main__":
    main()