"""
ClassBridge 2-Module Training Suite
Script: 05_train_dich_thuat_envit5.py
Chức năng: Huấn luyện mô hình Dịch thuật EnViT5 LoRA cân bằng 2 chiều VI <-> EN
Tối ưu: Giữ nguyên thuật ngữ CNTT, ngữ pháp chuẩn mực học thuật giảng đường.
"""

import io
import os
import sys
import argparse
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Dependencies
venv_site = Path("d:/TailieuNPKH/classbridge/backend/ai-service/.venv/Lib/site-packages")
if venv_site.exists():
    sys.path.insert(0, str(venv_site))

def main():
    print("=" * 80)
    print("🌐 [BƯỚC 5] HUẤN LUYỆN MÔ HÌNH DỊCH THUẬT SONG NGỮ ENVIT5 LORA")
    print("=" * 80)

    output_dir = Path("d:/TailieuNPKH/DoAN2module/04_TRANSLATION_MODULE/model_envit5_lora")
    output_dir.mkdir(parents=True, exist_ok=True)

    from classbridge.training.train_balanced_translation import main as run_train_trans
    
    try:
        print("\n🚀 Bắt đầu quá trình huấn luyện Dịch thuật EnViT5...")
        run_train_trans()
        print("\n✅ Hoàn tất huấn luyện Module Dịch thuật EnViT5!")
    except Exception as e:
        print(f"ℹ️ Huấn luyện kết thúc: {e}")

if __name__ == "__main__":
    main()
