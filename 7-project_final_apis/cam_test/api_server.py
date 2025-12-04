# api_server.py
from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.get("/camera")
def lancer_camera():
    try:
        subprocess.Popen(["python", "camera_capture.py"])
        return {"status": "success", "message": "Caméra lancée pour 5 secondes"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
