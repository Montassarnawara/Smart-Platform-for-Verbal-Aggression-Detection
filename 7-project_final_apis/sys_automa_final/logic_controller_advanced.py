import requests
import time
import os
import sys
from analyze import AudioFeatureExtractor

def start_analysis_cycle_advanced(base_url="http://localhost:8000", ai_url="http://localhost:8001"):
    """Cycle d'analyse avancé avec IA et modèles ML"""
    danger_scores = []
    all_analysis_data = []
    
    print("==> Démarrage de l'analyse avancée avec IA (1 minute)")
    
    # Initialiser l'extracteur de features audio
    extractor = AudioFeatureExtractor()

    for i in range(2):  # 2 tranches de 10s = 20s
        print(f"\n--- Segment {i+1}/2 ---")

        try:
            # 1. Enregistrement de 10s
            r1 = requests.get(f"{base_url}/check_and_record")
            record_result = r1.json()
            print("Enregistrement:", record_result)
            
            if "error" in record_result:
                print(f"❌ Erreur d'enregistrement: {record_result['error']}")
                continue

            # 2. Analyse avancée du fichier audio avec analyze.py
            # Récupérer le chemin du dernier fichier enregistré
            audio_path = get_latest_audio_file()
            
            if not audio_path or not os.path.exists(audio_path):
                print("❌ Fichier audio non trouvé")
                continue
                
            print(f"📊 Analyse du fichier: {audio_path}")
            
            # Utiliser AudioFeatureExtractor pour l'analyse complète
            analysis_result = extractor.process_audio_file(audio_path)
            
            if not analysis_result["detail"]:
                print("❌ Échec de l'analyse audio")
                continue
                
            print(f"✅ Analyse réussie: {len(analysis_result['detail'])} tranches analysées")
            all_analysis_data.append(analysis_result)

            # 3. Envoi à l'IA pour détection de danger avancée
            try:
                r3 = requests.post(f"{ai_url}/danger-alert-advanced", json=analysis_result)
                if r3.status_code == 200:
                    ai_result = r3.json()
                    print(f"🤖 IA Danger: {ai_result['percent']}%")
                    
                    # Afficher les détails des prédictions
                    if "slice_predictions" in ai_result:
                        slice_pred = ai_result["slice_predictions"]
                        print(f"   - Danger moyen: {slice_pred['average_danger']:.1f}%")
                        print(f"   - Danger max: {slice_pred['max_danger']:.1f}%")
                        print(f"   - Danger min: {slice_pred['min_danger']:.1f}%")
                    
                    if "file_predictions" in ai_result:
                        file_pred = ai_result["file_predictions"]
                        if not isinstance(file_pred, dict) or "error" not in file_pred:
                            print(f"   - Prédiction fichier: max={file_pred.get('danger_max', 'N/A'):.1f}%, moy={file_pred.get('danger_moy', 'N/A'):.1f}%")
                    
                    if "analysis_summary" in ai_result:
                        summary = ai_result["analysis_summary"]
                        print(f"   - Cris détectés: {summary.get('nb_cris_detectes', 0)}")
                        if summary.get('cri_types') and summary['cri_types'] != ['aucun']:
                            print(f"   - Types de cris: {', '.join(summary['cri_types'])}")
                    
                    danger_scores.append(ai_result["percent"])
                else:
                    print(f"❌ Erreur API IA: {r3.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Erreur de connexion à l'IA: {str(e)}")
                # Fallback sur l'analyse simple
                fallback_result = analyze_simple_fallback(audio_path)
                if fallback_result:
                    danger_scores.append(fallback_result)

        except Exception as e:
            print(f"❌ Erreur dans le segment {i+1}: {str(e)}")
            continue

        # Pause de 5 secondes
        time.sleep(5)

    # Calcul des statistiques finales
    if danger_scores:
        avg_danger = sum(danger_scores) / len(danger_scores)
        max_danger = max(danger_scores)
        min_danger = min(danger_scores)
        
        print(f"\n🛑 Analyse terminée avec IA:")
        print(f"   📊 Moyenne danger: {avg_danger:.2f}%")
        print(f"   📈 Danger maximum: {max_danger:.2f}%")
        print(f"   📉 Danger minimum: {min_danger:.2f}%")
        print(f"   🔢 Segments analysés: {len(danger_scores)}/12")
        
        # Évaluation du niveau de risque
        risk_level = evaluate_risk_level(avg_danger, max_danger)
        print(f"   ⚠️  Niveau de risque: {risk_level}")
        
        return {
            "average_danger": avg_danger,
            "max_danger": max_danger,
            "min_danger": min_danger,
            "risk_level": risk_level,
            "segments_analyzed": len(danger_scores),
            "all_scores": danger_scores
        }
    else:
        print("❌ Aucune analyse réussie")
        return {"error": "Aucune analyse réussie", "average_danger": 0}

def get_latest_audio_file(audio_dir="audio_chunks"):
    """Récupère le chemin du dernier fichier audio enregistré"""
    try:
        # Essayer plusieurs répertoires possibles
        possible_dirs = [audio_dir, ".", "data", "d", "audio_chunks"]
        
        for dir_path in possible_dirs:
            if os.path.exists(dir_path):
                files = [f for f in os.listdir(dir_path) if f.endswith('.wav')]
                if files:
                    # Récupérer le fichier le plus récent
                    latest_file = max(files, key=lambda x: os.path.getmtime(os.path.join(dir_path, x)))
                    return os.path.join(dir_path, latest_file)
        
        return None
            
    except Exception as e:
        print(f"Erreur lors de la recherche du fichier audio: {str(e)}")
        return None

def analyze_simple_fallback(audio_path):
    """Analyse simple en cas d'échec de l'IA"""
    try:
        from analyze import extract_amplitudes
        amplitudes = extract_amplitudes(audio_path, target_rate=100, limit=50)
        
        if isinstance(amplitudes, dict) and "error" in amplitudes:
            return None
            
        # Analyse simple basée sur les amplitudes
        import numpy as np
        amp_array = np.array(amplitudes if isinstance(amplitudes, list) else [])
        
        if len(amp_array) == 0:
            return None
            
        rms = np.sqrt(np.mean(amp_array ** 2))
        peak = np.max(np.abs(amp_array))
        variation = np.std(amp_array)
        
        # Score simple
        score = 0.4 * (20 * np.log10(rms + 1e-6) + 100) + 30 * peak + 20 * variation
        danger_percent = min(100, int(score))
        
        print(f"🔄 Fallback analyse simple: {danger_percent}%")
        return danger_percent
        
    except Exception as e:
        print(f"❌ Erreur fallback: {str(e)}")
        return None

def evaluate_risk_level(avg_danger, max_danger):
    """Évalue le niveau de risque basé sur les pourcentages de danger"""
    if max_danger >= 80 or avg_danger >= 70:
        return "🔴 CRITIQUE"
    elif max_danger >= 60 or avg_danger >= 50:
        return "🟠 ÉLEVÉ"
    elif max_danger >= 40 or avg_danger >= 30:
        return "🟡 MODÉRÉ"
    elif max_danger >= 20 or avg_danger >= 15:
        return "🟢 FAIBLE"
    else:
        return "⚪ MINIMAL"

# Conserver la fonction originale pour compatibilité
def start_analysis_cycle(base_url="http://localhost:8000"):
    """Version simple originale (pour compatibilité)"""
    danger_scores = []

    print("==> Démarrage de l'analyse de 1 minute (version simple)")

    for i in range(2):  # 2 tranches de 10s = 20s
        print(f"\n--- Segment {i+1}/2 ---")

        try:
            # 1. Enregistrement de 10s
            r1 = requests.get(f"{base_url}/check_and_record")
            print("Enregistrement:", r1.json())

            # 2. Analyse du dernier fichier avec 20 points
            r2 = requests.get(f"{base_url}/analyse/20")
            amplitudes_data = r2.json()
            print("Analyse:", amplitudes_data)

            # 3. Envoi à l'IA pour détection de danger
            r3 = requests.post(f"http://localhost:8001/danger-alert", json={
                "amplitudes": amplitudes_data["amplitudes"]
            })
            result = r3.json()
            print("Danger:", result)

            # 4. Sauvegarde pour la moyenne finale
            danger_scores.append(result["percent"])

        except Exception as e:
            print(f"❌ Erreur dans le segment {i+1}: {str(e)}")

        # Pause de 5 secondes
        time.sleep(5)

    if danger_scores:
        avg_danger = sum(danger_scores) / len(danger_scores)
        print(f"\n🛑 Analyse terminée. Moyenne danger: {avg_danger:.2f}%")
        return avg_danger
    else:
        print("❌ Aucune analyse réussie")
        return 0

# Script de test
if __name__ == "__main__":
    print("🧪 Test du logic controller avancé")
    
    # Test de la nouvelle fonction
    result = start_analysis_cycle_advanced()
    print(f"\n📊 Résultat final: {result}")
