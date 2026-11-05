# -*- coding: utf-8 -*-
"""
Script tạo file báo cáo hoàn chỉnh: NHOM6.docx (và NHOM6.pdf)
Đáp ứng đầy đủ 100% yêu cầu đề bài:
1. Dựa trên các Architectural Drivers đã có, chi tiết hóa:
   - Phân tích các QAs đã chọn và lựa chọn các kịch bản cụ thể (12 kịch bản 6-thành phần thuộc 4 nhóm QA).
   - Dựa trên các kịch bản, lựa chọn các Software Structures để thể hiện Module View của hệ thống
     (Module Decomposition View, Layered & Uses View, Generalization/Strategy Interface View theo 4 cấp độ C4).
   - Mô tả chi tiết các chức năng chính, vai trò, trách nhiệm và mối quan hệ với các thành phần khác
     cho toàn bộ các Module/Component/Class trong 9 sơ đồ kiến trúc.
   - Ghi rõ tên thành viên, mức độ đóng góp (100%) và thông tin 1 người đại diện nộp bài (NHOM6).
"""

import os
import shutil
from diagram_definitions import DIAGRAMS
from generate_word_reports import (
    make_p,
    make_run,
    make_page_break,
    make_h1,
    make_h2,
    make_h3,
    make_body_p,
    make_bullet_p,
    make_image_drawing_p,
    make_caption_p,
    make_table,
    write_docx_with_images,
    OUT_DIR,
)

ROOT_DIR = r"d:\TailieuNPKH\classbridge"


def build_nhom6_cover_page() -> list[str]:
    elems = []
    elems.append(
        make_p(
            make_run(
                "BỘ GIÁO DỤC VÀ ĐÀO TẠO — ĐẠI HỌC DUY TÂN\nTRƯỜNG CÔNG NGHỆ THÔNG TIN VÀ MÁY TÍNH\nKHOA KỸ THUẬT PHẦN MỀM",
                size_pt=11.5,
                bold=True,
                color="475569",
            ),
            align="center",
            space_before_pt=6,
            space_after_pt=32,
            line_spacing=1.3,
        )
    )
    elems.append(
        make_p(
            make_run("★ ★ ★", size_pt=12.0, bold=True, color="94A3B8"),
            align="center",
            space_after_pt=26,
        )
    )
    elems.append(
        make_p(
            make_run(
                "BÁO CÁO PHÂN TÍCH THUỘC TÍNH CHẤT LƯỢNG (QAs),\nKỊCH BẢN KIẾN TRÚC & THIẾT KẾ MODULE VIEW (C4 MODEL)",
                size_pt=19.5,
                bold=True,
                color="1E3A8A",
            ),
            align="center",
            space_after_pt=12,
            line_spacing=1.25,
        )
    )
    elems.append(
        make_p(
            make_run(
                "Từ Architectural Drivers đến Lựa chọn Software Structures, Module View & Đặc tả Thành phần",
                size_pt=12.5,
                bold=True,
                italic=True,
                color="2563EB",
            ),
            align="center",
            space_after_pt=20,
        )
    )
    elems.append(
        make_p(
            make_run(
                "Đề tài: ClassBridge — AI-Powered Assistant for EMI Classrooms\n(Hệ thống Trợ lý AI Hỗ trợ Tương tác Lớp học Giảng dạy bằng Tiếng Anh)",
                size_pt=13.0,
                bold=True,
                color="0F172A",
            ),
            align="center",
            space_after_pt=32,
            line_spacing=1.3,
        )
    )

    info_rows = [
        ["Tên nhóm nộp bài:", "NHÓM 6 (Mã nhóm Capstone: C1SE.38)"],
        ["Người đại diện nộp bài:", "Nguyễn Sỹ Tân — MSSV: 29212449741 (Nhóm trưởng / AI & Backend Lead)"],
        ["Thành viên nhóm:", "Nguyễn Sỹ Tân, Võ Trương Khải Hoàn, Phan Quang Tuấn, Trần Thị Thu Hồng, Nguyễn Thành Nhân"],
        ["Học phần / Chương trình:", "Kiến trúc Phần mềm & Đồ án Kỹ thuật Phần mềm (CMU-SE) — Đại học Duy Tân (DTU)"],
        ["Tên file quy định:", "NHOM6.docx (Chỉ 01 người đại diện nhóm nộp bài)"],
        ["Thời gian thực hiện:", "Học kỳ 1 — Năm học 2026"],
    ]
    elems.append(make_table([], info_rows, [5.3, 11.1], border_color="CBD5E1"))

    elems.append(
        make_p(
            make_run("ĐÀ NẴNG, NĂM 2026", size_pt=11.5, bold=True, color="64748B"),
            align="center",
            space_before_pt=40,
            space_after_pt=6,
        )
    )
    elems.append(make_page_break())
    return elems


def build_nhom6_toc() -> list[str]:
    elems = []
    elems.append(
        make_p(
            make_run("MỤC LỤC BÁO CÁO (NHÓM 6)", size_pt=16.0, bold=True, color="1E3A8A"),
            align="left",
            space_after_pt=10,
        )
    )
    toc_items = [
        ("PHẦN 1. THÔNG TIN NHÓM 6, NGƯỜI ĐẠI DIỆN NỘP BÀI & MỨC ĐỘ ĐÓNG GÓP", 0, True),
        ("1.1. Thông tin chung và Người đại diện nộp bài", 1, False),
        ("1.2. Bảng phân công nhiệm vụ và mức độ đóng góp của từng thành viên", 1, False),
        ("PHẦN 2. TỔNG HỢP ARCHITECTURAL DRIVERS NỀN TẢNG CỦA CLASSBRIDGE", 0, True),
        ("2.1. Bối cảnh bài toán (The Broken Feedback Loop) và Mục đích thiết kế (Design Purpose)", 1, False),
        ("2.2. Yêu cầu Chức năng Cốt lõi (Primary Functional Requirements: FR-01 đến FR-05)", 1, False),
        ("2.3. Ràng buộc Kiến trúc (Constraints) và Mối quan tâm Kiến trúc (Architectural Concerns)", 1, False),
        ("PHẦN 3. PHÂN TÍCH CÁC QAs ĐÃ CHỌN & LỰA CHỌN CÁC KỊCH BẢN CỤ THỂ", 0, True),
        ("3.1. Tổng quan lựa chọn 4 Thuộc tính Chất lượng (QAs) trọng tâm", 1, False),
        ("3.2. Phân tích QA 1: Performance (Hiệu năng & Độ trễ thời gian thực) — 3 Kịch bản cụ thể", 1, False),
        ("3.3. Phân tích QA 2: Availability & Fault Tolerance (Tính sẵn sàng & Chịu lỗi) — 3 Kịch bản cụ thể", 1, False),
        ("3.4. Phân tích QA 3: Security & Privacy (Bảo mật & Quyền riêng tư ẩn danh) — 3 Kịch bản cụ thể", 1, False),
        ("3.5. Phân tích QA 4: Modifiability (Tính dễ sửa đổi & Thử nghiệm mô hình) — 3 Kịch bản cụ thể", 1, False),
        ("PHẦN 4. LỰA CHỌN SOFTWARE STRUCTURES ĐỂ THỂ HIỆN MODULE VIEW & ĐẶC TẢ CHI TIẾT CÁC THÀNH PHẦN", 0, True),
        ("4.1. Cơ sở lựa chọn Software Structures cho Module View từ các Kịch bản QA", 1, False),
        ("4.2. Cấp độ 1 — System Context View (Hình 1): Ngữ cảnh Hệ thống & Quan hệ Tác nhân", 1, False),
        ("4.3. Cấp độ 2 — Top-Level Module Decomposition / Container View (Hình 2)", 1, False),
        ("4.4. Cấp độ 3 — Layered Component & Uses View cho 3 Phân hệ Lõi (Hình 3.1, 3.2, 3.3)", 1, False),
        ("4.4.1. Hình 3.1: Module View bên trong Backend API & WebSocket Server", 2, False),
        ("4.4.2. Hình 3.2: Module View bên trong Speech Processing Worker (FR-02)", 2, False),
        ("4.4.3. Hình 3.3: Module View bên trong NLP & LLM Inference Service (FR-03 & FR-05)", 2, False),
        ("4.5. Cấp độ 4 — Code / Generalization & Strategy Interface View (Hình 4.1, 4.2, 4.3, 4.4)", 1, False),
        ("4.5.1. Hình 4.1: Code View — Luồng Phụ đề Song ngữ & VAD Gate Chống ảo giác", 2, False),
        ("4.5.2. Hình 4.2: Code View — Luồng Gom nhóm Câu hỏi Ngữ nghĩa Đa ngôn ngữ", 2, False),
        ("4.5.3. Hình 4.3: Code View — Luồng Bảo mật Ẩn danh, Chống Spam & Phản hồi 1-nhiều", 2, False),
        ("4.5.4. Hình 4.4: Code View — Luồng Tổng hợp Báo cáo & Heatmap Cuối buổi", 2, False),
        ("PHẦN 5. MA TRẬN TRUY VẾT TOÀN DIỆN (QA SCENARIOS → SOFTWARE STRUCTURES → MODULES) & KẾT LUẬN", 0, True),
    ]
    for title, lvl, is_b in toc_items:
        elems.append(
            make_p(
                make_run(title, size_pt=11.0, bold=is_b, color="1E3A8A" if is_b else "334155"),
                align="left",
                space_before_pt=2 if is_b else 0,
                space_after_pt=2.5,
                line_spacing=1.15,
                left_indent_cm=0.55 * lvl,
            )
        )
    elems.append(make_page_break())
    return elems


def build_part1_team_and_contribution() -> list[str]:
    elems = []
    elems.append(make_h1("PHẦN 1. THÔNG TIN NHÓM 6, NGƯỜI ĐẠI DIỆN NỘP BÀI & MỨC ĐỘ ĐÓNG GÓP"))

    elems.append(make_h2("1.1. Thông tin chung và Người đại diện nộp bài"))
    elems.append(
        make_bullet_p(
            "NHÓM 6 (Mã nhóm đồ án Capstone: C1SE.38 — Khoa Kỹ thuật Phần mềm, Đại học Duy Tân).",
            bold_prefix="Tên nhóm thực hiện: ",
        )
    )
    elems.append(
        make_bullet_p(
            "ClassBridge — Hệ thống Trợ lý AI hỗ trợ tương tác và phá vỡ rào cản ngôn ngữ trong lớp học giảng dạy bằng tiếng Anh (English-Medium Instruction - EMI).",
            bold_prefix="Tên đề tài: ",
        )
    )
    elems.append(
        make_bullet_p(
            "Nguyễn Sỹ Tân (MSSV: 29212449741 — Vai trò: Nhóm trưởng / AI & Backend Lead). Thực hiện đúng quy định chỉ 01 người đại diện duy nhất nộp file NHOM6.docx.",
            bold_prefix="Người đại diện nộp bài: ",
        )
    )

    elems.append(make_h2("1.2. Bảng phân công nhiệm vụ và mức độ đóng góp của từng thành viên"))
    elems.append(
        make_body_p(
            "Tất cả 05 thành viên của Nhóm 6 cùng tham gia phân tích Architectural Drivers, xây dựng kịch bản thuộc tính chất lượng (Quality Attribute Scenarios), lựa chọn cấu trúc phần mềm (Software Structures - Module View) và đặc tả chi tiết vai trò, trách nhiệm, mối quan hệ của từng thành phần:"
        )
    )

    mem_headers = ["STT", "Họ và Tên", "Vai trò", "Nhiệm vụ chi tiết trong báo cáo NHOM6", "Đóng góp"]
    mem_rows = [
        [
            "1",
            "Nguyễn Sỹ Tân\n(Đại diện nộp)",
            "Nhóm trưởng /\nAI & Backend Lead",
            "Phân tích QA 1 (Performance) & QA 4 (Modifiability); lựa chọn cấu trúc Strategy/Adapter; thiết kế & đặc tả Module View cho Speech Processing (Hình 3.2, 4.1) và Semantic Clustering (Hình 4.2); tổng hợp và nộp bài.",
            "20%",
        ],
        [
            "2",
            "Võ Trương Khải Hoàn",
            "System Architect",
            "Tổng hợp Architectural Drivers; phân tích QA 2 (Availability & Fault Tolerance); xác lập cấu trúc phân rã Module Decomposition (Hình 1, Hình 2) và chiến thuật cô lập lỗi Worker Isolation.",
            "20%",
        ],
        [
            "3",
            "Phan Quang Tuấn",
            "Backend Developer",
            "Phân tích QA 3 (Security & Privacy); thiết kế & đặc tả chức năng, vai trò, trách nhiệm và quan hệ cho Backend API & WebSocket Server (Hình 3.1) và Security & Broadcast Module (Hình 4.3).",
            "20%",
        ],
        [
            "4",
            "Trần Thị Thu Hồng",
            "Frontend / UI-UX",
            "Đặc tả chức năng, vai trò, trách nhiệm và mối quan hệ của Student Mobile Web, Lecturer Dashboard, NLP & LLM Service (Hình 3.3) và Session Summary & Heatmap Module (Hình 4.4).",
            "20%",
        ],
        [
            "5",
            "Nguyễn Thành Nhân",
            "QA / Data Engineer",
            "Chuẩn hóa 12 kịch bản chất lượng 6 thành phần; lập bảng Ma trận Truy vết (Drivers → QAs → Software Structures → Modules); kiểm định thước đo định lượng (Response Measures) và nghiệm thu tài liệu.",
            "20%",
        ],
        [
            "Tổng",
            "05 Thành viên Nhóm 6 (C1SE.38)",
            "Hoàn thành 100%",
            "Thống nhất toàn bộ nội dung phân tích QAs, 12 kịch bản, 9 sơ đồ Module View (C4 Model) và bảng đặc tả trách nhiệm thành phần.",
            "100%",
        ],
    ]
    elems.append(make_table(mem_headers, mem_rows, [1.2, 3.4, 2.8, 7.2, 1.8]))
    return elems


def build_part2_architectural_drivers_summary() -> list[str]:
    elems = []
    elems.append(make_page_break())
    elems.append(make_h1("PHẦN 2. TỔNG HỢP ARCHITECTURAL DRIVERS NỀN TẢNG CỦA CLASSBRIDGE"))

    elems.append(make_h2("2.1. Bối cảnh bài toán (The Broken Feedback Loop) và Mục đích thiết kế (Design Purpose)"))
    elems.append(
        make_body_p(
            "Trong các lớp học chuyên ngành Công nghệ Thông tin giảng dạy bằng tiếng Anh (English-Medium Instruction - EMI), vòng phản hồi giữa giảng viên quốc tế và sinh viên Việt Nam thường xuyên bị đứt gãy (The Broken Feedback Loop) do 3 nguyên nhân cốt lõi: (1) Giảng viên thiếu thông tin phản hồi thời gian thực về điểm nghẽn hiểu bài của sinh viên; (2) Sinh viên gặp rào cản ngôn ngữ với thuật ngữ chuyên ngành, ngữ điệu (accent) và e ngại tâm lý sợ phát âm sai khi hỏi trước đám đông; (3) Câu hỏi của sinh viên bị phân mảnh, trùng lặp ý nghĩa dưới nhiều cách diễn đạt (tiếng Việt, tiếng Anh, hoặc pha trộn code-switching)."
        )
    )
    elems.append(
        make_body_p(
            "Xây dựng một hệ thống trợ lý AI thời gian thực tự triển khai mô hình cục bộ (Self-hosted / In-house AI Inference) có khả năng vận hành trực tiếp tại lớp học (Pilot Deployment) nhằm khép kín chu trình 4 bước: (1) Phụ đề song ngữ trực tiếp (≤ 1.5s); (2) Hỏi đáp ẩn danh & Gom nhóm câu hỏi tương đồng ngữ nghĩa (≤ 500ms); (3) Bảng điều khiển giảng viên & Phản hồi đại diện 1-nhiều (≤ 400ms); và (4) Tổng hợp báo cáo & Biểu đồ nhiệt mức độ hiểu bài (Comprehension Heatmap) cuối buổi.",
            bold_prefix="Mục đích thiết kế (Design Purpose): ",
        )
    )

    elems.append(make_h2("2.2. Yêu cầu Chức năng Cốt lõi (Primary Functional Requirements: FR-01 đến FR-05)"))
    fr_headers = ["Mã FR", "Tên Yêu cầu Chức năng Cốt lõi", "Đặc tả Nghiệp vụ & Yêu cầu Kiến trúc Trọng tâm"]
    fr_rows = [
        [
            "FR-01",
            "Khởi tạo & Tham gia Phiên học Ẩn danh",
            "Giảng viên khởi tạo phiên học mới trên Dashboard, hệ thống tự động sinh mã PIN 6 số động và mã QR. Sinh viên quét QR hoặc nhập PIN trên trình duyệt di động (Zero-Install) để vào thẳng phòng học với định danh tạm thời một chiều (Anonymous_Hash_ID) mà không cần tạo tài khoản hay đăng nhập.",
        ],
        [
            "FR-02",
            "Chuyển đổi & Dịch Phụ đề Thời gian thực",
            "Thu luồng âm thanh trực tiếp từ micro giảng viên, lọc tạp âm và khoảng lặng bằng Silero VAD. Chuyển đổi đoạn âm thanh tiếng Anh sang văn bản bằng Faster-Whisper và dịch thuật ngữ chuyên ngành CNTT sang tiếng Việt (NLLB-200 / EnViT5) để hiển thị phụ đề song ngữ tức thì trên màn chiếu và điện thoại sinh viên.",
        ],
        [
            "FR-03",
            "Gom nhóm Câu hỏi Ngữ nghĩa Đa ngôn ngữ",
            "Cho phép sinh viên gửi câu hỏi tự do bằng tiếng Việt, tiếng Anh hoặc pha trộn thuật ngữ (code-switching). Chuyển đổi văn bản câu hỏi thành vector ngữ nghĩa 768 chiều, tính khoảng cách Cosine với tâm các cụm hiện tại để tự động gộp vào cụm tương đồng hoặc khởi tạo cụm mới.",
        ],
        [
            "FR-04",
            "Quản lý Cụm câu hỏi & Phản hồi Đại diện 1-nhiều",
            "Sắp xếp và làm nổi bật các cụm câu hỏi nóng nhất trên Dashboard giảng viên theo số lượng sinh viên cùng thắc mắc. Khi giảng viên trả lời một lần cho cụm đại diện, hệ thống tự động dịch song ngữ và phát tán (broadcast) qua WebSocket đến toàn bộ sinh viên thuộc cụm đó.",
        ],
        [
            "FR-05",
            "Tổng hợp Báo cáo & Lưu trữ Bài giảng Cuối buổi",
            "Khi kết thúc buổi học, mô hình LLM cục bộ (Qwen2.5-7B / Ollama) tổng hợp nội dung chính từ bản ghi lời giảng (transcript) và danh sách các cụm câu hỏi, lập biểu đồ nhiệt mức độ hiểu bài theo dòng thời gian (Comprehension Heatmap) và lưu trữ toàn bộ tư liệu vào PostgreSQL.",
        ],
    ]
    elems.append(make_table(fr_headers, fr_rows, [1.8, 4.6, 10.0]))

    elems.append(make_h2("2.3. Ràng buộc Kiến trúc (Constraints) và Mối quan tâm Kiến trúc (Architectural Concerns)"))
    elems.append(
        make_bullet_p(
            "Bắt buộc triển khai các mô hình AI mã nguồn mở chạy cục bộ (Silero VAD, Faster-Whisper CTranslate2, multilingual-e5-base / LaBSE, Meta NLLB-200 / EnViT5, Qwen2.5-7B) thay vì gọi API thương mại bên ngoài để đảm bảo tính đóng góp học thuật (Novelty), làm chủ độ trễ và bảo mật dữ liệu lớp học; giao diện sinh viên bắt buộc là Mobile Web Zero-Install (Next.js/React); Backend sử dụng Python FastAPI, WebSocket và PostgreSQL đóng gói bằng Docker.",
            bold_prefix="Ràng buộc Kỹ thuật (Technical Constraints): ",
        )
    )
    elems.append(
        make_bullet_p(
            "Ngân sách thuê máy chủ đám mây bằng 0 VND (vận hành tối ưu trên máy chủ GPU cục bộ của nhóm/phòng Lab); bắt buộc hoàn thiện các luồng cốt lõi để chạy thử nghiệm thực tế (Pilot Deployment) tại 2–3 lớp học EMI vào Tuần 4–5.",
            bold_prefix="Ràng buộc Nghiệp vụ & Lịch trình (Business & Schedule Constraints): ",
        )
    )
    elems.append(
        make_bullet_p(
            "(1) Cô lập tiến trình xử lý nặng (Worker Isolation) giữa Speech Pipeline và NLP Clustering để không làm nghẽn sự kiện WebSocket; (2) Chống ảo giác mô hình Whisper (Hallucination Mitigation) bằng cổng kiểm soát giọng nói VAD Gate; (3) Đảm bảo độ ổn định kết nối và chống mất gói tin cho 50–100 thiết bị di động dùng chung mạng Wi-Fi giảng đường.",
            bold_prefix="Mối quan tâm Kiến trúc (Architectural Concerns): ",
        )
    )
    return elems


def make_scenario_table_doc(scenario_rows: list[tuple[str, str]]) -> str:
    rows = [[k, v] for k, v in scenario_rows]
    return make_table(["Thành phần kịch bản (SEI 6-Part)", "Nội dung đặc tả chi tiết & Thước đo định lượng"], rows, [5.0, 11.4])


def build_part3_qas_and_scenarios() -> list[str]:
    elems = []
    elems.append(make_page_break())
    elems.append(make_h1("PHẦN 3. PHÂN TÍCH CÁC QAs ĐÃ CHỌN & LỰA CHỌN CÁC KỊCH BẢN CỤ THỂ"))

    elems.append(make_h2("3.1. Tổng quan lựa chọn 4 Thuộc tính Chất lượng (QAs) trọng tâm"))
    elems.append(
        make_body_p(
            "Dựa trên mục đích thiết kế và các Architectural Drivers của hệ thống tương tác lớp học thời gian thực tích hợp AI cục bộ, Nhóm 6 xác định 04 Thuộc tính Chất lượng (Quality Attributes - QAs) đóng vai trò quyết định đến sự thành bại của kiến trúc hệ thống ClassBridge:"
        )
    )
    qa_overview_headers = ["Thứ tự ưu tiên", "Thuộc tính Chất lượng (QA)", "Lý do cốt lõi định hình kiến trúc", "Chiến thuật Kiến trúc (Architectural Tactics) áp dụng"]
    qa_overview_rows = [
        [
            "QA 1\n(Ưu tiên #1)",
            "Performance\n(Hiệu năng & Độ trễ thời gian thực)",
            "Hệ thống phải đồng bộ trực tiếp với lời giảng tại lớp và phản hồi tức thì khi hàng chục sinh viên gửi câu hỏi cùng lúc.",
            "Asynchronous Pipeline, CTranslate2 FP16 Quantization, In-Memory Vector Centroid Cache, O(1) WebSocket Room Multicast.",
        ],
        [
            "QA 2\n(Ưu tiên #2)",
            "Availability & Fault Tolerance\n(Tính sẵn sàng & Khả năng chịu lỗi)",
            "Ca học thực nghiệm (45–90 phút) không thể tạm dừng nếu tiến trình AI quá tải VRAM hoặc Wi-Fi giảng đường chập chờn.",
            "Worker Process Isolation, OOM Memory Watchdog & Auto-Restart, Client LocalStorage Queue & Auto-Reconnect, Silero VAD Gate.",
        ],
        [
            "QA 3\n(Ưu tiên #3)",
            "Security & Privacy\n(Bảo mật & Quyền riêng tư ẩn danh)",
            "Sinh viên chỉ dám đặt câu hỏi khi danh tính được bảo vệ tuyệt đối; đồng thời phòng học không tài khoản phải chống được spam và người lạ.",
            "One-way Salted Hash (Anonymous_Hash_ID), Zero PII Storage, Token-Bucket Rate Limiter (≤ 20ms), Dynamic 6-Digit PIN & Short-lived QR.",
        ],
        [
            "QA 4\n(Ưu tiên #4)",
            "Modifiability\n(Tính dễ sửa đổi & Thử nghiệm mô hình)",
            "Phục vụ nghiên cứu khoa học: cần đối sánh nhiều mô hình (e5-base vs. LaBSE, Qwen2.5 vs. Lightweight LLM) và tinh chỉnh ngưỡng Cosine.",
            "Polymorphism / Strategy & Adapter Pattern, Unified Interface (ISTTEngine, IEmbeddingStrategy, ILLMProvider), Dynamic Runtime Config.",
        ],
    ]
    elems.append(make_table(qa_overview_headers, qa_overview_rows, [2.2, 3.6, 5.2, 5.4]))

    # 3.2 QA 1: Performance
    elems.append(make_h2("3.2. Phân tích QA 1: Performance (Hiệu năng & Độ trễ thời gian thực)"))
    elems.append(
        make_body_p(
            "ClassBridge vận hành đồng bộ với lời giảng trực tiếp tại lớp. Nếu phụ đề hiển thị trễ quá vài giây, sinh viên sẽ không thể đối chiếu nội dung bài giảng đang chiếu trên slide. Đồng thời, sau một khái niệm khó, hàng chục sinh viên có thể gửi câu hỏi dồn dập cùng lúc; nếu thuật toán gom cụm ngữ nghĩa hoặc cơ chế phát tán câu trả lời xử lý chậm, giảng viên sẽ chuyển sang phần bài học khác trước khi nhận ra điểm nghẽn kiến thức của lớp, làm mất đi giá trị cốt lõi của vòng phản hồi thời gian thực.",
            bold_prefix="Phân tích chuyên sâu lý do lựa chọn QA 1: ",
        )
    )

    elems.append(make_h3("Kịch bản 1.1: Xử lý và hiển thị phụ đề song ngữ trực tiếp (FR-02)"))
    elems.append(
        make_scenario_table_doc([
            ("Nguồn kích thích (Source)", "Giảng viên nước ngoài đang giảng bài trực tiếp tại lớp học EMI."),
            ("Tác nhân kích thích (Stimulus)", "Giảng viên nói một câu hoàn chỉnh bằng tiếng Anh qua micro (độ dài đoạn âm thanh khoảng 3–5 giây)."),
            ("Thành phần bị tác động (Artifact)", "Speech Processing Worker (Silero VAD → Faster-Whisper → Bilingual Translator) và WebSocket Broadcast Engine."),
            ("Môi trường (Environment)", "Giờ học bình thường, hệ thống đang duy trì kết nối WebSocket đồng thời với 60 thiết bị của sinh viên trong lớp."),
            ("Phản hồi của hệ thống (Response)", "Hệ thống lọc bỏ khoảng lặng, nhận diện giọng nói thành văn bản tiếng Anh, dịch sang tiếng Việt (bảo toàn thuật ngữ CNTT) và đẩy đồng loạt phụ đề song ngữ lên màn hình chiếu và thiết bị sinh viên."),
            ("Thước đo phản hồi (Response Measure)", "Tổng độ trễ đầu-cuối (End-to-End Latency) từ lúc giảng viên ngắt câu đến khi phụ đề hiển thị trên màn hình đạt ≤ 1.5 giây đối với ít nhất 95% các câu thoại."),
        ])
    )

    elems.append(make_h3("Kịch bản 1.2: Gom cụm ngữ nghĩa khi nhiều sinh viên hỏi đồng thời (FR-03)"))
    elems.append(
        make_scenario_table_doc([
            ("Nguồn kích thích (Source)", "40 sinh viên trong lớp học EMI."),
            ("Tác nhân kích thích (Stimulus)", "Sinh viên gửi dồn dập 40 câu hỏi (bằng cả tiếng Việt, tiếng Anh và thuật ngữ pha trộn code-switching) trong vòng 15 giây sau một khái niệm khó."),
            ("Thành phần bị tác động (Artifact)", "Task Queue, NLP & LLM Inference Service (multilingual-e5-base + Semantic Clustering Engine) và Lecturer Dashboard."),
            ("Môi trường (Environment)", "Chế độ tải cao đột biến (Peak Load) trong phiên học, luồng phụ đề âm thanh vẫn đang chạy song song."),
            ("Phản hồi của hệ thống (Response)", "Hệ thống đưa yêu cầu vào hàng đợi bất đồng bộ, trích xuất vector embedding 768 chiều cho từng câu hỏi, tính khoảng cách Cosine với tâm cụm (Cluster Centroid Cache), phân loại vào cụm ngữ nghĩa và cập nhật lên Dashboard giảng viên."),
            ("Thước đo phản hồi (Response Measure)", "Thời gian xử lý trung bình để phân cụm và cập nhật giao diện cho mỗi câu hỏi mới đạt ≤ 500ms, không xảy ra hiện tượng rớt hàng đợi (0% Queue Drop)."),
        ])
    )

    elems.append(make_h3("Kịch bản 1.3: Phát tán câu trả lời đại diện 1-nhiều — Broadcast Response (FR-04)"))
    elems.append(
        make_scenario_table_doc([
            ("Nguồn kích thích (Source)", "Giảng viên."),
            ("Tác nhân kích thích (Stimulus)", "Giảng viên bấm gửi câu trả lời giải thích bằng tiếng Anh cho một cụm câu hỏi đang có 15 sinh viên theo dõi."),
            ("Thành phần bị tác động (Artifact)", "Session & QnA Controller, Bilingual Translator và WebSocket Broadcast Engine (Cluster Subscription Registry)."),
            ("Môi trường (Environment)", "Hệ thống đang hoạt động bình thường trong giờ học."),
            ("Phản hồi của hệ thống (Response)", "Hệ thống tự động dịch câu trả lời sang tiếng Việt, lưu vào PostgreSQL và tra cứu bảng đăng ký nhóm O(1) để phát đồng thời bản phản hồi song ngữ đến đúng màn hình của 15 sinh viên trong cụm."),
            ("Thước đo phản hồi (Response Measure)", "100% sinh viên trong cụm nhận được thông báo và nội dung câu trả lời trên điện thoại trong vòng ≤ 400ms kể từ khi giảng viên nhấn nút gửi."),
        ])
    )

    # 3.3 QA 2: Availability & Fault Tolerance
    elems.append(make_page_break())
    elems.append(make_h2("3.3. Phân tích QA 2: Availability & Fault Tolerance (Tính sẵn sàng & Khả năng chịu lỗi)"))
    elems.append(
        make_body_p(
            "Một buổi học thực nghiệm (Pilot) kéo dài liên tục từ 45 đến 90 phút và tuyệt đối không thể tạm dừng bài giảng của giảng viên để khắc phục sự cố phần mềm. Do hệ thống chạy các mô hình AI cục bộ tiêu tốn nhiều VRAM/GPU và hoạt động trên mạng Wi-Fi giảng đường dễ chập chờn khi có đông sinh viên truy cập, kiến trúc bắt buộc phải có cơ chế cô lập lỗi (Fault Isolation), cổng chặn dữ liệu nhiễu (VAD Gate) và khả năng tự phục hồi (Self-healing) để sự cố ở một module không làm sập toàn bộ phiên học.",
            bold_prefix="Phân tích chuyên sâu lý do lựa chọn QA 2: ",
        )
    )

    elems.append(make_h3("Kịch bản 2.1: Cô lập lỗi khi tiến trình nhận diện giọng nói (STT) bị quá tải (FR-02)"))
    elems.append(
        make_scenario_table_doc([
            ("Nguồn kích thích (Source)", "Tiến trình hệ thống nội bộ (Internal AI Worker)."),
            ("Tác nhân kích thích (Stimulus)", "Tiến trình Faster-Whisper gặp lỗi tràn bộ nhớ (Out-of-Memory - OOM) hoặc treo tiến trình do xử lý một đoạn âm thanh nhiễu kéo dài."),
            ("Thành phần bị tác động (Artifact)", "Speech Processing Worker Container (WorkerMemoryGuard & FasterWhisperEngine) và hệ thống Backend."),
            ("Môi trường (Environment)", "Đang trong giờ học trực tiếp, sinh viên vẫn đang đặt câu hỏi và giảng viên đang theo dõi Dashboard."),
            ("Phản hồi của hệ thống (Response)", "Nhờ kiến trúc tách biệt tiến trình (Worker Isolation), luồng đặt câu hỏi ẩn danh và gom cụm ngữ nghĩa (Q&A Clustering) vẫn tiếp tục hoạt động bình thường. Bộ giám sát Worker Health & Memory Guard tự động giải phóng VRAM và khởi động lại STT Worker mà không làm gián đoạn phiên học."),
            ("Thước đo phản hồi (Response Measure)", "Luồng Q&A và Dashboard duy trì 100% thời gian hoạt động (Zero Downtime); tiến trình STT tự động khôi phục và tiếp tục hiển thị phụ đề trong vòng ≤ 5 giây."),
        ])
    )

    elems.append(make_h3("Kịch bản 2.2: Tự động khôi phục khi thiết bị sinh viên rớt mạng Wi-Fi tạm thời (FR-01, FR-03)"))
    elems.append(
        make_scenario_table_doc([
            ("Nguồn kích thích (Source)", "Mạng Wi-Fi tại giảng đường."),
            ("Tác nhân kích thích (Stimulus)", "Kết nối mạng trên điện thoại của sinh viên bị ngắt quãng trong 10 giây ngay lúc sinh viên bấm nút 'Gửi câu hỏi ẩn danh'."),
            ("Thành phần bị tác động (Artifact)", "Student Mobile Web Client (Local Storage Queue & WebSocket Auto-reconnect Client)."),
            ("Môi trường (Environment)", "Môi trường mạng không ổn định tại phòng học đông người."),
            ("Phản hồi của hệ thống (Response)", "Giao diện Web của sinh viên lưu tạm câu hỏi vào bộ nhớ cục bộ (Local Storage Queue), hiển thị trạng thái chờ mạng, tự động kết nối lại (Auto-reconnect) khi có Wi-Fi, gửi lại câu hỏi và đồng bộ danh sách câu trả lời mà không bắt nhập lại mã PIN."),
            ("Thước đo phản hồi (Response Measure)", "Tỷ lệ mất mát câu hỏi của sinh viên là 0%; kết nối WebSocket và trạng thái phòng học được đồng bộ hoàn tất trong ≤ 2 giây sau khi thiết bị có mạng trở lại."),
        ])
    )

    elems.append(make_h3("Kịch bản 2.3: Chặn đứng chuỗi dữ liệu rác khi không có giọng nói giảng viên (FR-02)"))
    elems.append(
        make_scenario_table_doc([
            ("Nguồn kích thích (Source)", "Môi trường âm thanh phòng học."),
            ("Tác nhân kích thích (Stimulus)", "Giảng viên dừng giảng bài trong 3 phút để sinh viên làm bài tập, micro chỉ thu tiếng ồn quạt máy và tiếng thảo luận nhỏ trong lớp."),
            ("Thành phần bị tác động (Artifact)", "VAD Audio Gate (SileroVADGate) và STT Inference Engine (FasterWhisperEngine)."),
            ("Môi trường (Environment)", "Micro giảng viên vẫn đang bật ở chế độ thu âm trực tiếp (Live Recording)."),
            ("Phản hồi của hệ thống (Response)", "Module VAD phát hiện âm thanh không phải giọng nói rõ ràng của giảng viên (isHumanSpeech() == False) và tự động ngắt luồng đẩy audio chunk sang Whisper (Early Return), giữ nguyên màn hình phụ đề ở câu nói cuối cùng thay vì sinh ra các chuỗi văn bản ảo giác (Hallucination)."),
            ("Thước đo phản hồi (Response Measure)", "0 dòng phụ đề rác/ảo giác được hiển thị lên màn hình trong suốt thời gian giảng viên im lặng; tiết kiệm ≥ 80% tài nguyên GPU/CPU trong khoảng thời gian nghỉ."),
        ])
    )

    # 3.4 QA 3: Security & Privacy
    elems.append(make_page_break())
    elems.append(make_h2("3.4. Phân tích QA 3: Security & Privacy (Bảo mật & Quyền riêng tư ẩn danh)"))
    elems.append(
        make_body_p(
            "Yếu tố tâm lý then chốt giúp sinh viên Việt Nam vượt qua nỗi sợ để đặt câu hỏi trong lớp học tiếng Anh (EMI) là sự ẩn danh tuyệt đối. Nếu sinh viên lo sợ giảng viên hoặc bạn bè truy vết được danh tính khi hỏi một khái niệm cơ bản, họ sẽ không sử dụng hệ thống. Ngược lại, cơ chế tham gia nhanh bằng QR/PIN không cần đăng nhập tài khoản lại đặt ra thách thức bảo mật: hệ thống phải chống được hành vi cố tình spam câu hỏi rác làm loạn thuật toán phân cụm và ngăn chặn người lạ bên ngoài phòng học truy cập trái phép.",
            bold_prefix="Phân tích chuyên sâu lý do lựa chọn QA 3: ",
        )
    )

    elems.append(make_h3("Kịch bản 3.1: Bảo vệ danh tính tuyệt đối của sinh viên đặt câu hỏi (FR-01, FR-03)"))
    elems.append(
        make_scenario_table_doc([
            ("Nguồn kích thích (Source)", "Giảng viên hoặc người dùng có quyền truy cập vào giao diện quản trị/báo cáo."),
            ("Tác nhân kích thích (Stimulus)", "Kiểm tra thông tin chi tiết của một câu hỏi trên Dashboard hoặc trong dữ liệu lưu trữ cuối buổi nhằm tìm kiếm danh tính người gửi."),
            ("Thành phần bị tác động (Artifact)", "Auth & Anonymizer (SessionAuthMiddleware), Primary Database (PostgreSQL) và Lecturer Dashboard."),
            ("Môi trường (Environment)", "Trong giờ học trực tiếp và sau khi xuất báo cáo lưu trữ cuối buổi."),
            ("Phản hồi của hệ thống (Response)", "Hệ thống chỉ cấp phát một mã phiên băm ngẫu nhiên một chiều có muối (Anonymous_Hash_ID), hoàn toàn không thu thập và không lưu trữ họ tên, mã số sinh viên, email hay địa chỉ IP cá nhân vào bảng câu hỏi."),
            ("Thước đo phản hồi (Response Measure)", "0% khả năng truy vết ngược từ nội dung câu hỏi về danh tính cá nhân thật của sinh viên trên cả giao diện lẫn cơ sở dữ liệu."),
        ])
    )

    elems.append(make_h3("Kịch bản 3.2: Chống tấn công làm ngập lụt câu hỏi — Spam / Flooding Attack (FR-03)"))
    elems.append(
        make_scenario_table_doc([
            ("Nguồn kích thích (Source)", "Một sinh viên cố tình gây rối trong lớp học."),
            ("Tác nhân kích thích (Stimulus)", "Sử dụng công cụ tự động hoặc bấm liên tục để gửi 30 câu hỏi vô nghĩa trong vòng 10 giây nhằm làm nhiễu loạn thuật toán gom cụm và làm tràn màn hình giảng viên."),
            ("Thành phần bị tác động (Artifact)", "Anti-Spam Rate Limiter (AntiSpamRateLimiter) và NLP & LLM Inference Service."),
            ("Môi trường (Environment)", "Phiên học đang diễn ra bình thường."),
            ("Phản hồi của hệ thống (Response)", "Tầng kiểm soát tốc độ theo thuật toán Token Bucket (theo từng Anonymous_Hash_ID) phát hiện tần suất bất thường, lập tức chặn các request vượt ngưỡng ngay tại cổng Backend trước khi chúng đi vào mô hình AI và trả thông báo cảnh báo về thiết bị gửi."),
            ("Thước đo phản hồi (Response Measure)", "Hệ thống giới hạn tối đa 3 câu hỏi / phút trên mỗi phiên ẩn danh; 100% các request vượt ngưỡng bị từ chối trong ≤ 20ms mà không tiêu tốn tài nguyên của mô hình NLP."),
        ])
    )

    elems.append(make_h3("Kịch bản 3.3: Ngăn chặn truy cập trái phép vào phiên học đang diễn ra (FR-01)"))
    elems.append(
        make_scenario_table_doc([
            ("Nguồn kích thích (Source)", "Người dùng bên ngoài không thuộc lớp học."),
            ("Tác nhân kích thích (Stimulus)", "Cố tình đoán đường dẫn URL của phòng học để vào xem phụ đề hoặc gửi câu hỏi phá rối."),
            ("Thành phần bị tác động (Artifact)", "Auth & Anonymizer (SessionAuthMiddleware) và Classroom Projector."),
            ("Môi trường (Environment)", "Phiên học đang mở trên mạng nội bộ/Internet."),
            ("Phản hồi của hệ thống (Response)", "Hệ thống yêu cầu xác thực bằng mã PIN 6 số động (chỉ hiển thị trực tiếp trên máy chiếu tại phòng học) hoặc chữ ký số ngắn hạn nằm trong mã QR của đúng ca học đó; tự động hủy hiệu lực mã PIN ngay khi giảng viên kết thúc buổi học."),
            ("Thước đo phản hồi (Response Measure)", "Từ chối 100% các kết nối WebSocket và HTTP request không đính kèm Session Token hợp lệ của ca học hiện tại."),
        ])
    )

    # 3.5 QA 4: Modifiability
    elems.append(make_page_break())
    elems.append(make_h2("3.5. Phân tích QA 4: Modifiability (Tính dễ sửa đổi & Thử nghiệm mô hình)"))
    elems.append(
        make_body_p(
            "Dự án ClassBridge gắn liền với mục tiêu nghiên cứu khoa học thực nghiệm. Nhóm cần liên tục thử nghiệm và đối sánh các mô hình ngôn ngữ khác nhau (ví dụ: so sánh LaBSE với intfloat/multilingual-e5-base, hoặc điều chỉnh ngưỡng Cosine Similarity) để đo đạc các chỉ số học thuật (Adjusted Rand Index - ARI, NMI, Silhouette Score, WER, BLEU). Kiến trúc phải đảm bảo tính tách biệt lỏng lẻo (Loose Coupling) thông qua các giao diện trừu tượng (Interfaces) để việc thay đổi mô hình AI hoặc tham số thuật toán không làm xáo trộn hệ thống Backend, Giao diện và Cơ sở dữ liệu.",
            bold_prefix="Phân tích chuyên sâu lý do lựa chọn QA 4: ",
        )
    )

    elems.append(make_h3("Kịch bản 4.1: Thay thế mô hình trích xuất Vector Embedding để chạy Benchmark (FR-03)"))
    elems.append(
        make_scenario_table_doc([
            ("Nguồn kích thích (Source)", "Thành viên phụ trách AI/NLP của nhóm phát triển."),
            ("Tác nhân kích thích (Stimulus)", "Yêu cầu đổi mô hình embedding từ LaBSE sang intfloat/multilingual-e5-base để đo lường sự thay đổi của chỉ số Adjusted Rand Index (ARI) và Silhouette Score."),
            ("Thành phần bị tác động (Artifact)", "Embedding Model Adapter (IEmbeddingStrategy, MultilingualE5Adapter, LaBSEAdapter)."),
            ("Môi trường (Environment)", "Trong quá trình phát triển và thực nghiệm (Development / Testing)."),
            ("Phản hồi của hệ thống (Response)", "Nhờ áp dụng mẫu thiết kế Strategy/Adapter Pattern cho tầng AI, lập trình viên chỉ cần khai báo tên mô hình mới trong cấu hình và nạp Adapter tương ứng mà không cần sửa đổi logic phân cụm OnlineClusteringEngine hay cấu trúc API."),
            ("Thước đo phản hồi (Response Measure)", "Việc chuyển đổi mô hình hoàn tất và sẵn sàng chạy kiểm thử trong ≤ 1 giờ làm việc, với 0 dòng code bị sửa đổi ở tầng Frontend và Database."),
        ])
    )

    elems.append(make_h3("Kịch bản 4.2: Tinh chỉnh ngưỡng tương đồng ngữ nghĩa — Similarity Threshold (FR-03)"))
    elems.append(
        make_scenario_table_doc([
            ("Nguồn kích thích (Source)", "Nhóm nghiên cứu / Quản trị viên trong giai đoạn chạy thử nghiệm (Pilot Deployment)."),
            ("Tác nhân kích thích (Stimulus)", "Sau buổi học thử nghiệm đầu tiên, nhóm nhận thấy các câu hỏi bị gom chung hơi lỏng lẻo và muốn tăng ngưỡng Cosine Similarity từ 0.65 lên 0.75."),
            ("Thành phần bị tác động (Artifact)", "Dynamic Config Manager (DynamicConfigManager) và OnlineClusteringEngine."),
            ("Môi trường (Environment)", "Giữa các ca học thực nghiệm."),
            ("Phản hồi của hệ thống (Response)", "Tham số ngưỡng phân cụm được tách riêng thành biến cấu hình động (Runtime Settings); nhóm cập nhật giá trị mới qua hàm setThreshold(0.75) và hệ thống áp dụng ngay lập tức cho các câu hỏi tiếp theo mà không cần biên dịch (build) hay khởi động lại hệ thống."),
            ("Thước đo phản hồi (Response Measure)", "Thời gian cập nhật và áp dụng ngưỡng thuật toán mới mất ≤ 5 phút, không gây gián đoạn cơ sở dữ liệu hiện có."),
        ])
    )

    elems.append(make_h3("Kịch bản 4.3: Chuyển đổi mô hình tạo báo cáo tổng kết cuối buổi — Summarization LLM (FR-05)"))
    elems.append(
        make_scenario_table_doc([
            ("Nguồn kích thích (Source)", "Nhóm phát triển."),
            ("Tác nhân kích thích (Stimulus)", "Muốn thay đổi công cụ tổng hợp báo cáo cuối buổi từ mô hình chạy cục bộ (Qwen2.5-7B qua Ollama) sang một mô hình lượng tử hóa gọn nhẹ hơn (LightweightLLMAdapter q4_k_m) khi máy chủ tại phòng học mới thiếu VRAM."),
            ("Thành phần bị tác động (Artifact)", "SessionSummaryService và giao diện ILLMProvider (OllamaQwenAdapter, LightweightLLMAdapter)."),
            ("Môi trường (Environment)", "Trước khi triển khai tại một phòng học mới có cấu hình phần cứng khác biệt."),
            ("Phản hồi của hệ thống (Response)", "Tầng giao tiếp LLM được chuẩn hóa qua một giao diện chung (Unified LLM Interface - ILLMProvider); việc chuyển đổi Adapter xử lý tóm tắt diễn ra độc lập, giữ nguyên định dạng đối tượng trả về SessionReportDTO cho biểu đồ nhiệt (Heatmap) và file PDF lưu trữ."),
            ("Thước đo phản hồi (Response Measure)", "Thay đổi hoàn tất trong ≤ 30 phút cấu hình, 100% các tính năng hiển thị báo cáo và lưu trữ PDF hoạt động bình thường không phát sinh lỗi tương thích."),
        ])
    )
    return elems


# Detailed Component/Module Responsibility Tables for each of the 9 Diagrams
MODULE_SPECS_BY_DIAGRAM = {
    "Hinh_1_System_Context": {
        "intro": "Ở Cấp độ 1 (System Context View), hệ thống được đặt trong môi trường lớp học EMI thực tế nhằm xác định rõ ranh giới hệ thống (Context Boundary), vai trò của 3 nhóm tác nhân con người và 2 hệ thống phần cứng ngoại vi tại giảng đường:",
        "headers": ["Thành phần / Tác nhân", "Loại phần tử", "Chức năng chính, Vai trò & Trách nhiệm", "Mối quan hệ tương tác với các thành phần khác"],
        "rows": [
            [
                "ClassBridge System",
                "Software System\n(Hệ thống trung tâm)",
                "Chức năng chính: Xử lý phụ đề song ngữ thời gian thực (≤ 1.5s), gom cụm câu hỏi đa ngôn ngữ (≤ 500ms), phát tán câu trả lời đại diện 1-nhiều (≤ 400ms) và tổng hợp báo cáo Comprehension Heatmap cuối buổi.\nVai trò & Trách nhiệm: Là cầu nối trí tuệ nhân tạo tự triển khai cục bộ (Self-hosted AI) khôi phục vòng phản hồi giữa giảng viên và sinh viên mà không phụ thuộc API thương mại.",
                "• Nhận luồng âm thanh bài giảng từ Classroom Microphone [WebRTC/Audio Stream].\n• Giao tiếp 2 chiều thời gian thực với Student và Lecturer [HTTPS/WSS].\n• Nhận lệnh cấu hình tham số từ Admin [HTTPS].\n• Xuất giao diện hiển thị mã PIN/QR và phụ đề ra Classroom Projector [Browser UI].",
            ],
            [
                "Sinh viên\n(Student)",
                "Person\n(Tác nhân chính)",
                "Chức năng chính: Quét mã QR hoặc nhập PIN 6 số để vào phiên học ẩn danh, theo dõi phụ đề song ngữ Anh – Việt, gửi câu hỏi ẩn danh và nhận đáp án từ giảng viên.\nVai trò & Trách nhiệm: Người thụ hưởng phụ đề và khởi tạo tín hiệu phản hồi lỗ hổng kiến thức trong lớp EMI.",
                "• Tương tác với ClassBridge System qua trình duyệt di động [HTTPS/WSS].\n• Quan sát mã QR / mã PIN 6 số động trên Classroom Projector để xác thực vào phòng học.",
            ],
            [
                "Giảng viên\n(Lecturer)",
                "Person\n(Tác nhân chính)",
                "Chức năng chính: Khởi tạo phiên học, giảng bài bằng tiếng Anh, theo dõi bảng xếp hạng các cụm câu hỏi nóng nhất và gửi câu trả lời đại diện 1 lần cho cả cụm.\nVai trò & Trách nhiệm: Người điều phối buổi học và giải đáp các điểm nghẽn kiến thức đã được AI gom nhóm.",
                "• Nói trực tiếp vào Classroom Microphone.\n• Tương tác với ClassBridge System qua Lecturer Dashboard [HTTPS/WSS] để quản lý phiên học, trả lời cụm câu hỏi và xem Heatmap cuối buổi.",
            ],
            [
                "Quản trị viên\n(Admin)",
                "Person\n(Tác nhân quản trị)",
                "Chức năng chính: Quản lý tài khoản giảng viên, cấu hình phòng học và tinh chỉnh động các tham số AI (ngưỡng Cosine Similarity, lựa chọn Adapter mô hình).\nVai trò & Trách nhiệm: Đảm bảo hệ thống vận hành tối ưu và phục vụ thực nghiệm khoa học (QA 4).",
                "• Gửi yêu cầu cấu hình tham số AI và quản trị phiên học tới ClassBridge System [HTTPS].",
            ],
            [
                "Classroom Microphone",
                "External Hardware\n(Thiết bị ngoại vi)",
                "Chức năng chính: Thu tín hiệu giọng nói tiếng Anh trực tiếp của giảng viên tại bục giảng.\nVai trò & Trách nhiệm: Cung cấp dữ liệu âm thanh đầu vào liên tục cho luồng phụ đề thời gian thực (FR-02).",
                "• Truyền luồng âm thanh số hóa (PCM 16kHz) vào ClassBridge System qua giao thức [WebRTC / Audio Stream].",
            ],
            [
                "Classroom Projector",
                "External Display\n(Thiết bị hiển thị)",
                "Chức năng chính: Trình chiếu công khai mã PIN 6 số động, mã QR của ca học và phụ đề song ngữ trực tiếp trên phông chiếu giảng đường.\nVai trò & Trách nhiệm: Đảm bảo chỉ sinh viên có mặt vật lý trong phòng học mới thấy mã PIN (đáp ứng Kịch bản QA 3.3).",
                "• Nhận luồng hiển thị giao diện trực tiếp từ ClassBridge System [Browser UI].",
            ],
        ],
    },
    "Hinh_2_Container": {
        "intro": "Ở Cấp độ 2 (Container / Top-Level Module Decomposition View), hệ thống ClassBridge được phân rã thành 07 Container độc lập nhằm thỏa mãn trực tiếp Kịch bản QA 2.1 (Worker Isolation), QA 2.2 (Offline Queue), QA 1.2 (0% Queue Drop) và QA 3.1 (Ẩn danh):",
        "headers": ["Tên Container / Module", "Công nghệ", "Chức năng chính, Vai trò & Trách nhiệm", "Mối quan hệ với các Thành phần khác"],
        "rows": [
            [
                "Student Mobile Web",
                "Next.js / React\n(Browser UI)",
                "Chức năng chính: Hiển thị phụ đề song ngữ thời gian thực, cung cấp khung đặt câu hỏi ẩn danh đa ngôn ngữ và nhận thông báo câu trả lời.\nVai trò & Trách nhiệm: Giao diện Zero-Install cho sinh viên; tích hợp Local Storage Queue & Auto-reconnect để đạt 0% mất câu hỏi và đồng bộ lại ≤ 2s khi rớt Wi-Fi (QA 2.2).",
                "• Phục vụ trực tiếp tác nhân Sinh viên [HTTPS/WSS].\n• Kết nối hai chiều với Backend API & WebSocket [JSON / WebSocket] để gửi câu hỏi và nhận phụ đề/đáp án.",
            ],
            [
                "Lecturer Dashboard",
                "Next.js / React\n(Browser UI)",
                "Chức năng chính: Khởi tạo phiên học, thu âm giọng giảng, hiển thị các cụm câu hỏi theo mức độ ưu tiên, gửi câu trả lời đại diện 1-nhiều và hiển thị biểu đồ Comprehension Heatmap.\nVai trò & Trách nhiệm: Trung tâm chỉ huy và quan sát điểm nghẽn kiến thức dành cho giảng viên.",
                "• Phục vụ trực tiếp Giảng viên & Admin [HTTPS/WSS].\n• Truyền Audio chunk và gửi câu trả lời cụm tới Backend API & WebSocket [JSON / WebSocket].",
            ],
            [
                "Backend API & WebSocket",
                "Python / FastAPI\n(Core Server)",
                "Chức năng chính: Quản lý vòng đời phiên học, xác thực PIN/QR, băm ẩn danh Anonymous_Hash_ID, kiểm soát tốc độ chống Spam (≤ 20ms) và điều phối phát tán WebSocket 1-nhiều (≤ 400ms).\nVai trò & Trách nhiệm: Nhạc trưởng trung tâm kết nối tầng giao diện, tầng dữ liệu và 2 tiến trình AI Worker.",
                "• Nhận kết nối từ Student Mobile Web và Lecturer Dashboard [JSON/WebSocket].\n• Giao việc bất đồng bộ cho Speech Processing Worker và NLP & LLM Inference Service [Async Worker Task].\n• Đọc/ghi sự kiện với Task Queue & Cache [Async I/O] và Primary Database [SQL/Asyncpg].",
            ],
            [
                "Speech Processing Worker",
                "Silero VAD +\nFaster-Whisper +\nNLLB",
                "Chức năng chính: Lọc khoảng lặng/tạp âm, nhận diện giọng nói tiếng Anh sang văn bản và dịch thuật ngữ CNTT sang tiếng Việt (≤ 1.5s).\nVai trò & Trách nhiệm: Tiến trình AI xử lý âm thanh được cô lập hoàn toàn (Worker Isolation) để nếu gặp lỗi OOM vẫn tự khởi động lại ≤ 5s mà không làm sập luồng Hỏi đáp Q&A (QA 2.1, QA 2.3).",
                "• Nhận Audio chunk (3–5s) từ Backend API & WebSocket / Task Queue và trả về gói phụ đề song ngữ [Async Worker Task].",
            ],
            [
                "NLP & LLM Inference Service",
                "multilingual-e5-base\n+ Qwen2.5 / Ollama",
                "Chức năng chính: Trích xuất vector ngữ nghĩa 768 chiều, gom cụm câu hỏi bằng khoảng cách Cosine (≤ 500ms) và tổng hợp báo cáo + Heatmap cuối buổi.\nVai trò & Trách nhiệm: Tiến trình AI xử lý ngôn ngữ tự nhiên độc lập, đảm bảo tính mô-đun hóa và dễ dàng thay thế mô hình nghiên cứu (QA 1.2, QA 4).",
                "• Nhận câu hỏi mới và yêu cầu tổng kết cuối buổi từ Backend API & WebSocket [Async Worker Task], trả về kết quả phân cụm và báo cáo JSON.",
            ],
            [
                "Task Queue & Cache",
                "In-Memory / Redis",
                "Chức năng chính: Đệm hàng đợi sự kiện âm thanh, hàng đợi câu hỏi đột biến và lưu trạng thái phiên học/tâm cụm.\nVai trò & Trách nhiệm: Chống nghẽn cổ chai, đảm bảo 0% rớt hàng đợi (0% Queue Drop) khi 40 sinh viên hỏi đồng thời trong 15 giây (QA 1.2).",
                "• Giao tiếp tốc độ cao với Backend API & WebSocket và các AI Workers [Async I/O].",
            ],
            [
                "Primary Database",
                "PostgreSQL",
                "Chức năng chính: Lưu trữ bền vững thông tin phiên học, bản ghi lời giảng (transcript), danh sách cụm câu hỏi và báo cáo tổng kết.\nVai trò & Trách nhiệm: Đảm bảo toàn vẹn dữ liệu và quyền riêng tư tuyệt đối (chỉ lưu Anonymous_Hash_ID, 0% lưu thông tin định danh cá nhân theo QA 3.1).",
                "• Nhận truy vấn đọc/ghi bất đồng bộ từ Backend API & WebSocket và các Worker thông qua giao thức [SQL / Asyncpg].",
            ],
        ],
    },
    "Hinh_3_1_Component_Backend": {
        "intro": "Hình 3.1 thể hiện cấu trúc Layered & Uses Module View bên trong Container Backend API & WebSocket Server (FastAPI), được chia thành 3 tầng chức năng rõ rệt (Tầng Bảo mật & Chống Spam → Tầng Điều phối REST & WebSocket → Tầng Cấu hình động & Truy xuất Dữ liệu):",
        "headers": ["Tên Component (Module)", "Tầng kiến trúc", "Chức năng chính, Vai trò & Trách nhiệm", "Mối quan hệ (Uses / Giao tiếp)"],
        "rows": [
            [
                "Auth & Anonymizer",
                "Tầng 1: Security Middleware",
                "Chức năng chính: Kiểm tra mã PIN 6 số động hoặc chữ ký QR ngắn hạn; sinh mã băm một chiều Anonymous_Hash_ID.\nVai trò & Trách nhiệm: Chốt chặn bảo mật đầu tiên, từ chối 100% truy cập trái phép từ ngoài lớp (QA 3.3) và xóa bỏ hoàn toàn liên kết tới danh tính thật của sinh viên (QA 3.1).",
                "• Nhận request từ Student Mobile Web [HTTPS/REST].\n• Chuyển tiếp request đã gắn Anonymous_Hash_ID sang Anti-Spam Rate Limiter và cấp quyền kết nối vào WebSocket Broadcast Engine.",
            ],
            [
                "Anti-Spam Rate Limiter",
                "Tầng 1: Token Bucket Filter",
                "Chức năng chính: Đếm và giới hạn tần suất gửi câu hỏi tối đa 3 câu/phút trên mỗi Anonymous_Hash_ID.\nVai trò & Trách nhiệm: Chặn đứng tấn công làm ngập lụt câu hỏi (Flooding/Spam Attack) trong ≤ 20ms ngay tại cổng vào, bảo vệ tài nguyên GPU/CPU của tầng AI (QA 3.2).",
                "• Nhận request đã xác thực từ Auth & Anonymizer và Lecturer Dashboard.\n• Chỉ chuyển các câu hỏi hợp lệ xuống Session & QnA Controller.",
            ],
            [
                "Session & QnA Controller",
                "Tầng 2: FastAPI Router Controller",
                "Chức năng chính: Điều phối khởi tạo phiên học, tiếp nhận câu hỏi hợp lệ, xử lý câu trả lời đại diện của giảng viên và kích hoạt tạo báo cáo cuối buổi.\nVai trò & Trách nhiệm: Bộ não điều phối nghiệp vụ trung tâm của Backend.",
                "• Nhận câu hỏi hợp lệ từ Anti-Spam Rate Limiter.\n• Giao tác vụ phân cụm & tóm tắt cho NLP & LLM Service [Async Worker].\n• Kích hoạt WebSocket Broadcast Engine để phát tán đáp án 1-nhiều.\n• Đọc/cập nhật ngưỡng qua Dynamic Config Manager và lưu dữ liệu qua Data Access Repository.",
            ],
            [
                "WebSocket Broadcast Engine",
                "Tầng 2: Real-time WS Manager",
                "Chức năng chính: Quản lý danh sách kết nối theo Phòng học (Room) và Cụm câu hỏi (Cluster Group); đẩy phụ đề và đáp án song ngữ thời gian thực.\nVai trò & Trách nhiệm: Đảm bảo tốc độ phát tán câu trả lời 1-nhiều đạt ≤ 400ms tới 100% sinh viên trong cụm (QA 1.3).",
                "• Nhận lệnh Broadcast từ Session & QnA Controller.\n• Đẩy Audio chunk và nhận phụ đề từ Speech Processing Worker [Async Worker].\n• Đẩy gói tin JSON trực tiếp tới Student Mobile Web và Lecturer Dashboard.",
            ],
            [
                "Dynamic Config Manager",
                "Tầng 3: Runtime Settings",
                "Chức năng chính: Lưu giữ và cập nhật nóng các tham số thuật toán (như ngưỡng Cosine Similarity 0.65 → 0.75).\nVai trò & Trách nhiệm: Cho phép tinh chỉnh tham số thực nghiệm trong ≤ 5 phút giữa các ca học mà không cần build lại hệ thống (QA 4.2).",
                "• Cung cấp và cập nhật tham số cấu hình thời gian thực cho Session & QnA Controller và WebSocket Broadcast Engine.",
            ],
            [
                "Data Access Repository",
                "Tầng 3: SQLAlchemy Async",
                "Chức năng chính: Thực thi các truy vấn bất đồng bộ đọc/ghi phiên học, cụm câu hỏi ẩn danh và báo cáo tổng kết.\nVai trò & Trách nhiệm: Tách biệt hoàn toàn logic nghiệp vụ khỏi chi tiết truy vấn cơ sở dữ liệu quan hệ.",
                "• Được gọi bởi Session & QnA Controller.\n• Thực thi giao dịch SQL bất đồng bộ xuống Primary Database (PostgreSQL).",
            ],
        ],
    },
    "Hinh_3_2_Component_Speech_Worker": {
        "intro": "Hình 3.2 thể hiện cấu trúc Module View bên trong Container Speech Processing Worker (Isolated Python Worker), giải quyết trọn vẹn tính năng FR-02 cùng các kịch bản QA 1.1 (Độ trễ ≤ 1.5s), QA 2.1 (Tự phục hồi OOM ≤ 5s) và QA 2.3 (Chặn 100% ảo giác khi giảng viên im lặng):",
        "headers": ["Tên Component (Module)", "Loại Component", "Chức năng chính, Vai trò & Trách nhiệm", "Mối quan hệ (Uses / Luồng dữ liệu)"],
        "rows": [
            [
                "Audio Stream Consumer",
                "Async Worker\n(Input Adapter)",
                "Chức năng chính: Tiêu thụ các đoạn âm thanh cắt ngắn (Audio Chunk 3–5s) từ hàng đợi và chuẩn hóa về PCM 16kHz mono.\nVai trò & Trách nhiệm: Chuẩn hóa tín hiệu âm thanh đầu vào ổn định trước khi qua cổng lọc giọng nói.",
                "• Nhận Audio Chunk từ Task Queue (Audio Stream).\n• Truyền luồng dữ liệu PCM 16kHz sang VAD Audio Gate.",
            ],
            [
                "VAD Audio Gate",
                "Silero VAD\n(Acoustic Filter)",
                "Chức năng chính: Phát hiện hoạt động giọng nói con người (Voice Activity Detection) và cắt bỏ khoảng lặng.\nVai trò & Trách nhiệm: Ngắt luồng ngay lập tức khi giảng viên dừng giảng bài (chỉ có tiếng quạt/tiếng ồn nền), chặn 100% lỗi ảo giác (Hallucination) và tiết kiệm ≥ 80% GPU/CPU (QA 2.3).",
                "• Nhận PCM Bytes từ Audio Stream Consumer.\n• Chỉ đẩy các đoạn âm thanh có giọng nói hợp lệ xuống STT Inference Engine.",
            ],
            [
                "STT Inference Engine",
                "Faster-Whisper\n(CTranslate2 FP16)",
                "Chức năng chính: Giải mã âm thanh giọng giảng tiếng Anh thành văn bản gốc với tốc độ cao.\nVai trò & Trách nhiệm: Trái tim nhận diện giọng nói cục bộ, tối ưu hóa bộ nhớ VRAM trên GPU.",
                "• Nhận Filtered Audio từ VAD Audio Gate.\n• Được giám sát liên tục bởi Worker Health & Memory Guard.\n• Chuyển văn bản tiếng Anh (Raw Transcript) sang Bilingual Translator.",
            ],
            [
                "Bilingual Translator",
                "NLLB-200 / EnViT5\n(Translation Module)",
                "Chức năng chính: Dịch phụ đề tiếng Anh sang tiếng Việt, bảo toàn chính xác các thuật ngữ chuyên ngành CNTT.\nVai trò & Trách nhiệm: Hoàn tất cặp phụ đề song ngữ đảm bảo tổng độ trễ đầu-cuối ≤ 1.5s (QA 1.1).",
                "• Nhận văn bản gốc từ STT Inference Engine.\n• Đẩy phụ đề song ngữ (≤ 1.5s) ra WebSocket Broadcast Engine.\n• Ghi nhận câu thoại xuống Transcript Buffer.",
            ],
            [
                "Worker Health & Memory Guard",
                "Fault Supervisor\n(Watchdog)",
                "Chức năng chính: Theo dõi mức tiêu thụ VRAM/RAM của tiến trình STT và bắt ngoại lệ Out-of-Memory (OOM).\nVai trò & Trách nhiệm: Tự động giải phóng bộ nhớ và khởi động lại mô hình STT trong ≤ 5s mà không ảnh hưởng tới luồng Q&A (QA 2.1).",
                "• Giám sát và thực thi cơ chế tự phục hồi trực tiếp trên STT Inference Engine [Process Watchdog].",
            ],
            [
                "Transcript Buffer",
                "Batch Writer\n(State Buffer)",
                "Chức năng chính: Đệm các câu thoại song ngữ kèm dấu thời gian (Timestamp) và ghi theo lô xuống CSDL.\nVai trò & Trách nhiệm: Giảm tải I/O cho cơ sở dữ liệu trong giờ giảng và cung cấp dữ liệu đầu vào cho báo cáo cuối buổi (FR-05).",
                "• Nhận bản ghi câu thoại từ Bilingual Translator [Async I/O].\n• Lưu trữ bền vững xuống Primary Database (PostgreSQL).",
            ],
        ],
    },
    "Hinh_3_3_Component_NLP_LLM": {
        "intro": "Hình 3.3 thể hiện cấu trúc Module View bên trong Container NLP & LLM Inference Service, hiện thực hóa tính năng gom nhóm câu hỏi đa ngôn ngữ (FR-03), tổng hợp báo cáo & Heatmap cuối buổi (FR-05), đồng thời đáp ứng Kịch bản QA 1.2 (≤ 500ms), QA 4.1 (Đổi mô hình Embedding ≤ 1h) và QA 4.3 (Đổi LLM ≤ 30p):",
        "headers": ["Tên Component (Module)", "Loại Component", "Chức năng chính, Vai trò & Trách nhiệm", "Mối quan hệ (Uses / Luồng dữ liệu)"],
        "rows": [
            [
                "Multilingual Text Normalizer",
                "Preprocessor\n(Text Cleaner)",
                "Chức năng chính: Làm sạch câu hỏi tự do của sinh viên, chuẩn hóa Unicode NFC, từ viết tắt và cấu trúc pha trộn Việt – Anh (code-switching).\nVai trò & Trách nhiệm: Đảm bảo chất lượng đầu vào đồng nhất trước khi trích xuất vector ngữ nghĩa.",
                "• Nhận câu hỏi ẩn danh mới từ Session & QnA Controller.\n• Chuyển chuỗi văn bản đã làm sạch sang Embedding Model Adapter.",
            ],
            [
                "Embedding Model Adapter",
                "Strategy Pattern\n(Vector Encoder)",
                "Chức năng chính: Ánh xạ câu hỏi đa ngôn ngữ thành vector ngữ nghĩa dày đặc 768 chiều.\nVai trò & Trách nhiệm: Đóng gói mô hình ngôn ngữ theo mẫu Strategy/Adapter, cho phép hoán đổi giữa multilingual-e5-base và LaBSE trong ≤ 1 giờ để chạy Benchmark (QA 4.1).",
                "• Nhận Normalized Text từ Multilingual Text Normalizer.\n• Truyền mảng số thực Vector 768 chiều xuống Semantic Clustering Engine.",
            ],
            [
                "Semantic Clustering Engine",
                "Cosine Similarity\n(Core Engine)",
                "Chức năng chính: Tính độ tương đồng Cosine giữa vector câu hỏi mới với tâm các cụm hiện có; tự động gộp vào cụm vượt ngưỡng hoặc tạo cụm mới.\nVai trò & Trách nhiệm: Xử lý phân cụm trực tuyến trong ≤ 500ms/câu hỏi với 0% rớt hàng đợi (QA 1.2).",
                "• Nhận Vector 768 chiều từ Embedding Model Adapter.\n• Đọc và cập nhật tâm cụm với Cluster Centroid Cache.\n• Đẩy danh sách cụm cập nhật (≤ 500ms) ra Lecturer Dashboard.",
            ],
            [
                "Unified LLM Summarizer",
                "Qwen2.5-7B / Ollama\n(LLM Adapter)",
                "Chức năng chính: Tổng hợp nội dung cốt lõi của bài giảng từ transcript và các cụm câu hỏi; đối chiếu mật độ câu hỏi theo dòng thời gian để tính Comprehension Heatmap.\nVai trò & Trách nhiệm: Chuẩn hóa giao diện gọi LLM cục bộ, hỗ trợ đổi sang mô hình nhẹ trong ≤ 30 phút khi thiếu VRAM (QA 4.3).",
                "• Nhận sự kiện kết thúc buổi học (End Session Event) từ Session & QnA Controller.\n• Chuyển kết quả tổng hợp có cấu trúc xuống Report & Heatmap Exporter.",
            ],
            [
                "Cluster Centroid Cache",
                "Vector State\n(In-Memory Cache)",
                "Chức năng chính: Lưu trữ nhanh các vector tâm cụm (Centroids) đang hoạt động trong phiên học trên bộ nhớ RAM.\nVai trò & Trách nhiệm: Giúp phép tính khoảng cách Cosine đạt tốc độ mili-giây mà không phải đọc lại từ ổ cứng.",
                "• Phục vụ truy xuất/cập nhật tức thì cho Semantic Clustering Engine.\n• Đồng bộ dữ liệu cụm câu hỏi xuống Primary Database (PostgreSQL).",
            ],
            [
                "Report & Heatmap Exporter",
                "JSON / PDF Builder\n(Exporter)",
                "Chức năng chính: Đóng gói dữ liệu tóm tắt bài giảng, danh sách cụm câu hỏi đã giải đáp và tọa độ Comprehension Heatmap thành chuẩn JSON và file PDF.\nVai trò & Trách nhiệm: Cung cấp tư liệu ôn tập hoàn chỉnh sau buổi học (FR-05).",
                "• Nhận dữ liệu từ Unified LLM Summarizer.\n• Lưu trữ báo cáo & Heatmap xuống Primary Database (PostgreSQL).",
            ],
        ],
    },
    "Hinh_4_1_Code_Speech_Pipeline": {
        "intro": "Hình 4.1 biểu diễn cấu trúc Code / Class & Interface View của Speech Processing Module (FR-02), thể hiện rõ cách sử dụng mẫu thiết kế Polymorphism / Strategy Interface (ISTTEngine, ITranslator) kết hợp lớp kiểm soát lỗi WorkerMemoryGuard và cổng lọc SileroVADGate:",
        "headers": ["Tên Lớp / Giao diện (Class/Interface)", "Vai trò trong Module", "Chức năng chính, Thuộc tính & Phương thức Trách nhiệm", "Mối quan hệ (Implements / Calls / Instantiates)"],
        "rows": [
            [
                "class SpeechPipelineWorker",
                "Core Worker Controller",
                "Chức năng & Trách nhiệm: Lớp điều phối trung tâm của luồng phụ đề qua hàm processAudioChunk(sessionId, audio). Thực thi kiểm tra vadGate.isHumanSpeech() đầu tiên để thoát sớm (Early Return) nếu im lặng; gọi đa hình sttEngine.transcribe() và translator.translateEnToVi().",
                "• Phụ thuộc (Uses) vào SileroVADGate và WorkerMemoryGuard.\n• Gọi đa hình qua giao diện ISTTEngine và ITranslator.\n• Khởi tạo (Instantiates) đối tượng kết quả SubtitlePayloadDTO (≤ 1.5s).",
            ],
            [
                "class SileroVADGate",
                "VAD Filter Class\n(Kịch bản QA 2.3)",
                "Chức năng & Trách nhiệm: Lọc khoảng lặng và tạp âm phòng học với ngưỡng probThreshold = 0.5. Cung cấp isHumanSpeech(audioBytes): bool và trimSilence(audioBytes): bytes để chặn 100% văn bản ảo giác và tiết kiệm ≥ 80% tài nguyên GPU.",
                "• Được gọi trực tiếp ở bước 1 bởi SpeechPipelineWorker trước khi chạm tới mô hình Whisper.",
            ],
            [
                "class WorkerMemoryGuard",
                "Fault Isolation Class\n(Kịch bản QA 2.1)",
                "Chức năng & Trách nhiệm: Giám sát giới hạn bộ nhớ maxVramLimitMB. Cung cấp checkMemory(engine) và recoverOnOOM(engine) để tự động giải phóng VRAM và nạp lại mô hình trong ≤ 5s khi xảy ra lỗi tràn bộ nhớ.",
                "• Giám sát và bảo vệ vòng đời thực thi của SpeechPipelineWorker và FasterWhisperEngine.",
            ],
            [
                "<<interface>> ISTTEngine\n& class FasterWhisperEngine",
                "STT Strategy Interface\n& Concrete Adapter",
                "Chức năng & Trách nhiệm: Giao diện ISTTEngine định nghĩa hợp đồng transcribe(audioBytes): str. Lớp FasterWhisperEngine hiện thực hóa bằng động cơ CTranslate2 (computeType='int8_float16') và hỗ trợ reloadModel().",
                "• FasterWhisperEngine thực thi (Implements) giao diện ISTTEngine và được tiêm (Inject) vào SpeechPipelineWorker.",
            ],
            [
                "<<interface>> ITranslator\n& class NLLBTranslatorAdapter",
                "Translation Interface\n& Concrete Adapter",
                "Chức năng & Trách nhiệm: Giao diện ITranslator định nghĩa hợp đồng translateEnToVi(text): str. Lớp NLLBTranslatorAdapter bọc mô hình AutoModelForSeq2SeqLM (Meta NLLB-200 / EnViT5) để dịch chuẩn thuật ngữ CNTT.",
                "• NLLBTranslatorAdapter thực thi (Implements) giao diện ITranslator và được gọi bởi SpeechPipelineWorker.",
            ],
            [
                "class SubtitlePayloadDTO",
                "Data Transfer Object",
                "Chức năng & Trách nhiệm: Đóng gói dữ liệu phụ đề chuẩn hóa gồm sessionId, englishText, vietnameseText và timestamp để đẩy qua WebSocket trong ≤ 1.5s (QA 1.1).",
                "• Được khởi tạo bởi SpeechPipelineWorker và truyền sang WebSocket Broadcast Engine.",
            ],
        ],
    },
    "Hinh_4_2_Code_Clustering": {
        "intro": "Hình 4.2 biểu diễn cấu trúc Code / Class & Strategy Interface View của Semantic Question Clustering Module (FR-03), minh họa trực tiếp cách đạt được Kịch bản QA 4.1 (Thay đổi mô hình Embedding trong ≤ 1 giờ với 0 dòng code sửa ở UI/DB), QA 4.2 (Đổi nóng ngưỡng Cosine ≤ 5 phút) và QA 1.2 (Phân cụm ≤ 500ms):",
        "headers": ["Tên Lớp / Giao diện (Class/Interface)", "Vai trò trong Module", "Chức năng chính, Thuộc tính & Phương thức Trách nhiệm", "Mối quan hệ (Implements / Calls / Composition)"],
        "rows": [
            [
                "class OnlineClusteringEngine",
                "Core Clustering Service",
                "Chức năng & Trách nhiệm: Thực thi thuật toán gom cụm trực tuyến qua assignOrCreateCluster(q, clusters), computeCosine(vecA, vecB) và updateCentroid(cluster, newVec) trong ≤ 500ms/câu hỏi (QA 1.2).",
                "• Đọc ngưỡng động từ DynamicConfigManager.\n• Nhận văn bản sạch từ MultilingualNormalizer.\n• Gọi đa hình encode(text) qua giao diện IEmbeddingStrategy.\n• Quản lý và cập nhật đối tượng QuestionCluster.",
            ],
            [
                "class DynamicConfigManager",
                "Runtime Config Class\n(Kịch bản QA 4.2)",
                "Chức năng & Trách nhiệm: Quản lý thuộc tính similarityThreshold: float = 0.75 thông qua getThreshold() và setThreshold(newVal), cho phép đổi nóng ngưỡng phân cụm từ 0.65 lên 0.75 ngay giữa ca học trong ≤ 5 phút.",
                "• Cung cấp ngưỡng tương đồng thời gian thực cho OnlineClusteringEngine.",
            ],
            [
                "class MultilingualNormalizer",
                "Text Preprocessor Class",
                "Chức năng & Trách nhiệm: Cung cấp phương thức cleanCodeSwitching(text: str): str để chuẩn hóa câu hỏi pha trộn tiếng Việt – tiếng Anh trước khi mã hóa vector.",
                "• Tiền xử lý chuỗi văn bản đầu vào cho OnlineClusteringEngine.",
            ],
            [
                "<<interface>> IEmbeddingStrategy",
                "Strategy Pattern Interface\n(Kịch bản QA 4.1)",
                "Chức năng & Trách nhiệm: Giao diện trừu tượng hóa việc trích xuất vector ngữ nghĩa 768 chiều qua phương thức duy nhất encode(text: str): List[float].",
                "• Được gọi bởi OnlineClusteringEngine và được hiện thực hóa bởi MultilingualE5Adapter & LaBSEAdapter.",
            ],
            [
                "class MultilingualE5Adapter\n& class LaBSEAdapter",
                "Concrete Strategy Adapters\n(Kịch bản QA 4.1)",
                "Chức năng & Trách nhiệm: Hai lớp Adapter độc lập bọc mô hình intfloat/multilingual-e5-base (có hàm addQueryPrefix) và sentence-transformers/LaBSE, giúp nhóm nghiên cứu chuyển đổi mô hình chạy Benchmark ARI/Silhouette trong ≤ 1 giờ.",
                "• Cùng thực thi (Implements) giao diện IEmbeddingStrategy mà không làm thay đổi bất kỳ dòng code nào của OnlineClusteringEngine.",
            ],
            [
                "class QuestionCluster &\nclass QuestionEntity",
                "Domain Entities",
                "Chức năng & Trách nhiệm: QuestionCluster lưu giữ clusterId, representativeText, centroidVector và danh sách subscriberAnonIds. QuestionEntity lưu questionId, anonymousHashId, rawContent và embeddingVector.",
                "• Một QuestionCluster chứa nhiều QuestionEntity theo quan hệ hợp thành 1-nhiều (1-to-Many Composition).",
            ],
        ],
    },
    "Hinh_4_3_Code_Security_Broadcast": {
        "intro": "Hình 4.3 biểu diễn cấu trúc Code / Class View của Security & 1-to-Many Broadcast Module (FR-01, FR-04), giải quyết trực tiếp 3 kịch bản bảo mật QA 3.1 (0% lộ danh tính), QA 3.2 (Chặn Spam ≤ 20ms), QA 3.3 (Chặn truy cập trái phép bằng PIN/QR động) và kịch bản hiệu năng QA 1.3 (Broadcast 1-nhiều ≤ 400ms):",
        "headers": ["Tên Lớp / Cấu trúc (Class/Registry)", "Vai trò trong Module", "Chức năng chính, Thuộc tính & Phương thức Trách nhiệm", "Mối quan hệ (Calls / Lookup / Broadcast)"],
        "rows": [
            [
                "class SessionAuthMiddleware",
                "Security Guard Class\n(QA 3.1 & QA 3.3)",
                "Chức năng & Trách nhiệm: Kiểm tra tính hợp lệ của mã PIN 6 số động hoặc token QR qua verifyPinOrQR(sessionId, token): bool (chặn 100% người lạ ngoài lớp). Sinh định danh ẩn danh một chiều qua generateAnonHash(sessionId, key) với secretSalt.",
                "• Đón nhận trực tiếp Student & Lecturer Request.\n• Chuyển request hợp lệ kèm Anonymous_Hash_ID sang AntiSpamRateLimiter.",
            ],
            [
                "class AntiSpamRateLimiter",
                "Token Bucket Class\n(Kịch bản QA 3.2)",
                "Chức năng & Trách nhiệm: Giới hạn tốc độ gửi câu hỏi với maxQuestionsPerMin = 3. Phương thức allowRequest(anonHashId): bool từ chối tức thì mọi request spam trong ≤ 20ms trước khi chạm tới tầng AI.",
                "• Nhận Anonymous_Hash_ID từ SessionAuthMiddleware.\n• Chỉ cho phép các yêu cầu hợp lệ đi vào QnAController.",
            ],
            [
                "class QnAController",
                "FastAPI Router Controller",
                "Chức năng & Trách nhiệm: Cung cấp 2 điểm cuối nghiệp vụ chính: submitQuestion(sessionId, anonId, text) để nhận câu hỏi & đăng ký sinh viên vào cụm; answerCluster(clusterId, answerText) để nhận câu trả lời đại diện từ giảng viên.",
                "• Gọi BilingualTranslator.translateAnswer() để dịch câu trả lời.\n• Gọi WebSocketBroadcastManager.broadcastToCluster() và đóng gói BilingualAnswerDTO.",
            ],
            [
                "class WebSocketBroadcastManager",
                "Real-time Engine Class\n(Kịch bản QA 1.3)",
                "Chức năng & Trách nhiệm: Quản lý kết nối thời gian thực qua subscribeCluster(clusterId, anonId, ws) và phát tán đồng loạt đáp án qua broadcastToCluster(clusterId, payload) trong ≤ 400ms.",
                "• Tra cứu danh sách kết nối WebSocket với độ phức tạp O(1) trên Cluster Subscription Registry.",
            ],
            [
                "Cluster Subscription Registry\n& class BilingualAnswerDTO",
                "In-Memory Map &\nResponse Payload",
                "Chức năng & Trách nhiệm: Bảng băm ánh xạ Dict[clusterId, Set[WebSocket]] lưu danh sách sinh viên đang theo dõi từng cụm; BilingualAnswerDTO đóng gói clusterId, answerEn, answerVi.",
                "• Phục vụ tra cứu O(1) và truyền tải gói tin WebSocket Frame tới 100% sinh viên trong cụm.",
            ],
        ],
    },
    "Hinh_4_4_Code_Summary_Heatmap": {
        "intro": "Hình 4.4 biểu diễn cấu trúc Code / Class & Unified Interface View của Session Summary & Heatmap Module (FR-05), hiện thực hóa Kịch bản QA 4.3 (Chuyển đổi linh hoạt mô hình LLM tạo báo cáo cuối buổi trong ≤ 30 phút cấu hình khi máy chủ thiếu VRAM):",
        "headers": ["Tên Lớp / Giao diện (Class/Interface)", "Vai trò trong Module", "Chức năng chính, Thuộc tính & Phương thức Trách nhiệm", "Mối quan hệ (Implements / Calls / Produces)"],
        "rows": [
            [
                "class SessionSummaryService",
                "Core Summary Service",
                "Chức năng & Trách nhiệm: Điều phối quy trình tổng kết cuối buổi học qua generateEndSessionReport(sessionId): SessionReportDTO và hỗ trợ chuyển đổi nóng mô hình qua switchLLMProvider(newProvider).",
                "• Truy xuất dữ liệu từ SessionRepository.\n• Gọi HeatmapCalculator để tính mật độ câu hỏi theo giờ.\n• Gọi đa hình summarize() qua giao diện ILLMProvider và xuất SessionReportDTO.",
            ],
            [
                "class SessionRepository",
                "Data Access Class",
                "Chức năng & Trách nhiệm: Cung cấp getSessionTranscripts(sessionId), getSessionClusters(sessionId) và saveReport(reportDTO) để đọc lịch sử buổi học và lưu báo cáo.",
                "• Cung cấp dữ liệu đầu vào bất đồng bộ cho SessionSummaryService.",
            ],
            [
                "class HeatmapCalculator",
                "Analytics Helper Class",
                "Chức năng & Trách nhiệm: Thực thi thuật toán alignQuestionsToTimeline(transcripts, clusters): List[HeatmapPoint] để khớp thời điểm sinh viên đặt câu hỏi với mốc thời gian giảng bài, xác định chính xác đoạn kiến thức gây khó hiểu nhất.",
                "• Trả danh sách điểm nhiệt (HeatmapPoint) cho SessionSummaryService.",
            ],
            [
                "<<interface>> ILLMProvider",
                "Unified LLM Interface\n(Kịch bản QA 4.3)",
                "Chức năng & Trách nhiệm: Giao diện thống nhất định nghĩa phương thức summarize(transcript: str, clusters: List): str, tách biệt hoàn toàn logic tạo báo cáo khỏi mô hình LLM cụ thể.",
                "• Được gọi bởi SessionSummaryService và được hiện thực hóa bởi các lớp Adapter LLM.",
            ],
            [
                "class OllamaQwenAdapter &\nclass LightweightLLMAdapter",
                "Concrete LLM Adapters\n(Kịch bản QA 4.3)",
                "Chức năng & Trách nhiệm: OllamaQwenAdapter kết nối mô hình mặc định qwen2.5:7b; LightweightLLMAdapter chạy mô hình lượng tử hóa nhẹ q4_k_m khi máy chủ phòng học thiếu VRAM (chuyển đổi trong ≤ 30 phút cấu hình).",
                "• Cùng thực thi (Implements) giao diện ILLMProvider, đảm bảo 100% tương thích ngược.",
            ],
            [
                "class SessionReportDTO",
                "Report & Heatmap Payload",
                "Chức năng & Trách nhiệm: Cấu trúc dữ liệu chuẩn hóa chứa sessionId, executiveSummary, comprehensionHeatmap và resolvedClusters phục vụ hiển thị lên Dashboard và xuất file PDF.",
                "• Được kết xuất bởi SessionSummaryService và lưu trữ xuống PostgreSQL.",
            ],
        ],
    },
}


def build_part4_software_structures_and_module_views() -> list[str]:
    elems = []
    elems.append(make_page_break())
    elems.append(
        make_h1("PHẦN 4. LỰA CHỌN SOFTWARE STRUCTURES ĐỂ THỂ HIỆN MODULE VIEW & ĐẶC TẢ CHI TIẾT CÁC THÀNH PHẦN")
    )

    elems.append(make_h2("4.1. Cơ sở lựa chọn Software Structures cho Module View từ các Kịch bản QA"))
    elems.append(
        make_body_p(
            "Theo phương pháp luận thiết kế kiến trúc phần mềm (Software Architecture in Practice — Bass, Clements, Kazman kết hợp mô hình C4 của Simon Brown), từ 12 kịch bản thuộc tính chất lượng đã phân tích ở Phần 3, Nhóm 6 lựa chọn 03 cấu trúc phần mềm (Software Structures) thuộc góc nhìn Module View để biểu diễn kiến trúc hệ thống ClassBridge từ tổng thể đến chi tiết mã nguồn:"
        )
    )

    struct_headers = [
        "Software Structure (Module View)",
        "Cấp độ Sơ đồ C4 tương ứng",
        "Kịch bản QA dẫn xuất trực tiếp",
        "Quyết định Kiến trúc & Lý do lựa chọn cấu trúc",
    ]
    struct_rows = [
        [
            "1. Decomposition Structure\n(Cấu trúc Phân rã Module & Ranh giới Hệ thống)",
            "Cấp độ 1 (Hình 1)\n& Cấp độ 2 (Hình 2)",
            "QA 1.1, QA 1.2,\nQA 2.1, QA 2.2,\nQA 3.1, QA 3.3",
            "Phân rã hệ thống thành các Container/Module độc lập: tách riêng giao diện Zero-Install (Student Mobile Web) có LocalQueue (QA 2.2), tách biệt hoàn toàn Speech Processing Worker và NLP & LLM Inference Service khỏi Backend API (Worker Isolation — QA 2.1) và dùng Task Queue trung gian (0% Queue Drop — QA 1.2).",
        ],
        [
            "2. Layered & Uses Structure\n(Cấu trúc Phân tầng & Quan hệ Phụ thuộc 'Uses')",
            "Cấp độ 3 — Component View\n(Hình 3.1, 3.2, 3.3)",
            "QA 1.1, QA 1.2,\nQA 1.3, QA 2.3,\nQA 3.1, QA 3.2,\nQA 4.2",
            "Bên trong mỗi Container lõi, các module được tổ chức theo 3 tầng nghiêm ngặt: Tầng 1 (Security / Ingestion / Preprocessor: Auth & Anonymizer, Anti-Spam Rate Limiter, VAD Audio Gate) → Tầng 2 (Core Controllers & AI Engines) → Tầng 3 (Dynamic Config, In-Memory Cache & Persistence). Đảm bảo chặn Spam ≤ 20ms (QA 3.2) và chặn ảo giác âm thanh ngay từ tầng 1 (QA 2.3).",
        ],
        [
            "3. Generalization / Strategy & Adapter Structure\n(Cấu trúc Đa hình & Giao diện Trừu tượng)",
            "Cấp độ 4 — Code View\n(Hình 4.1, 4.2, 4.3, 4.4)",
            "QA 4.1, QA 4.2,\nQA 4.3, QA 1.3,\nQA 2.1, QA 2.3",
            "Sử dụng các Interface chiến lược (ISTTEngine, ITranslator, IEmbeddingStrategy, ILLMProvider) và các lớp Adapter thực thi độc lập ở 2 bên cánh (FasterWhisperEngine, NLLBTranslatorAdapter, MultilingualE5Adapter, LaBSEAdapter, OllamaQwenAdapter, LightweightLLMAdapter) để đổi mô hình trong ≤ 30–60 phút với 0 dòng code sửa đổi ở tầng điều phối và giao diện (QA 4.1, QA 4.3).",
        ],
    ]
    elems.append(make_table(struct_headers, struct_rows, [3.6, 2.8, 2.6, 7.4]))

    # Render all 9 diagrams with their full descriptions + detailed responsibility tables
    section_titles = {
        "Hinh_1_System_Context": "4.2. Cấp độ 1 — System Context View (Hình 1): Ngữ cảnh Hệ thống & Quan hệ Tác nhân",
        "Hinh_2_Container": "4.3. Cấp độ 2 — Top-Level Module Decomposition / Container View (Hình 2)",
        "Hinh_3_1_Component_Backend": "4.4.1. Hình 3.1: Module View (Layered & Uses) — Backend API & WebSocket Server",
        "Hinh_3_2_Component_Speech_Worker": "4.4.2. Hình 3.2: Module View (Layered & Uses) — Speech Processing Worker (FR-02)",
        "Hinh_3_3_Component_NLP_LLM": "4.4.3. Hình 3.3: Module View (Layered & Uses) — NLP & LLM Inference Service (FR-03 & FR-05)",
        "Hinh_4_1_Code_Speech_Pipeline": "4.5.1. Hình 4.1: Code & Interface View — Speech Processing Module (FR-02 & QA 1.1, 2.1, 2.3)",
        "Hinh_4_2_Code_Clustering": "4.5.2. Hình 4.2: Code & Strategy View — Semantic Question Clustering Module (FR-03 & QA 1.2, 4.1, 4.2)",
        "Hinh_4_3_Code_Security_Broadcast": "4.5.3. Hình 4.3: Code View — Security & 1-to-Many Broadcast Module (FR-01, FR-04 & QA 1.3, 3.1, 3.2, 3.3)",
        "Hinh_4_4_Code_Summary_Heatmap": "4.5.4. Hình 4.4: Code & Unified LLM View — Session Summary & Heatmap Module (FR-05 & QA 4.3)",
    }

    for idx, diag in enumerate(DIAGRAMS, start=1):
        did = diag["id"]
        elems.append(make_page_break())

        if did == "Hinh_3_1_Component_Backend":
            elems.append(make_h2("4.4. Cấp độ 3 — Layered Component & Uses View cho 3 Phân hệ Lõi (Hình 3.1, 3.2, 3.3)"))
        elif did == "Hinh_4_1_Code_Speech_Pipeline":
            elems.append(make_h2("4.5. Cấp độ 4 — Code / Generalization & Strategy Interface View (Hình 4.1, 4.2, 4.3, 4.4)"))

        sec_heading = section_titles.get(did, diag["figure_title"])
        if did in ("Hinh_1_System_Context", "Hinh_2_Container"):
            elems.append(make_h2(sec_heading))
        else:
            elems.append(make_h3(sec_heading))

        spec_info = MODULE_SPECS_BY_DIAGRAM[did]
        elems.append(make_body_p(spec_info["intro"]))

        # Embedded High-Res C4 Diagram Image
        cw = diag.get("canvas_w", 1600)
        ch = diag.get("canvas_h", 1080)
        img_w_cm = 16.4
        img_h_cm = round(img_w_cm * (ch / float(cw)), 2)
        r_id = f"rIdImg{idx}"
        elems.append(make_image_drawing_p(r_id, 300 + idx, diag["filename"], img_w_cm, img_h_cm))
        elems.append(make_caption_p(diag["figure_title"]))

        # Detailed Table of Functions, Roles, Responsibilities, and Relationships
        elems.append(
            make_h3(
                f"Bảng đặc tả Chức năng chính, Vai trò, Trách nhiệm & Mối quan hệ của các Thành phần trong {diag['figure_title'].split('—')[0].strip()}"
            )
        )
        elems.append(make_table(spec_info["headers"], spec_info["rows"], [3.3, 2.5, 5.6, 5.0]))

        # Narrative bullets from original specification
        elems.append(make_h3(f"Tổng hợp luồng hoạt động và cơ chế đáp ứng QA của {diag['figure_title'].split('—')[0].strip()}"))
        for bold_pref, desc_txt in diag["descriptions"]:
            elems.append(make_bullet_p(desc_txt, bold_prefix=bold_pref))

    return elems


def build_part5_traceability_and_conclusion() -> list[str]:
    elems = []
    elems.append(make_page_break())
    elems.append(
        make_h1("PHẦN 5. MA TRẬN TRUY VẾT TOÀN DIỆN (QA SCENARIOS → SOFTWARE STRUCTURES → MODULES) & KẾT LUẬN")
    )
    elems.append(
        make_body_p(
            "Bảng ma trận dưới đây tổng hợp toàn bộ chuỗi truy vết khép kín từ 12 Kịch bản Thuộc tính Chất lượng (QA Scenarios) sang các Chiến thuật Kiến trúc (Architectural Tactics), Cấu trúc Phần mềm (Software Structures - Module View) và các Module/Class chịu trách nhiệm thực thi trong hệ thống ClassBridge:"
        )
    )

    matrix_headers = [
        "Mã Kịch bản QA",
        "Yêu cầu Định lượng (Response Measure)",
        "Software Structure (Module View)",
        "Module / Component / Class chịu trách nhiệm chính",
        "Sơ đồ Minh họa",
    ]
    matrix_rows = [
        [
            "Kịch bản 1.1\n(Performance)",
            "Độ trễ phụ đề song ngữ đầu-cuối ≤ 1.5s (≥ 95% câu thoại)",
            "Decomposition & Layered Pipeline + Strategy Interface",
            "Speech Processing Worker, Audio Stream Consumer, STT Inference Engine (FasterWhisperEngine), Bilingual Translator (NLLBTranslatorAdapter), SubtitlePayloadDTO",
            "Hình 2,\nHình 3.2,\nHình 4.1",
        ],
        [
            "Kịch bản 1.2\n(Performance)",
            "Phân cụm 40 câu hỏi đồng thời ≤ 500ms/câu, 0% Queue Drop",
            "Async Queue Decomposition + In-Memory Centroid Cache",
            "Task Queue & Cache, Semantic Clustering Engine (OnlineClusteringEngine), Cluster Centroid Cache, QuestionCluster",
            "Hình 2,\nHình 3.3,\nHình 4.2",
        ],
        [
            "Kịch bản 1.3\n(Performance)",
            "Broadcast câu trả lời 1-nhiều ≤ 400ms tới 100% SV trong cụm",
            "Uses & Event-Driven Room Multicast Structure",
            "Session & QnA Controller (QnAController), WebSocket Broadcast Engine (WebSocketBroadcastManager), Cluster Subscription Registry",
            "Hình 3.1,\nHình 4.3",
        ],
        [
            "Kịch bản 2.1\n(Availability)",
            "Q&A Zero Downtime khi STT lỗi OOM; STT tự hồi phục ≤ 5s",
            "Process / Worker Isolation & Supervisor Structure",
            "Speech Processing Worker (Isolated Container), Worker Health & Memory Guard (WorkerMemoryGuard.recoverOnOOM)",
            "Hình 2,\nHình 3.2,\nHình 4.1",
        ],
        [
            "Kịch bản 2.2\n(Availability)",
            "0% mất câu hỏi khi rớt Wi-Fi 10s; tự đồng bộ lại ≤ 2s",
            "Client-Server Decoupled State & Local Queue",
            "Student Mobile Web (Local Storage Queue & Auto-reconnect WebSocket Client), WebSocket Broadcast Engine",
            "Hình 2,\nHình 3.1",
        ],
        [
            "Kịch bản 2.3\n(Availability)",
            "0 dòng phụ đề ảo giác khi giảng viên im lặng; tiết kiệm ≥ 80% GPU",
            "Layered Filter Gate (Early Return Pattern)",
            "VAD Audio Gate (class SileroVADGate.isHumanSpeech), SpeechPipelineWorker",
            "Hình 3.2,\nHình 4.1",
        ],
        [
            "Kịch bản 3.1\n(Security & Privacy)",
            "0% khả năng truy vết ngược danh tính thật của sinh viên",
            "Layered Security Middleware & Anonymized Persistence",
            "Auth & Anonymizer (SessionAuthMiddleware.generateAnonHash), QuestionEntity (chỉ lưu anonymousHashId), Primary Database",
            "Hình 2,\nHình 3.1,\nHình 4.2, 4.3",
        ],
        [
            "Kịch bản 3.2\n(Security & Privacy)",
            "Giới hạn 3 câu/phút/phiên; chặn Spam Flooding ≤ 20ms",
            "Layered Gateway Guard (Token Bucket Pattern)",
            "Anti-Spam Rate Limiter (class AntiSpamRateLimiter.allowRequest)",
            "Hình 3.1,\nHình 4.3",
        ],
        [
            "Kịch bản 3.3\n(Security & Privacy)",
            "Từ chối 100% kết nối không có PIN 6 số động / QR hợp lệ",
            "Context Physical Display + Session Auth Guard",
            "Classroom Projector (hiển thị PIN tại phòng), Auth & Anonymizer (SessionAuthMiddleware.verifyPinOrQR)",
            "Hình 1,\nHình 3.1,\nHình 4.3",
        ],
        [
            "Kịch bản 4.1\n(Modifiability)",
            "Đổi mô hình Embedding (LaBSE ↔ e5-base) ≤ 1h, 0 sửa code UI/DB",
            "Generalization / Strategy & Adapter Structure",
            "Embedding Model Adapter (<<interface>> IEmbeddingStrategy, MultilingualE5Adapter, LaBSEAdapter)",
            "Hình 3.3,\nHình 4.2",
        ],
        [
            "Kịch bản 4.2\n(Modifiability)",
            "Đổi nóng ngưỡng Cosine (0.65 → 0.75) giữa ca học ≤ 5 phút",
            "Externalized Runtime Configuration Structure",
            "Dynamic Config Manager (class DynamicConfigManager.setThreshold), OnlineClusteringEngine",
            "Hình 3.1,\nHình 4.2",
        ],
        [
            "Kịch bản 4.3\n(Modifiability)",
            "Đổi mô hình LLM tóm tắt cuối buổi ≤ 30 phút cấu hình khi thiếu VRAM",
            "Unified Interface & Pluggable Adapter Structure",
            "Unified LLM Summarizer (<<interface>> ILLMProvider, OllamaQwenAdapter, LightweightLLMAdapter), SessionSummaryService",
            "Hình 3.3,\nHình 4.4",
        ],
    ]
    elems.append(make_table(matrix_headers, matrix_rows, [2.4, 3.5, 3.2, 5.3, 2.0]))

    elems.append(make_h2("Kết luận chung của Nhóm 6"))
    elems.append(
        make_body_p(
            "Thông qua tài liệu này, Nhóm 6 (Mã nhóm C1SE.38) đã hoàn thành việc chi tiết hóa toàn bộ các Architectural Drivers của hệ thống ClassBridge thành 04 nhóm Thuộc tính Chất lượng (Performance, Availability & Fault Tolerance, Security & Privacy, Modifiability) với 12 kịch bản định lượng cụ thể. Từ các kịch bản đó, nhóm đã lựa chọn và thiết kế hệ thống Software Structures theo 4 cấp độ C4 Model (9 sơ đồ trực quan từ System Context, Container, Component đến Code/Interface View), đồng thời đặc tả đầy đủ chức năng chính, vai trò, trách nhiệm và mối quan hệ phụ thuộc/tương tác của từng thành phần, sẵn sàng cho giai đoạn hiện thực hóa và triển khai thực nghiệm (Pilot Deployment)."
        )
    )
    return elems


def main():
    all_elems = []
    all_elems.extend(build_nhom6_cover_page())
    all_elems.extend(build_nhom6_toc())
    all_elems.extend(build_part1_team_and_contribution())
    all_elems.extend(build_part2_architectural_drivers_summary())
    all_elems.extend(build_part3_qas_and_scenarios())
    all_elems.extend(build_part4_software_structures_and_module_views())
    all_elems.extend(build_part5_traceability_and_conclusion())

    body_xml = "".join(all_elems)
    header_text = "NHÓM 6 (C1SE.38) — Phân Tích QAs, Kịch Bản & Thiết Kế Software Structures (Module View) | ClassBridge"

    out_paths = [
        os.path.join(OUT_DIR, "NHOM6.docx"),
        os.path.join(ROOT_DIR, "NHOM6.docx"),
    ]
    for p in out_paths:
        write_docx_with_images(p, body_xml, header_text)


if __name__ == "__main__":
    main()
