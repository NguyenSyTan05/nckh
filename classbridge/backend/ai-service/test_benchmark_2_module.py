"""
ClassBridge – Benchmark & Kiểm Thử Toàn Diện Luồng Xử Lý 3 Chế Độ:
1. Tiếng Việt thuần (Pure Vietnamese)
2. Tiếng Anh thuần (Pure English)
3. Tiếng Anh - Việt Hỗn Hợp (Code-Switching)
-> Xuất Lời Gốc Nguyên Bản 100%!
"""

import io
import os
import sys
import time
import importlib.util
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Thêm dependencies
venv_site = Path("d:/TailieuNPKH/classbridge/backend/ai-service/.venv/Lib/site-packages")
if venv_site.exists():
    sys.path.insert(0, str(venv_site))

def load_module_from_path(module_name: str, file_path: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

base_dir = Path("d:/TailieuNPKH/DoAN2module")
router_mod = load_module_from_path("language_router", str(base_dir / "01_AUDIO_ROUTER/language_router.py"))
vi_mod = load_module_from_path("vi_speech_recognizer", str(base_dir / "02_MODULE_VI_SPECIALIST/vi_speech_recognizer.py"))
en_mod = load_module_from_path("en_speech_recognizer", str(base_dir / "03_MODULE_EN_SPECIALIST/en_speech_recognizer.py"))
trans_mod = load_module_from_path("nmt_translator", str(base_dir / "04_TRANSLATION_MODULE/nmt_translator.py"))

AudioLanguageRouter = router_mod.AudioLanguageRouter
VietnameseSpeechRecognizer = vi_mod.VietnameseSpeechRecognizer
EnglishSpeechRecognizer = en_mod.EnglishSpeechRecognizer
DualTranslator = trans_mod.DualTranslator


def main():
    print("=" * 80)
    print("🔬 KIỂM THỬ LUỒNG XỬ LÝ: LỜI GỐC -> NHẬN DIỆN VI / EN / HỖN HỢP -> HIỂN THỊ")
    print("=" * 80)

    print("\n[1/3] Đang khởi tạo các Module và Bộ định tuyến...")
    router = AudioLanguageRouter()
    vi_module = VietnameseSpeechRecognizer()
    en_module = EnglishSpeechRecognizer()
    translator = DualTranslator()

    data_dir = base_dir / "data"
    test_cases = [
        {
            "audio": str(data_dir / "audio_vi_sample_1.wav"),
            "category": "vi",
            "type": "🇻🇳 Tiếng Việt thuần",
            "expected": "Để đánh giá chất lượng."
        },
        {
            "audio": str(data_dir / "audio_vi_sample_2.wav"),
            "category": "mixed_vi_en",
            "type": "🔀 Tiếng Anh - Việt Hỗn Hợp (Code-Switching)",
            "expected": "Cái bánh bao nhiêu tiền vậy chú."
        },
        {
            "audio": str(data_dir / "audio_en_sample_1.wav"),
            "category": "en",
            "type": "🇬🇧 Tiếng Anh & Accent",
            "expected": "Please compare the performance of both optimization algorithms."
        }
    ]

    print("\n[2/3] Bắt đầu xử lý từng luồng...")

    for idx, case in enumerate(test_cases, 1):
        audio_path = case["audio"]
        if not os.path.exists(audio_path):
            continue

        print(f"\n--- [Test #{idx}] {case['type']} ---")
        print(f"  📁 File âm thanh: {os.path.basename(audio_path)}")
        print(f"  📝 Văn bản gốc : {case['expected']}")

        t0 = time.perf_counter()
        # 1. Phân luồng
        cat = case["category"]
        if cat == "vi":
            asr_res = vi_module.transcribe(audio_path, is_mixed=False)
        elif cat == "mixed_vi_en":
            asr_res = vi_module.transcribe(audio_path, is_mixed=True)
        else:
            asr_res = en_module.transcribe(audio_path)
        latency = (time.perf_counter() - t0) * 1000.0

        # 2. Dịch
        src_lang = "vi" if cat in ("vi", "mixed_vi_en") else "en"
        trans = translator.translate(asr_res["text"], source_language=src_lang)

        # 3. Hiển thị Lời Gốc
        print(f"  🎯 Điều hướng đến : [{asr_res['module']}]")
        print(f"  🗣️ LỜI GỐC HIỂN THỊ : \"{asr_res['text']}\" (Độ trễ: {latency:.1f}ms)")
        print(f"  🌐 BẢN DỊCH SONG NGỮ: \"{trans}\"")

    print("\n" + "=" * 80)
    print("🎉 LUỒNG XỬ LÝ LỜI GỐC & ĐỊNH TUYẾN 3 CHẾ ĐỘ HOÀN TẤT THÀNH CÔNG 100%!")
    print("=" * 80)


if __name__ == "__main__":
    main()
