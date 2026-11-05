"""
Module Train Tiếng Anh - Bước 1: Chuẩn bị dữ liệu Tiếng Anh & Accent Châu Á / Người Việt
Quét siêu tốc bằng os.scandir và xác thực kiểm định file wav.
"""
import io
import os
import sys
import json
import random
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Nạp môi trường venv
venv_site = Path("d:/TailieuNPKH/classbridge/backend/ai-service/.venv/Lib/site-packages")
if venv_site.exists():
    sys.path.insert(0, str(venv_site))

import soundfile as sf


def parse_sample_txt(txt_path: str) -> dict:
    info = {}
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    key, val = line.split(":", 1)
                    info[key.strip()] = val.strip()
    except Exception:
        pass
    return info


def main():
    print("=" * 80)
    print("🇬🇧 [TRAIN TIẾNG ANH - BƯỚC 1] CHUẨN BỊ & KIỂM ĐỊNH MANIFEST TIẾNG ANH & ACCENT")
    print("=" * 80)

    curr_dir = Path(__file__).parent
    train_file = curr_dir / "manifest_en_train.jsonl"
    val_file = curr_dir / "manifest_en_val.jsonl"
    all_file = curr_dir / "manifest_en.jsonl"

    samples_dir = "d:/TailieuNPKH/classbridge/backend/data/samples"
    valid_records = []

    print("🔍 Đang quét nhanh bằng os.scandir...")

    if os.path.exists(samples_dir):
        # Thu thập các file en_accent
        with os.scandir(samples_dir) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.startswith("en_accent_") and entry.name.endswith(".txt"):
                    txt_path = entry.path
                    wav_path = txt_path[:-4] + ".wav"
                    if not os.path.exists(wav_path):
                        continue

                    # Kiểm tra kích thước file > 10KB
                    if os.path.getsize(wav_path) < 10240:
                        continue

                    parsed = parse_sample_txt(txt_path)
                    text = parsed.get("text", "").strip()
                    if not text or len(text) < 3:
                        continue

                    # Xác thực mở được bằng soundfile
                    try:
                        info = sf.info(wav_path)
                        if info.duration < 0.3 or info.duration > 30.0:
                            continue
                    except Exception:
                        continue

                    valid_records.append({
                        "audio": wav_path.replace("\\", "/"),
                        "audio_filepath": wav_path.replace("\\", "/"),
                        "text": text,
                        "language": "en",
                        "speaker_id": parsed.get("speaker", "en_spk"),
                        "accent": parsed.get("accent", "en_accent")
                    })

                    if len(valid_records) >= 300:  # Đủ mẫu thì dừng quét ngay
                        break

    print(f"✅ Đã tìm thấy và kiểm định thành công {len(valid_records)} mẫu âm thanh hợp lệ 100%!")

    random.seed(42)
    random.shuffle(valid_records)
    selected_records = valid_records[:200]  # Giữ đúng 200 mẫu

    split_idx = max(1, int(len(selected_records) * 0.9))
    train_recs = selected_records[:split_idx]
    val_recs = selected_records[split_idx:]

    with open(train_file, "w", encoding="utf-8") as f:
        for r in train_recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(val_file, "w", encoding="utf-8") as f:
        for r in val_recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(all_file, "w", encoding="utf-8") as f:
        for r in selected_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Đồng bộ sang thư mục manifests chung
    shared_manifest = Path(__file__).resolve().parent.parent / "manifests" / "manifest_en_specialist.jsonl"
    if shared_manifest.parent.exists():
        with open(shared_manifest, "w", encoding="utf-8") as f:
            for r in train_recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"📊 Phân chia tập dữ liệu:")
    print(f"   • Train (90%)      : {len(train_recs)} mẫu -> {train_file}")
    print(f"   • Validation (10%) : {len(val_recs)} mẫu -> {val_file}")
    print(f"   • Tổng hợp         : {len(selected_records)} mẫu -> {all_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
