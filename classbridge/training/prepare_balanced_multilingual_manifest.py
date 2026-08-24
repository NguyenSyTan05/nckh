from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Iterable


def detect_language(source: str) -> str:
    s = (source or "").strip().lower()
    if s.startswith("en:"):
        return "en"
    if s.startswith("vi:"):
        return "vi"
    if s.startswith("english") or s.startswith("the "):
        return "en"
    return "vi" if any(ch in s for ch in "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ") else "en"


def read_rows(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            source = str(obj.get("source") or obj.get("src") or "").strip()
            target = str(obj.get("target") or obj.get("tgt") or "").strip()
            if not source or not target:
                continue
            rows.append({
                "source": source,
                "target": target,
                "direction": str(obj.get("direction") or ("en2vi" if detect_language(source) == "en" else "vi2en")).strip(),
            })
    return rows


def build_balanced_manifest(rows: Iterable[dict]) -> list[dict]:
    region_cycle = {
        "vi": ["north", "central", "south", "mixed"],
        "en": ["us", "uk", "india", "australia", "vietnam", "mixed"],
    }
    accent_cycle = {
        "vi": {
            "north": "vi_north_hanoi",
            "central": "vi_central_hue",
            "south": "vi_south_hcm",
            "mixed": "vi_mixed",
        },
        "en": {
            "us": "en_us",
            "uk": "en_uk",
            "india": "en_india",
            "australia": "en_au",
            "vietnam": "en_vietnamese",
            "mixed": "en_mixed",
        },
    }

    balanced: list[dict] = []
    counts = defaultdict(int)
    for idx, row in enumerate(rows):
        source = str(row["source"])
        language = detect_language(source)
        region = region_cycle[language][idx % len(region_cycle[language])]
        accent = accent_cycle[language][region]
        counts[(language, region)] += 1
        speaker = f"{language}_{region}_{counts[(language, region)]:02d}"
        balanced.append({
            "source": source,
            "target": str(row["target"]),
            "direction": str(row.get("direction") or ("en2vi" if language == "en" else "vi2en")),
            "language": language,
            "region": region,
            "accent": accent,
            "speaker_id": speaker,
            "dataset": "balanced_multilingual",
        })
    return balanced


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a balanced regional EN/VI training manifest.")
    parser.add_argument("--input", type=Path, default=Path("data/manifests/translation_pairs_fixed.jsonl"), help="Input JSONL translation pairs")
    parser.add_argument("--output", type=Path, default=Path("data/manifests/translation_balanced.jsonl"), help="Output balanced manifest")
    args = parser.parse_args()

    rows = read_rows(args.input)
    if not rows:
        raise SystemExit(f"No valid rows found in {args.input}")

    balanced = build_balanced_manifest(rows)
    write_jsonl(args.output, balanced)

    by_language = defaultdict(int)
    by_region = defaultdict(int)
    for row in balanced:
        by_language[row["language"]] += 1
        by_region[row["region"]] += 1

    print(f"Generated {len(balanced)} balanced rows to {args.output}")
    print(f"Language counts: {dict(by_language)}")
    print(f"Region counts: {dict(by_region)}")


if __name__ == "__main__":
    main()
