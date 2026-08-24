"""
ClassBridge – Layer A: Raw Whisper ASR Benchmark on Real Audio Files
"""
import sys
import os
import json
from pathlib import Path
import soundfile as sf
import numpy as np

# Force UTF-8 output on Windows console
os.environ["PYTHONIOENCODING"] = "utf-8"
for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")


AI_SERVICE_DIR = Path(__file__).resolve().parents[2] / "backend" / "ai-service"
sys.path.insert(0, str(AI_SERVICE_DIR))

import main

audio_dir = Path("d:/TailieuNPKH/classbridge/data/audio/local")
audio_files = [
    ("vi_000.wav", "auto", "Chào mừng đến với buổi học (VI)"),
    ("vi_001.wav", "auto", "Tìm hiểu về trí tuệ nhân tạo (VI)"),
    ("vi_019.wav", "auto", "Kiến trúc microservice (VI mixed)"),
    ("en_000.wav", "auto", "Welcome to today's lecture (EN)"),
    ("en_001.wav", "auto", "Please turn off your mobile phones (EN)"),
    ("en_002.wav", "auto", "Today we will cover chapters (EN)"),
    ("en_003.wav", "auto", "The midterm exam will take place (EN)"),
]

print(f"\n{'='*70}")
print(" LAYER A: RAW ASR WHISPER INFERENCE ON PHYSICAL AUDIO SAMPLES")
print(f"{'='*70}\n")

results = []
for name, lang_mode, desc in audio_files:
    file_path = audio_dir / name
    if not file_path.exists():
        print(f"File {name} not found, skipping...")
        continue
    
    audio_data, sr = sf.read(str(file_path))
    if audio_data.ndim > 1:
        audio_data = audio_data.mean(axis=1)
    audio_data = audio_data.astype(np.float32)

    print(f"▶ File: {name:<25} ({desc} | Mode: {lang_mode} | Peak: {np.max(np.abs(audio_data)):.3f})")
    raw_text, lang, conf, _ = main.transcribe_file(
        audio_source=audio_data,
        language=lang_mode,
        context="",
        audio_profile="hybrid",
        model=main.whisper_fast,
        accurate=False,
    )
    print(f"   [RAW_TEXT]   : {raw_text}")
    print(f"   [DETECT_LANG]: {lang}")
    print(f"   [CONFIDENCE] : {conf:.3f}\n")
    results.append((name, raw_text, lang, conf))

print("======================================================================")
print(f" 🏆 LAYER A (RAW ASR) PROCESSED {len(results)} PHYSICAL AUDIO FILES!")
print("======================================================================")
