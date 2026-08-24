"""
ClassBridge - Real Human Dataset Recorder & Quality Verifier
Công cụ thu thập dữ liệu âm thanh thực tế, kiểm tra chất lượng audio (RMS/Silence/Peak) & xác nhận Transcript từ người thật.

Quy trình chuẩn hóa:
1. Nhập Speaker ID thật (đảm bảo ít nhất 2 speaker_vi, 2 speaker_en riêng biệt).
2. Chọn Ngôn ngữ, Accent (7 vùng miền VN + 5 English accents), Scenario.
3. Thu âm PCM 16kHz Mono WAV từ microphone.
4. Kiểm tra chất lượng: Độ dài, RMS Energy, Peak Amplitude (Từ chối file im lặng/nhiễu quá bé).
5. Cho phép: [1] Nghe lại, [2] Thu lại, [3] Chấp nhận.
6. Chạy Whisper gợi ý -> Người dùng xác nhận/sửa ground truth -> Lưu `transcript_verified: true`.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
from typing import Any, Dict, List, Optional

# ── Auto-inject virtualenv site-packages ──────────────────────────────────────
_VENV = Path(__file__).resolve().parent.parent / "backend" / "ai-service" / ".venv" / "Lib" / "site-packages"
if _VENV.exists() and str(_VENV) not in sys.path:
    sys.path.insert(0, str(_VENV))

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
SAMPLES_DIR = DATA_DIR / "samples"
MANIFEST_PATH = DATA_DIR / "bilingual_sample_manifest.jsonl"

SAMPLE_RATE = 16000
CHANNELS = 1

# Các danh mục Accent chuẩn hóa
ACCENT_OPTIONS = {
    # Tiếng Việt 7 vùng miền
    "1": ("vi_north_hanoi", "Tiếng Việt - Hà Nội"),
    "2": ("vi_north_outer", "Tiếng Việt - Bắc ngoài Hà Nội"),
    "3": ("vi_central_nghean", "Tiếng Việt - Nghệ An / Hà Tĩnh"),
    "4": ("vi_central_hue", "Tiếng Việt - Huế"),
    "5": ("vi_central_quangnam", "Tiếng Việt - Quảng Nam / Đà Nẵng"),
    "6": ("vi_south_hcm", "Tiếng Việt - TP.HCM / Đông Nam Bộ"),
    "7": ("vi_south_mientay", "Tiếng Việt - Miền Tây"),
    # Tiếng Anh & Pha trộn
    "8": ("en_us", "English - US Accent"),
    "9": ("en_uk", "English - UK Accent"),
    "10": ("en_indian", "English - Indian Accent"),
    "11": ("en_asian", "English - Asian Accent"),
    "12": ("en_vietnamese_accent", "English - Vietnamese Accent"),
    "13": ("mixed_en_vi", "Anh-Việt Pha Trộn (Code-switching)"),
}

SCENARIO_OPTIONS = {
    "1": "clean_mic",
    "2": "phone_to_laptop",
    "3": "classroom_noise",
    "4": "far_mic",
    "5": "fast_speech",
    "6": "normal_speech",
    "7": "it_terminology",
}


def load_baseline_whisper() -> Any:
    """Nạp faster-whisper-small model gợi ý transcript."""
    try:
        from faster_whisper import WhisperModel
        print("📥 Đang nạp faster-whisper-small để gợi ý transcript...")
        model = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=2)
        return model
    except Exception as e:
        print(f"⚠️  Không thể nạp faster-whisper: {e}")
        return None


def record_audio_clip(duration: float = 6.0) -> Optional[Any]:
    """Thu âm từ micro bằng sounddevice."""
    try:
        import sounddevice as sd
        print(f"\n🎙️ BẮT ĐẦU THU ÂM TRONG {duration} GIÂY... Hãy nói ngay!")
        recording = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="float32")
        sd.wait()
        print("✅ Thu âm hoàn tất!")
        return recording
    except Exception as e:
        print(f"❌ Không thể truy cập Micro: {e}")
        return None


def verify_audio_quality(audio_data: Any) -> tuple[bool, str, float, float]:
    """Kiểm tra RMS Energy & Peak Amplitude để loại bỏ file im lặng."""
    import numpy as np
    arr = np.asarray(audio_data, dtype=np.float32)
    if arr.size == 0:
        return False, "Audio rỗng", 0.0, 0.0
    
    rms = float(np.sqrt(np.mean(arr * arr) + 1e-9))
    peak = float(np.max(np.abs(arr)))

    if rms < 0.005:
        return False, f"Âm thanh quá bé hoặc im lặng (RMS={rms:.4f} < 0.005)", rms, peak
    if peak < 0.02:
        return False, f"Tín hiệu đỉnh quá thấp (Peak={peak:.4f} < 0.02)", rms, peak

    return True, "Chất lượng âm thanh đạt chuẩn", rms, peak


def play_audio_clip(audio_data: Any):
    """Phát lại âm thanh vừa thu."""
    try:
        import sounddevice as sd
        print("🔊 Đang phát lại âm thanh...")
        sd.play(audio_data, SAMPLE_RATE)
        sd.wait()
    except Exception as e:
        print(f"⚠️  Không thể phát lại âm thanh: {e}")


def main_recorder():
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("=========================================================================")
    print("   ClassBridge AI - REAL HUMAN DATASET COLLECTOR & VERIFIER             ")
    print("=========================================================================")
    print("Mục tiêu: Thu âm giọng nói người thật & xác nhận Human Transcript 100%.")
    print("-------------------------------------------------------------------------")

    speaker_id = input("👉 Nhập Speaker ID người nói (VD: speaker_vi_01, speaker_en_01): ").strip()
    if not speaker_id:
        print("❌ Speaker ID không được để trống!")
        sys.exit(1)

    print("\n👉 Chọn Accent phân loại:")
    for k, v in ACCENT_OPTIONS.items():
        print(f"   [{k:2s}] {v[1]} ({v[0]})")
    accent_choice = input("Lựa chọn [1-13]: ").strip()
    accent_code, accent_name = ACCENT_OPTIONS.get(accent_choice, ("vi_north_hanoi", "Tiếng Việt - Hà Nội"))

    lang = "en" if accent_code.startswith("en") else "vi"

    print("\n👉 Chọn Scenario môi trường:")
    for k, v in SCENARIO_OPTIONS.items():
        print(f"   [{k}] {v}")
    scen_choice = input("Lựa chọn [1-7]: ").strip()
    scenario_code = SCENARIO_OPTIONS.get(scen_choice, "normal_speech")

    whisper_model = load_baseline_whisper()
    sample_counter = len(list(SAMPLES_DIR.glob("*.wav"))) + 1

    import soundfile as sf

    while True:
        print("\n-------------------------------------------------------------------------")
        prompt_text = input("👉 Nhập câu chuẩn dự kiến sẽ đọc (hoặc gõ 'exit' để dừng): ").strip()
        if prompt_text.lower() == "exit":
            break
        if not prompt_text:
            continue

        while True:
            audio_data = record_audio_clip(duration=6.0)
            if audio_data is None:
                break

            valid, msg, rms, peak = verify_audio_quality(audio_data)
            print(f"📊 Chất lượng audio: RMS={rms:.4f}, Peak={peak:.4f} -> {msg}")
            if not valid:
                print("❌ Âm thanh không đạt tiêu chuẩn. Vui lòng thu lại!")
                continue

            print("\n👉 Tùy chọn âm thanh:")
            print("   [1] Nghe lại")
            print("   [2] Thu lại")
            print("   [3] Chấp nhận & Tiếp tục")
            opt = input("Lựa chọn [1/2/3]: ").strip()
            if opt == "1":
                play_audio_clip(audio_data)
                continue
            elif opt == "2":
                continue
            else:
                break

        if audio_data is None:
            break

        sample_filename = f"sample_real_{speaker_id}_{sample_counter:03d}.wav"
        wav_path = SAMPLES_DIR / sample_filename
        sf.write(str(wav_path), audio_data, SAMPLE_RATE)

        # Gợi ý bằng Whisper (Không tự ý lưu thành ground truth)
        ai_suggestion = ""
        if whisper_model:
            try:
                segments, _ = whisper_model.transcribe(str(wav_path), beam_size=2)
                ai_suggestion = " ".join([s.text.strip() for s in segments]).strip()
                print(f"🤖 Whisper dự đoán gợi ý: \"{ai_suggestion}\"")
            except Exception:
                pass

        print(f"👉 Bản dự kiến: \"{prompt_text}\"")
        final_transcript = input("👉 Xác nhận/Sửa lại bản ghi ĐÚNG từ người thật (Nhấn ENTER nếu bản trên đúng): ").strip()
        if not final_transcript:
            final_transcript = prompt_text

        rel_audio_path = f"data/samples/{sample_filename}"
        row = {
            "audio": rel_audio_path,
            "text": final_transcript,
            "language": lang,
            "speaker_id": speaker_id,
            "accent": accent_code,
            "scenario": scenario_code,
            "human_verified": True,
            "transcript_verified": True,
        }

        with open(MANIFEST_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

        print(f"✅ Đã lưu file WAV: {rel_audio_path}")
        print(f"✅ Đã lưu Manifest (Speaker={speaker_id}, Accent={accent_code}, Verified=True)")
        sample_counter += 1

        cont = input("\nThu tiếp câu khác với speaker này? [Y/n]: ").strip().lower()
        if cont == "n":
            break

    print("\n=========================================================================")
    print(f"🎉 HOÀN TẤT THU DỮ LIỆU THẬT! File manifest hiện tại: {MANIFEST_PATH}")
    print("=========================================================================")


if __name__ == "__main__":
    main_recorder()
