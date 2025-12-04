audio_analyse_project/
│
├── backend/
│   ├── main.py               # Serveur FastAPI (API)
│   ├── analyse.py            # Analyse du son (amplitude, etc.)
│   ├── record.py             # Enregistrement du son
│   ├── requirements.txt      # Dépendances Python
│   └── db.py                 # Connexion à MongoDB
│
├── data/
│   └── enregistrement.wav    # Fichier audio généré (par record.py)
│
├── frontend/ (optionnel)
│   └── streamlit_app.py      # Interface simple pour lancer l'enregistrement / voir le graphe
│
└── README.md                 # Explication du projet


pip install -r requirements.txt

# Aller dans le dossier backend
cd backend

# Installer les dépendances
pip install -r requirements.txt

# 1. Enregistrer l'audio
python record.py

# 2. Analyser l'audio
python analyse.py

# 3. Lancer le serveur API
uvicorn main:app --reload

# 4. (Optionnel) Lancer l'interface graphique
streamlit run ../frontend/streamlit_app.py
