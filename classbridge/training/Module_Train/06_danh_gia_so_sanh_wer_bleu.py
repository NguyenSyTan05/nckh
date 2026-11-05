"""
ClassBridge Unified Engine
Script: 06_kiem_tra_model_hien_tai_1_luong.py (trước đây là 06_danh_gia_so_sanh_wer_bleu.py)
Chức năng: Chạy kiểm tra Model thống nhất hiện tại theo 1 luồng duy nhất (Single Unified Stream):
- 1 Mô hình Whisper ASR duy nhất trên GPU (Float16) cho cả Tiếng Việt & Tiếng Anh
- 1 Mô hình Meta NLLB-200 NMT trên CPU (Đa luồng) dịch thuật song ngữ 2 chiều
- Không so sánh module rời rạc, chạy trực tiếp luồng ASR -> Dịch thuật
"""

import io
import os
import sys
import time
from pathlib import Path

# Đảm bảo Windows console in đúng UTF-8 không lỗi font tiếng Việt
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
    except Exception:
        pass

# Nạp đường dẫn Virtualenv & AI Modules
project_root = Path(__file__).resolve().parents[2]
ai_service_dir = project_root / "backend" / "ai-service"
venv_site = ai_service_dir / ".venv" / "Lib" / "site-packages"
if venv_site.exists() and str(venv_site) not in sys.path:
    sys.path.insert(0, str(venv_site))
if str(ai_service_dir) not in sys.path:
    sys.path.insert(0, str(ai_service_dir))
trans_dir = ai_service_dir / "04_TRANSLATION_MODULE"
if str(trans_dir) not in sys.path:
    sys.path.insert(0, str(trans_dir))


def main():
    print("=" * 75)
    print("🚀 [CHẠY 1 LUỒNG] KIỂM TRA MODEL HIỆN TẠI (UNIFIED ASR + META NLLB-200)")
    print("=" * 75)

    from unified_speech_recognizer import UnifiedSpeechRecognizer
    from nmt_translator import NLLBTranslator
    from faster_whisper.audio import decode_audio

    # 1. Khởi tạo 1 luồng duy nhất
    print("\n[1/3] Đang nạp Model hiện tại của hệ thống...")
    asr = UnifiedSpeechRecognizer()
    translator = NLLBTranslator(device="cpu")

    # 2. Xác định file âm thanh kiểm tra (nhận từ tham số dòng lệnh hoặc file mẫu mặc định)
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        test_audio_path = sys.argv[1]
    else:
        test_audio_path = str(ai_service_dir / "test_vi_speech.mp3")

    if not os.path.exists(test_audio_path):
        print(f"❌ Không tìm thấy file âm thanh mẫu tại: {test_audio_path}")
        return

    print(f"\n[2/3] Đang nạp âm thanh: {Path(test_audio_path).name}")
    audio = decode_audio(test_audio_path, sampling_rate=16000)
    duration_sec = len(audio) / 16000
    print(f"  ➜ Thời lượng âm thanh: {duration_sec:.2f} giây")

    # 3. Chạy 1 luồng: Nhận diện giọng nói (ASR)
    print("\n[3/3] Đang xử lý 1 luồng (ASR ➜ Dịch thuật)...")
    t0 = time.time()
    res_asr = asr.transcribe(audio, language="auto")
    t_asr = (time.time() - t0) * 1000

    transcript = res_asr.get("text", "").strip()
    detected_lang = res_asr.get("language", "vi")

    print("\n" + "-" * 75)
    print(f"🎤 LỜI GỐC NHẬN DIỆN ({t_asr:.0f}ms) [Ngôn ngữ: {detected_lang.upper()}]:")
    print(f"   \"{transcript}\"")

    # 4. Chạy 1 luồng: Dịch thuật đối ứng
    target_lang = "en" if detected_lang == "vi" else "vi"
    t1 = time.time()
    translated = translator.translate(transcript, source_language=detected_lang, target_language=target_lang)
    t_trans = (time.time() - t1) * 1000

    print(f"\n🌐 BẢN DỊCH SONG NGỮ ({t_trans:.0f}ms) [Sang: {target_lang.upper()}]:")
    print(f"   \"{translated}\"")
    print("-" * 75)
    print(f"⚡ Tổng thời gian xử lý toàn luồng: {(t_asr + t_trans):.0f}ms")
    print("=" * 75)
    print("✅ HOÀN TẤT CHẠY 1 LUỒNG MODEL HIỆN TẠI!")
    print("=" * 75)


if __name__ == "__main__":
    main()
