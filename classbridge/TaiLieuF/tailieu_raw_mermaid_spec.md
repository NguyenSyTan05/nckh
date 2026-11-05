CẤP ĐỘ 1: SYSTEM CONTEXT DIAGRAM (1 HÌNH)Hình 1: System Context Diagram — Ngữ cảnh Hệ thống ClassBridge(Bố cục cân xứng: Sinh viên & Giảng viên ở 2 bên cánh trên $\rightarrow$ Hệ thống ClassBridge ở tâm $\rightarrow$ Thiết bị phòng học & Admin ở dưới).   Đoạn mã%%{init: {'flowchart': {'nodeSpacing': 35, 'rankSpacing': 45, 'padding': 12}, 'themeVariables': {'fontSize': '13px'}}}%%
flowchart TB
    classDef person fill:#f5f9ff,stroke:#1168bd,stroke-width:2px,color:#1168bd,rx:40px,ry:40px;
    classDef sys fill:#eef6ff,stroke:#1168bd,stroke-width:2.5px,color:#0b4884,rx:6px,ry:6px;
    classDef ext fill:#f5f5f5,stroke:#555555,stroke-width:2px,color:#222222,rx:4px,ry:4px;

    %% Hai cánh Trái - Phải phía trên
    Student(("<b>Sinh viên (Student)</b><br/><i>[Person]</i><br/><br/>Xem phụ đề song ngữ,<br/>hỏi ẩn danh & nhận đáp án"))
    Lecturer(("<b>Giảng viên (Lecturer)</b><br/><i>[Person]</i><br/><br/>Giảng bài tiếng Anh, xem cụm<br/>câu hỏi & trả lời 1-nhiều"))

    %% Khung Hệ thống trung tâm ở chính giữa
    subgraph Context_Boundary ["<b>Môi trường Lớp học EMI (Classroom Context)</b>"]
        direction TB
        ClassBridge["<b>ClassBridge System</b><br/><i>[Software System: Self-hosted AI Assistant]</i><br/><br/>Trợ lý AI tự triển khai cục bộ hỗ trợ phụ đề song ngữ<br/>thời gian thực (<= 1.5s), gom nhóm câu hỏi đa ngôn ngữ<br/>(<= 500ms) và tổng hợp báo cáo lớp học EMI"]
    end

    %% Hai cánh Trái - Phải phía dưới (Hệ thống ngoại vi & Admin)
    MicSystem["<b>Classroom Microphone</b><br/><i>[External Hardware]</i><br/><br/>Thu tín hiệu giọng nói<br/>trực tiếp của giảng viên"]
    Admin(("<b>Quản trị viên (Admin)</b><br/><i>[Person]</i><br/><br/>Quản lý tài khoản & tinh chỉnh<br/>ngưỡng mô hình AI"))
    Projector["<b>Classroom Projector</b><br/><i>[External Display]</i><br/><br/>Trình chiếu mã PIN 6 số động,<br/>mã QR & phụ đề tại lớp"]

    %% Luồng kết nối cân xứng 2 bên
    Student -. "Quét QR/PIN, xem phụ đề &<br/>gửi câu hỏi ẩn danh <i>[HTTPS/WSS]</i>" .-> ClassBridge
    Lecturer -. "Tạo phiên học, xem cụm câu hỏi &<br/>gửi câu trả lời đại diện <i>[HTTPS/WSS]</i>" .-> ClassBridge

    MicSystem -. "Truyền luồng âm thanh bài giảng<br/><i>[WebRTC / Audio Stream]</i>" .-> ClassBridge
    Admin -. "Cấu hình tham số AI & phiên học<br/><i>[HTTPS]</i>" .-> ClassBridge
    ClassBridge -. "Hiển thị mã PIN/QR & phụ đề<br/><i>[Browser UI]</i>" .-> Projector

    class Student,Lecturer,Admin person;
    class ClassBridge sys;
    class MicSystem,Projector ext;
    style Context_Boundary fill:none,stroke:#666666,stroke-width:2px,stroke-dasharray: 6 6,color:#333333
Mô tả chi tiết Hình 1 (System Context Diagram)Hệ thống trung tâm (ClassBridge System): Hệ thống trợ lý AI khép kín tự triển khai mô hình mã nguồn mở cục bộ (Self-hosted / In-house AI Inference) giúp phá vỡ rào cản ngôn ngữ và khôi phục vòng phản hồi thời gian thực trong lớp học giảng dạy bằng tiếng Anh (EMI) mà không phụ thuộc vào API thương mại bên ngoài.   Các Tác nhân (Actors):Sinh viên (Student): Truy cập nhanh vào phiên học qua trình duyệt di động bằng mã QR hoặc mã PIN 6 số với định danh tạm thời (Anonymous #ID) mà không cần cài đặt ứng dụng hay đăng nhập. Theo dõi phụ đề song ngữ Anh – Việt trực tiếp, gửi câu hỏi bằng tiếng Việt, tiếng Anh hoặc ngôn ngữ pha trộn (code-switching) và nhận câu trả lời từ giảng viên.   Giảng viên (Lecturer): Khởi tạo phiên học mới, giảng bài trực tiếp bằng tiếng Anh, theo dõi các cụm câu hỏi nóng nhất trên Dashboard và nhập câu trả lời một lần cho câu hỏi đại diện để hệ thống tự động dịch và phát tán (1-nhiều) tới toàn bộ sinh viên trong nhóm đó.   Quản trị viên (Admin): Quản lý danh sách người dùng, lớp học và điều chỉnh động các tham số thuật toán (như ngưỡng tương đồng Cosine Similarity Threshold, đổi mô hình AI) phục vụ thực nghiệm.   Các Hệ thống Ngoại vi (External Systems):Classroom Microphone: Hệ thống thu âm tại giảng đường tiếp nhận giọng nói trực tiếp của giảng viên (kèm tạp âm phòng học) để đẩy vào luồng xử lý âm thanh.   Classroom Projector: Màn chiếu tại lớp hiển thị công khai mã PIN 6 số động (chống người lạ bên ngoài phòng học truy cập trái phép theo Kịch bản QA 3.3) và hiển thị phụ đề song ngữ trực tiếp.   CẤP ĐỘ 2: CONTAINER DIAGRAM (1 HÌNH)Hình 2: Container Diagram — Sơ đồ Kiến trúc Container(Bố cục chuẩn 100% theo hình mẫu của bạn: Sinh viên bên trái, Giảng viên bên phải, Khung ClassBridge System ở giữa gồm 2 UI ở trên $\rightarrow$ Backend ở tâm $\rightarrow$ 2 khối trụ Queue & DB ở đáy $\rightarrow$ 2 khối AI Worker màu xám ở bên cánh trái).   Đoạn mã%%{init: {'flowchart': {'nodeSpacing': 30, 'rankSpacing': 40, 'padding': 10}, 'themeVariables': {'fontSize': '13px'}}}%%
flowchart TB
    classDef person fill:#f5f9ff,stroke:#1168bd,stroke-width:2px,color:#1168bd,rx:35px,ry:35px;
    classDef ui fill:#eef6ff,stroke:#1168bd,stroke-width:2px,color:#0b4884,rx:4px,ry:4px;
    classDef backend fill:#eef6ff,stroke:#1168bd,stroke-width:2px,color:#0b4884,rx:4px,ry:4px;
    classDef db fill:#eef6ff,stroke:#1168bd,stroke-width:2px,color:#0b4884;
    classDef aiworker fill:#f5f5f5,stroke:#555555,stroke-width:2px,color:#222222,rx:4px,ry:4px;

    %% Tác nhân ở 2 cánh Trái - Phải
    Student(("<b>Sinh viên</b><br/><i>[Person]</i><br/>Hỏi đáp ẩn danh &<br/>xem phụ đề"))
    Lecturer(("<b>Giảng viên & Admin</b><br/><i>[Person]</i><br/>Giảng bài, quản lý cụm<br/>câu hỏi & cấu hình"))

    %% Khung Hệ thống ở chính giữa
    subgraph ClassBridge_System ["<b>ClassBridge System</b> <i>[System Boundary]</i>"]
        direction TB
        
        %% Tầng 1: Hai giao diện Web xếp ngang nhau
        StudentUI["<b>Student Mobile Web</b><br/><i>[Container: Next.js / React]</i><br/><br/>Giao diện Zero-Install xem phụ đề,<br/>hỏi ẩn danh & lưu LocalQueue khi rớt mạng"]
        LecturerUI["<b>Lecturer Dashboard</b><br/><i>[Container: Next.js / React]</i><br/><br/>Giao diện thu âm bài giảng, quản lý<br/>cụm câu hỏi, trả lời 1-nhiều & xem Heatmap"]

        %% Tầng 2: Backend ở tâm
        Backend["<b>>_ Backend API & WebSocket</b><br/><i>[Container: Python / FastAPI]</i><br/><br/>Quản lý phiên học, xác thực PIN/JWT,<br/>chống Spam (Rate Limit) & Broadcast<br/>thời gian thực (<= 400ms)"]

        %% Tầng 3: Hai khối trụ Lưu trữ ở đáy
        TaskQueue[("<b>Task Queue & Cache</b><br/><i>[Container: In-Memory / Redis]</i><br/><br/>Hàng đợi sự kiện bất đồng bộ<br/>(0% Queue Drop) & lưu trạng thái")]
        PostgresDB[("<b>Primary Database</b><br/><i>[Container: PostgreSQL]</i><br/><br/>Lưu trữ phiên học, transcript,<br/>cụm câu hỏi (Anonymous_Hash_ID)<br/>và báo cáo tổng kết")]
    end

    %% Hai khối AI Worker cô lập nằm ở cánh bên ngoài
    STTWorker["<b>Speech Processing Worker</b><br/><i>[Container: Silero VAD + Faster-Whisper]</i><br/><br/>Tiến trình cô lập (Worker Isolation):<br/>Lọc khoảng lặng, nhận diện giọng nói<br/>tiếng Anh & dịch sang tiếng Việt"]
    NLPWorker["<b>NLP & LLM Inference Service</b><br/><i>[Container: multilingual-e5-base + Qwen]</i><br/><br/>Trích xuất vector 768 chiều, gom cụm<br/>Cosine Similarity & tổng hợp báo cáo"]

    %% Kết nối cân đối
    Student -. "Truy cập qua trình duyệt di động<br/><i>[HTTPS / WSS]</i>" .-> StudentUI
    Lecturer -. "Truy cập qua trình duyệt máy tính<br/><i>[HTTPS / WSS]</i>" .-> LecturerUI

    StudentUI -. "Gửi câu hỏi & nhận phụ đề/phản hồi<br/><i>[JSON / WebSocket]</i>" .-> Backend
    LecturerUI -. "Truyền Audio chunk & trả lời cụm<br/><i>[JSON / WebSocket]</i>" .-> Backend

    Backend -. "Đẩy Audio chunk & nhận phụ đề<br/><i>[Async Worker Task]</i>" .-> STTWorker
    Backend -. "Gửi câu hỏi để phân cụm & tạo báo cáo<br/><i>[Async Worker Task]</i>" .-> NLPWorker

    Backend -. "Đẩy/Đọc hàng đợi sự kiện<br/><i>[Async I/O]</i>" .-> TaskQueue
    Backend -. "Đọc và ghi dữ liệu vào<br/><i>[SQL / Asyncpg]</i>" .-> PostgresDB

    class Student,Lecturer person;
    class StudentUI,LecturerUI ui;
    class Backend backend;
    class TaskQueue,PostgresDB db;
    class STTWorker,NLPWorker aiworker;
    style ClassBridge_System fill:none,stroke:#666666,stroke-width:2px,stroke-dasharray: 6 6,color:#333333
Mô tả chi tiết Hình 2 (Container Diagram)Student Mobile Web (Next.js / React): Ứng dụng web siêu nhẹ chạy trực tiếp trên trình duyệt điện thoại (Zero-Install). Tích hợp cơ chế lưu tạm câu hỏi vào Local Storage Queue và tự động kết nối lại (Auto-reconnect) để đảm bảo 0% mất mát câu hỏi và đồng bộ lại phòng học trong $\le 2\text{s}$ khi mạng Wi-Fi giảng đường bị ngắt quãng (Kịch bản QA 2.2).   Lecturer Dashboard (Next.js / React): Giao diện dành cho giảng viên thu âm giọng giảng, theo dõi các cụm câu hỏi được cập nhật trực tiếp, gửi câu trả lời đại diện 1-nhiều và xem biểu đồ nhiệt điểm nghẽn kiến thức (Comprehension Heatmap) cuối buổi.   Backend API & WebSocket (Python / FastAPI): Trái tim điều phối của hệ thống. Quản lý vòng đời phiên học, xác thực mã PIN 6 số động, cấp mã ẩn danh một chiều (Anonymous_Hash_ID), chặn đứng tấn công spam vượt ngưỡng 3 câu/phút trong $\le 20\text{ms}$ (Kịch bản QA 3.2) và phát tán câu trả lời 1-nhiều qua WebSocket trong $\le 400\text{ms}$ (Kịch bản QA 1.3).   Speech Processing Worker (Silero VAD + Faster-Whisper): Container độc lập xử lý âm thanh. Được tách rời hoàn toàn (Worker Isolation) để nếu tiến trình STT gặp lỗi tràn bộ nhớ (OOM), hệ thống tự động giải phóng bộ nhớ và khởi động lại trong $\le 5\text{s}$ mà không làm gián đoạn luồng Hỏi đáp Q&A (Kịch bản QA 2.1).   NLP & LLM Inference Service (multilingual-e5-base + Qwen/Ollama): Dịch vụ AI trích xuất vector ngữ nghĩa 768 chiều, gom cụm câu hỏi bằng khoảng cách Cosine trong $\le 500\text{ms}$ (Kịch bản QA 1.2) và tổng hợp báo cáo bài giảng cuối buổi (FR-05).   Task Queue & Cache (In-Memory / Redis): Hàng đợi sự kiện trung gian đảm bảo 0% rớt hàng đợi (0% Queue Drop) khi 40 sinh viên gửi câu hỏi dồn dập cùng lúc.   Primary Database (PostgreSQL): Lưu trữ bền vững thông tin phiên học, bản ghi lời giảng (transcript), các cụm câu hỏi (chỉ lưu Anonymous_Hash_ID, cam kết 0% khả năng truy vết ngược danh tính thật theo Kịch bản QA 3.1) và dữ liệu biểu đồ nhiệt cuối buổi.   CẤP ĐỘ 3: COMPONENT DIAGRAM (3 HÌNH RIÊNG BIỆT CHO 3 CONTAINER LÕI)Hình 3.1: Component Diagram — Backend API & WebSocket Server(Phóng to bên trong Backend API & WebSocket Server với bố cục đối xứng Trái – Giữa – Phải).   Đoạn mã%%{init: {'flowchart': {'nodeSpacing': 28, 'rankSpacing': 38, 'padding': 10}, 'themeVariables': {'fontSize': '13px'}}}%%
flowchart TB
    classDef ui fill:#eef6ff,stroke:#1168bd,stroke-width:2px,color:#0b4884,rx:4px,ry:4px;
    classDef comp fill:#eef6ff,stroke:#1168bd,stroke-width:2px,color:#0b4884,rx:4px,ry:4px;
    classDef db fill:#eef6ff,stroke:#1168bd,stroke-width:2px,color:#0b4884;
    classDef extworker fill:#f5f5f5,stroke:#555555,stroke-width:2px,color:#222222,rx:4px,ry:4px;

    %% Hai khối Giao diện ở 2 cánh trên
    StudentUI["<b>Student Mobile Web</b><br/><i>[Container: Next.js]</i><br/>Gửi câu hỏi ẩn danh &<br/>nhận phụ đề / đáp án"]
    LecturerUI["<b>Lecturer Dashboard</b><br/><i>[Container: Next.js]</i><br/>Truyền Audio, quản lý cụm<br/>& gửi câu trả lời 1-nhiều"]

    %% Khung Backend Container ở chính giữa (3 tầng x 2 cột cân đối)
    subgraph Backend_Boundary ["<b>Backend API & WebSocket Server</b> <i>[Container Boundary: FastAPI]</i>"]
        direction TB
        
        %% Tầng 1: Bảo mật & Chống Spam
        AuthGuard["<b>Auth & Anonymizer</b><br/><i>[Component: Security Middleware]</i><br/><br/>Kiểm tra mã PIN 6 số động / QR<br/>& băm một chiều Anonymous_Hash_ID"]
        RateLimiter["<b>Anti-Spam Rate Limiter</b><br/><i>[Component: Token Bucket]</i><br/><br/>Giới hạn tối đa 3 câu hỏi/phút,<br/>chặn Flooding Attack <= 20ms"]

        %% Tầng 2: Điều phối trung tâm
        SessionCtrl["<b>>_ Session & QnA Controller</b><br/><i>[Component: FastAPI Router]</i><br/><br/>Điều phối tạo phiên học, nhận câu hỏi,<br/>xử lý câu trả lời đại diện & báo cáo"]
        WSManager["<b>>_ WebSocket Broadcast Engine</b><br/><i>[Component: WebSocket Manager]</i><br/><br/>Quản lý Room phòng học & phát tán<br/>phụ đề / đáp án 1-nhiều (<= 400ms)"]

        %% Tầng 3: Cấu hình động & Truy xuất DB
        ConfigMgr[("<b>Dynamic Config Manager</b><br/><i>[Component: Runtime Settings]</i><br/><br/>Đổi nóng ngưỡng Cosine<br/>(0.65 -> 0.75) trong <= 5p")]
        Repo[("<b>Data Access Repository</b><br/><i>[Component: SQLAlchemy Async]</i><br/><br/>Đọc/Ghi phiên học, cụm câu hỏi<br/>và báo cáo tổng kết")]
    end

    %% Các khối ngoại vi ở cánh trái, cánh phải và đáy
    STTWorker["<b>Speech Processing Worker</b><br/><i>[Container: VAD + Whisper]</i><br/>Xử lý âm thanh & dịch phụ đề"]
    NLPWorker["<b>NLP & LLM Service</b><br/><i>[Container: e5-base + Qwen]</i><br/>Gom cụm Cosine & tạo Heatmap"]
    PostgresDB[("<b>Primary Database</b><br/><i>[Container: PostgreSQL]</i><br/>Lưu trữ dữ liệu bền vững")]

    %% Luồng kết nối cân xứng
    StudentUI -. "Gửi câu hỏi + PIN<br/><i>[HTTPS / REST]</i>" .-> AuthGuard
    LecturerUI -. "Quản lý & Trả lời<br/><i>[HTTPS / REST]</i>" .-> AuthGuard
    StudentUI -. "Nhận phụ đề & đáp án<br/><i>[WebSocket]</i>" .-> WSManager
    LecturerUI -. "Truyền Audio & nhận cụm<br/><i>[WebSocket]</i>" .-> WSManager

    AuthGuard -. "Gắn Anonymous_Hash_ID" .-> RateLimiter
    RateLimiter -. "Chuyển câu hỏi hợp lệ" .-> SessionCtrl
    SessionCtrl -. "Kích hoạt Broadcast 1-nhiều" .-> WSManager

    WSManager -. "Đẩy Audio & nhận phụ đề<br/><i>[Async Worker Task]</i>" .-> STTWorker
    SessionCtrl -. "Phân cụm & tóm tắt báo cáo<br/><i>[Async Worker Task]</i>" .-> NLPWorker

    SessionCtrl -. "Đọc/Cập nhật ngưỡng" .-> ConfigMgr
    SessionCtrl -. "Gọi lưu trữ dữ liệu" .-> Repo
    Repo -. "Truy vấn SQL bất đồng bộ" .-> PostgresDB

    class StudentUI,LecturerUI ui;
    class AuthGuard,RateLimiter,SessionCtrl,WSManager comp;
    class ConfigMgr,Repo,PostgresDB db;
    class STTWorker,NLPWorker extworker;
    style Backend_Boundary fill:none,stroke:#666666,stroke-width:2px,stroke-dasharray: 6 6,color:#333333
Mô tả chi tiết Hình 3.1 (Component Diagram - Backend API & WebSocket Server)Auth & Anonymizer (Security Middleware): Xác thực mã PIN 6 số động hoặc chữ ký số ngắn hạn trong mã QR để từ chối 100% kết nối trái phép từ bên ngoài lớp học (Kịch bản QA 3.3). Sinh mã định danh băm một chiều Anonymous_Hash_ID cho sinh viên, đảm bảo 0% khả năng truy vết ngược danh tính cá nhân (Kịch bản QA 3.1).   Anti-Spam Rate Limiter (Token Bucket): Kiểm soát tần suất gửi câu hỏi theo từng Anonymous_Hash_ID (tối đa 3 câu/phút), lập tức từ chối các request vượt ngưỡng trong $\le 20\text{ms}$ trước khi đi vào mô hình AI (Kịch bản QA 3.2).   Session & QnA Controller (FastAPI Router): Xử lý các yêu cầu REST API khởi tạo phiên học, tiếp nhận câu hỏi hợp lệ đẩy sang dịch vụ NLP, nhận câu trả lời đại diện từ giảng viên và kích hoạt tổng hợp báo cáo cuối buổi.   WebSocket Broadcast Engine (WebSocket Manager): Duy trì kết nối WebSocket với 60–100 thiết bị theo cấu trúc Phòng học (Room) và Nhóm câu hỏi (Cluster Group), đảm bảo phát tán câu trả lời 1-nhiều tới đúng sinh viên trong cụm trong vòng $\le 400\text{ms}$ (Kịch bản QA 1.3).   Dynamic Config Manager (Runtime Settings): Quản lý các tham số động, cho phép nhóm nghiên cứu tinh chỉnh ngưỡng tương đồng ngữ nghĩa (Similarity Threshold từ $0.65 \rightarrow 0.75$) ngay giữa các ca học thực nghiệm trong $\le 5$ phút mà không cần biên dịch lại hệ thống (Kịch bản QA 4.2).   Data Access Repository (SQLAlchemy Async): Đóng gói toàn bộ truy vấn đọc/ghi phiên học, lịch sử câu hỏi và báo cáo xuống PostgreSQL.   Hình 3.2: Component Diagram — Speech Processing Worker (Tính năng lõi FR-02)(Phóng to bên trong Speech Processing Worker với luồng xử lý cân đối).   Đoạn mã%%{init: {'flowchart': {'nodeSpacing': 28, 'rankSpacing': 38, 'padding': 10}, 'themeVariables': {'fontSize': '13px'}}}%%
flowchart TB
    classDef comp fill:#eef6ff,stroke:#1168bd,stroke-width:2px,color:#0b4884,rx:4px,ry:4px;
    classDef db fill:#eef6ff,stroke:#1168bd,stroke-width:2px,color:#0b4884;
    classDef ext fill:#f5f5f5,stroke:#555555,stroke-width:2px,color:#222222,rx:4px,ry:4px;

    %% Hai khối ngoại vi ở 2 cánh Trái - Phải
    AudioInput["<b>Task Queue (Audio Stream)</b><br/><i>[Container: Async Queue]</i><br/><br/>Cung cấp các đoạn âm thanh<br/>cắt ngắn (3-5 giây) từ giảng viên"]
    WSOutput["<b>WebSocket Broadcast Engine</b><br/><i>[Container: FastAPI Server]</i><br/><br/>Nhận phụ đề song ngữ để đẩy<br/>lên màn chiếu & điện thoại"]

    %% Khung Container chính ở giữa (3 tầng x 2 cột)
    subgraph STT_Boundary ["<b>Speech Processing Worker</b> <i>[Container Boundary: Isolated Python Worker]</i>"]
        direction TB
        
        %% Tầng 1: Thu nhận & Lọc khoảng lặng
        AudioConsumer["<b>Audio Stream Consumer</b><br/><i>[Component: Async Worker]</i><br/><br/>Nhận Audio Chunk (3-5s) và<br/>chuẩn hóa tần số lấy mẫu 16kHz"]
        VADGate["<b>VAD Audio Gate</b><br/><i>[Component: Silero VAD]</i><br/><br/>Phát hiện giọng nói giảng viên,<br/>ngắt luồng khi im lặng chống ảo giác"]

        %% Tầng 2: Nhận diện Whisper & Dịch thuật
        WhisperEngine["<b>>_ STT Inference Engine</b><br/><i>[Component: Faster-Whisper]</i><br/><br/>Chuyển đổi giọng nói tiếng Anh<br/>sang văn bản với độ trễ thấp"]
        TermTranslator["<b>>_ Bilingual Translator</b><br/><i>[Component: NLLB / MarianMT]</i><br/><br/>Dịch phụ đề tiếng Anh sang tiếng Việt,<br/>bảo toàn thuật ngữ chuyên ngành IT"]

        %% Tầng 3: Giám sát lỗi & Bộ đệm bản ghi
        MemoryGuard[("<b>Worker Health & Memory Guard</b><br/><i>[Component: Fault Supervisor]</i><br/><br/>Giám sát tràn bộ nhớ (OOM)<br/>& tự khởi động lại STT <= 5s")]
        TranscriptStore[("<b>Transcript Buffer</b><br/><i>[Component: Batch Writer]</i><br/><br/>Đệm bản ghi lời giảng kèm<br/>dấu thời gian (Timestamp)")]
    end

    PostgresDB[("<b>Primary Database</b><br/><i>[Container: PostgreSQL]</i><br/><br/>Lưu trữ toàn bộ bản ghi<br/>lời giảng phục vụ báo cáo")]

    %% Luồng kết nối
    AudioInput -. "1. Đẩy Audio Chunk (3-5s)<br/><i>[Async Worker Task]</i>" .-> AudioConsumer
    AudioConsumer -. "2. Truyền luồng 16kHz<br/><i>[PCM Bytes]</i>" .-> VADGate
    VADGate -. "3. Chỉ đẩy đoạn có giọng nói<br/><i>[Filtered Audio]</i>" .-> WhisperEngine
    WhisperEngine -. "4. Văn bản tiếng Anh<br/><i>[Raw Transcript]</i>" .-> TermTranslator

    TermTranslator -. "5. Trả phụ đề song ngữ (<= 1.5s)<br/><i>[JSON Payload]</i>" .-> WSOutput
    
    MemoryGuard -. "Giám sát & tự khôi phục OOM<br/><i>[Process Watchdog]</i>" .-> WhisperEngine
    TermTranslator -. "Ghi nhận câu thoại<br/><i>[Async I/O]</i>" .-> TranscriptStore
    TranscriptStore -. "Lưu bản ghi lời giảng<br/><i>[SQL / Asyncpg]</i>" .-> PostgresDB

    class AudioConsumer,VADGate,WhisperEngine,TermTranslator comp;
    class MemoryGuard,TranscriptStore,PostgresDB db;
    class AudioInput,WSOutput ext;
    style STT_Boundary fill:none,stroke:#666666,stroke-width:2px,stroke-dasharray: 6 6,color:#333333
Mô tả chi tiết Hình 3.2 (Component Diagram - Speech Processing Worker)Audio Stream Consumer (Async Worker): Nhận luồng âm thanh cắt theo khung 3–5 giây từ hàng đợi sự kiện và chuẩn hóa về định dạng 16kHz mono.   VAD Audio Gate (Silero VAD): Cổng kiểm soát âm thanh giúp phát hiện khi giảng viên dừng giảng bài (micro chỉ thu tiếng quạt máy và tiếng thảo luận nhỏ) để tự động ngắt luồng đẩy sang Whisper, đảm bảo 0 dòng phụ đề rác/ảo giác (Hallucination) và tiết kiệm $\ge 80\%$ tài nguyên GPU/CPU (Kịch bản QA 2.3).   STT Inference Engine (Faster-Whisper): Giải mã các đoạn âm thanh có giọng nói hợp lệ thành văn bản tiếng Anh với tốc độ cao.   Bilingual Translator (NLLB / MarianMT): Dịch văn bản tiếng Anh sang tiếng Việt (bảo toàn thuật ngữ chuyên ngành IT), đảm bảo tổng độ trễ đầu-cuối từ lúc giảng viên ngắt câu đến khi hiển thị phụ đề đạt $\le 1.5\text{s}$ (Kịch bản QA 1.1).   Worker Health & Memory Guard & Transcript Buffer: Thực thi cơ chế cô lập lỗi (Fault Isolation); nếu tiến trình STT gặp lỗi tràn bộ nhớ (OOM) hoặc treo do âm thanh nhiễu kéo dài, bộ giám sát tự động giải phóng bộ nhớ và khởi động lại STT Worker trong $\le 5\text{s}$ mà không ảnh hưởng đến luồng Hỏi đáp (Kịch bản QA 2.1), đồng thời lưu bản ghi lời giảng vào PostgreSQL.   Hình 3.3: Component Diagram — NLP & LLM Inference Service (Tính năng lõi FR-03 & FR-05)(Phóng to bên trong NLP & LLM Inference Service với bố cục cân đối Trái – Giữa – Phải).   Đoạn mã%%{init: {'flowchart': {'nodeSpacing': 28, 'rankSpacing': 38, 'padding': 10}, 'themeVariables': {'fontSize': '13px'}}}%%
flowchart TB
    classDef comp fill:#eef6ff,stroke:#1168bd,stroke-width:2px,color:#0b4884,rx:4px,ry:4px;
    classDef db fill:#eef6ff,stroke:#1168bd,stroke-width:2px,color:#0b4884;
    classDef ext fill:#f5f5f5,stroke:#555555,stroke-width:2px,color:#222222,rx:4px,ry:4px;

    %% Hai khối ngoại vi ở 2 cánh Trái - Phải
    QuestionInput["<b>Session & QnA Controller</b><br/><i>[Container: FastAPI Backend]</i><br/><br/>Gửi câu hỏi ẩn danh mới &<br/>yêu cầu tổng kết cuối buổi"]
    DashboardOut["<b>Lecturer Dashboard</b><br/><i>[Container: Next.js UI]</i><br/><br/>Hiển thị danh sách cụm câu hỏi<br/>nóng nhất & biểu đồ Heatmap"]

    %% Khung Container chính ở giữa (3 tầng x 2 cột)
    subgraph NLP_Boundary ["<b>NLP & LLM Inference Service</b> <i>[Container Boundary: Self-hosted AI Service]</i>"]
        direction TB
        
        %% Tầng 1: Tiền xử lý & Trích xuất Vector
        TextNorm["<b>Multilingual Text Normalizer</b><br/><i>[Component: Preprocessor]</i><br/><br/>Chuẩn hóa câu hỏi tiếng Việt, Anh<br/>& pha trộn thuật ngữ (Code-switching)"]
        EmbedAdapter["<b>Embedding Model Adapter</b><br/><i>[Component: Strategy Pattern]</i><br/><br/>Trích xuất vector ngữ nghĩa 768 chiều<br/>(Hỗ trợ đổi e5-base / LaBSE)"]

        %% Tầng 2: Gom cụm Cosine & Tổng hợp LLM
        ClusterEngine["<b>>_ Semantic Clustering Engine</b><br/><i>[Component: Cosine Similarity]</i><br/><br/>So khớp vector với tâm cụm hiện tại,<br/>gộp cụm hoặc tạo mới trong <= 500ms"]
        LLMSummarizer["<b>>_ Unified LLM Summarizer</b><br/><i>[Component: Qwen2.5-7B / Ollama]</i><br/><br/>Tổng hợp nội dung bài giảng cuối buổi<br/>& tính toán Comprehension Heatmap"]

        %% Tầng 3: Quản lý Tâm cụm & Xuất báo cáo
        CentroidStore[("<b>Cluster Centroid Cache</b><br/><i>[Component: Vector State]</i><br/><br/>Lưu giữ và cập nhật vector tâm<br/>của các cụm trong phiên học")]
        ReportBuilder[("<b>Report & Heatmap Exporter</b><br/><i>[Component: JSON / PDF Builder]</i><br/><br/>Đóng gói dữ liệu biểu đồ nhiệt<br/>và biên bản buổi học")]
    end

    PostgresDB[("<b>Primary Database</b><br/><i>[Container: PostgreSQL]</i><br/><br/>Lưu trữ danh sách cụm câu hỏi<br/>và báo cáo tổng kết ca học")]

    %% Luồng kết nối
    QuestionInput -. "1. Gửi câu hỏi ẩn danh mới<br/><i>[Async Worker Task]</i>" .-> TextNorm
    TextNorm -. "2. Chuỗi văn bản đã làm sạch<br/><i>[Normalized Text]</i>" .-> EmbedAdapter
    EmbedAdapter -. "3. Truyền Vector 768 chiều<br/><i>[Float Array]</i>" .-> ClusterEngine

    QuestionInput -. "Kích hoạt tổng kết cuối buổi<br/><i>[End Session Event]</i>" .-> LLMSummarizer
    ClusterEngine -. "4. Cập nhật cụm câu hỏi (<= 500ms)<br/><i>[WebSocket Push]</i>" .-> DashboardOut
    LLMSummarizer -. "Trả dữ liệu Heatmap & Tóm tắt<br/><i>[JSON Response]</i>" .-> DashboardOut

    ClusterEngine -. "Đọc và cập nhật tâm cụm<br/><i>[Centroid Update]</i>" .-> CentroidStore
    LLMSummarizer -. "Kết xuất báo cáo tổng hợp<br/><i>[Structured JSON]</i>" .-> ReportBuilder
    CentroidStore -. "Đồng bộ cụm câu hỏi<br/><i>[SQL / Asyncpg]</i>" .-> PostgresDB
    ReportBuilder -. "Lưu trữ báo cáo & Heatmap<br/><i>[SQL / Asyncpg]</i>" .-> PostgresDB

    class TextNorm,EmbedAdapter,ClusterEngine,LLMSummarizer comp;
    class CentroidStore,ReportBuilder,PostgresDB db;
    class QuestionInput,DashboardOut ext;
    style NLP_Boundary fill:none,stroke:#666666,stroke-width:2px,stroke-dasharray: 6 6,color:#333333
Mô tả chi tiết Hình 3.3 (Component Diagram - NLP & LLM Inference Service)Multilingual Text Normalizer (Preprocessor): Tiền xử lý văn bản câu hỏi tự do của sinh viên, chuẩn hóa từ viết tắt và cấu trúc pha trộn Việt – Anh (code-switching).   Embedding Model Adapter (Strategy Pattern): Chuyển đổi văn bản câu hỏi thành vector ngữ nghĩa 768 chiều. Áp dụng mẫu thiết kế Strategy/Adapter Pattern giúp nhóm phát triển dễ dàng thay thế mô hình giữa LaBSE và intfloat/multilingual-e5-base trong $\le 1$ giờ làm việc để chạy Benchmark đo các chỉ số ARI, NMI, Silhouette Score mà không sửa code phân cụm (Kịch bản QA 4.1).   Semantic Clustering Engine (Cosine Similarity): Tính khoảng cách Cosine giữa vector câu hỏi mới với tâm các cụm hiện tại (Cluster Centroid Cache), tự động gộp vào cụm tương đồng hoặc khởi tạo cụm mới và cập nhật lên Dashboard giảng viên trong $\le 500\text{ms}$ với 0% rớt hàng đợi (Kịch bản QA 1.2).   Unified LLM Summarizer & Report Exporter: Sử dụng giao diện LLM chuẩn hóa (Unified LLM Interface) gọi mô hình cục bộ (Qwen2.5-7B qua Ollama) tổng hợp nội dung bài giảng và tạo dữ liệu Comprehension Heatmap, cho phép chuyển đổi sang mô hình gọn nhẹ hơn trong $\le 30$ phút cấu hình khi máy chủ thiếu VRAM (FR-05 & Kịch bản QA 4.3).   CẤP ĐỘ 4: CODE DIAGRAM (4 HÌNH CHO 4 LUỒNG XỬ LÝ LÕI)Hình 4.1: Code Diagram — Luồng Phụ đề Song ngữ & VAD Gate Chống ảo giác (FR-02)(Bố cục cân xứng: Khung Module ở giữa $\rightarrow$ Worker Controller ở tâm $\rightarrow$ 2 Adapter thực thi ở 2 cánh Trái – Phải).   Đoạn mã%%{init: {'flowchart': {'nodeSpacing': 28, 'rankSpacing': 38, 'padding': 10}, 'themeVariables': {'fontSize': '13px'}}}%%
flowchart TB
    classDef ctrl fill:#eef6ff,stroke:#1168bd,stroke-width:2px,color:#0b4884,rx:4px,ry:4px;
    classDef iface fill:#ffffff,stroke:#1168bd,stroke-width:2px,stroke-dasharray: 4 4,color:#0b4884,rx:4px,ry:4px;
    classDef impl fill:#f5f5f5,stroke:#555555,stroke-width:2px,color:#222222,rx:4px,ry:4px;
    classDef dto fill:#eef6ff,stroke:#1168bd,stroke-width:2px,color:#0b4884;

    %% Hai Class Adapter nằm cân xứng ở 2 cánh Trái - Phải
    FasterWhisper["<b>class FasterWhisperEngine</b><br/><i>[Implements: ISTTEngine]</i><br/><br/>- model: WhisperModel<br/>- computeType: str = 'int8_float16'<br/>+ transcribe(audioBytes): str<br/>+ reloadModel(): void"]
    NLLBAdapter["<b>class NLLBTranslatorAdapter</b><br/><i>[Implements: ITranslator]</i><br/><br/>- model: AutoModelForSeq2SeqLM<br/>- tokenizer: AutoTokenizer<br/>+ translateEnToVi(text): str"]

    %% Khung Code Module ở chính giữa
    subgraph Speech_Code_Module ["<b>Speech Processing Module</b> <i>[Code Boundary: FR-02 & QA 1.1, 2.1, 2.3]</i>"]
        direction TB
        
        %% Tầng 1: VAD Gate & Memory Guard
        VADGate["<b>class SileroVADGate</b><br/><i>[VAD Filter Class]</i><br/><br/>- probThreshold: float = 0.5<br/>+ isHumanSpeech(audioBytes): bool<br/>+ trimSilence(audioBytes): bytes"]
        MemGuard["<b>class WorkerMemoryGuard</b><br/><i>[Fault Isolation Class]</i><br/><br/>- maxVramLimitMB: int<br/>+ checkMemory(engine): bool<br/>+ recoverOnOOM(engine): void"]

        %% Tầng 2: Worker Controller ở tâm
        Worker["<b>>_ class SpeechPipelineWorker</b><br/><i>[Core Worker Controller]</i><br/><br/>- vadGate: SileroVADGate<br/>- sttEngine: ISTTEngine<br/>- translator: ITranslator<br/>+ processAudioChunk(sessionId, audio): SubtitleDTO"]

        %% Tầng 3: Interfaces ở đáy khung
        ISTT["<b>&lt;&lt;interface&gt;&gt; ISTTEngine</b><br/><i>[STT Strategy Interface]</i><br/><br/>+ transcribe(audioBytes: bytes): str"]
        ITrans["<b>&lt;&lt;interface&gt;&gt; ITranslator</b><br/><i>[Translation Interface]</i><br/><br/>+ translateEnToVi(text: str): str"]
    end

    SubDTO[("<b>class SubtitlePayloadDTO</b><br/><i>[Data Transfer Object]</i><br/><br/>+ sessionId: str<br/>+ englishText: str<br/>+ vietnameseText: str<br/>+ timestamp: float")]

    %% Luồng gọi phương thức
    VADGate -. "1. Kiểm tra isHumanSpeech()<br/><i>[Chặn 100% ảo giác]</i>" .-> Worker
    MemGuard -. "2. Giám sát recoverOnOOM()<br/><i>[Tự phục hồi <= 5s]</i>" .-> Worker

    Worker -. "3. Gọi transcribe()<br/><i>[Polymorphic Call]</i>" .-> ISTT
    Worker -. "4. Gọi translateEnToVi()<br/><i>[Polymorphic Call]</i>" .-> ITrans
    Worker -. "5. Đóng gói kết quả (<= 1.5s)<br/><i>[Instantiates]</i>" .-> SubDTO

    FasterWhisper -. "Implements Interface<br/><i>[CTranslate2 Engine]</i>" .-> ISTT
    NLLBAdapter -. "Implements Interface<br/><i>[Bilingual Model]</i>" .-> ITrans

    class VADGate,MemGuard,Worker ctrl;
    class ISTT,ITrans iface;
    class FasterWhisper,NLLBAdapter impl;
    class SubDTO dto;
    style Speech_Code_Module fill:none,stroke:#666666,stroke-width:2px,stroke-dasharray: 6 6,color:#333333
Mô tả chi tiết Hình 4.1 (Code Diagram - Luồng Phụ đề Song ngữ & VAD Gate)Class SpeechPipelineWorker: Điều phối luồng xử lý âm thanh thông qua phương thức processAudioChunk(sessionId, audio). Luôn kiểm tra âm thanh qua vadGate.isHumanSpeech(audioBytes) trước tiên; nếu giảng viên đang im lặng (trả về False), phương thức lập tức thoát sớm (Early Return) để ngăn chặn 100% lỗi sinh văn bản ảo giác (Kịch bản QA 2.3).   Class SileroVADGate: Chứa phương thức isHumanSpeech() tính xác suất có giọng nói con người so với ngưỡng probThreshold = 0.5 và phương thức trimSilence() cắt bỏ khoảng lặng thừa ở hai đầu đoạn âm thanh.   Class WorkerMemoryGuard: Cung cấp phương thức recoverOnOOM(engine) bắt ngoại lệ tràn bộ nhớ (Out-of-Memory), tự động giải phóng VRAM và gọi reloadModel() để khôi phục tiến trình STT trong vòng $\le 5\text{s}$ mà không ảnh hưởng tới luồng Hỏi đáp (Kịch bản QA 2.1).   Interface ISTTEngine (FasterWhisperEngine) & ITranslator (NLLBTranslatorAdapter): Thực hiện nhận diện giọng nói tiếng Anh qua transcribe() và dịch sang tiếng Việt qua translateEnToVi(), trả về đối tượng SubtitlePayloadDTO với tổng độ trễ $\le 1.5\text{s}$ (Kịch bản QA 1.1).   Hình 4.2: Code Diagram — Luồng Gom nhóm Câu hỏi Ngữ nghĩa Đa ngôn ngữ (FR-03 & QA 4)(Bố cục cân xứng: Khung Clustering Module ở giữa $\rightarrow$ 2 Adapter mô hình e5-base và LaBSE ở 2 cánh Trái – Phải).   Đoạn mã%%{init: {'flowchart': {'nodeSpacing': 28, 'rankSpacing': 38, 'padding': 10}, 'themeVariables': {'fontSize': '13px'}}}%%
flowchart TB
    classDef ctrl fill:#eef6ff,stroke:#1168bd,stroke-width:2px,color:#0b4884,rx:4px,ry:4px;
    classDef iface fill:#ffffff,stroke:#1168bd,stroke-width:2px,stroke-dasharray: 4 4,color:#0b4884,rx:4px,ry:4px;
    classDef impl fill:#f5f5f5,stroke:#555555,stroke-width:2px,color:#222222,rx:4px,ry:4px;
    classDef entity fill:#eef6ff,stroke:#1168bd,stroke-width:2px,color:#0b4884;

    %% Hai Class Adapter mô hình AI nằm cân xứng ở 2 bên cánh
    E5Adapter["<b>class MultilingualE5Adapter</b><br/><i>[Implements: IEmbeddingStrategy]</i><br/><br/>- e5Model: AutoModel<br/>+ encode(text): List[float]<br/>- addQueryPrefix(text): str"]
    LaBSEAdapter["<b>class LaBSEAdapter</b><br/><i>[Implements: IEmbeddingStrategy]</i><br/><br/>- labseModel: SentenceTransformer<br/>+ encode(text): List[float]"]

    %% Khung Module chính ở giữa
    subgraph Clustering_Code_Module ["<b>Semantic Question Clustering Module</b> <i>[Code Boundary: FR-03 & QA 1.2, 4.1, 4.2]</i>"]
        direction TB
        
        %% Tầng 1: Cấu hình động & Tiền xử lý
        ConfigMgr["<b>class DynamicConfigManager</b><br/><i>[Runtime Config Class]</i><br/><br/>- similarityThreshold: float = 0.75<br/>+ getThreshold(): float<br/>+ setThreshold(newVal: float): void"]
        Normalizer["<b>class MultilingualNormalizer</b><br/><i>[Text Preprocessor Class]</i><br/><br/>+ cleanCodeSwitching(text: str): str"]

        %% Tầng 2: Engine gom cụm trực tuyến ở tâm
        ClusterEngine["<b>>_ class OnlineClusteringEngine</b><br/><i>[Core Clustering Service]</i><br/><br/>- embedStrategy: IEmbeddingStrategy<br/>- configMgr: DynamicConfigManager<br/>+ assignOrCreateCluster(q, clusters): QuestionCluster<br/>+ computeCosine(vecA, vecB): float<br/>+ updateCentroid(cluster, newVec): void"]

        %% Tầng 3: Strategy Interface & Cluster Entity
        IEmbed["<b>&lt;&lt;interface&gt;&gt; IEmbeddingStrategy</b><br/><i>[Strategy Pattern Interface]</i><br/><br/>+ encode(text: str): List[float]"]
        ClusterEntity[("<b>class QuestionCluster</b><br/><i>[Domain Entity]</i><br/><br/>+ clusterId: str<br/>+ representativeText: str<br/>+ centroidVector: List[float]<br/>+ subscriberAnonIds: List[str]<br/>+ addQuestion(q): void")]
    end

    QuestionEntity[("<b>class QuestionEntity</b><br/><i>[Domain Entity]</i><br/><br/>+ questionId: str<br/>+ anonymousHashId: str<br/>+ rawContent: str<br/>+ embeddingVector: List[float]")]

    %% Luồng gọi phương thức
    ConfigMgr -. "1. Đọc ngưỡng getThreshold()<br/><i>[Đổi nóng 0.65 -> 0.75 <= 5p]</i>" .-> ClusterEngine
    Normalizer -. "2. Làm sạch câu hỏi đa ngôn ngữ<br/><i>[cleanCodeSwitching()]</i>" .-> ClusterEngine

    ClusterEngine -. "3. Trích xuất Vector 768 chiều<br/><i>[encode(text)]</i>" .-> IEmbed
    ClusterEngine -. "4. Gộp cụm hoặc khởi tạo mới<br/><i>[<= 500ms / câu hỏi]</i>" .-> ClusterEntity
    ClusterEntity -. "Quản lý các câu hỏi thành viên<br/><i>[1-to-Many Composition]</i>" .-> QuestionEntity

    E5Adapter -. "Implements Strategy<br/><i>[intfloat/multilingual-e5-base]</i>" .-> IEmbed
    LaBSEAdapter -. "Implements Strategy<br/><i>[sentence-transformers/LaBSE]</i>" .-> IEmbed

    class ConfigMgr,Normalizer,ClusterEngine ctrl;
    class IEmbed iface;
    class E5Adapter,LaBSEAdapter impl;
    class ClusterEntity,QuestionEntity entity;
    style Clustering_Code_Module fill:none,stroke:#666666,stroke-width:2px,stroke-dasharray: 6 6,color:#333333
Mô tả chi tiết Hình 4.2 (Code Diagram - Luồng Gom nhóm Câu hỏi Ngữ nghĩa Đa ngôn ngữ)Class OnlineClusteringEngine: Chứa thuật toán phân cụm trực tuyến qua phương thức assignOrCreateCluster(q, clusters). Phương thức này gọi embedStrategy.encode() để lấy vector 768 chiều, tính khoảng cách qua computeCosine(vecA, vecB) và so sánh với ngưỡng lấy từ DynamicConfigManager. Nếu độ tương đồng đạt ngưỡng thì gộp câu hỏi vào cụm và gọi updateCentroid(); ngược lại thì khởi tạo một QuestionCluster mới trong $\le 500\text{ms}$ (Kịch bản QA 1.2).   Interface IEmbeddingStrategy, MultilingualE5Adapter, LaBSEAdapter: Áp dụng mẫu thiết kế Strategy Pattern giúp tách rời thuật toán phân cụm khỏi mô hình ngôn ngữ cụ thể. Nhóm nghiên cứu có thể chuyển đổi từ LaBSE sang intfloat/multilingual-e5-base trong $\le 1$ giờ làm việc để đo chỉ số ARI và Silhouette Score với 0 dòng code bị sửa ở tầng Frontend và Database (Kịch bản QA 4.1).   Class DynamicConfigManager: Cung cấp phương thức setThreshold(newVal) cho phép cập nhật nóng ngưỡng tương đồng (ví dụ từ $0.65$ lên $0.75$) ngay giữa các ca học thực nghiệm trong $\le 5$ phút (Kịch bản QA 4.2).   Class QuestionCluster & QuestionEntity: Lưu trữ câu hỏi đại diện (representativeText), vector tâm cụm (centroidVector) và danh sách định danh ẩn danh của sinh viên trong cụm (subscriberAnonIds) để phục vụ phản hồi 1-nhiều.   Hình 4.3: Code Diagram — Luồng Bảo mật Ẩn danh, Chống Spam & Phản hồi 1-nhiều (FR-01, FR-04 & QA 3)(Bố cục cân xứng: Khung Security & Broadcast ở giữa $\rightarrow$ Request đầu vào bên trái, Dịch vụ dịch thuật bên phải).   Đoạn mã%%{init: {'flowchart': {'nodeSpacing': 28, 'rankSpacing': 38, 'padding': 10}, 'themeVariables': {'fontSize': '13px'}}}%%
flowchart TB
    classDef ctrl fill:#eef6ff,stroke:#1168bd,stroke-width:2px,color:#0b4884,rx:4px,ry:4px;
    classDef ext fill:#f5f5f5,stroke:#555555,stroke-width:2px,color:#222222,rx:4px,ry:4px;
    classDef store fill:#eef6ff,stroke:#1168bd,stroke-width:2px,color:#0b4884;

    %% Hai khối bên ngoài ở 2 cánh Trái - Phải
    ClientReq["<b>Student & Lecturer Request</b><br/><i>[Incoming HTTP / WebSocket]</i><br/><br/>Gửi câu hỏi kèm PIN/Token hoặc<br/>gửi câu trả lời đại diện cho cụm"]
    TranslationSvc["<b>class BilingualTranslator</b><br/><i>[External AI Service]</i><br/><br/>+ translateAnswer(text, targetLang): str"]

    %% Khung Module chính ở giữa
    subgraph Security_Broadcast_Module ["<b>Security & 1-to-Many Broadcast Module</b> <i>[Code Boundary: FR-01, FR-04 & QA 1.3, 3.1, 3.2, 3.3]</i>"]
        direction TB
        
        %% Tầng 1: Xác thực PIN & Chống Spam
        AuthMid["<b>class SessionAuthMiddleware</b><br/><i>[Security Guard Class]</i><br/><br/>- secretSalt: str<br/>+ verifyPinOrQR(sessionId, token): bool<br/>+ generateAnonHash(sessionId, key): str"]
        RateLimit["<b>class AntiSpamRateLimiter</b><br/><i>[Token Bucket Class]</i><br/><br/>- maxQuestionsPerMin: int = 3<br/>+ allowRequest(anonHashId): bool"]

        %% Tầng 2: Controller điều phối Hỏi đáp & WebSocket Manager
        QnACtrl["<b>>_ class QnAController</b><br/><i>[FastAPI Router Controller]</i><br/><br/>- clusterEngine: OnlineClusteringEngine<br/>- wsManager: WebSocketBroadcastManager<br/>+ submitQuestion(sessionId, anonId, text): ClusterDTO<br/>+ answerCluster(clusterId, answerText): BroadcastDTO"]
        WSMgr["<b>>_ class WebSocketBroadcastManager</b><br/><i>[Real-time Engine Class]</i><br/><br/>+ subscribeCluster(clusterId, anonId, ws): void<br/>+ broadcastToCluster(clusterId, payload): void"]

        %% Tầng 3: Bảng đăng ký nhóm & DTO ở đáy
        SubMap[("<b>Cluster Subscription Registry</b><br/><i>[In-Memory Map: Dict[str, Set[WS]]]</i><br/><br/>Ánh xạ clusterId tới danh sách kết nối<br/>WebSocket của sinh viên trong cụm")]
        AnswerDTO[("<b>class BilingualAnswerDTO</b><br/><i>[Response Payload]</i><br/><br/>+ clusterId: str<br/>+ answerEn: str<br/>+ answerVi: str")]
    end

    %% Luồng gọi phương thức
    ClientReq -. "1. Kiểm tra verifyPinOrQR()<br/><i>[Chặn 100% truy cập trái phép]</i>" .-> AuthMid
    AuthMid -. "2. Gắn generateAnonHash()<br/><i>[0% lộ danh tính sinh viên]</i>" .-> RateLimit
    RateLimit -. "3. Kiểm tra allowRequest()<br/><i>[Chặn Spam <= 20ms]</i>" .-> QnACtrl

    QnACtrl -. "4. Dịch song ngữ câu trả lời<br/><i>[translateAnswer()]</i>" .-> TranslationSvc
    QnACtrl -. "5. Gọi broadcastToCluster()<br/><i>[Phát tán 1-nhiều <= 400ms]</i>" .-> WSMgr

    WSMgr -. "Tra cứu danh sách sinh viên thuộc cụm<br/><i>[O(1) Lookup]</i>" .-> SubMap
    WSMgr -. "Đẩy gói tin đáp án song ngữ<br/><i>[WebSocket Frame]</i>" .-> AnswerDTO

    class AuthMid,RateLimit,QnACtrl,WSMgr ctrl;
    class ClientReq,TranslationSvc ext;
    class SubMap,AnswerDTO store;
    style Security_Broadcast_Module fill:none,stroke:#666666,stroke-width:2px,stroke-dasharray: 6 6,color:#333333
Mô tả chi tiết Hình 4.3 (Code Diagram - Luồng Bảo mật Ẩn danh, Chống Spam & Phản hồi 1-nhiều)Class SessionAuthMiddleware: Phương thức verifyPinOrQR(sessionId, token) kiểm tra mã PIN 6 số động hoặc chữ ký số ngắn hạn trong mã QR để từ chối 100% kết nối không hợp lệ (Kịch bản QA 3.3). Phương thức generateAnonHash() tạo mã băm một chiều Anonymous_Hash_ID, cam kết không lưu họ tên, MSSV, email hay IP cá nhân (Kịch bản QA 3.1).   Class AntiSpamRateLimiter: Phương thức allowRequest(anonHashId) giới hạn tối đa 3 câu hỏi/phút trên mỗi phiên ẩn danh, chặn đứng các cuộc tấn công spam trong $\le 20\text{ms}$ (Kịch bản QA 3.2).   Class QnAController & WebSocketBroadcastManager: Khi sinh viên gửi câu hỏi qua submitQuestion(), kết nối WebSocket được đăng ký vào Cluster Subscription Registry qua hàm subscribeCluster(). Khi giảng viên trả lời câu hỏi đại diện qua answerCluster(), hệ thống dịch song ngữ câu trả lời và gọi broadcastToCluster() để đẩy thông báo đồng thời đến 100% sinh viên trong cụm đó trong vòng $\le 400\text{ms}$ (Kịch bản QA 1.3).   Hình 4.4: Code Diagram — Luồng Tổng hợp Báo cáo & Heatmap Cuối buổi (FR-05 & QA 4.3)(Bố cục cân xứng: Khung Summary Module ở giữa $\rightarrow$ 2 Adapter LLM Qwen2.5-7B và LightweightLLM ở 2 cánh Trái – Phải).   Đoạn mã%%{init: {'flowchart': {'nodeSpacing': 28, 'rankSpacing': 38, 'padding': 10}, 'themeVariables': {'fontSize': '13px'}}}%%
flowchart TB
    classDef ctrl fill:#eef6ff,stroke:#1168bd,stroke-width:2px,color:#0b4884,rx:4px,ry:4px;
    classDef iface fill:#ffffff,stroke:#1168bd,stroke-width:2px,stroke-dasharray: 4 4,color:#0b4884,rx:4px,ry:4px;
    classDef impl fill:#f5f5f5,stroke:#555555,stroke-width:2px,color:#222222,rx:4px,ry:4px;
    classDef dto fill:#eef6ff,stroke:#1168bd,stroke-width:2px,color:#0b4884;

    %% Hai Class Adapter LLM nằm cân xứng ở 2 cánh Trái - Phải
    QwenAdapter["<b>class OllamaQwenAdapter</b><br/><i>[Implements: ILLMProvider]</i><br/><br/>- endpoint: str<br/>- modelName: str = 'qwen2.5:7b'<br/>+ summarize(transcript, clusters): str"]
    LightAdapter["<b>class LightweightLLMAdapter</b><br/><i>[Implements: ILLMProvider]</i><br/><br/>- localModelPath: str<br/>- quantizedType: str = 'q4_k_m'<br/>+ summarize(transcript, clusters): str"]

    %% Khung Module chính ở giữa
    subgraph Summary_Code_Module ["<b>Session Summary & Heatmap Module</b> <i>[Code Boundary: FR-05 & QA 4.3]</i>"]
        direction TB
        
        %% Tầng 1: Nguồn dữ liệu & Tính toán Heatmap
        SessionRepo["<b>class SessionRepository</b><br/><i>[Data Access Class]</i><br/><br/>+ getSessionTranscripts(sessionId): List<br/>+ getSessionClusters(sessionId): List<br/>+ saveReport(reportDTO): void"]
        HeatmapCalc["<b>class HeatmapCalculator</b><br/><i>[Analytics Helper Class]</i><br/><br/>+ alignQuestionsToTimeline(transcripts, clusters): List[HeatmapPoint]"]

        %% Tầng 2: Service tổng hợp báo cáo ở tâm
        SummarySvc["<b>>_ class SessionSummaryService</b><br/><i>[Core Summary Service]</i><br/><br/>- llmProvider: ILLMProvider<br/>- sessionRepo: SessionRepository<br/>+ generateEndSessionReport(sessionId): SessionReportDTO<br/>+ switchLLMProvider(newProvider): void"]

        %% Tầng 3: Unified Interface & DTO ở đáy
        ILLM["<b>&lt;&lt;interface&gt;&gt; ILLMProvider</b><br/><i>[Unified LLM Interface]</i><br/><br/>+ summarize(transcript: str, clusters: List): str"]
        ReportDTO[("<b>class SessionReportDTO</b><br/><i>[Report & Heatmap Payload]</i><br/><br/>+ sessionId: str<br/>+ executiveSummary: str<br/>+ comprehensionHeatmap: List[HeatmapPoint]<br/>+ resolvedClusters: List[ClusterDTO]")]
    end

    %% Luồng gọi phương thức
    SessionRepo -. "1. Nạp Transcript & Cụm câu hỏi<br/><i>[Async DB Read]</i>" .-> SummarySvc
    HeatmapCalc -. "2. Tính mật độ điểm nghẽn theo giờ<br/><i>[alignQuestionsToTimeline()]</i>" .-> SummarySvc

    SummarySvc -. "3. Gọi tóm tắt qua giao diện chung<br/><i>[summarize()]</i>" .-> ILLM
    SummarySvc -. "4. Kết xuất báo cáo & Heatmap<br/><i>[Chuẩn hóa JSON / PDF]</i>" .-> ReportDTO

    QwenAdapter -. "Implements Interface<br/><i>[Mô hình mặc định Qwen2.5-7B]</i>" .-> ILLM
    LightAdapter -. "Implements Interface<br/><i>[Đổi mô hình nhẹ <= 30p khi thiếu VRAM]</i>" .-> ILLM

    class SessionRepo,HeatmapCalc,SummarySvc ctrl;
    class ILLM iface;
    class QwenAdapter,LightAdapter impl;
    class ReportDTO dto;
    style Summary_Code_Module fill:none,stroke:#666666,stroke-width:2px,stroke-dasharray: 6 6,color:#333333
Mô tả chi tiết Hình 4.4 (Code Diagram - Luồng Tổng hợp Báo cáo & Heatmap Cuối buổi)Class SessionSummaryService & HeatmapCalculator: Khi kết thúc buổi học, phương thức generateEndSessionReport(sessionId) truy xuất toàn bộ bản ghi lời giảng (transcript) và danh sách các cụm câu hỏi từ SessionRepository. Đồng thời, phương thức alignQuestionsToTimeline() đối chiếu mật độ câu hỏi của sinh viên theo dòng thời gian bài giảng để tạo dữ liệu biểu đồ nhiệt Comprehension Heatmap (FR-05).   Interface ILLMProvider, OllamaQwenAdapter, LightweightLLMAdapter: Chuẩn hóa tầng giao tiếp mô hình ngôn ngữ lớn qua một giao diện thống nhất (Unified LLM Interface). Khi triển khai tại phòng học mới có máy chủ cục bộ thiếu VRAM, nhóm phát triển có thể chuyển đổi từ OllamaQwenAdapter (Qwen2.5-7B) sang LightweightLLMAdapter trong $\le 30$ phút cấu hình mà vẫn giữ nguyên định dạng SessionReportDTO phục vụ hiển thị biểu đồ nhiệt và xuất file PDF lưu trữ (Kịch bản QA 4.3).   