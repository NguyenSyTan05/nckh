"""
Module Train Dịch Thuật - Bước 1: Huấn luyện EnViT5 LoRA Song Ngữ (VI <-> EN)
"""
import io
import os
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Dependencies
venv_site = Path("d:/TailieuNPKH/classbridge/backend/ai-service/.venv/Lib/site-packages")
if venv_site.exists():
    sys.path.insert(0, str(venv_site))
project_parent = str(Path(__file__).resolve().parents[3])
if project_parent not in sys.path:
    sys.path.insert(0, project_parent)

def main():
    print("=" * 70)
    print("🌐 [TRAIN DỊCH THUẬT] HUẤN LUYỆN ENVIT5 LORA SONG NGỮ CÂN BẰNG 2 CHIỀU")
    print("=" * 70)

    from classbridge.training.train_balanced_translation import main as run_train_trans
    try:
        run_train_trans()
        print("\n✅ Hoàn tất huấn luyện Module Dịch thuật EnViT5!")
    except Exception as e:
        print(f"ℹ️ Huấn luyện kết thúc: {e}")

if __name__ == "__main__":
    main()
