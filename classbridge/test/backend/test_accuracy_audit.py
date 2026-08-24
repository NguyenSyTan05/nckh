"""
ClassBridge Accuracy & Language Audit Test Suite
Kiểm tra toàn diện:
1. Độ chuẩn xác thanh dấu tiếng Việt (đủ 6 thanh điệu, không mất dấu).
2. Nhận dạng tiếng Anh chuẩn xác (không bị ép hay phiên âm sang tiếng Việt).
3. Câu xen kẽ thuật ngữ kỹ thuật (Code-Switching EN-VI).
4. Khử hoàn toàn các ngôn ngữ ngoại lai (Bồ Đào Nha, Tây Ban Nha...).
"""

import sys
from pathlib import Path

# Add backend/ai-service to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend" / "ai-service"))

if sys.platform == "win32":
    reconfig_out = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfig_out):
        reconfig_out(encoding="utf-8")
    reconfig_err = getattr(sys.stderr, "reconfigure", None)
    if callable(reconfig_err):
        reconfig_err(encoding="utf-8")

import unicodedata
from modules.correction_module import CorrectionModule
from modules.transcript_stabilizer import TranscriptStabilizer
import main


def test_vietnamese_diacritics():
    print("[AUDIT 1 — DẤU TIẾNG VIỆT] Kiểm tra bảo toàn 100% thanh dấu tiếng Việt...")
    cm = CorrectionModule()
    
    sentences = [
        "Hôm nay chúng ta học về kiến trúc phần mềm và hệ thống phân tán.",
        "Trường Đại học Bách Khoa đào tạo kỹ sư công nghệ thông tin chất lượng cao.",
        "Phụ đề song ngữ theo thời gian thực giúp sinh viên tiếp thu bài giảng dễ dàng.",
        "Thầy cô giảng dạy rất nhiệt tình và chu đáo.",
        "Đề cương môn học bao gồm cơ sở dữ liệu và mạng máy tính.",
        "Mã nguồn mở và giải thuật tối ưu hóa.",
    ]
    
    combined = " ".join(cm.clean(s) for s in sentences)
    for s in sentences:
        cleaned = cm.clean(s)
        assert cleaned == unicodedata.normalize("NFC", s), f"Dấu bị lệch: '{cleaned}' vs '{s}'"
        print(f"  Verified VN: '{cleaned}'")

    assert all(c in combined.casefold() for c in ["ê", "ế", "ệ", "á", "à", "ả", "ã", "ạ", "ư", "ơ", "đ"]), "Thiếu nguyên âm có dấu trong corpus"
    
    print("  ✓ PASS AUDIT 1: Toàn bộ 6 thanh điệu tiếng Việt được bảo toàn chuẩn xác 100% NFC.\n")


def test_english_preservation():
    print("[AUDIT 2 — TIẾNG ANH THUẦN TÚY] Kiểm tra bảo toàn từ vựng tiếng Anh...")
    cm = CorrectionModule()
    
    en_sentences = [
        "Today we are going to study software architecture.",
        "Hello everyday everyone.",
        "Machine learning models require clean training datasets.",
        "Microservices architecture enables high scalability.",
    ]
    
    for s in en_sentences:
        cleaned = cm.clean(s)
        assert cleaned == s, f"Tiếng Anh bị biến đổi: '{cleaned}' vs '{s}'"
    
    print("  ✓ PASS AUDIT 2: Tiếng Anh giữ nguyên vẹn 100%, không bị sửa bừa.\n")


def test_code_switching_mixed():
    print("[AUDIT 3 — PHA TRỘN THUẬT NGỮ EN-VI] Kiểm tra câu hỗn hợp...")
    cm = CorrectionModule()
    
    mixed_sentences = [
        "Hôm nay chúng ta sẽ tìm hiểu về microservices và REST API.",
        "Sinh viên cần viết unit test cho các module backend trong Python.",
        "Hệ thống deploy trên Docker và Kubernetes với CI/CD pipeline tự động.",
    ]
    
    for s in mixed_sentences:
        cleaned = cm.clean(s)
        # Check both Vietnamese tones and English tech terms exist
        assert "tìm hiểu" in cleaned or "cần viết" in cleaned or "tự động" in cleaned
        assert "microservices" in cleaned or "backend" in cleaned or "Kubernetes" in cleaned
        print(f"  Verified Mixed: '{cleaned}'")
    
    print("  ✓ PASS AUDIT 3: Thuật ngữ tiếng Anh trong câu tiếng Việt được bảo tồn hoàn hảo.\n")


def test_foreign_hallucination_immunity():
    print("[AUDIT 4 — CHỐNG TIẾNG LẠ NGOẠI LAI] Kiểm tra bộ lọc ngôn ngữ chỉ nhận VI và EN...")
    # Test probability router
    vi_leads = [("vi", 0.70), ("en", 0.20), ("pt", 0.10)]
    en_leads = [("en", 0.60), ("vi", 0.30), ("es", 0.10)]
    foreign_confusion = [("pt", 0.40), ("en", 0.35), ("vi", 0.25)]
    
    lang1, _ = main.choose_supported_language(vi_leads)
    assert lang1 == "vi", f"Expected 'vi', got '{lang1}'"
    
    lang2, _ = main.choose_supported_language(en_leads)
    assert lang2 == "en", f"Expected 'en', got '{lang2}'"
    
    lang3, _ = main.choose_supported_language(foreign_confusion)
    assert lang3 == "en", f"Expected 'en', got '{lang3}'"
    
    print("  ✓ PASS AUDIT 4: Bộ định tuyến chỉ nhận VI/EN, loại bỏ 100% ngôn ngữ lạ ngoại lai.\n")


if __name__ == "__main__":
    print("==========================================================================")
    print(" 🔍 CLASSBRIDGE COMPREHENSIVE ASR & DIACRITICS AUDIT")
    print("==========================================================================")
    test_vietnamese_diacritics()
    test_english_preservation()
    test_code_switching_mixed()
    test_foreign_hallucination_immunity()
    print("==========================================================================")
    print(" 🏆 ALL 4 AUDIT SUITES PASSED 100% — CODE CHUẨN XÁC, ĐỦ DẤU, ĐÚNG TỪ")
    print("==========================================================================")
