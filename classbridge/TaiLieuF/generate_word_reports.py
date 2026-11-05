# -*- coding: utf-8 -*-
"""
Trình tạo Báo cáo Microsoft Word (.docx) chuẩn OpenXML (không phụ thuộc thư viện ngoài):
- Nhúng trực tiếp 9 hình ảnh sơ đồ kiến trúc C4 Model (chuẩn c4model.com, độ phân giải cao 2400px)
- Căn chỉnh trang A4, Header/Footer, đánh số trang tự động, Bìa báo cáo chuẩn ĐH Duy Tân (DTU)
- Xuất ra 3 file Word hoàn chỉnh trong thư mục TaiLieuF:
  1. ClassBridge_BaoCao_KienTruc_C4_Model_C1SE38.docx (Báo cáo chuyên sâu Thiết kế Kiến trúc C4 Model - 9 Hình)
  2. ClassBridge_BaoCao_TongHop_Drivers_Va_C4_Model_C1SE38.docx (Báo cáo Tổng hợp Drivers + 12 Kịch bản QA + 9 Hình C4)
  3. tailieu.docx (Cập nhật trực tiếp thành file Word hoàn chỉnh chứa đầy đủ 9 hình C4 và mô tả chi tiết)
"""

import os
import shutil
import zipfile
import html
import re
from diagram_definitions import DIAGRAMS

TEMPLATE_DOCX = r"d:\TailieuNPKH\classbridge\ClassBridge_Architectural_Drivers_C1SE38.docx"
PNG_DIR = r"d:\TailieuNPKH\classbridge\TaiLieuF\02_HinhAnh_SoDo_PNG"
OUT_DIR = r"d:\TailieuNPKH\classbridge\TaiLieuF"


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def make_run(text: str, size_pt: float = 12.0, bold: bool = False, italic: bool = False, color: str = "1E293B") -> str:
    sz_half = int(round(size_pt * 2))
    b_xml = "<w:b/><w:bCs/>" if bold else ""
    i_xml = "<w:i/><w:iCs/>" if italic else ""
    parts = str(text).split("\n")
    t_elems = []
    for idx, part in enumerate(parts):
        if idx > 0:
            t_elems.append("<w:br/>")
        space_attr = ' xml:space="preserve"' if (part.startswith(" ") or part.endswith(" ")) else ""
        t_elems.append(f"<w:t{space_attr}>{esc(part)}</w:t>")
    inner = "".join(t_elems)
    return (
        f"<w:r>"
        f"<w:rPr>"
        f'<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>'
        f"{b_xml}{i_xml}"
        f'<w:color w:val="{color}"/>'
        f'<w:sz w:val="{sz_half}"/><w:szCs w:val="{sz_half}"/>'
        f"</w:rPr>"
        f"{inner}"
        f"</w:r>"
    )


def make_p(
    runs_xml: str,
    align: str = "both",
    space_before_pt: float = 0,
    space_after_pt: float = 4.5,
    line_spacing: float = 1.25,
    keep_next: bool = False,
    left_indent_cm: float = 0.0,
    bullet: bool = False,
) -> str:
    sb = int(round(space_before_pt * 20))
    sa = int(round(space_after_pt * 20))
    ls = int(round(line_spacing * 240))
    kn = "<w:keepNext/>" if keep_next else ""
    pstyle = '<w:pStyle w:val="ListBullet"/>' if bullet else ""
    ind = f'<w:ind w:left="{int(round(left_indent_cm * 567))}"/>' if left_indent_cm > 0 else ""
    return (
        f"<w:p>"
        f"<w:pPr>"
        f"{pstyle}{kn}"
        f'<w:spacing w:before="{sb}" w:after="{sa}" w:line="{ls}" w:lineRule="auto"/>'
        f"{ind}"
        f'<w:jc w:val="{align}"/>'
        f"</w:pPr>"
        f"{runs_xml}"
        f"</w:p>"
    )


def make_page_break() -> str:
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def make_h1(text: str) -> str:
    return make_p(
        make_run(text, size_pt=15.0, bold=True, color="1E3A8A"),
        align="left",
        space_before_pt=14,
        space_after_pt=8,
        keep_next=True,
    )


def make_h2(text: str) -> str:
    return make_p(
        make_run(text, size_pt=13.5, bold=True, color="2563EB"),
        align="left",
        space_before_pt=11,
        space_after_pt=5,
        keep_next=True,
    )


def make_h3(text: str) -> str:
    return make_p(
        make_run(text, size_pt=12.0, bold=True, color="0F172A"),
        align="left",
        space_before_pt=8,
        space_after_pt=4,
        keep_next=True,
    )


def make_body_p(text: str, bold_prefix: str = "") -> str:
    runs = ""
    if bold_prefix:
        runs += make_run(bold_prefix, size_pt=12.0, bold=True, color="0F172A")
    runs += make_run(text, size_pt=12.0, bold=False, color="1E293B")
    return make_p(runs, align="both", space_before_pt=0, space_after_pt=4.5, line_spacing=1.25)


def make_bullet_p(text: str, bold_prefix: str = "") -> str:
    runs = ""
    if bold_prefix:
        runs += make_run(bold_prefix, size_pt=12.0, bold=True, color="0F172A")
    runs += make_run(text, size_pt=12.0, bold=False, color="1E293B")
    return make_p(runs, align="both", space_before_pt=0, space_after_pt=4.0, line_spacing=1.25, bullet=True)


def make_image_drawing_p(r_id: str, doc_pr_id: int, name: str, width_cm: float, height_cm: float) -> str:
    cx = int(round(width_cm * 360000))
    cy = int(round(height_cm * 360000))
    return (
        '<w:p>'
        '<w:pPr><w:keepNext/><w:spacing w:before="80" w:after="60"/><w:jc w:val="center"/></w:pPr>'
        '<w:r>'
        '<w:drawing>'
        '<wp:inline distT="0" distB="0" distL="0" distR="0" '
        'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">'
        f'<wp:extent cx="{cx}" cy="{cy}"/>'
        '<wp:effectExtent l="0" t="0" r="0" b="0"/>'
        f'<wp:docPr id="{doc_pr_id}" name="{esc(name)}"/>'
        '<wp:cNvGraphicFramePr>'
        '<a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/>'
        '</wp:cNvGraphicFramePr>'
        '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:nvPicPr>'
        f'<pic:cNvPr id="{doc_pr_id}" name="{esc(name)}"/>'
        '<pic:cNvPicPr/>'
        '</pic:nvPicPr>'
        '<pic:blipFill>'
        f'<a:blip r:embed="{r_id}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/>'
        '<a:stretch><a:fillRect/></a:stretch>'
        '</pic:blipFill>'
        '<pic:spPr>'
        '<a:xfrm>'
        '<a:off x="0" y="0"/>'
        f'<a:ext cx="{cx}" cy="{cy}"/>'
        '</a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        '<a:ln w="9525"><a:solidFill><a:srgbClr val="CBD5E1"/></a:solidFill></a:ln>'
        '</pic:spPr>'
        '</pic:pic>'
        '</a:graphicData>'
        '</a:graphic>'
        '</wp:inline>'
        '</w:drawing>'
        '</w:r>'
        '</w:p>'
    )


def make_caption_p(caption_text: str) -> str:
    return make_p(
        make_run(caption_text, size_pt=11.0, bold=True, italic=True, color="1E3A8A"),
        align="center",
        space_before_pt=2,
        space_after_pt=10,
    )


def make_table(headers: list[str], rows: list[list[str]], col_widths_cm: list[float], border_color: str = "CBD5E1") -> str:
    dxa_widths = [int(round(w * 567)) for w in col_widths_cm]
    grid_cols = "".join(f'<w:gridCol w:w="{w}"/>' for w in dxa_widths)

    borders_xml = (
        f'<w:tblBorders>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="{border_color}"/>'
        f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="{border_color}"/>'
        f'<w:left w:val="single" w:sz="4" w:space="0" w:color="{border_color}"/>'
        f'<w:right w:val="single" w:sz="4" w:space="0" w:color="{border_color}"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{border_color}"/>'
        f'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="{border_color}"/>'
        f'</w:tblBorders>'
    )

    tr_list = []
    # Header row
    if headers:
        h_cells = []
        for ci, h_text in enumerate(headers):
            w_dxa = dxa_widths[ci]
            p_xml = make_p(
                make_run(h_text, size_pt=11.0, bold=True, color="FFFFFF"),
                align="center",
                space_before_pt=2,
                space_after_pt=2,
                line_spacing=1.15,
            )
            h_cells.append(
                f"<w:tc>"
                f"<w:tcPr>"
                f'<w:tcW w:w="{w_dxa}" w:type="dxa"/>'
                f'<w:shd w:val="clear" w:color="auto" w:fill="1E3A8A"/>'
                f'<w:tcMar><w:top w:w="130" w:type="dxa"/><w:bottom w:w="130" w:type="dxa"/>'
                f'<w:left w:w="150" w:type="dxa"/><w:right w:w="150" w:type="dxa"/></w:tcMar>'
                f'<w:vAlign w:val="center"/>'
                f"</w:tcPr>"
                f"{p_xml}"
                f"</w:tc>"
            )
        tr_list.append(
            f"<w:tr><w:trPr><w:cantSplit/><w:tblHeader/></w:trPr>{''.join(h_cells)}</w:tr>"
        )

    # Body rows
    for ri, r_data in enumerate(rows):
        bg = "F8FAFC" if ri % 2 == 1 else "FFFFFF"
        b_cells = []
        for ci, val in enumerate(r_data):
            w_dxa = dxa_widths[ci]
            is_bold = (ci == 0)
            col_txt = "1E3A8A" if ci == 0 else "1E293B"
            align_c = "center" if (len(val) <= 10 and ci in (0, len(r_data) - 1)) else "left"
            p_xml = make_p(
                make_run(val, size_pt=11.0, bold=is_bold, color=col_txt),
                align=align_c,
                space_before_pt=1.5,
                space_after_pt=1.5,
                line_spacing=1.2,
            )
            b_cells.append(
                f"<w:tc>"
                f"<w:tcPr>"
                f'<w:tcW w:w="{w_dxa}" w:type="dxa"/>'
                f'<w:shd w:val="clear" w:color="auto" w:fill="{bg}"/>'
                f'<w:tcMar><w:top w:w="100" w:type="dxa"/><w:bottom w:w="100" w:type="dxa"/>'
                f'<w:left w:w="140" w:type="dxa"/><w:right w:w="140" w:type="dxa"/></w:tcMar>'
                f'<w:vAlign w:val="center"/>'
                f"</w:tcPr>"
                f"{p_xml}"
                f"</w:tc>"
            )
        tr_list.append(f"<w:tr><w:trPr><w:cantSplit/></w:trPr>{''.join(b_cells)}</w:tr>")

    return (
        f"<w:tbl>"
        f"<w:tblPr>"
        f'<w:tblW w:w="0" w:type="auto"/>'
        f'<w:jc w:val="center"/>'
        f"{borders_xml}"
        f"</w:tblPr>"
        f"<w:tblGrid>{grid_cols}</w:tblGrid>"
        f"{''.join(tr_list)}"
        f"</w:tbl>"
        + make_p("", space_before_pt=2, space_after_pt=6)
    )


def build_cover_page(main_title: str, sub_doc_type: str) -> list[str]:
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
            space_before_pt=10,
            space_after_pt=42,
            line_spacing=1.3,
        )
    )
    elems.append(
        make_p(
            make_run("★ ★ ★", size_pt=12.0, bold=True, color="94A3B8"),
            align="center",
            space_after_pt=36,
        )
    )
    elems.append(
        make_p(
            make_run(main_title, size_pt=21.0, bold=True, color="1E3A8A"),
            align="center",
            space_after_pt=14,
            line_spacing=1.25,
        )
    )
    elems.append(
        make_p(
            make_run(sub_doc_type, size_pt=13.5, bold=True, italic=True, color="2563EB"),
            align="center",
            space_after_pt=22,
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
            space_after_pt=45,
            line_spacing=1.3,
        )
    )

    info_rows = [
        ["Mã nhóm thực hiện:", "C1SE.38"],
        ["Chương trình đào tạo:", "Kỹ thuật Phần mềm (CMU-SE 450/451) — Capstone Project"],
        ["Thành viên thực hiện:", "Nguyễn Sỹ Tân (Lead), Võ Trương Khải Hoàn, Phan Quang Tuấn, Trần Thị Thu Hồng, Nguyễn Thành Nhân"],
        ["Phương pháp Kiến trúc:", "C4 Model (Context, Containers, Components, Code) & Architectural Drivers (QAs)"],
        ["Đơn vị đào tạo:", "Đại học Duy Tân (DTU) — Đà Nẵng, Năm 2026"],
    ]
    elems.append(make_table([], info_rows, [5.5, 10.8], border_color="E2E8F0"))

    elems.append(
        make_p(
            make_run("ĐÀ NẴNG, NĂM 2026", size_pt=11.5, bold=True, color="64748B"),
            align="center",
            space_before_pt=55,
            space_after_pt=10,
        )
    )
    elems.append(make_page_break())
    return elems


def build_c4_sections(include_part_prefix: bool = False) -> list[str]:
    """Xây dựng toàn bộ 4 cấp độ C4 (9 hình + mô tả chi tiết + bảng đối chiếu)."""
    elems = []

    if include_part_prefix:
        elems.append(make_h1("PHẦN 5. THIẾT KẾ KIẾN TRÚC HỆ THỐNG THEO MÔ HÌNH C4 (C4 MODEL ARCHITECTURE)"))
        elems.append(
            make_body_p(
                "Dựa trên các Architectural Drivers, Yêu cầu Chức năng Cốt lõi (FR-01 đến FR-05) và 12 kịch bản Thuộc tính Chất lượng (QA Scenarios) đã xác lập, nhóm C1SE.38 thiết kế kiến trúc hệ thống ClassBridge theo chuẩn mô hình C4 (Simon Brown) xuyên suốt 4 cấp độ từ tổng quan đến chi tiết mã nguồn: Cấp độ 1 (System Context — 1 hình), Cấp độ 2 (Container — 1 hình), Cấp độ 3 (Component — 3 hình cho 3 Container lõi) và Cấp độ 4 (Code — 4 hình cho 4 luồng xử lý lõi)."
            )
        )

    # Track level headers so we only emit each CẤP ĐỘ header once
    seen_levels = set()

    for idx, diag in enumerate(DIAGRAMS, start=1):
        lvl = diag["level_title"]
        if lvl not in seen_levels:
            if idx > 1:
                elems.append(make_page_break())
            elems.append(make_h1(lvl))
            seen_levels.add(lvl)
        else:
            elems.append(make_page_break())

        # Figure heading
        elems.append(make_h2(diag["figure_title"]))
        elems.append(
            make_body_p(
                f"({diag['layout_note']})",
                bold_prefix="Bố cục kiến trúc chuẩn C4: ",
            )
        )

        # Embedded High-Res PNG Diagram
        cw = diag.get("canvas_w", 1600)
        ch = diag.get("canvas_h", 1080)
        img_w_cm = 16.4
        img_h_cm = round(img_w_cm * (ch / float(cw)), 2)
        r_id = f"rIdImg{idx}"
        elems.append(make_image_drawing_p(r_id, 100 + idx, diag["filename"], img_w_cm, img_h_cm))
        elems.append(make_caption_p(diag["figure_title"]))

        # Detailed description section
        elems.append(make_h3(f"Mô tả chi tiết {diag['figure_title'].split('—')[0].strip()}"))
        for bold_pref, desc_txt in diag["descriptions"]:
            elems.append(make_bullet_p(desc_txt, bold_prefix=bold_pref))

    # Add Traceability Summary Table at the end of C4 section
    elems.append(make_page_break())
    elems.append(make_h1("TỔNG HỢP ĐỐI CHIẾU KIẾN TRÚC C4 VỚI YÊU CẦU CHỨC NĂNG & KỊCH BẢN CHẤT LƯỢNG"))
    elems.append(
        make_body_p(
            "Bảng dưới đây tổng hợp sự ánh xạ trực tiếp giữa 9 sơ đồ kiến trúc C4 (Cấp độ 1 → Cấp độ 4) với các Yêu cầu Chức năng Cốt lõi (Primary FRs) và 12 Kịch bản Thuộc tính Chất lượng (Quality Attribute Scenarios) của hệ thống ClassBridge:"
        )
    )

    trace_headers = ["Sơ đồ C4", "Cấp độ C4", "Thành phần / Lớp Trọng tâm", "Ánh xạ FR & Kịch bản QA"]
    trace_rows = [
        [
            "Hình 1",
            "Level 1: System Context",
            "ClassBridge System, Student, Lecturer, Admin, Classroom Mic & Projector",
            "Toàn bộ FR-01 → FR-05; Kịch bản QA 3.3 (Mã PIN 6 số động trên máy chiếu tại lớp)"
        ],
        [
            "Hình 2",
            "Level 2: Container Diagram",
            "Student Mobile Web, Lecturer Dashboard, Backend FastAPI, STT Worker, NLP Service, Redis Queue, PostgreSQL",
            "FR-01 → FR-05; QA 1.1, QA 1.2 (0% Queue Drop), QA 1.3 (≤ 400ms), QA 2.1 (Worker Isolation), QA 2.2 (LocalQueue ≤ 2s), QA 3.1"
        ],
        [
            "Hình 3.1",
            "Level 3: Component (Backend)",
            "Auth & Anonymizer, Anti-Spam Rate Limiter, Session & QnA Controller, WS Broadcast Engine, Dynamic Config Mgr",
            "FR-01, FR-04; QA 1.3 (Broadcast ≤ 400ms), QA 3.1 (Anonymous_Hash_ID), QA 3.2 (Rate Limit ≤ 20ms), QA 3.3, QA 4.2 (Đổi ngưỡng ≤ 5p)"
        ],
        [
            "Hình 3.2",
            "Level 3: Component (Speech Worker)",
            "Audio Stream Consumer, VAD Audio Gate (Silero VAD), STT Inference (Faster-Whisper), Bilingual Translator, Memory Guard",
            "FR-02; QA 1.1 (Độ trễ phụ đề ≤ 1.5s), QA 2.1 (Tự phục hồi OOM ≤ 5s), QA 2.3 (Chặn 100% ảo giác, tiết kiệm ≥ 80% GPU)"
        ],
        [
            "Hình 3.3",
            "Level 3: Component (NLP & LLM)",
            "Multilingual Normalizer, Embedding Adapter, Semantic Clustering Engine, Unified LLM Summarizer, Centroid Cache",
            "FR-03, FR-05; QA 1.2 (Gom cụm Cosine ≤ 500ms), QA 4.1 (Strategy Pattern e5-base/LaBSE ≤ 1h), QA 4.3 (Unified LLM ≤ 30p)"
        ],
        [
            "Hình 4.1",
            "Level 4: Code (Speech Pipeline)",
            "SpeechPipelineWorker, SileroVADGate, WorkerMemoryGuard, ISTTEngine, ITranslator, SubtitlePayloadDTO",
            "FR-02; QA 1.1 (≤ 1.5s), QA 2.1 (recoverOnOOM ≤ 5s), QA 2.3 (isHumanSpeech Early Return)"
        ],
        [
            "Hình 4.2",
            "Level 4: Code (Clustering)",
            "OnlineClusteringEngine, IEmbeddingStrategy, MultilingualE5Adapter, LaBSEAdapter, DynamicConfigManager",
            "FR-03; QA 1.2 (assignOrCreateCluster ≤ 500ms), QA 4.1 (Đổi mô hình Benchmark ≤ 1h), QA 4.2 (setThreshold ≤ 5p)"
        ],
        [
            "Hình 4.3",
            "Level 4: Code (Security & Broadcast)",
            "SessionAuthMiddleware, AntiSpamRateLimiter, QnAController, WebSocketBroadcastManager, Cluster Subscription Registry",
            "FR-01, FR-04; QA 1.3 (broadcastToCluster ≤ 400ms), QA 3.1 (0% truy vết danh tính), QA 3.2 (Chặn spam ≤ 20ms), QA 3.3"
        ],
        [
            "Hình 4.4",
            "Level 4: Code (Summary & Heatmap)",
            "SessionSummaryService, HeatmapCalculator, ILLMProvider, OllamaQwenAdapter, LightweightLLMAdapter, SessionReportDTO",
            "FR-05; QA 4.3 (Chuyển đổi mô hình tóm tắt cục bộ ≤ 30 phút cấu hình khi thiếu VRAM)"
        ],
    ]
    elems.append(make_table(trace_headers, trace_rows, [2.2, 3.3, 5.5, 5.4]))
    return elems


def build_c4_toc() -> list[str]:
    elems = []
    elems.append(
        make_p(
            make_run("MỤC LỤC BÁO CÁO THIẾT KẾ KIẾN TRÚC C4 MODEL", size_pt=16.0, bold=True, color="1E3A8A"),
            align="left",
            space_after_pt=12,
        )
    )
    toc_entries = [
        ("CẤP ĐỘ 1: SYSTEM CONTEXT DIAGRAM (1 HÌNH)", 0, True),
        ("Hình 1: System Context Diagram — Ngữ cảnh Hệ thống ClassBridge", 1, False),
        ("Mô tả chi tiết Hình 1 (System Context Diagram)", 2, False),
        ("CẤP ĐỘ 2: CONTAINER DIAGRAM (1 HÌNH)", 0, True),
        ("Hình 2: Container Diagram — Sơ đồ Kiến trúc Container", 1, False),
        ("Mô tả chi tiết Hình 2 (Container Diagram)", 2, False),
        ("CẤP ĐỘ 3: COMPONENT DIAGRAM (3 HÌNH RIÊNG BIỆT CHO 3 CONTAINER LÕI)", 0, True),
        ("Hình 3.1: Component Diagram — Backend API & WebSocket Server", 1, False),
        ("Hình 3.2: Component Diagram — Speech Processing Worker (Tính năng lõi FR-02)", 1, False),
        ("Hình 3.3: Component Diagram — NLP & LLM Inference Service (Tính năng lõi FR-03 & FR-05)", 1, False),
        ("CẤP ĐỘ 4: CODE DIAGRAM (4 HÌNH CHO 4 LUỒNG XỬ LÝ LÕI)", 0, True),
        ("Hình 4.1: Code Diagram — Luồng Phụ đề Song ngữ & VAD Gate Chống ảo giác (FR-02)", 1, False),
        ("Hình 4.2: Code Diagram — Luồng Gom nhóm Câu hỏi Ngữ nghĩa Đa ngôn ngữ (FR-03 & QA 4)", 1, False),
        ("Hình 4.3: Code Diagram — Luồng Bảo mật Ẩn danh, Chống Spam & Phản hồi 1-nhiều (FR-01, FR-04 & QA 3)", 1, False),
        ("Hình 4.4: Code Diagram — Luồng Tổng hợp Báo cáo & Heatmap Cuối buổi (FR-05 & QA 4.3)", 1, False),
        ("TỔNG HỢP ĐỐI CHIẾU KIẾN TRÚC C4 VỚI YÊU CẦU CHỨC NĂNG & KỊCH BẢN CHẤT LƯỢNG", 0, True),
    ]
    for title, lvl, is_b in toc_entries:
        elems.append(
            make_p(
                make_run(title, size_pt=11.5, bold=is_b, color="1E3A8A" if is_b else "334155"),
                align="left",
                space_before_pt=2 if is_b else 0,
                space_after_pt=3,
                line_spacing=1.18,
                left_indent_cm=0.6 * lvl,
            )
        )
    elems.append(make_page_break())
    return elems


def write_docx_with_images(output_docx_path: str, body_inner_xml: str, header_title: str):
    os.makedirs(os.path.dirname(output_docx_path), exist_ok=True)
    with zipfile.ZipFile(TEMPLATE_DOCX, "r") as zin:
        orig_doc_xml = zin.read("word/document.xml").decode("utf-8")
        orig_rels_xml = zin.read("word/_rels/document.xml.rels").decode("utf-8")
        orig_ct_xml = zin.read("[Content_Types].xml").decode("utf-8")
        orig_hdr_xml = zin.read("word/header1.xml").decode("utf-8")

        # Extract <w:document ...><w:body> prefix and <w:sectPr>...</w:sectPr></w:body></w:document> suffix
        body_start_idx = orig_doc_xml.find("<w:body>") + len("<w:body>")
        sect_start_idx = orig_doc_xml.rfind("<w:sectPr")
        doc_prefix = orig_doc_xml[:body_start_idx]
        doc_suffix = orig_doc_xml[sect_start_idx:]

        new_doc_xml = doc_prefix + body_inner_xml + doc_suffix

        # Add PNG Default ContentType if not present
        if 'Extension="png"' not in orig_ct_xml:
            new_ct_xml = orig_ct_xml.replace(
                "<Types ",
                '<Types ',
            ).replace(
                '<Default Extension="jpeg" ContentType="image/jpeg"/>',
                '<Default Extension="jpeg" ContentType="image/jpeg"/><Default Extension="png" ContentType="image/png"/>',
            )
        else:
            new_ct_xml = orig_ct_xml

        # Add 9 image relationships rIdImg1 .. rIdImg9
        img_rels = []
        for idx, diag in enumerate(DIAGRAMS, start=1):
            img_rels.append(
                f'<Relationship Id="rIdImg{idx}" '
                f'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
                f'Target="media/{diag["filename"]}.png"/>'
            )
        new_rels_xml = orig_rels_xml.replace("</Relationships>", "".join(img_rels) + "</Relationships>")

        # Update header text
        new_hdr_xml = orig_hdr_xml.replace(
            "ClassBridge — Báo Cáo Kiến Trúc (Architectural Drivers) | Nhóm C1SE.38",
            esc(header_title),
        )

        with zipfile.ZipFile(output_docx_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "word/document.xml":
                    zout.writestr(item, new_doc_xml.encode("utf-8"))
                elif item.filename == "word/_rels/document.xml.rels":
                    zout.writestr(item, new_rels_xml.encode("utf-8"))
                elif item.filename == "[Content_Types].xml":
                    zout.writestr(item, new_ct_xml.encode("utf-8"))
                elif item.filename == "word/header1.xml":
                    zout.writestr(item, new_hdr_xml.encode("utf-8"))
                else:
                    zout.writestr(item, data)

            # Embed all 9 high-res PNG files into word/media/
            for diag in DIAGRAMS:
                png_path = os.path.join(PNG_DIR, f'{diag["filename"]}.png')
                zout.write(png_path, f'word/media/{diag["filename"]}.png')

    print(f"[SUCCESS] Generated Word report: {output_docx_path}")


def main():
    # 1. Backup original raw text in tailieu.docx if it's plain text
    raw_tailieu_path = os.path.join(OUT_DIR, "tailieu.docx")
    backup_md_path = os.path.join(OUT_DIR, "tailieu_raw_mermaid_spec.md")
    if os.path.exists(raw_tailieu_path) and not zipfile.is_zipfile(raw_tailieu_path):
        shutil.copyfile(raw_tailieu_path, backup_md_path)
        print(f"[BACKUP] Backed up raw specification to: {backup_md_path}")

    # 2. Build Dedicated C4 Model Architecture Design Word Report
    c4_doc_elems = []
    c4_doc_elems.extend(
        build_cover_page(
            "BÁO CÁO THIẾT KẾ KIẾN TRÚC HỆ THỐNG\nTHEO MÔ HÌNH C4 (C4 MODEL ARCHITECTURE)",
            "Cấp độ 1: System Context • Cấp độ 2: Container • Cấp độ 3: Component • Cấp độ 4: Code",
        )
    )
    c4_doc_elems.extend(build_c4_toc())
    c4_doc_elems.extend(build_c4_sections(include_part_prefix=False))
    c4_body_xml = "".join(c4_doc_elems)

    c4_report_path = os.path.join(OUT_DIR, "ClassBridge_BaoCao_KienTruc_C4_Model_C1SE38.docx")
    write_docx_with_images(
        c4_report_path,
        c4_body_xml,
        "ClassBridge — Báo Cáo Thiết Kế Kiến Trúc C4 Model (4 Cấp Độ - 9 Sơ Đồ) | Nhóm C1SE.38",
    )

    # Also write to tailieu.docx so opening tailieu.docx in Word opens the complete C4 report
    write_docx_with_images(
        raw_tailieu_path,
        c4_body_xml,
        "ClassBridge — Báo Cáo Thiết Kế Kiến Trúc C4 Model (4 Cấp Độ - 9 Sơ Đồ) | Nhóm C1SE.38",
    )

    # 3. Build Master Combined Report (Architectural Drivers + 12 QA Scenarios + 9 C4 Diagrams)
    with zipfile.ZipFile(TEMPLATE_DOCX, "r") as zin:
        orig_doc_xml = zin.read("word/document.xml").decode("utf-8")
        body_start_idx = orig_doc_xml.find("<w:body>") + len("<w:body>")
        sect_start_idx = orig_doc_xml.rfind("<w:sectPr")
        drivers_body_xml = orig_doc_xml[body_start_idx:sect_start_idx]

    # Update Title in Master Report and append C4 Sections before Conclusion
    drivers_body_xml = drivers_body_xml.replace(
        "BÁO CÁO XÁC ĐỊNH",
        "BÁO CÁO TỔNG HỢP THIẾT KẾ KIẾN TRÚC C4 MODEL &amp;",
    )
    c4_master_addition = make_page_break() + "".join(build_c4_sections(include_part_prefix=True))
    master_body_xml = drivers_body_xml + c4_master_addition

    master_report_path = os.path.join(OUT_DIR, "ClassBridge_BaoCao_TongHop_Drivers_Va_C4_Model_C1SE38.docx")
    write_docx_with_images(
        master_report_path,
        master_body_xml,
        "ClassBridge — Báo Cáo Tổng Hợp Architectural Drivers & Thiết Kế Kiến Trúc C4 Model | Nhóm C1SE.38",
    )


if __name__ == "__main__":
    main()
