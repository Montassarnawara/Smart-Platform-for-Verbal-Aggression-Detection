import os
import math
import numpy as np
import pandas as pd
import soundfile as sf
from scipy.signal import resample

# Configuration
DOSSIER_SON = "son_test"
DUREE_FENETRE = 5  # secondes
CSV_SORTIE = "resultats_audio_son_test.csv"
TAUX_ECHANTILLONNAGE = 44100  # Hz

def analyse_tranche(tranche):
    rms = np.sqrt(np.mean(tranche ** 2))
    dB = 20 * np.log10(rms + 1e-6)
    peak = np.max(np.abs(tranche))
    std = np.std(tranche)

    # Score linéaire entre 0 et 100
    score = (rms / 1.0) * 100
    score = min(score, 100)

    # Danger (%) basé sur des seuils arbitraires
    if dB > 90 or peak > 0.9:
        danger = 100
    elif dB > 85:
        danger = 80
    elif dB > 80:
        danger = 60
    elif dB > 70:
        danger = 40
    elif dB > 60:
        danger = 20
    else:
        danger = 10

    return {
        "amplitude": rms,
        "rms": rms,
        "dB": dB,
        "Peak": peak,
        "StdDev": std,
        "Score": score,
        "Danger%": danger
    }

def traiter_fichier_audio(chemin, titre, id_debut):
    data, samplerate = sf.read(chemin)
    
    if data.ndim > 1:  # Stereo -> mono
        data = np.mean(data, axis=1)
    
    if samplerate != TAUX_ECHANTILLONNAGE:
        nb_echantillons = int(len(data) * TAUX_ECHANTILLONNAGE / samplerate)
        data = resample(data, nb_echantillons)
    
    n = TAUX_ECHANTILLONNAGE * DUREE_FENETRE
    nb_tranches = len(data) // n

    lignes = []
    dangers = []

    for i in range(nb_tranches):
        tranche = data[i * n:(i + 1) * n]
        resultats = analyse_tranche(tranche)
        dangers.append(resultats["Danger%"])
        lignes.append({
            "id": id_debut + i,
            "titre": titre,
            **resultats
        })

    # Ajout de la moyenne danger par fichier
    moy_danger = np.mean(dangers) if dangers else 0
    for ligne in lignes:
        ligne["moy_danger"] = round(moy_danger, 2)

    return lignes, id_debut + nb_tranches

def analyser_dossier_son():
    toutes_les_lignes = []
    id_courant = 1

    for fichier in os.listdir(DOSSIER_SON):
        if fichier.endswith(".wav"):
            chemin = os.path.join(DOSSIER_SON, fichier)
            lignes, id_courant = traiter_fichier_audio(chemin, fichier, id_courant)
            toutes_les_lignes.extend(lignes)

    df = pd.DataFrame(toutes_les_lignes)
    colonnes = ["id", "titre", "amplitude", "rms", "dB", "Peak", "StdDev", "Score", "Danger%", "moy_danger"]
    df.to_csv(CSV_SORTIE, index=False, columns=colonnes)
    print(f"✅ Analyse terminée. Résultats dans '{CSV_SORTIE}'.")

if __name__ == "__main__":
    analyser_dossier_son()
