import re
import sys

for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="backslashreplace")

raw_input = """
Tại sao em nhìn cho thầy này?, Vì sao cái năm họ sử dụng cũng là Đúng rồi, bây giờ thầy nói chuyện này. Vì tinh băng ở đây có mặt nào.

Trong các sản xuất khác đó, còn phải sửa bán tiền không? Nâng hàng đó phải là gia đình của em không? Không. Nó phải là vãng thân. Em không? Đúng không? Vậy em tiền sao tiền được hả? Lòng tin và tín dụng. Thân đó là thứ. Mà Visa buôn bán. Mastercard buôn bán., Nhưng một điều. Mastercard buôn bán như cái đó, nó đảm bảo sự uy tín. Ví dụ bên A.

Các bạn có thể nhận thêm những bản tin của bạn không trốn được. Tức là thành công mặt bạn đúng không? Nhưng đó là vấn đề khi mà tất cả mọi người đều được thực dân ở tại Đà Hà, khu vực.
"""

VIETNAMESE_COMMON_CORRECTIONS = {
    r"\b(nâng|ngâng)\s*hàng\b": "ngân hàng",
    r"\bvãng\s*thân\b": "bản thân",
    r"\b(vi\s*tinh\s*băng|viett?in\s*bank|viettinbank|viêtinbank)\b": "VietinBank",
    r"\b(vietcom\s*bank|việt\s*com\s*bank)\b": "Vietcombank",
    r"\b(techcom\s*bank|tếch\s*com\s*bank)\b": "Techcombank",
    r"\b(master\s*card|mát\s*tơ\s*cạc)\b": "Mastercard",
    r"\b(vi\s*sa)\b": "Visa",
    r"\bcập\s*nhập\b": "cập nhật",
}

def clean_transcript(text: str) -> str:
    result = text
    for pat, rep in VIETNAMESE_COMMON_CORRECTIONS.items():
        result = re.sub(pat, rep, result, flags=re.IGNORECASE)

    # 1. Khử dấu câu kép lặp như '?,', '.,', ',.', '?!', '??'
    result = re.sub(r'([?!\.])[,;:]+', r'\1', result)
    result = re.sub(r'[,;:]+([?!\.])', r'\1', result)
    result = re.sub(r'([,;:])\1+', r'\1', result)
    result = re.sub(r'([.?!])\1+', r'\1', result)

    # 2. Nối câu bị ngắt ngẫu hứng trước các từ liên từ tiếng Việt
    result = re.sub(r'\.\s+(mà|nhưng|và|thì|để|hoặc|chứ|bởi\s+vì|tại\s+vì|cho\s+nên|vậy\s+nên|nếu)\b', r', \1', result, flags=re.IGNORECASE)

    result = re.sub(r'\s+([,.;:!?])', r'\1', result)
    result = re.sub(r'\s+', ' ', result).strip()
    return result

print("=== CLEANED OUTPUT ===")
print(clean_transcript(raw_input))
