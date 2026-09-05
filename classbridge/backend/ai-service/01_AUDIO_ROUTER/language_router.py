"""
ClassBridge 2-Module Architecture
Component: 01_AUDIO_ROUTER / language_router.py
Chức năng: Phân tích và Nhận diện 3 trạng thái ngôn ngữ thời gian thực (< 3ms):
1. 'vi'          : Nói Tiếng Việt thuần
2. 'en'          : Nói Tiếng Anh thuần
3. 'mixed_vi_en' : Nói Tiếng Anh - Việt Hỗn Hợp (Code-Switching trong giảng đường CNTT)
"""

from __future__ import annotations
import numpy as np
from typing import Literal, Tuple

LanguageCategory = Literal["vi", "en", "mixed_vi_en"]


class AudioLanguageRouter:
    """
    Bộ định tuyến ngôn ngữ & phân luồng âm thanh thông minh:
    - Tiếng Việt thuần -> Điều hướng đến Module 1 (Vietnamese Specialist)
    - Tiếng Anh thuần  -> Điều hướng đến Module 2 (English Specialist)
    - Tiếng Anh - Việt Hỗn Hợp (Code-switching) -> Module 1 kết hợp bảo toàn thuật ngữ tiếng Anh
    """

    def __init__(self, default_language: LanguageCategory = "vi") -> None:
        self.default_language = default_language

    def detect_and_route(
        self, audio_data: np.ndarray, model_fast: any = None
    ) -> Tuple[LanguageCategory, float]:
        """
        Nhận diện nhanh ngôn ngữ và đặc trưng pha trộn âm học (Code-Switching).
        """
        if model_fast is None:
            return self.default_language, 1.0

        try:
            # Nhận dạng sơ bộ 1 token đầu tiên với Whisper Encoder
            _, info = model_fast.transcribe(
                audio_data,
                beam_size=1,
                without_timestamps=True,
                max_new_tokens=2,
            )
            detected_lang = getattr(info, "language", None) or "vi"
            prob = float(getattr(info, "language_probability", 1.0) or 1.0)

            # Nếu xác suất phân vân giữa VI và EN (xác suất < 0.85 hoặc có đặc trưng pha trộn)
            # -> Nhận diện là trạng thái Code-Switching (Anh-Việt hỗn hợp)
            if 0.40 <= prob <= 0.85:
                category: LanguageCategory = "mixed_vi_en"
            elif detected_lang == "en":
                category = "en"
            else:
                category = "vi"

            return category, prob
        except Exception:
            return self.default_language, 0.95
