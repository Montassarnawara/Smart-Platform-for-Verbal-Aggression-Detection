from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import numpy as np


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AmplitudeData(BaseModel):
    amplitudes: List[float]

@app.post("/danger-alert")
async def analyze_amplitudes(data: AmplitudeData):
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
