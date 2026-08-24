"""
ClassBridge – Auto Punctuation & Code-Switching Preservation Module
"""

from __future__ import annotations

import re

# Regex phát hiện thuật ngữ tiếng Anh trong câu tiếng Việt (Code-switching preservation)
TECH_TERMS = re.compile(
    r"\b(classbridge|api|sql|nosql|java|python|c\+\+|c#|golang|rust|html|css|javascript|typescript|react|next\.js|vite|"
    r"software|testing|unit test|test case|bug|debug|framework|backend|frontend|fullstack|"
    r"boundary value|equivalence partitioning|black-box|white-box|scrum|sprint|"
    r"agile|database|primary key|foreign key|rest api|graphql|docker|kubernetes|ci/cd|"
    r"machine learning|deep learning|ai|llm|prompt|model|token|dataset|pipeline|"
    r"websocket|webrtc|microservices|architecture|server|client|cloud|devops|"
    r"github|gitlab|linux|windows|macos|openai|whisper|fastapi|django|flask|nodejs|node\.js|"
    r"mongodb|postgresql|postgres|mysql|redis|kafka|rabbitmq|json|yaml|xml)\b",
    flags=re.IGNORECASE,
)


# Map standard capitalization for academic / tech acronyms
TECH_ACRONYMS = {
    "api": "API",
    "sql": "SQL",
    "nosql": "NoSQL",
    "html": "HTML",
    "css": "CSS",
    "ai": "AI",
    "llm": "LLM",
    "ci/cd": "CI/CD",
    "ui": "UI",
    "ux": "UX",
    "rest api": "REST API",
    "graphql": "GraphQL",
    "jwt": "JWT",
    "http": "HTTP",
    "https": "HTTPS",
    "cpu": "CPU",
    "gpu": "GPU",
    "ram": "RAM",
    "json": "JSON",
    "yaml": "YAML",
    "xml": "XML",
    "webrtc": "WebRTC",
}

TECH_PROPER_NOUNS = {
    "classbridge": "ClassBridge",
    "python": "Python",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "react": "React",
    "next.js": "Next.js",
    "vite": "Vite",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "golang": "Golang",
    "rust": "Rust",
    "java": "Java",
    "github": "GitHub",
    "gitlab": "GitLab",
    "linux": "Linux",
    "windows": "Windows",
    "macos": "macOS",
    "openai": "OpenAI",
    "whisper": "Whisper",
    "mongodb": "MongoDB",
    "postgresql": "PostgreSQL",
    "postgres": "Postgres",
    "mysql": "MySQL",
    "redis": "Redis",
    "kafka": "Kafka",
    "rabbitmq": "RabbitMQ",
    "websocket": "WebSocket",
    "microservices": "Microservices",
    "backend": "Backend",
    "frontend": "Frontend",
    "devops": "DevOps",
}


def preserve_code_switching(text: str, language: str) -> str:
    """
    Đảm bảo các thuật ngữ chuyên ngành CNTT/AI được định dạng chuẩn xác, viết hoa đúng quy cách.
    """
    if not text:
        return text

    def _capitalize_match(match: re.Match) -> str:
        term = match.group(0)
        low = term.lower()
        if low in TECH_ACRONYMS:
            return TECH_ACRONYMS[low]
        if low in TECH_PROPER_NOUNS:
            return TECH_PROPER_NOUNS[low]
        return term

    return TECH_TERMS.sub(_capitalize_match, text)


CLAUSE_BOUNDARY_PATTERNS = re.compile(
    r"\b(because|so|but|and|or|however|although|therefore|meanwhile|after|before|when|while|if|that|which|who|then|also|so that|in order to|as a result|vì|nên|nhưng|mà|cho nên|bởi vì|tuy nhiên|mặc dù|sau khi|trước khi|khi|nếu|thì)\b",
    flags=re.IGNORECASE,
)


def smart_punctuate_stream(text: str, language: str = "en") -> str:
    """
    Tự động chèn dấu phẩy và chấm câu vào luồng nói liên tục, ngắt câu tự nhiên theo liên từ và nhịp nói.
    Tránh ngắt dấu chấm quá sớm làm đứt đoạn cụm danh từ hoặc câu đơn bình thường.
    """
    if not text:
        return ""

    words = text.strip().split()
    if not words:
        return ""

    # Viết hoa từ đầu tiên
    words[0] = words[0].capitalize()

    punctuated_words = []
    word_count_since_period = 0

    for i, w in enumerate(words):
        clean_w = w
        word_count_since_period += 1

        is_connector = bool(CLAUSE_BOUNDARY_PATTERNS.match(clean_w.strip(",.!?")))
        if is_connector and word_count_since_period >= 6 and i < len(words) - 1:
            # Ngắt chấm nếu vế trước đã rất dài (>= 18 từ)
            if word_count_since_period >= 18:
                punctuated_words.append(".")
                word_count_since_period = 0
                clean_w = clean_w.capitalize()
            elif not clean_w.startswith(","):
                clean_w = ", " + clean_w
        elif word_count_since_period >= 28 and i < len(words) - 1:
            clean_w = clean_w + "."
            word_count_since_period = 0
            if i + 1 < len(words):
                words[i + 1] = words[i + 1].capitalize()

        punctuated_words.append(clean_w)

    result = " ".join(punctuated_words)
    result = re.sub(r"\s+([,.;:!?])", r"\1", result)
    result = re.sub(r"\.\s*\.", ".", result)

    if len(words) >= 3 and result[-1] not in ".!?":
        result += "."

    return result


QUESTION_START_RE = re.compile(
    r"^(what|why|how|where|when|who|can|is|are|do|does|did|thầy|cô|sao|gì|bao nhiêu|chạy như thế nào)\b",
    flags=re.IGNORECASE,
)
QUESTION_END_RE = re.compile(
    r"(không ạ|không thầy|không cô|nhỉ|hả|như thế nào)\?*$",
    flags=re.IGNORECASE,
)


VIETNAMESE_REDUPLICATIONS = {
    "chi chi", "gì gì", "từ từ", "dần dần", "ngày ngày", "người người", "ai ai", "sao sao",
    "nhiều nhiều", "ít ít", "nhanh nhanh", "chậm chậm", "lâu lâu", "rõ rõ", "đâu đâu", "nào nào",
    "khác khác", "xem xem", "nghĩ nghĩ", "nói nói", "cười cười", "học học", "làm làm", "chơi chơi",
    "đo đỏ", "nho nhỏ", "xanh xanh", "trắng trắng", "đen đen", "vàng vàng", "sớm sớm", "muộn muộn",
    "khẽ khẽ", "nhè nhẹ", "vừa vừa", "từng từng", "mỗi mỗi", "đôi đôi", "đầy đầy", "vơi vơi"
}


def remove_repetitions(text: str) -> str:
    """
    Loại bỏ từ và cụm từ (1-6 từ) bị lặp lại liên tiếp do Whisper STT stuttering / hallucination 
    hoặc MarianMT translation repeat.
    Ví dụ:
        'Giáo trình công nghệ, phần mềm, phần mềm.' -> 'Giáo trình công nghệ, phần mềm.'
        'Technology, software, software.' -> 'Technology, software.'
        'Tôi tôi tôi muốn' -> 'Tôi muốn'
    """
    if not text or not text.strip():
        return text

    def _replace_repeated(match: re.Match) -> str:
        full_match = match.group(0)
        first_phrase = match.group(1)
        trimmed = first_phrase.strip().lower()
        # Nếu là từ láy tiếng Việt chỉ lặp 2 lần (ví dụ "chi chi", "từ từ")
        if " " not in trimmed:
            two_words = f"{trimmed} {trimmed}"
            occurrences = len(re.findall(rf"\b{re.escape(trimmed)}\b", full_match, flags=re.IGNORECASE))
            if occurrences <= 2 and two_words in VIETNAMESE_REDUPLICATIONS:
                return full_match

        # Bắt giữ dấu chấm/câu ở cuối chuỗi lặp nếu có (ví dụ: '.', '!', '?')
        m_punct = re.search(r"([.,!?;:]+)\s*$", full_match)
        trailing_punct = m_punct.group(1) if m_punct else ""
        return f"{first_phrase}{trailing_punct}"

    # Regex bắt các cụm từ / câu lặp lại liên tiếp do Whisper STT hoặc MarianMT lặp
    pattern = re.compile(
        r"\b(\w+(?:[\s'\"\\-]+\w+){0,25})\b(?:[\s,;:–—\-]+(?:\1\b))+([.,!?;:]*)",
        flags=re.IGNORECASE | re.UNICODE,
    )


    # Chạy lặp tối đa 4 lần để xử lý các tầng lặp lồng nhau nếu có
    prev = ""
    curr = text
    for _ in range(4):
        if prev == curr:
            break
        prev = curr
        curr = pattern.sub(_replace_repeated, curr)

    # Xử lý các dấu câu thừa sau khi lặp (ví dụ: ", ." -> ".")
    curr = re.sub(r"[\s,;:–—\-]+\.", ".", curr)
    curr = re.sub(r",\s*,", ",", curr)
    return curr.strip()



def format_auto_punctuation(text: str, language: str) -> str:
    """
    Tự động chuẩn hóa dấu câu, khử lặp từ và viết hoa chữ cái đầu cho final transcript.
    """
    if not text:
        return ""

    text = remove_repetitions(text)
    cleaned = smart_punctuate_stream(text, language)
    cleaned = preserve_code_switching(cleaned, language)

    # Viết hoa chữ cái đầu tiên
    if len(cleaned) > 0 and cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]

    # smart_punctuate_stream có thể đã thêm dấu chấm, vì vậy phải kiểm tra
    # dạng câu hỏi trên nội dung chưa có dấu kết thúc. Nếu không, các hậu tố
    # như "như thế nào." sẽ không khớp QUESTION_END_RE.
    if len(cleaned.split()) >= 3:
        question_candidate = cleaned.rstrip(".!?:;").rstrip()
        is_question = bool(
            QUESTION_START_RE.search(question_candidate)
            or QUESTION_END_RE.search(question_candidate)
        )
        if is_question and cleaned.endswith("."):
            cleaned = cleaned[:-1] + "?"
        elif cleaned[-1] not in ".!?:;":
            cleaned += "?" if is_question else "."

    return cleaned

