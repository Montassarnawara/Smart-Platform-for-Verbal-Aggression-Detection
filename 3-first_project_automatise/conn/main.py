from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.responses import JSONResponse

app = FastAPI()

class SoundLevels(BaseModel):
    levels: List[int]  # Une liste de niveaux sonores


@app.get("/")
async def root():
    return {"message": "ESP32 Alert API is running 🚀"}


@app.post("/danger-alert")
async def analyze_levels(data: SoundLevels):
    values = data.levels
    if not values:
        return JSONResponse(status_code=400, content={"error": "Empty levels"})

    avg = round(sum(values) / len(values), 2)
    print(f"📥 Reçu niveaux: {values}")
    print(f"📊 Moyenne: {avg}")

    if avg > 90:
        percent = 90
    elif avg > 70:
        percent = 70
    elif avg > 50:
        percent = 50
    else:
        percent = 20

    return {"danger": percent > 50, "percent": percent}


