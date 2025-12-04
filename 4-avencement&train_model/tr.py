import numpy as np
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt

# === 1. Charger un fichier audio WAV ===
sample_rate, data = wav.read("sing.wav")  # Exemple : 44100 Hz

# === 2. Convertir en mono si stéréo ===
if len(data.shape) == 2:
    data = data.mean(axis=1)

# === 3. Durée totale du signal (en secondes) ===
duration = len(data) / sample_rate
print(f"Durée : {duration:.2f} s")

# === 4. Fréquence d’échantillonnage souhaitée ===
target_rate = 100  # 100 Hz → 1 valeur toutes les 10 ms

# === 5. Indices des échantillons à conserver ===
step = int(sample_rate / target_rate)
sampled_data = data[::step]

# === 6. Normaliser les amplitudes entre -1 et 1 (optionnel) ===
max_amplitude = np.max(np.abs(sampled_data))
normalized_data = sampled_data / max_amplitude

# === 7. Résultat : liste des amplitudes ===
amplitudes_list = normalized_data.tolist()

# Afficher les 10 premières amplitudes
print("Amplitudes échantillonnées :", amplitudes_list[:200])

# === 8. Visualiser ===
plt.plot(amplitudes_list[0:600])
plt.title("Amplitude du signal (échantillonnée à 100 Hz)")
plt.xlabel("échantillon")
plt.ylabel("Amplitude")
plt.grid()
plt.show()
