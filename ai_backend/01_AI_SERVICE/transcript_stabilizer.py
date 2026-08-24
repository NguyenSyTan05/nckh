"""
ClassBridge – Realtime Transcript Stabilizer Module
(Local Agreement & Monotonic Prefix Locking)

Thuật toán chống nhảy chữ, chống mất chữ, bảo toàn dấu tiếng Việt và thuật ngữ tiếng Anh:
1. Duy trì prefix đã được xác nhận (_locked_words).
2. Khi partial mới đến:
   - Khóa cứng tiền tố (Prefix Locking) để không bao giờ bị giật/đổi chữ ở đầu câu.
   - So khớp tiền tố chung (Longest Common Prefix) giữa 2 revision liên tiếp.
   - Chốt các từ đã xuất hiện ổn định vào _locked_words.
   - Giữ lại 1-2 từ đuôi mới nhất làm unstable_text.
3. Khi finalize:
   - Khóa toàn bộ thành stable_text và reset sạch sẽ cho segment kế tiếp.
"""

from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass
from typing import Any, List

logger = logging.getLogger(__name__)


@dataclass
class StabilizedResult:
    stable_text: str
    unstable_text: str
    full_text: str
    is_final: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "stable_text": self.stable_text,
            "unstable_text": self.unstable_text,
            "full_text": self.full_text,
            "is_final": self.is_final,
        }


def _clean_text_basic(text: str) -> str:
    """Chuẩn hóa Unicode NFC cơ bản, giữ nguyên dấu tiếng Việt và dấu nháy đơn tiếng Anh."""
    if not text:
        return ""
    cleaned = unicodedata.normalize("NFC", text)
    # Loại bỏ ký tự rác / backtick, không xóa dấu nháy đơn ' hay các ký tự hợp lệ
    cleaned = re.sub(r'[\u0060\u00B4\u02CA\u02CB\u02C6\u02DC\^~|]+', '', cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _normalize_word_match(w: str) -> str:
    """Chuẩn hóa từ để so khớp (bỏ dấu câu, lowercase, NFC)."""
    return re.sub(r"[^\w\s]", "", unicodedata.normalize("NFC", w).lower()).strip()


class TranscriptStabilizer:
    """
    ClassBridge Realtime Transcript Stabilizer:
    - Thuật toán Local Agreement (Prefix Locking).
    - Đảm bảo stable_text tăng đơn điệu (Monotonic), không bao giờ co lại hoặc nhảy chữ.
    - Giữ trọn vẹn mọi từ phát âm, không làm mất chữ hay làm sai lệch dấu tiếng Việt.
    """

    def __init__(
        self,
        min_stable_count: int = 2,
        unstable_tail_words: int = 1,
        **kwargs: Any,
    ) -> None:
        self.min_stable_count = max(1, min_stable_count)
        self.unstable_tail_words = max(1, unstable_tail_words)
        self._locked_words: List[str] = []
        self._prev_words: List[str] = []
        self._last_full_text: str = ""

    def reset(self) -> None:
        """Reset trạng thái khi bắt đầu segment mới."""
        self._locked_words.clear()
        self._prev_words.clear()
        self._last_full_text = ""

    def process_partial(self, partial_text: str) -> StabilizedResult:
        """
        Xử lý partial transcript mới từ Whisper cho segment hiện tại.
        Áp dụng Local Agreement để chốt dần từng từ đã ổn định.
        """
        cleaned = _clean_text_basic(partial_text)
        if not cleaned:
            return StabilizedResult(
                stable_text=" ".join(self._locked_words),
                unstable_text="",
                full_text=" ".join(self._locked_words),
                is_final=False,
            )

        current_words = cleaned.split()
        if not current_words:
            return StabilizedResult(
                stable_text=" ".join(self._locked_words),
                unstable_text="",
                full_text=" ".join(self._locked_words),
                is_final=False,
            )

        # 1. Tìm vị trí tiếp nối nếu _locked_words đã có
        if self._locked_words:
            # Kiểm tra xem current_words có bắt đầu bằng _locked_words không
            locked_len = len(self._locked_words)
            match_len = 0
            for i in range(min(locked_len, len(current_words))):
                if _normalize_word_match(self._locked_words[i]) == _normalize_word_match(current_words[i]):
                    match_len += 1
                else:
                    break

            if match_len == locked_len:
                # current_words tiếp nối hoàn hảo locked_words
                new_candidate_words = current_words[locked_len:]
            else:
                # Nếu sliding window của Whisper bị trượt hoặc thay đổi từ đầu,
                # tìm vị trí xuất hiện của phần đuôi locked_words trong current_words
                overlap_idx = -1
                for i in range(len(current_words)):
                    sub_locked = [_normalize_word_match(w) for w in self._locked_words[-3:]]
                    sub_curr = [_normalize_word_match(w) for w in current_words[i:i+len(sub_locked)]]
                    if sub_locked and sub_curr == sub_locked:
                        overlap_idx = i + len(sub_locked)
                        break

                if overlap_idx != -1 and overlap_idx < len(current_words):
                    new_candidate_words = current_words[overlap_idx:]
                else:
                    # Giữ nguyên locked_words và lấy các từ mới ngoài locked_words
                    locked_norm_set = set(_normalize_word_match(w) for w in self._locked_words)
                    new_candidate_words = [w for w in current_words if _normalize_word_match(w) not in locked_norm_set]
                    if not new_candidate_words:
                        new_candidate_words = current_words[-self.unstable_tail_words:]
        else:
            new_candidate_words = current_words

        # 2. So khớp Local Agreement với _prev_words để chốt từ
        if self._prev_words and new_candidate_words:
            common_count = 0
            for w_prev, w_curr in zip(self._prev_words, new_candidate_words):
                if _normalize_word_match(w_prev) == _normalize_word_match(w_curr):
                    common_count += 1
                else:
                    break

            # Chốt các từ khớp vượt qua ngưỡng unstable_tail_words
            lockable_count = max(0, common_count)
            if len(new_candidate_words) > self.unstable_tail_words:
                lockable_count = min(lockable_count, len(new_candidate_words) - self.unstable_tail_words)

            if lockable_count > 0:
                words_to_lock = new_candidate_words[:lockable_count]
                self._locked_words.extend(words_to_lock)
                new_candidate_words = new_candidate_words[lockable_count:]

        self._prev_words = list(new_candidate_words)

        # 3. Tổng hợp Stable và Unstable
        stable_str = " ".join(self._locked_words).strip()
        unstable_str = " ".join(new_candidate_words).strip()

        if stable_str and unstable_str:
            full_str = f"{stable_str} {unstable_str}"
        elif stable_str:
            full_str = stable_str
        else:
            full_str = unstable_str

        self._last_full_text = full_str

        return StabilizedResult(
            stable_text=stable_str,
            unstable_text=unstable_str,
            full_text=full_str,
            is_final=False,
        )

    def finalize(self, final_text: str) -> StabilizedResult:
        """
        Xác nhận segment đã kết thúc (final).
        Khóa toàn bộ văn bản và reset để đón segment mới.
        """
        cleaned = _clean_text_basic(final_text)
        if not cleaned:
            cleaned = self._last_full_text or " ".join(self._locked_words)

        # Đảm bảo final_text chứa đủ các từ đã từng locked
        if self._locked_words:
            locked_prefix = " ".join(self._locked_words)
            if not _normalize_word_match(cleaned).startswith(_normalize_word_match(locked_prefix)[:10]):
                cleaned = f"{locked_prefix} {cleaned}".strip()

        self.reset()
        return StabilizedResult(
            stable_text=cleaned,
            unstable_text="",
            full_text=cleaned,
            is_final=True,
        )
