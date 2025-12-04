import numpy as np
import pandas as pd
import librosa
from scipy import signal
from faker import Faker
import random
from sklearn.preprocessing import MinMaxScaler

# Initialisation
fake = Faker()
np.random.seed(42)
random.seed(42)

# Configuration
NUM_FILES = 30  # Nombre de fichiers synthétiques à générer
CHUNKS_PER_FILE = (3, 8)  # Nombre de tranches par fichier
OUTPUT_DETAILS = "synthetic_audio_details.csv"
OUTPUT_SUMMARY = "synthetic_audio_summary.csv"
SAMPLE_RATE = 44100
DURATION = 5  # secondes par tranche

# Modèles statistiques basés sur vos données
class AudioFeatureGenerator:
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.cri_types = {
            'bebe': {
                'centroid': (4500, 6000), 
                'bandwidth': (3000, 4000),
                'mfcc': (-50, -30),
                'danger_mult': 1.5
            },
            'enfant': {
                'centroid': (3500, 5000),
                'bandwidth': (2500, 3500),
                'mfcc': (-40, -20),
                'danger_mult': 1.3
            },
            'adulte': {
                'centroid': (2000, 4000),
                'bandwidth': (2000, 3000),
                'mfcc': (-30, 0),
                'danger_mult': 1.2
            }
        }
        
    def generate_audio_features(self, cri_type=None):
        if cri_type is None:
            # Génération de bruit de fond
            rms = np.random.uniform(0.01, 0.1)
            peak = rms * np.random.uniform(3, 8)
            centroid = np.random.uniform(1000, 3000)
            bandwidth = np.random.uniform(1000, 2500)
            mfcc = np.random.uniform(-60, 20)
            flatness = np.random.uniform(0.001, 0.1)
            pcen = np.random.uniform(0.05, 0.3)
            zcr = np.random.uniform(0.02, 0.1)
            env = random.randint(1, 3)
        else:
            # Génération avec type de cri spécifique
            params = self.cri_types[cri_type]
            rms = np.random.uniform(0.05, 0.25)
            peak = np.clip(rms * np.random.uniform(4, 10), 0.3, 1.0)
            centroid = np.random.uniform(*params['centroid'])
            bandwidth = np.random.uniform(*params['bandwidth'])
            mfcc = np.random.uniform(*params['mfcc'])
            flatness = np.random.uniform(0.001, 0.05)
            pcen = np.random.uniform(0.1, 0.4)
            zcr = np.random.uniform(0.03, 0.08)
            env = random.randint(2, 3)
            
        # Calcul des dérivés
        db = 20 * np.log10(rms + 1e-6)
        score = min(100, (rms * 80 + peak * 15 + db * 0.5))
        
        return {
            'amplitude': rms,
            'rms': rms,
            'dB': db,
            'Peak': peak,
            'Score': score,
            'env': env,
            'centroid_mean': centroid,
            'bandwidth_mean': bandwidth,
            'flatness_mean': flatness,
            'mfcc_mean': mfcc,
            'pcen_mean': pcen,
            'zcr_mean': zcr
        }
    
    def calculate_danger(self, features, cri_type=None):
        base_danger = min(100, (
            0.3 * features['rms'] * 100 +
            0.2 * features['Peak'] * 100 +
            0.15 * (features['centroid_mean'] / 100) +
            0.1 * (features['bandwidth_mean'] / 50) +
            0.1 * np.clip(features['mfcc_mean'] + 50, 0, 100) +
            0.1 * features['pcen_mean'] * 100 +
            0.05 * features['zcr_mean'] * 500
        ))
        
        if cri_type is not None:
            base_danger *= self.cri_types[cri_type]['danger_mult']
            base_danger = min(100, base_danger)
            
        # Ajout de variation aléatoire
        base_danger *= np.random.uniform(0.9, 1.1)
        
        return np.clip(base_danger, 10, 100)

# Génération des données synthétiques
def generate_synthetic_data():
    generator = AudioFeatureGenerator()
    details_data = []
    summary_data = []
    current_id = 1
    
    for file_num in range(NUM_FILES):
        # Déterminer le type de fichier (avec ou sans cris)
        file_type = random.choices(['cri', 'bruit'], weights=[0.7, 0.3])[0]
        
        if file_type == 'cri':
            dominant_cri_type = random.choices(
                ['bebe', 'enfant', 'adulte'], 
                weights=[0.2, 0.3, 0.5]
            )[0]
        else:
            dominant_cri_type = None
        
        # Générer les tranches
        num_chunks = random.randint(*CHUNKS_PER_FILE)
        file_dangers = []
        file_title = f"synth_{fake.word()}_{file_num}.wav"
        
        for chunk in range(num_chunks):
            # Déterminer si cette tranche contient un cri
            if file_type == 'cri':
                if random.random() < 0.8:  # 80% de chance d'avoir le cri dominant
                    current_cri_type = dominant_cri_type
                else:
                    current_cri_type = random.choices(
                        ['bebe', 'enfant', 'adulte', None], 
                        weights=[0.1, 0.2, 0.6, 0.1]
                    )[0]
            else:
                current_cri_type = None
                
            # Générer les caractéristiques
            features = generator.generate_audio_features(current_cri_type)
            
            # Calculer le danger
            danger = generator.calculate_danger(features, current_cri_type)
            file_dangers.append(danger)
            
            # Ajouter aux données détaillées
            details_data.append({
                'id': current_id,
                'titre': file_title,
                **features,
                'Danger%': danger,
                'cri': current_cri_type is not None,
                'cri_type': current_cri_type if current_cri_type else "aucun",
                'moy_danger': 0  # Temporaire, sera mis à jour plus tard
            })
            
            current_id += 1
        
        # Calculer les statistiques globales du fichier
        if file_dangers:
            danger_max = max(file_dangers)
            danger_moy = np.mean(file_dangers)
            danger_std = np.std(file_dangers)
            moy_danger = 0.7 * danger_max + 0.3 * danger_moy
            
            # Mettre à jour le moy_danger dans les tranches
            for i in range(len(details_data)-num_chunks, len(details_data)):
                details_data[i]['moy_danger'] = round(moy_danger, 2)
            
            # Extraire les features moyennes
            file_df = pd.DataFrame(details_data[-num_chunks:])
            summary_data.append({
                'titre': file_title,
                'nb_tranches': num_chunks,
                'nb_cris': file_df['cri'].sum(),
                'cri_type_dom': file_df['cri_type'].mode()[0] if file_df['cri'].any() else "aucun",
                'danger_max': danger_max,
                'danger_moy': danger_moy,
                'danger_std': danger_std,
                'env_moy': file_df['env'].mean(),
                'rms_moy': file_df['rms'].mean(),
                'peak_moy': file_df['Peak'].mean(),
                'centroid_moy': file_df['centroid_mean'].mean(),
                'bandwidth_moy': file_df['bandwidth_mean'].mean(),
                'mfcc_moy': file_df['mfcc_mean'].mean(),
                'pcen_moy': file_df['pcen_mean'].mean()
            })
    
    # Création des DataFrames
    df_details = pd.DataFrame(details_data)
    df_summary = pd.DataFrame(summary_data)
    
    # Réorganisation des colonnes
    details_cols = [
        'id', 'titre', 'amplitude', 'rms', 'dB', 'Peak', 'Score', 'Danger%',
        'env', 'cri', 'cri_type', 'moy_danger', 'centroid_mean', 'bandwidth_mean',
        'flatness_mean', 'mfcc_mean', 'pcen_mean', 'zcr_mean'
    ]
    
    summary_cols = [
        'titre', 'nb_tranches', 'nb_cris', 'cri_type_dom', 'danger_max',
        'danger_moy', 'danger_std', 'env_moy', 'rms_moy', 'peak_moy',
        'centroid_moy', 'bandwidth_moy', 'mfcc_moy', 'pcen_moy'
    ]
    
    return df_details[details_cols], df_summary[summary_cols]

# Génération et sauvegarde des données
df_details, df_summary = generate_synthetic_data()

# Sauvegarde des fichiers
df_details.to_csv(OUTPUT_DETAILS, index=False)
df_summary.to_csv(OUTPUT_SUMMARY, index=False)

# Affichage des statistiques
print(f"✅ Données synthétiques générées ({len(df_details)} tranches, {len(df_summary)} fichiers)")
print(f"📊 Fichier détaillé : {OUTPUT_DETAILS}")
print(f"📈 Fichier récapitulatif : {OUTPUT_SUMMARY}")

print("\n📌 Statistiques Danger% :")
print(f"- Moyenne : {df_details['Danger%'].mean():.1f}")
print(f"- Max : {df_details['Danger%'].max():.1f}")
print(f"- Min : {df_details['Danger%'].min():.1f}")

print("\n🔊 Répartition des types de cris :")
print(df_details['cri_type'].value_counts())