from fastapi import FastAPI
from pymongo import MongoClient
from pydantic import BaseModel

app = FastAPI()

# Connexion MongoDB Atlas
MONGO_URL = " mongodb+srv://your_username:your_password@your_cluster.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URL)
db = client["son_danger"]
collection = db["alertes"]

class SoundAlert(BaseModel):
    danger: bool
    level: int

@app.post("/danger-alert")
async def receive_alert(data: SoundAlert):
    collection.insert_one(data.dict())

    level = data.level
    if level > 90:
        percent = 90
    elif level > 70:
        percent = 60
    elif level > 50:
        percent = 40
    else:
        percent = 20

    return {"danger": True, "percent": percent}