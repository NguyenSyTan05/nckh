# -*- coding: utf-8 -*-
"""
Xuất toàn bộ 9 sơ đồ kiến trúc C4 Model (Cấp độ 1 -> Cấp độ 4)
ra chuẩn file .drawio (diagrams.net XML) theo đúng phong cách c4model.com:
- Hình người C4 (Person) màu xanh lá đậm (#2e6b4e)
- Khung trình duyệt UI, Folder, Terminal (>_), Cylinder DB màu xanh dương (#2b6cb0)
- Khung External / Worker bên ngoài màu nâu xám (#6b5b57)
- Khung Boundary có nhãn nằm ở góc dưới bên trái (Bottom-Left)
- Mũi tên nét đứt thẳng (Straight Dashed Line) nối trực tiếp giữa các khối.
"""

import os
import html
from diagram_definitions import DIAGRAMS

OUT_DIR = r"d:\TailieuNPKH\classbridge\TaiLieuF\01_SoDo_DrawIO"
ROOT_DIR = r"d:\TailieuNPKH\classbridge\TaiLieuF"


def get_node_style(kind: str) -> str:
    base = "whiteSpace=wrap;html=1;align=center;verticalAlign=middle;spacingLeft=8;spacingRight=8;spacingTop=6;spacingBottom=6;fontFamily=Segoe UI;"
    if kind == "person":
        return (
            "shape=mxgraph.c4.person2;whiteSpace=wrap;html=1;align=center;verticalAlign=top;"
            "spacingTop=48;spacingLeft=8;spacingRight=8;"
            "fillColor=#f4fbf7;strokeColor=#2e6b4e;strokeWidth=2.2;fontColor=#1e4631;fontFamily=Segoe UI;"
        )
    elif kind == "ui":
        return (
            "shape=mxgraph.c4.webBrowserContainer2;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;"
            "spacingTop=22;spacingLeft=8;spacingRight=8;"
            "fillColor=#f2f7fc;strokeColor=#2b6cb0;strokeWidth=2.2;fontColor=#163a5f;fontFamily=Segoe UI;"
        )
    elif kind == "folder":
        return (
            "shape=folder;fontStyle=0;tabWidth=70;tabHeight=16;tabPosition=left;html=1;whiteSpace=wrap;"
            "align=center;verticalAlign=middle;spacingTop=14;"
            "fillColor=#f2f7fc;strokeColor=#2b6cb0;strokeWidth=2.2;fontColor=#163a5f;fontFamily=Segoe UI;"
        )
    elif kind in ("backend", "comp", "sys"):
        return (
            base
            + "rounded=1;arcSize=6;fillColor=#f2f7fc;strokeColor=#2b6cb0;strokeWidth=2.2;fontColor=#163a5f;"
        )
    elif kind == "db":
        return (
            "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=12;"
            "align=center;verticalAlign=middle;spacingLeft=8;spacingRight=8;spacingTop=14;spacingBottom=6;"
            "fillColor=#f2f7fc;strokeColor=#2b6cb0;strokeWidth=2.2;fontColor=#163a5f;fontFamily=Segoe UI;"
        )
    elif kind == "iface":
        return (
            base
            + "rounded=1;arcSize=6;fillColor=#ffffff;strokeColor=#2b6cb0;strokeWidth=2;dashed=1;dashPattern=6 4;fontColor=#163a5f;"
        )
    else:  # ext
        return (
            base
            + "rounded=1;arcSize=6;fillColor=#f8f6f6;strokeColor=#6b5b57;strokeWidth=2.2;fontColor=#3b2f2c;"
        )


def format_node_html(node: dict) -> str:
    title = html.escape(node["title"])
    if node["kind"] == "backend" and not title.startswith("&gt;_"):
        title = f"&gt;_ {title}"
    stereo = html.escape(node["stereo"])
    body_lines = "<br/>".join(html.escape(line) for line in node["lines"])
    html_val = (
        f'<div style="line-height:1.3;">'
        f'<b style="font-size:13.5px;">{title}</b><br/>'
        f'<span style="font-size:10.5px;opacity:0.85;">{stereo}</span><br/><br/>'
        f'<span style="font-size:11.5px;">{body_lines}</span>'
        f"</div>"
    )
    return html.escape(html_val, quote=True)


def format_boundary_html(b: dict) -> str:
    t = html.escape(b["title"])
    s = html.escape(b.get("subtitle", ""))
    val = (
        f'<div style="line-height:1.25;text-align:left;">'
        f'<b style="font-size:13.5px;color:#222222;">{t}</b><br/>'
        f'<span style="font-size:11px;color:#555555;">{s}</span>'
        f"</div>"
    )
    return html.escape(val, quote=True)


def format_edge_html(label: str) -> str:
    lines = label.split("\n")
    if len(lines) >= 2:
        main_txt = html.escape(lines[0])
        sub_txt = html.escape(lines[1])
        val = (
            f'<div style="background:#ffffff;padding:1px 4px;line-height:1.2;">'
            f'<span style="font-size:11px;color:#333333;font-weight:600;">{main_txt}</span><br/>'
            f'<span style="font-size:10px;color:#555555;">{sub_txt}</span>'
            f"</div>"
        )
    else:
        val = (
            f'<div style="background:#ffffff;padding:1px 4px;">'
            f'<span style="font-size:11px;color:#333333;font-weight:600;">{html.escape(label)}</span>'
            f"</div>"
        )
    return html.escape(val, quote=True)


def build_diagram_xml(diag: dict) -> str:
    cw = diag.get("canvas_w", 1600)
    ch = diag.get("canvas_h", 1080)
    cells = []

    # Boundaries (Label at Bottom-Left just like c4model.com!)
    for b in diag.get("boundaries", []):
        b_val = format_boundary_html(b)
        b_style = (
            "rounded=1;arcSize=3;whiteSpace=wrap;html=1;align=left;verticalAlign=bottom;"
            "spacingLeft=14;spacingBottom=10;fillColor=none;"
            "strokeColor=#555555;strokeWidth=2;fontFamily=Segoe UI;"
        )
        cells.append(
            f'        <mxCell id="{b["id"]}" value="{b_val}" style="{b_style}" vertex="1" parent="1">\n'
            f'          <mxGeometry x="{b["x"]}" y="{b["y"]}" width="{b["w"]}" height="{b["h"]}" as="geometry" />\n'
            f"        </mxCell>"
        )

    # Nodes
    for n in diag["nodes"]:
        n_val = format_node_html(n)
        n_style = get_node_style(n["kind"])
        cells.append(
            f'        <mxCell id="{n["id"]}" value="{n_val}" style="{n_style}" vertex="1" parent="1">\n'
            f'          <mxGeometry x="{n["x"]}" y="{n["y"]}" width="{n["w"]}" height="{n["h"]}" as="geometry" />\n'
            f"        </mxCell>"
        )

    # Straight Dashed Edges (c4model.com style)
    for idx, e in enumerate(diag["edges"], start=1):
        e_val = format_edge_html(e["label"])
        e_style = (
            "edgeStyle=none;rounded=0;html=1;"
            "strokeColor=#666666;strokeWidth=1.8;dashed=1;dashPattern=6 5;"
            "endArrow=block;endFill=1;endSize=7;fontFamily=Segoe UI;labelBackgroundColor=#ffffff;"
        )
        cells.append(
            f'        <mxCell id="edge_{idx}" value="{e_val}" style="{e_style}" '
            f'edge="1" parent="1" source="{e["src"]}" target="{e["dst"]}">\n'
            f'          <mxGeometry relative="1" as="geometry" />\n'
            f"        </mxCell>"
        )

    cells_str = "\n".join(cells)
    return (
        f'  <diagram id="{diag["id"]}" name="{html.escape(diag["tab_name"], quote=True)}">\n'
        f'    <mxGraphModel dx="1600" dy="1000" grid="1" gridSize="10" guides="1" tooltips="1" '
        f'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{cw}" pageHeight="{ch}" '
        f'math="0" shadow="0">\n'
        f"      <root>\n"
        f'        <mxCell id="0" />\n'
        f'        <mxCell id="1" parent="0" />\n'
        f"{cells_str}\n"
        f"      </root>\n"
        f"    </mxGraphModel>\n"
        f"  </diagram>"
    )


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    all_pages = []

    for diag in DIAGRAMS:
        page_xml = build_diagram_xml(diag)
        all_pages.append(page_xml)
        single_mxfile = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<mxfile host="app.diagrams.net" modified="2026-11-04T09:48:00.000Z" '
            'agent="ClassBridge-C4-Generator" version="24.7.0" type="device">\n'
            f"{page_xml}\n"
            "</mxfile>\n"
        )
        out_path = os.path.join(OUT_DIR, f'{diag["filename"]}.drawio')
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(single_mxfile)
        print(f"[OK] Saved C4 Draw.io: {out_path}")

    combined_mxfile = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<mxfile host="app.diagrams.net" modified="2026-11-04T09:48:00.000Z" '
        'agent="ClassBridge-C4-Generator" version="24.7.0" type="device">\n'
        + "\n".join(all_pages)
        + "\n</mxfile>\n"
    )
    master_out1 = os.path.join(OUT_DIR, "00_Full_9_SoDo_C4_ClassBridge_C1SE38.drawio")
    master_out2 = os.path.join(ROOT_DIR, "ClassBridge_9_SoDo_KienTruc_C4_Model_C1SE38.drawio")
    for p in (master_out1, master_out2):
        with open(p, "w", encoding="utf-8") as f:
            f.write(combined_mxfile)
        print(f"[OK] Saved Master 9-Tab Draw.io: {p}")


if __name__ == "__main__":
    main()
