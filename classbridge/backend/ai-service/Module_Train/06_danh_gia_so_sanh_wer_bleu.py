"""
ClassBridge 2-Module Training Suite
Script: 06_danh_gia_so_sanh_wer_bleu.py
Chức năng: Đánh giá toàn diện chất lượng sau khi huấn luyện cả 2 module:
- Đo WER Tiếng Việt (Module 1)
- Đo WER Tiếng Anh & Accent (Module 2)
- Đo BLEU Dịch thuật (Module Dịch thuật)
- Xuất báo cáo thực nghiệm chi tiết cho đồ án / NCKH
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
    print("=" * 80)
    print("🔬 [BƯỚC 6] ĐÁNH GIÁ CHẤT LƯỢNG TOÀN DIỆN HỆ THỐNG 2 MODULE (WER & BLEU)")
    print("=" * 80)

    benchmark_script = "d:/TailieuNPKH/DoAN2module/test_benchmark_2_module.py"
    subprocess.run([sys.executable, benchmark_script], check=True)

if __name__ == "__main__":
    main()
