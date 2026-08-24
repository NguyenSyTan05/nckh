import re
import unicodedata
import sys

for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="backslashreplace")

text1 = "có dụng gọi là xóa đi yêu dịch vì cái nhã`m đó cũng tính là một yêu dịch. Đúno rô`i đấ y. Vậy nên sẽ tính hành và sau đây sẽ đi bài bóng này. | Để không tìm hiểu, để không cứ tắ t, đúng không? Để không bỏ lỡ. Thì tấ t cả giao dịch, dù người đó bị xóa đi thì giao dịch cũng phải được lại. Ví dụ là em đi phim, mình đi máy, mình nói. Thường khi nó sẽ ghi ngu trâ`m thì nó sẽ cập nhập đế n một sản phẩm gì đó thêm vô đúng không? Chứ nó không có dụng gọi là xóa nhiề u gì Vì kích nhập nó cũng tính là một cái gì?"
text2 = "dùng một. Thêm một bảng, hoặc người Còn, nế u, mà anh xóa một phát là cái bóng khóc thôi vậy. Được rô`i này, drop thì có cầ n thấ y nhiệt đó. À, drop không nhiệt đâu. Không, drop đấ y. | Hãy subscribe cho kênh Ghiề n Mì Gõ Để không bỏ lỡ những video hấ p dẫn"

def clean_vietnamese_text_and_hallucinations(text: str) -> str:
    if not text:
        return ""
    
    # 1. Chuẩn hóa backtick (`) và dấu phụ tách rời: nhã`m -> nhằm/nhảm, rô`i -> rồi, trâ`m -> trầm
    text = re.sub(r'([a-zA-Z\u00C0-\u1EF9]+)[`\']([a-zA-Z\u00C0-\u1EF9]+)', r'\1\2', text)
    text = text.replace("`", "")

    # 2. Nối các âm tiết tiếng Việt bị gãy dấu thanh do space giữa nguyên âm có dấu và phụ âm cuối
    # Ví dụ: "đế n" -> "đến", "tấ t" -> "tất", "tắ t" -> "tắt", "nế u" -> "nếu", "cầ n" -> "cần", "thấ y" -> "thấy", "đấ y" -> "đấy", "hấ p" -> "hấp", "nhiề u" -> "nhiều", "rô i" -> "rồi", "Ghiề n" -> "Ghiền"
    vn_vowels = r"[a-zA-Z\u00C0-\u1EF9]*[àáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵĐđ]"
    vn_endings = r"[cnptumy]|ch|ng|nh"
    text = re.sub(rf"\b({vn_vowels})\s+({vn_endings})\b", r"\1\2", text, flags=re.IGNORECASE)
    text = unicodedata.normalize("NFC", text)

    # 3. Xóa triệt để các hallucination spam YouTube / Whisper artifacts dù nằm ở đầu, giữa hay cuối câu
    hallucination_patterns = [
        r"(?:\|\s*)?(?:Hãy\s+)?(?:like\s+và\s+)?(?:subscribe|subtitles\s+by|thanks?\s+for\s+watching|đăng\s+ký\s+kênh|ủng\s+hộ\s+kênh|bấm\s+chuông\s+theo\s+dõi|chia\s+sẻ\s+video|theo\s+dõi\s+kênh)(?:[\s\w\d_]*(?:Ghiền\s+Mì\s+Gõ|kênh|video|hấp\s+dẫn|tiếp\s+theo|bên\s+dưới|nhé|nha|ạ))?[.,!?]*",
        r"(?:\|\s*)?Để\s+không\s+bỏ\s+lỡ\s+(?:những\s+)?(?:video|tập|phim|nội\s+dung)[\s\w\d_]*(?:hấp\s+dẫn|tiếp\s+theo|mới\s+nhất)?[.,!?]*",
        r"(?:\|\s*)?(?:Cảm\s+ơn|Chúc)\s+(?:các\s+)?(?:bạn|quý\s+vị|mọi\s+người)\s+đã\s+(?:theo\s+dõi|xem|lắng\s+nghe)[\s\w\d_]*[.,!?]*",
        r"(?:phim\s+sương|học\s+vệ\s+luật|quay\s+man|đoại\s+đất|bác\s+sân|quét\s+trong\s+thái|đôi\s+vào\s+cao\s+đường)",
    ]
    for pat in hallucination_patterns:
        text = re.sub(pat, "", text, flags=re.IGNORECASE)

    # 4. Chuẩn hóa khoảng trắng và dấu câu
    text = re.sub(r"\s*\|\s*", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    
    return text

print("--- TEXT 1 BEFORE ---")
print(text1)
print("\n--- TEXT 1 AFTER ---")
print(clean_vietnamese_text_and_hallucinations(text1))

print("\n" + "="*50)
print("--- TEXT 2 BEFORE ---")
print(text2)
print("\n--- TEXT 2 AFTER ---")
print(clean_vietnamese_text_and_hallucinations(text2))
