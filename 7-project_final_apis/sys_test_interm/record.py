import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import os
import time
from analyze import analyze_audio_chunk

sample_rate = 44100
chunk_duration = 5  # sec
max_duration = 10   # sec
chunk_dir = "audio_chunks"
os.makedirs(chunk_dir, exist_ok=True)

def record_chunk(filename, duration=chunk_duration):
    print(f"Recording {duration}s to {filename}")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()
    wav.write(filename, sample_rate, audio)
    return filename

def start_recording():
    total_chunks = int(max_duration / chunk_duration)
    analysis_results = []

    for i in range(total_chunks):
        fname = os.path.join(chunk_dir, f"chunk_{i}.wav")
        record_chunk(fname)
        analysis = analyze_audio_chunk(fname)
        analysis_results.append(analysis)
        time.sleep(0.5)  # petite pause entre les chunks (optionnel)

    return analysis_results
