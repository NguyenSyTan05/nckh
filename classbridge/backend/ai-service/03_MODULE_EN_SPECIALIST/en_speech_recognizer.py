"""
ClassBridge 2-Module Architecture
Component: 03_MODULE_EN_SPECIALIST / en_speech_recognizer.py
Chức năng: Chuyên gia nhận dạng tiếng Anh & Accent Châu Á (Whisper Decoder Micro-4).
Tối ưu: Nhận diện giọng tiếng Anh người Việt, thuật ngữ CNTT (Docker, API, Kubernetes).
"""

from __future__ import annotations
import os
import unicodedata
import re
from pathlib import Path
import numpy as np


class EnglishSpeechRecognizer:
    def __init__(
        self,
        model_path: str = "d:/TailieuNPKH/classbridge/backend/ai-service/Module_Train/02_TRAIN_TIENG_ANH/model_en_ct2",
        fallback_path: str = "d:/TailieuNPKH/DoAN2module/Module_Train/02_TRAIN_TIENG_ANH/model_en_ct2",
        device: str = "cuda",
        compute_type: str = "float16",
    ) -> None:
        self.device = device
        self.compute_type = compute_type
        if os.path.exists(model_path):
            chosen_path = model_path
        elif os.path.exists(fallback_path):
            chosen_path = fallback_path
        else:
            chosen_path = model_path
        print(f"[Module 2 - EN Specialist] 🇬🇧 Đang nạp mô hình chuyên gia Tiếng Anh từ: {chosen_path}")
        
        from faster_whisper import WhisperModel
        self.model = WhisperModel(
            chosen_path,
            device=self.device,
            compute_type=self.compute_type,
            cpu_threads=4,
            num_workers=1,
        )

    def transcribe(self, audio: str | np.ndarray, beam_size: int = 1) -> dict:
        segments, info = self.model.transcribe(
            audio,
            language="en",
            beam_size=beam_size,
            temperature=0.0,
            repetition_penalty=1.05,
            without_timestamps=True,
            condition_on_previous_text=False,
        )
        
        raw_text = " ".join([seg.text.strip() for seg in segments])
        cleaned_text = unicodedata.normalize("NFC", raw_text)
        cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
        
        return {
            "module": "Module 2 (English Specialist)",
            "language": "en",
            "text": cleaned_text,
            "raw_text": raw_text,
            "duration": getattr(info, "duration", 0.0),
        }
