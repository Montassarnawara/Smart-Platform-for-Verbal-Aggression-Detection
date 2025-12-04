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
from scipy.io import wavfile
import numpy as np
import os

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API audio 🎙️"}

@app.get("/analyse")
def analyse_audio():
    chemin_audio = "../data/enregistrement.wav"
    if not os.path.exists(chemin_audio):
        return {"error": "Fichier audio non trouvé. Lance record.py"}

    frequence, data = wavfile.read(chemin_audio)
    amplitude_moyenne = float(np.mean(np.abs(data)))
    amplitude_max = int(np.max(np.abs(data)))

    return {
        "frequence": frequence,
        "amplitude_moyenne": amplitude_moyenne,
        "amplitude_max": amplitude_max,
        "nb_echantillons": len(data)
    }
