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
from analyze import analyze_directory, extract_amplitudes
import os
from logic_controller import start_analysis_cycle
import requests




app = FastAPI()

rec_status = {"rec": False}

@app.get("/run_cycle")
def run_full_cycle():
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

@app.get("/check_and_record")


def check_and_record():
    rec_status["rec"] = True
    if rec_status["rec"]:
        print("Recording started...")
        
        # 1. Enregistrer l'audio (analyse locale)
        analyses = start_recording()
        
        # 2. Extraire les amplitudes les plus récentes (5 secondes)
        from analyze import extract_amplitudes
        import os
        files = sorted(f for f in os.listdir("audio_chunks") if f.endswith(".wav"))
        if not files:
            return {"status": "error", "message": "Aucun fichier audio trouvé."}

        last_file = os.path.join("audio_chunks", files[-1])
        amplitudes = extract_amplitudes(last_file, limit=50)  # par exemple 50 points

        # 3. Envoi à l'IA pour détection de danger
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
    else:
        return {"status": "waiting"}


@app.get("/analyse")
def get_all_analyses():
    return analyze_directory("audio_chunks")

@app.get("/analyse/{n}")
def get_amplitudes(n: int):
    files = sorted(f for f in os.listdir("audio_chunks") if f.endswith(".wav"))
    if not files:
        return {"error": "Aucun fichier audio trouvé dans audio_chunks."}

    last_file = os.path.join("audio_chunks", files[len(files)-1])
    amplitudes = extract_amplitudes(last_file, limit=n)
    return {"file": files[-1], "amplitudes": amplitudes}
