#!/usr/bin/env python3
"""Test simple pour vérifier le chargement des modèles dans l'API"""

import sys
import os

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Importer la fonction de chargement depuis danger_alert
    from danger_alert import load_models
    
    print("🔄 Test de chargement des modèles dans l'API...")
    
    # Tester le chargement
    success = load_models()
    
    if success:
        print("✅ Les modèles se chargent correctement dans l'API!")
        
        # Importer les variables globales pour vérifier
        from danger_alert import slice_models, file_models
        
        print(f"Slice models keys: {list(slice_models.keys()) if slice_models else 'None'}")
        print(f"File models keys: {list(file_models.keys()) if file_models else 'None'}")
        
    else:
        print("❌ Échec du chargement des modèles")
        
except Exception as e:
    print(f"❌ Erreur lors du test: {str(e)}")
    import traceback
    traceback.print_exc()
