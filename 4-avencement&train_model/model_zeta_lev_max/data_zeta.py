import pandas as pd

def concatener_tables(fichier1, fichier2, sortie='table_concatenee.csv'):
    # Lire les deux fichiers CSV
    try:
        df1 = pd.read_csv(fichier1)
        df2 = pd.read_csv(fichier2)
    except Exception as e:
        print(f"Erreur de lecture des fichiers : {e}")
        return

    # Vérifier que les colonnes sont identiques
    if list(df1.columns) != list(df2.columns):
        print("❌ Les colonnes des deux fichiers ne sont pas identiques.")
        return

    # Concaténer les DataFrames
    df_concat = pd.concat([df1, df2], ignore_index=True)

    # Sauvegarder dans un nouveau fichier CSV
    try:
        df_concat.to_csv(sortie, index=False)
        print(f"✅ Tables concaténées et sauvegardées dans '{sortie}'")
    except Exception as e:
        print(f"Erreur d'écriture du fichier : {e}")

# Exemple d'utilisation
if __name__ == "__main__":
    concatener_tables("resultats_audio_final.csv", "synthetic_audio_details.csv", "data_details.csv")


