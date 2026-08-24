"""Safe, local phrase corrections learned from verified ASR pairs."""

from __future__ import annotations

import json
import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _normalized_phrase(value: str) -> str:
    return " ".join(value.strip().split())


@lru_cache(maxsize=8)
def _load_rules_cached(path: str, modified_ns: int) -> tuple[dict[str, Any], ...]:
    del modified_ns
    memory_path = Path(path)
    if memory_path.suffix.lower() == ".jsonl":
        candidates = []
        for line in memory_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped:
                candidates.append(json.loads(stripped))
    else:
        payload = json.loads(memory_path.read_text(encoding="utf-8"))
        candidates = payload.get("rules", [])

    rules = []
    for candidate in candidates:
        source = _normalized_phrase(candidate.get("source", ""))
        target = _normalized_phrase(candidate.get("target", ""))
        language = str(candidate.get("language", "")).lower()
        support = int(candidate.get("support", 0))
        confidence = float(candidate.get("confidence", 0.0))
        if (
            source
            and target
            and source.casefold() != target.casefold()
            and language in {"en", "vi"}
            and support >= 2
            and confidence >= 0.8
        ):
            source_words = [re.escape(word) for word in source.split()]
            pattern = re.compile(
                r"(?<!\w)" + r"\s+".join(source_words) + r"(?!\w)",
                flags=re.IGNORECASE,
            )
            rules.append(
                {
                    "source": source,
                    "target": target,
                    "language": language,
                    "support": support,
                    "confidence": confidence,
                    "pattern": pattern,
                }
            )
    rules.sort(key=lambda rule: len(rule["source"].split()), reverse=True)
    return tuple(rules)


def load_rules(path: str) -> tuple[dict[str, Any], ...]:
    memory_path = Path(path)
    if not memory_path.is_file():
        return ()
    return _load_rules_cached(str(memory_path.resolve()), memory_path.stat().st_mtime_ns)


def correction_memory_stats(path: str) -> dict[str, int]:
    rules = load_rules(path)
    return {
        "rules": len(rules),
        "vi_rules": sum(rule["language"] == "vi" for rule in rules),
        "en_rules": sum(rule["language"] == "en" for rule in rules),
    }


def apply_correction_memory(text: str, language: str, path: str) -> str:
    """Apply only high-support phrase substitutions for the detected language."""
    corrected = _normalized_phrase(text)
    if not corrected or language not in {"en", "vi"}:
        return corrected
    before = corrected
    for rule in load_rules(path):
        if rule["language"] != language:
            continue
        pattern: re.Pattern = rule["pattern"]

        def replace(match: re.Match[str]) -> str:
            target = rule["target"]
            if match.group(0)[:1].isupper():
                target = target[:1].upper() + target[1:]
            return target

        corrected = pattern.sub(replace, corrected)
    if corrected != before:
        logger.debug("[CORRECTION] before=%r after=%r language=%s", before, corrected, language)
    return corrected

