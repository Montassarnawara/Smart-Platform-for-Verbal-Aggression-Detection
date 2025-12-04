# 🎵 Système d'Analyse Audio avec IA

## 📋 Description

Système complet d'analyse audio en temps réel avec intelligence artificielle pour la détection de dangers et l'analyse avancée des signaux sonores.

## 🏗️ Architecture

```
📦 Système Audio IA
├── 🎤 audio_api_system.py     # API principale (port 8000)
├── 🧠 danger_alert.py         # API IA ML models (port 8001)
├── 🔍 analyze.py              # Extracteur de caractéristiques audio
├── 🎯 logic_controller_advanced.py  # Contrôleur logique avancé
└── 🚀 start_system.py         # Script de lancement
```

## 🚀 Démarrage Rapide

### Option 1: Démarrage automatique (Recommandé)
```bash
python start_system.py
```

### Option 2: Démarrage manuel
```bash
# Terminal 1 - API IA
uvicorn danger_alert:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 - API Audio
uvicorn audio_api_system:app --host 0.0.0.0 --port 8000 --reload
```

## 🌐 Endpoints Disponibles

### 🎤 API Audio Principale (http://localhost:8000)

#### Endpoints de Base
- `GET /` - Page d'accueil avec statut
- `GET /status` - Statut complet du système
- `GET /test_full_system` - Test de l'ensemble du système

#### Enregistrement Audio
- `POST /check_and_record` - Enregistrement simple
- `POST /check_and_record_advanced` - Enregistrement avec analyse IA complète
- `POST /run_cycle` - Cycle d'analyse de 12x5 secondes
- `POST /run_cycle_advanced` - Cycle avancé avec IA

#### Analyse Audio
- `POST /analyse_advanced` - Analyse complète d'un fichier audio
- `GET /analyse/{n}` - Extraire n amplitudes du dernier fichier

### 🧠 API IA (http://localhost:8001)

- `GET /` - Statut des modèles ML
- `GET /models-status` - Détails des modèles chargés
- `POST /analyze-audio-advanced` - Analyse IA avancée
- `GET /docs` - Documentation Swagger

## 📊 Format des Données

### Réponse d'Analyse Complète
```json
{
  "status": "success",
  "summary": {
    "danger_percent": 45,
    "risk_level": "medium",
    "slice_predictions": {
      "slice_0": {"prediction": 0.3, "confidence": 0.85},
      "slice_1": {"prediction": 0.6, "confidence": 0.92}
    },
    "file_predictions": {
      "overall_risk": 0.45,
      "dominant_features": ["mfcc_variance", "spectral_rolloff"]
    },
    "audio_features": {
      "duration": 5.0,
      "cry_detected": true,
      "dominant_frequency": 1200.5
    }
  }
}
```

## 🔧 Configuration

### Fichiers Requis
- `slice_models.pkl` - Modèles ML pour l'analyse par tranches
- `file_models.pkl` - Modèles ML pour l'analyse globale

### Dossiers
- `audio_chunks/` - Stockage des enregistrements audio
- `__pycache__/` - Cache Python (généré automatiquement)

## 🧪 Tests

### Test Complet du Système
```bash
curl http://localhost:8000/test_full_system
```

### Test d'Enregistrement Avancé
```bash
curl -X POST http://localhost:8000/check_and_record_advanced
```

### Vérification du Statut
```bash
curl http://localhost:8000/status
```

## 📈 Flux d'Analyse

1. **Enregistrement** → `audio_api_system.py`
2. **Extraction de caractéristiques** → `analyze.py` (AudioFeatureExtractor)
3. **Prédiction IA** → `danger_alert.py` (Modèles ML)
4. **Évaluation des risques** → `logic_controller_advanced.py`
5. **Résultat final** → API Response

## 🛠️ Développement

### Structure des Classes Principales

```python
# analyze.py
class AudioFeatureExtractor:
    def process_audio_file(file_path) -> dict
    def extract_slice_features(audio, sr) -> list
    def detect_cry(audio, sr) -> bool

# danger_alert.py  
class ModelContainer:
    def predict_slice(features) -> dict
    def predict_file(features) -> dict

# logic_controller_advanced.py
def start_analysis_cycle_advanced() -> dict
def evaluate_risk_level(percent) -> str
```

## 🐛 Dépannage

### API IA Non Accessible
```bash
# Vérifier que l'API IA fonctionne
curl http://localhost:8001/models-status
```

### Modèles ML Non Chargés
- Vérifier la présence de `slice_models.pkl` et `file_models.pkl`
- Redémarrer l'API IA

### Erreur d'Enregistrement Audio
- Vérifier les permissions du microphone
- Contrôler l'existence du dossier `audio_chunks/`

## 📋 Dépendances

```txt
fastapi
uvicorn
librosa
scikit-learn
joblib
pandas
numpy
soundfile
scipy
pyaudio
requests
```

## 🎯 Utilisation Recommandée

1. **Lancer le système** : `python start_system.py`
2. **Tester** : Aller sur http://localhost:8000/test_full_system
3. **Analyser** : Utiliser `/check_and_record_advanced` pour des analyses complètes
4. **Surveiller** : Consulter `/status` pour le monitoring

---

🚀 **Système prêt pour la production !**
