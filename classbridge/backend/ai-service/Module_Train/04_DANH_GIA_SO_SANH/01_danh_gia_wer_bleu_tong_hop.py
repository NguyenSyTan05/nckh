"""
Module Train - Đánh Giá & Báo Cáo Nghiệm Thu Tổng Hợp
"""
import io
import os
import sys
import subprocess
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

def main():
    print("=" * 70)
    print("🔬 [ĐÁNH GIÁ TỔNG HỢP] ĐO ĐẠC WER TIẾNG VIỆT, TIẾNG ANH & BLEU DỊCH THUẬT")
    print("=" * 70)

    test_script = "d:/TailieuNPKH/DoAN2module/test_benchmark_2_module.py"
    subprocess.run([sys.executable, test_script], check=True)

if __name__ == "__main__":
    main()
