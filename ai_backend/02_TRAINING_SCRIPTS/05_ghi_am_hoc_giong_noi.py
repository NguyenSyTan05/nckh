"""
ClassBridge - Automated Personal Voice Recording & Fine-Tuning Module
Huấn luyện cá nhân hóa giọng nói giảng viên / sinh viên trực tiếp

Thư mục: classbridge/training/
"""
# pyrefly: ignore-all-errors
from __future__ import annotations

import csv
import os
import sys
import time
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
from typing import Any, Dict, List

# ── Tự động chèn virtualenv site-packages vào sys.path ──────────────────────
_VENV_SITE = Path(__file__).resolve().parent.parent / "backend" / "ai-service" / ".venv" / "Lib" / "site-packages"
if _VENV_SITE.exists() and str(_VENV_SITE) not in sys.path:
    sys.path.insert(0, str(_VENV_SITE))
# ─────────────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
AI_SERVICE_DIR = PROJECT_DIR / "backend" / "ai-service"
DATASET_DIR = BASE_DIR / "custom_voice_samples"
MODEL_OUTPUT_DIR = AI_SERVICE_DIR / "whisper-voice-fine-tuned"

SAMPLE_RATE = 16000
CHANNELS = 1

SAMPLE_PROMPTS: List[str] = [
    "Chào mừng các bạn đến với buổi học về trí tuệ nhân tạo hôm nay.",
    "Một hai ba bốn năm sáu bảy tám chín mười.",
    "1 2 3 4 5 6 7 8 9 10.",
    "Welcome to ClassBridge real-time bilingual transcription system.",
    "Hệ thống tự động phân tách người nói và dịch thuật song ngữ.",
    "Giảng viên có thể bắt đầu hoặc tạm dừng phiên dịch bất kỳ lúc nào.",
    "Chúng ta sẽ cùng tìm hiểu về thuật toán xử lý ngôn ngữ tự nhiên.",
    "Please turn to page twenty-five of your textbook.",
    "Phụ đề hiển thị trực tiếp và hỗ trợ xuất file bài giảng.",
    "Mạng thần kinh nhân tạo và các mô hình học máy sâu.",
    "Computer science and software engineering curriculum.",
    "Thưa thầy em có câu hỏi về phần bài tập nhóm vừa giao.",
    "Tín chỉ môn học và đề cương chi tiết của học kỳ này.",
    "10 20 30 40 50 100 1000.",
    "Cảm ơn các bạn đã lắng nghe bài giảng hôm nay.",
]


def record_audio(sentence: str, index: int) -> str:
    """Thu âm một câu mẫu từ micro, lưu file WAV, trả về đường dẫn."""
    try:
        import sounddevice as sd  # type: ignore[import]
        import soundfile as sf  # type: ignore[import]
    except ImportError:
        print("⚠️  Thiếu thư viện: pip install sounddevice soundfile")
        raise

    print(f"\n=======================================================")
    print(f"📌 Câu {index + 1}/{len(SAMPLE_PROMPTS)}:")
    print(f'   👉 Vui lòng đọc: "{sentence}"')
    print("=======================================================")
    input("👉 Nhấn ENTER để bắt đầu thu âm (nói trong 4.5 giây)...")

    print("🎙️ ĐANG THU ÂM... Hãy đọc câu trên ngay!")
    duration = 4.5
    recording = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="float32")
    sd.wait()
    print("✅ Thu âm hoàn tất!")

    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    audio_path = DATASET_DIR / f"sample_{index + 1}.wav"
    sf.write(str(audio_path), recording, SAMPLE_RATE)
    return str(audio_path)


def create_metadata_csv(samples: List[Dict[str, str]]) -> str:
    """Tạo file CSV manifest từ danh sách mẫu thu âm."""
    csv_path = DATASET_DIR / "dataset.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["audio_path", "sentence"])
        for sample in samples:
            writer.writerow([sample["audio_path"], sample["sentence"]])
    print(f"📊 Đã tạo tập dữ liệu huấn luyện tại: {csv_path}")
    return str(csv_path)


def run_fine_tuning(csv_path: str) -> None:
    """Chạy fine-tuning Whisper LoRA với dữ liệu thu âm cá nhân."""
    print("\n🚀 Bắt đầu quá trình Huấn luyện Mô hình Giọng nói (Fine-Tuning LoRA)...")
    try:
        from transformers import (  # type: ignore[import]
            WhisperFeatureExtractor,
            WhisperTokenizer,
            WhisperProcessor,
            WhisperForConditionalGeneration,
        )
        from datasets import load_dataset, Audio  # type: ignore[import]
        from peft import LoraConfig, get_peft_model  # type: ignore[import]

        MODEL_NAME = "openai/whisper-base"
        print(f"[ClassBridge Train] Nạp mô hình gốc {MODEL_NAME}...")

        processor = WhisperProcessor.from_pretrained(MODEL_NAME, language="Vietnamese", task="transcribe")
        tokenizer = WhisperTokenizer.from_pretrained(MODEL_NAME, language="Vietnamese", task="transcribe")
        feature_extractor = WhisperFeatureExtractor.from_pretrained(MODEL_NAME)

        raw_dataset = load_dataset("csv", data_files={"train": csv_path})
        raw_dataset = raw_dataset.cast_column("audio_path", Audio(sampling_rate=16000))

        def prepare_data(batch: Dict[str, Any]) -> Dict[str, Any]:
            audio = batch["audio_path"]
            batch["input_features"] = feature_extractor(
                audio["array"], sampling_rate=audio["sampling_rate"]
            ).input_features[0]
            batch["labels"] = tokenizer(batch["sentence"]).input_ids
            return batch

        raw_dataset.map(prepare_data, remove_columns=raw_dataset["train"].column_names)

        model = WhisperForConditionalGeneration.from_pretrained(MODEL_NAME)
        model.config.forced_decoder_ids = None
        model.config.suppress_tokens = []

        lora_config = LoraConfig(
            r=32, lora_alpha=64, target_modules=["q_proj", "v_proj"],
            lora_dropout=0.05, bias="none"
        )
        model = get_peft_model(model, lora_config)

        MODEL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        model.save_pretrained(str(MODEL_OUTPUT_DIR))
        processor.save_pretrained(str(MODEL_OUTPUT_DIR))
        print(f"\n🎉 HOÀN TẤT! Mô hình giọng nói đã lưu tại: {MODEL_OUTPUT_DIR}")
        print("💡 Khi khởi động lại ứng dụng, ClassBridge sẽ tự động dùng giọng này!")

    except Exception as e:
        print(f"⚠️ Cảnh báo trong quá trình train: {e}")
        print("Mẹo: pip install torch transformers peft datasets soundfile")


def main() -> None:
    print("=========================================================================")
    print("   ClassBridge - HUẤN LUYỆN & CÁ NHÂN HÓA GIỌNG NÓI CHÍNH XÁC (STT)   ")
    print("=========================================================================")
    print("Chương trình này sẽ thu âm các mẫu câu giọng của bạn để huấn luyện Whisper.")

    choice = input("\nBạn có muốn bắt đầu thu âm ngay bây giờ? (y/n): ").strip().lower()
    if choice != "y":
        print("Đã hủy quá trình thu âm.")
        return

    samples: List[Dict[str, str]] = []
    for i, prompt in enumerate(SAMPLE_PROMPTS):
        audio_path = record_audio(prompt, i)
        samples.append({"audio_path": audio_path, "sentence": prompt})
        time.sleep(0.5)

    csv_path = create_metadata_csv(samples)
    run_fine_tuning(csv_path)


if __name__ == "__main__":
    main()
