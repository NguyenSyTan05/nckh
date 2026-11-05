# -*- coding: utf-8 -*-
"""
Tạo file Word (.docx) chỉ chứa thuần túy từ Hình 1 (1.1) đến Hình 4.4:
- Không trang bìa, không mục lục, không bảng phụ lục dư thừa
- Chỉ gồm đúng 4 Cấp độ C4 (từ Hình 1 / 1.1 đến Hình 4.4):
  Mỗi mục gồm: Tiêu đề Hình + Hình ảnh sơ đồ C4 sắc nét + Mô tả chi tiết ngay bên dưới.
"""

import os
from diagram_definitions import DIAGRAMS
from generate_word_reports import (
    make_h1,
    make_h2,
    make_h3,
    make_body_p,
    make_bullet_p,
    make_image_drawing_p,
    make_caption_p,
    make_page_break,
    write_docx_with_images,
    OUT_DIR,
)


def build_only_figures_1_to_4_4() -> str:
    elems = []
    seen_levels = set()

    for idx, diag in enumerate(DIAGRAMS, start=1):
        lvl = diag["level_title"]
        if idx > 1:
            elems.append(make_page_break())

        if lvl not in seen_levels:
            elems.append(make_h1(lvl))
            seen_levels.add(lvl)

        # Figure heading
        fig_title = diag["figure_title"]
        elems.append(make_h2(fig_title))
        elems.append(
            make_body_p(
                f"({diag['layout_note']})",
                bold_prefix="Bố cục sơ đồ: ",
            )
        )

        # Embedded High-Res PNG Diagram
        cw = diag.get("canvas_w", 1600)
        ch = diag.get("canvas_h", 1080)
        img_w_cm = 16.4
        img_h_cm = round(img_w_cm * (ch / float(cw)), 2)
        r_id = f"rIdImg{idx}"
        elems.append(make_image_drawing_p(r_id, 200 + idx, diag["filename"], img_w_cm, img_h_cm))
        elems.append(make_caption_p(fig_title))

        # Detailed description section
        short_name = fig_title.split("—")[0].strip()
        elems.append(make_h3(f"Mô tả chi tiết {short_name}"))
        for bold_pref, desc_txt in diag["descriptions"]:
            elems.append(make_bullet_p(desc_txt, bold_prefix=bold_pref))

    return "".join(elems)


def main():
    body_xml = build_only_figures_1_to_4_4()
    out_docx = os.path.join(OUT_DIR, "ClassBridge_Hinh_1_1_Den_4_4_Va_Mo_Ta.docx")
    write_docx_with_images(
        out_docx,
        body_xml,
        "ClassBridge — Sơ Đồ Kiến Trúc C4 Model (Hình 1 đến Hình 4.4) & Mô Tả Chi Tiết | Nhóm C1SE.38",
    )


if __name__ == "__main__":
    main()

