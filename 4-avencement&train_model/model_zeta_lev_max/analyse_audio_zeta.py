# Copyright 2025 Montassar Nawara
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import numpy as np
import pandas as pd
import soundfile as sf
import librosa
from scipy.signal import spectrogram, find_peaks
from scipy.ndimage import gaussian_filter1d
from sklearn.preprocessing import MinMaxScaler

# =======================
# Configuration globale
# =======================
DOSSIER_SON = "son"
DUREE_FENETRE = 5  # secondes
CSV_SORTIE = "resultats_audio_final.csv"
CSV_RESUME = "resumes_par_fichier.csv"
TAUX_ECHANTILLONNAGE = 44100  # Hz
N_MFCC = 13  # Nombre de coefficients MFCC

# Seuils pour la détection
SEUIL_CRI_FREQ_MIN = 1500
SEUIL_CRI_FREQ_MAX = 6000
SEUIL_CRI_PUISSANCE = 0.3
MIN_DUREE_CRI = 0.3

class AudioAnalyzer:
    def __init__(self):
        self.danger_history = []
        self.scaler = MinMaxScaler()
        self.cri_types = {
            'bebe': {'centroid_min': 2500, 'bandwidth_min': 1000, 'mfcc_range': (-300, -100)},
            'enfant': {'centroid_min': 2000, 'bandwidth_min': 800, 'mfcc_range': (-200, -50)},
            'adulte': {'centroid_min': 1500, 'bandwidth_min': 600, 'mfcc_range': (-100, 0)}
        }
        
    def normaliser_donnees(self, data):
        """Normalise les données audio entre -1 et 1"""
        return data / np.max(np.abs(data) + 1e-6)
    
    def extraire_features(self, tranche, sr):
        """Extrait les caractéristiques audio avancées"""
        # Normalisation
        tranche = self.normaliser_donnees(tranche)
        
        # Features spectrales
        S = np.abs(librosa.stft(tranche))
        centroid = librosa.feature.spectral_centroid(S=S, sr=sr)[0]
        bandwidth = librosa.feature.spectral_bandwidth(S=S, sr=sr)[0]
        flatness = librosa.feature.spectral_flatness(y=tranche)
        
        # MFCCs
        mfccs = librosa.feature.mfcc(y=tranche, sr=sr, n_mfcc=N_MFCC)
        
        # PCEN (Per-Channel Energy Normalization)
        pcen = librosa.pcen(librosa.feature.melspectrogram(y=tranche, sr=sr), sr=sr)
        
        # ZCR (Zero Crossing Rate)
        zcr = librosa.feature.zero_crossing_rate(tranche)
        
        return {
            'centroid_mean': np.mean(centroid),
            'centroid_std': np.std(centroid),
            'bandwidth_mean': np.mean(bandwidth),
            'flatness_mean': np.mean(flatness),
            'mfcc_mean': np.mean(mfccs),
            'mfcc_std': np.std(mfccs),
            'pcen_mean': np.mean(pcen),
            'pcen_std': np.std(pcen),
            'zcr_mean': np.mean(zcr)
        }
    
    def detecter_type_cri(self, features):
        """Détermine le type de cri basé sur les caractéristiques"""
        for cri_type, params in self.cri_types.items():
            if (features['centroid_mean'] > params['centroid_min'] and
                features['bandwidth_mean'] > params['bandwidth_min'] and
                params['mfcc_range'][0] < features['mfcc_mean'] < params['mfcc_range'][1]):
                return cri_type
        return None
    
    def detecter_cri_avance(self, tranche, sr):
        """Détection avancée de cris avec classification de type"""
        # Analyse spectrale de base
        nperseg = 1024
        f, t, Sxx = spectrogram(tranche, fs=sr, nperseg=nperseg)
        
        # Détection dans les hautes fréquences
        mask_freq = (f >= SEUIL_CRI_FREQ_MIN) & (f <= SEUIL_CRI_FREQ_MAX)
        puissance_cri = np.mean(Sxx[mask_freq, :], axis=0)
        puissance_tot = np.mean(Sxx, axis=0)
        puissance_tot[puissance_tot == 0] = 1e-6
        ratio_cri = puissance_cri / puissance_tot
        ratio_cri = gaussian_filter1d(ratio_cri, sigma=2)
        
        # Extraction des caractéristiques
        features = self.extraire_features(tranche, sr)
        cri_type = self.detecter_type_cri(features)
        
        # Détection temporelle des cris
        seuil_adaptatif = max(SEUIL_CRI_PUISSANCE, float(np.percentile(ratio_cri, 90)))
        peaks, _ = find_peaks(ratio_cri, height=seuil_adaptatif, distance=5)
        
        for peak in peaks:
            start = max(0, t[peak] - 0.2)
            end = min(t[-1], t[peak] + 0.2)
            
            while start > 0 and ratio_cri[int(start * sr / nperseg)] > seuil_adaptatif/2:
                start -= 0.1
            while end < t[-1] and ratio_cri[int(end * sr / nperseg)] > seuil_adaptatif/2:
                end += 0.1
                
            if (end - start) >= MIN_DUREE_CRI:
                return True, cri_type
        
        return False, None
    
    def estimer_nbr_sources(self, tranche):
        """Estimation du nombre de sources sonores"""
        try:
            # Séparation de sources par NMF
            S = np.abs(librosa.stft(tranche))
            W, H = librosa.decompose.decompose(S, n_components=3, sort=True)
            components = W @ H
            n_components = np.sum(np.max(components, axis=1) > 0.1)
            return min(3, max(1, n_components))
        except Exception as e:
            print(f"Erreur séparation sources: {str(e)}")
            return 1 if np.std(tranche) < 0.05 else 2
    
    def calculer_danger_avance(self, features, cri_detecte, cri_type, n_sources):
        """Calcul du danger basé sur un modèle multi-facteurs"""
        # Facteurs de pondération
        weights = {
            'rms': 0.3,
            'peak': 0.2,
            'centroid': 0.15,
            'bandwidth': 0.1,
            'mfcc': 0.1,
            'pcen': 0.1,
            'zcr': 0.05
        }
        
        # Normalisation des features
        rms_norm = np.clip(features['rms'] * 100, 0, 100)
        peak_norm = np.clip(features['peak'] * 100, 0, 100)
        centroid_norm = np.clip(features['centroid_mean'] / 5000 * 100, 0, 100)
        bandwidth_norm = np.clip(features['bandwidth_mean'] / 3000 * 100, 0, 100)
        mfcc_norm = np.clip((features['mfcc_mean'] + 300) / 3, 0, 100)
        pcen_norm = np.clip(features['pcen_mean'] * 20, 0, 100)
        zcr_norm = np.clip(features['zcr_mean'] * 500, 0, 100)
        
        # Calcul de base
        danger = (weights['rms'] * rms_norm +
                 weights['peak'] * peak_norm +
                 weights['centroid'] * centroid_norm +
                 weights['bandwidth'] * bandwidth_norm +
                 weights['mfcc'] * mfcc_norm +
                 weights['pcen'] * pcen_norm +
                 weights['zcr'] * zcr_norm)
        
        # Majoration pour les cris
        if cri_detecte:
            if cri_type == 'bebe':
                danger *= 1.5
            elif cri_type == 'enfant':
                danger *= 1.3
            else:  # adulte ou inconnu
                danger *= 1.2
            danger = min(100, danger)
        
        # Pondération par le nombre de sources
        danger *= (1 + 0.1 * (n_sources - 1))
        
        # Mémoire contextuelle
        if self.danger_history:
            avg_prev = np.mean(self.danger_history[-3:])
            danger = 0.7 * danger + 0.3 * avg_prev
        
        self.danger_history.append(danger)
        return np.clip(danger, 10, 100)
    
    def analyser_tranche(self, tranche, sr):
        """Analyse complète d'une tranche audio"""
        # Caractéristiques de base
        rms = np.sqrt(np.mean(tranche ** 2))
        peak = np.max(np.abs(tranche))
        dB = 20 * np.log10(rms + 1e-6)
        
        # Détection avancée
        cri_detecte, cri_type = self.detecter_cri_avance(tranche, sr)
        n_sources = self.estimer_nbr_sources(tranche)
        
        # Extraction des caractéristiques avancées
        features = self.extraire_features(tranche, sr)
        features.update({'rms': rms, 'peak': peak, 'dB': dB})
        
        # Calcul du danger
        danger = self.calculer_danger_avance(features, cri_detecte, cri_type, n_sources)
        
        # Score de qualité audio
        score = min(100, (rms / 1.0) * 100)
        
        return {
            "amplitude": rms,
            "rms": rms,
            "dB": dB,
            "Peak": peak,
            "Score": score,
            "Danger%": danger,
            "env": n_sources,
            "cri": cri_detecte,
            "cri_type": cri_type if cri_detecte else "aucun",
            **features
        }

def traiter_fichier_audio(chemin, titre, id_debut, analyzer):
    """Traite un fichier audio complet"""
    try:
        try:
            data, sr_orig = sf.read(chemin)
            if data is None or sr_orig is None:
                raise ValueError(f"Impossible de lire le fichier audio: {chemin}")
        except Exception as e:
            print(f"Erreur lecture fichier audio {chemin}: {str(e)}")
            return [], id_debut, None
        if data.ndim > 1:
            data = np.mean(data, axis=1)
        
        # Rééchantillonnage si nécessaire
        if sr_orig != TAUX_ECHANTILLONNAGE:
            data = librosa.resample(data, orig_sr=sr_orig, target_sr=TAUX_ECHANTILLONNAGE)
        
        n_samples = TAUX_ECHANTILLONNAGE * DUREE_FENETRE
        nb_tranches = len(data) // n_samples

        lignes = []
        dangers = []
        
        for i in range(nb_tranches):
            tranche = data[i * n_samples:(i + 1) * n_samples]
            if len(tranche) < n_samples:
                continue  # Ignorer les tranches incomplètes
                
            resultats = analyzer.analyser_tranche(tranche, TAUX_ECHANTILLONNAGE)
            dangers.append(resultats["Danger%"])
            
            lignes.append({
                "id": id_debut + i,
                "titre": titre,
                **resultats
            })

        # Calcul de la moyenne pondérée
        if dangers:
            max_danger = max(dangers)
            avg_danger = np.mean(dangers)
            moy_danger = 0.7 * max_danger + 0.3 * avg_danger
        else:
            moy_danger = 0
            
        for ligne in lignes:
            ligne["moy_danger"] = round(moy_danger, 2)

        # Création du résumé pour ce fichier
        df_file = pd.DataFrame(lignes)
        
        if not df_file.empty:
            resume = {
                "titre": titre,
                "nb_tranches": len(df_file),
                "nb_cris": df_file["cri"].sum(),
                "cri_type_dom": df_file["cri_type"].mode()[0] if any(df_file["cri"]) else "aucun",
                "danger_max": df_file["Danger%"].max(),
                "danger_moy": df_file["Danger%"].mean(),
                "danger_std": df_file["Danger%"].std(),
                "env_moy": df_file["env"].mean(),
                "rms_moy": df_file["rms"].mean(),
                "peak_moy": df_file["Peak"].mean(),
                "centroid_moy": df_file["centroid_mean"].mean(),
                "bandwidth_moy": df_file["bandwidth_mean"].mean(),
                "mfcc_moy": df_file["mfcc_mean"].mean(),
                "pcen_moy": df_file["pcen_mean"].mean(),
            }
        else:
            resume = {
                "titre": titre,
                "nb_tranches": 0,
                "nb_cris": 0,
                "cri_type_dom": "aucun",
                "danger_max": 0,
                "danger_moy": 0,
                "danger_std": 0,
                "env_moy": 0,
                "rms_moy": 0,
                "peak_moy": 0,
                "centroid_moy": 0,
                "bandwidth_moy": 0,
                "mfcc_moy": 0,
                "pcen_moy": 0,
            }

        return lignes, id_debut + nb_tranches, resume
    
    except Exception as e:
        print(f"Erreur traitement {titre}: {str(e)}")
        return [], id_debut, None

def analyser_dossier_son():
    """Analyse tous les fichiers audio du dossier"""
    analyzer = AudioAnalyzer()
    toutes_les_lignes = []
    resumes = []
    id_courant = 1

    # Parcours des fichiers triés
    fichiers = sorted([f for f in os.listdir(DOSSIER_SON) if f.endswith('.wav')])
    
    for fichier in fichiers:
        chemin = os.path.join(DOSSIER_SON, fichier)
        lignes, id_courant, resume = traiter_fichier_audio(chemin, fichier, id_courant, analyzer)
        toutes_les_lignes.extend(lignes)
        if resume is not None:
            resumes.append(resume)

    # Création du DataFrame des résultats détaillés
    if toutes_les_lignes:
        df = pd.DataFrame(toutes_les_lignes)
        
        # Sélection et ordre des colonnes
        colonnes_principales = [
            "id", "titre", "amplitude", "rms", "dB", "Peak", "Score", 
            "Danger%", "env", "cri", "cri_type", "moy_danger"
        ]
        
        # Ajout des caractéristiques avancées
        colonnes_features = [
            "centroid_mean", "bandwidth_mean", "flatness_mean",
            "mfcc_mean", "pcen_mean", "zcr_mean"
        ]
        
        colonnes = colonnes_principales + colonnes_features
        
        # Enregistrement des résultats
        df.to_csv(CSV_SORTIE, index=False, columns=colonnes)
        print(f"\n✅ Analyse terminée. {len(df)} tranches analysées.")
        print(f"📊 Statistiques Danger%: Moy={df['Danger%'].mean():.1f} Max={df['Danger%'].max():.1f} Min={df['Danger%'].min():.1f}")
        print(f"💾 Résultats détaillés enregistrés dans '{CSV_SORTIE}'")
    else:
        print("Aucune donnée détaillée à enregistrer!")

    # Création du DataFrame des résumés
    if resumes:
        df_resume = pd.DataFrame(resumes)
        df_resume.to_csv(CSV_RESUME, index=False)
        print(f"\n📊 Résumés par fichier:")
        print(df_resume)
        print(f"💾 Résumés globaux enregistrés dans '{CSV_RESUME}'")
    else:
        print("Aucun résumé à enregistrer!")

if __name__ == "__main__":
    analyser_dossier_son()