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
from record import start_recording
from analyze import analyze_directory, extract_amplitudes, AudioFeatureExtractor
import os
from logic_controller_advanced import start_analysis_cycle_advanced, start_analysis_cycle
import requests




app = FastAPI()

rec_status = {"rec": False}

@app.get("/run_cycle_advanced")
def run_full_cycle_advanced():
    """Lance le cycle d'analyse avancé avec IA et modèles ML"""
    result = start_analysis_cycle_advanced()
    return result

@app.get("/run_cycle")
def run_full_cycle():
    """Lance le cycle d'analyse simple (compatibilité)"""
    avg = start_analysis_cycle()
    return {"average_danger": avg}

@app.get("/start_sys")
def start_system():
    """Point de départ : affiche un message et active la détection."""
    rec_status["rec"] = True
    return {"message": "Système initialisé. En attente de détection..."}

@app.get("/detection")
def trigger_detection():
    rec_status["rec"] = True
    return {"message": "Détection activée. Enregistrement en attente."}

@app.get("/Ndetection")
def trigger_Ndetection():
    rec_status["rec"] = False
    return {"message": "Détection stoppée."}

@app.get("/check_and_record_advanced")
def check_and_record_advanced():
    """Enregistrement et analyse avancée avec IA"""
    rec_status["rec"] = True
    if rec_status["rec"]:
        print("🎙️ Enregistrement avancé démarré...")
        
        try:
            # 1. Enregistrer l'audio (5 secondes)
            analyses = start_recording()
            
            # 2. Récupérer le dernier fichier enregistré
            files = sorted(f for f in os.listdir("audio_chunks") if f.endswith(".wav"))
            if not files:
                return {"status": "error", "message": "Aucun fichier audio trouvé."}

            last_file = os.path.join("audio_chunks", files[-1])
            print(f"📁 Fichier enregistré : {last_file}")
            
            # 3. Analyse avancée avec AudioFeatureExtractor
            extractor = AudioFeatureExtractor()
            analysis_result = extractor.process_audio_file(last_file)
            
            if not analysis_result["detail"]:
                return {"status": "error", "message": "Échec de l'analyse audio avancée."}
            
            print(f"✅ Analyse avancée réussie: {len(analysis_result['detail'])} tranches analysées")
            
            # 4. Envoi à l'IA pour détection de danger avancée
            try:
                r3 = requests.post("http://localhost:8001/danger-alert-advanced", json=analysis_result)
                if r3.status_code == 200:
                    ai_result = r3.json()
                    print(f"🤖 Analyse IA terminée: {ai_result['percent']}% de danger")
                else:
                    ai_result = {"error": f"Erreur API IA: {r3.status_code}"}
            except Exception as e:
                ai_result = {"error": f"Erreur connexion IA: {str(e)}"}

            rec_status["rec"] = False

            return {
                "status": "done",
                "file": files[-1],
                "analysis": analysis_result,
                "danger_analysis": ai_result,
                "summary": {
                    "nb_tranches": len(analysis_result["detail"]),
                    "danger_percent": ai_result.get("percent", 0),
                    "cris_detectes": sum(1 for d in analysis_result["detail"] if d.get('cri', False))
                }
            }
            
        except Exception as e:
            rec_status["rec"] = False
            return {"status": "error", "message": f"Erreur lors de l'enregistrement avancé: {str(e)}"}
    else:
        return {"status": "waiting"}

@app.get("/check_and_record")
def check_and_record():
    """Enregistrement et analyse simple (compatibilité)"""
    rec_status["rec"] = True
    if rec_status["rec"]:
        print("🎙️ Enregistrement simple démarré...")
        
        try:
            # 1. Enregistrer l'audio (analyse locale)
            analyses = start_recording()
            
            # 2. Extraire les amplitudes les plus récentes (5 secondes)
            files = sorted(f for f in os.listdir("audio_chunks") if f.endswith(".wav"))
            if not files:
                return {"status": "error", "message": "Aucun fichier audio trouvé."}

            last_file = os.path.join("audio_chunks", files[-1])
            amplitudes = extract_amplitudes(last_file, limit=50)  # par exemple 50 points

            # 3. Envoi à l'IA pour détection de danger simple
            try:
                r3 = requests.post("http://localhost:8001/danger-alert", json={
                    "amplitudes": amplitudes
                })
                result = r3.json()
            except Exception as e:
                result = {"error": str(e)}

            rec_status["rec"] = False

            return {
                "status": "done",
                "danger_analysis": result,
                "file": files[-1]
            }
            
        except Exception as e:
            rec_status["rec"] = False
            return {"status": "error", "message": f"Erreur lors de l'enregistrement: {str(e)}"}
    else:
        return {"status": "waiting"}


@app.get("/analyse_advanced")
def get_advanced_analysis():
    """Analyse avancée de tous les fichiers audio"""
    try:
        extractor = AudioFeatureExtractor()
        results = []
        
        files = sorted(f for f in os.listdir("audio_chunks") if f.endswith(".wav"))
        if not files:
            return {"error": "Aucun fichier audio trouvé dans audio_chunks."}
        
        for filename in files:
            file_path = os.path.join("audio_chunks", filename)
            analysis = extractor.process_audio_file(file_path)
            results.append({
                "filename": filename,
                "analysis": analysis
            })
        
        return {"analyses": results}
        
    except Exception as e:
        return {"error": f"Erreur lors de l'analyse avancée: {str(e)}"}

@app.get("/analyse")
def get_all_analyses():
    """Analyse simple de tous les fichiers"""
    return analyze_directory("audio_chunks")

@app.get("/analyse/{n}")
def get_amplitudes(n: int):
    """Extraire n amplitudes du dernier fichier"""
    files = sorted(f for f in os.listdir("audio_chunks") if f.endswith(".wav"))
    if not files:
        return {"error": "Aucun fichier audio trouvé dans audio_chunks."}

    last_file = os.path.join("audio_chunks", files[len(files)-1])
    amplitudes = extract_amplitudes(last_file, limit=n)
    return {"file": files[-1], "amplitudes": amplitudes}

@app.get("/status")
def get_system_status():
    """Obtenir le statut du système"""
    try:
        # Vérifier les fichiers audio disponibles
        audio_files = []
        if os.path.exists("audio_chunks"):
            audio_files = sorted(f for f in os.listdir("audio_chunks") if f.endswith(".wav"))
        
        # Vérifier la connexion à l'API IA
        ia_status = "unknown"
        try:
            response = requests.get("http://localhost:8001/models-status", timeout=2)
            if response.status_code == 200:
                ia_data = response.json()
                ia_status = "connected" if ia_data.get("models_available", False) else "models_not_loaded"
            else:
                ia_status = "error"
        except:
            ia_status = "disconnected"
        
        return {
            "recording_status": rec_status["rec"],
            "audio_files_count": len(audio_files),
            "latest_file": audio_files[-1] if audio_files else None,
            "ia_api_status": ia_status,
            "system_ready": len(audio_files) > 0 and ia_status == "connected"
        }
        
    except Exception as e:
        return {"error": f"Erreur lors de la vérification du statut: {str(e)}"}

@app.get("/test_full_system")
def test_full_system():
    """Test complet du système : enregistrement → analyse → IA"""
    try:
        print("🧪 Test complet du système démarré...")
        
        # 1. Test d'enregistrement
        record_result = check_and_record_advanced()
        if record_result.get("status") != "done":
            return {"error": "Échec du test d'enregistrement", "details": record_result}
        
        print("✅ Test d'enregistrement réussi")
        
        # 2. Test de connexion IA
        try:
            ia_status = requests.get("http://localhost:8001/models-status", timeout=5)
            if ia_status.status_code != 200:
                return {"error": "API IA non accessible", "status_code": ia_status.status_code}
        except Exception as e:
            return {"error": f"Connexion IA échouée: {str(e)}"}
        
        print("✅ Test de connexion IA réussi")
        
        return {
            "status": "success",
            "message": "Système entièrement fonctionnel",
            "record_test": "✅ OK",
            "ia_connection": "✅ OK",
            "last_analysis": record_result.get("summary", {})
        }
        
    except Exception as e:
        return {"error": f"Erreur lors du test complet: {str(e)}"}
