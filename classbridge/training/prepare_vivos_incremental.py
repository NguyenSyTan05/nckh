"""Prepare a speaker-balanced VIVOS increment without leaking validation speakers."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import tarfile
from collections import defaultdict
from pathlib import Path

import soundfile as sf

EXPECTED_SHA256 = "147477f7a7702cbafc2ee3808d1c142989d0dbc8d9fce8e07d5f329d5119e4ca"


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True)
    parser.add_argument("--extract-dir", required=True)
    parser.add_argument("--train-output", required=True)
    parser.add_argument("--validation-output", required=True)
    parser.add_argument("--max-per-speaker", type=int, default=12)
    parser.add_argument("--validation-speakers", type=int, default=8)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_extract(archive: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    with tarfile.open(archive, "r:gz") as bundle:
        for member in bundle.getmembers():
            target = (destination / member.name).resolve()
            if root not in target.parents and target != root:
                raise ValueError(f"Unsafe archive member: {member.name}")
        bundle.extractall(destination)


def load_prompts(root: Path) -> dict[str, str]:
    prompts: dict[str, str] = {}
    for prompt_file in root.rglob("prompts.txt"):
        for line in prompt_file.read_text(encoding="utf-8").splitlines():
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2:
                prompts[parts[0]] = parts[1].strip()
    return prompts


def main() -> None:
    args = arguments()
    archive = Path(args.archive).resolve()
    extract_dir = Path(args.extract_dir).resolve()
    actual = sha256(archive)
    if actual != EXPECTED_SHA256:
        raise ValueError(f"VIVOS checksum mismatch: {actual}")
    safe_extract(archive, extract_dir)
    prompts = load_prompts(extract_dir)

    rows_by_speaker: dict[str, list[dict[str, object]]] = defaultdict(list)
    for audio in sorted(extract_dir.rglob("*.wav")):
        utterance_id = audio.stem
        text = prompts.get(utterance_id, "").strip()
        if not text:
            continue
        speaker = audio.parent.name
        info = sf.info(str(audio))
        duration = info.frames / info.samplerate
        if not 1.0 <= duration <= 20.0:
            continue
        rows_by_speaker[speaker].append({
            "audio": str(audio),
            "text": text,
            "language": "vi",
            "speaker_id": f"vivos:{speaker}",
            "accent": "vi_mixed",
            "dataset": "VIVOS",
            "duration_seconds": round(duration, 3),
        })

    rng = random.Random(args.seed)
    speakers = sorted(rows_by_speaker)
    rng.shuffle(speakers)
    validation_speakers = set(speakers[: args.validation_speakers])
    train_rows: list[dict[str, object]] = []
    validation_rows: list[dict[str, object]] = []
    for speaker in speakers:
        rows = rows_by_speaker[speaker]
        rng.shuffle(rows)
        if speaker in validation_speakers:
            validation_rows.extend(rows[:2])
        else:
            train_rows.extend(rows[: args.max_per_speaker])
    rng.shuffle(train_rows)
    rng.shuffle(validation_rows)

    for path, rows in [
        (Path(args.train_output), train_rows),
        (Path(args.validation_output), validation_rows),
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
            encoding="utf-8",
        )
    print(json.dumps({
        "train_rows": len(train_rows),
        "validation_rows": len(validation_rows),
        "train_speakers": len(set(speakers) - validation_speakers),
        "validation_speakers": len(validation_speakers),
    }))


if __name__ == "__main__":
    main()
