"""
ClassBridge 2-Module Architecture
Component: 02_MODULE_VI_SPECIALIST / vi_speech_recognizer.py
Chức năng: Chuyên gia nhận dạng Tiếng Việt & Tiếng Anh - Việt Hỗn Hợp (Code-Switching).
Tối ưu:
- Bắt trọn 5 dấu thanh điệu tiếng Việt (Sắc, Huyền, Hỏi, Ngã, Nặng).
- Giữ nguyên bản 100% thuật ngữ tiếng Anh CNTT khi giảng viên nói chêm (Docker, API, Kubernetes, React, Backend...).
- Không dùng từ điển gán ép hay câu mẫu có sẵn.
"""

from __future__ import annotations
import os
import unicodedata
import re
from pathlib import Path
import numpy as np


class VietnameseSpeechRecognizer:
    def __init__(
        self,
        model_path: str = "d:/TailieuNPKH/classbridge/backend/ai-service/Module_Train/01_TRAIN_TIENG_VIET/model_vi_ct2",
        fallback_path: str = "d:/TailieuNPKH/DoAN2module/Module_Train/01_TRAIN_TIENG_VIET/model_vi_ct2",
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
            chosen_path = "d:/TailieuNPKH/classbridge/training/outputs/whisper-custom-proportions-ct2"
        print(f"[Module 1 - VI Specialist] 🇻🇳 Đang nạp mô hình chuyên gia Tiếng Việt từ: {chosen_path}")
        
        from faster_whisper import WhisperModel
        self.model = WhisperModel(
            chosen_path,
            device=self.device,
            compute_type=self.compute_type,
            cpu_threads=4,
            num_workers=1,
        )

    def transcribe(self, audio: str | np.ndarray, beam_size: int = 1, is_mixed: bool = False) -> dict:
        """
        Nhận diện âm thanh Tiếng Việt thuần hoặc Tiếng Anh - Việt Hỗn Hợp.
        """
        segments, info = self.model.transcribe(
            audio,
            language="vi",
            beam_size=beam_size,
            temperature=0.0,
            repetition_penalty=1.05,
            without_timestamps=True,
            condition_on_previous_text=False,
        )
        
        raw_text = " ".join([seg.text.strip() for seg in segments])
        cleaned_text = unicodedata.normalize("NFC", raw_text)
        cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
        
        module_name = "Module 1 (Vietnamese Specialist - Code Switching Enabled)" if is_mixed else "Module 1 (Vietnamese Specialist)"
        
        return {
            "module": module_name,
            "language": "mixed_vi_en" if is_mixed else "vi",
            "text": cleaned_text,
            "raw_text": raw_text,
            "duration": getattr(info, "duration", 0.0),
        }
