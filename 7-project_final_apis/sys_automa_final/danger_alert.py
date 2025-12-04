# Copyright 2025 Montassar Nawara
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.





from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import numpy as np
import pandas as pd
import joblib
import os
import sys
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

# Classes nécessaires pour la désérialisation des modèles
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


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AudioAnalysisData(BaseModel):
    detail: List[Dict[str, Any]]  # Liste des tranches analysées
    summary: Dict[str, Any]       # Résumé global

class AmplitudeData(BaseModel):
    amplitudes: List[float]

# Variables globales pour les modèles (chargés au démarrage)
slice_models = None
file_models = None

def load_models():
    """Charge les modèles pré-entraînés"""
    global slice_models, file_models
    
    try:
        print("🔄 Chargement des modèles...")
        
        # SOLUTION DÉFINITIVE : Ajouter les classes au module __main__ AVANT le chargement
        import __main__
        setattr(__main__, 'AudioPreprocessor', AudioPreprocessor)
        setattr(__main__, 'ModelContainer', ModelContainer)
        
        # Charger directement les données des modèles
        slice_data = joblib.load('slice_models.pkl')
        file_data = joblib.load('file_models.pkl')
        
        print(f"Clés dans slice_data: {list(slice_data.keys())}")
        print(f"Clés dans file_data: {list(file_data.keys())}")
        
        # Charger directement les modèles et preprocessors
        slice_models = {
            'danger_model': slice_data['danger_model'],
            'moy_danger_model': slice_data['moy_danger_model'],
            'preprocessor': slice_data['preprocessor']
        }
        
        file_models = {
            'max_model': file_data['max_model'],
            'moy_model': file_data['moy_model'], 
            'std_model': file_data['std_model'],
            'preprocessor': file_data['preprocessor']
        }
        
        print("✅ Modèles chargés avec succès - DÉFINITIVEMENT RÉPARÉ!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du chargement des modèles: {str(e)}")
        # Tentative alternative si le problème persiste
        try:
            print("� Tentative de récupération...")
            
            # Forcer l'ajout des classes dans tous les modules possibles
            import __main__
            setattr(__main__, 'AudioPreprocessor', AudioPreprocessor)
            setattr(__main__, 'ModelContainer', ModelContainer)
            
            # Re-essayer le chargement
            slice_data = joblib.load('slice_models.pkl')
            file_data = joblib.load('file_models.pkl')
            
            slice_models = {
                'danger_model': slice_data['danger_model'],
                'moy_danger_model': slice_data['moy_danger_model'],
                'preprocessor': slice_data['preprocessor']
            }
            
            file_models = {
                'max_model': file_data['max_model'],
                'moy_model': file_data['moy_model'], 
                'std_model': file_data['std_model'],
                'preprocessor': file_data['preprocessor']
            }
            
            print("✅ Modèles chargés avec succès en mode récupération!")
            return True
            
        except Exception as e2:
            print(f"❌ Échec définitif: {str(e2)}")
            print("💡 Les fichiers de modèles nécessitent peut-être d'être re-générés")
            return False

# Charger les modèles au démarrage de l'API
@app.on_event("startup")
async def startup_event():
    load_models()

@app.post("/danger-alert-advanced")
async def analyze_audio_advanced(data: AudioAnalysisData):
    """Analyse avancée avec modèles ML sur les données d'analyse audio complète"""
    global slice_models, file_models
    
    if not slice_models or not file_models or 'danger_model' not in slice_models or 'max_model' not in file_models:
        return {"error": "Modèles non chargés correctement", "percent": 0}
    
    try:
        # Convertir les données en DataFrame
        if not data.detail:
            return {"error": "Aucune donnée de tranche fournie", "percent": 0}
        
        details_df = pd.DataFrame(data.detail)
        summary_dict = data.summary
        
        # Préparer les données pour les prédictions sur les tranches
        # ORDRE EXACT selon le modèle entraîné
        required_slice_features = [
            'amplitude', 'rms', 'dB', 'Peak', 'Score', 'env',
            'centroid_mean', 'bandwidth_mean', 'flatness_mean',
            'mfcc_mean', 'pcen_mean', 'zcr_mean', 'cri_type'
        ]
        
        # Vérifier que toutes les features nécessaires sont présentes
        missing_features = [f for f in required_slice_features if f not in details_df.columns]
        if missing_features:
            print(f"Features manquantes: {missing_features}")
            print(f"Colonnes disponibles: {list(details_df.columns)}")
            return {"error": f"Features manquantes: {missing_features}", "percent": 0}
        
        # Sélectionner les features dans l'ordre exact
        X_slice = details_df[required_slice_features]
        print(f"Ordre des features pour prédiction: {list(X_slice.columns)}")
        print(f"Forme des données: {X_slice.shape}")
        
        # Prédictions sur les tranches
        try:
            # Mode direct avec preprocessor séparé
            X_slice_processed = slice_models['preprocessor'].transform(X_slice)
            slice_predictions = {
                'Danger%': slice_models['danger_model'].predict(X_slice_processed),
                'moy_danger': slice_models['moy_danger_model'].predict(X_slice_processed)
            }
            print(f"Prédictions tranches réussies. Shapes: Danger%={len(slice_predictions['Danger%'])}, moy_danger={len(slice_predictions['moy_danger'])}")
        except Exception as e:
            print(f"Erreur lors des prédictions sur les tranches: {str(e)}")
            return {"error": f"Erreur prédictions tranches: {str(e)}", "percent": 0}
        
        # Prédictions sur le fichier (si données de résumé disponibles)
        file_predictions = {}
        required_file_features = [
            'nb_tranches', 'nb_cris', 'env_moy', 'rms_moy', 
            'peak_moy', 'centroid_moy', 'bandwidth_moy',
            'mfcc_moy', 'pcen_moy', 'cri_type_dom'
        ]
        
        if summary_dict and all(k in summary_dict for k in required_file_features):
            summary_df = pd.DataFrame([summary_dict])
            
            X_file = summary_df[required_file_features]
            print(f"Ordre des features fichier: {list(X_file.columns)}")
            print(f"Forme des données fichier: {X_file.shape}")
            
            try:
                # Mode direct avec preprocessor séparé
                X_file_processed = file_models['preprocessor'].transform(X_file)
                file_predictions = {
                    'danger_max': float(file_models['max_model'].predict(X_file_processed)[0]),
                    'danger_moy': float(file_models['moy_model'].predict(X_file_processed)[0]),
                    'danger_std': float(file_models['std_model'].predict(X_file_processed)[0])
                }
                print(f"Prédictions fichier réussies: {file_predictions}")
            except Exception as e:
                print(f"Erreur lors des prédictions sur le fichier: {str(e)}")
                file_predictions = {"error": f"Erreur prédictions fichier: {str(e)}"}
        else:
            missing_summary_keys = [k for k in required_file_features if k not in summary_dict] if summary_dict else required_file_features
            print(f"Données de résumé insuffisantes. Clés manquantes: {missing_summary_keys}")
        
        # Calculer le pourcentage de danger global
        danger_percent = int(np.mean(slice_predictions['Danger%']))
        
        return {
            "percent": danger_percent,
            "slice_predictions": {
                "danger_percentages": [float(x) for x in slice_predictions['Danger%']],
                "moy_danger": [float(x) for x in slice_predictions['moy_danger']],
                "average_danger": float(np.mean(slice_predictions['Danger%'])),
                "max_danger": float(np.max(slice_predictions['Danger%'])),
                "min_danger": float(np.min(slice_predictions['Danger%']))
            },
            "file_predictions": file_predictions,
            "analysis_summary": {
                "nb_tranches": len(details_df),
                "nb_cris_detectes": sum(1 for d in data.detail if d.get('cri', False)),
                "cri_types": list(set(d.get('cri_type', 'aucun') for d in data.detail if d.get('cri', False)))
            }
        }
        
    except Exception as e:
        print(f"Erreur dans l'analyse avancée: {str(e)}")
        return {"error": f"Erreur d'analyse: {str(e)}", "percent": 0}

@app.post("/danger-alert")
async def analyze_amplitudes(data: AmplitudeData):
    """Analyse simple des amplitudes (compatible avec l'ancienne version)"""
    amplitudes = np.array(data.amplitudes)

    # Sécurité : vérifier si données vides
    if amplitudes.size == 0:
        return {"percent": 0, "message": "Aucune donnée reçue"}

    # 1. RMS (volume global)
    rms = np.sqrt(np.mean(amplitudes ** 2))
    db_rms = 20 * np.log10(rms + 1e-6) + 100  # +1e-6 pour éviter log(0)

    # 2. Pic d’amplitude
    peak = np.max(np.abs(amplitudes))

    # 3. Variation (écart-type)
    variation = np.std(amplitudes)

    # Pondération personnalisée (à ajuster selon expérimentation)
    score = 0.4 * db_rms + 30 * peak + 20 * variation

    # Normalisation du score dans une plage [0, 100]
    danger_percent = min(100, int(score))

    print(f"RMS: {rms:.4f}, dB: {db_rms:.2f}, Peak: {peak:.3f}, StdDev: {variation:.4f} => Score: {score:.2f}, Danger%: {danger_percent}")

    return {
        "percent": danger_percent,
        "details": {
            "rms": float(rms),
            "db": float(db_rms),
            "peak": float(peak),
            "variation": float(variation)
        }
    }

@app.get("/models-status")
async def get_models_status():
    """Vérifier le statut des modèles chargés"""
    slice_loaded = slice_models is not None and 'danger_model' in slice_models
    file_loaded = file_models is not None and 'max_model' in file_models
    return {
        "slice_models_loaded": slice_loaded,
        "file_models_loaded": file_loaded,
        "models_available": slice_loaded and file_loaded,
        "slice_models_keys": list(slice_models.keys()) if slice_models else [],
        "file_models_keys": list(file_models.keys()) if file_models else []
    }
