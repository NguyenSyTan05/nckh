"""Evaluate the multilingual ASR + translation pipeline across four variants.

This script compares four pipeline shapes on a held-out manifest:

1. Whisper + EnViT5
2. Whisper + Correction Memory + EnViT5
3. Whisper LoRA + Correction Memory + EnViT5
4. Whisper LoRA + Correction Memory + EnViT5 + conditional AI review

The script is intentionally lightweight and avoids new dependencies. It uses
existing local runtime helpers and writes a compact summary report to stdout.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
import time
from collections import Counter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
SERVICE_DIR = REPO_ROOT / "backend" / "ai-service"
if str(SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(SERVICE_DIR))

import main as ai


TOKEN_RE = re.compile(r"[^\w']+", re.UNICODE)
CHAR_TOKEN_RE = re.compile(r"\S", re.UNICODE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="JSONL evaluation manifest")
    parser.add_argument(
        "--output",
        default="data/evaluation/results.csv",
        help="CSV output for the summary report",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=0,
        help="Optional cap for the number of rows to evaluate",
    )
    parser.add_argument(
        "--whisper-model",
        default="",
        help="Optional Whisper model or exported CTranslate2 adapter path",
    )
    parser.add_argument(
        "--whisper-accurate-model",
        default="",
        help="Optional small/accurate Whisper model",
    )
    parser.add_argument(
        "--correction-memory",
        default=str(SERVICE_DIR / "correction-memory.json"),
        help="JSON or JSONL correction memory file",
    )
    parser.add_argument(
        "--use-llm-review",
        action="store_true",
        help="Enable LLM review for difficult cases in variant 4",
    )
    parser.add_argument(
        "--language",
        default="auto",
        help="Evaluate a locked language code (auto, en, vi)",
    )
    return parser.parse_args()


def normalize_text(value: str) -> str:
    value = " ".join(str(value).strip().split())
    return value.casefold()


def tokenize_words(text: str) -> list[str]:
    normalized = normalize_text(text)
    return [token for token in TOKEN_RE.split(normalized) if token]


def tokenize_chars(text: str) -> list[str]:
    normalized = normalize_text(text)
    return [token for token in CHAR_TOKEN_RE.findall(normalized) if token]


def levenshtein_distance(left: str, right: str) -> int:
    left_chars = list(left)
    right_chars = list(right)
    previous = list(range(len(right_chars) + 1))
    for left_index, left_char in enumerate(left_chars, 1):
        current = [left_index]
        for right_index, right_char in enumerate(right_chars, 1):
            insert_cost = current[right_index - 1] + 1
            delete_cost = previous[right_index] + 1
            substitute_cost = previous[right_index - 1] + (left_char != right_char)
            current.append(min(insert_cost, delete_cost, substitute_cost))
        previous = current
    return previous[-1]


def word_error_rate(reference: str, hypothesis: str) -> float:
    ref_tokens = tokenize_words(reference)
    hyp_tokens = tokenize_words(hypothesis)
    distance = levenshtein_distance(
        " ".join(ref_tokens),
        " ".join(hyp_tokens),
    )
    return distance / max(len(ref_tokens), 1)


def char_error_rate(reference: str, hypothesis: str) -> float:
    ref_chars = "".join(tokenize_chars(reference))
    hyp_chars = "".join(tokenize_chars(hypothesis))
    distance = levenshtein_distance(ref_chars, hyp_chars)
    return distance / max(len(ref_chars), 1)


def clipped_precision(candidate_tokens: list[str], reference_tokens: list[str], n: int) -> float:
    candidate_ngrams = Counter(
        tuple(candidate_tokens[i:i + n])
        for i in range(len(candidate_tokens) - n + 1)
    )
    reference_ngrams = Counter(
        tuple(reference_tokens[i:i + n])
        for i in range(len(reference_tokens) - n + 1)
    )
    if not candidate_ngrams:
        return 0.0
    matched = sum(
        min(candidate_ngrams[ngram], reference_ngrams[ngram])
        for ngram in candidate_ngrams
    )
    total = sum(candidate_ngrams.values())
    return matched / max(total, 1)


def bleu_score(reference: str, hypothesis: str) -> float:
    ref_tokens = tokenize_words(reference)
    hyp_tokens = tokenize_words(hypothesis)
    if not hyp_tokens or not ref_tokens:
        return 0.0
    precisions = []
    for n in range(1, 5):
        if len(hyp_tokens) >= n:
            precisions.append(clipped_precision(hyp_tokens, ref_tokens, n))
    if not precisions:
        return 0.0
    brevity_penalty = (
        1.0
        if len(hyp_tokens) >= len(ref_tokens)
        else math.exp(1.0 - len(ref_tokens) / max(len(hyp_tokens), 1))
    )
    # Clamp the precision values to avoid math domain errors on completely
    # mismatched candidate/reference n-grams.
    geometric_mean = math.exp(
        sum(math.log(max(p, 1e-9)) for p in precisions) / len(precisions)
    )
    return brevity_penalty * geometric_mean


def chr_f_score(reference: str, hypothesis: str) -> float:
    ref = "".join(tokenize_chars(reference))
    hyp = "".join(tokenize_chars(hypothesis))
    if not ref or not hyp:
        return 0.0
    ref_ngrams = Counter(ref[i:i + 6] for i in range(len(ref) - 5))
    hyp_ngrams = Counter(hyp[i:i + 6] for i in range(len(hyp) - 5))
    overlap = sum(min(ref_ngrams[n], hyp_ngrams[n]) for n in ref_ngrams)
    precision = overlap / max(sum(hyp_ngrams.values()), 1)
    recall = overlap / max(sum(ref_ngrams.values()), 1)
    if precision + recall <= 0:
        return 0.0
    return (2.0 * precision * recall) / (precision + recall)


def read_manifest(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            row["audio"] = str(row["audio"]).strip()
            row["text"] = str(row.get("text", "")).strip()
            if not row["text"]:
                raise ValueError(f"Line {line_number} is missing a reference transcript")
            rows.append(row)
    if not rows:
        raise ValueError("Evaluation manifest is empty")
    return rows


def read_audio_to_numpy(audio_path: Path) -> np.ndarray:
    if not audio_path.is_file():
        raise FileNotFoundError(audio_path)
    try:
        import soundfile as sf

        waveform, sample_rate = sf.read(audio_path, dtype="float32", always_2d=False)
        if waveform.ndim == 2:
            waveform = waveform.mean(axis=1)
        if sample_rate != 16_000:
            raise ValueError("Expected a 16 kHz evaluation waveform")
        return np.asarray(waveform, dtype=np.float32)
    except Exception:
        import wave

        with wave.open(str(audio_path), "rb") as wav_file:
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            frame_count = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            frames = wav_file.readframes(frame_count)
        if sample_rate != 16_000:
            raise ValueError("Expected a 16 kHz evaluation waveform")
        if sample_width == 2:
            waveform = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
            waveform /= 32768.0
        else:
            waveform = np.frombuffer(frames, dtype=np.uint8).astype(np.float32)
            waveform /= 255.0
        if channels > 1:
            waveform = waveform.reshape(-1, channels).mean(axis=1)
        return waveform.astype(np.float32)


def run_variant(
    row: dict[str, Any],
    variant: str,
    use_llm_review: bool,
    correction_path: str,
    whisper_model_override: str,
    whisper_accurate_override: str,
) -> dict[str, Any]:
    start_time = time.perf_counter()
    audio_path = Path(row["audio"])
    if not audio_path.is_absolute():
        audio_path = (Path(row.get("manifest_parent", ".")) / audio_path).resolve()
    audio = read_audio_to_numpy(audio_path)

    if whisper_model_override:
        os.environ["WHISPER_MODEL"] = whisper_model_override
    if whisper_accurate_override:
        os.environ["WHISPER_ACCURATE_MODEL"] = whisper_accurate_override

    # Keep a single expensive model load for the whole evaluation pass.
    ai.load_models()

    source_language = row.get("language", "auto")
    use_accurate_whisper = variant in {"v3", "v4"}
    transcription_model = ai.whisper_accurate if use_accurate_whisper else ai.whisper_fast
    transcription_flag = use_accurate_whisper

    transcript, detected_language, confidence, _ = ai.transcribe_file(
        audio,
        source_language,
        "",
        "speech",
        transcription_model,
        transcription_flag,
    )
    transcript = ai.clean_recognized_text(transcript)
    corrected = ai.apply_correction_memory(transcript, detected_language, correction_path)

    if variant == "v1":
        source_text = transcript
    else:
        source_text = corrected

    translation = ai.translate_text(source_text, detected_language)
    final_translation = translation
    if variant == "v4" and use_llm_review and ai.LLM_BASE_URL:
        should_review = ai.needs_llm_review(source_text, translation, confidence)
        if should_review:
            final_translation = ai.review_translation_with_llm(source_text, translation)

    total_latency = round((time.perf_counter() - start_time) * 1000)
    return {
        "raw_transcript": transcript,
        "corrected_transcript": corrected,
        "source_text": source_text,
        "translation": translation,
        "final_translation": final_translation,
        "language": detected_language,
        "confidence": confidence,
        "latency_ms": total_latency,
    }


def summarize(rows: list[dict[str, Any]], reference_text: str, reference_translation: str) -> dict[str, Any]:
    summary = {
        "WER": word_error_rate(reference_text, rows[-1]["raw_transcript"]),
        "CER": char_error_rate(reference_text, rows[-1]["raw_transcript"]),
        "BLEU": 0.0,
        "chrF": 0.0,
        "latency_ms": float(rows[-1]["latency_ms"]),
    }
    if reference_translation:
        summary["BLEU"] = bleu_score(reference_translation, rows[-1]["final_translation"])
        summary["chrF"] = chr_f_score(reference_translation, rows[-1]["final_translation"])
    return summary


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "variant",
        "raw_transcript",
        "corrected_transcript",
        "translation",
        "final_translation",
        "language",
        "confidence",
        "WER",
        "CER",
        "BLEU",
        "chrF",
        "latency_ms",
    ]
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).resolve()
    manifest_rows = read_manifest(input_path)
    if args.max_samples > 0:
        manifest_rows = manifest_rows[: args.max_samples]

    for row in manifest_rows:
        row["manifest_parent"] = input_path.parent

    if args.whisper_model:
        os.environ["WHISPER_MODEL"] = args.whisper_model
    if args.whisper_accurate_model:
        os.environ["WHISPER_ACCURATE_MODEL"] = args.whisper_accurate_model

    ai.load_models()

    variants = [
        ("v1", False),
        ("v2", True),
        ("v3", True),
        ("v4", True),
    ]
    all_results: list[dict[str, Any]] = []

    for variant, _use_correction in variants:
        per_variant: list[dict[str, Any]] = []
        for row in manifest_rows:
            result = run_variant(
                row=row,
                variant=variant,
                use_llm_review=args.use_llm_review,
                correction_path=args.correction_memory,
                whisper_model_override=os.getenv("WHISPER_MODEL", ""),
                whisper_accurate_override=os.getenv("WHISPER_ACCURATE_MODEL", ""),
            )
            reference_text = row.get("text", "")
            reference_translation = (
                row.get("reference_translation")
                or row.get("translation")
                or row.get("target_text")
                or ""
            )
            per_variant.append(
                {
                    "variant": variant,
                    "raw_transcript": result["raw_transcript"],
                    "corrected_transcript": result["corrected_transcript"],
                    "translation": result["translation"],
                    "final_translation": result["final_translation"],
                    "language": result["language"],
                    "confidence": result["confidence"],
                    "WER": word_error_rate(reference_text, result["raw_transcript"]),
                    "CER": char_error_rate(reference_text, result["raw_transcript"]),
                    "BLEU": (
                        0.0
                        if not reference_translation
                        else bleu_score(reference_translation, result["final_translation"])
                    ),
                    "chrF": (
                        0.0
                        if not reference_translation
                        else chr_f_score(reference_translation, result["final_translation"])
                    ),
                    "latency_ms": result["latency_ms"],
                }
            )
        variant_aggregate = {
            "variant": variant,
            "raw_transcript": "",
            "corrected_transcript": "",
            "translation": "",
            "final_translation": "",
            "language": "",
            "confidence": 0.0,
            "WER": sum(item["WER"] for item in per_variant) / max(len(per_variant), 1),
            "CER": sum(item["CER"] for item in per_variant) / max(len(per_variant), 1),
            "BLEU": sum(item["BLEU"] for item in per_variant) / max(len(per_variant), 1),
            "chrF": sum(item["chrF"] for item in per_variant) / max(len(per_variant), 1),
            "latency_ms": sum(item["latency_ms"] for item in per_variant) / max(len(per_variant), 1),
        }
        all_results.append(variant_aggregate)

    write_csv(Path(args.output), all_results)
    for row in all_results:
        print(
            f"{row['variant']}: WER={row['WER']:.4f}, CER={row['CER']:.4f}, "
            f"BLEU={row['BLEU']:.4f}, chrF={row['chrF']:.4f}, latency_ms={row['latency_ms']:.1f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
