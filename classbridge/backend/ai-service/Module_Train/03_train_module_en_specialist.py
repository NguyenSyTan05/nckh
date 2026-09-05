"""
ClassBridge 2-Module Training Suite
Script: 03_train_module_en_specialist.py
Chức năng: Huấn luyện LoRA chuyên sâu cho Module 2: Chuyên gia Tiếng Anh & Accent (English Specialist)
Tối ưu: Nhận diện giọng Tiếng Anh người Việt, thuật ngữ CNTT quốc tế (Docker, API, Kubernetes, etc.).
"""

import io
import os
import sys
import argparse
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Thêm dependencies
venv_site = Path("d:/TailieuNPKH/classbridge/backend/ai-service/.venv/Lib/site-packages")
if venv_site.exists():
    sys.path.insert(0, str(venv_site))

import torch

def main():
    parser = argparse.ArgumentParser(description="Train Module 2 - English & Accent Specialist")
    parser.add_argument("--epochs", type=int, default=3, help="Số epoch huấn luyện")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--batch_size", type=int, default=4, help="Batch size")
    args = parser.parse_args()

    print("=" * 80)
    print("🇬🇧 [BƯỚC 3] HUẤN LUYỆN MODULE 2: CHUYÊN GIA TIẾNG ANH & ACCENT (ENGLISH SPECIALIST)")
    print("=" * 80)

    output_dir = Path("d:/TailieuNPKH/DoAN2module/Module_Train/outputs/model_en_lora")
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = Path("d:/TailieuNPKH/DoAN2module/Module_Train/manifests/manifest_en_specialist.jsonl")
    if not manifest_path.exists():
        print("⚠️ Chưa có manifest. Đang tự động chạy Bước 1...")
        import subprocess
        subprocess.run([sys.executable, "d:/TailieuNPKH/DoAN2module/Module_Train/01_chuan_bi_du_lieu_2_module.py"], check=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"⚙️ Thiết bị phần cứng: {device.upper()}")
    if device == "cuda":
        print(f"🎮 Card đồ họa: {torch.cuda.get_device_name(0)}")

    print(f"\n📊 Cấu hình huấn luyện:")
    print(f"   - Epochs       : {args.epochs}")
    print(f"   - Learning Rate: {args.lr}")
    print(f"   - Batch Size   : {args.batch_size}")
    print(f"   - Ngôn ngữ     : Tiếng Anh (en)")
    print(f"   - Output Dir   : {output_dir}")

    # Gọi hàm huấn luyện Whisper LoRA Accent
    from classbridge.training.train_accent_module import main as run_accent_train
    
    try:
        print("\n🚀 Bắt đầu quá trình huấn luyện LoRA Tiếng Anh & Accent...")
        run_accent_train()
        print("\n✅ Hoàn tất huấn luyện Module 2 (Tiếng Anh & Accent)!")
    except Exception as e:
        print(f"ℹ️ Huấn luyện kết thúc: {e}")

if __name__ == "__main__":
    main()
