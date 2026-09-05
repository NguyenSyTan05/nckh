"""
Module Train Tiếng Việt - Bước 2: Huấn luyện Whisper LoRA Tiếng Việt (Bảo toàn 5 dấu thanh)
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
sys.path.insert(0, "d:/TailieuNPKH")

import torch

def main():
    parser = argparse.ArgumentParser(description="Train Whisper LoRA Tiếng Việt")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--smoke_test", action="store_true", help="Chạy thử nhanh 50 steps")
    args = parser.parse_args()

    print("=" * 70)
    print("🇻🇳 [TRAIN TIẾNG VIỆT - BƯỚC 2] HUẤN LUYỆN LORA CHUYÊN GIA TIẾNG VIỆT")
    print("=" * 70)

    curr_dir = Path(__file__).parent
    output_dir = curr_dir / "output_model_vi_lora"
    train_file = curr_dir / "manifest_vi_train.jsonl"
    val_file = curr_dir / "manifest_vi_val.jsonl"

    if not train_file.exists() or not val_file.exists():
        import subprocess
        subprocess.run([sys.executable, str(curr_dir / "01_chuan_bi_du_lieu_vi.py")], check=True)

    from classbridge.training.finetune_whisper_lora import main as run_finetune
    
    cmd_args = [
        "finetune_whisper_lora.py",
        "--train", str(train_file),
        "--validation", str(val_file),
        "--output", str(output_dir),
        "--model", "openai/whisper-base",
        "--language", "vi",
        "--epochs", str(args.epochs),
        "--learning-rate", str(args.lr),
        "--batch-size", str(args.batch_size),
        "--gradient-accumulation", "2",
        "--lora-rank", "16",
        "--lora-alpha", "32",
    ]
    if args.smoke_test:
        cmd_args.append("--smoke-test")

    sys.argv = cmd_args

    try:
        run_finetune()
        print(f"\n✅ Hoàn tất huấn luyện Module Tiếng Việt -> {output_dir}")
    except Exception as e:
        print(f"ℹ️ Huấn luyện kết thúc: {e}")

if __name__ == "__main__":
    main()
