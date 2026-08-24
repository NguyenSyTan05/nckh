"""
ClassBridge Integrated Transcript Pipeline Module
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .asr_module import ASRModule
from .correction_module import CorrectionModule
from .transcript_stabilizer import TranscriptStabilizer, StabilizedResult


@dataclass
class PipelineOutput:
    raw_text: str
    cleaned_text: str
    stable_text: str
    unstable_text: str
    full_text: str
    language: str
    confidence: float
    is_final: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "raw_text": self.raw_text,
            "cleaned_text": self.cleaned_text,
            "stable_text": self.stable_text,
            "unstable_text": self.unstable_text,
            "full_text": self.full_text,
            "language": self.language,
            "confidence": self.confidence,
            "is_final": self.is_final,
        }


class TranscriptPipeline:
    """
    Pipeline hợp nhất:
    Audio PCM 16kHz -> ASR -> Correction -> Stabilizer -> Output sạch
    """

    def __init__(self, asr_module: ASRModule | None = None) -> None:
        self.asr = asr_module or ASRModule()
        self.correction = CorrectionModule()
        self.stabilizer = TranscriptStabilizer(unstable_tail_words=1)

    def reset(self) -> None:
        """Reset trạng thái stabilizer cho câu mới."""
        self.stabilizer.reset()

    def process_chunk(
        self,
        audio_pcm: np.ndarray,
        language: str | None = None,
        is_final: bool = False,
    ) -> PipelineOutput:
        """
        Xử lý 1 chunk audio thời gian thực từ stream.
        """
        # 1. ASR
        raw_text, detected_lang, confidence = self.asr.transcribe(
            audio_pcm=audio_pcm,
            language=language,
            is_streaming=not is_final,
        )

        # 2. Correction & Normalization
        cleaned = self.correction.clean(raw_text)

        # 3. Stabilization
        if is_final:
            stabilized = self.stabilizer.finalize(cleaned)
        else:
            stabilized = self.stabilizer.process_partial(cleaned)

        return PipelineOutput(
            raw_text=raw_text,
            cleaned_text=cleaned,
            stable_text=stabilized.stable_text,
            unstable_text=stabilized.unstable_text,
            full_text=stabilized.full_text,
            language=detected_lang,
            confidence=confidence,
            is_final=is_final,
        )
