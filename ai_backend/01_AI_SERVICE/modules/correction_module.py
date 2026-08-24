"""
ClassBridge – Lightweight Phonetic Normalization & Tech Preservation Engine
Chế độ hiện tại: Pure Raw Model Mode (Giữ nguyên bản 100% kết quả từ AI Model).
Toàn bộ các bộ từ điển mẫu và quy tắc sửa từ trước đây đã được comment lại bên dưới để tiện theo dõi và debug.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Dict, List, Pattern, Tuple

_RE_MULTI_SPACES = re.compile(r"\s+")
_RE_INVALID_CHARS = re.compile(r'[\u0060\u00B4\u02CA\u02CB\u02C6\u02DC\^~|]+')

# ==============================================================================
# [ĐÃ COMMENT LẠI ĐỂ DEBUG LỜI GỐC NGUYÊN BẢN CỦA MÔ HÌNH WHISPER]
# ==============================================================================
#
# # 1. Ánh xạ âm vị học chuẩn hóa phát âm vùng miền Bắc - Trung - Nam
# REGIONAL_PHONETIC_REPLACEMENTS: List[Tuple[Pattern, str]] = [
#     # Lẫn L/N (Miền Bắc)
#     (re.compile(r"\b[Nn]ưu ý\b"), "lưu ý"),
#     (re.compile(r"\b[Nn]ập trình\b"), "lập trình"),
#     (re.compile(r"\b[Nn]ực lượng\b"), "lực lượng"),
#     (re.compile(r"\b[Nn]ĩnh vực\b"), "lĩnh vực"),
#     (re.compile(r"\b[Nn]ô(?:\s*|-)?g[ií]c\b", re.IGNORECASE), "lô-gíc"),
#     (re.compile(r"\b[Nn]ý do\b"), "lý do"),
#     (re.compile(r"\b[Nn]ý thuyết\b"), "lý thuyết"),
#     (re.compile(r"\b[Nn]iên kết\b"), "liên kết"),
#     (re.compile(r"\b[Nn]ựa chọn\b"), "lựa chọn"),
#     (re.compile(r"\b[Ll]ói chuyện\b"), "nói chuyện"),
#     (re.compile(r"\b[Ll]ăng lực\b"), "năng lực"),
#     (re.compile(r"\b[Ll]ội dung\b"), "nội dung"),
#     (re.compile(r"\b[Ll]ăm học\b"), "năm học"),
#     (re.compile(r"\b[Ll]ền tảng\b"), "nền tảng"),
#     (re.compile(r"\b[Ll]guyên nhân\b"), "nguyên nhân"),
#
#     # Lẫn V/D (Miền Nam / Miền Tây)
#     (re.compile(r"\b[Dd]ấn đề\b"), "vấn đề"),
#     (re.compile(r"\b[Dd]ề mặt\b"), "về mặt"),
#     (re.compile(r"\b[Dd]ề việc\b"), "về việc"),
#     (re.compile(r"\b[Dd]ề phía\b"), "về phía"),
#     (re.compile(r"\b[Dd]ị trí\b"), "vị trí"),
#     (re.compile(r"\b[Dd]ận hành\b"), "vận hành"),
#     (re.compile(r"\b[Dd]ăn bản\b"), "văn bản"),
#     (re.compile(r"\b[Dd]òng lặp\b"), "vòng lặp"),
#     (re.compile(r"\b[Dd]ô cùng\b"), "vô cùng"),
#     (re.compile(r"\b[Dd]í dụ\b"), "ví dụ"),
#     (re.compile(r"\b[Dd]ai trò\b"), "vai trò"),
#
#     # Biến âm phụ âm cuối / từ ngữ chuyên ngành
#     (re.compile(r"\b[Bb]ắc đầu\b"), "bắt đầu"),
#     (re.compile(r"\b[Cc]hương chình\b"), "chương trình"),
#     (re.compile(r"\b[Ss]ử lí\b"), "xử lý"),
#     (re.compile(r"\b[Xx]ử lí\b"), "xử lý"),
#     (re.compile(r"\b[Ss]ử lý\b"), "xử lý"),
#     (re.compile(r"\b[Gg]iá chì\b"), "giá trị"),
#     (re.compile(r"\b[Gg]iải quyết triệt để\b"), "giải quyết triệt để"),
#     (re.compile(r"\b(rơi vào|tình trạng|trạng thái)\s+bị tắc\b", re.IGNORECASE), r"\1 bế tắc"),
#
#     # Tên ngôn ngữ lập trình & Khoa/Lớp chuyên biệt
#     (re.compile(r"\bngôn ngữ\s+c\b", re.IGNORECASE), "ngôn ngữ C"),
#     (re.compile(r"\bngôn ngữ\s+c\+\+\b", re.IGNORECASE), "ngôn ngữ C++"),
#     (re.compile(r"\bngôn ngữ\s+c#\b", re.IGNORECASE), "ngôn ngữ C#"),
#     (re.compile(r"\bkhoa\s+p\b", re.IGNORECASE), "khoa P"),
#     (re.compile(r"\blớp\s+c\b", re.IGNORECASE), "lớp C"),
#
#     # Sửa lỗi phát âm / nhận diện nhầm ChatGPT
#     (re.compile(r"\b[Cc]h[ea]t\s*T\s*53\b", re.IGNORECASE), "ChatGPT"),
#     (re.compile(r"\b[Cc]h[ea]t\s*T\s*5\.?3\b", re.IGNORECASE), "ChatGPT"),
#     (re.compile(r"\b[Cc]h[ea]t\s*gpt\b", re.IGNORECASE), "ChatGPT"),
#     (re.compile(r"\b[Cc]h[ea]t\s*g\s*p\s*t\b", re.IGNORECASE), "ChatGPT"),
# ]
#
# # 2. Thuật ngữ CNTT & Tên riêng cần viết hoa chuẩn xác
# TECH_TERMS_MAP: Dict[str, str] = {
#     "api": "API", "apis": "APIs", "rest api": "REST API", "restful api": "RESTful API",
#     "graphql": "GraphQL", "docker": "Docker", "kubernetes": "Kubernetes", "k8s": "K8s",
#     "react": "React", "reactjs": "ReactJS", "nextjs": "Next.js", "next.js": "Next.js",
#     "fastapi": "FastAPI", "python": "Python", "javascript": "JavaScript", "typescript": "TypeScript",
#     "golang": "Golang", "rust": "Rust", "java": "Java", "database": "Database", "databases": "Databases",
#     "sql": "SQL", "nosql": "NoSQL", "mongodb": "MongoDB", "postgresql": "PostgreSQL", "postgres": "Postgres",
#     "mysql": "MySQL", "redis": "Redis", "kafka": "Kafka", "rabbitmq": "RabbitMQ", "microservices": "Microservices",
#     "backend": "Backend", "frontend": "Frontend", "fullstack": "Fullstack", "ci/cd": "CI/CD", "cicd": "CI/CD",
#     "devops": "DevOps", "ai": "AI", "llm": "LLM", "chatgpt": "ChatGPT", "gpt-4": "GPT-4", "gpt-3.5": "GPT-3.5",
#     "claude": "Claude", "gemini": "Gemini", "copilot": "Copilot", "deep learning": "Deep Learning",
#     "machine learning": "Machine Learning", "neural network": "Neural Network", "ui": "UI", "ux": "UX",
#     "json": "JSON", "yaml": "YAML", "xml": "XML", "websocket": "WebSocket", "webrtc": "WebRTC",
#     "github": "GitHub", "gitlab": "GitLab", "linux": "Linux", "windows": "Windows", "macos": "macOS",
#     "openai": "OpenAI", "whisper": "Whisper", "classbridge": "ClassBridge", "unit test": "Unit Test",
#     "test case": "Test Case", "pull request": "Pull Request",
# }
#
# _RE_ACOUSTIC_TAGS = re.compile(
#     r"\[(?:music|applause|laughter|silence|whispering|coughing|cheering|screaming|sigh|gasp|crying|snicker|inaudible|breathing|groan|noise|static|âm nhạc|vỗ tay|tiếng cười|tiếng thở|tiếng ho|tiếng ồn)\]"
#     r"|\((?:music|applause|laughter|silence|whispering|coughing|cheering|screaming|sigh|gasp|crying|snicker|inaudible|breathing|groan|noise|static|âm nhạc|vỗ tay|tiếng cười|tiếng thở|tiếng ho|tiếng ồn)\)"
#     r"|[♪♫🎵🎶]+",
#     flags=re.IGNORECASE,
# )
#
# SILENCE_GHOST_PHRASES = {
#     "thank you for watching", "thanks for watching", "thank you for listening", "thanks for listening",
#     "thank you very much", "thank you so much", "subtitles by", "please subscribe", "like and subscribe",
#     "cảm ơn các bạn đã theo dõi", "cảm ơn các bạn đã lắng nghe", "cảm ơn mọi người đã theo dõi",
#     "cảm ơn quý vị và các bạn", "cảm ơn đã xem", "chúc các bạn một ngày tốt lành",
#     "hẹn gặp lại", "chào tạm biệt", "tạm biệt", "đăng ký kênh", "chia sẻ video", "ủng hộ kênh",
# }
# ==============================================================================


class CorrectionModule:
    """
    Pure Raw Model Mode:
    - Trả về 100% lời gốc nguyên bản do mô hình AI sinh ra.
    - Không can thiệp sửa từ hay gán ép từ điển cứng.
    - Chỉ chuẩn hóa Unicode NFC để tránh lỗi vỡ font tiếng Việt.
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
