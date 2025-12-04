import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import os

chemin_audio = "../data/enregistrement.wav"

# Charger l’audio
if not os.path.exists(chemin_audio):
    raise FileNotFoundError("Fichier audio non trouvé. Lance d'abord record.py")

frequence, data = wavfile.read(chemin_audio)
temps = np.linspace(0, len(data) / frequence, num=len(data))

# Analyse
amplitude_moyenne = float(np.mean(np.abs(data)))
amplitude_max = int(np.max(np.abs(data)))

print(f"📊 Amplitude moyenne : {amplitude_moyenne:.2f}")
print(f"📊 Amplitude max     : {amplitude_max}")

# Graphique
plt.figure(figsize=(10, 4))
plt.plot(temps, data)
plt.title("Amplitude du son dans le temps")
plt.xlabel("Temps [s]")
plt.ylabel("Amplitude")
plt.grid(True)
plt.tight_layout()
plt.show()
