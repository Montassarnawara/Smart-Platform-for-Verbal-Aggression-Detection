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


import numpy as np
import scipy.io.wavfile as wav
import os

def analyze_audio_chunk(filepath):
    rate, data = wav.read(filepath)

    if len(data.shape) == 2:  # stéréo → mono
        data = data.mean(axis=1)

    duration = len(data) / rate
    max_amp = float(np.max(np.abs(data)))
    mean_amp = float(np.mean(np.abs(data)))

    return {
        "file": filepath,
        "frequence": rate,
        "duration": round(duration, 2),
        "max_amplitude": round(max_amp, 4),
        "mean_amplitude": round(mean_amp, 4),
        "nb_echantillons": len(data)
    }

def extract_amplitudes(filepath: str, target_rate: int = 100, limit: int = 50):
    if not os.path.exists(filepath):
        return {"error": "Fichier audio non trouvé."}

    sample_rate, data = wav.read(filepath)

    if len(data.shape) == 2:
        data = data.mean(axis=1)

    step = int(sample_rate / target_rate)
    sampled_data = data[::step]

    max_amplitude = np.max(np.abs(sampled_data))
    normalized_data = sampled_data / max_amplitude

    return normalized_data[:limit].tolist()

def analyze_directory(directory):
    results = []
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".wav"):
            path = os.path.join(directory, filename)
            analysis = analyze_audio_chunk(path)
            results.append(analysis)
    return {"analyses": results}
