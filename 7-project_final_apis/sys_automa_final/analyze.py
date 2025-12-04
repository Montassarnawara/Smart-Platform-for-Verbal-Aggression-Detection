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





import numpy as np
import scipy.io.wavfile as wav
import os
import librosa
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
                return {"detail": [], "summary": {}}
            
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
                return {"detail": [], "summary": {}}
                
            # Ajout des informations de base
            for i, slice_info in enumerate(slices):
                slice_info['id'] = i + 1
                slice_info['titre'] = os.path.basename(audio_path)
            
            summary = self.create_summary(slices, os.path.basename(audio_path))
            
            return {"detail": slices, "summary": summary}
            
        except Exception as e:
            print(f"Erreur avec {os.path.basename(audio_path)}: {str(e)}")
            return {"detail": [], "summary": {}}
    
    def extract_slice_features(self, slice_data):
        """Extrait les features d'une tranche audio"""
        try:
            # Normalisation
            max_val = np.max(np.abs(slice_data)) + 1e-6
            slice_data = slice_data / max_val
            
            # Caractéristiques de base
            rms = np.sqrt(np.mean(slice_data**2))
            features = {
                'amplitude': float(np.mean(np.abs(slice_data))),
                'rms': float(rms),
                'dB': float(20 * np.log10(rms + 1e-6)),
                'Peak': float(np.max(np.abs(slice_data))),
                'Score': float(min(100, rms * 100)),
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
    
    def create_summary(self, slices, filename):
        """Crée le résumé statistique"""
        if not slices:
            return {}
        
        try:
            cris = [s for s in slices if s.get('cri', False)]
            cri_types = [s['cri_type'] for s in cris if s.get('cri_type') != 'aucun']
            
            summary = {
                'titre': filename,
                'nb_tranches': len(slices),
                'nb_cris': len(cris),
                'cri_type_dom': max(set(cri_types), key=cri_types.count) if cri_types else 'aucun',
                'env_moy': float(np.mean([s['env'] for s in slices])),
                'rms_moy': float(np.mean([s['rms'] for s in slices])),
                'peak_moy': float(np.mean([s['Peak'] for s in slices])),
                'centroid_moy': float(np.mean([s['centroid_mean'] for s in slices])),
                'bandwidth_moy': float(np.mean([s['bandwidth_mean'] for s in slices])),
                'mfcc_moy': float(np.mean([s['mfcc_mean'] for s in slices])),
                'pcen_moy': float(np.mean([s['pcen_mean'] for s in slices]))
            }
            return summary
        except Exception as e:
            print(f"Erreur création résumé: {str(e)}")
            return {}

def analyze_audio_chunk(filepath):
    """Fonction compatible avec l'ancienne interface"""
    extractor = AudioFeatureExtractor()
    result = extractor.process_audio_file(filepath)
    
    if result["detail"]:
        first_slice = result["detail"][0]
        return {
            "file": filepath,
            "frequence": extractor.sample_rate,
            "duration": round(len(result["detail"]) * extractor.window_size, 2),
            "max_amplitude": round(first_slice["Peak"], 4),
            "mean_amplitude": round(first_slice["amplitude"], 4),
            "nb_echantillons": extractor.samples_per_window * len(result["detail"]),
            "advanced_analysis": result
        }
    else:
        return {"file": filepath, "error": "Échec de l'analyse"}

def extract_amplitudes(filepath: str, target_rate: int = 100, limit: int = 50):
    """Fonction compatible avec l'ancienne interface"""
    if not os.path.exists(filepath):
        return {"error": "Fichier audio non trouvé."}

    try:
        # Utiliser librosa pour plus de robustesse
        audio_data = librosa.load(filepath, sr=None, mono=True)[0]
        
        # Échantillonnage
        step = max(1, int(len(audio_data) / target_rate))
        sampled_data = audio_data[::step]
        
        # Normalisation
        max_amplitude = np.max(np.abs(sampled_data))
        if max_amplitude > 0:
            normalized_data = sampled_data / max_amplitude
        else:
            normalized_data = sampled_data
        
        return normalized_data[:limit].tolist()
    except Exception as e:
        return {"error": f"Erreur lors de l'extraction: {str(e)}"}

def analyze_directory(directory):
    """Analyse tous les fichiers WAV d'un répertoire"""
    results = []
    extractor = AudioFeatureExtractor()
    
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".wav"):
            path = os.path.join(directory, filename)
            analysis = extractor.process_audio_file(path)
            results.append({
                "filename": filename,
                "path": path,
                "analysis": analysis
            })
    
    return {"analyses": results}
print("Audio analysis module loaded successfully.")