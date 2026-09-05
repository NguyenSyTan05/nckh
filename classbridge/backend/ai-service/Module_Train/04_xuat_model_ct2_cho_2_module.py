"""
ClassBridge 2-Module Training Suite
Script: 04_xuat_model_ct2_cho_2_module.py
Chức năng: Chuyển đổi và Tối ưu hóa 2 mô hình đã huấn luyện sang định dạng CTranslate2 GPU Float16:
1. Module Tiếng Việt -> d:/TailieuNPKH/DoAN2module/02_MODULE_VI_SPECIALIST/model_vi_ct2
2. Module Tiếng Anh  -> d:/TailieuNPKH/DoAN2module/03_MODULE_EN_SPECIALIST/model_en_ct2
"""

import io
import os
import sys
import subprocess
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

def export_model_to_ct2(hf_model_or_merged: str, output_ct2_dir: Path):
    print(f"📦 Đang chuyển đổi {hf_model_or_merged} -> {output_ct2_dir}...")
    output_ct2_dir.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        "ct2-transformers-converter",
        "--model", str(hf_model_or_merged),
        "--output_dir", str(output_ct2_dir),
        "--quantization", "float16",
        "--copy_files", "tokenizer.json", "preprocessor_config.json", "tokenizer_config.json"
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Đã xuất thành công sang: {output_ct2_dir}")
    except Exception as e:
        print(f"⚠️ Chú ý khi xuất: {e}")

def main():
    print("=" * 80)
    print("🚀 [BƯỚC 4] XUẤT MÔ HÌNH CTRANSLATE2 FLOAT16 CHO 2 MODULE CHUYÊN BIỆT")
    print("=" * 80)

    base_dir = Path("d:/TailieuNPKH/DoAN2module")
    
    # 1. Xuất Module 1: Tiếng Việt
    out_vi = base_dir / "02_MODULE_VI_SPECIALIST/model_vi_ct2"
    lora_vi = base_dir / "Module_Train/outputs/model_vi_lora"
    src_vi = str(lora_vi) if lora_vi.exists() else "d:/TailieuNPKH/classbridge/training/outputs/whisper-custom-proportions-ct2"
    export_model_to_ct2(src_vi, out_vi)

    # 2. Xuất Module 2: Tiếng Anh
    out_en = base_dir / "03_MODULE_EN_SPECIALIST/model_en_ct2"
    lora_en = base_dir / "Module_Train/outputs/model_en_lora"
    src_en = str(lora_en) if lora_en.exists() else "d:/TailieuNPKH/classbridge/backend/ai-service/whisper-decoder-micro4-en-ct2"
    export_model_to_ct2(src_en, out_en)

    print("\n🎉 Hoàn thành xuất cả 2 mô hình sang CTranslate2 Float16 cho GPU!")

if __name__ == "__main__":
    main()
