"""Test minimal pour vérifier l'API"""
print("🔄 Test de démarrage de l'API...")

try:
    import danger_alert
    print("✅ Import de danger_alert réussi")
    
    # Test du chargement des modèles
    result = danger_alert.load_models()
    print(f"📊 Résultat du chargement: {result}")
    
    if result:
        print("✅ L'API devrait démarrer correctement maintenant!")
        print("🚀 Vous pouvez démarrer l'API avec: uvicorn danger_alert:app --reload --port 8001")
    else:
        print("❌ Problème avec le chargement des modèles")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
