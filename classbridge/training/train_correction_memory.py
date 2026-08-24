"""Learn safe phrase substitutions from verified ASR correction pairs.

Input JSONL row:
{"raw":"nhận dạng dọng nói","corrected":"nhận dạng giọng nói","language":"vi"}
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path


WORD_PATTERN = re.compile(r"\w+(?:['’-]\w+)*", re.UNICODE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Verified JSONL correction pairs")
    parser.add_argument(
        "--output",
        default=str(Path(__file__).resolve().parent.parent / "backend" / "ai-service" / "correction-memory.json"),
        help="Runtime correction-memory JSON",
    )
    parser.add_argument("--min-support", type=int, default=2)
    parser.add_argument("--min-confidence", type=float, default=0.8)
    parser.add_argument("--max-source-words", type=int, default=5)
    return parser.parse_args()


def words(text: str) -> list[str]:
    return WORD_PATTERN.findall(" ".join(str(text).strip().split()))


def extract_replacements(
    raw: str,
    corrected: str,
    maximum_source_words: int,
) -> list[tuple[str, str]]:
    raw_words = words(raw)
    corrected_words = words(corrected)
    matcher = SequenceMatcher(
        None,
        [word.casefold() for word in raw_words],
        [word.casefold() for word in corrected_words],
        autojunk=False,
    )
    replacements = []
    for operation, raw_start, raw_end, fixed_start, fixed_end in matcher.get_opcodes():
        if operation != "replace":
            continue
        source = raw_words[raw_start:raw_end]
        target = corrected_words[fixed_start:fixed_end]
        if not source or not target or len(source) > maximum_source_words:
            continue
        replacements.append((" ".join(source).casefold(), " ".join(target)))
    return replacements


def train(
    input_path: Path,
    minimum_support: int,
    minimum_confidence: float,
    maximum_source_words: int,
) -> list[dict]:
    candidates: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    with input_path.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            language = str(row.get("language", "vi")).lower()
            if language not in {"en", "vi"}:
                raise ValueError(f"Unsupported language on line {line_number}: {language}")
            raw = str(row.get("raw", ""))
            corrected = str(row.get("corrected", ""))
            if not raw or not corrected:
                raise ValueError(f"Missing raw/corrected text on line {line_number}")
            for wrong, fixed in extract_replacements(
                raw, corrected, maximum_source_words
            ):
                candidates[(language, wrong)][fixed] += 1

    rules = []
    for (language, source), targets in candidates.items():
        target, support = targets.most_common(1)[0]
        total = sum(targets.values())
        confidence = support / total
        if support < minimum_support or confidence < minimum_confidence:
            continue
        rules.append(
            {
                "language": language,
                "source": source,
                "target": target,
                "support": support,
                "confidence": round(confidence, 4),
            }
        )
    rules.sort(key=lambda rule: (-rule["support"], rule["language"], rule["source"]))
    return rules


def main() -> None:
    args = parse_args()
    if args.min_support < 2:
        raise ValueError("--min-support must be at least 2 to avoid one-off rewrites")
    if not 0.8 <= args.min_confidence <= 1.0:
        raise ValueError("--min-confidence must be between 0.8 and 1.0")
    rules = train(
        Path(args.input),
        args.min_support,
        args.min_confidence,
        args.max_source_words,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps({"version": 1, "rules": rules}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(rules)} verified correction rules to {output}")


if __name__ == "__main__":
    main()

