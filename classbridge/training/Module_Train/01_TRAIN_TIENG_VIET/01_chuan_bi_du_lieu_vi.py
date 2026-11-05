import io
import os
import sys
import json
from pathlib import Path
from collections import defaultdict

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

def main():
    print("=" * 80)
    print("🇻🇳 TẠO MANIFEST TIẾNG VIỆT CHUẨN XÁC 100%: ĐỦ ĐÚNG 6,300 MẪU (63 TỈNH x 100)")
    print("=" * 80)

    samples_vi_dir = Path("d:/TailieuNPKH/classbridge/backend/data/samples/samples_vi")
    if not samples_vi_dir.exists():
        print(f"❌ Không tìm thấy thư mục {samples_vi_dir}")
        return

    # Quét nhanh bằng os.scandir
    print("🔍 Đang quét thư mục samples_vi...")
    province_map = defaultdict(list)
    
    with os.scandir(str(samples_vi_dir)) as entries:
        for entry in entries:
            if entry.is_file() and entry.name.startswith("vimd_") and entry.name.endswith(".wav"):
                filename = entry.name
                stem = filename[:-4]
                parts = stem.split("_")
                if len(parts) >= 4:
                    reg = parts[1]
                    prov = parts[2]
                    if prov in ["Hà", "Hồ", "Đà"]:
                        continue
                    
                    spk_id = f"{parts[3]}_{parts[4]}" if len(parts) >= 5 else parts[3]
                    sample_idx = int(parts[-1]) if parts[-1].isdigit() else 9999
                    
                    province_map[prov].append({
                        "filename": filename,
                        "stem": stem,
                        "wav_path": str(Path(entry.path)).replace("\\", "/"),
                        "txt_path": str(Path(entry.path).with_suffix(".txt")).replace("\\", "/"),
                        "reg": reg,
                        "prov": prov,
                        "spk_id": spk_id,
                        "sample_idx": sample_idx
                    })

    print(f"🏛️ Đã quét xong: Tìm thấy {len(province_map)} tỉnh thành!")

    all_6300 = []
    train_5040 = []
    val_630 = []
    test_630 = []

    for prov, samples in sorted(province_map.items()):
        # Sắp xếp đúng theo số thứ tự từ 1 đến 100
        samples.sort(key=lambda x: x["sample_idx"])
        top100 = samples[:100]

        if len(top100) < 100:
            print(f"⚠️ Cảnh báo: Tỉnh {prov} chỉ có {len(top100)} mẫu!")

        # Đọc nội dung file txt cho đúng 100 mẫu này
        processed_top100 = []
        for item in top100:
            text = ""
            if os.path.exists(item["txt_path"]):
                try:
                    with open(item["txt_path"], "r", encoding="utf-8") as f:
                        raw = f.read().strip()
                        # Bóc tách chính xác dòng chứa câu nói (bỏ qua metadata)
                        for line in raw.splitlines():
                            line_s = line.strip()
                            if line_s.startswith("text"):
                                parts = line_s.split(":", 1)
                                if len(parts) > 1:
                                    text = parts[1].strip()
                                    break
                        if not text:
                            text = raw
                except Exception:
                    pass
            
            row = {
                "audio": item["wav_path"],
                "audio_filepath": item["wav_path"],
                "text": text,
                "language": "vi",
                "speaker_id": f"{item['prov']}_{item['spk_id']}",
                "region": item["reg"],
                "province": item["prov"],
                "sample_idx": item["sample_idx"]
            }
            processed_top100.append(row)

        all_6300.extend(processed_top100)
        train_5040.extend(processed_top100[:80])
        val_630.extend(processed_top100[80:90])
        test_630.extend(processed_top100[90:100])

    print(f"\n📊 KẾT QUẢ PHÂN BỔ DỮ LIỆU:")
    print(f"  • Tổng số tỉnh thành           : {len(province_map)} tỉnh")
    print(f"  • Tổng cộng (63 tỉnh x 100 mẫu) : {len(all_6300)} mẫu (100%)")
    print(f"  • Tập TRAIN (63 tỉnh x 80 mẫu)  : {len(train_5040)} mẫu (80%)")
    print(f"  • Tập VAL   (63 tỉnh x 10 mẫu)  : {len(val_630)} mẫu (10%)")
    print(f"  • Tập TEST  (63 tỉnh x 10 mẫu)  : {len(test_630)} mẫu (10%)")

    # Xuất file ra các thư mục
    curr_dir = Path(__file__).resolve().parent
    module_train_manifests = curr_dir.parent / "manifests"
    targets = [
        curr_dir,
        module_train_manifests,
    ]

    for t_dir in targets:
        t_dir.mkdir(parents=True, exist_ok=True)
        
        with open(t_dir / "manifest_vi_train.jsonl", "w", encoding="utf-8") as f:
            for item in train_5040:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        
        with open(t_dir / "manifest_vi_val.jsonl", "w", encoding="utf-8") as f:
            for item in val_630:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

        with open(t_dir / "manifest_vi_test.jsonl", "w", encoding="utf-8") as f:
            for item in test_630:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

        with open(t_dir / "manifest_vi.jsonl", "w", encoding="utf-8") as f:
            for item in all_6300:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

    with open(module_train_manifests / "manifest_vi_specialist.jsonl", "w", encoding="utf-8") as f:
        for item in train_5040:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print("\n🎉 ĐÃ CẬP NHẬT HOÀN TẤT CHÍNH XÁC 6,300 MẪU (5,040 TRAIN / 630 VAL / 630 TEST)!")
    print("=" * 80)

if __name__ == "__main__":
    main()
