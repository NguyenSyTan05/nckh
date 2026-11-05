import os
import docx
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def set_table_borders(table, color="D3D3D3", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:right w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def set_row_cant_split(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

def set_row_header(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

def add_page_number_to_run(run):
    fldSimple = parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls('w'))
    run._r.append(fldSimple)

def add_total_pages_to_run(run):
    fldSimple = parse_xml(r'<w:fldSimple %s w:instr="NUMPAGES"/>' % nsdecls('w'))
    run._r.append(fldSimple)

def build_document():
    doc = docx.Document()

    # Page setup - A4
    for section in doc.sections:
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)
        section.top_margin = Cm(2.2)
        section.bottom_margin = Cm(2.2)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.0)
        section.different_first_page_header_footer = True

        # Header for normal pages
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("ClassBridge — Báo Cáo Kiến Trúc (Architectural Drivers) | Nhóm C1SE.38")
        hrun.font.name = "Times New Roman"
        hrun.font.size = Pt(8.5)
        hrun.font.italic = True
        hrun.font.color.rgb = RGBColor(100, 116, 139)

        # Footer for normal pages
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.text = ""
        frun1 = fp.add_run("Đại học Duy Tân (DTU) — Khoa Công nghệ Thông tin\tTrang ")
        frun1.font.name = "Times New Roman"
        frun1.font.size = Pt(9)
        frun1.font.color.rgb = RGBColor(100, 116, 139)
        
        frun_page = fp.add_run()
        add_page_number_to_run(frun_page)
        frun_page.font.name = "Times New Roman"
        frun_page.font.size = Pt(9)
        frun_page.font.bold = True
        frun_page.font.color.rgb = RGBColor(30, 58, 138)

        frun2 = fp.add_run(" / ")
        frun2.font.name = "Times New Roman"
        frun2.font.size = Pt(9)
        frun2.font.color.rgb = RGBColor(100, 116, 139)

        frun_total = fp.add_run()
        add_total_pages_to_run(frun_total)
        frun_total.font.name = "Times New Roman"
        frun_total.font.size = Pt(9)
        frun_total.font.color.rgb = RGBColor(100, 116, 139)

    # Base styling
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(30, 41, 59)
    normal_style.paragraph_format.line_spacing = 1.25
    normal_style.paragraph_format.space_after = Pt(4)

    # ==========================
    # COVER PAGE
    # ==========================
    p_uni = doc.add_paragraph()
    p_uni.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_uni = p_uni.add_run("BỘ GIÁO DỤC VÀ ĐÀO TẠO — ĐẠI HỌC DUY TÂN\nTRƯỜNG CÔNG NGHỆ THÔNG TIN VÀ MÁY TÍNH\nKHOA KỸ THUẬT PHẦN MỀM")
    r_uni.font.name = "Times New Roman"
    r_uni.font.size = Pt(11)
    r_uni.font.bold = True
    r_uni.font.color.rgb = RGBColor(71, 85, 105)
    p_uni.paragraph_format.space_after = Pt(50)

    # Decorative Line
    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_line = p_line.add_run("★ ★ ★")
    r_line.font.name = "Times New Roman"
    r_line.font.size = Pt(11)
    r_line.font.color.rgb = RGBColor(148, 163, 184)
    p_line.paragraph_format.space_after = Pt(40)

    # Main Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("BÁO CÁO XÁC ĐỊNH\nARCHITECTURAL DRIVERS")
    r_title.font.name = "Times New Roman"
    r_title.font.size = Pt(22)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(30, 58, 138)  # Deep Navy Blue
    p_title.paragraph_format.space_after = Pt(20)

    # Subtitle / Subject
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("Đề tài: ClassBridge — AI-Powered Assistant for EMI Classrooms\n(Hệ thống Trợ lý AI Hỗ trợ Tương tác Lớp học Giảng dạy bằng Tiếng Anh)")
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(13)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(15, 23, 42)
    p_sub.paragraph_format.space_after = Pt(60)

    # Info Box / Table
    info_table = doc.add_table(rows=5, cols=2)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(info_table, color="FFFFFF") # Borderless
    
    info_data = [
        ("Mã nhóm thực hiện:", "C1SE.38"),
        ("Chương trình đào tạo:", "Kỹ thuật Phần mềm (SE) - Capstone Project"),
        ("Thành viên chính phụ trách:", "Nguyễn Sỹ Tân (Lead) & Nhóm C1SE.38"),
        ("Đơn vị đào tạo:", "Đại học Duy Tân (DTU)"),
        ("Thời gian thực hiện:", "Học kỳ 1 — Năm học 2026")
    ]
    
    for idx, (label, val) in enumerate(info_data):
        row = info_table.rows[idx]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Cm(6.5)
        c1.width = Cm(9.5)
        
        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r0 = p0.add_run(label)
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(11.5)
        r0.font.bold = True
        r0.font.color.rgb = RGBColor(51, 65, 85)
        p0.paragraph_format.space_after = Pt(4)
        
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r1 = p1.add_run(val)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = RGBColor(15, 23, 42)
        p1.paragraph_format.space_after = Pt(4)

    p_bottom = doc.add_paragraph()
    p_bottom.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_bottom.paragraph_format.space_before = Pt(80)
    r_bottom = p_bottom.add_run("ĐÀ NẴNG, NĂM 2026")
    r_bottom.font.name = "Times New Roman"
    r_bottom.font.size = Pt(11)
    r_bottom.font.bold = True
    r_bottom.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_page_break()

    # ==========================
    # MỤC LỤC
    # ==========================
    p_toc_title = doc.add_paragraph()
    r_toc_title = p_toc_title.add_run("MỤC LỤC")
    r_toc_title.font.name = "Times New Roman"
    r_toc_title.font.size = Pt(16)
    r_toc_title.font.bold = True
    r_toc_title.font.color.rgb = RGBColor(30, 58, 138)
    p_toc_title.paragraph_format.space_after = Pt(12)

    toc_items = [
        ("PHẦN 1. THÔNG TIN ĐỀ TÀI VÀ PHÂN CÔNG ĐÓNG GÓP", 0, True),
        ("1.1. Thông tin chung", 1, False),
        ("1.2. Danh sách thành viên và mức độ đóng góp", 1, False),
        ("PHẦN 2. TỔNG QUAN HỆ THỐNG CLASSBRIDGE", 0, True),
        ("2.1. Bối cảnh và Vấn đề cốt lõi (The Broken Feedback Loop)", 1, False),
        ("2.2. Ý tưởng giải quyết và Chu trình khép kín", 1, False),
        ("PHẦN 3. XÁC ĐỊNH ARCHITECTURAL DRIVERS", 0, True),
        ("3.1. Mục đích thiết kế (Design Purpose)", 1, False),
        ("3.2. Yêu cầu Chức năng Cốt lõi (Primary Functional Requirements)", 1, False),
        ("3.2.1. FR-01: Khởi tạo & Tham gia Phiên học Ẩn danh", 2, False),
        ("3.2.2. FR-02: Chuyển đổi & Dịch Phụ đề Thời gian thực", 2, False),
        ("3.2.3. FR-03: Gom nhóm Câu hỏi Ngữ nghĩa Đa ngôn ngữ", 2, False),
        ("3.2.4. FR-04: Quản lý Cụm câu hỏi & Phản hồi Đại diện", 2, False),
        ("3.2.5. FR-05: Tổng hợp Báo cáo & Lưu trữ Bài giảng", 2, False),
        ("3.3. Ràng buộc Kiến trúc (Architectural Constraints)", 1, False),
        ("3.3.1. Ràng buộc Kỹ thuật (Technical Constraints)", 2, False),
        ("3.3.2. Ràng buộc Nghiệp vụ và Lịch trình (Business & Schedule Constraints)", 2, False),
        ("3.4. Mối quan tâm Kiến trúc (Architectural Concerns)", 1, False),
        ("PHẦN 4. THUỘC TÍNH CHẤT LƯỢNG (QAs) VÀ CÁC KỊCH BẢN CHI TIẾT", 0, True),
        ("4.1. QA 1: Performance (Hiệu năng & Độ trễ thời gian thực)", 1, False),
        ("4.1.1. Lý do lựa chọn", 2, False),
        ("4.1.2. Kịch bản 1.1: Xử lý và hiển thị phụ đề song ngữ trực tiếp", 2, False),
        ("4.1.3. Kịch bản 1.2: Gom cụm ngữ nghĩa khi nhiều sinh viên hỏi đồng thời", 2, False),
        ("4.1.4. Kịch bản 1.3: Phát tán câu trả lời đại diện 1-nhiều (Broadcast Response)", 2, False),
        ("4.2. QA 2: Availability & Fault Tolerance (Tính sẵn sàng & Khả năng chịu lỗi)", 1, False),
        ("4.2.1. Lý do lựa chọn", 2, False),
        ("4.2.2. Kịch bản 2.1: Cô lập lỗi khi tiến trình nhận diện giọng nói (STT) bị quá tải", 2, False),
        ("4.2.3. Kịch bản 2.2: Tự động khôi phục khi thiết bị sinh viên rớt mạng Wi-Fi tạm thời", 2, False),
        ("4.2.4. Kịch bản 2.3: Chặn đứng chuỗi dữ liệu rác khi không có giọng nói giảng viên", 2, False),
        ("4.3. QA 3: Security & Privacy (Bảo mật & Quyền riêng tư ẩn danh)", 1, False),
        ("4.3.1. Lý do lựa chọn", 2, False),
        ("4.3.2. Kịch bản 3.1: Bảo vệ danh tính tuyệt đối của sinh viên đặt câu hỏi", 2, False),
        ("4.3.3. Kịch bản 3.2: Chống tấn công làm ngập lụt câu hỏi (Spam / Flooding Attack)", 2, False),
        ("4.3.4. Kịch bản 3.3: Ngăn chặn truy cập trái phép vào phiên học đang diễn ra", 2, False),
        ("4.4. QA 4: Modifiability (Tính dễ sửa đổi & Thử nghiệm mô hình)", 1, False),
        ("4.4.1. Lý do lựa chọn", 2, False),
        ("4.4.2. Kịch bản 4.1: Thay thế mô hình trích xuất Vector Embedding để chạy Benchmark", 2, False),
        ("4.4.3. Kịch bản 4.2: Tinh chỉnh ngưỡng tương đồng ngữ nghĩa (Similarity Threshold)", 2, False),
        ("4.4.4. Kịch bản 4.3: Chuyển đổi mô hình tạo báo cáo tổng kết cuối buổi (Summarization LLM)", 2, False),
        ("PHẦN 5. KẾT LUẬN VÀ KẾ HOẠCH BÀN GIAO", 0, True)
    ]

    for item, level, is_bold in toc_items:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.6 * level)
        p.paragraph_format.space_after = Pt(2.5)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(item)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.bold = is_bold
        if is_bold:
            r.font.color.rgb = RGBColor(30, 58, 138)
        else:
            r.font.color.rgb = RGBColor(51, 65, 85)

    doc.add_page_break()

    # Helpers for content
    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(15)
        r.font.bold = True
        r.font.color.rgb = RGBColor(30, 58, 138)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(13.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(37, 99, 235)
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(15, 23, 42)
        return p

    def add_p(text, bold_prefix=None):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4.5)
        p.paragraph_format.line_spacing = 1.25
        if bold_prefix:
            r_bold = p.add_run(bold_prefix)
            r_bold.font.name = "Times New Roman"
            r_bold.font.size = Pt(12)
            r_bold.font.bold = True
            r_bold.font.color.rgb = RGBColor(15, 23, 42)
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.color.rgb = RGBColor(30, 41, 59)
        return p

    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3.5)
        p.paragraph_format.line_spacing = 1.25
        if bold_prefix:
            r_bold = p.add_run(bold_prefix)
            r_bold.font.name = "Times New Roman"
            r_bold.font.size = Pt(12)
            r_bold.font.bold = True
            r_bold.font.color.rgb = RGBColor(15, 23, 42)
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.color.rgb = RGBColor(30, 41, 59)
        return p

    def create_scenario_table(scenario_data):
        """
        Creates a clean 6-part QA scenario table.
        scenario_data: list of tuples (component_name, detail_text)
        """
        tbl = doc.add_table(rows=len(scenario_data) + 1, cols=2)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(tbl, color="CBD5E1", sz="4")

        # Header row
        hdr_row = tbl.rows[0]
        set_row_cant_split(hdr_row)
        set_row_header(hdr_row)
        
        hdr_c0 = hdr_row.cells[0]
        hdr_c1 = hdr_row.cells[1]
        hdr_c0.width = Cm(4.8)
        hdr_c1.width = Cm(11.7)
        
        set_cell_background(hdr_c0, "1E3A8A")
        set_cell_background(hdr_c1, "1E3A8A")
        set_cell_margins(hdr_c0, top=140, bottom=140, left=180, right=180)
        set_cell_margins(hdr_c1, top=140, bottom=140, left=180, right=180)

        p0 = hdr_c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r0 = p0.add_run("Thành phần kịch bản")
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(11)
        r0.font.bold = True
        r0.font.color.rgb = RGBColor(255, 255, 255)

        p1 = hdr_c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r1 = p1.add_run("Nội dung chi tiết")
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(11)
        r1.font.bold = True
        r1.font.color.rgb = RGBColor(255, 255, 255)

        # Body rows
        for i, (comp, detail) in enumerate(scenario_data):
            row = tbl.rows[i + 1]
            set_row_cant_split(row)
            c0, c1 = row.cells[0], row.cells[1]
            c0.width = Cm(4.8)
            c1.width = Cm(11.7)
            
            # Subtle zebra shading
            bg_col = "F8FAFC" if i % 2 == 1 else "FFFFFF"
            set_cell_background(c0, "EFF6FF" if i % 2 == 1 else "F8FAFC")
            set_cell_background(c1, bg_col)
            set_cell_margins(c0, top=110, bottom=110, left=160, right=160)
            set_cell_margins(c1, top=110, bottom=110, left=160, right=160)

            p_comp = c0.paragraphs[0]
            p_comp.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r_comp = p_comp.add_run(comp)
            r_comp.font.name = "Times New Roman"
            r_comp.font.size = Pt(11)
            r_comp.font.bold = True
            r_comp.font.color.rgb = RGBColor(30, 58, 138)

            p_det = c1.paragraphs[0]
            p_det.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p_det.paragraph_format.line_spacing = 1.2
            r_det = p_det.add_run(detail)
            r_det.font.name = "Times New Roman"
            r_det.font.size = Pt(11)
            r_det.font.color.rgb = RGBColor(30, 41, 59)

        # Spacing after table
        p_sp = doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(4)
        p_sp.paragraph_format.space_after = Pt(8)

    # ==========================
    # PHẦN 1
    # ==========================
    add_h1("PHẦN 1. THÔNG TIN ĐỀ TÀI VÀ PHÂN CÔNG ĐÓNG GÓP")
    
    add_h2("1.1. Thông tin chung")
    add_bullet("ClassBridge — Hệ thống Trợ lý AI hỗ trợ tương tác và phá vỡ rào cản ngôn ngữ trong lớp học giảng dạy bằng tiếng Anh (English-Medium Instruction - EMI).", "Tên đề tài: ")
    add_bullet("C1SE.38", "Mã nhóm: ")
    add_bullet("Đại học Duy Tân (DTU)", "Đơn vị: ")

    add_h2("1.2. Danh sách thành viên và mức độ đóng góp")
    
    # Table 1.2
    mem_table = doc.add_table(rows=7, cols=5)
    mem_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(mem_table, color="CBD5E1", sz="4")

    # Header
    m_hdr = mem_table.rows[0]
    set_row_cant_split(m_hdr)
    set_row_header(m_hdr)
    col_widths = [Cm(1.2), Cm(3.8), Cm(3.2), Cm(6.5), Cm(1.8)]
    hdr_titles = ["STT", "Họ và Tên", "Vai trò", "Nhiệm vụ phụ trách trong báo cáo Drivers", "Đóng góp"]
    
    for ci, title in enumerate(hdr_titles):
        c = m_hdr.cells[ci]
        c.width = col_widths[ci]
        set_cell_background(c, "1E3A8A")
        set_cell_margins(c, top=140, bottom=140, left=120, right=120)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(title)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    members_data = [
        ("1", "Nguyễn Sỹ Tân", "AI / Backend Lead", "Xác định mục đích thiết kế, ràng buộc kỹ thuật AI In-house, xây dựng kịch bản QA Performance & Modifiability.", "20%"),
        ("2", "Võ Trương Khải Hoàn", "System Architect", "Phân tích yêu cầu chức năng cốt lõi (Primary FRs), xác định Architectural Concerns và kịch bản Availability.", "20%"),
        ("3", "Phan Quang Tuấn", "Backend Developer", "Thiết kế luồng truyền nhận WebSocket real-time, xây dựng kịch bản QA Security & Privacy (Ẩn danh, Chống spam).", "20%"),
        ("4", "Trần Thị Thu Hồng", "Frontend / UI-UX", "Xác định yêu cầu Dashboard Giảng viên & Student Mobile Web, chuẩn hóa cấu trúc kịch bản chất lượng 6 thành phần.", "20%"),
        ("5", "Nguyễn Thành Nhân", "QA / Data Engineer", "Thiết lập thước đo định lượng (Response Measures), rà soát tính khả thi và nghiệm thu toàn bộ tài liệu.", "20%")
    ]

    for ri, row_data in enumerate(members_data):
        row = mem_table.rows[ri + 1]
        set_row_cant_split(row)
        bg_col = "F8FAFC" if ri % 2 == 1 else "FFFFFF"
        for ci, val in enumerate(row_data):
            c = row.cells[ci]
            c.width = col_widths[ci]
            set_cell_background(c, bg_col)
            set_cell_margins(c, top=100, bottom=100, left=120, right=120)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if ci in [0, 4] else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(10.5)
            if ci == 1:
                r.font.bold = True
            r.font.color.rgb = RGBColor(30, 41, 59)

    # Total row
    tot_row = mem_table.rows[6]
    set_row_cant_split(tot_row)
    c_tot_span = tot_row.cells[0]
    set_cell_background(c_tot_span, "F1F5F9")
    set_cell_margins(c_tot_span, top=110, bottom=110, left=120, right=120)
    p_tot0 = c_tot_span.paragraphs[0]
    p_tot0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_tot0 = p_tot0.add_run("Tổng cộng")
    r_tot0.font.name = "Times New Roman"
    r_tot0.font.size = Pt(10.5)
    r_tot0.font.bold = True

    for ci in range(1, 4):
        c = tot_row.cells[ci]
        set_cell_background(c, "F1F5F9")
        set_cell_margins(c, top=110, bottom=110, left=120, right=120)

    # Merge first 4 cells of total row
    c_tot_span.merge(tot_row.cells[1]).merge(tot_row.cells[2]).merge(tot_row.cells[3])

    c_tot_pct = tot_row.cells[4]
    set_cell_background(c_tot_pct, "F1F5F9")
    set_cell_margins(c_tot_pct, top=110, bottom=110, left=120, right=120)
    p_tot1 = c_tot_pct.paragraphs[0]
    p_tot1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_tot1 = p_tot1.add_run("100%")
    r_tot1.font.name = "Times New Roman"
    r_tot1.font.size = Pt(10.5)
    r_tot1.font.bold = True

    # Spacing
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_after = Pt(12)

    # ==========================
    # PHẦN 2
    # ==========================
    doc.add_page_break()
    add_h1("PHẦN 2. TỔNG QUAN HỆ THỐNG CLASSBRIDGE")
    
    add_h2("2.1. Bối cảnh và Vấn đề cốt lõi (The Broken Feedback Loop)")
    add_p("Trong các lớp học chuyên ngành công nghệ thông tin sử dụng tiếng Anh làm ngôn ngữ giảng dạy (English-Medium Instruction - EMI), khoảng cách hiểu bài (comprehension gap) giữa giảng viên quốc tế và sinh viên Việt Nam thường xuyên bị đứt gãy do ba nguyên nhân chính:")
    add_bullet("Lớp học vận hành một chiều khiến giảng viên không thể nắm bắt được sinh viên đang bị vướng mắc ở khái niệm nào, dẫn đến việc tiếp tục giảng qua các phần kiến thức nền tảng trong khi sinh viên đã mất phương hướng.", "Giảng viên thiếu thông tin phản hồi thời gian thực: ")
    add_bullet("Nhiều sinh viên có trình độ tiếng Anh chưa đồng đều, gặp khó khăn với thuật ngữ chuyên ngành và ngữ điệu (accent), dẫn đến không hiểu bài giảng và đặc biệt e ngại đặt câu hỏi bằng tiếng Anh trước đám đông do rào cản tâm lý sợ phát âm sai.", "Rào cản ngôn ngữ và tâm lý của sinh viên: ")
    add_bullet("Nhiều sinh viên cùng gặp một lỗi hoặc thắc mắc chung một khái niệm nhưng lại diễn đạt theo nhiều cách khác nhau (tiếng Việt, tiếng Anh, hoặc pha trộn code-switching), khiến giảng viên mất nhiều thời gian nếu phải giải đáp rời rạc từng câu một.", "Sự phân mảnh câu hỏi: ")

    add_h2("2.2. Ý tưởng giải quyết và Chu trình khép kín")
    add_p("ClassBridge khôi phục vòng phản hồi (Feedback Loop) hoàn chỉnh trong lớp học EMI thông qua quy trình 4 bước khép kín:")
    add_bullet("Khi giảng viên giảng bài bằng tiếng Anh, hệ thống thu âm trực tiếp qua micro, lọc khoảng lặng bằng Silero VAD, sử dụng mô hình Faster-Whisper để chuyển đổi lời nói sang văn bản và dịch song ngữ Anh ↔ Việt theo thời gian thực.", "Bước 1 — Phụ đề song ngữ trực tiếp: ")
    add_bullet("Khi sinh viên không hiểu bài, sinh viên quét mã QR hoặc nhập PIN để đặt câu hỏi ẩn danh (bằng tiếng Việt, tiếng Anh hoặc kết hợp). Module AI (multilingual-e5-base) tự động gom các câu hỏi có tính tương đồng ngữ nghĩa thành từng cụm (Cluster).", "Bước 2 — Hỏi đáp ẩn danh & Gom nhóm tương đồng: ")
    add_bullet("Giảng viên theo dõi trên Dashboard các cụm câu hỏi nóng nhất kèm thống kê trực quan và trả lời một lần cho câu hỏi đại diện; hệ thống tự động dịch và phát (broadcast) câu trả lời song ngữ đến toàn bộ sinh viên trong nhóm đó.", "Bước 3 — Bảng điều khiển Giảng viên & Phản hồi 1-nhiều: ")
    add_bullet("Khi kết thúc buổi học, AI tổng hợp nội dung bài giảng, lập biểu đồ nhiệt các điểm nghẽn kiến thức (Comprehension Heatmap) theo dòng thời gian và lưu trữ bài giảng cùng lịch sử hỏi đáp vào cơ sở dữ liệu.", "Bước 4 — Tổng hợp cuối buổi & Lưu trữ: ")

    # ==========================
    # PHẦN 3
    # ==========================
    doc.add_page_break()
    add_h1("PHẦN 3. XÁC ĐỊNH ARCHITECTURAL DRIVERS")
    
    add_h2("3.1. Mục đích thiết kế (Design Purpose)")
    add_p("Xây dựng một hệ thống thời gian thực tự triển khai mô hình AI cục bộ (Self-hosted / In-house AI Inference) có khả năng vận hành trực tiếp tại lớp học (Pilot Deployment) nhằm hiển thị hóa lỗ hổng kiến thức của sinh viên lên màn hình giảng viên mà không yêu cầu sinh viên nói trực tiếp bằng tiếng Anh, đồng thời cung cấp dữ liệu thực nghiệm định lượng phục vụ công bố khoa học.")

    add_h2("3.2. Yêu cầu Chức năng Cốt lõi (Primary Functional Requirements)")
    
    add_h3("3.2.1. FR-01: Khởi tạo & Tham gia Phiên học Ẩn danh")
    add_p("Giảng viên khởi tạo phiên học mới trên Dashboard, hệ thống tự động sinh mã PIN 6 số và mã QR. Sinh viên quét mã QR hoặc nhập PIN trên trình duyệt di động để vào thẳng phòng học với định danh tạm thời (Anonymous #ID) mà không cần tạo tài khoản hay đăng nhập.")

    add_h3("3.2.2. FR-02: Chuyển đổi & Dịch Phụ đề Thời gian thực")
    add_p("Hệ thống thu luồng âm thanh trực tiếp từ micro của giảng viên, lọc tạp âm và khoảng lặng thông qua Silero VAD. Chuyển đổi đoạn âm thanh tiếng Anh sang văn bản bằng Faster-Whisper và dịch thuật ngữ chuyên ngành sang tiếng Việt để hiển thị phụ đề song ngữ trên màn chiếu và thiết bị sinh viên.")

    add_h3("3.2.3. FR-03: Gom nhóm Câu hỏi Ngữ nghĩa Đa ngôn ngữ")
    add_p("Cho phép sinh viên gửi câu hỏi tự do bằng tiếng Việt, tiếng Anh hoặc pha trộn thuật ngữ (code-switching). Chuyển đổi văn bản câu hỏi thành vector ngữ nghĩa 768 chiều, tính toán khoảng cách Cosine với tâm các cụm hiện tại để tự động gộp vào cụm tương đồng hoặc khởi tạo cụm mới.")

    add_h3("3.2.4. FR-04: Quản lý Cụm câu hỏi & Phản hồi Đại diện")
    add_p("Sắp xếp và làm nổi bật các cụm câu hỏi trên Dashboard giảng viên dựa trên số lượng câu hỏi thành viên. Khi giảng viên nhập câu trả lời cho một cụm, hệ thống tự động dịch song ngữ và phát tán qua WebSocket đến toàn bộ sinh viên thuộc cụm đó.")

    add_h3("3.2.5. FR-05: Tổng hợp Báo cáo & Lưu trữ Bài giảng")
    add_p("Khi kết thúc buổi học, mô hình LLM cục bộ tổng hợp các nội dung chính từ bản ghi lời giảng (transcript) và danh sách các cụm câu hỏi. Tạo biểu đồ nhiệt mức độ hiểu bài theo dòng thời gian (Comprehension Heatmap) và lưu trữ toàn bộ tư liệu buổi học vào PostgreSQL.")

    add_h2("3.3. Ràng buộc Kiến trúc (Architectural Constraints)")
    
    add_h3("3.3.1. Ràng buộc Kỹ thuật (Technical Constraints)")
    add_bullet("Bắt buộc triển khai các mô hình mã nguồn mở chạy cục bộ (Silero VAD, Faster-Whisper, multilingual-e5-base, NLLB/Qwen) thay vì phụ thuộc vào các API thương mại bên ngoài để đảm bảo tính đóng góp học thuật (Novelty), làm chủ độ trễ và bảo mật dữ liệu lớp học.", "Mô hình AI Tự triển khai (Self-hosted / In-house AI Inference): ")
    add_bullet("Giao diện dành cho sinh viên bắt buộc phải là Mobile Web siêu nhẹ chạy trực tiếp trên trình duyệt điện thoại, không yêu cầu cài đặt ứng dụng.", "Nền tảng Tiếp cận Zero-Install: ")
    add_bullet("Frontend sử dụng Next.js (React) và Tailwind CSS; Backend sử dụng Python (FastAPI); Giao tiếp thời gian thực qua WebSocket; Cơ sở dữ liệu PostgreSQL; Đóng gói bằng Docker.", "Ngăn xếp Công nghệ Quy định: ")

    add_h3("3.3.2. Ràng buộc Nghiệp vụ và Lịch trình (Business & Schedule Constraints)")
    add_bullet("Hệ thống phải hoàn thiện các luồng cốt lõi để đưa vào vận hành thử nghiệm tại 2–3 lớp học EMI thực tế vào Tuần 4–5 của học kỳ.", "Thời hạn Pilot bắt buộc: ")
    add_bullet("Chi phí thuê máy chủ đám mây bằng 0 VND; toàn bộ hệ thống phải được tối ưu hóa để vận hành ổn định trên máy chủ cục bộ của nhóm hoặc phòng Lab nhà trường.", "Ngân sách hạ tầng: ")

    add_h2("3.4. Mối quan tâm Kiến trúc (Architectural Concerns)")
    add_bullet("Tác vụ nhận diện giọng nói liên tục tiêu tốn nhiều tài nguyên GPU/CPU; cần tách biệt hoàn toàn tiến trình Speech Pipeline khỏi tiến trình NLP Clustering để không gây nghẽn hàng đợi sự kiện WebSocket.", "Cô lập Tiến trình Xử lý Nặng (Worker Isolation): ")
    add_bullet("Mô hình Whisper dễ sinh ra các từ ngữ vô nghĩa khi gặp tiếng ồn nền hoặc khoảng lặng dài; kiến trúc bắt buộc phải có cổng kiểm soát âm thanh (VAD Gate) trước khi đưa dữ liệu vào mô hình.", "Chống Ảo giác Mô hình (Hallucination Mitigation): ")
    add_bullet("Duy trì phiên làm việc và chống mất gói tin cho 50–100 thiết bị di động kết nối chung mạng Wi-Fi giảng đường.", "Độ ổn định Kết nối Mạng Phòng học: ")

    # ==========================
    # PHẦN 4
    # ==========================
    doc.add_page_break()
    add_h1("PHẦN 4. THUỘC TÍNH CHẤT LƯỢNG (QAs) VÀ CÁC KỊCH BẢN CHI TIẾT")
    add_p("Nhóm C1SE.38 xác định 4 thuộc tính chất lượng quan trọng nhất đối với hệ thống ClassBridge: Performance, Availability & Fault Tolerance, Security & Privacy, và Modifiability.")

    # 4.1
    add_h2("4.1. QA 1: Performance (Hiệu năng & Độ trễ thời gian thực)")
    add_h3("4.1.1. Lý do lựa chọn")
    add_p("ClassBridge vận hành đồng bộ với lời giảng trực tiếp tại lớp. Nếu phụ đề hiển thị trễ quá vài giây, sinh viên sẽ không thể đối chiếu nội dung bài giảng. Đồng thời, nếu việc gom cụm câu hỏi xử lý chậm, giảng viên sẽ chuyển sang phần bài học khác trước khi nhận ra điểm nghẽn kiến thức của lớp, làm mất đi giá trị của vòng phản hồi thời gian thực.")

    add_h3("4.1.2. Kịch bản 1.1: Xử lý và hiển thị phụ đề song ngữ trực tiếp")
    create_scenario_table([
        ("Nguồn kích thích (Source)", "Giảng viên nước ngoài đang giảng bài."),
        ("Tác nhân kích thích (Stimulus)", "Giảng viên nói một câu hoàn chỉnh bằng tiếng Anh qua micro (độ dài đoạn âm thanh khoảng 3–5 giây)."),
        ("Thành phần bị tác động (Artifact)", "Speech Processing Pipeline (Silero VAD → Faster-Whisper → Translation Service) và WebSocket Gateway."),
        ("Môi trường (Environment)", "Giờ học bình thường, hệ thống đang duy trì kết nối đồng thời với 60 thiết bị của sinh viên trong lớp."),
        ("Phản hồi của hệ thống (Response)", "Hệ thống lọc bỏ khoảng lặng, nhận diện giọng nói thành văn bản tiếng Anh, dịch sang tiếng Việt và đẩy đồng loạt phụ đề song ngữ lên màn hình chiếu và thiết bị sinh viên."),
        ("Thước đo phản hồi (Response Measure)", "Tổng độ trễ đầu-cuối (End-to-End Latency) từ lúc giảng viên ngắt câu đến khi phụ đề hiển thị trên màn hình đạt ≤ 1.5 giây đối với ít nhất 95% các câu thoại.")
    ])

    add_h3("4.1.3. Kịch bản 1.2: Gom cụm ngữ nghĩa khi nhiều sinh viên hỏi đồng thời")
    create_scenario_table([
        ("Nguồn kích thích (Source)", "40 sinh viên trong lớp học EMI."),
        ("Tác nhân kích thích (Stimulus)", "Sinh viên gửi dồn dập 40 câu hỏi (bằng cả tiếng Việt, tiếng Anh và thuật ngữ pha trộn) trong vòng 15 giây sau một khái niệm khó."),
        ("Thành phần bị tác động (Artifact)", "NLP Clustering Service (multilingual-e5-base + Agglomerative Clustering) và Lecturer Dashboard."),
        ("Môi trường (Environment)", "Chế độ tải cao đột biến (Peak Load) trong phiên học, luồng phụ đề âm thanh vẫn đang chạy song song."),
        ("Phản hồi của hệ thống (Response)", "Hệ thống trích xuất vector embedding cho từng câu hỏi, tính toán khoảng cách Cosine, phân loại vào các cụm ngữ nghĩa và cập nhật danh sách cụm lên Dashboard giảng viên."),
        ("Thước đo phản hồi (Response Measure)", "Thời gian xử lý trung bình để phân cụm và cập nhật giao diện cho mỗi câu hỏi mới đạt ≤ 500ms, không xảy ra hiện tượng rớt hàng đợi (0% Queue Drop).")
    ])

    add_h3("4.1.4. Kịch bản 1.3: Phát tán câu trả lời đại diện 1-nhiều (Broadcast Response)")
    create_scenario_table([
        ("Nguồn kích thích (Source)", "Giảng viên."),
        ("Tác nhân kích thích (Stimulus)", "Giảng viên bấm gửi câu trả lời giải thích bằng tiếng Anh cho một cụm câu hỏi đang có 15 sinh viên theo dõi."),
        ("Thành phần bị tác động (Artifact)", "Backend API, Translation Module và WebSocket Broadcast Engine."),
        ("Môi trường (Environment)", "Hệ thống đang hoạt động bình thường trong giờ học."),
        ("Phản hồi của hệ thống (Response)", "Hệ thống tự động dịch câu trả lời sang tiếng Việt, lưu vào PostgreSQL và phát đồng thời bản phản hồi song ngữ đến đúng màn hình của các sinh viên trong cụm."),
        ("Thước đo phản hồi (Response Measure)", "100% sinh viên trong cụm nhận được thông báo và nội dung câu trả lời trên điện thoại trong vòng ≤ 400ms kể từ khi giảng viên nhấn nút gửi.")
    ])

    # 4.2
    add_h2("4.2. QA 2: Availability & Fault Tolerance (Tính sẵn sàng & Khả năng chịu lỗi)")
    add_h3("4.2.1. Lý do lựa chọn")
    add_p("Một buổi học thực nghiệm (Pilot) kéo dài liên tục từ 45 đến 90 phút và không thể tạm dừng để khắc phục sự cố phần mềm. Do hệ thống chạy các mô hình AI cục bộ tiêu tốn nhiều tài nguyên và hoạt động trên mạng Wi-Fi giảng đường dễ chập chờn, kiến trúc bắt buộc phải có cơ chế cô lập lỗi (Fault Isolation) và tự phục hồi để sự cố ở một module không làm sập toàn bộ phiên học.")

    add_h3("4.2.2. Kịch bản 2.1: Cô lập lỗi khi tiến trình nhận diện giọng nói (STT) bị quá tải")
    create_scenario_table([
        ("Nguồn kích thích (Source)", "Tiến trình hệ thống nội bộ (Internal AI Worker)."),
        ("Tác nhân kích thích (Stimulus)", "Tiến trình Faster-Whisper gặp lỗi tràn bộ nhớ (Out-of-Memory) hoặc treo tiến trình do xử lý một đoạn âm thanh nhiễu kéo dài."),
        ("Thành phần bị tác động (Artifact)", "STT Worker Container và hệ thống Backend."),
        ("Môi trường (Environment)", "Đang trong giờ học trực tiếp, sinh viên vẫn đang đặt câu hỏi và giảng viên đang theo dõi Dashboard."),
        ("Phản hồi của hệ thống (Response)", "Nhờ kiến trúc tách biệt tiến trình, luồng đặt câu hỏi ẩn danh và gom cụm ngữ nghĩa (Q&A Clustering) vẫn tiếp tục hoạt động bình thường. Hệ thống giám sát tự động giải phóng bộ nhớ và khởi động lại STT Worker mà không làm gián đoạn phiên học."),
        ("Thước đo phản hồi (Response Measure)", "Luồng Q&A và Dashboard duy trì 100% thời gian hoạt động (Zero Downtime); tiến trình STT tự động khôi phục và tiếp tục hiển thị phụ đề trong vòng ≤ 5 giây.")
    ])

    add_h3("4.2.2. Kịch bản 2.2: Tự động khôi phục khi thiết bị sinh viên rớt mạng Wi-Fi tạm thời")
    create_scenario_table([
        ("Nguồn kích thích (Source)", "Mạng Wi-Fi tại giảng đường."),
        ("Tác nhân kích thích (Stimulus)", "Kết nối mạng trên điện thoại của sinh viên bị ngắt quãng trong 10 giây ngay lúc sinh viên bấm nút \"Gửi câu hỏi ẩn danh\"."),
        ("Thành phần bị tác động (Artifact)", "Student Mobile Web Client (Local State & WebSocket Client)."),
        ("Môi trường (Environment)", "Môi trường mạng không ổn định tại phòng học đông người."),
        ("Phản hồi của hệ thống (Response)", "Giao diện Web của sinh viên lưu tạm câu hỏi vào bộ nhớ cục bộ (Local Storage Queue), hiển thị trạng thái chờ mạng, tự động kết nối lại (Auto-reconnect) khi có Wi-Fi, gửi lại câu hỏi và đồng bộ danh sách câu trả lời mà không bắt nhập lại mã PIN."),
        ("Thước đo phản hồi (Response Measure)", "Tỷ lệ mất mát câu hỏi của sinh viên là 0%; kết nối WebSocket và trạng thái phòng học được đồng bộ hoàn tất trong ≤ 2 giây sau khi thiết bị có mạng trở lại.")
    ])

    add_h3("4.2.3. Kịch bản 2.3: Chặn đứng chuỗi dữ liệu rác khi không có giọng nói giảng viên")
    create_scenario_table([
        ("Nguồn kích thích (Source)", "Môi trường âm thanh phòng học."),
        ("Tác nhân kích thích (Stimulus)", "Giảng viên dừng giảng bài trong 3 phút để sinh viên làm bài tập, micro chỉ thu tiếng ồn quạt máy và tiếng thảo luận nhỏ trong lớp."),
        ("Thành phần bị tác động (Artifact)", "Module lọc giọng nói (Silero VAD) và Mô hình Faster-Whisper."),
        ("Môi trường (Environment)", "Micro giảng viên vẫn đang bật ở chế độ thu âm trực tiếp (Live Recording)."),
        ("Phản hồi của hệ thống (Response)", "Module VAD phát hiện âm thanh không phải giọng nói rõ ràng của giảng viên và tự động ngắt luồng đẩy audio chunk sang Whisper, giữ nguyên màn hình phụ đề ở câu nói cuối cùng thay vì sinh ra các chuỗi văn bản ảo giác (Hallucination)."),
        ("Thước đo phản hồi (Response Measure)", "0 dòng phụ đề rác/ảo giác được hiển thị lên màn hình trong suốt thời gian giảng viên im lặng; tiết kiệm ≥ 80% tài nguyên GPU/CPU trong khoảng thời gian nghỉ.")
    ])

    # 4.3
    add_h2("4.3. QA 3: Security & Privacy (Bảo mật & Quyền riêng tư ẩn danh)")
    add_h3("4.3.1. Lý do lựa chọn")
    add_p("Yếu tố then chốt giúp sinh viên vượt qua rào cản tâm lý để đặt câu hỏi trong lớp EMI là sự ẩn danh tuyệt đối. Nếu sinh viên lo sợ danh tính bị lộ khi hỏi một kiến thức cơ bản, họ sẽ không sử dụng hệ thống. Ngược lại, cơ chế tham gia ẩn danh không cần tài khoản đòi hỏi hệ thống phải có biện pháp chống spam câu hỏi rác hoặc truy cập trái phép từ bên ngoài lớp học.")

    add_h3("4.3.2. Kịch bản 3.1: Bảo vệ danh tính tuyệt đối của sinh viên đặt câu hỏi")
    create_scenario_table([
        ("Nguồn kích thích (Source)", "Giảng viên hoặc người dùng có quyền truy cập vào giao diện quản trị/báo cáo."),
        ("Tác nhân kích thích (Stimulus)", "Kiểm tra thông tin chi tiết của một câu hỏi trên Dashboard hoặc trong dữ liệu lưu trữ cuối buổi nhằm tìm kiếm danh tính người gửi."),
        ("Thành phần bị tác động (Artifact)", "Cơ sở dữ liệu PostgreSQL, API Response và Giao diện Dashboard."),
        ("Môi trường (Environment)", "Trong giờ học và sau khi xuất báo cáo lưu trữ cuối buổi."),
        ("Phản hồi của hệ thống (Response)", "Hệ thống chỉ cấp phát một mã phiên ngẫu nhiên một chiều (Anonymous_Hash_ID), hoàn toàn không thu thập họ tên, mã số sinh viên, email hay địa chỉ IP cá nhân vào bảng câu hỏi."),
        ("Thước đo phản hồi (Response Measure)", "0% khả năng truy vết ngược từ nội dung câu hỏi về danh tính cá nhân thật của sinh viên trên cả giao diện lẫn cơ sở dữ liệu.")
    ])

    add_h3("4.3.3. Kịch bản 3.2: Chống tấn công làm ngập lụt câu hỏi (Spam / Flooding Attack)")
    create_scenario_table([
        ("Nguồn kích thích (Source)", "Một sinh viên cố tình gây rối trong lớp học."),
        ("Tác nhân kích thích (Stimulus)", "Sử dụng công cụ tự động hoặc bấm liên tục để gửi 30 câu hỏi vô nghĩa trong vòng 10 giây nhằm làm nhiễu loạn thuật toán gom cụm và làm tràn màn hình giảng viên."),
        ("Thành phần bị tác động (Artifact)", "API Gateway / Rate Limiter và NLP Clustering Engine."),
        ("Môi trường (Environment)", "Phiên học đang diễn ra bình thường."),
        ("Phản hồi của hệ thống (Response)", "Tầng kiểm soát tốc độ (Rate Limiting theo Session Token) phát hiện tần suất bất thường, lập tức chặn các request vượt ngưỡng trước khi chúng đi vào mô hình AI và trả thông báo cảnh báo về thiết bị gửi."),
        ("Thước đo phản hồi (Response Measure)", "Hệ thống giới hạn tối đa 3 câu hỏi / phút trên mỗi phiên ẩn danh; 100% các request vượt ngưỡng bị từ chối trong ≤ 20ms mà không tiêu tốn tài nguyên của mô hình NLP.")
    ])

    add_h3("4.3.4. Kịch bản 3.3: Ngăn chặn truy cập trái phép vào phiên học đang diễn ra")
    create_scenario_table([
        ("Nguồn kích thích (Source)", "Người dùng bên ngoài không thuộc lớp học."),
        ("Tác nhân kích thích (Stimulus)", "Cố tình đoán đường dẫn URL của phòng học để vào xem phụ đề hoặc gửi câu hỏi phá rối."),
        ("Thành phần bị tác động (Artifact)", "Session Authentication Middleware."),
        ("Môi trường (Environment)", "Phiên học đang mở trên mạng nội bộ/Internet."),
        ("Phản hồi của hệ thống (Response)", "Hệ thống yêu cầu xác thực bằng mã PIN 6 số động (chỉ hiển thị trên máy chiếu tại phòng học) hoặc chữ ký số ngắn hạn nằm trong mã QR của đúng ca học đó; tự động hủy hiệu lực mã PIN ngay khi giảng viên kết thúc buổi học."),
        ("Thước đo phản hồi (Response Measure)", "Từ chối 100% các kết nối WebSocket và HTTP request không đính kèm Session Token hợp lệ của ca học hiện tại.")
    ])

    # 4.4
    add_h2("4.4. QA 4: Modifiability (Tính dễ sửa đổi & Thử nghiệm mô hình)")
    add_h3("4.4.1. Lý do lựa chọn")
    add_p("Dự án ClassBridge gắn liền với mục tiêu nghiên cứu khoa học thực nghiệm. Nhóm cần liên tục thử nghiệm và đối sánh các mô hình ngôn ngữ khác nhau (ví dụ: so sánh LaBSE với multilingual-e5-base, hoặc điều chỉnh ngưỡng Cosine Similarity) để đo đạc các chỉ số học thuật (ARI, NMI, Silhouette Score). Kiến trúc phải đảm bảo tính tách biệt (Loose Coupling) để việc thay đổi mô hình AI không làm xáo trộn hệ thống Backend và Giao diện.")

    add_h3("4.4.2. Kịch bản 4.1: Thay thế mô hình trích xuất Vector Embedding để chạy Benchmark")
    create_scenario_table([
        ("Nguồn kích thích (Source)", "Thành viên phụ trách AI/NLP của nhóm phát triển."),
        ("Tác nhân kích thích (Stimulus)", "Yêu cầu đổi mô hình embedding từ LaBSE sang intfloat/multilingual-e5-base để đo lường sự thay đổi của chỉ số Adjusted Rand Index (ARI) và Silhouette Score."),
        ("Thành phần bị tác động (Artifact)", "Module EmbeddingService trong tầng AI Inference."),
        ("Môi trường (Environment)", "Trong quá trình phát triển và thực nghiệm (Development / Testing)."),
        ("Phản hồi của hệ thống (Response)", "Nhờ áp dụng mẫu thiết kế Strategy/Adapter Pattern cho tầng AI, lập trình viên chỉ cần khai báo tên mô hình mới trong file cấu hình .env và nạp trọng số tương ứng mà không cần sửa đổi logic phân cụm hay cấu trúc API."),
        ("Thước đo phản hồi (Response Measure)", "Việc chuyển đổi mô hình hoàn tất và sẵn sàng chạy kiểm thử trong ≤ 1 giờ làm việc, với 0 dòng code bị sửa đổi ở tầng Frontend và Database.")
    ])

    add_h3("4.4.3. Kịch bản 4.2: Tinh chỉnh ngưỡng tương đồng ngữ nghĩa (Similarity Threshold)")
    create_scenario_table([
        ("Nguồn kích thích (Source)", "Nhóm nghiên cứu trong giai đoạn chạy thử nghiệm (Pilot Deployment)."),
        ("Tác nhân kích thích (Stimulus)", "Sau buổi học thử nghiệm đầu tiên, nhóm nhận thấy các câu hỏi bị gom chung hơi lỏng lẻo và muốn tăng ngưỡng Cosine Similarity từ 0.65 lên 0.75."),
        ("Thành phần bị tác động (Artifact)", "Cấu hình thuật toán gom cụm (Clustering Configuration)."),
        ("Môi trường (Environment)", "Giữa các ca học thực nghiệm."),
        ("Phản hồi của hệ thống (Response)", "Tham số ngưỡng phân cụm được tách riêng thành biến cấu hình động; nhóm cập nhật giá trị mới và hệ thống áp dụng ngay lập tức cho các câu hỏi tiếp theo mà không cần biên dịch (build) hay triển khai lại toàn bộ hệ thống."),
        ("Thước đo phản hồi (Response Measure)", "Thời gian cập nhật và áp dụng ngưỡng thuật toán mới mất ≤ 5 phút, không gây gián đoạn cơ sở dữ liệu hiện có.")
    ])

    add_h3("4.4.4. Kịch bản 4.3: Chuyển đổi mô hình tạo báo cáo tổng kết cuối buổi (Summarization LLM)")
    create_scenario_table([
        ("Nguồn kích thích (Source)", "Nhóm phát triển."),
        ("Tác nhân kích thích (Stimulus)", "Muốn thay đổi công cụ tổng hợp báo cáo cuối buổi từ mô hình chạy cục bộ (Qwen2.5-7B qua Ollama) sang một mô hình gọn nhẹ hơn khi máy chủ cục bộ thiếu VRAM."),
        ("Thành phần bị tác động (Artifact)", "SessionSummaryService tại Backend."),
        ("Môi trường (Environment)", "Trước khi triển khai tại một phòng học mới có cấu hình phần cứng khác biệt."),
        ("Phản hồi của hệ thống (Response)", "Tầng giao tiếp LLM được chuẩn hóa qua một giao diện chung (Unified LLM Interface); việc chuyển đổi điểm cuối (Endpoint) xử lý tóm tắt diễn ra độc lập, giữ nguyên định dạng JSON trả về cho biểu đồ nhiệt (Heatmap) và file PDF lưu trữ."),
        ("Thước đo phản hồi (Response Measure)", "Thay đổi hoàn tất trong ≤ 30 phút cấu hình, 100% các tính năng hiển thị báo cáo và lưu trữ PDF hoạt động bình thường không phát sinh lỗi tương thích.")
    ])

    # ==========================
    # PHẦN 5
    # ==========================
    doc.add_page_break()
    add_h1("PHẦN 5. KẾT LUẬN VÀ KẾ HOẠCH BÀN GIAO")
    add_p("Tài liệu Architectural Drivers của đề tài ClassBridge (Nhóm C1SE.38) đã xác lập đầy đủ các nền tảng kiến trúc cốt lõi:")
    add_bullet("Giải quyết bài toán đứt gãy vòng phản hồi (Broken Feedback Loop) trong lớp học EMI thông qua chu trình 4 bước khép kín: Phụ đề song ngữ trực tiếp (Whisper STT + Dịch), Hỏi đáp ẩn danh & Gom nhóm tương đồng, Dashboard giảng viên phản hồi 1-nhiều, và Tổng hợp lưu trữ bài giảng cuối buổi.")
    add_bullet("Đáp ứng nghiêm ngặt ràng buộc triển khai mô hình AI cục bộ (Self-hosted / In-house AI Inference) nhằm đảm bảo giá trị nghiên cứu khoa học và sẵn sàng cho cột mốc thử nghiệm thực tế (Pilot Deployment) vào Tuần 4–5 của học kỳ.")
    add_bullet("Định lượng hóa 12 kịch bản thuộc tính chất lượng thuộc 4 nhóm (Performance, Availability, Security, Modifiability), làm cơ sở trực tiếp cho giai đoạn thiết kế kiến trúc hệ thống (System Architecture Design) tiếp theo.")

    # Save destinations
    output_paths = [
        r"d:\TailieuNPKH\classbridge\docs\ClassBridge_Architectural_Drivers_C1SE38.docx",
        r"d:\TailieuNPKH\classbridge\ClassBridge_Architectural_Drivers_C1SE38.docx",
    ]
    
    # Also save to user Downloads folder if accessible
    user_profile = os.environ.get("USERPROFILE", "")
    if user_profile:
        dl_dir = os.path.join(user_profile, "Downloads")
        if os.path.exists(dl_dir):
            output_paths.append(os.path.join(dl_dir, "ClassBridge_Architectural_Drivers_C1SE38.docx"))

    for path in output_paths:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            doc.save(path)
            print(f"[SUCCESS] Saved docx to: {path}")
        except Exception as e:
            print(f"[ERROR] Could not save to {path}: {e}")

if __name__ == "__main__":
    build_document()
