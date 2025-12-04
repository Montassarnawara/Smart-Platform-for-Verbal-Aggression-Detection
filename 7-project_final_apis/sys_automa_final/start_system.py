#!/usr/bin/env python3
"""
Script de lancement du système complet d'analyse audio avec IA
"""

import subprocess
import time
import sys
import requests
import os

def check_port(port):
    """Vérifier si un port est utilisé"""
    try:
        response = requests.get(f"http://localhost:{port}/", timeout=2)
        return True
    except:
        return False

def start_danger_alert_api():
    """Démarrer l'API danger_alert sur le port 8001"""
    print("🚀 Démarrage de l'API danger_alert (port 8001)...")
    
    # Vérifier si déjà en cours
    if check_port(8001):
        print("⚠️ API danger_alert déjà en cours sur le port 8001")
        return None
    
    # Démarrer l'API
    process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "danger_alert:app", 
        "--host", "0.0.0.0", 
        "--port", "8001",
        "--reload"
    ], cwd=os.getcwd())
    
    # Attendre que l'API soit prête
    for _ in range(30):  # 30 secondes max
        time.sleep(1)
        if check_port(8001):
            print("✅ API danger_alert prête !")
            return process
    
    print("❌ Échec du démarrage de l'API danger_alert")
    process.terminate()
    return None

def start_audio_api():
    """Démarrer l'API audio principale sur le port 8000"""
    print("🚀 Démarrage de l'API audio principale (port 8000)...")
    
    # Vérifier si déjà en cours
    if check_port(8000):
        print("⚠️ API audio déjà en cours sur le port 8000")
        return None
    
    # Démarrer l'API
    process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "audio_api_system:app", 
        "--host", "0.0.0.0", 
        "--port", "8000",
        "--reload"
    ], cwd=os.getcwd())
    
    # Attendre que l'API soit prête
    for _ in range(15):  # 15 secondes max
        time.sleep(1)
        if check_port(8000):
            print("✅ API audio principale prête !")
            return process
    
    print("❌ Échec du démarrage de l'API audio")
    process.terminate()
    return None

def test_system():
    """Tester le système complet"""
    print("\n🧪 Test du système complet...")
    
    try:
        # Test de l'API principale
        response = requests.get("http://localhost:8000/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print("✅ Status système:", status)
        else:
            print("❌ Erreur status système")
            return False
        
        # Test complet
        response = requests.get("http://localhost:8000/test_full_system", timeout=30)
        if response.status_code == 200:
            result = response.json()
            print("✅ Test complet réussi:", result.get("message", "OK"))
            return True
        else:
            print("❌ Test complet échoué")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Fonction principale"""
    print("=" * 60)
    print("🎵 SYSTÈME D'ANALYSE AUDIO AVEC IA - DÉMARRAGE")
    print("=" * 60)
    
    processes = []
    
    try:
        # 1. Démarrer l'API danger_alert
        danger_process = start_danger_alert_api()
        if danger_process:
            processes.append(danger_process)
        
        # 2. Démarrer l'API audio principale
        audio_process = start_audio_api()
        if audio_process:
            processes.append(audio_process)
        
        # 3. Vérifier que tout fonctionne
        if len(processes) >= 1:  # Au moins l'API audio
            time.sleep(2)
            print("\n" + "=" * 60)
            print("🎯 URLS DISPONIBLES:")
            print("  • API Audio: http://localhost:8000")
            print("  • Documentation: http://localhost:8000/docs")
            if danger_process:
                print("  • API IA: http://localhost:8001")
                print("  • Doc IA: http://localhost:8001/docs")
            print("=" * 60)
            
            # Test du système
            test_system()
            
            print("\n✨ Système prêt ! Appuyez sur Ctrl+C pour arrêter.")
            
            # Attendre l'arrêt
            while True:
                time.sleep(1)
        else:
            print("❌ Aucune API n'a pu être démarrée")
    
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du système...")
    
    finally:
        # Arrêter tous les processus
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        print("✅ Système arrêté proprement")

if __name__ == "__main__":
    main()
