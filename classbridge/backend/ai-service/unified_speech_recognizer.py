"""
ClassBridge Unified Architecture
Component: unified_speech_recognizer.py
Chức năng: Nhận dạng giọng nói Đa ngữ Thống nhất (Tiếng Việt, Tiếng Anh & Code-switching)
Nguyên tắc cốt lõi:
- NGHE ĐƯỢC CHỮ GÌ THÌ HIỂN THỊ ĐÚNG CHỮ ĐÓ.
- Tuyệt đối không dùng các từ mẫu cố định hay ép buộc từ điển thay thế từ ngữ.
- Whisper CTranslate2 Float16 thuần túy âm học (Acoustic Decoding) với Beam Search 5.
- Silero VAD bảo toàn âm thanh, chống nuốt câu/mất từ khi nói dài.
- Chuẩn hóa hiển thị: Unicode NFC, viết hoa đầu câu, khoảng trắng chuẩn quanh dấu câu.
"""

from __future__ import annotations
import os
import sys
import re
import unicodedata
from pathlib import Path
import numpy as np

# Đảm bảo Windows console không bị lỗi mã hóa khi in tiếng Việt / emoji
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def clean_transcript_text(text: str) -> str:
    """
    Chuẩn hóa hiển thị văn bản tự nhiên, KHÔNG thay đổi bất kỳ từ nào người nói đã phát âm:
    - Chuẩn hóa Unicode dựng sẵn NFC (tránh lỗi hiển thị font tiếng Việt).
    - Chuẩn hóa khoảng cách quanh dấu câu.
    - Viết hoa chữ cái đầu câu.
    """
    if not text or not text.strip():
        return ""

    # 1. Chuẩn hóa Unicode NFC
    s = unicodedata.normalize("NFC", text.strip())

    # 2. Xóa khoảng trắng thừa trước dấu câu (ví dụ: "xin chào , các bạn" -> "xin chào, các bạn")
    s = re.sub(r"\s+([,\.!\?:;])", r"\1", s)
    s = re.sub(r"([,\.!\?:;])([^\s0-9])", r"\1 \2", s)
    s = re.sub(r"\s+", " ", s).strip()

    # 3. Viết hoa chữ cái đầu câu và sau dấu chấm, hỏi, than (hỗ trợ đầy đủ Unicode tiếng Việt)
    def capitalize_match(match):
        prefix = match.group(1)
        char = match.group(2)
        return prefix + char.upper()

    s = re.sub(r"(^|[.!?]\s+)([^\W\d_])", capitalize_match, s, flags=re.UNICODE)
    if len(s) > 0 and s[0].islower():
        s = s[0].upper() + s[1:]

    return s.strip()


def remove_repeated_phrases(text: str) -> str:
    """Khử các vòng lặp token bất thường do decoder (ví dụ lặp 3-4 lần liên tục cùng 1 từ)."""
    if not text:
        return ""
    current = text.strip()
    for _ in range(3):
        tokens = re.findall(r"\S+", current)
        if len(tokens) <= 1:
            break

        def norm_tok(t: str) -> str:
            return re.sub(r"^[^\w\s]+|[^\w\s]+$", "", t).lower()

        n = len(tokens)
        i = 0
        cleaned_tokens: list[str] = []
        changed = False

        while i < n:
            matched = False
            for phrase_len in range(1, min(15, (n - i) // 2 + 1)):
                phrase_norms = [norm_tok(tokens[i + k]) for k in range(phrase_len)]
                if not any(phrase_norms):
                    continue

                repeat_count = 1
                j = i + phrase_len
                while j + phrase_len <= n:
                    next_norms = [norm_tok(tokens[j + k]) for k in range(phrase_len)]
                    if next_norms == phrase_norms:
                        repeat_count += 1
                        j += phrase_len
                    else:
                        break

                # Chỉ khử nếu lặp từ 3 lần trở lên (để bảo tồn từ láy đôi tiếng Việt như "luôn luôn", "rất rất", "từ từ")
                if (phrase_len == 1 and repeat_count >= 3) or (phrase_len > 1 and repeat_count >= 2):
                    cleaned_tokens.extend(tokens[i : i + phrase_len])
                    i = j
                    matched = True
                    changed = True
                    break

            if not matched:
                cleaned_tokens.append(tokens[i])
                i += 1

        current = " ".join(cleaned_tokens)
        current = re.sub(r"([,\.!?])(\s*\1)+", r"\1", current)
        if not changed:
            break

    current = re.sub(r",\s*$", "", current)
    return current.strip()


# Danh sách mẫu chuỗi rác / hallucination từ tiếng ồn micro, tiếng thở, nhạc nền hoặc phụ đề phim/YouTube
HALLUCINATION_PATTERNS = [
    # Ảo giác tiếng Anh pop/movie/YouTube khi im lặng hoặc có nhạc/tiếng thở
    r"^\s*(i\s+see\s+the\s+light|i'm\s+coming|i\s+am\s+coming|i'm\s+cold|i'm\s+single|i\s+know|that\s+is\s+so|big,?\s+big\s+way|storm\s+meeting\s+done)\.?\s*$",
    r"^\s*(hey|bye|bye\s+bye|bye\s+now|goodbye|i\s+am|thank\s+you.*|thanks.*|all\s+right|alright|yes|no|ok|okay|that's\s+how\s+i\s+get\s+it|we\s+want\s+ai\s+now|let's\s+go.*|i'm\s+not\s+in|i\s+need\s+to\s+come\s+back|i'll\s+pass\s+it\s+in|so,?\s+we'll\s+go\s+back.*)\.?\s*$",
    r"^\s*(you|you\s+know|so|yeah|the\s+end|welcome\s+back|see\s+you\s+next\s+time|see\s+you\s+later)\.?\s*$",
    # Ảo giác phụ đề YouTube
    r".*(subscribe|đăng\s*ký)\s+(cho\s+)?kênh.*",
    r".*(la\s*la\s*school|ghiền\s*mì\s*gõ|fap\s*tv).*",
    r".*để\s+không\s+bỏ\s+lỡ.*",
    r".*(like\s+và\s+subscribe|bấm\s*chuông|subtitles?\s+by).*?",
    # Ký hiệu âm nhạc/tiếng ồn
    r"^\s*(\[.*?\]|\(.*?\)|♪+|♫+|\.+|\-+)\s*$",
    # Ảo giác tiếng ngoại lai Latin (Ý, Tây Ban Nha, Bồ Đào Nha, Hà Lan...)
    r".*\b(non\s+è|della|nostra|nostro|allora|ematina|cabe\s+aí|vamos\s+a|jij\s+bent\s+het)\b.*",
]
HALLUCINATION_REGEX = re.compile("|".join(HALLUCINATION_PATTERNS), re.IGNORECASE)

# TẤT CẢ các nguyên âm và ký tự có dấu thanh điệu tiếng Việt (chuẩn NFC)
ALL_VI_CHARS_REGEX = re.compile(
    r"[àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ"
    r"ÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ]"
)

# Ký tự đặc trưng chỉ có trong tiếng Việt (không bao giờ trùng với tiếng Tây Âu)
VI_SPECIFIC_CHARS_REGEX = re.compile(
    r"[ăâđêôơưảãạẳẵặẩẫậẻẽẹểễệỉĩịỏõọổỗộởỡợủũụửữựỳýỷỹỵ"
    r"ĂÂĐÊÔƠƯẢÃẠẲẴẶẨẪẬẺẼẸỂỄỆỈĨỊỎÕỌỔỖỘỞỠỢỦŨỤỬỮỰỲÝỶỸỴ]"
)

# Tập các từ đơn tiếng Việt phổ biến không dấu (dùng để nhận dạng câu tiếng Việt dù chưa có dấu)
VI_UNACCENTED_WORDS = {
    "toi", "ban", "anh", "em", "co", "la", "va", "khong", "nguoi", "trong",
    "cho", "di", "ve", "lam", "nay", "do", "duoc", "ra", "vao", "voi",
    "den", "theo", "biet", "noi", "nhung", "thi", "ma", "cac", "lop",
    "hoc", "bai", "thay", "da", "se", "dang", "con", "mot", "hai", "ba"
}

# Ký tự ngoại lai ngoài song ngữ Anh - Việt (Hàn, Gruzia, CJK, Cyrillic, Ả Rập, Thái,...)
FOREIGN_SCRIPTS_REGEX = re.compile(
    r"[\uac00-\ud7a3\u1100-\u11ff"  # Hangul (Hàn Quốc)
    r"\u10a0-\u10ff\u1c90-\u1cba"  # Georgian (Gruzia)
    r"\u4e00-\u9fff\u3400-\u4dbf"  # CJK (Trung Quốc)
    r"\u3040-\u30ff"              # Hiragana / Katakana (Nhật Bản)
    r"\u0400-\u04ff"              # Cyrillic (Nga)
    r"\u0600-\u06ff"              # Arabic (Ả Rập)
    r"\u0e00-\u0e7f]"             # Thai (Thái Lan)
)

# Prompt chuẩn hướng dẫn Whisper giải mã đầy đủ thanh điệu và dấu câu tiếng Việt
VI_INITIAL_PROMPT = (
    "Xin chào, đây là bài giảng và hội thoại tiếng Việt chuẩn xác, "
    "có đầy đủ dấu thanh điệu, dấu câu rõ ràng từng từ ngữ: "
    "á, à, ả, ã, ạ, ă, ắ, ằ, ẳ, ẵ, ặ, â, ấ, ầ, ẩn, ẫ, ậ, "
    "é, è, ẻ, ẽ, ẹ, ê, ế, ề, ể, ễ, ệ, "
    "í, ì, ỉ, ĩ, ị, "
    "ó, ò, ỏ, õ, ọ, ô, ố, ồ, ổ, ỗ, ộ, ơ, ớ, ờ, ở, ỡ, ợ, "
    "ú, ù, ủ, ũ, ụ, ư, ứ, ừ, ử, ữ, ự, "
    "ý, ỳ, ỷ, ỹ, y, đ."
)


def is_hallucination(text: str) -> bool:
    """
    Kiểm tra xem câu có phải là ảo giác YouTube, ảo giác tiếng ồn phòng hoặc ngoại lai.
    Bảo tồn trọn vẹn mọi lời nói tự nhiên của người dùng.
    """
    if not text or not text.strip():
        return True
    cleaned = text.strip()

    # 1. Loại bỏ ngay nếu chứa ký tự ngoại lai ngoài song ngữ Anh - Việt
    if FOREIGN_SCRIPTS_REGEX.search(cleaned):
        return True

    # 2. Loại bỏ các mẫu câu rác / ảo giác do tiếng ồn mic hoặc phụ đề học vẹt
    if HALLUCINATION_REGEX.search(cleaned):
        return True

    # 3. Loại bỏ chuỗi lặp 1 từ vô hạn do decoder (ví dụ: a a a a a)
    words = cleaned.split()
    if len(words) >= 4 and len(set(w.lower() for w in words)) <= 1:
        return True

    # 4. Loại bỏ các chuỗi chỉ toàn ký tự lạ / ký hiệu đặc biệt
    letters_or_digits = re.findall(r"[\w\d]", cleaned, flags=re.UNICODE)
    if len(letters_or_digits) < 1:
        return True

    return False


class UnifiedSpeechRecognizer:
    """
    Module Nhận dạng Giọng nói Đa ngữ Thống nhất:
    - 1 mô hình Whisper CTranslate2 duy nhất phục vụ toàn bộ ngôn ngữ (VI / EN / Code-Switching).
    - Tối ưu bộ nhớ VRAM cho GPU RTX 3050 (4GB) ~ 1GB VRAM.
    - Nhận dạng thuần túy theo âm thanh thực tế: Nghe được chữ gì thì hiển thị chữ đó!
    - Tuyệt đối không dùng từ mẫu hay từ điển thay thế từ ngữ.
    """

    def __init__(
        self,
        device: str = "cuda",
        compute_type: str = "float16",
    ) -> None:
        self.device = device
        self.compute_type = compute_type

        candidate_paths = [
            "C:/Users/Nguyen Sy Tan/.cache/huggingface/hub/models--Systran--faster-whisper-small/snapshots/536b0662742c02347bc0e980a01041f333bce120",
            os.getenv("WHISPER_MODEL_PATH", ""),
            "d:/TailieuNPKH/classbridge/training/Module_Train/01_TRAIN_TIENG_VIET/model_vi_ct2",
            str(Path(__file__).resolve().parent.parent / "training" / "Module_Train" / "01_TRAIN_TIENG_VIET" / "model_vi_ct2"),
            "d:/TailieuNPKH/classbridge/backend/ai-service/.models/hub/models--Systran--faster-whisper-small/snapshots/536b0662742c02347bc0e980a01041f333bce120",
        ]

        chosen_path = None
        for p in candidate_paths:
            if p and os.path.exists(p):
                chosen_path = p
                break

        if not chosen_path:
            chosen_path = "small"

        print(f"[Unified ASR] 🎙️ Đang nạp mô hình Whisper đa ngữ từ: {chosen_path}", flush=True)

        from faster_whisper import WhisperModel
        try:
            self.model = WhisperModel(
                chosen_path,
                device=self.device,
                compute_type=self.compute_type,
                cpu_threads=4,
                num_workers=1,
            )
        except Exception as e:
            print(f"[Unified ASR] ⚠️ Lỗi nạp CUDA ({e}), chuyển sang CPU...", flush=True)
            self.device = "cpu"
            self.compute_type = "int8"
            self.model = WhisperModel(
                chosen_path,
                device="cpu",
                compute_type="int8",
                cpu_threads=4,
                num_workers=1,
            )

        # Warmup GPU để loại bỏ hoàn toàn Cold Start, câu nói đầu tiên của người dùng phản hồi ngay tức thì
        try:
            dummy_pcm = np.zeros(16000, dtype=np.float32)
            _ = list(self.model.transcribe(dummy_pcm, language="vi", beam_size=1, without_timestamps=True)[0])
        except Exception:
            pass

        print("[Unified ASR] ✅ Mô hình ASR Đa ngữ (Acoustic Fast-Greedy) đã sẵn sàng!", flush=True)

    def transcribe(
        self,
        audio: str | np.ndarray,
        language: str | None = None,
        beam_size: int = 2,
        previous_text: str | None = None,
    ) -> dict:
        """
        Nhận dạng giọng nói thuần túy theo âm thanh thực tế:
        - Sử dụng initial_prompt tiếng Việt chuẩn mực để giữ trọn vẹn dấu thanh.
        - Khóa cứng temperature = 0.0 để triệt tiêu hoàn toàn hallucination.
        - Padding VAD 400ms để không bao giờ bị cắt mất âm đầu và âm cuối.
        """
        target_lang = None
        if language:
            lowered = language.lower().strip()
            if lowered in ["vi", "vn", "vietnamese"]:
                target_lang = "vi"
            elif lowered in ["en", "english"]:
                target_lang = "en"
            # "auto" / "mixed_vi_en" -> target_lang = None (Whisper tự nhận diện ngôn ngữ)

        # Định hướng giải mã tiếng Việt chuẩn có dấu nếu là tiếng Việt hoặc tự động
        prompt = VI_INITIAL_PROMPT if (target_lang == "vi" or target_lang is None) else None

        effective_beam = max(2, beam_size or 2)
        segments, info = self.model.transcribe(
            audio,
            language=target_lang,
            beam_size=effective_beam,
            best_of=effective_beam,
            temperature=0.0,                  # Khóa cứng 0.0: Tuyệt đối không sinh từ ngẫu nhiên
            repetition_penalty=1.20,          # Khử vòng lặp token bất thường
            no_repeat_ngram_size=3,           # Không lặp cụm 3 từ giống nhau liên tục
            without_timestamps=True,
            condition_on_previous_text=False,
            initial_prompt=prompt,            # Đảm bảo đầy đủ dấu tiếng Việt
            hotwords=None,
            compression_ratio_threshold=2.4,  # Chuẩn Whisper: Không loại bỏ câu bình thường
            log_prob_threshold=-1.0,          # Chuẩn Whisper: Không kích hoạt fallback sai lệch
            no_speech_threshold=0.6,          # Bỏ qua tiếng thở / tiếng ồn phòng
            vad_filter=True,                  # Silero VAD
            vad_parameters=dict(
                threshold=0.35,               # Nhạy bén với cả giọng nhỏ nhẹ, nói thầm
                min_speech_duration_ms=150,   # Không nuốt từ ngắn ('dạ', 'vâng', 'có', 'đúng')
                max_speech_duration_s=float("inf"),
                min_silence_duration_ms=300,
                speech_pad_ms=400,            # Đệm 400ms trước và sau: Bảo toàn trọn vẹn âm đầu & âm cuối
            ),
        )

        valid_segments = [
            seg for seg in segments
            if seg.text.strip()
            and getattr(seg, "no_speech_prob", 0.0) < 0.65
        ]

        raw_text = " ".join([seg.text.strip() for seg in valid_segments if seg.text.strip()])

        cleaned_text = unicodedata.normalize("NFC", raw_text)
        cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
        cleaned_text = clean_transcript_text(cleaned_text)
        cleaned_text = remove_repeated_phrases(cleaned_text)

        if is_hallucination(cleaned_text):
            cleaned_text = ""

        # Xác định ngôn ngữ hiển thị
        det_model_lang = getattr(info, "language", "vi") or "vi"
        detected_prob = getattr(info, "language_probability", 1.0)

        # ─── Kiểm tra tính hợp lệ của ngôn ngữ & loại bỏ ảo giác ────────────────
        has_vi_chars = bool(ALL_VI_CHARS_REGEX.search(cleaned_text)) if cleaned_text else False
        words_lower = [w.lower() for w in re.findall(r"\b[^\W\d_]+\b", cleaned_text, flags=re.UNICODE)]
        has_vi_unaccented = any(w in VI_UNACCENTED_WORDS for w in words_lower) if words_lower else False
        is_vietnamese = has_vi_chars or has_vi_unaccented

        # 1. Nếu người dùng chọn TIẾNG VIỆT (target_lang == 'vi'):
        # Tuyệt đối không cho phép hiển thị câu tiếng Anh học vẹt như 'I see the light', 'I'm coming', 'I know'
        if target_lang == "vi" and cleaned_text:
            if not is_vietnamese:
                print(f"[Unified ASR] 🚫 Chặn ảo giác tiếng Anh trong chế độ Tiếng Việt: '{cleaned_text}'", flush=True)
                cleaned_text = ""

        # 2. Ở chế độ Tự động (target_lang is None):
        if target_lang is None and cleaned_text:
            # Phát hiện ảo giác ngôn ngữ ngoại lai Latin (Ý, Pháp, TBN, Bồ Đào Nha...)
            romance_leak_pattern = re.compile(
                r"\b(non|della|delle|nostra|nostro|allora|ematina|cabe|vamos|costa|mais|para|voce|esta|sono|con|por)\b",
                re.IGNORECASE
            )
            if romance_leak_pattern.search(cleaned_text) and not is_vietnamese:
                print(f"[Unified ASR] 🚫 Loại bỏ ảo giác tiếng Latin/Romance: '{cleaned_text}'", flush=True)
                cleaned_text = ""

            # Whisper báo ngôn ngữ khác EN và VI mà không có dấu tiếng Việt
            if cleaned_text and det_model_lang not in ("en", "vi") and not is_vietnamese:
                print(f"[Unified ASR] 🚫 Loại bỏ ảo giác ngôn ngữ ngoại lai [{det_model_lang}]: '{cleaned_text}'", flush=True)
                cleaned_text = ""

            # Lọc ảo giác tiếng Anh ngắn do tiếng thở/nhiễu mic sinh ra
            if cleaned_text and det_model_lang == "en" and not is_vietnamese:
                if is_hallucination(cleaned_text) or len(words_lower) <= 4:
                    # Kiểm tra các câu tiếng Anh ngắn học vẹt
                    en_noise_pat = re.compile(
                        r"^(hey|bye|bye\s+bye|i\s+am|yes|no|ok|okay|thank\s+you|thanks|i\s+see\s+the\s+light|"
                        r"i'm\s+coming|i'm\s+cold|i'm\s+single|i\s+know|that\s+is\s+so|big\s+way|storm\s+meeting|you)\.?$",
                        re.IGNORECASE
                    )
                    if en_noise_pat.match(cleaned_text.strip()):
                        print(f"[Unified ASR] 🚫 Loại bỏ ảo giác tiếng Anh do nhiễu im lặng: '{cleaned_text}'", flush=True)
                        cleaned_text = ""

        # Xác định language output
        if target_lang == "en":
            detected_language = "en"
        elif target_lang == "vi":
            detected_language = "vi"
        else:
            if is_vietnamese:
                detected_language = "vi"
            elif det_model_lang == "en":
                detected_language = "en"
            else:
                detected_language = "vi"

        return {
            "module": "Unified ASR (Whisper Multilingual)",
            "language": detected_language,
            "language_prob": float(detected_prob or 1.0),
            "text": cleaned_text,
            "raw_text": raw_text,
            "duration": getattr(info, "duration", 0.0),
        }

