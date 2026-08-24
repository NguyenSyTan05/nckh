"""Evaluate a faster-whisper model with the same automatic language mode as the app."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel
from faster_whisper.audio import decode_audio
from jiwer import wer


def normalize(text: str) -> str:
    return re.sub(r"[^\w]+", " ", text.casefold(), flags=re.UNICODE).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--limit-per-language", type=int, default=20)
    args = parser.parse_args()

    rows = [
        json.loads(line)
        for line in Path(args.manifest).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    selected: list[dict] = []
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        language = row["language"]
        if counts[language] < args.limit_per_language:
            selected.append(row)
            counts[language] += 1

    model = WhisperModel(args.model, device="cuda", compute_type="int8_float16")
    references: dict[str, list[str]] = defaultdict(list)
    predictions: dict[str, list[str]] = defaultdict(list)
    detected_correct: dict[str, int] = defaultdict(int)
    for index, row in enumerate(selected, 1):
        decoded = decode_audio(row["audio"], sampling_rate=16_000)
        audio = np.asarray(decoded[0] if isinstance(decoded, tuple) else decoded, dtype=np.float32)
        _, _, probabilities = model.detect_language(
            audio=audio, vad_filter=True, language_detection_segments=2
        )
        scores = dict(probabilities)
        forced_language = "vi" if scores.get("vi", 0) >= scores.get("en", 0) else "en"
        segments, info = model.transcribe(
            audio,
            language=forced_language,
            beam_size=2,
            vad_filter=True,
            condition_on_previous_text=False,
        )
        prediction = " ".join(segment.text for segment in segments).strip()
        language = row["language"]
        references[language].append(normalize(row["text"]))
        predictions[language].append(normalize(prediction))
        detected_correct[language] += int(forced_language == language)
        print(f"[{index}/{len(selected)}] {language}->{forced_language}: {prediction[:100]}")

    for language in ("en", "vi"):
        total = len(references[language])
        score = 100 * wer(references[language], predictions[language])
        accuracy = 100 * detected_correct[language] / max(1, total)
        print(f"RESULT {language}: WER={score:.2f}% language_accuracy={accuracy:.1f}% n={total}")


if __name__ == "__main__":
    main()
