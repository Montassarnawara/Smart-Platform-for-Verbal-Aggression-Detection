project/
│
├── main.py               # Point d’entrée (app FastAPI)
├── record.py             # Gère l'enregistrement audio en tranches
├── analyze.py            # Analyse chaque tranche audio
├── audio_chunks/         # Répertoire pour stocker les fichiers audio 5s
└── requirements.txt      # Dépendances (streamlit, sounddevice, fastapi...)


main.py (FastAPI)
   |
   --> route /detection (GET)
         |
         --> vérifie état global (ex: rec == True)
               |
               --> si vrai :
                      |
                      --> appelle record.py (fonction start_recording)
                              |
                              --> boucle: enregistre 5s -> analyse -> stocke
                              --> max 60s (12 tranches)
                              --> retourne liste d’analyses

