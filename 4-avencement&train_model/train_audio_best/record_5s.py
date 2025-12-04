import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np

# === Paramètres ===
DURATION = 5  # secondes
SAMPLE_RATE = 44100  # Hz
OUTPUT_FILE = "recorded_5s.wav"

print("🎙️ Enregistrement en cours... (5s)")
audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
sd.wait()
print("✅ Enregistrement terminé.")

# Sauvegarde fichier
wav.write(OUTPUT_FILE, SAMPLE_RATE, audio)
print(f"💾 Fichier sauvegardé sous : {OUTPUT_FILE}")
