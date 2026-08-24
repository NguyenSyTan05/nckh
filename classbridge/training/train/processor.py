"""
train.processor

Processing logic: extract_samples uses backend.utils for helpers/constants.
"""
from __future__ import annotations

import glob
import json
import time
from pathlib import Path
import sys

import pyarrow.parquet as pq
import pandas as pd

from backend.utils import (
    VIMD_DATA_DIR,
    OUT_SAMPLES,
    OUT_MANIFESTS,
    MANIFEST_PATH,
    META_COLS,
    MIN_FREE_GB,
    safe_name,
    parse_gender,
    check_disk_space,
    count_shard_rows,
)


def extract_samples(
    split: str,
    region_filter: str | None,
    tinh_filter: str | None,
    n_max: int,
    resume: bool = False,
    dry_run: bool = False,
) -> int:
    all_files = sorted(glob.glob(str(VIMD_DATA_DIR / "*.parquet")))
    if split == "train":
        shards = [f for f in all_files if Path(f).name.startswith("train")]
    elif split == "test":
        shards = [f for f in all_files if Path(f).name.startswith("test")]
    else:
        shards = all_files

    print(f"\n ViMD split={split!r}  -> {len(shards)} shard(s) tim thay")
    print(f"   Region filter : {region_filter or 'Tat ca'}")
    print(f"   Tinh filter   : {tinh_filter or 'Tat ca'}")
    print(f"   Gioi han mau  : {n_max if n_max > 0 else 'KHONG GIOI HAN (lay het)'}")
    print(f"   Resume mode   : {'Bat - bo qua file da co' if resume else 'Tat'}")
    print(f"   Dry-run       : {'Bat - khong ghi file' if dry_run else 'Tat'}")
    print(f"   Output        : {OUT_SAMPLES}\n")

    # Kiểm tra dung lượng ổ đĩa
    free_gb = check_disk_space(OUT_SAMPLES)
    print(f"   Dung luong o dia con trong: {free_gb:.1f} GB")
    if free_gb < MIN_FREE_GB and not dry_run:
        print(f"   [CANH BAO] Chi con {free_gb:.1f} GB. Toi thieu can {MIN_FREE_GB} GB.")
        print(f"   Tiep tuc? (y/n): ", end="", flush=True)
        try:
            ans = input().strip().lower()
            if ans != "y":
                sys.exit("Da huy.")
        except (EOFError, KeyboardInterrupt):
            sys.exit("Huy do moi truong khong tuong tac.")

    # Nếu dry-run: ước tính tổng số hàng
    if dry_run:
        print("   [DRY-RUN] Dang dem tong so hang...")
        total_rows = 0
        for sp in shards:
            r = count_shard_rows(sp, region_filter, tinh_filter)
            total_rows += r
        estimate_gb = total_rows * 3.5 / 1024  # ước tính ~3.5MB/file WAV trung bình
        print(f"\n   -> Uoc tinh tong: {total_rows:,} mau")
        print(f"   -> Uoc tinh dung luong WAV: ~{estimate_gb:.1f} GB")
        print(f"   -> Dung luong con trong    : {free_gb:.1f} GB")
        if estimate_gb > free_gb:
            print(f"   [CANH BAO] Khong du dung luong! Can them ~{estimate_gb - free_gb:.1f} GB.")
        return total_rows

    # Tải danh sách file đã có (để resume)
    existing_wavs: set[str] = set()
    if resume:
        existing_wavs = {f.stem for f in OUT_SAMPLES.glob("vimd_*.wav")}
        print(f"   [RESUME] Phat hien {len(existing_wavs):,} file da co trong thu muc samples.")

    saved = 0
    skipped = 0
    manifest = []
    t_start = time.perf_counter()

    for shard_idx, shard_path in enumerate(shards, 1):
        if n_max > 0 and (saved + skipped) >= n_max:
            print(f"\n  Dat gioi han tổng {n_max} mau (gom ca mau cu & moi). Dung lai.")
            break

        shard_name = Path(shard_path).name

        # Kiểm tra dung lượng mỗi 10 shard
        if shard_idx % 10 == 0:
            free_gb = check_disk_space(OUT_SAMPLES)
            if free_gb < 1.0:
                print(f"\n  [DUNG] O dia chi con {free_gb:.2f} GB! Dang luu manifest va thoat...")
                break

        try:
            df_meta = pq.read_table(shard_path, columns=META_COLS).to_pandas()
        except Exception as e:
            print(f"  [WARN] Bo qua {shard_name}: {e}")
            continue

        # Lọc
        mask = pd.Series([True] * len(df_meta))
        if region_filter:
            mask &= df_meta["region"].str.lower() == region_filter.lower()
        if tinh_filter:
            mask &= df_meta["province_name"].str.lower() == tinh_filter.lower()

        indices = df_meta[mask].index.tolist()
        if not indices:
            continue

        # Đọc cột audio
        try:
            df_audio = pq.read_table(shard_path, columns=["audio"]).to_pandas()
        except Exception as e:
            print(f"  [WARN] Khong doc duoc audio tu {shard_name}: {e}")
            continue

        shard_saved = 0
        for idx in indices:
            if n_max > 0 and (saved + skipped) >= n_max:
                break

            row_meta = df_meta.iloc[idx]
            row_audio = df_audio.iloc[idx]

            province = safe_name(row_meta["province_name"])
            region = safe_name(row_meta["region"])
            speaker = safe_name(str(row_meta["speakerID"]))
            orig_fname = Path(str(row_meta["filename"])).stem
            text = str(row_meta["text"])
            gender = parse_gender(row_meta.get("gender"))

            out_stem = f"vimd_{region}_{province}_{speaker}_{orig_fname}"
            out_wav = OUT_SAMPLES / f"{out_stem}.wav"
            out_txt = OUT_SAMPLES / f"{out_stem}.txt"

            # Resume: bỏ qua file đã có
            if resume and out_stem in existing_wavs:
                skipped += 1
                continue

            # Lấy audio bytes
            audio_val = row_audio["audio"]
            if isinstance(audio_val, dict):
                audio_bytes = audio_val.get("bytes") or audio_val.get("array")
            elif isinstance(audio_val, (bytes, bytearray)):
                audio_bytes = audio_val
            else:
                audio_bytes = None

            if not audio_bytes:
                continue

            # Ghi WAV
            with open(out_wav, "wb") as wf:
                wf.write(audio_bytes if isinstance(audio_bytes, (bytes, bytearray)) else bytes(audio_bytes))

            # Ghi metadata .txt
            with open(out_txt, "w", encoding="utf-8") as tf:
                tf.write(f"file     : {out_wav.name}\n")
                tf.write(f"text     : {text}\n")
                tf.write(f"speaker  : {row_meta['speakerID']}\n")
                tf.write(f"gender   : {gender}\n")
                tf.write(f"region   : {row_meta['region']}\n")
                tf.write(f"province : {row_meta['province_name']}\n")
                tf.write(f"split    : {split}\n")
                tf.write(f"shard    : {shard_name}\n")

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

            existing_wavs.add(out_stem)
            saved += 1
            shard_saved += 1

        # Ghi manifest theo từng shard để không mất dữ liệu nếu bị dừng giữa chừng
        if manifest:
            with open(MANIFEST_PATH, "a", encoding="utf-8") as mf:
                for entry in manifest:
                    mf.write(json.dumps(entry, ensure_ascii=False) + "\n")
            manifest.clear()

        elapsed = time.perf_counter() - t_start
        free_gb = check_disk_space(OUT_SAMPLES)
        eta_s = (len(shards) - shard_idx) * (elapsed / shard_idx) if shard_idx > 0 else 0
        print(
            f"  [{shard_idx:3d}/{len(shards)}] {shard_name} | "
            f"+{shard_saved} moi | Tong moi: {saved:,} | "
            f"Bo qua cu: {skipped:,} | "
            f"O dia: {free_gb:.1f}GB | "
            f"ETA: {int(eta_s//60)}m{int(eta_s%60)}s"
        )

        if n_max > 0 and (saved + skipped) >= n_max:
            print(f"\n  Dat gioi han {n_max} mau. Dung lai.")
            break

    elapsed_total = time.perf_counter() - t_start
    print(f"\n  Thoi gian tong cong: {int(elapsed_total//60)}m{int(elapsed_total%60)}s")
    return saved
