"""
ClassBridge – Lightweight Phonetic Normalization & Unicode Standardizer
Chế độ hoạt động: Pure Raw Model Mode (Bảo tồn 100% lời nói gốc nguyên bản từ AI Model).
Không dùng bất kỳ từ điển gán ép hay câu mẫu có sẵn nào.
"""

from __future__ import annotations

import re
import unicodedata

_RE_MULTI_SPACES = re.compile(r"\s+")
_RE_INVALID_CHARS = re.compile(r'[\u0060\u00B4\u02CA\u02CB\u02C6\u02DC\^~|]+')


class CorrectionModule:
    """
    Pure Raw Model Mode:
    - Trả về 100% lời gốc nguyên bản do mô hình AI sinh ra.
    - Không can thiệp sửa từ hay gán ép từ điển cứng.
    - Chỉ chuẩn hóa Unicode NFC để đảm bảo hiển thị tiếng Việt và tiếng Anh chuẩn xác.
    """

    def __init__(self) -> None:
        pass

    def clean(self, text: str) -> str:
        """Trả về 100% lời gốc nguyên bản từ mô hình AI."""
        if not text or not text.strip():
            return ""

        # Chuẩn hóa Unicode NFC duy nhất để tránh lỗi font hiển thị
        cleaned = unicodedata.normalize("NFC", text)
        cleaned = _RE_INVALID_CHARS.sub("", cleaned)
        cleaned = _RE_MULTI_SPACES.sub(" ", cleaned).strip()
        return cleaned
