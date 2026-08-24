"""
ClassBridge ASR Module (Whisper CTranslate2 Engine)
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Literal

import numpy as np

logger = logging.getLogger("classbridge.asr")


def detect_best_device() -> tuple[str, str]:
    """Phát hiện GPU NVIDIA CUDA (float16) hoặc fallback CPU (int8)."""
    if os.getenv("WHISPER_DEVICE"):
        dev = os.getenv("WHISPER_DEVICE", "cpu").lower()
        comp = os.getenv("WHISPER_COMPUTE_TYPE", "float16" if dev == "cuda" else "int8").lower()
        return dev, comp
    try:
        import ctranslate2
        if ctranslate2.get_cuda_device_count() > 0:
            logger.info("🚀 Phát hiện NVIDIA GPU! Kích hoạt tăng tốc CUDA float16.")
            return "cuda", "float16"
    except Exception:
        pass
    return "cpu", "int8"


class ASRModule:
    """
    Module nhận dạng giọng nói sử dụng Faster-Whisper / CTranslate2.
    """

    def __init__(self, model_path: str | None = None) -> None:
        self.device, self.compute_type = detect_best_device()
        self.model_path = model_path or self._resolve_default_model_path()
        self.model: Any = None
        self._load_model()

    def _resolve_default_model_path(self) -> str:
        base_dir = Path(__file__).parent.parent
        turbo_path = base_dir / "whisper-large-v3-turbo-ct2"
        if turbo_path.exists():
            return str(turbo_path)
        legacy_path = base_dir / "whisper-multi-accent-ct2"
        if legacy_path.exists():
            return str(legacy_path)
        return "Systran/faster-whisper-large-v3-turbo"

    def _load_model(self) -> None:
        from faster_whisper import WhisperModel
        logger.info("🎯 Nạp mô hình ASR từ: %s (device=%s, compute=%s)", self.model_path, self.device, self.compute_type)
        try:
            self.model = WhisperModel(
                self.model_path,
                device=self.device,
                compute_type=self.compute_type,
                cpu_threads=max(2, min(8, (os.cpu_count() or 4) // 2)),
                num_workers=1,
            )
        except Exception as exc:
            if self.device == "cuda":
                logger.warning("CUDA lỗi, fallback sang CPU int8: %s", exc)
                self.device = "cpu"
                self.compute_type = "int8"
                self.model = WhisperModel(
                    self.model_path,
                    device="cpu",
                    compute_type="int8",
                    cpu_threads=max(2, min(8, (os.cpu_count() or 4) // 2)),
                    num_workers=1,
                )
            else:
                raise

    def transcribe(
        self,
        audio_pcm: np.ndarray,
        language: str | None = None,
        beam_size: int = 1,
        is_streaming: bool = True,
    ) -> tuple[str, str, float]:
        """
        Nhận diện audio PCM 16kHz float32.
        - language: None (Auto detect), "vi", "en"
        - Trả về: (text, detected_language, confidence)
        """
        if audio_pcm is None or audio_pcm.size == 0:
            return "", "vi" if language == "vi" else "en", 0.0

        if not np.isfinite(audio_pcm).all():
            audio_pcm = np.nan_to_num(audio_pcm, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)

        peak = float(np.max(np.abs(audio_pcm)))
        if peak < 0.005:
            return "", "vi" if language == "vi" else "en", 0.0

        # Normalization nhẹ nhàng
        if 0.008 <= peak < 0.50:
            gain = min(2.5, 0.60 / peak)
            audio_pcm = audio_pcm * gain

        target_lang = None if (not language or language == "auto") else (language if language in {"vi", "en"} else None)

        segments, info = self.model.transcribe(
            audio_pcm,
            language=target_lang,
            beam_size=beam_size,
            best_of=1,
            temperature=0.0,
            repetition_penalty=1.0,
            no_repeat_ngram_size=0,
            without_timestamps=True,
            max_new_tokens=160 if is_streaming else 256,
            log_prob_threshold=-1.2,
            no_speech_threshold=0.50,
            vad_filter=True,
            vad_parameters={
                "threshold": 0.45,
                "min_speech_duration_ms": 100,
                "min_silence_duration_ms": 250,
            },
            condition_on_previous_text=False,
        )

        raw_lang = getattr(info, "language", None) or "vi"
        all_probs = dict(getattr(info, "all_language_probs", []) or [])
        en_prob = all_probs.get("en", 0.0)
        vi_prob = all_probs.get("vi", 0.0)

        if en_prob >= 0.25 or en_prob > vi_prob:
            detected = "en"
        else:
            detected = "vi"

        # Khóa cứng tuyệt đối chỉ nhận Tiếng Việt hoặc Tiếng Anh
        if raw_lang not in {"en", "vi"}:
            segments, info = self.model.transcribe(
                audio_pcm,
                language=detected,
                beam_size=beam_size,
                best_of=1,
                temperature=0.0,
                repetition_penalty=1.0,
                no_repeat_ngram_size=0,
                without_timestamps=True,
                max_new_tokens=160 if is_streaming else 256,
                log_prob_threshold=-1.2,
                no_speech_threshold=0.60,
                vad_filter=False if is_streaming else True,
                condition_on_previous_text=False,
            )

        accepted_texts = []
        confidences = []
        for segment in segments:
            text = segment.text.strip()
            if text:
                accepted_texts.append(text)
                confidences.append(float(np.exp(max(-5.0, segment.avg_logprob))) * (1.0 - float(segment.no_speech_prob)))

        full_text = " ".join(accepted_texts).strip()
        mean_conf = float(np.mean(confidences)) if confidences else 0.0

        return full_text, detected, mean_conf
