"""
Classes nécessaires pour la désérialisation des modèles ML
"""
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

class AudioPreprocessor:
    """Preprocessor pour les données audio"""
    def __init__(self, numeric_features, categorical_features):
        self.preprocessor = ColumnTransformer([
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])
    
    def transform(self, X):
        return self.preprocessor.transform(X)

class ModelContainer:
    """Conteneur pour modèle avec preprocessing intégré"""
    def __init__(self, preprocessor, model):
        self.preprocessor = preprocessor
        self.model = model
    
    def predict(self, X):
        return self.model.predict(self.preprocessor.transform(X))
