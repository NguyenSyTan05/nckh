"""
ClassBridge 2-Module Training Suite
Script: 01_chuan_bi_du_lieu_2_module.py
Chức năng: Chuẩn bị 92 mẫu Tiếng Việt siêu gọn (46 người x 2 mẫu) và 50 mẫu Tiếng Anh Accent
"""

import io
import os
import sys
import json
import random
from pathlib import Path
from collections import defaultdict

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


def normalize_casing(text: str) -> str:
    text = text.strip()
    if not text:
        return ""
    text = text.lower()
    text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
    if text and text[-1] not in ".?!,":
        text += "."
    return text


def main():
    print("=" * 80)
    print("🚀 [BƯỚC 1] SIÊU TINH GỌN: 92 MẪU TIẾNG VIỆT & 50 MẪU TIẾNG ANH")
    print("=" * 80)

    base_dir = Path("d:/TailieuNPKH/DoAN2module/Module_Train")
    manifests_dir = base_dir / "manifests"
    manifests_dir.mkdir(parents=True, exist_ok=True)

    src_vivos = Path("d:/TailieuNPKH/classbridge/training/data/vivos/vivos/train")
    src_accent = Path("d:/TailieuNPKH/classbridge/training/data/viet_english_accent/audio")

    # 1. Tạo tập Tiếng Việt chuẩn 92 mẫu (46 người x 2 mẫu/người)
    vi_file = manifests_dir / "manifest_vi_specialist.jsonl"
    speaker_samples = defaultdict(list)
    prompts_file = src_vivos / "prompts.txt"

    if prompts_file.exists():
        with open(prompts_file, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(" ", 1)
                if len(parts) == 2:
                    spk_id, raw_text = parts
                    spk_folder = spk_id.split("_")[0]
                    audio_path = src_vivos / "waves" / spk_folder / f"{spk_id}.wav"
                    if audio_path.exists():
                        speaker_samples[spk_folder].append({
                            "audio": str(audio_path).replace("\\", "/"),
                            "audio_filepath": str(audio_path).replace("\\", "/"),
                            "text": normalize_casing(raw_text),
                            "language": "vi",
                            "speaker_id": spk_folder,
                            "module": "module_vi_specialist"
                        })

    SPEAKER_CAP = 2
    vi_records = []
    for spk, samples in sorted(speaker_samples.items()):
        random.seed(42)
        random.shuffle(samples)
        vi_records.extend(samples[:SPEAKER_CAP])

    random.seed(42)
    random.shuffle(vi_records)

    with open(vi_file, "w", encoding="utf-8") as f:
        for r in vi_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"✅ Đã tạo Manifest Tiếng Việt: {len(vi_records)} mẫu (Siêu gọn 92 mẫu) -> {vi_file}")

    # 2. Tạo tập Tiếng Anh cân bằng (50 mẫu)
    en_file = manifests_dir / "manifest_en_specialist.jsonl"
    en_records = []
    if src_accent.exists():
        for wav in src_accent.glob("*.wav"):
            wav_str = str(wav).replace("\\", "/")
            en_records.append({
                "audio": wav_str,
                "audio_filepath": wav_str,
                "text": "Academic English lecture with technology terminology.",
                "language": "en",
                "speaker_id": "spk_accent",
                "accent": "vietnamese_accent_english",
                "module": "module_en_specialist"
            })
    random.seed(42)
    random.shuffle(en_records)
    en_records = en_records[:50]

    with open(en_file, "w", encoding="utf-8") as f:
        for r in en_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"✅ Đã tạo Manifest Tiếng Anh: {len(en_records)} mẫu -> {en_file}")

    print("=" * 80)

if __name__ == "__main__":
    main()
