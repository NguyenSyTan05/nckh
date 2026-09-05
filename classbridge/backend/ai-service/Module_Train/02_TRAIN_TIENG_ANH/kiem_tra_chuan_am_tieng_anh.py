"""
Kiểm Tra Nhận Diện Âm Tiếng Anh & Accent Trực Tiếp Bằng Mô Hình CTranslate2 Vừa Huấn Luyện
"""

import io
import os
import sys
import json
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Virtualenv
venv_site = Path("d:/TailieuNPKH/classbridge/backend/ai-service/.venv/Lib/site-packages")
if venv_site.exists():
    sys.path.insert(0, str(venv_site))


def calculate_wer(reference: str, hypothesis: str) -> float:
    ref_words = reference.lower().strip().split()
    hyp_words = hypothesis.lower().strip().split()
    if not ref_words:
        return 0.0 if not hyp_words else 1.0

    d = [[0] * (len(hyp_words) + 1) for _ in range(len(ref_words) + 1)]
    for i in range(len(ref_words) + 1):
        d[i][0] = i
    for j in range(len(hyp_words) + 1):
        d[0][j] = j

    for i in range(1, len(ref_words) + 1):
        for j in range(1, len(hyp_words) + 1):
            if ref_words[i - 1] == hyp_words[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                d[i][j] = min(
                    d[i - 1][j] + 1,      # Deletion
                    d[i][j - 1] + 1,      # Insertion
                    d[i - 1][j - 1] + 1   # Substitution
                )
    return d[len(ref_words)][len(hyp_words)] / len(ref_words)


def main():
    print("=" * 80)
    print("🇬🇧 KIỂM TRA ĐỘ CHÍNH XÁC MÔ HÌNH TIẾNG ANH & ACCENT TRÊN GPU")
    print("=" * 80)

    from faster_whisper import WhisperModel
    import torch

    curr_dir = Path(__file__).parent
    model_path = curr_dir / "model_en_ct2"
    if not model_path.exists():
        model_path = Path("d:/TailieuNPKH/classbridge/backend/ai-service/whisper-decoder-micro4-en-ct2")
    if not model_path.exists():
        model_path = Path("d:/TailieuNPKH/classbridge/backend/ai-service/whisper-large-v3-turbo-ct2")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"

    print(f"📦 Mô hình CTranslate2 : {model_path}")
    print(f"⚙️ Thiết bị phần cứng  : {device.upper()} ({compute_type})")

    model = WhisperModel(str(model_path), device=device, compute_type=compute_type)

    val_file = curr_dir / "manifest_en_val.jsonl"
    if not val_file.exists():
        val_file = curr_dir / "manifest_en.jsonl"

    if not val_file.exists():
        print(f"❌ Không tìm thấy {val_file}")
        return

    samples = []
    with open(val_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    samples.append(json.loads(line.strip()))
                except Exception:
                    pass

    test_samples = [s for s in samples if os.path.exists(s.get("audio") or s.get("audio_filepath", ""))]
    test_samples = test_samples[:5]  # Lấy 5 mẫu ngẫu nhiên từ tập Val để test

    if not test_samples:
        print("❌ Không có mẫu âm thanh kiểm thử hợp lệ trên ổ đĩa!")
        return

    print(f"\n📊 Đang kiểm tra {len(test_samples)} mẫu âm thanh kiểm thử Tiếng Anh & Accent...")
    print("-" * 80)

    total_wer = 0.0
    latencies = []

    for i, s in enumerate(test_samples, 1):
        audio_p = s.get("audio") or s.get("audio_filepath")
        ref_text = s.get("text", "")

        t0 = time.perf_counter()
        segments, _ = model.transcribe(audio_p, language="en", beam_size=1)
        pred_text = " ".join([seg.text.strip() for seg in segments]).strip()
        latency = (time.perf_counter() - t0) * 1000
        latencies.append(latency)

        wer = calculate_wer(ref_text, pred_text) if ref_text else 0.0
        total_wer += wer

        print(f"[{i}/{len(test_samples)}] 🎙️ Accent: {s.get('accent', 'English')}")
        print(f"   📖 Lời gốc (Reference)  : \"{ref_text}\"")
        print(f"   🤖 AI Nhận diện (Output): \"{pred_text}\"")
        print(f"   ⏱️ Độ trễ: {latency:.1f} ms | Lỗi WER: {wer*100:.1f}%\n")

    avg_wer = (total_wer / len(test_samples)) * 100
    avg_acc = max(0.0, 100.0 - avg_wer)
    avg_lat = sum(latencies) / len(latencies)

    print("=" * 80)
    print("🏆 TỔNG KẾT KẾT QUẢ ĐO ĐẠC TIẾNG ANH & ACCENT:")
    print(f"   ✅ Độ chính xác từ (Word Accuracy) : {avg_acc:.2f}%")
    print(f"   ✅ Tỷ lệ lỗi trung bình (Avg WER)   : {avg_wer:.2f}%")
    print(f"   ⚡ Độ trễ trung bình trên GPU       : {avg_lat:.1f} ms / câu")
    print("=" * 80)


if __name__ == "__main__":
    main()
