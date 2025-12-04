import os
import numpy as np
import scipy.io.wavfile as wav
import csv

# ========== Fonction d’analyse ==========
def analyze_amplitudes(amplitudes):
    amplitudes = np.array(amplitudes)
    if amplitudes.size == 0:
        return {
            "percent": 0, "rms": 0, "db": 0,
            "peak": 0, "variation": 0, "score": 0
        }

    rms = np.sqrt(np.mean(amplitudes ** 2))
    db_rms = 20 * np.log10(rms + 1e-6) + 100
    peak = np.max(np.abs(amplitudes))
    variation = np.std(amplitudes)
    score = 0.4 * db_rms + 30 * peak + 20 * variation
    danger_percent = min(100, int(score))

    return {
        "percent": danger_percent,
        "rms": float(rms),
        "db": float(db_rms),
        "peak": float(peak),
        "variation": float(variation),
        "score": float(score)
    }

# ========== Analyse de tous les fichiers ==========
def process_directory(directory="son/", output_csv="resultats.csv"):
    output_data = []
    id_counter = 1

    for filename in os.listdir(directory):
        if filename.endswith(".wav"):
            filepath = os.path.join(directory, filename)
            print(f"\n🎵 Traitement de {filename}...")

            # Lecture du fichier
            sample_rate, data = wav.read(filepath)
            if len(data.shape) == 2:
                data = data.mean(axis=1)

            duration = len(data) / sample_rate
            step = int(sample_rate / 100)  # 100Hz = 1 valeur / 10ms
            sampled_data = data[::step]
            max_amplitude = np.max(np.abs(sampled_data))
            if max_amplitude == 0:
                continue
            normalized_data = sampled_data / max_amplitude

            samples_per_chunk = 5 * 100  # 5 secondes * 100 échantillons/sec
            num_chunks = len(normalized_data) // samples_per_chunk
            total_danger = 0

            for i in range(num_chunks):
                start = i * samples_per_chunk
                end = start + samples_per_chunk
                chunk = normalized_data[start:end]
                analysis = analyze_amplitudes(chunk)
                total_danger += analysis["percent"]

                output_data.append([
                    id_counter,
                    filename,
                    analysis["rms"],
                    analysis["db"],
                    analysis["peak"],
                    analysis["variation"],
                    analysis["score"],
                    analysis["percent"],
                    None  # moy_danger à remplir après
                ])
                id_counter += 1

            # Moyenne danger% pour ce fichier
            moy_danger = total_danger / max(1, num_chunks)
            for row in output_data[-num_chunks:]:
                row[-1] = moy_danger

    # Écriture dans le CSV
    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "id", "titre", "rms", "dB", "Peak",
            "StdDev", "Score", "Danger%", "moy_danger"
        ])
        writer.writerows(output_data)

    print(f"\n✅ Résultats sauvegardés dans {output_csv}")

# ========== Exécution principale ==========
if __name__ == "__main__":
    process_directory()
