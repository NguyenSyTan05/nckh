# -*- coding: utf-8 -*-
"""
Định nghĩa tọa độ chuẩn C4 Model (theo đúng mẫu c4model.com trên slide bài giảng):
- Kích thước khối gọn gàng (w=260, h=145), khoảng cách thoáng rộng (160px-200px)
- Hình dáng trực quan chuẩn C4:
  + person: Hình người C4 (Đầu tròn + Thân bo góc, viền xanh lá đậm #2e6b4e)
  + ui: Khung trình duyệt Web (Thanh tiêu đề có 3 chấm tròn + thanh URL, viền xanh dương #2b6cb0)
  + backend / comp: Khung dịch vụ có biểu tượng terminal ">_" ở góc trái trên (viền xanh dương #2b6cb0)
  + db: Hình trụ Database / Cache (Cylinder chuẩn C4, viền xanh dương #2b6cb0)
  + iface: Khung Interface nét đứt (viền xanh dương nét đứt #2b6cb0)
  + ext: Khung hệ thống ngoại vi / Worker độc lập bên ngoài Boundary (viền nâu xám #6b5b57)
- Khung Boundary: Đặt nhãn tên Boundary ở góc dưới bên trái (Bottom-Left) giống hệt c4model.com
- Mũi tên: Nét đứt thẳng (Straight Dashed Arrow) nối trực tiếp từ tâm cạnh khối này tới khối kia,
  nhãn chữ gọn gàng nằm giữa mũi tên có nền trắng mảnh không viền.
"""

DIAGRAMS = [
    # =========================================================================
    # HÌNH 1: SYSTEM CONTEXT DIAGRAM
    # =========================================================================
    {
        "id": "Hinh_1_System_Context",
        "filename": "Hinh_1_System_Context_Diagram",
        "tab_name": "Hình 1 - System Context",
        "level_title": "CẤP ĐỘ 1: SYSTEM CONTEXT DIAGRAM (1 HÌNH)",
        "figure_title": "Hình 1: System Context Diagram — Ngữ cảnh Hệ thống ClassBridge",
        "layout_note": "Bố cục cân xứng chuẩn C4: Sinh viên & Giảng viên ở 2 bên cánh trên → Hệ thống ClassBridge ở tâm → Thiết bị phòng học & Admin ở dưới.",
        "canvas_w": 1600,
        "canvas_h": 1060,
        "boundaries": [
            {
                "id": "b_context",
                "title": "Môi trường Lớp học EMI (Classroom Context)",
                "subtitle": "[Context Boundary]",
                "x": 450, "y": 350, "w": 700, "h": 300
            }
        ],
        "nodes": [
            {
                "id": "Student",
                "kind": "person",
                "title": "Sinh viên (Student)",
                "stereo": "[Person]",
                "lines": [
                    "Xem phụ đề song ngữ trực tiếp,",
                    "hỏi ẩn danh (QR/PIN) & nhận đáp án"
                ],
                "x": 210, "y": 40, "w": 270, "h": 185
            },
            {
                "id": "Lecturer",
                "kind": "person",
                "title": "Giảng viên (Lecturer)",
                "stereo": "[Person]",
                "lines": [
                    "Giảng bài tiếng Anh, xem cụm",
                    "câu hỏi & trả lời đại diện 1-nhiều"
                ],
                "x": 1120, "y": 40, "w": 270, "h": 185
            },
            {
                "id": "ClassBridge",
                "kind": "sys",
                "title": "ClassBridge System",
                "stereo": "[Software System: Self-hosted AI]",
                "lines": [
                    "Trợ lý AI tự triển khai cục bộ hỗ trợ phụ đề",
                    "song ngữ thời gian thực (≤ 1.5s), gom cụm câu hỏi",
                    "đa ngôn ngữ (≤ 500ms) & tổng hợp báo cáo EMI"
                ],
                "x": 580, "y": 405, "w": 440, "h": 175
            },
            {
                "id": "MicSystem",
                "kind": "ext",
                "title": "Classroom Microphone",
                "stereo": "[External Hardware]",
                "lines": [
                    "Thu tín hiệu giọng nói trực tiếp",
                    "của giảng viên tại lớp học"
                ],
                "x": 140, "y": 800, "w": 280, "h": 150
            },
            {
                "id": "Admin",
                "kind": "person",
                "title": "Quản trị viên (Admin)",
                "stereo": "[Person]",
                "lines": [
                    "Quản lý tài khoản & tinh chỉnh",
                    "ngưỡng mô hình AI thực nghiệm"
                ],
                "x": 665, "y": 790, "w": 270, "h": 185
            },
            {
                "id": "Projector",
                "kind": "ext",
                "title": "Classroom Projector",
                "stereo": "[External Display]",
                "lines": [
                    "Trình chiếu mã PIN 6 số động,",
                    "mã QR & phụ đề tại lớp"
                ],
                "x": 1180, "y": 800, "w": 280, "h": 150
            }
        ],
        "edges": [
            {"src": "Student", "dst": "ClassBridge", "label": "Quét QR/PIN, xem phụ đề &\nhỏi ẩn danh [HTTPS/WSS]"},
            {"src": "Lecturer", "dst": "ClassBridge", "label": "Tạo phiên, xem cụm câu hỏi &\ntrả lời đại diện [HTTPS/WSS]"},
            {"src": "MicSystem", "dst": "ClassBridge", "label": "Truyền luồng âm thanh\n[WebRTC / Audio Stream]"},
            {"src": "Admin", "dst": "ClassBridge", "label": "Cấu hình tham số AI\n[HTTPS]"},
            {"src": "ClassBridge", "dst": "Projector", "label": "Hiển thị mã PIN/QR & phụ đề\n[Browser UI]"}
        ],
        "descriptions": [
            ("Hệ thống trung tâm (ClassBridge System): ", "Hệ thống trợ lý AI khép kín tự triển khai mô hình mã nguồn mở cục bộ (Self-hosted / In-house AI Inference) giúp phá vỡ rào cản ngôn ngữ và khôi phục vòng phản hồi thời gian thực trong lớp học giảng dạy bằng tiếng Anh (EMI) mà không phụ thuộc vào API thương mại bên ngoài."),
            ("Sinh viên (Student): ", "Truy cập nhanh vào phiên học qua trình duyệt di động bằng mã QR hoặc mã PIN 6 số với định danh tạm thời (Anonymous #ID) mà không cần cài đặt ứng dụng hay đăng nhập. Theo dõi phụ đề song ngữ Anh – Việt trực tiếp, gửi câu hỏi bằng tiếng Việt, tiếng Anh hoặc ngôn ngữ pha trộn (code-switching) và nhận câu trả lời từ giảng viên."),
            ("Giảng viên (Lecturer): ", "Khởi tạo phiên học mới, giảng bài trực tiếp bằng tiếng Anh, theo dõi các cụm câu hỏi nóng nhất trên Dashboard và nhập câu trả lời một lần cho câu hỏi đại diện để hệ thống tự động dịch và phát tán (1-nhiều) tới toàn bộ sinh viên trong nhóm đó."),
            ("Quản trị viên (Admin): ", "Quản lý danh sách người dùng, lớp học và điều chỉnh động các tham số thuật toán (như ngưỡng tương đồng Cosine Similarity Threshold, đổi mô hình AI) phục vụ thực nghiệm."),
            ("Classroom Microphone: ", "Hệ thống thu âm tại giảng đường tiếp nhận giọng nói trực tiếp của giảng viên (kèm tạp âm phòng học) để đẩy vào luồng xử lý âm thanh."),
            ("Classroom Projector: ", "Màn chiếu tại lớp hiển thị công khai mã PIN 6 số động (chống người lạ bên ngoài phòng học truy cập trái phép theo Kịch bản QA 3.3) và hiển thị phụ đề song ngữ trực tiếp.")
        ]
    },

    # =========================================================================
    # HÌNH 2: CONTAINER DIAGRAM (Chuẩn bố cục c4model.com trong ảnh mẫu)
    # =========================================================================
    {
        "id": "Hinh_2_Container",
        "filename": "Hinh_2_Container_Diagram",
        "tab_name": "Hình 2 - Container",
        "level_title": "CẤP ĐỘ 2: CONTAINER DIAGRAM (1 HÌNH)",
        "figure_title": "Hình 2: Container Diagram — Sơ đồ Kiến trúc Container",
        "layout_note": "Bố cục chuẩn 100% theo hình mẫu c4model.com: Sinh viên & Giảng viên ở trên, Khung ClassBridge System gồm 2 UI Browser ở tầng trên → Backend (>_) ở tâm → 2 khối trụ Queue & DB ở đáy → 2 khối AI Worker nằm tách biệt bên ngoài.",
        "canvas_w": 1600,
        "canvas_h": 1120,
        "boundaries": [
            {
                "id": "b_system",
                "title": "ClassBridge System",
                "subtitle": "[Software System]",
                "x": 350, "y": 280, "w": 820, "h": 780
            }
        ],
        "nodes": [
            {
                "id": "Student",
                "kind": "person",
                "title": "Sinh viên (Student)",
                "stereo": "[Person]",
                "lines": [
                    "Hỏi đáp ẩn danh &",
                    "xem phụ đề song ngữ"
                ],
                "x": 420, "y": 30, "w": 260, "h": 180
            },
            {
                "id": "Lecturer",
                "kind": "person",
                "title": "Giảng viên & Admin",
                "stereo": "[Person]",
                "lines": [
                    "Giảng bài, quản lý cụm",
                    "câu hỏi & cấu hình"
                ],
                "x": 840, "y": 30, "w": 260, "h": 180
            },
            {
                "id": "StudentUI",
                "kind": "ui",
                "title": "Student Mobile Web",
                "stereo": "[Container: Next.js / React]",
                "lines": [
                    "Giao diện Zero-Install xem phụ đề,",
                    "hỏi ẩn danh & lưu LocalQueue",
                    "khi rớt mạng Wi-Fi tạm thời"
                ],
                "x": 400, "y": 325, "w": 300, "h": 160
            },
            {
                "id": "LecturerUI",
                "kind": "ui",
                "title": "Lecturer Dashboard",
                "stereo": "[Container: Next.js / React]",
                "lines": [
                    "Giao diện thu âm bài giảng, quản lý",
                    "cụm câu hỏi, trả lời 1-nhiều",
                    "& xem Comprehension Heatmap"
                ],
                "x": 820, "y": 325, "w": 300, "h": 160
            },
            {
                "id": "Backend",
                "kind": "backend",
                "title": "Backend API & WebSocket",
                "stereo": "[Container: Python / FastAPI]",
                "lines": [
                    "Quản lý phiên học, xác thực PIN/JWT,",
                    "chống Spam (Rate Limit ≤ 20ms) &",
                    "Broadcast thời gian thực (≤ 400ms)"
                ],
                "x": 595, "y": 585, "w": 330, "h": 160
            },
            {
                "id": "TaskQueue",
                "kind": "db",
                "title": "Task Queue & Cache",
                "stereo": "[Container: In-Memory / Redis]",
                "lines": [
                    "Hàng đợi sự kiện bất đồng bộ",
                    "(0% Queue Drop) & lưu trạng thái"
                ],
                "x": 405, "y": 845, "w": 290, "h": 155
            },
            {
                "id": "PostgresDB",
                "kind": "db",
                "title": "Primary Database",
                "stereo": "[Container: PostgreSQL]",
                "lines": [
                    "Lưu trữ phiên học, transcript,",
                    "cụm câu hỏi (Anonymous_Hash_ID)",
                    "và báo cáo tổng kết"
                ],
                "x": 825, "y": 845, "w": 290, "h": 155
            },
            {
                "id": "STTWorker",
                "kind": "ext",
                "title": "Speech Processing Worker",
                "stereo": "[Container: Silero VAD + Faster-Whisper]",
                "lines": [
                    "Tiến trình cô lập (Worker Isolation):",
                    "Lọc khoảng lặng, nhận diện giọng nói",
                    "tiếng Anh & dịch sang tiếng Việt"
                ],
                "x": 25, "y": 585, "w": 275, "h": 160
            },
            {
                "id": "NLPWorker",
                "kind": "ext",
                "title": "NLP & LLM Inference Service",
                "stereo": "[Container: multilingual-e5-base + Qwen]",
                "lines": [
                    "Trích xuất vector 768 chiều, gom cụm",
                    "Cosine Similarity (≤ 500ms) &",
                    "tổng hợp báo cáo cuối buổi"
                ],
                "x": 1295, "y": 585, "w": 280, "h": 160
            }
        ],
        "edges": [
            {"src": "Student", "dst": "StudentUI", "label": "Truy cập qua trình duyệt di động\n[HTTPS / WSS]"},
            {"src": "Lecturer", "dst": "LecturerUI", "label": "Truy cập qua trình duyệt máy tính\n[HTTPS / WSS]"},
            {"src": "StudentUI", "dst": "Backend", "label": "Gửi câu hỏi & nhận phụ đề\n[JSON / WebSocket]"},
            {"src": "LecturerUI", "dst": "Backend", "label": "Truyền Audio & trả lời cụm\n[JSON / WebSocket]"},
            {"src": "Backend", "dst": "STTWorker", "label": "Đẩy Audio & nhận phụ đề\n[Async Worker Task]"},
            {"src": "Backend", "dst": "NLPWorker", "label": "Phân cụm & tạo báo cáo\n[Async Worker Task]"},
            {"src": "Backend", "dst": "TaskQueue", "label": "Đẩy/Đọc hàng đợi sự kiện\n[Async I/O]"},
            {"src": "Backend", "dst": "PostgresDB", "label": "Đọc và ghi dữ liệu vào\n[SQL / Asyncpg]"}
        ],
        "descriptions": [
            ("Student Mobile Web (Next.js / React): ", "Ứng dụng web siêu nhẹ chạy trực tiếp trên trình duyệt điện thoại (Zero-Install). Tích hợp cơ chế lưu tạm câu hỏi vào Local Storage Queue và tự động kết nối lại (Auto-reconnect) để đảm bảo 0% mất mát câu hỏi và đồng bộ lại phòng học trong ≤ 2s khi mạng Wi-Fi giảng đường bị ngắt quãng (Kịch bản QA 2.2)."),
            ("Lecturer Dashboard (Next.js / React): ", "Giao diện dành cho giảng viên thu âm giọng giảng, theo dõi các cụm câu hỏi được cập nhật trực tiếp, gửi câu trả lời đại diện 1-nhiều và xem biểu đồ nhiệt điểm nghẽn kiến thức (Comprehension Heatmap) cuối buổi."),
            ("Backend API & WebSocket (Python / FastAPI): ", "Trái tim điều phối của hệ thống. Quản lý vòng đời phiên học, xác thực mã PIN 6 số động, cấp mã ẩn danh một chiều (Anonymous_Hash_ID), chặn đứng tấn công spam vượt ngưỡng 3 câu/phút trong ≤ 20ms (Kịch bản QA 3.2) và phát tán câu trả lời 1-nhiều qua WebSocket trong ≤ 400ms (Kịch bản QA 1.3)."),
            ("Speech Processing Worker (Silero VAD + Faster-Whisper): ", "Container độc lập xử lý âm thanh. Được tách rời hoàn toàn (Worker Isolation) để nếu tiến trình STT gặp lỗi tràn bộ nhớ (OOM), hệ thống tự động giải phóng bộ nhớ và khởi động lại trong ≤ 5s mà không làm gián đoạn luồng Hỏi đáp Q&A (Kịch bản QA 2.1)."),
            ("NLP & LLM Inference Service (multilingual-e5-base + Qwen/Ollama): ", "Dịch vụ AI trích xuất vector ngữ nghĩa 768 chiều, gom cụm câu hỏi bằng khoảng cách Cosine trong ≤ 500ms (Kịch bản QA 1.2) và tổng hợp báo cáo bài giảng cuối buổi (FR-05)."),
            ("Task Queue & Cache (In-Memory / Redis): ", "Hàng đợi sự kiện trung gian đảm bảo 0% rớt hàng đợi (0% Queue Drop) khi 40 sinh viên gửi câu hỏi dồn dập cùng lúc."),
            ("Primary Database (PostgreSQL): ", "Lưu trữ bền vững thông tin phiên học, bản ghi lời giảng (transcript), các cụm câu hỏi (chỉ lưu Anonymous_Hash_ID, cam kết 0% khả năng truy vết ngược danh tính thật theo Kịch bản QA 3.1) và dữ liệu biểu đồ nhiệt cuối buổi.")
        ]
    },

    # =========================================================================
    # HÌNH 3.1: COMPONENT DIAGRAM — BACKEND API & WEBSOCKET SERVER
    # =========================================================================
    {
        "id": "Hinh_3_1_Component_Backend",
        "filename": "Hinh_3_1_Component_Backend_Server",
        "tab_name": "Hình 3.1 - Component Backend",
        "level_title": "CẤP ĐỘ 3: COMPONENT DIAGRAM (3 HÌNH RIÊNG BIỆT CHO 3 CONTAINER LÕI)",
        "figure_title": "Hình 3.1: Component Diagram — Backend API & WebSocket Server",
        "layout_note": "Phóng to bên trong Backend API & WebSocket Server với bố cục đối xứng Trái – Giữa – Phải chuẩn C4.",
        "canvas_w": 1600,
        "canvas_h": 1160,
        "boundaries": [
            {
                "id": "b_backend",
                "title": "Backend API & WebSocket Server",
                "subtitle": "[Container: FastAPI]",
                "x": 350, "y": 230, "w": 900, "h": 720
            }
        ],
        "nodes": [
            {
                "id": "StudentUI",
                "kind": "ui",
                "title": "Student Mobile Web",
                "stereo": "[Container: Next.js]",
                "lines": [
                    "Gửi câu hỏi ẩn danh &",
                    "nhận phụ đề / đáp án"
                ],
                "x": 400, "y": 30, "w": 290, "h": 135
            },
            {
                "id": "LecturerUI",
                "kind": "ui",
                "title": "Lecturer Dashboard",
                "stereo": "[Container: Next.js]",
                "lines": [
                    "Truyền Audio, quản lý cụm",
                    "& gửi câu trả lời 1-nhiều"
                ],
                "x": 910, "y": 30, "w": 290, "h": 135
            },
            {
                "id": "AuthGuard",
                "kind": "folder",
                "title": "Auth & Anonymizer",
                "stereo": "[Component: Security Middleware]",
                "lines": [
                    "Kiểm tra mã PIN 6 số động / QR",
                    "& băm một chiều Anonymous_Hash_ID"
                ],
                "x": 400, "y": 270, "w": 290, "h": 145
            },
            {
                "id": "RateLimiter",
                "kind": "folder",
                "title": "Anti-Spam Rate Limiter",
                "stereo": "[Component: Token Bucket]",
                "lines": [
                    "Giới hạn tối đa 3 câu hỏi/phút,",
                    "chặn Flooding Attack ≤ 20ms"
                ],
                "x": 910, "y": 270, "w": 290, "h": 145
            },
            {
                "id": "WSManager",
                "kind": "backend",
                "title": "WebSocket Broadcast Engine",
                "stereo": "[Component: WebSocket Manager]",
                "lines": [
                    "Quản lý Room phòng học & phát tán",
                    "phụ đề / đáp án 1-nhiều (≤ 400ms)"
                ],
                "x": 400, "y": 500, "w": 290, "h": 150
            },
            {
                "id": "SessionCtrl",
                "kind": "backend",
                "title": "Session & QnA Controller",
                "stereo": "[Component: FastAPI Router]",
                "lines": [
                    "Điều phối tạo phiên học, nhận câu hỏi,",
                    "xử lý câu trả lời đại diện & báo cáo"
                ],
                "x": 910, "y": 500, "w": 290, "h": 150
            },
            {
                "id": "ConfigMgr",
                "kind": "db",
                "title": "Dynamic Config Manager",
                "stereo": "[Component: Runtime Settings]",
                "lines": [
                    "Đổi nóng ngưỡng Cosine",
                    "(0.65 → 0.75) trong ≤ 5p"
                ],
                "x": 400, "y": 735, "w": 290, "h": 150
            },
            {
                "id": "Repo",
                "kind": "db",
                "title": "Data Access Repository",
                "stereo": "[Component: SQLAlchemy Async]",
                "lines": [
                    "Đọc/Ghi phiên học, cụm câu hỏi",
                    "và báo cáo tổng kết"
                ],
                "x": 910, "y": 735, "w": 290, "h": 150
            },
            {
                "id": "STTWorker",
                "kind": "ext",
                "title": "Speech Processing Worker",
                "stereo": "[Container: VAD + Whisper]",
                "lines": [
                    "Xử lý âm thanh &",
                    "dịch phụ đề song ngữ"
                ],
                "x": 25, "y": 500, "w": 265, "h": 150
            },
            {
                "id": "NLPWorker",
                "kind": "ext",
                "title": "NLP & LLM Service",
                "stereo": "[Container: e5-base + Qwen]",
                "lines": [
                    "Gom cụm Cosine &",
                    "tạo Comprehension Heatmap"
                ],
                "x": 1310, "y": 500, "w": 265, "h": 150
            },
            {
                "id": "PostgresDB",
                "kind": "db",
                "title": "Primary Database",
                "stereo": "[Container: PostgreSQL]",
                "lines": [
                    "Lưu trữ dữ liệu bền vững"
                ],
                "x": 910, "y": 985, "w": 290, "h": 140
            }
        ],
        "edges": [
            {"src": "StudentUI", "dst": "AuthGuard", "label": "Gửi câu hỏi + PIN\n[HTTPS / REST]"},
            {"src": "LecturerUI", "dst": "RateLimiter", "label": "Quản lý & Trả lời\n[HTTPS / WSS]"},
            {"src": "AuthGuard", "dst": "RateLimiter", "label": "Gắn Anonymous_Hash_ID"},
            {"src": "AuthGuard", "dst": "WSManager", "label": "Kết nối Room [WebSocket]"},
            {"src": "RateLimiter", "dst": "SessionCtrl", "label": "Chuyển câu hỏi hợp lệ"},
            {"src": "SessionCtrl", "dst": "WSManager", "label": "Kích hoạt Broadcast 1-nhiều"},
            {"src": "WSManager", "dst": "STTWorker", "label": "Đẩy Audio & nhận phụ đề\n[Async Worker Task]"},
            {"src": "SessionCtrl", "dst": "NLPWorker", "label": "Phân cụm & tóm tắt\n[Async Worker Task]"},
            {"src": "SessionCtrl", "dst": "ConfigMgr", "label": "Đọc/Cập nhật ngưỡng"},
            {"src": "SessionCtrl", "dst": "Repo", "label": "Gọi lưu trữ dữ liệu"},
            {"src": "Repo", "dst": "PostgresDB", "label": "Truy vấn SQL bất đồng bộ\n[Asyncpg]"}
        ],
        "descriptions": [
            ("Auth & Anonymizer (Security Middleware): ", "Xác thực mã PIN 6 số động hoặc chữ ký số ngắn hạn trong mã QR để từ chối 100% kết nối trái phép từ bên ngoài lớp học (Kịch bản QA 3.3). Sinh mã định danh băm một chiều Anonymous_Hash_ID cho sinh viên, đảm bảo 0% khả năng truy vết ngược danh tính cá nhân (Kịch bản QA 3.1)."),
            ("Anti-Spam Rate Limiter (Token Bucket): ", "Kiểm soát tần suất gửi câu hỏi theo từng Anonymous_Hash_ID (tối đa 3 câu/phút), lập tức từ chối các request vượt ngưỡng trong ≤ 20ms trước khi đi vào mô hình AI (Kịch bản QA 3.2)."),
            ("Session & QnA Controller (FastAPI Router): ", "Xử lý các yêu cầu REST API khởi tạo phiên học, tiếp nhận câu hỏi hợp lệ đẩy sang dịch vụ NLP, nhận câu trả lời đại diện từ giảng viên và kích hoạt tổng hợp báo cáo cuối buổi."),
            ("WebSocket Broadcast Engine (WebSocket Manager): ", "Duy trì kết nối WebSocket với 60–100 thiết bị theo cấu trúc Phòng học (Room) và Nhóm câu hỏi (Cluster Group), đảm bảo phát tán câu trả lời 1-nhiều tới đúng sinh viên trong cụm trong vòng ≤ 400ms (Kịch bản QA 1.3)."),
            ("Dynamic Config Manager (Runtime Settings): ", "Quản lý các tham số động, cho phép nhóm nghiên cứu tinh chỉnh ngưỡng tương đồng ngữ nghĩa (Similarity Threshold từ 0.65 → 0.75) ngay giữa các ca học thực nghiệm trong ≤ 5 phút mà không cần biên dịch lại hệ thống (Kịch bản QA 4.2)."),
            ("Data Access Repository (SQLAlchemy Async): ", "Đóng gói toàn bộ truy vấn đọc/ghi phiên học, lịch sử câu hỏi và báo cáo xuống PostgreSQL.")
        ]
    },

    # =========================================================================
    # HÌNH 3.2: COMPONENT DIAGRAM — SPEECH PROCESSING WORKER (FR-02)
    # =========================================================================
    {
        "id": "Hinh_3_2_Component_Speech_Worker",
        "filename": "Hinh_3_2_Component_Speech_Worker",
        "tab_name": "Hình 3.2 - Speech Worker",
        "level_title": "CẤP ĐỘ 3: COMPONENT DIAGRAM — SPEECH PROCESSING WORKER",
        "figure_title": "Hình 3.2: Component Diagram — Speech Processing Worker (Tính năng lõi FR-02)",
        "layout_note": "Phóng to bên trong Speech Processing Worker với luồng xử lý cân đối chuẩn C4.",
        "canvas_w": 1600,
        "canvas_h": 1060,
        "boundaries": [
            {
                "id": "b_stt",
                "title": "Speech Processing Worker",
                "subtitle": "[Container: Isolated Python Worker]",
                "x": 350, "y": 70, "w": 900, "h": 740
            }
        ],
        "nodes": [
            {
                "id": "AudioInput",
                "kind": "ext",
                "title": "Task Queue (Audio Stream)",
                "stereo": "[Container: Async Queue]",
                "lines": [
                    "Cung cấp các đoạn âm thanh",
                    "cắt ngắn (3–5 giây) từ giảng viên"
                ],
                "x": 25, "y": 120, "w": 265, "h": 150
            },
            {
                "id": "WSOutput",
                "kind": "ext",
                "title": "WebSocket Broadcast Engine",
                "stereo": "[Container: FastAPI Server]",
                "lines": [
                    "Nhận phụ đề song ngữ để đẩy",
                    "lên màn chiếu & điện thoại"
                ],
                "x": 1310, "y": 365, "w": 265, "h": 150
            },
            {
                "id": "AudioConsumer",
                "kind": "folder",
                "title": "Audio Stream Consumer",
                "stereo": "[Component: Async Worker]",
                "lines": [
                    "Nhận Audio Chunk (3–5s) và",
                    "chuẩn hóa tần số lấy mẫu 16kHz"
                ],
                "x": 400, "y": 120, "w": 290, "h": 150
            },
            {
                "id": "VADGate",
                "kind": "folder",
                "title": "VAD Audio Gate",
                "stereo": "[Component: Silero VAD]",
                "lines": [
                    "Phát hiện giọng nói giảng viên,",
                    "ngắt luồng khi im lặng chống ảo giác"
                ],
                "x": 910, "y": 120, "w": 290, "h": 150
            },
            {
                "id": "WhisperEngine",
                "kind": "backend",
                "title": "STT Inference Engine",
                "stereo": "[Component: Faster-Whisper]",
                "lines": [
                    "Chuyển đổi giọng nói tiếng Anh",
                    "sang văn bản với độ trễ thấp"
                ],
                "x": 400, "y": 365, "w": 290, "h": 150
            },
            {
                "id": "TermTranslator",
                "kind": "backend",
                "title": "Bilingual Translator",
                "stereo": "[Component: NLLB / MarianMT]",
                "lines": [
                    "Dịch phụ đề tiếng Anh sang tiếng Việt,",
                    "bảo toàn thuật ngữ chuyên ngành IT"
                ],
                "x": 910, "y": 365, "w": 290, "h": 150
            },
            {
                "id": "MemoryGuard",
                "kind": "db",
                "title": "Worker Health & Memory Guard",
                "stereo": "[Component: Fault Supervisor]",
                "lines": [
                    "Giám sát tràn bộ nhớ (OOM)",
                    "& tự khởi động lại STT ≤ 5s"
                ],
                "x": 400, "y": 605, "w": 290, "h": 150
            },
            {
                "id": "TranscriptStore",
                "kind": "db",
                "title": "Transcript Buffer",
                "stereo": "[Component: Batch Writer]",
                "lines": [
                    "Đệm bản ghi lời giảng kèm",
                    "dấu thời gian (Timestamp)"
                ],
                "x": 910, "y": 605, "w": 290, "h": 150
            },
            {
                "id": "PostgresDB",
                "kind": "db",
                "title": "Primary Database",
                "stereo": "[Container: PostgreSQL]",
                "lines": [
                    "Lưu trữ toàn bộ bản ghi",
                    "lời giảng phục vụ báo cáo"
                ],
                "x": 910, "y": 870, "w": 290, "h": 145
            }
        ],
        "edges": [
            {"src": "AudioInput", "dst": "AudioConsumer", "label": "1. Đẩy Audio Chunk (3-5s)\n[Async Worker Task]"},
            {"src": "AudioConsumer", "dst": "VADGate", "label": "2. Truyền luồng 16kHz\n[PCM Bytes]"},
            {"src": "VADGate", "dst": "WhisperEngine", "label": "3. Chỉ đẩy đoạn có giọng nói\n[Filtered Audio]"},
            {"src": "WhisperEngine", "dst": "TermTranslator", "label": "4. Văn bản tiếng Anh\n[Raw Transcript]"},
            {"src": "TermTranslator", "dst": "WSOutput", "label": "5. Trả phụ đề (≤ 1.5s)\n[JSON Payload]"},
            {"src": "MemoryGuard", "dst": "WhisperEngine", "label": "Giám sát & khôi phục OOM\n[Process Watchdog]"},
            {"src": "TermTranslator", "dst": "TranscriptStore", "label": "Ghi nhận câu thoại\n[Async I/O]"},
            {"src": "TranscriptStore", "dst": "PostgresDB", "label": "Lưu bản ghi lời giảng\n[SQL / Asyncpg]"}
        ],
        "descriptions": [
            ("Audio Stream Consumer (Async Worker): ", "Nhận luồng âm thanh cắt theo khung 3–5 giây từ hàng đợi sự kiện và chuẩn hóa về định dạng 16kHz mono."),
            ("VAD Audio Gate (Silero VAD): ", "Cổng kiểm soát âm thanh giúp phát hiện khi giảng viên dừng giảng bài (micro chỉ thu tiếng quạt máy và tiếng thảo luận nhỏ) để tự động ngắt luồng đẩy sang Whisper, đảm bảo 0 dòng phụ đề rác/ảo giác (Hallucination) và tiết kiệm ≥ 80% tài nguyên GPU/CPU (Kịch bản QA 2.3)."),
            ("STT Inference Engine (Faster-Whisper): ", "Giải mã các đoạn âm thanh có giọng nói hợp lệ thành văn bản tiếng Anh với tốc độ cao."),
            ("Bilingual Translator (NLLB / MarianMT): ", "Dịch văn bản tiếng Anh sang tiếng Việt (bảo toàn thuật ngữ chuyên ngành IT), đảm bảo tổng độ trễ đầu-cuối từ lúc giảng viên ngắt câu đến khi hiển thị phụ đề đạt ≤ 1.5s (Kịch bản QA 1.1)."),
            ("Worker Health & Memory Guard & Transcript Buffer: ", "Thực thi cơ chế cô lập lỗi (Fault Isolation); nếu tiến trình STT gặp lỗi tràn bộ nhớ (OOM) hoặc treo do âm thanh nhiễu kéo dài, bộ giám sát tự động giải phóng bộ nhớ và khởi động lại STT Worker trong ≤ 5s mà không ảnh hưởng đến luồng Hỏi đáp (Kịch bản QA 2.1), đồng thời lưu bản ghi lời giảng vào PostgreSQL.")
        ]
    },

    # =========================================================================
    # HÌNH 3.3: COMPONENT DIAGRAM — NLP & LLM INFERENCE SERVICE (FR-03 & FR-05)
    # =========================================================================
    {
        "id": "Hinh_3_3_Component_NLP_LLM",
        "filename": "Hinh_3_3_Component_NLP_LLM_Service",
        "tab_name": "Hình 3.3 - NLP & LLM",
        "level_title": "CẤP ĐỘ 3: COMPONENT DIAGRAM — NLP & LLM INFERENCE SERVICE",
        "figure_title": "Hình 3.3: Component Diagram — NLP & LLM Inference Service (Tính năng lõi FR-03 & FR-05)",
        "layout_note": "Phóng to bên trong NLP & LLM Inference Service với bố cục cân đối Trái – Giữa – Phải chuẩn C4.",
        "canvas_w": 1600,
        "canvas_h": 1060,
        "boundaries": [
            {
                "id": "b_nlp",
                "title": "NLP & LLM Inference Service",
                "subtitle": "[Container: Self-hosted AI Service]",
                "x": 350, "y": 70, "w": 900, "h": 740
            }
        ],
        "nodes": [
            {
                "id": "QuestionInput",
                "kind": "ext",
                "title": "Session & QnA Controller",
                "stereo": "[Container: FastAPI Backend]",
                "lines": [
                    "Gửi câu hỏi ẩn danh mới &",
                    "yêu cầu tổng kết cuối buổi"
                ],
                "x": 25, "y": 240, "w": 265, "h": 155
            },
            {
                "id": "DashboardOut",
                "kind": "ui",
                "title": "Lecturer Dashboard",
                "stereo": "[Container: Next.js UI]",
                "lines": [
                    "Hiển thị danh sách cụm câu hỏi",
                    "nóng nhất & biểu đồ Heatmap"
                ],
                "x": 1310, "y": 365, "w": 265, "h": 150
            },
            {
                "id": "TextNorm",
                "kind": "folder",
                "title": "Multilingual Text Normalizer",
                "stereo": "[Component: Preprocessor]",
                "lines": [
                    "Chuẩn hóa câu hỏi tiếng Việt, Anh",
                    "& pha trộn thuật ngữ (Code-switching)"
                ],
                "x": 400, "y": 120, "w": 290, "h": 150
            },
            {
                "id": "EmbedAdapter",
                "kind": "folder",
                "title": "Embedding Model Adapter",
                "stereo": "[Component: Strategy Pattern]",
                "lines": [
                    "Trích xuất vector ngữ nghĩa 768 chiều",
                    "(Hỗ trợ đổi e5-base / LaBSE)"
                ],
                "x": 910, "y": 120, "w": 290, "h": 150
            },
            {
                "id": "LLMSummarizer",
                "kind": "backend",
                "title": "Unified LLM Summarizer",
                "stereo": "[Component: Qwen2.5-7B / Ollama]",
                "lines": [
                    "Tổng hợp nội dung bài giảng cuối buổi",
                    "& tính toán Comprehension Heatmap"
                ],
                "x": 400, "y": 365, "w": 290, "h": 150
            },
            {
                "id": "ClusterEngine",
                "kind": "backend",
                "title": "Semantic Clustering Engine",
                "stereo": "[Component: Cosine Similarity]",
                "lines": [
                    "So khớp vector với tâm cụm hiện tại,",
                    "gộp cụm hoặc tạo mới trong ≤ 500ms"
                ],
                "x": 910, "y": 365, "w": 290, "h": 150
            },
            {
                "id": "ReportBuilder",
                "kind": "db",
                "title": "Report & Heatmap Exporter",
                "stereo": "[Component: JSON / PDF Builder]",
                "lines": [
                    "Đóng gói dữ liệu biểu đồ nhiệt",
                    "và biên bản buổi học"
                ],
                "x": 400, "y": 605, "w": 290, "h": 150
            },
            {
                "id": "CentroidStore",
                "kind": "db",
                "title": "Cluster Centroid Cache",
                "stereo": "[Component: Vector State]",
                "lines": [
                    "Lưu giữ và cập nhật vector tâm",
                    "của các cụm trong phiên học"
                ],
                "x": 910, "y": 605, "w": 290, "h": 150
            },
            {
                "id": "PostgresDB",
                "kind": "db",
                "title": "Primary Database",
                "stereo": "[Container: PostgreSQL]",
                "lines": [
                    "Lưu trữ danh sách cụm câu hỏi",
                    "và báo cáo tổng kết ca học"
                ],
                "x": 655, "y": 870, "w": 290, "h": 145
            }
        ],
        "edges": [
            {"src": "QuestionInput", "dst": "TextNorm", "label": "1. Gửi câu hỏi mới\n[Async Worker Task]"},
            {"src": "TextNorm", "dst": "EmbedAdapter", "label": "2. Chuỗi văn bản sạch\n[Normalized Text]"},
            {"src": "EmbedAdapter", "dst": "ClusterEngine", "label": "3. Vector 768 chiều\n[Float Array]"},
            {"src": "QuestionInput", "dst": "LLMSummarizer", "label": "Kích hoạt tổng kết\n[End Session Event]"},
            {"src": "ClusterEngine", "dst": "DashboardOut", "label": "4. Cập nhật cụm (≤ 500ms)\n[WebSocket Push]"},
            {"src": "LLMSummarizer", "dst": "ReportBuilder", "label": "Kết xuất báo cáo\n[Structured JSON]"},
            {"src": "ClusterEngine", "dst": "CentroidStore", "label": "Đọc & cập nhật tâm cụm\n[Centroid Update]"},
            {"src": "ReportBuilder", "dst": "PostgresDB", "label": "Lưu báo cáo & Heatmap\n[SQL / Asyncpg]"},
            {"src": "CentroidStore", "dst": "PostgresDB", "label": "Đồng bộ cụm câu hỏi\n[SQL / Asyncpg]"}
        ],
        "descriptions": [
            ("Multilingual Text Normalizer (Preprocessor): ", "Tiền xử lý văn bản câu hỏi tự do của sinh viên, chuẩn hóa từ viết tắt và cấu trúc pha trộn Việt – Anh (code-switching)."),
            ("Embedding Model Adapter (Strategy Pattern): ", "Chuyển đổi văn bản câu hỏi thành vector ngữ nghĩa 768 chiều. Áp dụng mẫu thiết kế Strategy/Adapter Pattern giúp nhóm phát triển dễ dàng thay thế mô hình giữa LaBSE và intfloat/multilingual-e5-base trong ≤ 1 giờ làm việc để chạy Benchmark đo các chỉ số ARI, NMI, Silhouette Score mà không sửa code phân cụm (Kịch bản QA 4.1)."),
            ("Semantic Clustering Engine (Cosine Similarity): ", "Tính khoảng cách Cosine giữa vector câu hỏi mới với tâm các cụm hiện tại (Cluster Centroid Cache), tự động gộp vào cụm tương đồng hoặc khởi tạo cụm mới và cập nhật lên Dashboard giảng viên trong ≤ 500ms với 0% rớt hàng đợi (Kịch bản QA 1.2)."),
            ("Unified LLM Summarizer & Report Exporter: ", "Sử dụng giao diện LLM chuẩn hóa (Unified LLM Interface) gọi mô hình cục bộ (Qwen2.5-7B qua Ollama) tổng hợp nội dung bài giảng và tạo dữ liệu Comprehension Heatmap, cho phép chuyển đổi sang mô hình gọn nhẹ hơn trong ≤ 30 phút cấu hình khi máy chủ thiếu VRAM (FR-05 & Kịch bản QA 4.3).")
        ]
    },

    # =========================================================================
    # HÌNH 4.1: CODE DIAGRAM — LUỒNG PHỤ ĐỀ SONG NGỮ & VAD GATE (FR-02)
    # =========================================================================
    {
        "id": "Hinh_4_1_Code_Speech_Pipeline",
        "filename": "Hinh_4_1_Code_Speech_Pipeline",
        "tab_name": "Hình 4.1 - Code Speech",
        "level_title": "CẤP ĐỘ 4: CODE DIAGRAM (4 HÌNH CHO 4 LUỒNG XỬ LÝ LÕI)",
        "figure_title": "Hình 4.1: Code Diagram — Luồng Phụ đề Song ngữ & VAD Gate Chống ảo giác (FR-02)",
        "layout_note": "Bố cục cân xứng chuẩn C4: Khung Module ở giữa → Worker Controller ở tâm → 2 Adapter thực thi ở 2 cánh Trái – Phải.",
        "canvas_w": 1600,
        "canvas_h": 1080,
        "boundaries": [
            {
                "id": "b_code_speech",
                "title": "Speech Processing Module",
                "subtitle": "[Code Boundary: FR-02 & QA 1.1, 2.1, 2.3]",
                "x": 350, "y": 60, "w": 900, "h": 760
            }
        ],
        "nodes": [
            {
                "id": "VADGate",
                "kind": "folder",
                "title": "class SileroVADGate",
                "stereo": "[VAD Filter Class]",
                "lines": [
                    "- probThreshold: float = 0.5",
                    "+ isHumanSpeech(audioBytes): bool",
                    "+ trimSilence(audioBytes): bytes"
                ],
                "x": 400, "y": 110, "w": 290, "h": 155
            },
            {
                "id": "MemGuard",
                "kind": "folder",
                "title": "class WorkerMemoryGuard",
                "stereo": "[Fault Isolation Class]",
                "lines": [
                    "- maxVramLimitMB: int",
                    "+ checkMemory(engine): bool",
                    "+ recoverOnOOM(engine): void"
                ],
                "x": 910, "y": 110, "w": 290, "h": 155
            },
            {
                "id": "Worker",
                "kind": "backend",
                "title": "class SpeechPipelineWorker",
                "stereo": "[Core Worker Controller]",
                "lines": [
                    "- vadGate: SileroVADGate",
                    "- sttEngine: ISTTEngine | - translator: ITranslator",
                    "+ processAudioChunk(sessionId, audio): SubtitleDTO"
                ],
                "x": 580, "y": 365, "w": 440, "h": 165
            },
            {
                "id": "ISTT",
                "kind": "iface",
                "title": "<<interface>> ISTTEngine",
                "stereo": "[STT Strategy Interface]",
                "lines": [
                    "+ transcribe(audioBytes: bytes): str"
                ],
                "x": 390, "y": 625, "w": 290, "h": 135
            },
            {
                "id": "ITrans",
                "kind": "iface",
                "title": "<<interface>> ITranslator",
                "stereo": "[Translation Interface]",
                "lines": [
                    "+ translateEnToVi(text: str): str"
                ],
                "x": 920, "y": 625, "w": 290, "h": 135
            },
            {
                "id": "FasterWhisper",
                "kind": "ext",
                "title": "class FasterWhisperEngine",
                "stereo": "[Implements: ISTTEngine]",
                "lines": [
                    "- model: WhisperModel",
                    "- computeType: str = 'int8_float16'",
                    "+ transcribe(audioBytes): str",
                    "+ reloadModel(): void"
                ],
                "x": 20, "y": 610, "w": 270, "h": 165
            },
            {
                "id": "NLLBAdapter",
                "kind": "ext",
                "title": "class NLLBTranslatorAdapter",
                "stereo": "[Implements: ITranslator]",
                "lines": [
                    "- model: AutoModelForSeq2SeqLM",
                    "- tokenizer: AutoTokenizer",
                    "+ translateEnToVi(text): str"
                ],
                "x": 1310, "y": 610, "w": 270, "h": 165
            },
            {
                "id": "SubDTO",
                "kind": "db",
                "title": "class SubtitlePayloadDTO",
                "stereo": "[Data Transfer Object]",
                "lines": [
                    "+ sessionId: str | + timestamp: float",
                    "+ englishText: str | + vietnameseText: str"
                ],
                "x": 620, "y": 875, "w": 360, "h": 145
            }
        ],
        "edges": [
            {"src": "VADGate", "dst": "Worker", "label": "1. isHumanSpeech()\n[Chặn 100% ảo giác]"},
            {"src": "MemGuard", "dst": "Worker", "label": "2. recoverOnOOM()\n[Tự phục hồi ≤ 5s]"},
            {"src": "Worker", "dst": "ISTT", "label": "3. Gọi transcribe()\n[Polymorphic Call]"},
            {"src": "Worker", "dst": "ITrans", "label": "4. Gọi translateEnToVi()\n[Polymorphic Call]"},
            {"src": "Worker", "dst": "SubDTO", "label": "5. Đóng gói (≤ 1.5s)\n[Instantiates]"},
            {"src": "FasterWhisper", "dst": "ISTT", "label": "Implements\n[CTranslate2]"},
            {"src": "NLLBAdapter", "dst": "ITrans", "label": "Implements\n[Bilingual]"}
        ],
        "descriptions": [
            ("Class SpeechPipelineWorker: ", "Điều phối luồng xử lý âm thanh thông qua phương thức processAudioChunk(sessionId, audio). Luôn kiểm tra âm thanh qua vadGate.isHumanSpeech(audioBytes) trước tiên; nếu giảng viên đang im lặng (trả về False), phương thức lập tức thoát sớm (Early Return) để ngăn chặn 100% lỗi sinh văn bản ảo giác (Kịch bản QA 2.3)."),
            ("Class SileroVADGate: ", "Chứa phương thức isHumanSpeech() tính xác suất có giọng nói con người so với ngưỡng probThreshold = 0.5 và phương thức trimSilence() cắt bỏ khoảng lặng thừa ở hai đầu đoạn âm thanh."),
            ("Class WorkerMemoryGuard: ", "Cung cấp phương thức recoverOnOOM(engine) bắt ngoại lệ tràn bộ nhớ (Out-of-Memory), tự động giải phóng VRAM và gọi reloadModel() để khôi phục tiến trình STT trong vòng ≤ 5s mà không ảnh hưởng tới luồng Hỏi đáp (Kịch bản QA 2.1)."),
            ("Interface ISTTEngine (FasterWhisperEngine) & ITranslator (NLLBTranslatorAdapter): ", "Thực hiện nhận diện giọng nói tiếng Anh qua transcribe() và dịch sang tiếng Việt qua translateEnToVi(), trả về đối tượng SubtitlePayloadDTO với tổng độ trễ ≤ 1.5s (Kịch bản QA 1.1).")
        ]
    },

    # =========================================================================
    # HÌNH 4.2: CODE DIAGRAM — LUỒNG GOM NHÓM CÂU HỎI NGỮ NGHĨA (FR-03 & QA 4)
    # =========================================================================
    {
        "id": "Hinh_4_2_Code_Clustering",
        "filename": "Hinh_4_2_Code_Question_Clustering",
        "tab_name": "Hình 4.2 - Code Clustering",
        "level_title": "CẤP ĐỘ 4: CODE DIAGRAM — GOM NHÓM CÂU HỎI NGỮ NGHĨA",
        "figure_title": "Hình 4.2: Code Diagram — Luồng Gom nhóm Câu hỏi Ngữ nghĩa Đa ngôn ngữ (FR-03 & QA 4)",
        "layout_note": "Bố cục cân xứng chuẩn C4: Khung Clustering Module ở giữa → 2 Adapter mô hình e5-base và LaBSE ở 2 cánh Trái – Phải.",
        "canvas_w": 1600,
        "canvas_h": 1080,
        "boundaries": [
            {
                "id": "b_code_cluster",
                "title": "Semantic Question Clustering Module",
                "subtitle": "[Code Boundary: FR-03 & QA 1.2, 4.1, 4.2]",
                "x": 350, "y": 60, "w": 900, "h": 760
            }
        ],
        "nodes": [
            {
                "id": "ConfigMgr",
                "kind": "folder",
                "title": "class DynamicConfigManager",
                "stereo": "[Runtime Config Class]",
                "lines": [
                    "- similarityThreshold: float = 0.75",
                    "+ getThreshold(): float",
                    "+ setThreshold(newVal: float): void"
                ],
                "x": 400, "y": 110, "w": 290, "h": 155
            },
            {
                "id": "Normalizer",
                "kind": "folder",
                "title": "class MultilingualNormalizer",
                "stereo": "[Text Preprocessor Class]",
                "lines": [
                    "+ cleanCodeSwitching(text: str): str"
                ],
                "x": 910, "y": 110, "w": 290, "h": 155
            },
            {
                "id": "ClusterEngine",
                "kind": "backend",
                "title": "class OnlineClusteringEngine",
                "stereo": "[Core Clustering Service]",
                "lines": [
                    "- embedStrategy: IEmbeddingStrategy",
                    "+ assignOrCreateCluster(q, clusters): QuestionCluster",
                    "+ computeCosine(vecA, vecB): float",
                    "+ updateCentroid(cluster, newVec): void"
                ],
                "x": 570, "y": 355, "w": 460, "h": 175
            },
            {
                "id": "IEmbed",
                "kind": "iface",
                "title": "<<interface>> IEmbeddingStrategy",
                "stereo": "[Strategy Pattern Interface]",
                "lines": [
                    "+ encode(text: str): List[float]"
                ],
                "x": 390, "y": 625, "w": 290, "h": 145
            },
            {
                "id": "ClusterEntity",
                "kind": "db",
                "title": "class QuestionCluster",
                "stereo": "[Domain Entity]",
                "lines": [
                    "+ clusterId: str | + representativeText: str",
                    "+ centroidVector: List[float]",
                    "+ subscriberAnonIds: List[str]"
                ],
                "x": 920, "y": 625, "w": 290, "h": 150
            },
            {
                "id": "E5Adapter",
                "kind": "ext",
                "title": "class MultilingualE5Adapter",
                "stereo": "[Implements: IEmbeddingStrategy]",
                "lines": [
                    "- e5Model: AutoModel",
                    "+ encode(text): List[float]",
                    "- addQueryPrefix(text): str"
                ],
                "x": 20, "y": 615, "w": 270, "h": 160
            },
            {
                "id": "LaBSEAdapter",
                "kind": "ext",
                "title": "class LaBSEAdapter",
                "stereo": "[Implements: IEmbeddingStrategy]",
                "lines": [
                    "- labseModel: SentenceTransformer",
                    "+ encode(text): List[float]"
                ],
                "x": 1310, "y": 365, "w": 270, "h": 160
            },
            {
                "id": "QuestionEntity",
                "kind": "db",
                "title": "class QuestionEntity",
                "stereo": "[Domain Entity]",
                "lines": [
                    "+ questionId: str | + anonymousHashId: str",
                    "+ rawContent: str | + embeddingVector: List[float]"
                ],
                "x": 885, "y": 875, "w": 360, "h": 145
            }
        ],
        "edges": [
            {"src": "ConfigMgr", "dst": "ClusterEngine", "label": "1. getThreshold()\n[Đổi nóng 0.65 → 0.75 ≤ 5p]"},
            {"src": "Normalizer", "dst": "ClusterEngine", "label": "2. Làm sạch câu hỏi\n[cleanCodeSwitching()]"},
            {"src": "ClusterEngine", "dst": "IEmbed", "label": "3. Vector 768 chiều\n[encode(text)]"},
            {"src": "ClusterEngine", "dst": "ClusterEntity", "label": "4. Gộp cụm / tạo mới\n[≤ 500ms / câu]"},
            {"src": "ClusterEntity", "dst": "QuestionEntity", "label": "Quản lý câu hỏi thành viên\n[1-to-Many]"},
            {"src": "E5Adapter", "dst": "IEmbed", "label": "Implements\n[e5-base]"},
            {"src": "LaBSEAdapter", "dst": "ClusterEngine", "label": "Strategy Benchmark\n[LaBSE Adapter]"}
        ],
        "descriptions": [
            ("Class OnlineClusteringEngine: ", "Chứa thuật toán phân cụm trực tuyến qua phương thức assignOrCreateCluster(q, clusters). Phương thức này gọi embedStrategy.encode() để lấy vector 768 chiều, tính khoảng cách qua computeCosine(vecA, vecB) và so sánh với ngưỡng lấy từ DynamicConfigManager. Nếu độ tương đồng đạt ngưỡng thì gộp câu hỏi vào cụm và gọi updateCentroid(); ngược lại thì khởi tạo một QuestionCluster mới trong ≤ 500ms (Kịch bản QA 1.2)."),
            ("Interface IEmbeddingStrategy, MultilingualE5Adapter, LaBSEAdapter: ", "Áp dụng mẫu thiết kế Strategy Pattern giúp tách rời thuật toán phân cụm khỏi mô hình ngôn ngữ cụ thể. Nhóm nghiên cứu có thể chuyển đổi từ LaBSE sang intfloat/multilingual-e5-base trong ≤ 1 giờ làm việc để đo chỉ số ARI và Silhouette Score với 0 dòng code bị sửa ở tầng Frontend và Database (Kịch bản QA 4.1)."),
            ("Class DynamicConfigManager: ", "Cung cấp phương thức setThreshold(newVal) cho phép cập nhật nóng ngưỡng tương đồng (ví dụ từ 0.65 lên 0.75) ngay giữa các ca học thực nghiệm trong ≤ 5 phút (Kịch bản QA 4.2)."),
            ("Class QuestionCluster & QuestionEntity: ", "Lưu trữ câu hỏi đại diện (representativeText), vector tâm cụm (centroidVector) và danh sách định danh ẩn danh của sinh viên trong cụm (subscriberAnonIds) để phục vụ phản hồi 1-nhiều.")
        ]
    },

    # =========================================================================
    # HÌNH 4.3: CODE DIAGRAM — BẢO MẬT ẨN DANH, CHỐNG SPAM & PHẢN HỒI 1-NHIỀU
    # =========================================================================
    {
        "id": "Hinh_4_3_Code_Security_Broadcast",
        "filename": "Hinh_4_3_Code_Security_Broadcast",
        "tab_name": "Hình 4.3 - Code Security",
        "level_title": "CẤP ĐỘ 4: CODE DIAGRAM — BẢO MẬT ẨN DANH & BROADCAST 1-NHIỀU",
        "figure_title": "Hình 4.3: Code Diagram — Luồng Bảo mật Ẩn danh, Chống Spam & Phản hồi 1-nhiều (FR-01, FR-04 & QA 3)",
        "layout_note": "Bố cục cân xứng chuẩn C4: Khung Security & Broadcast ở giữa → Request đầu vào bên trái, Dịch vụ dịch thuật bên phải.",
        "canvas_w": 1600,
        "canvas_h": 980,
        "boundaries": [
            {
                "id": "b_code_sec",
                "title": "Security & 1-to-Many Broadcast Module",
                "subtitle": "[Code Boundary: FR-01, FR-04 & QA 1.3, 3.1, 3.2, 3.3]",
                "x": 350, "y": 60, "w": 900, "h": 840
            }
        ],
        "nodes": [
            {
                "id": "ClientReq",
                "kind": "ext",
                "title": "Student & Lecturer Request",
                "stereo": "[Incoming HTTP / WebSocket]",
                "lines": [
                    "Gửi câu hỏi kèm PIN/Token hoặc",
                    "gửi câu trả lời đại diện cho cụm"
                ],
                "x": 20, "y": 115, "w": 270, "h": 155
            },
            {
                "id": "TranslationSvc",
                "kind": "ext",
                "title": "class BilingualTranslator",
                "stereo": "[External AI Service]",
                "lines": [
                    "+ translateAnswer(text, targetLang): str"
                ],
                "x": 1310, "y": 380, "w": 270, "h": 160
            },
            {
                "id": "AuthMid",
                "kind": "folder",
                "title": "class SessionAuthMiddleware",
                "stereo": "[Security Guard Class]",
                "lines": [
                    "- secretSalt: str",
                    "+ verifyPinOrQR(sessionId, token): bool",
                    "+ generateAnonHash(sessionId, key): str"
                ],
                "x": 400, "y": 115, "w": 300, "h": 155
            },
            {
                "id": "RateLimit",
                "kind": "folder",
                "title": "class AntiSpamRateLimiter",
                "stereo": "[Token Bucket Class]",
                "lines": [
                    "- maxQuestionsPerMin: int = 3",
                    "+ allowRequest(anonHashId): bool"
                ],
                "x": 900, "y": 115, "w": 300, "h": 155
            },
            {
                "id": "WSMgr",
                "kind": "backend",
                "title": "class WebSocketBroadcastManager",
                "stereo": "[Real-time Engine Class]",
                "lines": [
                    "+ subscribeCluster(clusterId, anonId, ws)",
                    "+ broadcastToCluster(clusterId, payload)"
                ],
                "x": 400, "y": 380, "w": 300, "h": 165
            },
            {
                "id": "QnACtrl",
                "kind": "backend",
                "title": "class QnAController",
                "stereo": "[FastAPI Router Controller]",
                "lines": [
                    "- clusterEngine: OnlineClusteringEngine",
                    "+ submitQuestion(sessionId, anonId, text)",
                    "+ answerCluster(clusterId, answerText)"
                ],
                "x": 900, "y": 380, "w": 300, "h": 165
            },
            {
                "id": "SubMap",
                "kind": "db",
                "title": "Cluster Subscription Registry",
                "stereo": "[In-Memory Map: Dict[str, Set[WS]]]",
                "lines": [
                    "Ánh xạ clusterId tới danh sách kết nối",
                    "WebSocket của sinh viên trong cụm"
                ],
                "x": 400, "y": 660, "w": 300, "h": 155
            },
            {
                "id": "AnswerDTO",
                "kind": "db",
                "title": "class BilingualAnswerDTO",
                "stereo": "[Response Payload]",
                "lines": [
                    "+ clusterId: str",
                    "+ answerEn: str | + answerVi: str"
                ],
                "x": 900, "y": 660, "w": 300, "h": 155
            }
        ],
        "edges": [
            {"src": "ClientReq", "dst": "AuthMid", "label": "1. verifyPinOrQR()\n[Chặn 100% trái phép]"},
            {"src": "AuthMid", "dst": "RateLimit", "label": "2. generateAnonHash()\n[0% lộ danh tính]"},
            {"src": "RateLimit", "dst": "QnACtrl", "label": "3. allowRequest()\n[Chặn Spam ≤ 20ms]"},
            {"src": "QnACtrl", "dst": "TranslationSvc", "label": "4. Dịch đáp án\n[translateAnswer()]"},
            {"src": "QnACtrl", "dst": "WSMgr", "label": "5. broadcastToCluster()\n[≤ 400ms]"},
            {"src": "WSMgr", "dst": "SubMap", "label": "Tra cứu sinh viên cụm\n[O(1) Lookup]"},
            {"src": "QnACtrl", "dst": "AnswerDTO", "label": "Đóng gói đáp án song ngữ\n[WebSocket Frame]"}
        ],
        "descriptions": [
            ("Class SessionAuthMiddleware: ", "Phương thức verifyPinOrQR(sessionId, token) kiểm tra mã PIN 6 số động hoặc chữ ký số ngắn hạn trong mã QR để từ chối 100% kết nối không hợp lệ (Kịch bản QA 3.3). Phương thức generateAnonHash() tạo mã băm một chiều Anonymous_Hash_ID, cam kết không lưu họ tên, MSSV, email hay IP cá nhân (Kịch bản QA 3.1)."),
            ("Class AntiSpamRateLimiter: ", "Phương thức allowRequest(anonHashId) giới hạn tối đa 3 câu hỏi/phút trên mỗi phiên ẩn danh, chặn đứng các cuộc tấn công spam trong ≤ 20ms (Kịch bản QA 3.2)."),
            ("Class QnAController & WebSocketBroadcastManager: ", "Khi sinh viên gửi câu hỏi qua submitQuestion(), kết nối WebSocket được đăng ký vào Cluster Subscription Registry qua hàm subscribeCluster(). Khi giảng viên trả lời câu hỏi đại diện qua answerCluster(), hệ thống dịch song ngữ câu trả lời và gọi broadcastToCluster() để đẩy thông báo đồng thời đến 100% sinh viên trong cụm đó trong vòng ≤ 400ms (Kịch bản QA 1.3).")
        ]
    },

    # =========================================================================
    # HÌNH 4.4: CODE DIAGRAM — TỔNG HỢP BÁO CÁO & HEATMAP CUỐI BUỔI
    # =========================================================================
    {
        "id": "Hinh_4_4_Code_Summary_Heatmap",
        "filename": "Hinh_4_4_Code_Summary_Heatmap",
        "tab_name": "Hình 4.4 - Code Summary",
        "level_title": "CẤP ĐỘ 4: CODE DIAGRAM — TỔNG HỢP BÁO CÁO & HEATMAP CUỐI BUỔI",
        "figure_title": "Hình 4.4: Code Diagram — Luồng Tổng hợp Báo cáo & Heatmap Cuối buổi (FR-05 & QA 4.3)",
        "layout_note": "Bố cục cân xứng chuẩn C4: Khung Summary Module ở giữa → 2 Adapter LLM Qwen2.5-7B và LightweightLLM ở 2 cánh Trái – Phải.",
        "canvas_w": 1600,
        "canvas_h": 980,
        "boundaries": [
            {
                "id": "b_code_sum",
                "title": "Session Summary & Heatmap Module",
                "subtitle": "[Code Boundary: FR-05 & QA 4.3]",
                "x": 350, "y": 60, "w": 900, "h": 840
            }
        ],
        "nodes": [
            {
                "id": "SessionRepo",
                "kind": "folder",
                "title": "class SessionRepository",
                "stereo": "[Data Access Class]",
                "lines": [
                    "+ getSessionTranscripts(sessionId): List",
                    "+ getSessionClusters(sessionId): List",
                    "+ saveReport(reportDTO): void"
                ],
                "x": 400, "y": 115, "w": 300, "h": 155
            },
            {
                "id": "HeatmapCalc",
                "kind": "folder",
                "title": "class HeatmapCalculator",
                "stereo": "[Analytics Helper Class]",
                "lines": [
                    "+ alignQuestionsToTimeline(",
                    "    transcripts, clusters): List[HeatmapPoint]"
                ],
                "x": 900, "y": 115, "w": 300, "h": 155
            },
            {
                "id": "SummarySvc",
                "kind": "backend",
                "title": "class SessionSummaryService",
                "stereo": "[Core Summary Service]",
                "lines": [
                    "- llmProvider: ILLMProvider",
                    "- sessionRepo: SessionRepository",
                    "+ generateEndSessionReport(sessionId): ReportDTO",
                    "+ switchLLMProvider(newProvider): void"
                ],
                "x": 570, "y": 375, "w": 460, "h": 170
            },
            {
                "id": "ILLM",
                "kind": "iface",
                "title": "<<interface>> ILLMProvider",
                "stereo": "[Unified LLM Interface]",
                "lines": [
                    "+ summarize(transcript: str, clusters: List): str"
                ],
                "x": 400, "y": 650, "w": 300, "h": 155
            },
            {
                "id": "ReportDTO",
                "kind": "db",
                "title": "class SessionReportDTO",
                "stereo": "[Report & Heatmap Payload]",
                "lines": [
                    "+ sessionId: str | + executiveSummary: str",
                    "+ comprehensionHeatmap: List[HeatmapPoint]",
                    "+ resolvedClusters: List[ClusterDTO]"
                ],
                "x": 900, "y": 650, "w": 300, "h": 155
            },
            {
                "id": "QwenAdapter",
                "kind": "ext",
                "title": "class OllamaQwenAdapter",
                "stereo": "[Implements: ILLMProvider]",
                "lines": [
                    "- endpoint: str",
                    "- modelName: str = 'qwen2.5:7b'",
                    "+ summarize(transcript, clusters): str"
                ],
                "x": 20, "y": 650, "w": 270, "h": 155
            },
            {
                "id": "LightAdapter",
                "kind": "ext",
                "title": "class LightweightLLMAdapter",
                "stereo": "[Implements: ILLMProvider]",
                "lines": [
                    "- localModelPath: str",
                    "- quantizedType: str = 'q4_k_m'",
                    "+ summarize(transcript, clusters): str"
                ],
                "x": 1310, "y": 380, "w": 270, "h": 155
            }
        ],
        "edges": [
            {"src": "SessionRepo", "dst": "SummarySvc", "label": "1. Nạp Transcript & Cụm\n[Async DB Read]"},
            {"src": "HeatmapCalc", "dst": "SummarySvc", "label": "2. Tính mật độ điểm nghẽn\n[alignQuestionsToTimeline()]"},
            {"src": "SummarySvc", "dst": "ILLM", "label": "3. Gọi tóm tắt chung\n[summarize()]"},
            {"src": "SummarySvc", "dst": "ReportDTO", "label": "4. Kết xuất báo cáo\n[Chuẩn hóa JSON / PDF]"},
            {"src": "QwenAdapter", "dst": "ILLM", "label": "Implements\n[Qwen2.5-7B]"},
            {"src": "LightAdapter", "dst": "SummarySvc", "label": "Đổi mô hình nhẹ ≤ 30p\n[Khi thiếu VRAM]"}
        ],
        "descriptions": [
            ("Class SessionSummaryService & HeatmapCalculator: ", "Khi kết thúc buổi học, phương thức generateEndSessionReport(sessionId) truy xuất toàn bộ bản ghi lời giảng (transcript) và danh sách các cụm câu hỏi từ SessionRepository. Đồng thời, phương thức alignQuestionsToTimeline() đối chiếu mật độ câu hỏi của sinh viên theo dòng thời gian bài giảng để tạo dữ liệu biểu đồ nhiệt Comprehension Heatmap (FR-05)."),
            ("Interface ILLMProvider, OllamaQwenAdapter, LightweightLLMAdapter: ", "Chuẩn hóa tầng giao tiếp mô hình ngôn ngữ lớn qua một giao diện thống nhất (Unified LLM Interface). Khi triển khai tại phòng học mới có máy chủ cục bộ thiếu VRAM, nhóm phát triển có thể chuyển đổi từ OllamaQwenAdapter (Qwen2.5-7B) sang LightweightLLMAdapter trong ≤ 30 phút cấu hình mà vẫn giữ nguyên định dạng SessionReportDTO phục vụ hiển thị biểu đồ nhiệt và xuất file PDF lưu trữ (Kịch bản QA 4.3).")
        ]
    }
]
