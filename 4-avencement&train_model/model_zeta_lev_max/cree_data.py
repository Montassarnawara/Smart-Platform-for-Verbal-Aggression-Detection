import numpy as np
import pandas as pd
import librosa
import os
import soundfile as sf
from scipy.signal import spectrogram, find_peaks
from scipy.ndimage import gaussian_filter1d
import warnings

class AudioFeatureExtractor:
    def __init__(self, sample_rate=44100, window_size=5):
        self.sample_rate = sample_rate
        self.window_size = window_size
        self.samples_per_window = sample_rate * window_size
        
    def process_audio_file(self, audio_path):
        """Traite un fichier audio avec gestion robuste des erreurs"""
        try:
            # Charger le fichier audio
            try:
                audio_data, sr = sf.read(audio_path)
                if audio_data.ndim > 1:
                    audio_data = np.mean(audio_data, axis=1)
                if sr != self.sample_rate:
                    audio_data = librosa.resample(audio_data, orig_sr=sr, target_sr=self.sample_rate)
            except Exception as e:
                print(f"SoundFile failed, fallback to librosa: {str(e)}")
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    audio_data = librosa.load(audio_path, sr=self.sample_rate, mono=True)[0]
            
            # Vérifier la longueur
            if len(audio_data) < self.samples_per_window:
                print(f"Fichier trop court ({len(audio_data)/self.sample_rate:.1f}s), ignoré")
                return pd.DataFrame(), pd.DataFrame()
            
            # Découpage et extraction
            slices = []
            for i in range(0, len(audio_data), self.samples_per_window):
                slice_data = audio_data[i:i+self.samples_per_window]
                if len(slice_data) == self.samples_per_window:
                    features = self.extract_slice_features(slice_data)
                    if features:  # Vérifier que l'extraction a réussi
                        features['tranche_id'] = len(slices) + 1
                        slices.append(features)
            
            if not slices:
                return pd.DataFrame(), pd.DataFrame()
                
            # Création des DataFrames
            detail_df = pd.DataFrame(slices)
            
            # Ajout des colonnes id et titre simulées pour la compatibilité
            detail_df['id'] = range(1, len(detail_df)+1)
            detail_df['titre'] = os.path.basename(audio_path)
            
            # Réorganisation des colonnes
            cols_order = ['id', 'titre'] + [col for col in detail_df.columns if col not in ['id', 'titre']]
            detail_df = detail_df[cols_order]
            
            summary_df = self.create_summary(detail_df, os.path.basename(audio_path))
            
            return detail_df, summary_df
            
        except Exception as e:
            print(f"Erreur avec {os.path.basename(audio_path)}: {str(e)}")
            return pd.DataFrame(), pd.DataFrame()
    
    def extract_slice_features(self, slice_data):
        """Extrait les features d'une tranche audio"""
        try:
            # Normalisation
            max_val = np.max(np.abs(slice_data)) + 1e-6
            slice_data = slice_data / max_val
            
            # Caractéristiques de base
            rms = np.sqrt(np.mean(slice_data**2))
            features = {
                'amplitude': np.mean(np.abs(slice_data)),
                'rms': rms,
                'dB': 20 * np.log10(rms + 1e-6),
                'Peak': np.max(np.abs(slice_data)),
                'Score': min(100, rms * 100),
                'env': self.estimate_sources(slice_data)
            }
            
            # Analyse spectrale
            S = np.abs(librosa.stft(slice_data))
            features.update({
                'centroid_mean': float(np.mean(librosa.feature.spectral_centroid(S=S, sr=self.sample_rate))),
                'bandwidth_mean': float(np.mean(librosa.feature.spectral_bandwidth(S=S, sr=self.sample_rate))),
                'flatness_mean': float(np.mean(librosa.feature.spectral_flatness(y=slice_data))),
                'mfcc_mean': float(np.mean(librosa.feature.mfcc(y=slice_data, sr=self.sample_rate, n_mfcc=13))),
                'pcen_mean': float(np.mean(librosa.pcen(librosa.feature.melspectrogram(y=slice_data, sr=self.sample_rate), sr=self.sample_rate))),
                'zcr_mean': float(np.mean(librosa.feature.zero_crossing_rate(slice_data)))
            })
            
            # Détection de cris
            cri_detecte, cri_type = self.detect_cry(slice_data)
            features.update({
                'cri': bool(cri_detecte),
                'cri_type': cri_type if cri_detecte else "aucun"
            })
            
            return features
        except Exception as e:
            print(f"Erreur extraction features: {str(e)}")
            return None
    
    def detect_cry(self, audio_data):
        """Détection de cris avec gestion d'erreurs"""
        try:
            f, t, Sxx = spectrogram(audio_data, fs=self.sample_rate, nperseg=1024)
            mask = (f >= 1500) & (f <= 6000)
            ratio = np.mean(Sxx[mask, :], axis=0) / (np.mean(Sxx, axis=0) + 1e-6)
            ratio = gaussian_filter1d(ratio, sigma=2)
            
            if np.max(ratio) > 0.3:
                centroid = np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=self.sample_rate))
                if centroid > 2500:
                    return True, "bebe"
                elif centroid > 2000:
                    return True, "enfant"
                else:
                    return True, "adulte"
            return False, None
        except:
            return False, None
    
    def estimate_sources(self, audio_data):
        """Estimation du nombre de sources"""
        try:
            return 1 if np.std(audio_data) < 0.05 else 2
        except:
            return 1
    
    def create_summary(self, detail_df, filename):
        """Crée le résumé statistique"""
        if detail_df.empty:
            return pd.DataFrame()
        
        try:
            summary = {
                'titre': filename,
                'nb_tranches': len(detail_df),
                'nb_cris': int(detail_df['cri'].sum()),
                'cri_type_dom': detail_df['cri_type'].mode()[0] if detail_df['cri'].sum() > 0 else 'aucun',
                'env_moy': float(detail_df['env'].mean()),
                'rms_moy': float(detail_df['rms'].mean()),
                'peak_moy': float(detail_df['Peak'].mean()),
                'centroid_moy': float(detail_df['centroid_mean'].mean()),
                'bandwidth_moy': float(detail_df['bandwidth_mean'].mean()),
                'mfcc_moy': float(detail_df['mfcc_mean'].mean()),
                'pcen_moy': float(detail_df['pcen_mean'].mean())
            }
            return pd.DataFrame([summary])
        except Exception as e:
            print(f"Erreur création résumé: {str(e)}")
            return pd.DataFrame()

if __name__ == "__main__":
    # Configuration
    input_dir = "son_test"
    output_detail = "data_son_test_detail.csv"
    output_summary = "data_test_summary.csv"
    
    # Vérification du dossier
    if not os.path.exists(input_dir):
        print(f"ERREUR: Dossier '{input_dir}' introuvable!")
        exit()
    
    # Initialisation
    extractor = AudioFeatureExtractor()
    all_details = []
    all_summaries = []
    
    # Traitement des fichiers
    print("\nDébut du traitement des fichiers audio...")
    for file in sorted(os.listdir(input_dir)):
        if file.lower().endswith('.wav'):
            print(f"\nTraitement de {file}...")
            audio_path = os.path.join(input_dir, file)
            detail_df, summary_df = extractor.process_audio_file(audio_path)
            
            if not detail_df.empty:
                all_details.append(detail_df)
                all_summaries.append(summary_df)
                print(f"Succès: {len(detail_df)} tranches analysées")
    
    # Sauvegarde des résultats
    if all_details:
        final_detail = pd.concat(all_details, ignore_index=True)
        final_detail.to_csv(output_detail, index=False)
        print(f"\n✅ {output_detail} sauvegardé ({len(final_detail)} tranches)")
        
        final_summary = pd.concat(all_summaries, ignore_index=True)
        final_summary.to_csv(output_summary, index=False)
        print(f"✅ {output_summary} sauvegardé ({len(final_summary)} fichiers)")
        
        print("\nStructure des fichiers créés:")
        print("Détails:", final_detail.columns.tolist())
        print("Résumé:", final_summary.columns.tolist())
    else:
        print("\n❌ Aucune donnée à sauvegarder!")