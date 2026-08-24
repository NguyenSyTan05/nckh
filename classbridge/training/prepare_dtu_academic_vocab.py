"""
ClassBridge – DTU Academic Vocabulary Dataset Builder
# pyrefly: ignore-all-errors

Tạo bộ từ vựng học thuật DTU cho việc:
1. Inject vào Whisper decoder (initial_prompt) để tăng độ chính xác thuật ngữ
2. Tạo test set câu hỏi sinh viên cho Semantic Question Clustering benchmark

Bộ từ vựng bao gồm:
  - Thuật ngữ CNTT, AI, Khoa học máy tính (EN + VI)
  - Tên môn học tại khoa CNTT DTU
  - Tên giảng viên phổ biến (anonymized)
  - Thuật ngữ học thuật chung trong giảng dạy ĐH

Output:
  data/dtu_vocab.json          – Từ vựng cho Whisper prompt injection
  data/dtu_questions_test.jsonl – Test set câu hỏi cho clustering

Cách chạy:
    python prepare_dtu_academic_vocab.py
    python prepare_dtu_academic_vocab.py --output-dir ../data
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Virtualenv injection
_VENV = Path(__file__).resolve().parent.parent / "backend" / "ai-service" / ".venv" / "Lib" / "site-packages"
if _VENV.exists() and str(_VENV) not in sys.path:
    sys.path.insert(0, str(_VENV))

# ===========================================================================
# DTU Academic Vocabulary
# ===========================================================================

DTU_VOCABULARY: dict[str, list[str]] = {
    # ── Môn học CNTT – DTU ────────────────────────────────────────────────
    "courses_vi": [
        "Lập trình hướng đối tượng",
        "Cấu trúc dữ liệu và giải thuật",
        "Cơ sở dữ liệu",
        "Mạng máy tính",
        "Hệ điều hành",
        "Kỹ thuật phần mềm",
        "Trí tuệ nhân tạo",
        "Học máy",
        "Thị giác máy tính",
        "Xử lý ngôn ngữ tự nhiên",
        "An toàn thông tin",
        "Điện toán đám mây",
        "Phát triển ứng dụng di động",
        "Kiểm thử phần mềm",
        "Quản trị dự án phần mềm",
        "Phân tích thiết kế hệ thống",
        "Lập trình web",
        "Cơ sở hạ tầng CNTT",
        "Big Data và phân tích dữ liệu",
        "DevOps và CI/CD",
    ],
    "courses_en": [
        "Object-Oriented Programming",
        "Data Structures and Algorithms",
        "Database Management Systems",
        "Computer Networks",
        "Operating Systems",
        "Software Engineering",
        "Artificial Intelligence",
        "Machine Learning",
        "Computer Vision",
        "Natural Language Processing",
        "Information Security",
        "Cloud Computing",
        "Mobile Application Development",
        "Software Testing",
        "Software Project Management",
        "Systems Analysis and Design",
        "Web Development",
        "IT Infrastructure",
        "Big Data Analytics",
        "DevOps and CI/CD",
    ],

    # ── Thuật ngữ AI / ML ─────────────────────────────────────────────────
    "ai_terms_vi": [
        "mô hình học máy", "mạng nơ-ron nhân tạo", "học sâu", "học tăng cường",
        "học có giám sát", "học không giám sát", "dữ liệu huấn luyện", "tập kiểm tra",
        "hàm mất mát", "độ chính xác", "ma trận nhầm lẫn", "độ nhạy", "độ đặc hiệu",
        "độ phức tạp tính toán", "thuật toán gradient descent", "lan truyền ngược",
        "hàm kích hoạt", "phép hợp tích", "chuẩn hóa dữ liệu", "chính quy hóa",
        "dropout", "batch normalization", "transformer", "attention mechanism",
        "vector nhúng", "biểu diễn véc-tơ", "phân cụm", "phân loại", "hồi quy",
        "cây quyết định", "rừng ngẫu nhiên", "máy vectơ hỗ trợ", "k láng giềng gần nhất",
        "mô hình ngôn ngữ lớn", "tạo sinh văn bản", "nhận diện giọng nói",
        "xử lý ảnh", "phát hiện đối tượng", "phân đoạn ngữ nghĩa",
    ],
    "ai_terms_en": [
        "machine learning model", "artificial neural network", "deep learning",
        "reinforcement learning", "supervised learning", "unsupervised learning",
        "training dataset", "test set", "loss function", "accuracy",
        "confusion matrix", "sensitivity", "specificity", "computational complexity",
        "gradient descent algorithm", "backpropagation", "activation function",
        "convolution", "data normalization", "regularization",
        "dropout", "batch normalization", "transformer", "attention mechanism",
        "word embedding", "vector representation", "clustering", "classification",
        "regression", "decision tree", "random forest", "support vector machine",
        "k-nearest neighbors", "large language model", "text generation",
        "speech recognition", "image processing", "object detection", "semantic segmentation",
    ],

    # ── Thuật ngữ Lập trình ────────────────────────────────────────────────
    "programming_terms_vi": [
        "lập trình hướng đối tượng", "kế thừa", "đa hình", "đóng gói", "trừu tượng",
        "giao diện", "lớp trừu tượng", "con trỏ", "tham chiếu", "bộ nhớ heap",
        "bộ nhớ stack", "thu dọn bộ nhớ", "đa luồng", "đồng bộ hóa",
        "thiết kế mẫu", "mẫu singleton", "mẫu observer", "mẫu factory",
        "kiến trúc MVC", "kiến trúc vi dịch vụ", "API RESTful", "giao thức HTTP",
        "cơ sở dữ liệu quan hệ", "cơ sở dữ liệu NoSQL", "truy vấn SQL",
        "chỉ mục", "khóa ngoại", "chuẩn hóa bảng", "giao tác", "xung đột đồng thời",
        "kiểm thử đơn vị", "kiểm thử tích hợp", "kiểm thử hệ thống",
        "tích hợp liên tục", "triển khai liên tục", "container Docker",
        "Kubernetes", "cân bằng tải", "caching", "hàng đợi tin nhắn",
    ],
    "programming_terms_en": [
        "object-oriented programming", "inheritance", "polymorphism", "encapsulation",
        "abstraction", "interface", "abstract class", "pointer", "reference",
        "heap memory", "stack memory", "garbage collection", "multithreading",
        "synchronization", "design pattern", "singleton pattern", "observer pattern",
        "factory pattern", "MVC architecture", "microservices architecture",
        "RESTful API", "HTTP protocol", "relational database", "NoSQL database",
        "SQL query", "index", "foreign key", "table normalization", "transaction",
        "concurrency conflict", "unit testing", "integration testing", "system testing",
        "continuous integration", "continuous deployment", "Docker container",
        "Kubernetes", "load balancing", "caching", "message queue",
    ],

    # ── Thuật ngữ học thuật chung ─────────────────────────────────────────
    "academic_vi": [
        "bài giảng", "bài tập lớn", "đồ án", "luận văn", "khóa luận tốt nghiệp",
        "kiểm tra giữa kỳ", "thi cuối kỳ", "điểm danh", "nhóm học tập",
        "thảo luận", "trình bày", "báo cáo", "nhận xét", "phản hồi",
        "câu hỏi", "giải thích", "ví dụ minh họa", "bài toán thực tế",
        "ứng dụng thực tiễn", "nghiên cứu khoa học", "công bố khoa học",
        "hội thảo", "hội nghị", "tài liệu tham khảo", "trích dẫn",
        "phương pháp nghiên cứu", "thực nghiệm", "kết quả", "kết luận",
    ],
    "academic_en": [
        "lecture", "assignment", "project", "thesis", "capstone project",
        "midterm exam", "final exam", "attendance", "study group",
        "discussion", "presentation", "report", "feedback", "review",
        "question", "explanation", "example", "real-world problem",
        "practical application", "scientific research", "publication",
        "workshop", "conference", "reference material", "citation",
        "research methodology", "experiment", "result", "conclusion",
    ],

    # ── Tên trường / khoa / đơn vị DTU ────────────────────────────────────
    "dtu_entities": [
        "Đại học Duy Tân", "DTU", "Duy Tan University",
        "Khoa Công nghệ thông tin", "Faculty of Information Technology",
        "Khoa Điện - Điện tử", "Khoa Kỹ thuật", "Khoa Kinh tế",
        "Viện nghiên cứu AI", "Trung tâm AI",
        "ClassBridge", "Foreign DTU", "DTU International",
        "Đà Nẵng", "Da Nang", "Central Vietnam",
    ],
}


# ===========================================================================
# Sample Questions for Clustering Test
# ===========================================================================

DTU_SAMPLE_QUESTIONS: list[dict] = [
    # === Cluster: Machine Learning ===
    {"id": "q001", "text": "What is machine learning?", "cluster": "ml_definition"},
    {"id": "q002", "text": "Can you explain machine learning?", "cluster": "ml_definition"},
    {"id": "q003", "text": "Máy học là gì vậy thầy?", "cluster": "ml_definition"},
    {"id": "q004", "text": "Em chưa hiểu machine learning, thầy giải thích lại được không?", "cluster": "ml_definition"},
    {"id": "q005", "text": "Machine learning khác gì với AI thông thường?", "cluster": "ml_definition"},

    # === Cluster: Deep Learning ===
    {"id": "q006", "text": "What is deep learning?", "cluster": "dl_definition"},
    {"id": "q007", "text": "How does deep learning differ from machine learning?", "cluster": "dl_definition"},
    {"id": "q008", "text": "Deep learning là gì và hoạt động như thế nào?", "cluster": "dl_definition"},
    {"id": "q009", "text": "Thầy ơi, deep learning và machine learning giống hay khác nhau?", "cluster": "dl_definition"},

    # === Cluster: Exam / Assessment ===
    {"id": "q010", "text": "When is the midterm exam?", "cluster": "exam_date"},
    {"id": "q011", "text": "Khi nào thi giữa kỳ thầy ơi?", "cluster": "exam_date"},
    {"id": "q012", "text": "Lịch thi giữa kỳ là khi nào?", "cluster": "exam_date"},
    {"id": "q013", "text": "Midterm exam schedule?", "cluster": "exam_date"},
    {"id": "q014", "text": "Thầy cho em hỏi ngày thi giữa kỳ ạ?", "cluster": "exam_date"},

    # === Cluster: Assignment Requirements ===
    {"id": "q015", "text": "What are the requirements for the final project?", "cluster": "project_requirements"},
    {"id": "q016", "text": "Can you clarify the project requirements?", "cluster": "project_requirements"},
    {"id": "q017", "text": "Yêu cầu đồ án là gì thầy?", "cluster": "project_requirements"},
    {"id": "q018", "text": "Đồ án cuối kỳ cần làm những gì ạ?", "cluster": "project_requirements"},
    {"id": "q019", "text": "Em không hiểu yêu cầu bài tập lớn, thầy giải thích được không?", "cluster": "project_requirements"},

    # === Cluster: Gradient Descent ===
    {"id": "q020", "text": "Can you explain gradient descent?", "cluster": "gradient_descent"},
    {"id": "q021", "text": "How does gradient descent work?", "cluster": "gradient_descent"},
    {"id": "q022", "text": "Gradient descent hoạt động như thế nào?", "cluster": "gradient_descent"},
    {"id": "q023", "text": "Thuật toán gradient descent là gì?", "cluster": "gradient_descent"},

    # === Cluster: Neural Networks ===
    {"id": "q024", "text": "What is a neural network?", "cluster": "neural_network"},
    {"id": "q025", "text": "How do neural networks work?", "cluster": "neural_network"},
    {"id": "q026", "text": "Mạng nơ-ron nhân tạo là gì?", "cluster": "neural_network"},
    {"id": "q027", "text": "Thầy giải thích mạng nơ-ron cho em hiểu với ạ", "cluster": "neural_network"},

    # === Singletons (unrelated questions) ===
    {"id": "q028", "text": "How do I install Python on Windows?", "cluster": "singleton_python_install"},
    {"id": "q029", "text": "What is the attendance policy?", "cluster": "singleton_attendance"},
    {"id": "q030", "text": "Thầy có thể recommend sách hay về AI không?", "cluster": "singleton_book_rec"},
    {"id": "q031", "text": "Where can I find the lecture slides?", "cluster": "singleton_slides"},
    {"id": "q032", "text": "Is the project individual or group work?", "cluster": "singleton_group_work"},
]


# ===========================================================================
# Build Whisper Prompt Injection String
# ===========================================================================

def build_whisper_prompt(language: str = "vi", max_length: int = 220) -> str:
    """
    Tạo chuỗi prompt cho Whisper initial_prompt để boost accuracy thuật ngữ.
    
    Args:
        language: 'vi', 'en', hoặc 'both'
        max_length: Giới hạn ký tự (Whisper tokenizer limit ~224 tokens)
    
    Returns:
        Chuỗi prompt ngắn gọn chứa từ khóa học thuật DTU
    """
    terms: list[str] = []

    if language in ("vi", "both"):
        terms.extend(DTU_VOCABULARY["ai_terms_vi"][:15])
        terms.extend(DTU_VOCABULARY["academic_vi"][:10])
        terms.extend(DTU_VOCABULARY["dtu_entities"][:5])

    if language in ("en", "both"):
        terms.extend(DTU_VOCABULARY["ai_terms_en"][:15])
        terms.extend(DTU_VOCABULARY["academic_en"][:5])

    # Ghép các thuật ngữ, cắt theo max_length
    prompt = ", ".join(terms)
    if len(prompt) > max_length:
        prompt = prompt[:max_length].rsplit(",", 1)[0]
    return prompt.strip()


# ===========================================================================
# Output builders
# ===========================================================================

def build_vocab_json(output_dir: Path) -> Path:
    """Xuất từ vựng ra JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "dtu_vocab.json"

    vocab_data = {
        "version": "1.0",
        "description": "DTU Academic Vocabulary for ClassBridge Whisper Prompt Injection",
        "whisper_prompt_vi": build_whisper_prompt("vi"),
        "whisper_prompt_en": build_whisper_prompt("en"),
        "whisper_prompt_both": build_whisper_prompt("both"),
        "vocabulary": DTU_VOCABULARY,
        "stats": {
            key: len(terms)
            for key, terms in DTU_VOCABULARY.items()
        },
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(vocab_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Đã xuất từ vựng: {output_path}")
    total_terms = sum(len(v) for v in DTU_VOCABULARY.values())
    print(f"   Tổng số thuật ngữ: {total_terms}")
    print(f"   Whisper prompt VI ({len(vocab_data['whisper_prompt_vi'])} chars): {vocab_data['whisper_prompt_vi'][:80]}...")
    return output_path


def build_question_test_set(output_dir: Path) -> Path:
    """Xuất bộ câu hỏi test cho Semantic Clustering."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "dtu_questions_test.jsonl"

    with open(output_path, "w", encoding="utf-8") as f:
        for q in DTU_SAMPLE_QUESTIONS:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")

    # Thống kê
    clusters: dict[str, list] = {}
    for q in DTU_SAMPLE_QUESTIONS:
        clusters.setdefault(q["cluster"], []).append(q["id"])

    print(f"\n✅ Đã xuất bộ câu hỏi test: {output_path}")
    print(f"   Tổng số câu hỏi : {len(DTU_SAMPLE_QUESTIONS)}")
    print(f"   Số nhóm thực sự : {len(clusters)}")
    print(f"   Nhóm câu hỏi:")
    for cluster, ids in sorted(clusters.items()):
        print(f"     • {cluster}: {len(ids)} câu ({', '.join(ids[:3])}{'...' if len(ids) > 3 else ''})")
    return output_path


def run_clustering_test(output_dir: Path) -> None:
    """Chạy clustering test và so sánh với ground truth."""
    try:
        from question_clustering import QuestionClusteringEngine  # type: ignore[import]
    except ImportError:
        print("⚠️  Không tìm thấy question_clustering.py – bỏ qua test clustering")
        return

    print("\n" + "=" * 65)
    print("  🧪 Chạy Clustering Test với dữ liệu DTU...")
    print("=" * 65)

    engine = QuestionClusteringEngine(similarity_threshold=0.72)

    for q in DTU_SAMPLE_QUESTIONS:
        engine.add_question("dtu-test", q["id"], q["text"])

    result = engine.get_clusters("dtu-test")
    if result is None:
        print("❌ Không có kết quả clustering")
        return

    # Ground truth: 9 clusters
    true_cluster_count = len({q["cluster"] for q in DTU_SAMPLE_QUESTIONS})
    print(f"\n📊 Kết quả:")
    print(f"  Ground truth clusters : {true_cluster_count}")
    print(f"  Predicted clusters    : {result.total_clusters}")
    print(f"  Duplicate reduced     : {result.duplicate_questions_reduced}")
    print(f"  Processing time       : {result.processing_time_ms}ms")

    accuracy = 1.0 - abs(result.total_clusters - true_cluster_count) / true_cluster_count
    print(f"  Cluster count accuracy: {accuracy:.0%}")
    print()
    for cluster in result.clusters[:5]:
        print(f"  [Nhóm {cluster.cluster_id}] Representative: \"{cluster.representative}\"")
        print(f"           {len(cluster.questions)} câu, similarity={cluster.avg_similarity:.2%}")
    print("=" * 65)


# ===========================================================================
# CLI
# ===========================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="ClassBridge DTU Academic Vocabulary Builder"
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parent.parent / "data"),
        help="Thư mục xuất dữ liệu",
    )
    parser.add_argument(
        "--run-test",
        action="store_true",
        help="Chạy clustering test sau khi tạo dataset",
    )
    args = parser.parse_args()
    output_dir = Path(args.output_dir)

    print("\n" + "=" * 65)
    print("  ClassBridge – DTU Academic Vocabulary Builder")
    print("=" * 65)

    build_vocab_json(output_dir)
    build_question_test_set(output_dir)

    if args.run_test:
        # Cần question_clustering.py trong Python path
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend" / "ai-service"))
        run_clustering_test(output_dir)

    print("\n✅ Hoàn tất! Sử dụng:")
    print(f"   Whisper prompt: data/dtu_vocab.json → 'whisper_prompt_vi'")
    print(f"   Test set      : data/dtu_questions_test.jsonl")


if __name__ == "__main__":
    main()
