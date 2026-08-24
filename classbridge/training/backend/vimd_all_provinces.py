"""
Copied vimd_all_provinces into backend package.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import glob
import shutil
import time
from collections import defaultdict
from pathlib import Path

# Ensure stdout/stderr use utf-8 to avoid UnicodeEncodeError on Windows consoles
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

try:
    import pyarrow.parquet as pq
    import pandas as pd
except ImportError as e:
    sys.exit(f"Thieu thu vien: {e}\n   Chay: pip install pyarrow pandas")

# === Đường dẫn ===============================================================
_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
VIMD_DATA_DIR = _ROOT / "ViMD_Dataset" / "data"
OUT_SAMPLES   = _ROOT / "classbridge" / "data" / "samples"
OUT_MANIFESTS = _ROOT / "classbridge" / "data" / "manifests"

OUT_SAMPLES.mkdir(parents=True, exist_ok=True)
OUT_MANIFESTS.mkdir(parents=True, exist_ok=True)

MANIFEST_PATH = OUT_MANIFESTS / "vimd_all_provinces.jsonl"

META_COLS = ["region", "province_code", "province_name",
             "filename", "text", "speakerID", "gender"]

MIN_FREE_GB = 2.0


def safe_name(s: str) -> str:
    # pyrefly: ignore [unnecessary-type-conversion]
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in str(s)).strip("_")


def parse_gender(g_val: object) -> str:
    if g_val is None or pd.isna(g_val):
        return "khong_xac_dinh"
    if g_val in [1, 1.0, "1", "1.0", "nam", "male", "M", "m"]:
        return "nam"
    if g_val in [0, 0.0, "0", "0.0", "nu", "nữ", "female", "F", "f"]:
        return "nu"
    return str(g_val).lower()


def scan_provinces(shards: list[str]) -> dict[str, list[str]]:
    print("\n  [SCAN] Dang quet danh sach tinh tu dataset (chi doc metadata)...")
    province_shards: dict[str, list[str]] = defaultdict(list)
    for i, sp in enumerate(shards, 1):
        try:
            tbl = pq.read_table(sp, columns=["province_name"])
            provinces_in_shard = tbl["province_name"].drop_null().unique().to_pylist()
            for p in provinces_in_shard:
                province_shards[str(p)].append(sp)
        except Exception as e:
            print(f"  [WARN] {Path(sp).name}: {e}")
        if i % 20 == 0 or i == len(shards):
            print(f"  [{i:3d}/{len(shards)}] Tim thay {len(province_shards)} tinh cho den nay...")
    return dict(province_shards)


def extract_for_province(
    province_name: str,
    shards_for_province: list[str],
    n_per_province: int,
    split: str,
    existing_stems: set[str],
    resume: bool,
    dry_run: bool = False,
) -> tuple[int, int, list[dict]]:
    saved_new     = 0
    already_exist = 0
    manifest      = []

    for shard_path in shards_for_province:
        if n_per_province > 0 and (saved_new + already_exist) >= n_per_province:
            break

        shard_name = Path(shard_path).name
        try:
            df_meta = pq.read_table(shard_path, columns=META_COLS).to_pandas()
        except Exception:
            continue

        mask    = df_meta["province_name"].astype(str) == province_name
        indices = df_meta[mask].index.tolist()
        if not indices:
            continue

        try:
            df_audio = pq.read_table(shard_path, columns=["audio"]).to_pandas()
        except Exception:
            continue

        for idx in indices:
            if n_per_province > 0 and (saved_new + already_exist) >= n_per_province:
                break

            row_meta  = df_meta.iloc[idx]
            row_audio = df_audio.iloc[idx]

            province_s = safe_name(row_meta["province_name"])
            region_s   = safe_name(row_meta["region"])
            speaker    = safe_name(str(row_meta["speakerID"]))
            orig_fname = Path(str(row_meta["filename"])).stem
            text       = str(row_meta["text"])
            gender     = parse_gender(row_meta.get("gender"))

            out_stem = f"vimd_{region_s}_{province_s}_{speaker}_{orig_fname}"
            out_wav  = OUT_SAMPLES / f"{out_stem}.wav"
            out_txt  = OUT_SAMPLES / f"{out_stem}.txt"

            # Resume: bỏ qua nếu đã có
            if resume and out_stem in existing_stems:
                already_exist += 1
                continue

            # Lấy audio bytes
            audio_val = row_audio["audio"]
            if isinstance(audio_val, dict):
                audio_bytes = audio_val.get("bytes") or audio_val.get("array")
            # pyrefly: ignore [unbound-name]
            elif isinstance(audio_bytes, (bytes, bytearray)):
                audio_bytes = audio_val
            else:
                audio_bytes = None

            if not audio_bytes:
                continue

            # Write files unless dry-run
            if not dry_run:
                try:
                    with open(out_wav, "wb") as wf:
                        wf.write(audio_bytes if isinstance(audio_bytes, (bytes, bytearray)) else bytes(audio_bytes))

                    with open(out_txt, "w", encoding="utf-8") as tf:
                        tf.write(f"file     : {out_wav.name}\n")
                        tf.write(f"text     : {text}\n")
                        tf.write(f"speaker  : {row_meta['speakerID']}\n")
                        tf.write(f"gender   : {gender}\n")
                        tf.write(f"region   : {row_meta['region']}\n")
                        tf.write(f"province : {row_meta['province_name']}\n")
                        tf.write(f"split    : {split}\n")
                        tf.write(f"shard    : {shard_name}\n")
                except Exception as e:
                    print(f"  [WARN] Khong the ghi file cho {out_stem}: {e}")
                    continue
            else:
                print(f"  [DRY] would write: {out_wav} ({len(audio_bytes)//2} samples)")
                print(f"  [DRY] would write metadata: {out_txt}")

            manifest.append({
                "audio_path": str(out_wav).replace("\\", "/"),
                "text": text,
                "speaker_id": str(row_meta["speakerID"]),
                "gender": gender,
                "region": str(row_meta["region"]),
                "province": str(row_meta["province_name"]),
                "language": "vi",
                "split": split,
                "source": "ViMD",
            })

            existing_stems.add(out_stem)
            saved_new += 1

    return saved_new, already_exist, manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Trich xuat audio ViMD du 63 tinh thanh -> classbridge/backend/data/samples/"
    )
    parser.add_argument("--split",         default="train", choices=["train", "test", "both"],
                        help="Split su dung (mac dinh: train)")
    parser.add_argument("--per-province",  type=int, default=10,
                        help="So mau moi tinh (0 = lay het, mac dinh: 10)")
    parser.add_argument("--resume",        action="store_true",
                        help="Bo qua file WAV da ton tai")
    parser.add_argument("--list-provinces", action="store_true",
                        help="Chi liet ke tinh co trong dataset, khong trich xuat")
    parser.add_argument("--clear-manifest", action="store_true",
                        help="Xoa manifest cu truoc khi chay")
    parser.add_argument("--dry-run", action="store_true", help="Không ghi file, chỉ mô phỏng (test)")
    args = parser.parse_args()

    print("=" * 65)
    print("  ClassBridge - ViMD Dataset -> 63 Tinh Thanh Extractor")
    print("=" * 65)

    if not VIMD_DATA_DIR.exists():
        sys.exit(f"Khong tim thay: {VIMD_DATA_DIR}")

    if args.clear_manifest and MANIFEST_PATH.exists():
        MANIFEST_PATH.unlink()
        print(f"  Da xoa manifest cu.")

    # Chọn shards
    all_files = sorted(glob.glob(str(VIMD_DATA_DIR / "*.parquet")))
    if args.split == "train":
        shards = [f for f in all_files if Path(f).name.startswith("train")]
    elif args.split == "test":
        shards = [f for f in all_files if Path(f).name.startswith("test")]
    else:
        shards = all_files

    print(f"\n  Split      : {args.split} ({len(shards)} shards)")
    print(f"  Mau/tinh   : {args.per_province if args.per_province > 0 else 'Tat ca'}")
    print(f"  Resume     : {'Bat' if args.resume else 'Tat'}")

    # Quét tên tỉnh
    province_shards = scan_provinces(shards)
    provinces = sorted(province_shards.keys())

    print(f"\n  -> Tim thay {len(provinces)} tinh/thanh pho trong dataset:")
    for i, p in enumerate(provinces, 1):
        n_shards = len(province_shards[p])
        print(f"     {i:2d}. {p:25s}  ({n_shards} shard(s))")

    if args.list_provinces:
        print("\n  [list-provinces] Hoan tat. Khong trich xuat.")
        return

    # Kiểm tra ổ đĩa
    free_gb = shutil.disk_usage(OUT_SAMPLES).free / 1024**3
    print(f"\n  Dung luong o dia con trong: {free_gb:.1f} GB")
    if free_gb < MIN_FREE_GB:
        print(f"  [CANH BAO] Rat it dung luong! Chi con {free_gb:.1f} GB.")

    # Resume: tải danh sách đã có
    existing_stems: set[str] = set()
    if args.resume:
        existing_stems = {f.stem for f in OUT_SAMPLES.glob("vimd_*.wav")}
        print(f"  [RESUME] {len(existing_stems):,} file WAV da co trong thu muc samples.")

    print(f"\n  Bat dau trich xuat...\n")
    t_start           = time.perf_counter()
    total_saved_new   = 0
    total_already     = 0
    province_summary: list[tuple[str, int, int]] = []

    for p_idx, province in enumerate(provinces, 1):
        try:
            p_shards = province_shards[province]

            # Kiểm tra ổ đĩa mỗi 10 tỉnh
            if p_idx % 10 == 0:
                free_gb = shutil.disk_usage(OUT_SAMPLES).free / 1024**3
                if free_gb < MIN_FREE_GB:
                    print(f"\n  [DUNG] O dia chi con {free_gb:.2f} GB! Dung.")
                    break

            saved_new, already_exist, manifest_entries = extract_for_province(
                province_name=province,
                shards_for_province=p_shards,
                n_per_province=args.per_province,
                split=args.split,
                existing_stems=existing_stems,
                resume=args.resume,
                dry_run=args.dry_run,
            )

            total_saved_new += saved_new
            total_already   += already_exist
            province_summary.append((province, saved_new, already_exist))

            # Ghi manifest ngay sau mỗi tỉnh
            if manifest_entries:
                if not args.dry_run:
                    with open(MANIFEST_PATH, "a", encoding="utf-8") as mf:
                        for entry in manifest_entries:
                            mf.write(json.dumps(entry, ensure_ascii=False) + "\n")
                else:
                    for entry in manifest_entries[:3]:
                        print(f"    [DRY] manifest: {entry['audio_path']} ...")

            elapsed = time.perf_counter() - t_start
            free_gb = shutil.disk_usage(OUT_SAMPLES).free / 1024**3
            status_str = f"+{saved_new:3d} moi" if not args.resume else f"+{saved_new:3d} moi, {already_exist:3d} cu"
            print(
                f"  [{p_idx:2d}/{len(provinces)}] {province:25s}: "
                f"{status_str:18s} | "
                f"Tong moi: {total_saved_new:,} | "
                f"O dia: {free_gb:.1f}GB | "
                f"{int(elapsed//60)}m{int(elapsed%60)}s"
            )
        except Exception as e:
            print(f"  [ERROR] Loi khi xet province {province}: {e}")
            continue

    elapsed_total = time.perf_counter() - t_start
    print("\n" + "=" * 65)
    print(f"  TONG KET - {len(province_summary)} TINH:")
    for province, cnt_new, cnt_exist in province_summary:
        tot = cnt_new + cnt_exist
        if tot > 0:
            detail = f"{cnt_new:4d} moi" if not args.resume else f"{cnt_new:3d} moi, {cnt_exist:3d} cu"
            st_flag = "OK"
        else:
            detail = "0 mau"
            st_flag = "KHONG CO MAU"
        print(f"    {province:28s}: {detail:18s}  [{st_flag}]")
    print("=" * 65)
    print(f"  Tong da xuat mới  : {total_saved_new:,} file WAV")
    if args.resume:
        print(f"  Tong da bo qua    : {total_already:,} file WAV (da co san)")
    print(f"  Thoi gian         : {int(elapsed_total//60)}m{int(elapsed_total%60)}s")
    print(f"  Output            : {OUT_SAMPLES}")
    if args.dry_run:
        print("  (Dry-run) Khong co file nao duoc ghi.\n  Manifest chi duoc in preview.")
    else:
        print(f"  Manifest          : {MANIFEST_PATH}")
    print("=" * 65)


if __name__ == "__main__":
    main()
