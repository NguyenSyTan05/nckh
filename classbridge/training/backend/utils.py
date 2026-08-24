"""
backend.utils

Constants and helper utilities for ViMD processing.
"""
from __future__ import annotations

import sys
import shutil
from pathlib import Path
import json

# Workspace root (modules live in subfolder; root is parent of package)
_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent

# === Đường dẫn cố định =======================================================
VIMD_DATA_DIR = _ROOT / "ViMD_Dataset" / "data"
OUT_SAMPLES = _ROOT / "classbridge" / "data" / "samples"
OUT_MANIFESTS = _ROOT / "classbridge" / "data" / "manifests"

OUT_SAMPLES.mkdir(parents=True, exist_ok=True)
OUT_MANIFESTS.mkdir(parents=True, exist_ok=True)

MANIFEST_PATH = OUT_MANIFESTS / "vimd_samples.jsonl"

META_COLS = ["region", "province_code", "province_name",
             "filename", "text", "speakerID", "gender"]

MIN_FREE_GB = 5.0   # Yêu cầu tối thiểu 5GB trống trước khi chạy


def safe_name(s: str) -> str:
    """Chuyển tên tỉnh / region thành tên file an toàn."""
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in str(s)).strip("_")


def parse_gender(g_val: object) -> str:
    try:
        import pandas as pd
    except Exception:
        # Fallback simple handling if pandas not available
        if g_val is None:
            return "khong_xac_dinh"
        return str(g_val).lower()

    if g_val is None or pd.isna(g_val):
        return "khong_xac_dinh"
    if g_val in [1, 1.0, "1", "1.0", "nam", "male", "M", "m"]:
        return "nam"
    if g_val in [0, 0.0, "0", "0.0", "nu", "nữ", "female", "F", "f"]:
        return "nu"
    return str(g_val).lower()


def check_disk_space(path: Path) -> float:
    """Trả về GB trống trên ổ chứa path."""
    usage = shutil.disk_usage(path)
    free_gb = usage.free / 1024**3
    return free_gb


def count_shard_rows(shard_path: str, region_filter: str | None, tinh_filter: str | None) -> int:
    """Đếm số hàng khớp trong shard (chỉ đọc metadata, không load audio)."""
    try:
        import pyarrow.parquet as pq
        df = pq.read_table(shard_path, columns=META_COLS).to_pandas()
        mask = df.index.to_series().apply(lambda _: True)
        if region_filter:
            mask &= df["region"].str.lower() == region_filter.lower()
        if tinh_filter:
            mask &= df["province_name"].str.lower() == tinh_filter.lower()
        return int(mask.sum())
    except Exception:
        return 0
