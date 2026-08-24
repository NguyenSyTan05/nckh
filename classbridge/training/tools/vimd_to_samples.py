"""Convert ViMD parquet rows into WAV samples for ClassBridge training."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from backend.utils import MANIFEST_PATH, VIMD_DATA_DIR
from train.processor import extract_samples


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Chuyen ViMD_Dataset (parquet) thanh mau WAV de train ClassBridge"
    )
    parser.add_argument("--split", default="train", choices=["train", "test", "both"])
    parser.add_argument("--region", default=None)
    parser.add_argument("--tinh", default=None)
    parser.add_argument("--n", type=int, default=20, help="So mau toi da; 0 la lay het")
    parser.add_argument("--clear-manifest", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.clear_manifest and MANIFEST_PATH.exists():
        MANIFEST_PATH.unlink()

    if not VIMD_DATA_DIR.exists():
        sys.exit(f"Khong tim thay: {VIMD_DATA_DIR}")

    total = extract_samples(
        split=args.split,
        region_filter=args.region,
        tinh_filter=args.tinh,
        n_max=args.n,
        resume=args.resume,
        dry_run=args.dry_run,
    )
    action = "Uoc tinh" if args.dry_run else "Da xuat"
    print(f"{action}: {total:,} mau")
    if not args.dry_run:
        print(f"Thu muc chay: {Path.cwd()}")
        print(f"Manifest: {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
