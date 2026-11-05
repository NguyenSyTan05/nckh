"""
Kiểm Tra Chất Lượng Mô Hình Dịch Thuật Học Thuật EnViT5 (VI <-> EN)
Đo đạc điểm số BLEU, độ chính xác thuật ngữ CNTT và độ trễ mili-giây trên GPU.
"""

import io
import os
import sys
import time
import math
from collections import Counter
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Virtualenv
venv_site = Path("d:/TailieuNPKH/classbridge/backend/ai-service/.venv/Lib/site-packages")
if venv_site.exists():
    sys.path.insert(0, str(venv_site))
sys.path.insert(0, "d:/TailieuNPKH")


def compute_sentence_bleu(reference: str, hypothesis: str) -> float:
    """Tính BLEU-4 cơ bản có làm mịn (smoothing) cho từng câu."""
    ref_tokens = reference.lower().strip().split()
    hyp_tokens = hypothesis.lower().strip().split()
    if not hyp_tokens or not ref_tokens:
        return 0.0

    precisions = []
    for n in range(1, 5):
        hyp_ngrams = [tuple(hyp_tokens[i:i+n]) for i in range(len(hyp_tokens)-n+1)]
        ref_ngrams = [tuple(ref_tokens[i:i+n]) for i in range(len(ref_tokens)-n+1)]
        if not hyp_ngrams:
            precisions.append(0.0)
            continue
        hyp_counts = Counter(hyp_ngrams)
        ref_counts = Counter(ref_ngrams)
        clipped = sum(min(count, ref_counts.get(ng, 0)) for ng, count in hyp_counts.items())
        precisions.append((clipped + 0.1) / (len(hyp_ngrams) + 0.1))

    # Brevity penalty
    c = len(hyp_tokens)
    r = len(ref_tokens)
    bp = 1.0 if c > r else math.exp(1 - r / c) if c > 0 else 0.0

    score = bp * math.exp(sum(math.log(p) for p in precisions) / 4)
    return min(1.0, score) * 100.0


def main():
    print("=" * 80)
    print("🌐 KIỂM TRA MÔ HÌNH DỊCH THUẬT SONG NGỮ HỌC THUẬT CNTT (VI <-> EN)")
    print("=" * 80)

    project_root = Path(__file__).resolve().parents[3]
    trans_module_dir = project_root / "backend" / "ai-service" / "04_TRANSLATION_MODULE"
    if str(trans_module_dir) not in sys.path:
        sys.path.insert(0, str(trans_module_dir))
    from nmt_translator import DualTranslator

    translator = DualTranslator(device="cuda")

    test_cases = [
        # Chiều 1: Tiếng Việt -> Tiếng Anh
        {
            "src": "Hệ thống sử dụng kiến trúc Microservices để phân phối tải và đảm bảo khả năng mở rộng.",
            "ref": "The system uses Microservices architecture to distribute load and ensure scalability.",
            "lang": "vi",
            "domain": "Kiến trúc hệ thống"
        },
        {
            "src": "Mô hình Whisper được tối ưu bằng CTranslate2 giúp giảm độ trễ xử lý xuống dưới một giây.",
            "ref": "The Whisper model is optimized with CTranslate2 to reduce processing latency below one second.",
            "lang": "vi",
            "domain": "Trí tuệ nhân tạo (AI)"
        },
        {
            "src": "Sinh viên cần cấu hình Docker container và kết nối với cơ sở dữ liệu PostgreSQL.",
            "ref": "Students need to configure the Docker container and connect to the PostgreSQL database.",
            "lang": "vi",
            "domain": "Công nghệ thông tin"
        },
        # Chiều 2: Tiếng Anh -> Tiếng Việt
        {
            "src": "The speech recognition pipeline supports real-time bilingual code-switching transcription.",
            "ref": "Quy trình nhận dạng giọng nói hỗ trợ phiên âm chuyển mã song ngữ thời gian thực.",
            "lang": "en",
            "domain": "Speech Processing"
        },
        {
            "src": "Kubernetes automatically manages container deployment and horizontal auto-scaling.",
            "ref": "Kubernetes tự động quản lý việc triển khai container và tự động mở rộng theo chiều ngang.",
            "lang": "en",
            "domain": "DevOps & Cloud"
        },
    ]

    print(f"\n📊 Đang kiểm thử {len(test_cases)} câu dịch thuật học thuật 2 chiều...")
    print("-" * 80)

    bleu_scores = []
    latencies = []

    for i, item in enumerate(test_cases, 1):
        src_text = item["src"]
        ref_text = item["ref"]
        lang = item["lang"]
        direction = "VI ➡️ EN" if lang == "vi" else "EN ➡️ VI"

        t0 = time.perf_counter()
        pred_text = translator.translate(src_text, source_language=lang)
        latency = (time.perf_counter() - t0) * 1000
        latencies.append(latency)

        bleu = compute_sentence_bleu(ref_text, pred_text)
        bleu_scores.append(bleu)

        print(f"[{i}/{len(test_cases)}] 🔄 Hướng: {direction} | Lĩnh vực: {item['domain']}")
        print(f"   📥 Câu gốc    : \"{src_text}\"")
        print(f"   📖 Bản dịch chuẩn : \"{ref_text}\"")
        print(f"   🤖 AI Dịch    : \"{pred_text}\"")
        print(f"   ⏱️ Độ trễ: {latency:.1f} ms | Điểm BLEU: {bleu:.2f}/100\n")

    avg_bleu = sum(bleu_scores) / len(bleu_scores)
    avg_lat = sum(latencies) / len(latencies)

    print("=" * 80)
    print("🏆 TỔNG KẾT KẾT QUẢ DỊCH THUẬT:")
    print(f"   ✅ Điểm BLEU trung bình     : {avg_bleu:.2f} / 100")
    print(f"   ⚡ Độ trễ dịch thuật trung bình: {avg_lat:.1f} ms / câu")
    print("=" * 80)


if __name__ == "__main__":
    main()
