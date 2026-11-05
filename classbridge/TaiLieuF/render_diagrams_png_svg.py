# -*- coding: utf-8 -*-
"""
Tính toán đường thẳng nối tâm-tới-tâm cắt viền (Ray-Box Intersection) chuẩn C4 Model (c4model.com)
để các mũi tên nét đứt đi thẳng tự nhiên từ cạnh hộp nguồn tới cạnh hộp đích.
"""

import os
import json
import math
from diagram_definitions import DIAGRAMS

OUT_PNG_DIR = r"d:\TailieuNPKH\classbridge\TaiLieuF\02_HinhAnh_SoDo_PNG"


def clip_ray_to_rect(cx: float, cy: float, w: float, h: float, dx: float, dy: float, pad: float = 4.0) -> tuple[float, float]:
    """Tìm giao điểm của tia xuất phát từ tâm (cx, cy) theo hướng (dx, dy) với hình chữ nhật (w, h)."""
    if abs(dx) < 1e-6 and abs(dy) < 1e-6:
        return (cx, cy)
    hw = (w / 2.0) + pad
    hh = (h / 2.0) + pad
    tx = hw / abs(dx) if abs(dx) > 1e-6 else float("inf")
    ty = hh / abs(dy) if abs(dy) > 1e-6 else float("inf")
    t = min(tx, ty)
    return (cx + dx * t, cy + dy * t)


def main():
    os.makedirs(OUT_PNG_DIR, exist_ok=True)
    export_list = []

    for diag in DIAGRAMS:
        node_map = {n["id"]: n for n in diag["nodes"]}
        computed_edges = []
        for e in diag["edges"]:
            n_src = node_map[e["src"]]
            n_dst = node_map[e["dst"]]

            # Tâm của 2 khối
            c1x = n_src["x"] + n_src["w"] / 2.0
            c1y = n_src["y"] + n_src["h"] / 2.0
            c2x = n_dst["x"] + n_dst["w"] / 2.0
            c2y = n_dst["y"] + n_dst["h"] / 2.0

            dx = c2x - c1x
            dy = c2y - c1y
            dist = math.hypot(dx, dy)
            if dist > 1e-6:
                ux, uy = dx / dist, dy / dist
            else:
                ux, uy = 0.0, 1.0

            p1 = clip_ray_to_rect(c1x, c1y, n_src["w"], n_src["h"], ux, uy, pad=2.0)
            p2 = clip_ray_to_rect(c2x, c2y, n_dst["w"], n_dst["h"], -ux, -uy, pad=4.0)

            lx = (p1[0] + p2[0]) / 2.0
            ly = (p1[1] + p2[1]) / 2.0

            computed_edges.append({
                "points": [[p1[0], p1[1]], [p2[0], p2[1]]],
                "label": e["label"],
                "lx": lx,
                "ly": ly
            })

        export_list.append({
            "filename": os.path.join(OUT_PNG_DIR, f'{diag["filename"]}.png'),
            "figure_title": diag["figure_title"],
            "canvas_w": diag.get("canvas_w", 1600),
            "canvas_h": diag.get("canvas_h", 1080),
            "boundaries": diag.get("boundaries", []),
            "nodes": diag["nodes"],
            "edges": computed_edges
        })

    json_path = os.path.join(OUT_PNG_DIR, "diagrams_render_spec.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(export_list, f, ensure_ascii=False, indent=2)
    print(f"[OK] Exported C4 straight-line render spec JSON: {json_path}")


if __name__ == "__main__":
    main()
