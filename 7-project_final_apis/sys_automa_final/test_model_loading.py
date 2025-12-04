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



"""
Script de test pour vérifier le chargement des modèles
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from model_classes import AudioPreprocessor, ModelContainer
import joblib

def test_model_loading():
    """Test de chargement des modèles"""
    try:
        print("🔄 Test de chargement des modèles...")
        
        # Ajouter les classes au module __main__ pour la désérialisation
        import __main__
        __main__.AudioPreprocessor = AudioPreprocessor
        __main__.ModelContainer = ModelContainer
        
        # Charger les modèles
        print("Chargement de slice_models.pkl...")
        slice_data = joblib.load('slice_models.pkl')
        print(f"Clés dans slice_data: {list(slice_data.keys())}")
        
        print("Chargement de file_models.pkl...")
        file_data = joblib.load('file_models.pkl')
        print(f"Clés dans file_data: {list(file_data.keys())}")
        
        print("✅ Chargement des modèles réussi!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

if __name__ == "__main__":
    test_model_loading()
