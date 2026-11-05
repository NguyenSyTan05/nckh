"""
Module Train Tiếng Anh - Bước 3: Xuất Model Tiếng Anh & Accent sang CTranslate2 Float16 cho GPU
Chức năng: Hợp nhất (Merge) trọng số LoRA Tiếng Anh vào Whisper Base và chuyển đổi sang CTranslate2 Float16.
"""

import io
import os
import sys
import subprocess
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Nạp môi trường venv
venv_site = Path("d:/TailieuNPKH/classbridge/backend/ai-service/.venv/Lib/site-packages")
if venv_site.exists():
    sys.path.insert(0, str(venv_site))
sys.path.insert(0, "d:/TailieuNPKH")


def main():
    print("=" * 80)
    print("🇬🇧 [TRAIN TIẾNG ANH - BƯỚC 3] XUẤT MÔ HÌNH SANG CTRANSLATE2 FLOAT16 GPU")
    print("=" * 80)

    curr_dir = Path(__file__).parent
    lora_dir = curr_dir / "output_model_en_lora"
    merged_dir = curr_dir / "output_model_en_merged"
    ct2_dir = curr_dir / "model_en_ct2"

    if not lora_dir.exists():
        print(f"❌ Không tìm thấy thư mục LoRA tại: {lora_dir}")
        print("💡 Vui lòng chạy Bước 2 (02_train_whisper_en_accent_lora.py) trước để huấn luyện!")
        return

    from classbridge.training.export_whisper_lora import main as run_export

    sys.argv = [
        "export_whisper_lora.py",
        "--base-model", "openai/whisper-base",
        "--adapter", str(lora_dir),
        "--merged-output", str(merged_dir),
        "--ct2-output", str(ct2_dir),
        "--quantization", "float16"
    ]

    try:
        run_export()
        print(f"\n🎉 HOÀN TẤT XUẤT MÔ HÌNH TIẾNG ANH & ACCENT:")
        print(f"   📁 Model Merged HuggingFace : {merged_dir}")
        print(f"   ⚡ Model CTranslate2 Float16 : {ct2_dir}")
        print("=" * 80)
    except Exception as e:
        print(f"❌ Lỗi khi xuất CTranslate2: {e}")


if __name__ == "__main__":
    main()
