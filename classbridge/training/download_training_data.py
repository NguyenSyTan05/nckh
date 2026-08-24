"""
ClassBridge - Dataset Downloader & Preparer
# pyrefly: ignore-all-errors
Tải và chuẩn bị dữ liệu train THẬT từ các nguồn công khai:

  1. VIVOS (Tiếng Việt ASR) - 15h giọng nói Tiếng Việt chuẩn
  2. Common Voice VI (Mozilla) - Giọng Việt đa vùng miền
  3. LibriSpeech (Tiếng Anh ASR) - 100h giọng Anh học thuật
  4. OPUS-100 EN-VI (Dịch thuật) - 1M cặp câu song ngữ học thuật
  5. PhoMT EN-VI (Dịch thuật VN) - Dataset dịch thuật học thuật VN chuẩn

Cách chạy:
    python download_training_data.py --dataset all
    python download_training_data.py --dataset vivos
    python download_training_data.py --dataset cv_vi
    python download_training_data.py --dataset librispeech
    python download_training_data.py --dataset translation
    python download_training_data.py --dataset local   # Chỉ dùng dữ liệu nội bộ

Yêu cầu:
    pip install datasets huggingface_hub soundfile librosa
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
from typing import Any, Dict, List

# ── Tự động chèn virtualenv ────────────────────────────────────────────────
_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
_VENV = _ROOT / "backend" / "ai-service" / ".venv" / "Lib" / "site-packages"
if _VENV.exists() and str(_VENV) not in sys.path:
    sys.path.insert(0, str(_VENV))
# ──────────────────────────────────────────────────────────────────────────

DATA_DIR = _ROOT / "data"
SAMPLES_DIR = DATA_DIR / "samples"
AUDIO_DIR = DATA_DIR / "audio"
MANIFEST_DIR = DATA_DIR / "manifests"

for _d in [DATA_DIR, SAMPLES_DIR, AUDIO_DIR, MANIFEST_DIR]:
    _d.mkdir(parents=True, exist_ok=True)

HF_CACHE = _ROOT / "backend" / "ai-service" / ".models" / "datasets"
os.environ.setdefault("HF_HOME", str(_ROOT / "backend" / "ai-service" / ".models"))
os.environ.setdefault("HF_DATASETS_CACHE", str(HF_CACHE))


# ──────────────────────────────────────────────────────────────────────────────
# Dữ liệu nội bộ: 120 câu học thuật EN & VI
# ──────────────────────────────────────────────────────────────────────────────

VI_ACADEMIC_SENTENCES: List[str] = [
    # Lớp học / Giảng viên
    "Chào mừng các bạn đến với buổi học hôm nay.",
    "Hôm nay chúng ta sẽ tìm hiểu về trí tuệ nhân tạo.",
    "Bài giảng hôm nay sẽ kéo dài khoảng chín mươi phút.",
    "Các bạn vui lòng tắt điện thoại trước khi vào lớp.",
    "Bài kiểm tra giữa kỳ sẽ diễn ra vào tuần tới.",
    "Vui lòng nộp bài tập trước thứ Sáu tuần này.",
    "Môn học này có ba tín chỉ và một buổi thực hành.",
    "Chương trình học bao gồm mười hai tuần lý thuyết.",
    "Đề cương môn học đã được gửi qua email sinh viên.",
    "Các bạn cần đọc trước tài liệu chương ba và bốn.",
    # Lập trình & CNTT
    "Mạng thần kinh nhân tạo bao gồm nhiều lớp ẩn.",
    "Thuật toán học máy cần dữ liệu huấn luyện chất lượng cao.",
    "Phần mềm này được viết bằng ngôn ngữ lập trình Python.",
    "Cơ sở dữ liệu quan hệ sử dụng ngôn ngữ truy vấn SQL.",
    "Hệ thống phân tán xử lý dữ liệu trên nhiều máy chủ.",
    "Điện toán đám mây cho phép lưu trữ và xử lý từ xa.",
    "Bảo mật thông tin là yêu cầu quan trọng trong phát triển phần mềm.",
    "Giao diện người dùng cần thân thiện và dễ sử dụng.",
    "Kiểm thử phần mềm giúp phát hiện và sửa lỗi kịp thời.",
    "Kiến trúc microservice giúp hệ thống linh hoạt và dễ mở rộng.",
    # Tính toán & Toán học
    "Đạo hàm của hàm số bằng không tại điểm cực trị.",
    "Ma trận vuông có định thức bằng không là ma trận suy biến.",
    "Xác suất của hai biến cố độc lập bằng tích hai xác suất riêng.",
    "Giải tích số giải quyết các bài toán toán học bằng máy tính.",
    "Lý thuyết đồ thị nghiên cứu các cấu trúc mạng và kết nối.",
    # Câu hỏi / Hội thoại
    "Thưa thầy em có câu hỏi về bài tập tuần này không?",
    "Bạn có thể giải thích lại phần giải thuật tìm kiếm nhị phân không?",
    "Khi nào chúng ta sẽ được nhận kết quả bài kiểm tra giữa kỳ?",
    "Em không hiểu phần về đệ quy trong bài giảng hôm nay.",
    "Thầy có thể cho thêm ví dụ về vòng lặp lồng nhau không?",
    # Đa vùng miền
    "Học kỳ này sinh viên cần đăng ký môn học trước ngày mười lăm.",
    "Phòng máy tính sẽ mở cửa từ bảy giờ sáng đến chín giờ tối.",
    "Luận văn tốt nghiệp cần được nộp trước khi hết học kỳ.",
    "Thư viện trường có đầy đủ tài liệu tham khảo cho sinh viên.",
    "Kết quả thi sẽ được công bố trên hệ thống quản lý sinh viên.",
    # Giọng Nam
    "Dữ liệu lớn đòi hỏi hạ tầng máy chủ mạnh và ổn định.",
    "Mô hình ngôn ngữ lớn được huấn luyện trên hàng tỷ từ.",
    "Xử lý ngôn ngữ tự nhiên giúp máy tính hiểu tiếng người.",
    "Nhận dạng giọng nói đã đạt độ chính xác hơn chín mươi lăm phần trăm.",
    "Trình biên dịch chuyển đổi mã nguồn thành mã máy thực thi.",
    # Số & Ký hiệu
    "Năm hai nghìn hai mươi lăm là năm của trí tuệ nhân tạo.",
    "Tốc độ xử lý đạt một trăm triệu phép tính mỗi giây.",
    "Bộ nhớ đệm lưu trữ bốn gigabyte dữ liệu tạm thời.",
    "Hệ thống phục vụ mười nghìn người dùng đồng thời.",
    "Độ trễ trung bình là năm mươi mili giây trên mỗi yêu cầu.",
]

EN_ACADEMIC_SENTENCES: List[str] = [
    # Classroom
    "Welcome to today's lecture on artificial intelligence.",
    "Please turn off your mobile phones before we begin.",
    "Today we will cover chapters three and four of the textbook.",
    "The midterm exam will take place next Thursday at nine o'clock.",
    "Please submit your assignment by Friday at midnight.",
    "This course carries three academic credits and one lab session.",
    "The course syllabus has been uploaded to the student portal.",
    "Office hours are on Monday and Wednesday from two to four PM.",
    "The final examination is scheduled for the last week of term.",
    "Make sure to review the lecture slides before next class.",
    # Programming & CS
    "A neural network consists of multiple layers of interconnected nodes.",
    "Machine learning algorithms require high-quality training data.",
    "This software is written in the Python programming language.",
    "Relational databases use structured query language for data retrieval.",
    "Distributed systems process workloads across multiple servers.",
    "Cloud computing enables remote storage and processing of data.",
    "Information security is a critical requirement in software development.",
    "The user interface should be intuitive and easy to navigate.",
    "Software testing helps identify and fix bugs before release.",
    "Microservice architecture makes systems more flexible and scalable.",
    # Mathematics
    "The derivative of a function equals zero at its critical points.",
    "A square matrix with zero determinant is called a singular matrix.",
    "The probability of two independent events equals the product of each.",
    "Numerical analysis solves mathematical problems using computation.",
    "Graph theory studies the structure and properties of networks.",
    # Questions & Dialogue
    "Could you please explain the binary search algorithm again?",
    "When will we receive the results of the midterm examination?",
    "I did not fully understand the section on recursive functions.",
    "Could you provide additional examples of nested loops?",
    "Is there a prerequisite for enrolling in this advanced course?",
    # Formal academic
    "Students must register for courses before the fifteenth of this month.",
    "The computer lab is open from seven AM to nine PM daily.",
    "The thesis must be submitted before the end of the semester.",
    "The library provides comprehensive reference materials for students.",
    "Examination results will be posted on the student management system.",
    # Technical
    "Big data infrastructure requires powerful and stable server hardware.",
    "Large language models are trained on billions of words.",
    "Natural language processing enables computers to understand human speech.",
    "Speech recognition has achieved over ninety-five percent accuracy.",
    "A compiler converts source code into executable machine code.",
    # Numbers & Symbols
    "The year two thousand and twenty five is the year of AI.",
    "Processing speed reaches one hundred million operations per second.",
    "The cache stores four gigabytes of temporary data.",
    "The system serves ten thousand concurrent users.",
    "Average latency is fifty milliseconds per request.",
]

EN_VI_TRANSLATION_PAIRS: List[Dict[str, str]] = [
    {"en": "Welcome to today's lecture on artificial intelligence.", "vi": "Chào mừng các bạn đến với bài giảng hôm nay về trí tuệ nhân tạo."},
    {"en": "Please submit your assignment before next Monday.", "vi": "Vui lòng nộp bài tập của bạn trước thứ Hai tuần sau."},
    {"en": "The neural network consists of multiple hidden layers.", "vi": "Mạng thần kinh nhân tạo bao gồm nhiều lớp ẩn."},
    {"en": "This course carries three academic credits.", "vi": "Khóa học này mang ba tín chỉ học thuật."},
    {"en": "Do you have any questions regarding the midterm exam?", "vi": "Các bạn có câu hỏi nào về bài thi giữa kỳ không?"},
    {"en": "The prerequisite for this course is Introduction to Programming.", "vi": "Môn học tiên quyết cho khóa này là Nhập môn Lập trình."},
    {"en": "Deep learning has revolutionized computer vision tasks.", "vi": "Học máy sâu đã tạo ra cuộc cách mạng trong thị giác máy tính."},
    {"en": "Distributed systems enable horizontal scaling of workloads.", "vi": "Hệ thống phân tán cho phép mở rộng theo chiều ngang."},
    {"en": "Please turn to page twenty-five of your textbook.", "vi": "Vui lòng mở trang hai mươi lăm trong sách giáo khoa."},
    {"en": "The final exam will cover all chapters from one to twelve.", "vi": "Bài thi cuối kỳ sẽ bao gồm tất cả các chương từ một đến mười hai."},
    {"en": "Software engineering involves design, implementation and testing.", "vi": "Kỹ thuật phần mềm bao gồm thiết kế, triển khai và kiểm thử."},
    {"en": "Cloud computing reduces infrastructure costs significantly.", "vi": "Điện toán đám mây giảm đáng kể chi phí hạ tầng."},
    {"en": "Natural language processing bridges humans and machines.", "vi": "Xử lý ngôn ngữ tự nhiên là cầu nối giữa con người và máy móc."},
    {"en": "The algorithm runs in linear time complexity.", "vi": "Thuật toán chạy với độ phức tạp thời gian tuyến tính."},
    {"en": "Object-oriented programming promotes code reusability.", "vi": "Lập trình hướng đối tượng thúc đẩy khả năng tái sử dụng mã nguồn."},
    {"en": "Data structures store and organize information efficiently.", "vi": "Cấu trúc dữ liệu lưu trữ và tổ chức thông tin hiệu quả."},
    {"en": "The database query returned five hundred records.", "vi": "Truy vấn cơ sở dữ liệu trả về năm trăm bản ghi."},
    {"en": "Machine learning models require validation and test datasets.", "vi": "Mô hình học máy cần tập dữ liệu kiểm định và kiểm thử."},
    {"en": "Version control systems track changes in source code over time.", "vi": "Hệ thống kiểm soát phiên bản theo dõi các thay đổi trong mã nguồn."},
    {"en": "Agile methodology allows teams to adapt quickly to change.", "vi": "Phương pháp Agile cho phép nhóm thích ứng nhanh với sự thay đổi."},
    {"en": "The server responded with a four-oh-four error code.", "vi": "Máy chủ phản hồi với mã lỗi bốn trăm linh bốn."},
    {"en": "Encryption protects sensitive data from unauthorized access.", "vi": "Mã hóa bảo vệ dữ liệu nhạy cảm khỏi truy cập trái phép."},
    {"en": "The API endpoint accepts JSON formatted requests.", "vi": "Điểm cuối API chấp nhận các yêu cầu định dạng JSON."},
    {"en": "Containerization simplifies application deployment across environments.", "vi": "Container hóa đơn giản hóa việc triển khai ứng dụng trên nhiều môi trường."},
    {"en": "Recursion is a technique where a function calls itself.", "vi": "Đệ quy là kỹ thuật mà một hàm tự gọi lại chính nó."},
    {"en": "The system processes one million transactions per day.", "vi": "Hệ thống xử lý một triệu giao dịch mỗi ngày."},
    {"en": "Binary search runs in logarithmic time on sorted arrays.", "vi": "Tìm kiếm nhị phân chạy trong thời gian logarit trên mảng đã sắp xếp."},
    {"en": "Regression testing ensures that new changes do not break existing functionality.", "vi": "Kiểm thử hồi quy đảm bảo các thay đổi mới không làm hỏng chức năng hiện có."},
    {"en": "Load balancing distributes traffic evenly across multiple servers.", "vi": "Cân bằng tải phân phối lưu lượng đều trên nhiều máy chủ."},
    {"en": "The microprocessor executes billions of instructions per second.", "vi": "Bộ vi xử lý thực thi hàng tỷ lệnh mỗi giây."},
]


# ──────────────────────────────────────────────────────────────────────────────
# 1. Tải VIVOS (Tiếng Việt ASR)
# ──────────────────────────────────────────────────────────────────────────────

def download_vivos(max_samples: int = 500) -> str:
    """Tải dataset VIVOS (Tiếng Việt) từ HuggingFace."""
    print("\n" + "=" * 60)
    print("  📥 [1/4] Tải VIVOS - Tiếng Việt ASR Dataset")
    print("=" * 60)
    try:
        from datasets import load_dataset, Audio

        print("  🔄 Đang tải VIVOS (có thể mất vài phút lần đầu)...")
        ds = load_dataset("vivos", split=f"train[:{max_samples}]", trust_remote_code=True)
        ds = ds.cast_column("audio", Audio(sampling_rate=16_000))

        manifest_path = MANIFEST_DIR / "vivos_train.jsonl"
        audio_out_dir = AUDIO_DIR / "vivos"
        audio_out_dir.mkdir(parents=True, exist_ok=True)

        rows_written = 0
        with open(manifest_path, "w", encoding="utf-8") as f:
            for i, row in enumerate(ds):
                try:
                    import soundfile as sf
                    import numpy as np
                    audio_path = audio_out_dir / f"vivos_{i:05d}.wav"
                    arr = np.array(row["audio"]["array"], dtype=np.float32)
                    sf.write(str(audio_path), arr, 16_000)
                    record = {
                        "audio": str(audio_path),
                        "text": row["sentence"].strip(),
                        "language": "vi",
                        "speaker_id": str(row.get("speaker_id", f"vi_spk_{i:03d}")),
                        "accent": "vi_north",
                        "dataset": "vivos",
                    }
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    rows_written += 1
                    if (i + 1) % 100 == 0:
                        print(f"    ✅ Đã xử lý {i + 1}/{max_samples} mẫu VIVOS...")
                except Exception as e:
                    print(f"    ⚠️ Bỏ qua mẫu {i}: {e}")

        print(f"  ✅ VIVOS: {rows_written} mẫu → {manifest_path}")
        return str(manifest_path)

    except Exception as e:
        print(f"  ❌ Lỗi tải VIVOS: {e}")
        print("  💡 Thử: pip install datasets soundfile")
        return ""


# ──────────────────────────────────────────────────────────────────────────────
# 2. Tải Common Voice Tiếng Việt
# ──────────────────────────────────────────────────────────────────────────────

def download_common_voice_vi(max_samples: int = 300) -> str:
    """Tải dataset Common Voice Tiếng Việt từ Mozilla (qua HuggingFace)."""
    print("\n" + "=" * 60)
    print("  📥 [2/4] Tải Common Voice VI - Tiếng Việt đa vùng miền")
    print("=" * 60)
    try:
        from datasets import load_dataset, Audio

        print("  🔄 Đang tải Mozilla Common Voice VI...")
        ds = load_dataset(
            "mozilla-foundation/common_voice_13_0",
            "vi",
            split=f"train[:{max_samples}]",
            trust_remote_code=True,
        )
        ds = ds.cast_column("audio", Audio(sampling_rate=16_000))

        manifest_path = MANIFEST_DIR / "common_voice_vi_train.jsonl"
        audio_out_dir = AUDIO_DIR / "cv_vi"
        audio_out_dir.mkdir(parents=True, exist_ok=True)

        rows_written = 0
        with open(manifest_path, "w", encoding="utf-8") as f:
            for i, row in enumerate(ds):
                try:
                    import soundfile as sf
                    import numpy as np
                    audio_path = audio_out_dir / f"cv_vi_{i:05d}.wav"
                    arr = np.array(row["audio"]["array"], dtype=np.float32)
                    sf.write(str(audio_path), arr, 16_000)
                    record = {
                        "audio": str(audio_path),
                        "text": row["sentence"].strip(),
                        "language": "vi",
                        "speaker_id": row.get("client_id", f"cv_vi_{i:03d}")[:16],
                        "accent": "vi_mixed",
                        "dataset": "common_voice_vi",
                    }
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    rows_written += 1
                    if (i + 1) % 100 == 0:
                        print(f"    ✅ Đã xử lý {i + 1}/{max_samples} mẫu CV_VI...")
                except Exception as e:
                    print(f"    ⚠️ Bỏ qua mẫu {i}: {e}")

        print(f"  ✅ Common Voice VI: {rows_written} mẫu → {manifest_path}")
        return str(manifest_path)

    except Exception as e:
        print(f"  ❌ Lỗi tải Common Voice VI: {e}")
        return ""


# ──────────────────────────────────────────────────────────────────────────────
# 3. Tải Common Voice Tiếng Anh
# ──────────────────────────────────────────────────────────────────────────────

def download_common_voice_en(max_samples: int = 300) -> str:
    """Tải dataset Common Voice Tiếng Anh từ Mozilla (qua HuggingFace)."""
    print("\n" + "=" * 60)
    print("  📥 [3/4] Tải Common Voice EN - Tiếng Anh đa giọng")
    print("=" * 60)
    try:
        from datasets import load_dataset, Audio

        print("  🔄 Đang tải Mozilla Common Voice EN...")
        ds = load_dataset(
            "mozilla-foundation/common_voice_13_0",
            "en",
            split=f"train[:{max_samples}]",
            trust_remote_code=True,
        )
        ds = ds.cast_column("audio", Audio(sampling_rate=16_000))

        manifest_path = MANIFEST_DIR / "common_voice_en_train.jsonl"
        audio_out_dir = AUDIO_DIR / "cv_en"
        audio_out_dir.mkdir(parents=True, exist_ok=True)

        rows_written = 0
        with open(manifest_path, "w", encoding="utf-8") as f:
            for i, row in enumerate(ds):
                try:
                    import soundfile as sf
                    import numpy as np
                    audio_path = audio_out_dir / f"cv_en_{i:05d}.wav"
                    arr = np.array(row["audio"]["array"], dtype=np.float32)
                    sf.write(str(audio_path), arr, 16_000)
                    record = {
                        "audio": str(audio_path),
                        "text": row["sentence"].strip(),
                        "language": "en",
                        "speaker_id": row.get("client_id", f"cv_en_{i:03d}")[:16],
                        "accent": "en_us",
                        "dataset": "common_voice_en",
                    }
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    rows_written += 1
                    if (i + 1) % 100 == 0:
                        print(f"    ✅ Đã xử lý {i + 1}/{max_samples} mẫu CV_EN...")
                except Exception as e:
                    print(f"    ⚠️ Bỏ qua mẫu {i}: {e}")

        print(f"  ✅ Common Voice EN: {rows_written} mẫu → {manifest_path}")
        return str(manifest_path)

    except Exception as e:
        print(f"  ❌ Lỗi tải Common Voice EN: {e}")
        return ""


# ──────────────────────────────────────────────────────────────────────────────
# 4. Tạo Dataset Dịch Thuật Song Ngữ EN↔VI
# ──────────────────────────────────────────────────────────────────────────────

def prepare_translation_dataset() -> str:
    """Tạo dataset dịch thuật song ngữ EN↔VI từ dữ liệu nội bộ + OPUS."""
    print("\n" + "=" * 60)
    print("  📝 [4/4] Chuẩn bị Dataset Dịch Thuật Song Ngữ EN↔VI")
    print("=" * 60)

    pairs: List[Dict[str, str]] = list(EN_VI_TRANSLATION_PAIRS)

    # Thử tải thêm từ OPUS-100
    try:
        from datasets import load_dataset
        print("  🔄 Đang tải thêm cặp câu từ OPUS-100 EN-VI...")
        opus_ds = load_dataset("opus100", "en-vi", split="train[:500]", trust_remote_code=True)
        for row in opus_ds:
            trans = row.get("translation", {})
            en_text = str(trans.get("en", "")).strip()
            vi_text = str(trans.get("vi", "")).strip()
            if en_text and vi_text and len(en_text) > 10:
                pairs.append({"en": en_text, "vi": vi_text})
        print(f"  ✅ Đã tải thêm {len(opus_ds)} cặp từ OPUS-100")
    except Exception as e:
        print(f"  ⚠️ Không tải được OPUS-100: {e} — Dùng dữ liệu nội bộ")

    # Lưu JSONL
    manifest_path = MANIFEST_DIR / "translation_en_vi.jsonl"
    with open(manifest_path, "w", encoding="utf-8") as f:
        for pair in pairs:
            f.write(json.dumps({"en": pair["en"], "vi": pair["vi"]}, ensure_ascii=False) + "\n")

    # Lưu CSV (dễ đọc)
    csv_path = MANIFEST_DIR / "translation_en_vi.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["en", "vi"])
        for pair in pairs:
            writer.writerow([pair["en"], pair["vi"]])

    print(f"  ✅ Dataset dịch thuật: {len(pairs)} cặp câu → {manifest_path}")
    return str(manifest_path)


# ──────────────────────────────────────────────────────────────────────────────
# 5. Tạo Dữ Liệu Văn Bản Nội Bộ (không cần audio)
# ──────────────────────────────────────────────────────────────────────────────

def prepare_local_text_manifest() -> str:
    """Tạo manifest văn bản nội bộ cho train correction memory."""
    print("\n" + "=" * 60)
    print("  📝 Chuẩn bị Dữ liệu Văn bản Nội bộ (EN & VI)")
    print("=" * 60)

    # ASR text manifest (không có audio thật — dùng cho correction memory)
    manifest_path = MANIFEST_DIR / "local_text_manifest.jsonl"
    count = 0
    with open(manifest_path, "w", encoding="utf-8") as f:
        for i, sentence in enumerate(VI_ACADEMIC_SENTENCES):
            record = {
                "text": sentence,
                "language": "vi",
                "speaker_id": f"vi_local_{i:03d}",
                "accent": "vi_north" if i < 20 else ("vi_central" if i < 35 else "vi_south"),
                "dataset": "classbridge_local",
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1

        for i, sentence in enumerate(EN_ACADEMIC_SENTENCES):
            record = {
                "text": sentence,
                "language": "en",
                "speaker_id": f"en_local_{i:03d}",
                "accent": "en_us" if i % 2 == 0 else "en_gb",
                "dataset": "classbridge_local",
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1

    print(f"  ✅ Văn bản nội bộ: {count} câu → {manifest_path}")

    # Cập nhật bilingual_sample_manifest.jsonl gốc
    bilingual_path = DATA_DIR / "bilingual_sample_manifest.jsonl"
    with open(bilingual_path, "w", encoding="utf-8") as f:
        for i, s in enumerate(VI_ACADEMIC_SENTENCES[:20]):
            record = {
                "audio": f"data/audio/local/vi_{i:03d}.wav",
                "text": s,
                "language": "vi",
                "speaker_id": f"vi_local_{i:03d}",
                "accent": "vi_north",
                "dataset": "classbridge_local",
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        for i, s in enumerate(EN_ACADEMIC_SENTENCES[:20]):
            record = {
                "audio": f"data/audio/local/en_{i:03d}.wav",
                "text": s,
                "language": "en",
                "speaker_id": f"en_local_{i:03d}",
                "accent": "en_us",
                "dataset": "classbridge_local",
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"  ✅ Cập nhật bilingual_sample_manifest.jsonl: 40 mẫu")

    return str(manifest_path)


# ──────────────────────────────────────────────────────────────────────────────
# 6. Tổng Hợp Manifest
# ──────────────────────────────────────────────────────────────────────────────

def merge_asr_manifests(manifest_paths: List[str]) -> str:
    """Gộp nhiều manifest JSONL thành một file train duy nhất."""
    merged_path = MANIFEST_DIR / "train_merged.jsonl"
    total = 0
    with open(merged_path, "w", encoding="utf-8") as out_f:
        for path in manifest_paths:
            if not path or not Path(path).exists():
                continue
            with open(path, "r", encoding="utf-8") as in_f:
                for line in in_f:
                    line = line.strip()
                    if line:
                        out_f.write(line + "\n")
                        total += 1
    print(f"\n  📦 Manifest tổng hợp: {total} mẫu → {merged_path}")
    return str(merged_path)


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="ClassBridge Dataset Downloader & Preparer"
    )
    parser.add_argument(
        "--dataset", "-d",
        choices=["all", "vivos", "cv_vi", "cv_en", "translation", "local"],
        default="local",
        help=(
            "Dataset cần tải:\n"
            "  all         - Tải tất cả (VIVOS + CV_VI + CV_EN + Translation)\n"
            "  vivos       - Chỉ tải VIVOS Tiếng Việt\n"
            "  cv_vi       - Common Voice Tiếng Việt\n"
            "  cv_en       - Common Voice Tiếng Anh\n"
            "  translation - Dataset dịch thuật EN↔VI\n"
            "  local       - Chỉ dùng dữ liệu nội bộ (không cần Internet)"
        ),
    )
    parser.add_argument(
        "--max-samples", "-n",
        type=int,
        default=300,
        help="Số mẫu tối đa mỗi dataset (mặc định: 300)",
    )
    args = parser.parse_args()

    print("\n" + "=" * 65)
    print("  🗂️  ClassBridge - Dataset Downloader & Preparer")
    print("=" * 65)
    print(f"  Chế độ    : {args.dataset}")
    print(f"  Số mẫu    : {args.max_samples} mỗi dataset")
    print(f"  Thư mục   : {DATA_DIR}")
    print("=" * 65)

    manifests: List[str] = []

    # Luôn tạo dữ liệu nội bộ trước (không cần Internet)
    local_path = prepare_local_text_manifest()
    manifests.append(local_path)

    if args.dataset in ("all", "translation"):
        trans_path = prepare_translation_dataset()

    if args.dataset in ("all", "vivos"):
        vivos_path = download_vivos(args.max_samples)
        if vivos_path:
            manifests.append(vivos_path)

    if args.dataset in ("all", "cv_vi"):
        cv_vi_path = download_common_voice_vi(args.max_samples)
        if cv_vi_path:
            manifests.append(cv_vi_path)

    if args.dataset in ("all", "cv_en"):
        cv_en_path = download_common_voice_en(args.max_samples)
        if cv_en_path:
            manifests.append(cv_en_path)

    # Gộp manifest nếu có nhiều nguồn
    if len(manifests) > 1:
        merged = merge_asr_manifests(manifests)
    else:
        merged = manifests[0] if manifests else ""

    print("\n" + "=" * 65)
    print("  🎉 HOÀN TẤT CHUẨN BỊ DỮ LIỆU!")
    print("=" * 65)
    print(f"  📁 Thư mục dữ liệu  : {DATA_DIR}")
    print(f"  📁 Manifests        : {MANIFEST_DIR}")
    print(f"  📁 Audio files      : {AUDIO_DIR}")
    print(f"\n  📄 Manifest train sẵn sàng: {merged}")
    print("\n  👉 Bước tiếp theo:")
    print("     npm run train  → Chọn [6] để train AI với dữ liệu trên")
    print("=" * 65)


if __name__ == "__main__":
    main()
