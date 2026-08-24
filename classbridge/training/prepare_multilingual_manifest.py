"""Validate and split consented ASR data without leaking speakers.

Input JSONL rows:
{"audio":"clips/a.wav","text":"Xin chào","language":"vi",
 "speaker_id":"teacher-01","accent":"vi-central"}

All recordings from one speaker are placed in exactly one split. This makes
validation measure generalisation to an unseen voice instead of memorisation.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path


LANGUAGE_ALIASES = {
    "english": "en",
    "vietnamese": "vi",
    "tiếng anh": "en",
    "tiếng việt": "vi",
    "en-us": "en",
    "en-gb": "en",
    "en-au": "en",
    "vi-vn": "vi",
    "vi": "vi",
    "en": "en",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/bilingual_sample_manifest.jsonl", help="Unsplit JSONL manifest")
    parser.add_argument("--train", default="data/train.jsonl")
    parser.add_argument("--validation", default="data/validation.jsonl")
    parser.add_argument("--validation-ratio", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--smoke-test", action="store_true", help="Bypass strict speaker-disjoint split for technical verification only")
    return parser.parse_args()



def normalized_language(value: object) -> str:
    language = str(value or "").strip().lower().replace("_", "-")
    language = LANGUAGE_ALIASES.get(language, language)
    if language.startswith("en"):
        language = "en"
    elif language.startswith("vi"):
        language = "vi"
    if not language or len(language) > 16:
        raise ValueError("Each row needs a short ISO language code, for example en or vi")
    if language not in {"en", "vi"}:
        raise ValueError("Only English and Vietnamese source rows are supported")
    return language


def read_rows(manifest_path: Path) -> list[dict]:
    rows: list[dict] = []
    seen_audio: set[str] = set()
    with manifest_path.open("r", encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid JSON on line {line_number}: {error}") from error
            text = " ".join(str(row.get("text", "")).split())
            if not text:
                raise ValueError(f"Line {line_number} has no verified transcript")
            audio_value = str(row.get("audio", "")).strip()
            if not audio_value:
                raise ValueError(f"Line {line_number} has no audio path")
            audio_path = Path(audio_value).expanduser()
            if not audio_path.is_absolute():
                candidate1 = (manifest_path.parent / audio_path).resolve()
                candidate2 = (manifest_path.parent.parent / audio_path).resolve()
                if candidate1.is_file():
                    audio_path = candidate1
                elif candidate2.is_file():
                    audio_path = candidate2
                else:
                    audio_path = candidate1
            if not audio_path.is_file():
                raise ValueError(f"Audio not found on line {line_number}: {audio_path}")

            audio_key = str(audio_path).casefold()
            if audio_key in seen_audio:
                raise ValueError(f"Duplicate audio on line {line_number}: {audio_path}")
            seen_audio.add(audio_key)
            speaker_id = str(row.get("speaker_id", "")).strip()
            if not speaker_id:
                raise ValueError(
                    f"Line {line_number} has no speaker_id; it is required to prevent voice leakage"
                )
            cleaned = dict(row)
            cleaned.update(
                audio=str(audio_path),
                text=text,
                language=normalized_language(row.get("language")),
                speaker_id=speaker_id,
                accent=str(row.get("accent", "unknown")).strip() or "unknown",
                region=str(row.get("region", "unknown")).strip() or "unknown",
            )
            rows.append(cleaned)
    if not rows:
        raise ValueError("The input manifest is empty")
    return rows


def split_by_speaker(
    rows: list[dict], validation_ratio: float, seed: int, smoke_test: bool = False
) -> tuple[list[dict], list[dict]]:
    if not 0.05 <= validation_ratio <= 0.40:
        raise ValueError("--validation-ratio must be between 0.05 and 0.40")
    by_speaker: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_speaker[row["speaker_id"]].append(row)

    speakers_by_language: dict[str, set[str]] = defaultdict(set)
    speakers_by_region: dict[str, set[str]] = defaultdict(set)
    total_by_language: Counter = Counter()
    total_by_region: Counter = Counter()
    for row in rows:
        speakers_by_language[row["language"]].add(row["speaker_id"])
        speakers_by_region[row["region"]].add(row["speaker_id"])
        total_by_language[row["language"]] += 1
        total_by_region[row["region"]] += 1

    vi_speakers = len(speakers_by_language.get("vi", set()))
    en_speakers = len(speakers_by_language.get("en", set()))

    print(f"📊 DATASET SPEAKER REPORT:")
    print(f"   - Vietnamese speakers: {vi_speakers} / 2 required")
    print(f"   - English speakers   : {en_speakers} / 2 required")

    insufficient = [
        language
        for language, speakers in speakers_by_language.items()
        if len(speakers) < 2
    ]

    if insufficient and not smoke_test:
        print("\n❌ INSUFFICIENT REAL SPEAKERS FOR PRODUCTION FINE-TUNING!")
        print("   Missing speakers per language:")
        if vi_speakers < 2:
            print(f"   - Vietnamese: need {2 - vi_speakers} more distinct real speaker(s)")
        if en_speakers < 2:
            print(f"   - English   : need {2 - en_speakers} more distinct real speaker(s)")
        print("\n👉 Please record real human audio using:")
        print("   python classbridge/training/record_classbridge_dataset.py\n")
        raise ValueError(
            f"Need at least two distinct real speakers for each language; missing: {', '.join(sorted(insufficient))}. Use --smoke-test ONLY for technical pipeline verification."
        )

    if insufficient and smoke_test:
        print("\n⚠️ WARNING: PIPELINE SMOKE-TEST MODE ENABLED!")
        print("   Bypassing strict speaker-disjoint validation for technical pipeline check.")
        print("   Do NOT use resulting model or WER scores as real production results!\n")
        # Split row-by-row for smoke testing
        rng = random.Random(seed)
        shuffled = list(rows)
        rng.shuffle(shuffled)
        val_count = max(1, int(len(shuffled) * validation_ratio))
        return shuffled[val_count:], shuffled[:val_count]


    # A validation split must leave at least one speaker in train for each
    # language and region. Keep the target per-language validation count at
    # least one clip and never exceed the number of available clips for that
    # language minus one.
    targets = {
        language: min(
            max(1, round(count * validation_ratio)),
            max(0, count - 1),
        )
        for language, count in total_by_language.items()
    }
    region_targets = {
        region: max(1, round(count * validation_ratio))
        for region, count in total_by_region.items()
    }
    rng = random.Random(seed)
    speaker_ids = list(by_speaker)
    rng.shuffle(speaker_ids)
    # Small groups first give the greedy split finer control over each language.
    # Sort deterministically after the seeded shuffle so repeated runs with the
    # same manifest and seed always produce the same validation choice.
    speaker_ids.sort(key=lambda speaker: (len(by_speaker[speaker]), speaker))
    validation_speakers: set[str] = set()
    validation_counts: Counter = Counter()
    validation_region_counts: Counter = Counter()

    for speaker_id in speaker_ids:
        contribution = Counter(row["language"] for row in by_speaker[speaker_id])
        region_contribution = Counter(row["region"] for row in by_speaker[speaker_id])
        helps = any(
            validation_counts[language] < targets[language]
            for language in contribution
        ) or any(
            validation_region_counts[region] < region_targets[region]
            for region in region_contribution
        )
        leaves_train_voice = all(
            len(speakers_by_language[language] - validation_speakers - {speaker_id}) >= 1
            for language in contribution
        ) and all(
            len(speakers_by_region[region] - validation_speakers - {speaker_id}) >= 1
            for region in region_contribution
        )
        if helps and leaves_train_voice:
            validation_speakers.add(speaker_id)
            validation_counts.update(contribution)
            validation_region_counts.update(region_contribution)

    # If the greedy pass misses a language or region entirely, force a speaker
    # from the missing group into validation while keeping at least one train
    # speaker for that group.
    missing_languages = [
        language
        for language, speakers in speakers_by_language.items()
        if validation_counts[language] < 1 and len(speakers) >= 2
    ]
    missing_regions = [
        region
        for region, speakers in speakers_by_region.items()
        if validation_region_counts[region] < 1 and len(speakers) >= 2
    ]
    if missing_languages or missing_regions:
        for speaker_id in speaker_ids:
            contribution = Counter(row["language"] for row in by_speaker[speaker_id])
            region_contribution = Counter(row["region"] for row in by_speaker[speaker_id])
            if not (
                any(language in missing_languages for language in contribution)
                or any(region in missing_regions for region in region_contribution)
            ):
                continue
            if all(
                len(speakers_by_language[language] - validation_speakers - {speaker_id}) >= 1
                for language in contribution
            ) and all(
                len(speakers_by_region[region] - validation_speakers - {speaker_id}) >= 1
                for region in region_contribution
            ):
                validation_speakers.add(speaker_id)
                validation_counts.update(contribution)
                validation_region_counts.update(region_contribution)
                missing_languages = [
                    language
                    for language in missing_languages
                    if validation_counts[language] < 1
                ]
                missing_regions = [
                    region
                    for region in missing_regions
                    if validation_region_counts[region] < 1
                ]
                if not missing_languages and not missing_regions:
                    break

    train_rows = [row for row in rows if row["speaker_id"] not in validation_speakers]
    validation_rows = [row for row in rows if row["speaker_id"] in validation_speakers]
    if not validation_rows:
        raise ValueError("Could not create a validation split; add more speakers")
    if any(validation_counts[language] < 1 for language in total_by_language):
        raise ValueError(
            "Could not reserve at least one validation speaker for every language; "
            "add more speakers or lower --validation-ratio"
        )
    if any(validation_region_counts[region] < 1 for region in total_by_region):
        raise ValueError(
            "Could not reserve at least one validation speaker for every region; "
            "add more speakers or lower --validation-ratio"
        )
    rng.shuffle(train_rows)
    rng.shuffle(validation_rows)
    return train_rows, validation_rows


def write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as target:
        for row in rows:
            target.write(json.dumps(row, ensure_ascii=False) + "\n")


def describe(name: str, rows: list[dict]) -> None:
    languages = Counter(row["language"] for row in rows)
    accents = Counter(row["accent"] for row in rows)
    regions = Counter(row["region"] for row in rows)
    speakers = {row["speaker_id"] for row in rows}
    print(
        f"{name}: {len(rows)} clips, {len(speakers)} speakers, "
        f"languages={dict(languages)}, accents={dict(accents)}, regions={dict(regions)}"
    )


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).resolve()
    rows = read_rows(input_path)
    train_rows, validation_rows = split_by_speaker(
        rows, args.validation_ratio, args.seed, smoke_test=args.smoke_test
    )

    write_rows(Path(args.train), train_rows)
    write_rows(Path(args.validation), validation_rows)
    describe("train", train_rows)
    describe("validation", validation_rows)


if __name__ == "__main__":
    main()
