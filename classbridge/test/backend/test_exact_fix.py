import re
import unicodedata
import sys

for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="backslashreplace")

raw = "Kính chồ`ng em có cảm nhận như không phải là dịu vinh dà, phải là dịu in. Hãy subscribe cho kênh Ghiề`n Mì Gõ Để không bỏ lỡ những video hấ´p dẫn|"

def clean_all(text: str) -> str:
    if not text:
        return ""

    # 1. Xóa bỏ tất cả các loại dấu nháy / backtick / accent kẹp trong từ hoặc đứng rời
    # ` (U+0060), ' (U+0027), ´ (U+00B4), ˊ (U+02CA), ˋ (U+02CB), ˆ (U+02C6), ˜ (U+02DC), ^, ~
    text = re.sub(r'[\u0060\u0027\u00B4\u02CA\u02CB\u02C6\u02DC\^~]+', '', text)

    # 2. Xóa combining diacritics đứng rời
    text = re.sub(r'[\u0300-\u036f\u1dc0-\u1dff\u02b0-\u02ff]', '', text)

    # 3. Nối các âm tiết tiếng Việt bị gãy phụ âm cuối
    vn_vowels = r"[a-zA-Z\u00C0-\u1EF9]*[àáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵĐđ]"
    vn_endings = r"ch|ng|nh|[cnptumy]"
    text = re.sub(rf"\b({vn_vowels})\s+({vn_endings})\b", r"\1\2", text, flags=re.IGNORECASE)

    # 4. Chuẩn hóa NFC
    text = unicodedata.normalize("NFC", text)

    # 5. Xóa triệt để các câu YouTube Spam & Hallucination
    hallucination_patterns = [
        r"(?:\|\s*)?(?:Hãy\s+|Vui\s+lòng\s+|Đừng\s+quên\s+)?(?:like\s+và\s+)?(?:subscribe|subtitles?\s+by|thanks?\s+for\s+watching|đăng\s+ký\s+kênh|ủng\s+hộ\s+kênh|bấm\s+chuông\s+theo\s+dõi|chia\s+sẻ\s+video|theo\s+dõi\s+kênh)(?:[\s\w\d_]*(?:Ghiền\s+Mì\s+Gõ|kênh|video|hấp\s+dẫn|tiếp\s+theo|bên\s+dưới|nhé|nha|ạ))?[.,!?]*",
        r"(?:\|\s*)?Để\s+không\s+bỏ\s+lỡ[\s\w\d_]*(?:hấp\s+dẫn|tiếp\s+theo|mới\s+nhất)?[.,!?]*",
        r"(?:\|\s*)?(?:Cảm\s+ơn|Chúc)\s+(?:các\s+)?(?:bạn|quý\s+vị|mọi\s+người)\s+đã\s+(?:theo\s+dõi|xem|lắng\s+nghe)[\s\w\d_]*[.,!?]*",
        r"(?:Ghiền\s+Mì\s+Gõ|FAPtv|phim\s+sương|học\s+vệ\s+luật|quay\s+man|đoại\s+đất|bác\s+sân|quét\s+trong\s+thái|đôi\s+vào\s+cao\s+đường)",
    ]
    for pat in hallucination_patterns:
        text = re.sub(pat, "", text, flags=re.IGNORECASE)

    # 6. Dọn dẹp khoảng trắng, dấu gạch đứng | và dấu câu kép
    text = re.sub(r'([?!\.])[,;:]+', r'\1', text)
    text = re.sub(r'[,;:]+([?!\.])', r'\1', text)
    text = re.sub(r'([,;:])\1+', r'\1', text)
    text = re.sub(r'([.?!])\1+', r'\1', text)
    text = re.sub(r"\s*\|\s*", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    return text

print("BEFORE:")
print(raw)
print("\nAFTER:")
print(clean_all(raw))
