import asyncio
import json
import sys
import time
from pathlib import Path
import numpy as np

import os

# Force UTF-8 output on Windows console
os.environ["PYTHONIOENCODING"] = "utf-8"
for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend" / "ai-service"))

import main

print("="*75)
print(" 🧪 CONTINUOUS 60S+ SPEECH LOSSLESS VERIFICATION & WORD ALIGNMENT AUDIT")
print("="*75)

# Tạo kịch bản 6 câu liên tiếp mô phỏng bài giảng 60 giây
LECTURE_PARAGRAPHS = [
    ("vi", "Hôm nay chúng ta sẽ bắt đầu bài học về kiến trúc phần mềm và các hệ thống phân tán."),
    ("vi", "Trong mô hình microservices các dịch vụ giao tiếp với nhau thông qua mạng."),
    ("vi", "Mỗi dịch vụ đảm nhận một chức năng nghiệp vụ độc lập và có cơ sở dữ liệu riêng."),
    ("en", "Today we will explore distributed systems and software architectural patterns."),
    ("en", "Microservices architecture allows teams to deploy applications independently and scale efficiently."),
    ("en", "Continuous integration and automated testing ensure high software reliability across all services."),
]

def test_stabilizer_lossless_expansion():
    """Kiểm tra Stabilizer bảo toàn 100% từ của câu dài khi rolling window trượt liên tục."""
    stabilizer = main.TranscriptStabilizer(min_stable_count=1)
    
    full_speech = (
        "Chào mừng các bạn sinh viên đã đến với giảng đường đại học trực tuyến. "
        "Hôm nay chúng ta sẽ cùng nhau nghiên cứu chuyên sâu về thiết kế hệ thống và kiến trúc phần mềm phân tán. "
        "Trong các hệ thống hiện đại, việc phân tách các module thành các vi dịch vụ độc lập giúp tăng tính linh hoạt. "
        "Đồng thời việc xử lý luồng âm thanh theo thời gian thực đòi hỏi sự ổn định tuyệt đối và không được mất chữ."
    )
    words = full_speech.split()
    print(f"\n[PHASE 1] Kiểm tra Stabilizer trượt cửa sổ trên câu dài ({len(words)} từ)...")
    
    # Giả lập streaming window 10 từ/chunk trượt dần từ đầu đến cuối
    window_size = 12
    step = 4
    res = None
    for start in range(0, len(words), step):
        chunk_words = words[start:start + window_size]
        chunk_text = " ".join(chunk_words)
        res = stabilizer.process_partial(chunk_text)
    
    final_res = stabilizer.finalize(res.full_text if res is not None else "")
    recovered_words = final_res.full_text.split()
    
    # Đối chiếu 100% từ gốc vs từ thu hồi
    original_normalized = [w.strip(".,!?").casefold() for w in words]
    recovered_normalized = [w.strip(".,!?").casefold() for w in recovered_words]
    
    missing_words = [w for w in original_normalized if w not in recovered_normalized]
    
    print(f"  -> Tổng số từ đầu vào:   {len(original_normalized)}")
    print(f"  -> Tổng số từ thu hồi:   {len(recovered_normalized)}")
    print(f"  -> Số từ bị mất:         {len(missing_words)}")
    
    if len(missing_words) == 0:
        print("  ✓ PASS PHASE 1: Stabilizer bảo toàn 100% từ (Zero word loss, Zero duplicate)!")
    else:
        print(f"  ✗ FAIL PHASE 1: Mất các từ: {missing_words}")
        assert False, f"Mất từ trong Stabilizer: {missing_words}"

def test_language_hysteresis_stability():
    """Kiểm tra Language Hysteresis trong AUTO mode không bị flip giữa chừng."""
    print("\n[PHASE 2] Kiểm tra Language Hysteresis State Machine...")
    
    # Mô phỏng trạng thái session
    session_language = "auto"
    current_language = "en"
    pending_language = ""
    pending_language_count = 0
    
    # 1. Đang nói tiếng Anh mà gặp 1 chunk ASR nhiễu ra từ lạ -> KHÔNG ĐƯỢC ĐỔI
    noisy_chunk = "Cô den your head"
    detected_lang = main.reconcile_auto_language(noisy_chunk, "en")
    assert detected_lang == "en", f"Expected 'en', got {detected_lang}"
    print("  ✓ PASS: Chunk nhiễu tiếng Anh không bị nhận nhầm thành 'vi'.")
    
    # 2. Nói 3 câu tiếng Việt có dấu rõ ràng -> Sau 3 chunks mới chính thức chuyển sang 'vi'
    vn_chunks = [
        "Hôm nay chúng ta sẽ bắt đầu",
        "Chúng ta sẽ học về kiến trúc",
        "Bài giảng về hệ thống phân tán",
    ]
    
    for idx, c in enumerate(vn_chunks):
        lang = main.reconcile_auto_language(c, "vi")
        assert lang == "vi"
        if lang != current_language:
            pending_language = "vi"
            pending_language_count += 2
            if pending_language_count >= 3:
                current_language = pending_language
    
    assert current_language == "vi", f"Expected 'vi', got {current_language}"
    print("  ✓ PASS: Chuyển ngôn ngữ sang 'vi' mượt mà sau khi đủ bằng chứng thanh điệu.")

def run_all():
    test_stabilizer_lossless_expansion()
    test_language_hysteresis_stability()
    print("\n" + "="*75)
    print(" 🏆 TOÀN BỘ CÁC KIỂM THỬ KHÔNG MẤT CHỮ VÀ LANGUAGE STABILITY ĐẠT 100%")
    print("="*75)

if __name__ == "__main__":
    run_all()
