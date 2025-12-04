import requests
import time

def start_analysis_cycle(base_url="http://localhost:8000"):
    danger_scores = []

    print("==> Démarrage de l'analyse de 1 minute")

    for i in range(2):  # 12 tranches de 5s = 60s
        print(f"\n--- Segment {i+1}/12 ---")

        # 1. Enregistrement de 5s
        r1 = requests.get(f"{base_url}/check_and_record")
        print("Enregistrement:", r1.json())

        # 2. Analyse du dernier fichier avec 20 points
        r2 = requests.get(f"{base_url}/analyse/20")
        amplitudes_data = r2.json()
        print("Analyse:", amplitudes_data)

        # 3. Envoi à l’IA pour détection de danger
        r3 = requests.post(f"http://localhost:8001/danger-alert", json={
            "amplitudes": amplitudes_data["amplitudes"]
        })
        result = r3.json()
        print("Danger:", result)

        # 4. Sauvegarde pour la moyenne finale
        danger_scores.append(result["percent"])

        # Pause de 5 secondes
        time.sleep(5)

    avg_danger = sum(danger_scores) / len(danger_scores)
    print(f"\n🛑 Analyse terminée. Moyenne danger: {avg_danger:.2f}%")

    # Possibilité d’envoyer à ESP32 ici via requête HTTP ou MQTT
    return avg_danger
