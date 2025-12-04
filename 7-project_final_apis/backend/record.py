import sounddevice as sd
from scipy.io.wavfile import write
import os

duree = 5
frequence = 44100
chemin_sortie = "../data/enregistrement.wav"

print("🎙️ Prépare-toi... Enregistrement dans 3 secondes...")
sd.sleep(3000)

print("🎙️ Enregistrement en cours...")
audio = sd.rec(int(duree * frequence), samplerate=frequence, channels=1, dtype='int16')
sd.wait()
print("✅ Enregistrement terminé.")

os.makedirs(os.path.dirname(chemin_sortie), exist_ok=True)
write(chemin_sortie, frequence, audio)

print(f"📁 Audio sauvegardé ici : {chemin_sortie}")
