import asyncio
import io
import logging
import os
import re
import sys
import time
import unicodedata
import warnings
from contextlib import asynccontextmanager
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO, Literal

if TYPE_CHECKING:
    # Only imported during type-checking; at runtime these are loaded on demand
    # inside functions to avoid loading heavy libraries at import time.
    pass  # noqa: F401

# Numerical libraries otherwise create a thread pool per CPU core while the
# two models are loading, which can exhaust RAM before the service is ready.
# Use ClassBridge-specific overrides instead of inheriting a machine-wide
# OPENBLAS setting that may be much too large for two Whisper models.
os.environ["OPENBLAS_NUM_THREADS"] = os.getenv(
    "CLASSBRIDGE_OPENBLAS_THREADS", "1"
)
os.environ["OMP_NUM_THREADS"] = os.getenv("CLASSBRIDGE_OMP_THREADS", "2")
os.environ["MKL_NUM_THREADS"] = os.getenv("CLASSBRIDGE_MKL_THREADS", "2")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

# Windows services often inherit a legacy console encoding (for example
# cp1252).  Startup messages contain Vietnamese text, so make logging safe
# before the first model-selection message is emitted.
for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="backslashreplace")

import uuid

import httpx
import numpy as np
from av.error import InvalidDataError
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from correction_memory import apply_correction_memory, correction_memory_stats
from transcript_stabilizer import TranscriptStabilizer
from modules.correction_module import CorrectionModule
from auto_punctuation import format_auto_punctuation, remove_repetitions
from session_manager import session_manager

correction_engine = CorrectionModule()

MODEL_CACHE_DIR = os.getenv("HF_HOME", str(Path(__file__).parent / ".models"))
os.environ.setdefault("HF_HOME", MODEL_CACHE_DIR)
CORRECTION_MEMORY_PATH = (
    os.getenv("CORRECTION_MEMORY_PATH", "").strip()
    or str(Path(__file__).parent / "correction-memory.json")
)
MODEL_MODE = os.getenv("MODEL_MODE", "local").lower()
CUSTOM_VOICE_MODEL_DIR = str(Path(__file__).parent / "whisper-voice-fine-tuned")
WHISPER_TURBO_CT2_MODEL_DIR = str(Path(__file__).parent / "whisper-large-v3-turbo-ct2")
WHISPER_CT2_MODEL_DIR = str(Path(__file__).parent / "whisper-decoder-micro1-ct2")
WHISPER_LEGACY_CT2_MODEL_DIR = str(Path(__file__).parent / "whisper-multi-accent-ct2")
WHISPER_ENGLISH_MODEL_DIR = str(Path(__file__).parent / "whisper-decoder-micro4-en-ct2")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "")
if not WHISPER_MODEL:
    if os.path.exists(WHISPER_TURBO_CT2_MODEL_DIR):
        WHISPER_MODEL = WHISPER_TURBO_CT2_MODEL_DIR
        print(f"[ClassBridge AI] 🎯 Tự động nạp mô hình Whisper Large V3 Turbo CT2 (Đa ngữ chuẩn): {WHISPER_TURBO_CT2_MODEL_DIR}")
    elif os.path.exists(WHISPER_LEGACY_CT2_MODEL_DIR):
        WHISPER_MODEL = WHISPER_LEGACY_CT2_MODEL_DIR
        print(f"[ClassBridge AI] 🎯 Tự động nạp mô hình Whisper Multi-Accent 63 Tỉnh Thành CT2: {WHISPER_LEGACY_CT2_MODEL_DIR}")
    elif os.path.exists(WHISPER_CT2_MODEL_DIR):
        WHISPER_MODEL = WHISPER_CT2_MODEL_DIR
        print(f"[ClassBridge AI] 🎯 Tự động nạp mô hình CTranslate2 đã train: {WHISPER_CT2_MODEL_DIR}")
    elif os.path.exists(CUSTOM_VOICE_MODEL_DIR):
        WHISPER_MODEL = CUSTOM_VOICE_MODEL_DIR
        print(f"[ClassBridge AI] 🎯 Tự động nạp mô hình giọng nói cá nhân hóa: {CUSTOM_VOICE_MODEL_DIR}")
    else:
        WHISPER_MODEL = "large-v3-turbo"


def _detect_best_whisper_device() -> tuple[str, str]:
    """Tự động sử dụng NVIDIA CUDA GPU để tăng tốc độ nhận dạng giọng nói gấp 5-10 lần."""
    if os.getenv("WHISPER_DEVICE"):
        dev = os.getenv("WHISPER_DEVICE", "cpu").lower()
        comp = os.getenv("WHISPER_COMPUTE_TYPE", "float16" if dev == "cuda" else "int8").lower()
        return dev, comp
    try:
        import ctranslate2
        if ctranslate2.get_cuda_device_count() > 0:
            print("[ClassBridge AI] 🚀 Phát hiện NVIDIA GPU! Kích hoạt tăng tốc CUDA float16.")
            return "cuda", "float16"
    except Exception:
        pass
    return "cpu", "int8"

WHISPER_DEVICE, WHISPER_COMPUTE_TYPE = _detect_best_whisper_device()

default_cpu_threads = max(4, min(8, (os.cpu_count() or 4) // 2))
# The final pass must not overwrite the trained model with the stock model.
WHISPER_ACCURATE_MODEL = os.getenv("WHISPER_ACCURATE_MODEL", WHISPER_MODEL)
WHISPER_ENGLISH_MODEL = os.getenv("WHISPER_ENGLISH_MODEL", WHISPER_ENGLISH_MODEL_DIR)
WHISPER_CPU_THREADS = int(os.getenv("WHISPER_CPU_THREADS", str(default_cpu_threads)))
WHISPER_NUM_WORKERS = max(1, int(os.getenv("WHISPER_NUM_WORKERS", "1")))
WHISPER_ACCURATE_WORKERS = max(
    1, int(os.getenv("WHISPER_ACCURATE_WORKERS", "1"))
)
WHISPER_ACCURATE_THREADS = max(
    1, int(os.getenv("WHISPER_ACCURATE_THREADS", str(default_cpu_threads)))
)
BALANCED_NMT_DIR = str(Path(__file__).parent / "nmt-academic-lora-balanced")
LEGACY_NMT_DIR = str(Path(__file__).parent / "nmt-academic-lora")
TRANSLATION_MODEL = os.getenv("TRANSLATION_MODEL", "")
if not TRANSLATION_MODEL:
    if os.path.exists(BALANCED_NMT_DIR):
        TRANSLATION_MODEL = BALANCED_NMT_DIR
        print(f"[ClassBridge AI] 🎯 Tự động nạp mô hình dịch thuật đã train (Balanced NMT LoRA): {BALANCED_NMT_DIR}")
    elif os.path.exists(LEGACY_NMT_DIR):
        TRANSLATION_MODEL = LEGACY_NMT_DIR
        print(f"[ClassBridge AI] 🎯 Tự động nạp mô hình dịch thuật đã train: {LEGACY_NMT_DIR}")
    else:
        TRANSLATION_MODEL = "VietAI/envit5-translation"

# Secondary translation model for ensemble voting (opus-mt, already local).
# EN→VI: Helsinki-NLP/opus-mt-en-vi  |  VI→EN: Helsinki-NLP/opus-mt-vi-en
TRANSLATION_SECONDARY_MODEL_EN_VI = os.getenv(
    "TRANSLATION_SECONDARY_EN_VI", "Helsinki-NLP/opus-mt-en-vi"
)
TRANSLATION_SECONDARY_MODEL_VI_EN = os.getenv(
    "TRANSLATION_SECONDARY_VI_EN", "Helsinki-NLP/opus-mt-vi-en"
)
TRANSLATION_USE_ENSEMBLE = os.getenv("TRANSLATION_USE_ENSEMBLE", "true").lower() in {"1", "true", "yes"}
# Translation is intentionally lower priority than live transcription.
TRANSLATION_CPU_THREADS = int(os.getenv("TRANSLATION_CPU_THREADS", "3"))
TRANSLATION_NUM_BEAMS = max(1, int(os.getenv("TRANSLATION_NUM_BEAMS", "1")))
TRANSLATION_MAX_NEW_TOKENS = max(
    24, int(os.getenv("TRANSLATION_MAX_NEW_TOKENS", "256"))
)
TRANSLATION_QUANTIZATION = os.getenv("TRANSLATION_QUANTIZATION", "int8").lower()
TRANSLATION_BACKEND = "envit5"

WHISPER_BEAM_SIZE = max(1, int(os.getenv("WHISPER_BEAM_SIZE", "1")))  # Fast greedy streaming (<30ms)
WHISPER_MUSIC_BEAM_SIZE = max(1, int(os.getenv("WHISPER_MUSIC_BEAM_SIZE", "2")))
WHISPER_ACCURATE_BEAM_SIZE = max(
    1, int(os.getenv("WHISPER_ACCURATE_BEAM_SIZE", "2"))
)
WHISPER_RETRY_CONFIDENCE = float(
    os.getenv("WHISPER_RETRY_CONFIDENCE", "0.25")
)
WHISPER_VI_RETRY_CONFIDENCE = float(
    os.getenv("WHISPER_VI_RETRY_CONFIDENCE", "0.34")
)
WHISPER_WARMUP = os.getenv("WHISPER_WARMUP", "true").lower() in {"1", "true", "yes"}
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "").rstrip("/")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-7B-Instruct")
LLM_TIMEOUT_SECONDS = float(os.getenv("LLM_TIMEOUT_SECONDS", "6"))
TRANSLATION_COURSE_CONTEXT = os.getenv("TRANSLATION_COURSE_CONTEXT", "").strip()
TRANSLATION_TOPIC_CONTEXT = os.getenv("TRANSLATION_TOPIC_CONTEXT", "").strip()

logger = logging.getLogger("classbridge.ai")
DEBUG_ASR = os.getenv("DEBUG_ASR", "false").strip().lower() in {"1", "true", "yes", "on"}
DEBUG_DISABLE_CORRECTION = os.getenv("DEBUG_DISABLE_CORRECTION", "false").strip().lower() in {"1", "true", "yes", "on"}
# Whisper models are loaded lazily in load_models(); None until then.
whisper_fast: Any = None
whisper_accurate: Any = None
whisper_english: Any = None
# Primary translation model (envit5 or nllb).
translator_models: dict[str, Any] = {}
translator_tokenizers: dict[str, Any] = {}
# Secondary ensemble models (Helsinki-NLP MarianMT opus-mt).
secondary_translator_models: dict[str, Any] = {}
secondary_translator_tokenizers: dict[str, Any] = {}
llm_client: httpx.AsyncClient | None = None
transcription_semaphore = asyncio.Semaphore(WHISPER_NUM_WORKERS)
accurate_transcription_semaphore = asyncio.Semaphore(WHISPER_ACCURATE_WORKERS)
TRANSLATION_NUM_WORKERS = max(1, int(os.getenv("TRANSLATION_NUM_WORKERS", "3")))
translation_semaphore = asyncio.Semaphore(TRANSLATION_NUM_WORKERS)


class PipelineResult(BaseModel):
    transcript: str
    corrected_text: str
    corrected_transcript: str = ""
    raw_transcript: str = ""
    envit5_translation: str = ""
    final_translation: str = ""
    translation: str = ""
    source_language: Literal["en", "vi"]
    latency_ms: int
    speaker_id: int = 1
    recognition_mode: Literal["fast", "accurate"] = "fast"
    confidence: float = 0.0
    ai_used: bool = False
    demo: bool = False


class TranscriptionResult(BaseModel):
    transcript: str
    corrected_text: str
    source_language: Literal["en", "vi"]
    latency_ms: int
    speaker_id: int = 1
    recognition_mode: Literal["fast", "accurate"] = "fast"
    confidence: float = 0.0
    demo: bool = False


class TranslationResult(BaseModel):
    translation: str
    source_language: Literal["en", "vi"]
    latency_ms: int


def load_models() -> None:
    global whisper_fast, whisper_accurate, whisper_english
    if MODEL_MODE == "demo":
        return

    from faster_whisper import WhisperModel

    # WHISPER_MODEL may be a Hugging Face model ID or a local fine-tuned model path.
    try:
        whisper_fast = WhisperModel(
            WHISPER_MODEL,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
            cpu_threads=min(WHISPER_CPU_THREADS, os.cpu_count() or 2),
            num_workers=WHISPER_NUM_WORKERS,
        )
    except Exception as exc:
        if WHISPER_DEVICE != "cuda":
            raise
        logger.warning("CUDA unavailable, falling back to CPU int8: %s", exc)
        whisper_fast = WhisperModel(
            WHISPER_MODEL,
            device="cpu",
            compute_type="int8",
            cpu_threads=min(WHISPER_CPU_THREADS, os.cpu_count() or 2),
            num_workers=WHISPER_NUM_WORKERS,
        )
    if WHISPER_ACCURATE_MODEL == WHISPER_MODEL or not WHISPER_ACCURATE_MODEL:
        whisper_accurate = whisper_fast
    else:
        try:
            whisper_accurate = WhisperModel(
                WHISPER_ACCURATE_MODEL,
                device=WHISPER_DEVICE,
                compute_type=WHISPER_COMPUTE_TYPE,
                cpu_threads=min(WHISPER_ACCURATE_THREADS, os.cpu_count() or 2),
                num_workers=WHISPER_ACCURATE_WORKERS,
            )
        except Exception as exc:
            logger.warning("Using whisper_fast as accurate model: %s", exc)
            whisper_accurate = whisper_fast
    whisper_english = whisper_accurate
    if WHISPER_WARMUP:
        # Force CTranslate2 to initialize its first inference silently before anyone starts speaking
        for model in list(dict.fromkeys([whisper_fast, whisper_accurate, whisper_english])):
            try:
                warmup_segments, _ = model.transcribe(
                    np.zeros(4_000, dtype=np.float32),
                    language="vi",
                    beam_size=1,
                    vad_filter=False,
                    without_timestamps=True,
                    max_new_tokens=2,
                )
                list(warmup_segments)
            except Exception:
                pass

    # Load and quantize the translator after both recognizers. MKL needs a
    # contiguous allocation while Whisper starts; loading EnViT5 first can
    # fragment the limited address space and make Whisper fail.
    load_translation_model()


def resolve_translation_model() -> tuple[str, bool]:
    configured_path = Path(TRANSLATION_MODEL).expanduser()
    if configured_path.exists():
        return str(configured_path.resolve()), True

    # Resolve an already cached Hub model to its concrete snapshot directory.
    # Passing a repository ID makes recent Transformers versions probe the
    # network for optional custom generation code even with local_files_only.
    from huggingface_hub import snapshot_download
    from huggingface_hub.errors import LocalEntryNotFoundError

    try:
        return snapshot_download(TRANSLATION_MODEL, local_files_only=True), True
    except LocalEntryNotFoundError:
        # On the first run, let Transformers download the configured model.
        return TRANSLATION_MODEL, False


def load_translation_model() -> None:
    if TRANSLATION_BACKEND in translator_models or MODEL_MODE == "demo":
        return
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    # Leave CPU capacity for Whisper so translations cannot block live captions.
    torch.set_num_threads(min(TRANSLATION_CPU_THREADS, os.cpu_count() or 2))
    if hasattr(torch.backends, "quantized"):
        try:
            torch.backends.quantized.engine = "fbgemm"
        except Exception:
            pass
    model_source, local_files_only = resolve_translation_model()
    adapter_cfg_file = Path(model_source) / "adapter_config.json"
    is_lora_dir = adapter_cfg_file.exists()

    if is_lora_dir:
        import json
        with open(adapter_cfg_file, "r", encoding="utf-8") as f:
            lora_cfg = json.load(f)
        base_model_path = lora_cfg.get("base_model_name_or_path", "VietAI/envit5-translation")
        tokenizer_source = model_source
    else:
        base_model_path = model_source
        tokenizer_source = model_source

    tokenizer_options: dict[str, Any] = {"local_files_only": local_files_only}
    if TRANSLATION_BACKEND == "nllb":
        tokenizer_options["src_lang"] = "eng_Latn"
    translator_tokenizers[TRANSLATION_BACKEND] = AutoTokenizer.from_pretrained(
        tokenizer_source, **tokenizer_options
    )
    model_options: dict[str, Any] = {"local_files_only": local_files_only and not is_lora_dir}
    if TRANSLATION_QUANTIZATION == "int8":
        # Loading through FP16 halves the temporary allocation, then dynamic
        # int8 makes CPU inference both faster and smaller. Remaining layers
        # are restored to FP32 because dynamic Linear expects FP32 activations.
        model_options["torch_dtype"] = torch.float16
    model = AutoModelForSeq2SeqLM.from_pretrained(
        base_model_path, **model_options
    )
    if is_lora_dir:
        try:
            from peft import PeftModel
            model = PeftModel.from_pretrained(model, model_source)
            model = model.merge_and_unload()
            print(f"[ClassBridge AI] 🎯 Đã tích hợp thành công LoRA Adapter đã huấn luyện vào mô hình dịch thuật!")
        except Exception as exc:
            logger.warning("Không thể gắn LoRA adapter (%s), sử dụng base model: %s", model_source, exc)
    model = model.eval()

    if TRANSLATION_QUANTIZATION == "int8":
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore", message="torch.ao.quantization is deprecated.*"
            )
            quantize_fn = getattr(torch.ao.quantization, "quantize_dynamic", None) or getattr(torch, "quantize_dynamic", None)
            if quantize_fn is not None:
                model = quantize_fn(
                    model, {torch.nn.Linear}, dtype=torch.qint8, inplace=True
                )
        model.float()
    elif TRANSLATION_QUANTIZATION != "none":
        raise ValueError(
            "TRANSLATION_QUANTIZATION must be either 'int8' or 'none'"
        )
    translator_models[TRANSLATION_BACKEND] = model


def resolve_secondary_model(model_name: str) -> tuple[str, bool]:
    """Resolve opus-mt model path preferring already-downloaded Hub cache."""
    from huggingface_hub import snapshot_download
    from huggingface_hub.errors import LocalEntryNotFoundError
    try:
        return snapshot_download(model_name, local_files_only=True), True
    except (LocalEntryNotFoundError, Exception):
        return model_name, False


def load_secondary_translation_model() -> None:
    """Load Helsinki-NLP/opus-mt models for ensemble translation.

    These are MarianMT models — compact, fast, and specialized for EN↔VI.
    Loading them in parallel to envit5 gives the ensemble two independent
    hypotheses to pick the better result from.
    """
    if not TRANSLATION_USE_ENSEMBLE or MODEL_MODE == "demo":
        return
    if "opus_en_vi" in secondary_translator_models and "opus_vi_en" in secondary_translator_models:
        return
    import torch
    from transformers import MarianMTModel, MarianTokenizer

    for key, model_name in [
        ("opus_en_vi", TRANSLATION_SECONDARY_MODEL_EN_VI),
        ("opus_vi_en", TRANSLATION_SECONDARY_MODEL_VI_EN),
    ]:
        if key in secondary_translator_models:
            continue
        try:
            model_source, local_only = resolve_secondary_model(model_name)
            tokenizer = MarianTokenizer.from_pretrained(
                model_source, local_files_only=local_only
            )
            model = MarianMTModel.from_pretrained(
                model_source, local_files_only=local_only
            ).eval()
            # Dynamic int8 for smaller RAM and faster CPU inference.
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="torch.ao.*")
                warnings.filterwarnings("ignore", message="torch.quantize.*")
                try:
                    quantize_fn = getattr(torch.ao.quantization, "quantize_dynamic", None) or getattr(torch, "quantize_dynamic", None)
                    if quantize_fn is not None:
                        model = quantize_fn(
                            model, {torch.nn.Linear}, dtype=torch.qint8, inplace=True
                        )
                        model.float()
                except Exception:
                    pass
            secondary_translator_models[key] = model
            secondary_translator_tokenizers[key] = tokenizer
            logger.info("Loaded secondary translation model: %s as %s", model_name, key)
        except Exception as exc:
            logger.warning("Could not load secondary translation model %s: %s", model_name, exc)


@asynccontextmanager
async def lifespan(_: FastAPI):
    global llm_client
    # Load Whisper models first (they allocate the most RAM).
    await asyncio.to_thread(load_models)
    # Then load translation models sequentially to avoid mkl_malloc OOM.
    await asyncio.to_thread(load_secondary_translation_model)
    if LLM_BASE_URL:
        llm_client = httpx.AsyncClient(
            timeout=LLM_TIMEOUT_SECONDS,
            limits=httpx.Limits(max_connections=4, max_keepalive_connections=2),
        )
    try:
        yield
    finally:
        if llm_client is not None:
            await llm_client.aclose()
            llm_client = None


app = FastAPI(title="ClassBridge AI Service", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("WEB_ORIGIN", "http://localhost:3000")],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    memory_stats = correction_memory_stats(CORRECTION_MEMORY_PATH)
    return {
        "status": "ok",
        "mode": MODEL_MODE,
        "whisper_model": WHISPER_MODEL,
        "whisper_accurate_model": WHISPER_ACCURATE_MODEL,
        "whisper_english_model": WHISPER_ENGLISH_MODEL,
        "whisper_threads": WHISPER_CPU_THREADS,
        "whisper_workers": WHISPER_NUM_WORKERS,
        "whisper_accurate_workers": WHISPER_ACCURATE_WORKERS,
        "whisper_accurate_threads": WHISPER_ACCURATE_THREADS,
        "whisper_beams": WHISPER_BEAM_SIZE,
        "whisper_accurate_beams": WHISPER_ACCURATE_BEAM_SIZE,
        "whisper_retry_confidence": WHISPER_RETRY_CONFIDENCE,
        "whisper_vi_retry_confidence": WHISPER_VI_RETRY_CONFIDENCE,
        "whisper_warmup": WHISPER_WARMUP,
        "translation_model": TRANSLATION_MODEL,
        "translation_backend": TRANSLATION_BACKEND,
        "translation_threads": TRANSLATION_CPU_THREADS,
        "translation_workers": TRANSLATION_NUM_WORKERS,
        "translation_beams": TRANSLATION_NUM_BEAMS,
        "translation_max_new_tokens": TRANSLATION_MAX_NEW_TOKENS,
        "translation_quantization": TRANSLATION_QUANTIZATION,
        "correction_memory": memory_stats,
    }


def decode_audio_content(content: bytes) -> np.ndarray:
    """Decode an upload once and reuse the 16 kHz waveform across the pipeline."""
    from faster_whisper.audio import decode_audio

    return np.asarray(
        decode_audio(io.BytesIO(content), sampling_rate=16_000),
        dtype=np.float32,
    )


def has_dynamic_vocal_content(
    audio: np.ndarray, sensitive: bool = False
) -> bool:
    """Reject steady tones before ASR while retaining changing speech/music."""
    audio = np.asarray(audio, dtype=np.float32)
    frame_size, hop_size = 400, 160
    if audio.size < frame_size * 4:
        return False
    frames = np.lib.stride_tricks.sliding_window_view(
        audio, frame_size
    )[::hop_size].copy()
    rms = np.sqrt(np.mean(frames * frames, axis=1) + 1e-9)
    minimum_rms = 0.0035 if sensitive else 0.007
    active = frames[
        rms >= max(minimum_rms, float(np.percentile(rms, 35)) * 0.65)
    ]
    if active.shape[0] < 6:
        return False
    spectra = np.abs(
        np.fft.rfft(active * np.hanning(frame_size), n=512, axis=1)
    )
    spectra /= np.linalg.norm(spectra, axis=1, keepdims=True) + 1e-9
    adjacent_similarity = np.sum(spectra[1:] * spectra[:-1], axis=1)
    spectral_change = float(np.mean(1.0 - adjacent_similarity))
    active_rms = np.sqrt(np.mean(active * active, axis=1) + 1e-9)
    amplitude_variation = float(np.std(active_rms) / (np.mean(active_rms) + 1e-9))
    minimum_spectral_change = 0.006 if sensitive else 0.012
    minimum_amplitude_variation = 0.06 if sensitive else 0.10
    return (
        spectral_change >= minimum_spectral_change
        or amplitude_variation >= minimum_amplitude_variation
    )


def collapse_repeated_phrases(text: str) -> str:
    """Collapse consecutive repeated Whisper word/phrase loops."""
    words = text.split()
    output: list[str] = []
    index = 0
    while index < len(words):
        repeated = False
        maximum_width = min(24, (len(words) - index) // 2)
        for width in range(maximum_width, 0, -1):
            phrase = [word.casefold() for word in words[index:index + width]]
            following = [
                word.casefold()
                for word in words[index + width:index + width * 2]
            ]
            if phrase != following:
                continue
            output.extend(words[index:index + width])
            index += width * 2
            while [
                word.casefold()
                for word in words[index:index + width]
            ] == phrase:
                index += width
            repeated = True
            break
        if not repeated:
            output.append(words[index])
            index += 1
    return " ".join(output)


DEFAULT_VIETNAMESE_PROMPT = None


def normalize_vietnamese_text(text: str) -> str:
    """Normalize Vietnamese smart punctuation and spacing without dictionary modification."""
    if not text:
        return text
    result = text

    # Khử khoảng trắng trước dấu câu trước khi gộp
    result = re.sub(r"\s+([,.?!;:])", r"\1", result)

    # Khử các lỗi ghép dấu câu kép: '?,', '.,', ',.', '?!', '?:', ',,', '..'
    result = re.sub(r'([?!\.])[,;:]+', r'\1', result)
    result = re.sub(r'[,;:]+([?!\.])', r'\1', result)
    result = re.sub(r'([,;:])\1+', r'\1', result)
    result = re.sub(r'\.{2,}', '.', result)
    result = re.sub(r'([.?!])\1+', r'\1', result)

    # Nối câu bị ngắt ngẫu hứng trước các liên từ tiếng Việt
    result = re.sub(r'\.\s+(mà|nhưng|và|thì|để|hoặc|chứ|bởi\s+vì|tại\s+vì|cho\s+nên|vậy\s+nên|nếu)\b', r', \1', result, flags=re.IGNORECASE)

    result = re.sub(r"\s+([,.?!;:])", r"\1", result)
    return result


# Danh sách các mẫu Hallucination YouTube / Whisper spam phổ biến
YOUTUBE_HALLUCINATION_PATTERNS = [
    re.compile(
        r"(?:\|\s*)?(?:Hãy\s+)?(?:like\s+và\s+)?(?:subscribe|subtitles\s+by|thanks?\s+for\s+watching|đăng\s+ký\s+kênh|ủng\s+hộ\s+kênh|bấm\s+chuông\s+theo\s+dõi|chia\s+sẻ\s+video|theo\s+dõi\s+kênh)(?:[\s\w\d_]*(?:Ghiền\s+Mì\s+Gõ|kênh|video|hấp\s+dẫn|tiếp\s+theo|bên\s+dưới|nhé|nha|ạ))?[.,!?]*",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"(?:\|\s*)?Để\s+không\s+bỏ\s+lỡ\s+(?:những\s+)?(?:video|tập|phim|nội\s+dung)[\s\w\d_]*(?:hấp\s+dẫn|tiếp\s+theo|mới\s+nhất)?[.,!?]*",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"(?:\|\s*)?(?:Cảm\s+ơn|Chúc)\s+(?:các\s+)?(?:bạn|quý\s+vị|mọi\s+người)[\s\w\d_]*(?:theo\s+dõi|xem|lắng\s+nghe|đón\s+bảo\s+vệ|hẹn\s+gặp\s+lại|tạm\s+biệt)[\s\w\d_]*[.,!?]*",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"(?:phim\s+sương|học\s+vệ\s+luật|quay\s+man|đoại\s+đất|bác\s+sân|quét\s+trong\s+thái|đôi\s+vào\s+cao\s+đường|đón\s+bảo\s+vệ\s+hội|cảm\s+thắng\s+và\s+tạm\s+biệt)",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:é\s+bem\s+aí|é\s+verdade\s+aí|todos\s+são|você|não|obrigado|de\s+ver\s+ir\s+aí|muito\s+obrigado|está\s+bem|até\s+logo|daí)\b",
        flags=re.IGNORECASE,
    ),
]


# Bộ lọc quét và xóa TOÀN BỘ ký tự ngoại lai (chữ Ấn Độ/Tamil như கொண்டுங்களை, chữ Trung 是, chữ Thái, chữ Nga, chữ Ả Rập...) do Whisper ảo giác
FOREIGN_SCRIPT_PATTERNS = re.compile(
    r"[^\w\s.,?!;:'\"()\/\-%àáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđÀÁẢÃẠÂẦẤẨẪẬĂẰẮẲẴẶÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ]",
    flags=re.IGNORECASE | re.UNICODE,
)


# Bộ lọc tạp âm vô nghĩa dạng lặp từ do nhiễu mic: th th th thong, a a a mem, rhom merem hmt...
NONSENSE_REPETITION_PATTERN = re.compile(
    r"\b(\w{1,3})\s+\1\s+\1\b",
    flags=re.IGNORECASE,
)


_RE_COMBINING_PRE = re.compile(
    r'([a-zA-Z\u00C0-\u1EF9])\s+([\u0300-\u036f\u1dc0-\u1dff\u02b0-\u02ff\u00B4\u02CA\u02CB]+)'
)
_RE_COMBINING_POST = re.compile(
    r'([\u0300-\u036f\u1dc0-\u1dff\u02b0-\u02ff\u00B4\u02CA\u02CB]+)\s+([a-zA-Z\u00C0-\u1EF9])'
)
_RE_COMBINING_ORPHAN = re.compile(r'[\u0300-\u036f\u1dc0-\u1dff\u02b0-\u02ff\u00B4\u02CA\u02CB]')
_RE_MARKDOWN_CHARS = re.compile(r"[*_`#~]+")
_RE_MUSIC_CHARS = re.compile(r"[♪♫]+")
_RE_MULTI_DOTS = re.compile(r"\.{2,}")
_RE_LEADING_PUNCT = re.compile(r"^\s*[\.,\?!]+\s*")
_RE_MULTI_SPACES = re.compile(r"\s+")
_RE_SPACE_PUNCT = re.compile(r"\s+([,.;:!?])")
_RE_WORD_REP = re.compile(r"(\b\w+\b)(?:\s+\1){2,}", flags=re.IGNORECASE)
_RE_WORD_TOKENS = re.compile(r"\b\w+\b", flags=re.UNICODE)
_RE_ALPHANUM_CHARS = re.compile(r"[\w\d]", flags=re.UNICODE)


def normalize_vietnamese_unicode(text: str) -> str:
    """Fix decomposed combining diacritics and rogue accent marks safely without joining words."""
    if not text:
        return ""
    # Chuẩn hóa Unicode NFC đầu tiên để bảo toàn 100% dấu tiếng Việt và tên tiếng Anh
    cleaned = unicodedata.normalize("NFC", text)
    # Loại bỏ ký tự rác / backtick, không xóa dấu nháy đơn '
    cleaned = re.sub(r'[\u0060\u00B4\u02CA\u02CB\u02C6\u02DC\^~|]+', '', cleaned)
    return unicodedata.normalize("NFC", cleaned)


FILLER_WORDS = {
    "uh", "um", "er", "ah", "eh", "oh", "hmm", "huh", "mm", "mmm", "ha", "haha",
    "ừ", "ừm", "ờ", "hở", "hả", "ủa", "nè", "à", "ê", "dạ", "haizz"
}

SILENCE_ARTIFACT_PHRASES = {
    "you", "thank you", "thanks", "thank you so much", "thank you very much",
    "thanks for watching", "thanks for listening", "thank you for watching", "thank you for listening",
    "thank you all", "thanks a lot", "thank you for your time", "thank you for attention",
    "bye", "bye bye", "goodbye", "see you", "see you later", "see you soon", "see you next time",
    "subtitles by", "please subscribe", "like and subscribe", "subscribe", "don't forget to subscribe",
    "translated by", "closed captions", "captioned by",
    "have a good day", "have a great day", "have a nice day",
    "apa yang kamu lakukan", "terima kasih",
    "thời sự", "bản tin", "chào tạm biệt", "hẹn gặp lại",
    "cảm ơn các bạn đã theo dõi", "cảm ơn các bạn đã lắng nghe", "cảm ơn mọi người đã theo dõi",
    "cảm ơn quý vị và các bạn", "cảm ơn đã xem", "chúc các bạn một ngày tốt lành",
    "đăng ký kênh", "nhấn chuông theo dõi", "chia sẻ video", "ủng hộ kênh",
}

VALID_SHORT_COMMANDS = {
    "yes", "no", "ok", "okay", "oke", "stop", "go", "done", "start", "next", "right", "wrong",
    "có", "không", "đúng", "sai", "tiếp", "tiếp tục", "bắt đầu", "dừng", "hết", "xong", "chào",
    "dạ", "vâng", "ừ", "ừm", "ờ", "um", "uh", "dạ vâng", "dạ có", "dạ không", "dạ được", "dạ đúng",
    "dạ thầy", "dạ cô", "ok ạ", "oke ạ", "được", "được ạ", "nghe rõ", "rõ ạ"
}


ACOUSTIC_HALLUCINATION_WORDS = {
    "music", "applause", "laughter", "silence", "whispering", "coughing", "cheering", "screaming",
    "sigh", "sighs", "gasp", "crying", "snicker", "inaudible", "pant", "panting", "breathing", "groan",
    "throat clearing", "clearing throat", "noise", "static", "background noise",
    "âm nhạc", "vỗ tay", "tiếng cười", "tiếng vỗ tay", "tiếng thở", "tiếng thở dài", "tiếng ho", "tiếng ồn", "tiếng quạt"
}

_RE_BRACKETED_ACOUSTIC = re.compile(
    r"\[(?:music|applause|laughter|silence|whispering|coughing|cheering|screaming|sigh|gasp|crying|snicker|inaudible|breathing|groan|noise|static|âm nhạc|vỗ tay|tiếng cười|tiếng thở|tiếng ho|tiếng ồn)\]"
    r"|\((?:music|applause|laughter|silence|whispering|coughing|cheering|screaming|sigh|gasp|crying|snicker|inaudible|breathing|groan|noise|static|âm nhạc|vỗ tay|tiếng cười|tiếng thở|tiếng ho|tiếng ồn)\)"
    r"|[♪♫🎵🎶]+",
    flags=re.IGNORECASE,
)


def is_speech_hallucination(text: str) -> bool:
    """Xác thực transcript an toàn, bảo tồn nguyên vẹn tiếng Việt xen lẫn thuật ngữ tiếng Anh."""
    if not text or not text.strip():
        return True

    # 1. Chuẩn hóa: chữ thường, loại bỏ toàn bộ dấu câu và khoảng trắng dư thừa
    normalized = re.sub(r"[^\w\s]+", "", text.casefold()).strip()
    if not normalized:
        return True

    words = normalized.split()
    if not words:
        return True

    # 2. Câu lệnh ngắn hợp lệ (Yes, No, OK, Có, Không, Đúng, Sai...) -> Hợp lệ
    if normalized in VALID_SHORT_COMMANDS:
        return False

    # 3. Ký hiệu âm thanh phi ngôn ngữ (chỉ chặn khi toàn bộ câu là nhãn âm thanh)
    if normalized in ACOUSTIC_HALLUCINATION_WORDS:
        return True

    # 4. Cụm từ ảo giác khi im lặng hoặc kết thúc video (YouTube / Outro)
    if normalized in SILENCE_ARTIFACT_PHRASES:
        return True
    if any(pat.search(text) for pat in YOUTUBE_HALLUCINATION_PATTERNS):
        return True

    # 5. Toàn bộ câu CHỈ gồm các từ đệm/filler vô nghĩa
    if len(words) <= 3 and all(w in FILLER_WORDS for w in words):
        return True

    # 6. Lặp từ vô nghĩa 3 lần liên tiếp
    if len(words) >= 3 and len(set(words)) == 1:
        return True

    return False




def is_playback_hallucination(
    text: str, context: str, average_log_probability: float
) -> bool:
    return is_speech_hallucination(text)


def clean_recognized_text(text: str) -> str:
    """Remove decoder markup/fragments, YouTube hallucinations, foreign script hallucinations, and mic static gibberish."""
    if not text:
        return ""
    text = normalize_vietnamese_unicode(text)
    if UNSUPPORTED_SCRIPT_PATTERN.search(text):
        return ""
    cleaned = FOREIGN_SCRIPT_PATTERNS.sub("", text)
    cleaned = _RE_MARKDOWN_CHARS.sub(" ", cleaned)
    cleaned = _RE_MUSIC_CHARS.sub(" ", cleaned)
    cleaned = _RE_MULTI_DOTS.sub(" ", cleaned)
    cleaned = _RE_LEADING_PUNCT.sub("", cleaned)
    cleaned = _RE_MULTI_SPACES.sub(" ", cleaned).strip()
    cleaned = _RE_SPACE_PUNCT.sub(r"\1", cleaned)
    cleaned = collapse_repeated_phrases(cleaned)
    cleaned = _RE_WORD_REP.sub(r"\1", cleaned)
    cleaned = normalize_vietnamese_text(cleaned)

    # Xóa triệt để các câu hallucination spam YouTube
    for pat in YOUTUBE_HALLUCINATION_PATTERNS:
        cleaned = pat.sub("", cleaned)
    cleaned = re.sub(r"\s*\|\s*", " ", cleaned)
    cleaned = _RE_MULTI_SPACES.sub(" ", cleaned).strip()

    if is_speech_hallucination(cleaned):
        return ""

    if NONSENSE_REPETITION_PATTERN.search(cleaned):
        return ""

    fragment_tokens = _RE_WORD_TOKENS.findall(cleaned)
    if (
        len(fragment_tokens) >= 2
        and all(len(token) == 1 for token in fragment_tokens)
        and any(token.isalpha() for token in fragment_tokens)
        and any(token.isdigit() for token in fragment_tokens)
    ):
        return ""

    character_count = len(_RE_ALPHANUM_CHARS.findall(cleaned))
    short_speech_tokens = {
        "a", "à", "ạ", "ờ", "ừ", "ý", "i", "ô", "ơ",
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    }
    return (
        cleaned
        if character_count >= 1 or cleaned.casefold() in short_speech_tokens
        else ""
    )





LANGUAGE_WORD_PATTERN = re.compile(r"[^\W\d_]+(?:'[^\W\d_]+)?", re.UNICODE)
VIETNAMESE_CHARACTER_PATTERN = re.compile(
    r"[ăâđêôơưáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩị"
    r"óòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ]",
    re.IGNORECASE,
)
UNSUPPORTED_SCRIPT_PATTERN = re.compile(
    r"[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af"
    r"\u0400-\u04ff\u0600-\u06ff\u0e00-\u0e7f]"
)
ENGLISH_SPECIFIC_LETTERS = re.compile(r"[fjwz]", re.IGNORECASE)
ENGLISH_SUFFIX_PATTERN = re.compile(r"\b\w{4,}(?:tion|ment|ing|ed|ness|ity|ism|able|ible|less|ful|ware|service|services|system|systems|client|server)\b", re.IGNORECASE)


def detect_language_label(
    text: str, dominant_language: str
) -> Literal["en", "vi", "mixed"]:
    """Trả về nhãn ngôn ngữ thực tế từ Whisper ASR."""
    if dominant_language == "en":
        return "en"
    return "vi"


def contains_unsupported_script(text: str) -> bool:
    """The product accepts only Vietnamese/English source text."""
    return bool(UNSUPPORTED_SCRIPT_PATTERN.search(text))


def is_low_confidence_fragment(text: str, confidence: float) -> bool:
    """Reject uncertain decoder guesses on noise while preserving valid short commands."""
    if not text or not text.strip():
        return True
    if is_speech_hallucination(text):
        return True
    norm = re.sub(r"[^\w\s]+", "", text.casefold()).strip()
    if norm in VALID_SHORT_COMMANDS:
        return confidence < 0.20
    word_count = len(norm.split())
    if confidence <= 0.22:
        return True
    if word_count <= 2 and confidence < 0.35:
        return True
    return False


def choose_supported_language(
    probabilities: list[tuple[str, float]], context: str = ""
) -> tuple[str, float]:
    """Chọn EN hoặc VI. Giữ tiếng Việt làm mặc định để bảo tồn code-switching (Anh-Việt lẫn lộn)."""
    scores = dict(probabilities)
    english_probability = scores.get("en", 0.0)
    vietnamese_probability = scores.get("vi", 0.0)

    # Chỉ chuyển hẳn sang EN khi người nói nói 100% tiếng Anh rõ ràng (>= 0.82) và không có âm điệu tiếng Việt (< 0.18)
    # Nếu nói Tiếng Việt hoặc xen kẽ từ CNTT tiếng Anh, dùng "vi" để Whisper nhận diện tiếng Việt chính xác và giữ nguyên từ mượn tiếng Anh
    if english_probability >= 0.82 and vietnamese_probability < 0.18:
        selected = "en"
    else:
        selected = "vi"

    total = english_probability + vietnamese_probability
    confidence = (
        max(english_probability, vietnamese_probability) / total
        if total > 1e-9
        else 0.5
    )
    return selected, confidence


def transcribe_file(
    audio_source: str | BinaryIO,
    language: str,
    context: str = "",
    audio_profile: str = "speech",
    model=None,
    accurate: bool = False,
    rolling_window: bool = False,
) -> tuple[str, str, float, float]:
    if model is None:
        if whisper_fast is None and MODEL_MODE != "demo":
            try:
                load_models()
                model = whisper_fast
            except Exception:
                pass
        if model is None:
            detected = "vi" if language == "vi" else "en"
            return "", detected, 0.0, 0.0

    requested_auto_language = (language == "auto" or not language)
    if requested_auto_language:
        # Tự động nhận diện 100% bằng mạng nơ-ron âm học của Whisper từ giọng nói thực tế
        selected_language = None
    else:
        selected_language = language if language in {"vi", "en"} else None

    supported_language_probabilities: list[tuple[str, float]] = []

    # Tự động khuếch đại âm thanh nhẹ nhàng (Tránh khuếch đại nhiễu mic)
    if isinstance(audio_source, np.ndarray) and audio_source.size > 0:
        peak = float(np.max(np.abs(audio_source)))
        if peak < 0.005:
            return "", selected_language, 0.0, 0.0
        if 0.008 <= peak < 0.50:
            gain = min(2.5, 0.60 / peak)
            audio_source = audio_source * gain

    is_music = audio_profile == "music"
    is_playback = audio_profile in {"hybrid", "media", "music"}
    log_probability_threshold = -1.5 if is_music and accurate else -1.2
    no_speech_threshold = 0.50
    # VAD Silero threshold chuẩn xác chống tiếng ồn mic và chống sinh chữ khi im lặng
    vad_threshold = 0.45
    max_new_tokens = 256 if accurate else 96 if is_music else 160

    # Beam size = 1 cho fast streaming (<30ms), = 2 cho accurate
    beam_size = (
        WHISPER_MUSIC_BEAM_SIZE
        if is_music
        else WHISPER_ACCURATE_BEAM_SIZE
        if accurate
        else WHISPER_BEAM_SIZE
    )

    # Cấu hình ngưỡng âm lượng và độ nhạy VAD
    min_speech_ms = 100
    min_silence_ms = 250
    speech_pad = 300

    # Khi streaming rolling window, tắt vad_filter bên trong transcribe để không bị nuốt phụ âm đầu/cuối của tiếng Việt
    use_vad = False if rolling_window else True
    
    # Prompt định hướng âm điệu tiếng Việt tự nhiên và thuật ngữ CNTT
    prompt_text = context if context else (
        "Xin chào các bạn, hôm nay chúng ta học về công nghệ thông tin, lập trình, hệ thống và phần mềm."
        if selected_language == "vi"
        else "Hello everyone, today we study computer science, software engineering, algorithms, and systems."
        if selected_language == "en"
        else "Xin chào các bạn. Hello everyone, welcome to class."
    )

    segments, info = model.transcribe(
        audio_source,
        language=selected_language,
        beam_size=beam_size,
        best_of=1 if not accurate else 2,
        patience=1.0,
        temperature=0.0,
        repetition_penalty=1.05,
        no_repeat_ngram_size=0,
        without_timestamps=True,
        max_new_tokens=max_new_tokens,
        log_prob_threshold=log_probability_threshold,
        no_speech_threshold=no_speech_threshold,
        vad_filter=use_vad,
        vad_parameters={
            "threshold": vad_threshold,
            "min_speech_duration_ms": min_speech_ms,
            "min_silence_duration_ms": min_silence_ms,
            "speech_pad_ms": speech_pad,
        } if use_vad else None,
        initial_prompt=prompt_text,
        condition_on_previous_text=False,
    )
    detected = getattr(info, "language", None) or selected_language or "vi"
    language_confidence = float(getattr(info, "language_probability", 1.0) or 1.0)
    accepted_segments = []
    confidence_scores = []
    for segment in segments:
        text = clean_recognized_text(segment.text)
        if not text:
            continue
        reliable = (
            segment.avg_logprob >= (-1.3 if accurate else -1.1)
            and segment.no_speech_prob <= 0.45
            and segment.compression_ratio <= 2.4
        )
        if reliable and not is_speech_hallucination(text):
            accepted_segments.append(text)
            confidence_scores.append(
                float(np.exp(max(-5.0, segment.avg_logprob)))
                * (1.0 - float(segment.no_speech_prob))
            )
    confidence = float(np.mean(confidence_scores)) if confidence_scores else 0.0
    transcript = clean_recognized_text(" ".join(accepted_segments))
    if is_low_confidence_fragment(transcript, confidence):
        return "", detected, 0.0, 0.0
    return transcript, detected, confidence, language_confidence



async def recognize_adaptively(
    audio: np.ndarray,
    language: str,
    context: str,
    audio_profile: str,
    allow_accurate: bool = True,
    rolling_window: bool = False,
) -> tuple[str, str, float, Literal["fast", "accurate"]]:
    if MODEL_MODE == "demo":
        transcript, detected, confidence, _ = transcribe_file(
            audio, language, context, audio_profile
        )
        return transcript, detected, confidence, "fast"

    if audio_profile in {"hybrid", "media", "music"} and not await asyncio.to_thread(
        has_dynamic_vocal_content, audio, audio_profile == "hybrid"
    ):
        detected = "vi" if language == "vi" else "en"
        return "", detected, 0.0, "fast"

    # Base is also a fast vocal gate for music. Instrument-only windows return
    # immediately instead of making Small decode noise up to its token limit.
    async with transcription_semaphore:
        fast_result = await asyncio.to_thread(
            transcribe_file,
            audio,
            language,
            context,
            audio_profile,
            whisper_fast,
            False,
            rolling_window,
        )
    transcript, detected, confidence, language_confidence = fast_result
    if is_low_confidence_fragment(transcript, confidence):
        transcript = ""
        confidence = 0.0

    # Streaming partials must return immediately with 1 single inference
    if not allow_accurate:
        return transcript, detected, confidence, "fast"
    retry_confidence = 0.70
    if transcript and confidence >= retry_confidence:
        return transcript, detected, confidence, "fast"
    # Keep short partials responsive, but allow the accurate model to retry a
    # low-confidence microphone sentence once enough audio context exists.
    if (
        audio_profile == "hybrid"
        and transcript
        and confidence >= max(0.22, retry_confidence * 0.65)
        and audio.size < 48_000
    ):
        return transcript, detected, confidence, "fast"
    if audio_profile == "music" and not transcript:
        return transcript, detected, confidence, "fast"
    # A second model pass costs more time than it can recover on sub-second
    # fragments, which are usually acknowledgements or tail audio.
    if audio.size < 36_000:
        return "", detected, 0.0, "fast"

    # Luôn dùng whisper_accurate (mô hình đa ngữ / tiếng Việt đã train) cho accurate pass
    specialist_model = whisper_english if detected == "en" else whisper_accurate
    specialist_language = detected if language == "auto" else language
    async with accurate_transcription_semaphore:
        accurate_result = await asyncio.to_thread(
            transcribe_file,
            audio,
            specialist_language,
            context,
            audio_profile,
            specialist_model,
            True,
            False,
        )
    (
        accurate_text,
        accurate_language,
        accurate_confidence,
        accurate_language_confidence,
    ) = accurate_result
    if is_low_confidence_fragment(accurate_text, accurate_confidence):
        accurate_text = ""
        accurate_confidence = 0.0
    if accurate_text and (
        not transcript
        or accurate_confidence >= confidence * 0.85
        or (
            language == "auto"
            and accurate_language_confidence >= language_confidence + 0.08
        )
    ):
        return (
            accurate_text,
            accurate_language,
            accurate_confidence,
            "accurate",
        )
    return transcript, detected, confidence, "fast"


async def recognize_speech(
    audio: np.ndarray,
    language: str,
    context: str,
    audio_profile: str,
    allow_accurate: bool = True,
    rolling_window: bool = False,
) -> tuple[str, str, float, Literal["fast", "accurate"], int]:
    """Recognize EN/VI speech without diarization or speaker embeddings."""
    recognition_result = await recognize_adaptively(
        audio, language, context, audio_profile, allow_accurate, rolling_window
    )
    return (*recognition_result, 1)


async def correct_with_llm(text: str, language: str, context: str) -> str:
    corrected_from_memory = apply_correction_memory(
        text,
        language,
        CORRECTION_MEMORY_PATH,
    )
    if not LLM_BASE_URL or not corrected_from_memory:
        return corrected_from_memory
    if language == "vi":
        system = (
            "Bạn là chuyên gia hiệu đính tiếng Việt và mô hình sửa lỗi nhận dạng giọng nói. "
            "Hãy sửa tất cả các lỗi chính tả, thiếu dấu thanh, nhầm lẫn phát âm vùng miền "
            "(như l/n, ch/tr, s/x, r/d/gi, v/d, thiếu dấu câu) trong bản ghi lời nói tiếng Việt. "
            "Giữ nguyên 100% ý nghĩa, từ ngữ học thuật và tên riêng. Chỉ trả về văn bản tiếng Việt đã được hiệu đính chuẩn."
        )
    else:
        system = (
            "You correct a continuous transcript from one university lecturer, including "
            "regional or non-native accents. Use the recent context to fix only clear "
            "speech-recognition errors, punctuation, casing, and academic terminology. "
            "Never summarize, paraphrase, or translate. Preserve meaning, language, names, "
            "formulas, and code. Return corrected transcript text only."
        )
    user = (
        f"Language: {language}\nRecent context: {context[-1200:]}"
        f"\nTranscript: {corrected_from_memory}"
    )
    headers = {"Authorization": f"Bearer {LLM_API_KEY}"} if LLM_API_KEY else {}
    client = llm_client
    owns_client = client is None
    if client is None:
        client = httpx.AsyncClient(timeout=LLM_TIMEOUT_SECONDS)
    try:
        response = await client.post(
            f"{LLM_BASE_URL}/chat/completions",
            headers=headers,
            json={
                "model": LLM_MODEL,
                "temperature": 0.1,
                "max_tokens": 400,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except (httpx.HTTPError, KeyError, IndexError, TypeError, AttributeError) as error:
        # Transcript correction is optional; an unavailable LLM must not stop
        # live captions or translation.
        logger.warning("LLM correction failed; using the raw transcript: %s", error)
        return corrected_from_memory
    finally:
        if owns_client:
            await client.aclose()


def _contains_mixed_language(text: str) -> bool:
    """Heuristic check for mixed English/Vietnamese speech traces."""
    return detect_language_label(text, "vi") == "mixed"


def needs_llm_review(corrected_text: str, translation: str, confidence: float) -> bool:
    """Only send difficult or low-confidence lines to the LLM for review."""
    if confidence < 0.55:
        return True
    if _contains_mixed_language(corrected_text):
        return True
    if re.search(
        r"\b(api|sql|java|python|classbridge|whisper|llm|docker|yaml|json|kubernetes|architecture|microservice|vector|prompt)\b",
        corrected_text,
        flags=re.IGNORECASE,
    ):
        return True
    if translation and len(translation.strip().split()) >= 3:
        source_word_count = len(corrected_text.strip().split())
        translation_word_count = len(translation.strip().split())
        if translation_word_count < 2 or source_word_count > translation_word_count * 1.8:
            return True
    if not translation or len(translation.strip().split()) < 3:
        return True
    return False


async def review_translation_with_llm(
    corrected_text: str, translation: str, context: str = ""
) -> str:
    """Review a completed translation and keep the original meaning, terminology, and entities."""
    llm_url = LLM_BASE_URL
    if not llm_url:
        return translation

    headers = {"Authorization": f"Bearer {LLM_API_KEY}"} if LLM_API_KEY else {}
    client = llm_client
    owns_client = client is None
    if client is None:
        client = httpx.AsyncClient(timeout=LLM_TIMEOUT_SECONDS)
    try:
        response = await client.post(
            f"{llm_url}/chat/completions",
            headers=headers,
            json={
                "model": LLM_MODEL,
                "temperature": 0.0,
                "max_tokens": 400,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are an English-Vietnamese translation reviewer. "
                            "Only fix mistranslations and awkward phrasing. "
                            "Do not add new content, remove original meaning, or change named entities and technical terms. "
                            "Return only the corrected translation sentence."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Course: {TRANSLATION_COURSE_CONTEXT or 'Not specified'}\n"
                            f"Topic: {TRANSLATION_TOPIC_CONTEXT or 'Not specified'}\n"
                            f"Previous context: {context[-1200:] or 'None'}\n"
                            f"Source: {corrected_text}\nTranslation: {translation}"
                        ),
                    },
                ],
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except (httpx.HTTPError, KeyError, IndexError, TypeError, AttributeError) as error:
        logger.warning("LLM review failed; keeping the EnViT5 translation: %s", error)
        return translation
    finally:
        if owns_client:
            await client.aclose()


@lru_cache(maxsize=512)
def translate_with_opus(normalized: str, source_language: str) -> str:
    """Translate using the Helsinki-NLP MarianMT model (opus-mt).

    MarianMT is fast and specialized for EN↔VI — it complements envit5 well
    as it has stronger coverage of common conversational and lecture vocabulary.
    """
    opus_key = "opus_en_vi" if source_language == "en" else "opus_vi_en"
    if opus_key not in secondary_translator_models:
        return ""
    import torch
    tokenizer = secondary_translator_tokenizers[opus_key]
    model = secondary_translator_models[opus_key]
    inputs = tokenizer(normalized, return_tensors="pt", truncation=True, max_length=256)
    input_len = int(inputs["input_ids"].shape[-1])
    with torch.inference_mode():
        generated = model.generate(
            **inputs,
            max_new_tokens=min(128, max(48, int(input_len * 2.5))),
            num_beams=1,
            do_sample=False,
            use_cache=True,
            early_stopping=True,
            repetition_penalty=1.1,
        )
    return tokenizer.batch_decode(generated, skip_special_tokens=True)[0].strip()


def _pick_better_translation(primary: str, secondary: str, source: str) -> str:
    """Choose the better of two translations using lightweight heuristics.

    Prefer whichever result:
    1. Has more words (longer usually means more complete)
    2. Is not obviously empty or too short compared to source
    3. Does not start with source-language text (copy-through error)

    Falls back to primary if secondary is unavailable.
    """
    if not secondary:
        return primary
    if not primary:
        return secondary
    src_words = len(source.split())
    p_words = len(primary.split())
    s_words = len(secondary.split())
    # A very short result relative to source is likely truncated or copy-through.
    p_ratio = p_words / max(src_words, 1)
    s_ratio = s_words / max(src_words, 1)
    # If primary is way too short and secondary is more complete, use secondary.
    if p_ratio < 0.35 and s_ratio >= 0.5:
        return secondary
    # Otherwise pick whichever is longer (more complete), but don't let
    # a slightly longer secondary override a clearly adequate primary.
    if s_words > p_words * 1.25 and s_ratio >= 0.45:
        return secondary
    return primary


TRANSLATION_GLOSSARY_EN_VI = {
    "black-box testing": "kiểm thử hộp đen",
    "white-box testing": "kiểm thử hộp trắng",
    "boundary value analysis": "phân tích giá trị biên",
    "boundary value": "giá trị biên",
    "control flow graph": "đồ thị luồng điều khiển",
    "equivalence partitioning": "phân vùng tương đương",
    "foreign key": "khóa ngoại",
    "primary key": "khóa chính",
    "software testing": "kiểm thử phần mềm",
    "test case": "ca kiểm thử",
    "unit test": "kiểm thử đơn vị",
    "integration test": "kiểm thử tích hợp",
    "performance test": "kiểm thử hiệu năng",
    "regression test": "kiểm thử hồi quy",
    "acceptance test": "kiểm thử chấp nhận",
    "artificial intelligence": "trí tuệ nhân tạo",
    "machine learning": "học máy",
    "deep learning": "học sâu",
    "neural network": "mạng nơ-ron",
    "natural language processing": "xử lý ngôn ngữ tự nhiên",
    "speech recognition": "nhận dạng giọng nói",
    "database": "cơ sở dữ liệu",
    "relational database": "cơ sở dữ liệu quan hệ",
    "source code": "mã nguồn",
    "operating system": "hệ điều hành",
    "distributed system": "hệ thống phân tán",
    "cloud computing": "điện toán đám mây",
    "data structure": "cấu trúc dữ liệu",
    "algorithm": "thuật toán",
    "software engineering": "công nghệ phần mềm",
    "object-oriented programming": "lập trình hướng đối tượng",
}


def apply_translation_glossary(
    source: str, translation: str, source_language: str
) -> str:
    """Normalize known terms in the translation without touching original text."""
    if not translation:
        return translation
    mapping = (
        TRANSLATION_GLOSSARY_EN_VI
        if source_language == "en"
        else {vi: en for en, vi in TRANSLATION_GLOSSARY_EN_VI.items()}
    )
    source_folded = source.casefold()
    result = translation
    for source_term, target_term in mapping.items():
        if source_term.casefold() not in source_folded:
            continue
        result = re.sub(
            rf"(?<!\w){re.escape(source_term)}(?!\w)",
            target_term,
            result,
            flags=re.IGNORECASE,
        )

    # Khi câu tiếng Việt chứa thuật ngữ tiếng Anh (code-switching), đảm bảo bản dịch EN giữ đúng thuật ngữ đó
    if source_language == "vi":
        for en_term in TRANSLATION_GLOSSARY_EN_VI:
            if en_term.casefold() in source_folded:
                words = en_term.split()
                if len(words) >= 2:
                    suffix = " ".join(words[1:])
                    result = re.sub(
                        rf"\b\w+\s+{re.escape(suffix)}\b",
                        en_term,
                        result,
                        flags=re.IGNORECASE,
                    )
                else:
                    result = re.sub(
                        rf"\b\w*{re.escape(en_term[2:])}\b",
                        en_term,
                        result,
                        flags=re.IGNORECASE,
                    )

    return result


@lru_cache(maxsize=1024)
def translate_single_sentence(sentence: str, source_language: str) -> str:
    sentence = sentence.strip()
    if not sentence:
        return ""

    # Loại bỏ triệt để các vết ba chấm (...) gây cắt từ
    sentence = re.sub(r"\.{2,}", " ", sentence).strip()
    if not sentence:
        return ""

    if sentence[-1] not in ".!?":
        sentence += "."

    # Direction is determined by the dominant language of the finalized
    # utterance. Mixed technical terms stay inside the sentence and are handled
    # by the bilingual model instead of flipping direction word by word.
    # Thử opus-mt trước (nhanh hơn), nhưng luôn so sánh với envit5 để
    # tránh trường hợp opus-mt dịch sai câu dài hoặc câu VI→EN phức tạp.
    opus_key = "opus_en_vi" if source_language == "en" else "opus_vi_en"
    opus_result = ""
    if secondary_translator_models and opus_key in secondary_translator_models:
        try:
            opus_result = translate_with_opus(sentence, source_language)
        except Exception:
            opus_result = ""

    envit5_result = translate_normalized(sentence, source_language)

    # Lọc bỏ ảo giác xin lỗi giả mạo từ opus/envit5 khi câu gốc không hề có từ xin lỗi
    if re.search(r"^(?:im\s+sorry|i'?m\s+sorry|sorry|i\s+am\s+sorry|i'?m\s+afraid)[,\.\s]*(?:i'?m\s+afraid)?[,\.\s]*$", opus_result.strip(), re.I):
        if not re.search(r"\b(xin\s*lỗi|tiếc\s*là|e\s*rằng|sorry)\b", sentence, re.I):
            opus_result = ""

    if re.search(r"^(?:im\s+sorry|i'?m\s+sorry|sorry|i\s+am\s+sorry|i'?m\s+afraid)[,\.\s]*(?:i'?m\s+afraid)?[,\.\s]*$", envit5_result.strip(), re.I):
        if not re.search(r"\b(xin\s*lỗi|tiếc\s*là|e\s*rằng|sorry)\b", sentence, re.I):
            envit5_result = ""

    # Nếu chỉ có một kết quả, dùng cái đó
    if not opus_result:
        return envit5_result
    if not envit5_result:
        return opus_result

    # Ensemble: chọn bản dịch tốt hơn dựa trên độ dài tương đối
    return _pick_better_translation(envit5_result, opus_result, sentence)


def split_text_into_chunks(text: str, max_words: int = 10) -> list[str]:
    """
    Tách đoạn văn thành các cụm nhỏ từ 8-10 từ dựa theo dấu câu (.!?), liên từ (because, and, so, when, I...),
    hoặc giới hạn số từ tối đa, đảm bảo MarianMT/EnViT5 dịch trọn vẹn 100% không bỏ sót bất kỳ từ nào.
    """
    if not text:
        return []

    raw_sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    final_chunks = []

    for sentence in raw_sentences:
        words = sentence.split()
        if len(words) <= max_words:
            final_chunks.append(sentence)
        else:
            # Tách theo liên từ hoặc đại từ nếu đoạn văn dài không có dấu chấm
            sub_splits = re.split(
                r"(?<=\s)(?=(?:because|so|but|and|or|however|although|when|while|if|that|which|who|I|you|he|she|we|they|let's)\b)",
                sentence,
                flags=re.IGNORECASE,
            )
            current_chunk: list[str] = []
            for part in sub_splits:
                part_words = part.strip().split()
                if not part_words:
                    continue
                if len(current_chunk) + len(part_words) > max_words and current_chunk:
                    final_chunks.append(" ".join(current_chunk))
                    current_chunk = list(part_words)
                else:
                    current_chunk.extend(part_words)
            if current_chunk:
                final_chunks.append(" ".join(current_chunk))

    return [c.strip() for c in final_chunks if c.strip()]


def translate_text(text: str, source_language: str) -> str:
    cleaned_input = remove_repetitions(text)
    normalized = " ".join(cleaned_input.split())
    if not normalized:
        return ""
    if not re.search(r"[^\W\d_]", normalized, flags=re.UNICODE):
        return normalized

    # Tách thành các cụm nhỏ 8-10 từ để dịch ĐẦY ĐỦ 100% toàn bộ bài giảng
    # Modern local translation models handle a normal sentence in one pass.
    # Ten-word chunks multiplied generation cost and destroyed sentence
    # context. Only split genuinely long lecture turns.
    chunks = split_text_into_chunks(normalized, max_words=40)
    if not chunks:
        res = translate_single_sentence(normalized, source_language)
        return remove_repetitions(res)

    translated_parts = []
    for c in chunks:
        trans = translate_single_sentence(c, source_language)
        if trans:
            translated_parts.append(trans)

    result = " ".join(translated_parts) if translated_parts else translate_single_sentence(normalized, source_language)
    result = apply_translation_glossary(normalized, result, source_language)
    return remove_repetitions(result)



@lru_cache(maxsize=1024)
def translate_normalized(normalized: str, source_language: str) -> str:
    if not normalized or not normalized.strip():
        return ""
    if MODEL_MODE == "demo":
        return normalized

    import torch

    model_key = TRANSLATION_BACKEND
    load_translation_model()

    tokenizer = translator_tokenizers[model_key]
    model = translator_models[model_key]
    if model_key == "nllb":
        source_code = "eng_Latn" if source_language == "en" else "vie_Latn"
        target_code = "vie_Latn" if source_language == "en" else "eng_Latn"
        tokenizer.src_lang = source_code
        model_input = normalized
    else:
        target_code = None
        model_input = f"{source_language}: {normalized}"
    inputs = tokenizer(model_input, return_tensors="pt", truncation=True, max_length=256)
    generation_options = {}
    if target_code:
        generation_options["forced_bos_token_id"] = tokenizer.convert_tokens_to_ids(
            target_code
        )
    input_token_count = int(inputs["input_ids"].shape[-1])
    # Allow up to 2.5× the source length so longer sentences are never cut
    # short. The TRANSLATION_MAX_NEW_TOKENS ceiling (default 128) prevents
    # runaway generation on very short inputs that accidentally get a huge cap.
    max_new_tokens = min(
        TRANSLATION_MAX_NEW_TOKENS, max(48, int(input_token_count * 2.5))
    )
    with torch.inference_mode():
        generated = model.generate(
            **inputs,
            **generation_options,
            max_new_tokens=max_new_tokens,
            num_beams=TRANSLATION_NUM_BEAMS,
            do_sample=False,
            use_cache=True,
            early_stopping=True,
            repetition_penalty=1.15,
            no_repeat_ngram_size=4,
        )
    result = tokenizer.batch_decode(generated, skip_special_tokens=True)[0].strip()
    if model_key == "envit5":
        target_prefix = "vi:" if source_language == "en" else "en:"
        if result.lower().startswith(target_prefix):
            result = result[len(target_prefix):].strip()
    # Post-process: strip residual source-language prefix if the model output
    # accidentally includes it (envit5 sometimes copies the input label).
    if model_key == "envit5" and ":" in result[:4]:
        result = result.split(":", 1)[-1].strip()

    # Tối ưu: Loại bỏ triệt để các vòng lặp lặp từ (ví dụ hi hi hi hi... hoặc Bài giảng tiếng Bài giảng tiếng...)
    result = collapse_repeated_phrases(result)
    result = re.sub(r"(\b\w+\b)(?:\s+\1){2,}", r"\1", result, flags=re.IGNORECASE)
    return result


@app.post("/v1/transcribe", response_model=TranscriptionResult)
async def transcribe_only(
    audio: UploadFile = File(...),
    source_language: Literal["auto", "en", "vi"] = Form("auto"),
    audio_profile: Literal["speech", "hybrid", "media", "music"] = Form("speech"),
    context: str = Form(""),
):
    started = time.perf_counter()
    content = await audio.read()
    if not content:
        raise HTTPException(status_code=400, detail="Audio is empty")
    if len(content) > 12 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio chunk is too large")

    try:
        decoded_audio = await asyncio.to_thread(decode_audio_content, content)
        (
            transcript,
            detected_language,
            confidence,
            recognition_mode,
            speaker_id,
        ) = await recognize_speech(
            decoded_audio,
            source_language,
            context,
            audio_profile,
        )
        # The live source line must not wait on an optional remote LLM. Apply
        # the local correction memory synchronously; deeper LLM correction is
        # still available on the combined non-live pipeline endpoint.
        corrected = apply_correction_memory(
            transcript,
            detected_language,
            CORRECTION_MEMORY_PATH,
        )
    except (InvalidDataError, ValueError, Exception) as error:
        logger.warning("Audio decoding or ASR processing failed: %s", error)
        return TranscriptionResult(
            transcript="",
            corrected_text="",
            source_language="vi" if source_language == "vi" else "en",
            latency_ms=round((time.perf_counter() - started) * 1000),
            speaker_id=1,
            recognition_mode="fast",
            confidence=0.0,
            demo=MODEL_MODE == "demo",
        )

    return TranscriptionResult(
        transcript=transcript,
        corrected_text=corrected,
        source_language=detected_language,
        latency_ms=round((time.perf_counter() - started) * 1000),
        speaker_id=speaker_id,
        recognition_mode=recognition_mode,
        confidence=round(confidence, 4),
        demo=MODEL_MODE == "demo",
    )


@app.post("/v1/translate", response_model=TranslationResult)
async def translate_only(
    text: str = Form(...),
    source_language: Literal["en", "vi"] = Form("en"),
):
    started = time.perf_counter()
    async with translation_semaphore:
        translation = await asyncio.to_thread(
            translate_text, text, source_language
        )
    return TranslationResult(
        translation=translation,
        source_language=source_language,
        latency_ms=round((time.perf_counter() - started) * 1000),
    )


@app.post("/v1/transcribe-translate", response_model=PipelineResult)
async def transcribe_translate(
    audio: UploadFile = File(...),
    source_language: Literal["auto", "en", "vi"] = Form("auto"),
    audio_profile: Literal["speech", "hybrid", "media", "music"] = Form("speech"),
    context: str = Form(""),
):
    started = time.perf_counter()
    content = await audio.read()
    if not content:
        raise HTTPException(status_code=400, detail="Audio is empty")
    if len(content) > 12 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio chunk is too large")

    try:
        decoded_audio = await asyncio.to_thread(decode_audio_content, content)
        (
            transcript,
            detected_language,
            confidence,
            recognition_mode,
            speaker_id,
        ) = await recognize_speech(
            decoded_audio,
            source_language,
            context,
            audio_profile,
        )
        corrected = apply_correction_memory(
            transcript,
            detected_language,
            CORRECTION_MEMORY_PATH,
        )

        if not corrected:
            envit5_translation = ""
            final_translation = ""
            should_review = False
        else:
            async with translation_semaphore:
                envit5_translation = await asyncio.to_thread(
                    translate_text, corrected, detected_language
                )
            should_review = needs_llm_review(corrected, envit5_translation, confidence)
            final_translation = envit5_translation
            if should_review:
                final_translation = await review_translation_with_llm(
                    corrected,
                    envit5_translation,
                )
        ai_used = bool(LLM_BASE_URL) and should_review
    except (InvalidDataError, ValueError, Exception) as error:
        logger.warning("Pipeline audio decoding or ASR processing failed: %s", error)
        return PipelineResult(
            transcript="",
            corrected_text="",
            corrected_transcript="",
            raw_transcript="",
            envit5_translation="",
            final_translation="",
            translation="",
            source_language="vi" if source_language == "vi" else "en",
            latency_ms=round((time.perf_counter() - started) * 1000),
            speaker_id=1,
            recognition_mode="fast",
            confidence=0.0,
            ai_used=False,
            demo=MODEL_MODE == "demo",
        )

    return PipelineResult(
        transcript=transcript,
        corrected_text=corrected,
        corrected_transcript=corrected,
        raw_transcript=transcript,
        envit5_translation=envit5_translation,
        final_translation=final_translation,
        translation=final_translation,
        source_language=detected_language,
        latency_ms=round((time.perf_counter() - started) * 1000),
        speaker_id=speaker_id,
        recognition_mode=recognition_mode,
        confidence=round(confidence, 4),
        ai_used=ai_used,
        demo=MODEL_MODE == "demo",
    )


class TranslationRequest(BaseModel):
    text: str
    source_language: str = "vi"
    context: str = ""


@app.post("/api/translate")
@app.post("/v1/translate")
async def api_translate(req: TranslationRequest):
    started = time.perf_counter()
    if not req.text.strip():
        return {"translation": "", "source_language": req.source_language, "latency_ms": 0}
    try:
        async with translation_semaphore:
            translated = await asyncio.to_thread(
                translate_text, req.text, req.source_language
            )
        translated = apply_translation_glossary(
            req.text, translated, req.source_language
        )
        return {
            "translation": translated,
            "source_language": req.source_language,
            "latency_ms": round((time.perf_counter() - started) * 1000),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))



# ===========================================================================
# ── WebSocket Streaming Pipeline (<7s latency) ──────────────────────────────
# ===========================================================================

# Active WebSocket streaming sessions: session_id → metadata
_stream_sessions: dict[str, dict] = {}
_stream_sessions_lock = asyncio.Lock()

STREAM_MAX_SESSIONS = int(os.getenv("STREAM_MAX_SESSIONS", "20"))
STREAM_SESSION_TTL = int(os.getenv("STREAM_SESSION_TTL", "7200"))  # 2 giờ
STREAM_SAMPLE_RATE = 16_000
STREAM_UPDATE_SECONDS = max(
    0.25, min(0.7, float(os.getenv("STREAM_UPDATE_SECONDS", "0.3")))
)
STREAM_UPDATE_SAMPLES = int(STREAM_SAMPLE_RATE * STREAM_UPDATE_SECONDS)
STREAM_ROLLING_SECONDS = max(
    8.0, min(20.0, float(os.getenv("STREAM_ROLLING_SECONDS", "15.0")))
)
STREAM_MAX_ROLLING_SAMPLES = int(STREAM_SAMPLE_RATE * STREAM_ROLLING_SECONDS)
STREAM_FINAL_MAX_SAMPLES = int(
    STREAM_SAMPLE_RATE * float(os.getenv("STREAM_FINAL_MAX_SECONDS", "30"))
)
STREAM_FINAL_SILENCE_SECONDS = max(
    0.8, min(3.0, float(os.getenv("STREAM_FINAL_SILENCE_SECONDS", "1.0")))
)
STREAM_PRE_ROLL_SAMPLES = int(
    STREAM_SAMPLE_RATE * float(os.getenv("STREAM_PRE_ROLL_SECONDS", "0.8"))
)
STREAM_POST_ROLL_SAMPLES = int(
    STREAM_SAMPLE_RATE * float(os.getenv("STREAM_POST_ROLL_SECONDS", "0.5"))
)
STREAM_FINAL_WORDS = max(30, int(os.getenv("STREAM_FINAL_WORDS", "50")))
STREAM_FINAL_ACCURATE = os.getenv(
    "STREAM_FINAL_ACCURATE",
    "false",
).lower() in {"1", "true", "yes"}
STREAM_MIN_SPEECH_RMS = max(
    0.008, float(os.getenv("STREAM_MIN_SPEECH_RMS", "0.010"))
)

STREAM_TRANSLATION_TAIL_SECONDS = max(
    1.0, float(os.getenv("STREAM_TRANSLATION_TAIL_SECONDS", "5"))
)
STREAM_EVENT_QUEUE_SIZE = max(32, int(os.getenv("STREAM_EVENT_QUEUE_SIZE", "256")))


@app.post("/stream/start")
async def stream_start(
    session_id: str = Form(default=""),
    language: str = Form(default="auto"),
):
    """
    Khởi tạo một streaming session và trả về session_id + join_code cho sinh viên.
    Dùng session_id cho Giảng viên /ws/stream/{session_id}
    Dùng join_code cho Sinh viên /ws/classroom/{join_code}
    """
    sid = session_id.strip() or str(uuid.uuid4())
    async with _stream_sessions_lock:
        now = time.monotonic()
        expired = [
            k for k, v in _stream_sessions.items()
            if now - v.get("created_at", now) > STREAM_SESSION_TTL
        ]
        for k in expired:
            del _stream_sessions[k]
            await session_manager.remove_session(k)
        if len(_stream_sessions) >= STREAM_MAX_SESSIONS:
            raise HTTPException(
                status_code=429,
                detail=f"Đã đạt giới hạn {STREAM_MAX_SESSIONS} streaming sessions đồng thời",
            )
        if sid in _stream_sessions:
            raise HTTPException(status_code=409, detail="Streaming session đã tồn tại")
        cls_session = await session_manager.create_session(sid, language)
        _stream_sessions[sid] = {
            "language": language,
            "created_at": now,
            "context": "",
            "join_code": cls_session.join_code,
        }
    return {
        "session_id": sid,
        "join_code": cls_session.join_code,
        "ws_url": f"/ws/stream/{sid}",
        "student_ws_url": f"/ws/classroom/{cls_session.join_code}",
        "language": language,
        "created_at": int(time.time()),
    }


@app.get("/classroom/join/{join_code}")
async def classroom_join_info(join_code: str):
    """Kiểm tra mã lớp học và trả về thông tin phòng học cho sinh viên."""
    session = await session_manager.get_by_code(join_code)
    if not session:
        raise HTTPException(status_code=404, detail=f"Mã lớp học '{join_code}' không tồn tại hoặc đã kết thúc.")
    return {
        "session_id": session.session_id,
        "join_code": session.join_code,
        "language": session.language,
        "student_count": len(session.student_sockets),
        "history": session.subtitles_history[-20:],
        "ws_url": f"/ws/classroom/{session.join_code}",
    }


@app.websocket("/ws/classroom/{join_code}")
async def ws_classroom_student(websocket: WebSocket, join_code: str):
    """WebSocket read-only dành cho Sinh viên tham gia xem phụ đề lớp học trực tiếp."""
    session = await session_manager.get_by_code(join_code)
    if not session:
        await websocket.close(code=4004, reason="Mã lớp học không tồn tại.")
        return

    await websocket.accept()
    session.student_sockets.add(websocket)
    logger.info("[WS Student] Sinh viên tham gia lớp %s (Tổng: %d)", join_code, len(session.student_sockets))

    try:
        # Gửi lịch sử phụ đề gần nhất khi mới vào phòng
        await websocket.send_json({
            "type": "init_history",
            "history": session.subtitles_history[-20:],
            "join_code": join_code,
        })
        while True:
            event = await websocket.receive()
            if event.get("type") == "websocket.disconnect":
                break
            raw = event.get("text") or ""
            # Sinh viên có thể gửi ping keepalive
            if "ping" in raw:
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        pass
    finally:
        session.student_sockets.discard(websocket)
        logger.info("[WS Student] Sinh viên rời lớp %s", join_code)


@app.websocket("/ws/stream/{session_id}")
async def ws_stream(websocket: WebSocket, session_id: str):
    """
    WebSocket Streaming Pipeline – Nhận audio binary → Trả về incremental partial & final transcript + dịch song ngữ.

    Protocol:
        Client → Server: binary audio chunks (PCM float32 LE, 16kHz, mono)
                         hoặc JSON {"action": "ping"} / {"action": "end"}
        Server → Client: JSON {
            "type"         : "partial" | "final" | "translation" | "error" | "pong" | "session_end",
            "stable_text"  : str,         # Lời đã được xác nhận (khóa)
            "unstable_text": str,         # Lời đang gõ/thay đổi
            "transcript"   : str,         # Toàn bộ câu
            "translation"  : str,         # Bản dịch song ngữ
            "language"     : "vi" | "en",
            "speaker_id"   : int,
            "confidence"   : float,
            "latency_ms"   : int,
            "mode"         : "fast" | "accurate"
        }
    """
    # Kiểm tra session đã được đăng ký chưa
    async with _stream_sessions_lock:
        meta = _stream_sessions.get(session_id)
    if meta is None:
        await websocket.close(code=4004, reason="Session không tồn tại. Gọi POST /stream/start trước.")
        return

    await websocket.accept()
    session_language = meta.get("language", "vi")
    if session_language not in {"vi", "en", "auto"}:
        session_language = "vi"
    context = meta.get("context", "")

    logger.info("[WS Stream] Session %s bắt đầu (language_mode=%s)", session_id[:16], session_language)


    import json as _json

    cls_session = await session_manager.get_by_id(session_id)
    event_queue: asyncio.Queue[tuple[str, bytes | None]] = asyncio.Queue(
        maxsize=STREAM_EVENT_QUEUE_SIZE
    )
    translation_queue: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue()
    send_lock = asyncio.Lock()
    teacher_connected = True
    audio_buffer = bytearray()
    # ── Audio diagnostics ─────────────────────────────────────────────────
    # Nếu microphone/PCM pipeline lỗi, client vẫn kết nối WS nhưng không bao giờ
    # gửi audio.  Các counter này giúp phát hiện "AI phỏng đoán" do thiếu
    # audio thật (Whisper hallucination trên silence).
    audio_chunks_received = 0
    audio_bytes_received = 0
    speech_chunks_detected = 0
    first_audio_logged = False
    no_audio_warned = False
    session_opened_at = time.monotonic()
    sliding_pcm = np.zeros(0, dtype=np.float32)
    segment_pcm = np.zeros(0, dtype=np.float32)
    pre_roll_pcm = np.zeros(0, dtype=np.float32)
    post_roll_pcm = np.zeros(0, dtype=np.float32)
    stabilizer = TranscriptStabilizer(min_stable_count=2, unstable_tail_words=1)
    silence_seconds = 0.0
    chunk_id = 0
    segment_id_counter = 0
    current_segment_id = 0
    current_revision = 0
    current_text = ""
    # Initialize language from session_language, not hardcoded "vi".
    # AUTO mode starts unknown; VI/EN modes lock immediately.
    current_language = session_language if session_language in {"vi", "en"} else "vi"
    current_language_label: Literal["en", "vi", "mixed"] = "vi"
    pending_language = ""
    pending_language_count = 0
    current_speaker_id = 1
    current_confidence = 0.0
    current_mode: Literal["fast", "accurate"] = "fast"
    current_latency_ms = 0
    asr_sequence = 0
    noise_floor = 0.0012
    end_reason = "disconnect"
    recent_finalized: list[tuple[str, float]] = []
    asr_in_flight = False

    async def send_teacher(message: dict) -> bool:
        nonlocal teacher_connected
        if not teacher_connected:
            return False
        try:
            async with send_lock:
                await websocket.send_json(message)
            return True
        except Exception:
            teacher_connected = False
            return False

    async def broadcast(message: dict) -> None:
        if cls_session:
            await cls_session.broadcast(message)

    segment_states: dict[int, dict[str, Any]] = {}

    def get_segment_state(seg_id: int) -> dict[str, Any]:
        state = segment_states.get(seg_id)
        if state is None:
            state = {"last_revision": 0, "final_committed": False}
            segment_states[seg_id] = state
        return state

    async def translation_worker() -> None:
        while True:
            job = await translation_queue.get()
            try:
                if job is None:
                    return
                started = time.perf_counter()
                try:
                    async with translation_semaphore:
                        translated = await asyncio.to_thread(
                            translate_text,
                            str(job["text"]),
                            str(job["language"]),
                        )
                except Exception as exc:
                    logger.warning("[WS Stream] Translation lỗi: %s", exc)
                    translated = ""
                translated = apply_translation_glossary(
                    str(job["text"]), translated, str(job["language"])
                )

                # Low-latency Translation: Gửi bản dịch neural/glossary ngay lập tức
                translation_msg = {
                    "type": "translation",
                    "session_id": session_id,
                    "segment_id": job["segment_id"],
                    "sequence": -1,
                    "timestamp_ms": int(time.time() * 1000),
                    "translation": translated,
                    "language": job["language"],
                    "language_label": job["language_label"],
                    "speaker_id": job["speaker_id"],
                    "latency_ms": round((time.perf_counter() - started) * 1000),
                }
                print(f"[TRANSLATION] {translated}")
                await send_teacher(translation_msg)

                if cls_session:
                    for history_item in reversed(cls_session.subtitles_history):
                        if history_item.get("segment_id") == job["segment_id"]:
                            history_item["translation"] = translated
                            break
                    await cls_session.broadcast(translation_msg)

                # Background LLM Review (Non-blocking): Tinh chỉnh ngữ nghĩa sau mà không chặn streaming
                if LLM_BASE_URL and needs_llm_review(str(job["text"]), translated, float(job.get("confidence", 1.0))):
                    async def _run_bg_llm_refine(job_data: dict, initial_trans: str) -> None:
                        try:
                            refined = await review_translation_with_llm(
                                str(job_data["text"]),
                                initial_trans,
                                str(job_data.get("context", "")),
                            )
                            if refined and refined.strip() and refined.strip() != initial_trans.strip():
                                update_msg = dict(job_data)
                                update_msg.update({
                                    "type": "translation",
                                    "session_id": session_id,
                                    "segment_id": job_data["segment_id"],
                                    "sequence": -1,
                                    "timestamp_ms": int(time.time() * 1000),
                                    "translation": refined,
                                    "is_refined": True,
                                })
                                await send_teacher(update_msg)
                                if cls_session:
                                    for h_item in reversed(cls_session.subtitles_history):
                                        if h_item.get("segment_id") == job_data["segment_id"]:
                                            h_item["translation"] = refined
                                            break
                                    await cls_session.broadcast(update_msg)
                        except Exception as e:
                            logger.debug("[WS Stream] Background LLM review: %s", e)
                    asyncio.create_task(_run_bg_llm_refine(job, translated))
            finally:
                translation_queue.task_done()

    async def receive_events() -> None:
        nonlocal teacher_connected
        try:
            while True:
                raw = await websocket.receive()
                if raw.get("type") == "websocket.disconnect":
                    teacher_connected = False
                    await event_queue.put(("disconnect", None))
                    return
                text_message = raw.get("text")
                if text_message is not None:
                    try:
                        message = _json.loads(text_message)
                    except (TypeError, ValueError):
                        continue
                    action = message.get("action")
                    if action == "ping":
                        await send_teacher({"type": "pong"})
                    elif action == "end":
                        await event_queue.put(("client_end", None))
                        return
                    continue
                binary = raw.get("bytes")
                if binary:
                    await event_queue.put(("audio", binary))
        except WebSocketDisconnect:
            teacher_connected = False
            await event_queue.put(("disconnect", None))
        except Exception as exc:
            teacher_connected = False
            logger.info("[WS Stream] receive kết thúc: %s", exc)
            await event_queue.put(("disconnect", None))

    async def refine_final_transcript() -> None:
        nonlocal current_text, current_language, current_language_label, current_confidence
        nonlocal current_mode, current_latency_ms, segment_pcm
        if (
            not STREAM_FINAL_ACCURATE
            or MODEL_MODE == "demo"
            or segment_pcm.size < STREAM_SAMPLE_RATE
            or not current_text.strip()
        ):
            return
        started = time.perf_counter()
        try:
            final_audio = np.concatenate([segment_pcm, post_roll_pcm])[
                -STREAM_FINAL_MAX_SAMPLES:
            ]
            final_model = whisper_english if current_language == "en" else whisper_accurate
            async with accurate_transcription_semaphore:
                result = await asyncio.to_thread(
                    transcribe_file,
                    final_audio,
                    current_language,
                    "",
                    "hybrid",
                    final_model,
                    True,
                )
            accurate_text, accurate_language, accurate_confidence, _ = result
            current_word_count = len(current_text.split())
            accurate_word_count = len(accurate_text.split())
            keeps_complete_turn = (
                current_word_count < 8
                or accurate_word_count >= max(4, int(current_word_count * 0.7))
            )
            if (
                accurate_text
                and keeps_complete_turn
                and accurate_language == current_language
                and accurate_confidence >= current_confidence * 0.9
            ):
                current_text = accurate_text
                current_confidence = accurate_confidence
                current_mode = "accurate"
                current_latency_ms += round((time.perf_counter() - started) * 1000)
        except Exception as exc:
            logger.warning("[WS Stream] Final accurate pass lỗi: %s", exc)

    async def finalize_current(reason: str) -> None:
        nonlocal context, sliding_pcm, segment_pcm, pre_roll_pcm, post_roll_pcm, silence_seconds
        nonlocal current_segment_id, current_revision, current_text, current_language, current_language_label
        nonlocal pending_language, pending_language_count
        nonlocal current_speaker_id, current_confidence, current_mode
        nonlocal current_latency_ms, chunk_id, asr_sequence
        if not current_text.strip() or current_segment_id == 0:
            stabilizer.reset()
            sliding_pcm = np.zeros(0, dtype=np.float32)
            segment_pcm = np.zeros(0, dtype=np.float32)
            post_roll_pcm = np.zeros(0, dtype=np.float32)
            silence_seconds = 0.0
            return

        if reason in {"pause", "sentence", "duration", "session_end"}:
            await refine_final_transcript()

        # 1. RAW ASR (Bất biến)
        raw_final = current_text

        # 2. Realtime Stabilizer finalize
        stabilized_final = stabilizer.finalize(raw_final)
        stable_final = stabilized_final.full_text

        # 3. Correction (Chỉ chạy 1 LẦN DUY NHẤT khi FINAL segment)
        if not DEBUG_DISABLE_CORRECTION:
            corrected_text = correction_engine.clean(stable_final)
        else:
            corrected_text = stable_final

        # 4. Final Text
        final_text = format_auto_punctuation(corrected_text, current_language)

        segment_state = get_segment_state(current_segment_id)
        if segment_state.get("final_committed"):
            stabilizer.reset()
            sliding_pcm = np.zeros(0, dtype=np.float32)
            segment_pcm = np.zeros(0, dtype=np.float32)
            post_roll_pcm = np.zeros(0, dtype=np.float32)
            silence_seconds = 0.0
            current_segment_id = 0
            current_revision = 0
            current_text = ""
            if session_language in {"vi", "en"}:
                current_language = session_language
                current_language_label = session_language
            pending_language = ""
            pending_language_count = 0
            current_speaker_id = 1
            current_confidence = 0.0
            current_mode = "fast"
            current_latency_ms = 0
            return

        chunk_id += 1
        current_revision += 1
        asr_sequence += 1
        segment_state["last_revision"] = current_revision
        segment_state["final_committed"] = True

        final_msg = {
            "session_id": session_id,
            "chunk_id": chunk_id,
            "segment_id": current_segment_id,
            "revision": current_revision,
            "type": "final",
            "text": final_text,
            "transcript": final_text,
            "raw_transcript": raw_final,
            "display_transcript": final_text,
            "stable_text": stable_final,
            "unstable_text": "",
            "final": True,
            "is_partial": False,
            "sequence": asr_sequence,
            "timestamp_ms": int(time.time() * 1000),
            "translation": "",
            "language": current_language,
            "language_label": current_language_label,
            "speaker_id": current_speaker_id,
            "confidence": round(current_confidence, 3),
            "latency_ms": current_latency_ms,
            "mode": current_mode,
            "final_reason": reason,
        }

        # Format 5-Tier Log chuẩn xác
        dur_str = f"{segment_pcm.size / STREAM_SAMPLE_RATE:.2f}"
        print(f"\n[AUDIO]       chunk_id={chunk_id:03d} duration={dur_str}s (FINAL)")
        print(f"[RAW ASR]     {raw_final}")
        print(f"[STABLE]      {stable_final}")
        print(f"[CORRECTED]   {corrected_text}")
        print(f"[FINAL]       {final_text}")


        await send_teacher(final_msg)
        if cls_session:
            cls_session.subtitles_history.append(dict(final_msg))
            await cls_session.broadcast(final_msg)
        await translation_queue.put({
            "segment_id": current_segment_id,
            "text": final_text,
            "language": current_language,
            "language_label": current_language_label,
            "speaker_id": current_speaker_id,
            "confidence": current_confidence,
            "context": context[-1200:],
        })
        context = f"{context} {final_text}"[-2000:]

        stabilizer.reset()
        sliding_pcm = np.zeros(0, dtype=np.float32)
        segment_pcm = np.zeros(0, dtype=np.float32)
        pre_roll_pcm = np.zeros(0, dtype=np.float32)
        post_roll_pcm = np.zeros(0, dtype=np.float32)
        silence_seconds = 0.0
        current_segment_id = 0
        current_revision = 0
        current_text = ""
        if session_language in {"vi", "en"}:
            current_language = session_language
            current_language_label = session_language
        pending_language = ""
        pending_language_count = 0
        current_speaker_id = 1
        current_confidence = 0.0
        current_mode = "fast"
        current_latency_ms = 0

    async def process_audio_window(new_pcm: np.ndarray) -> None:
        nonlocal sliding_pcm, segment_pcm, pre_roll_pcm, post_roll_pcm
        nonlocal silence_seconds, segment_id_counter, current_segment_id, current_revision
        nonlocal current_text, current_language, current_language_label, current_speaker_id
        nonlocal pending_language, pending_language_count
        nonlocal current_confidence, current_mode, current_latency_ms
        nonlocal noise_floor, speech_chunks_detected, chunk_id, asr_sequence, asr_in_flight
        if new_pcm.size == 0:
            return
        if not np.isfinite(new_pcm).all():
            new_pcm = np.nan_to_num(new_pcm, nan=0.0, posinf=0.0, neginf=0.0).astype(
                np.float32
            )
        energy = float(np.sqrt(np.mean(new_pcm ** 2)))
        speech_chunks_detected += 1 if energy >= STREAM_MIN_SPEECH_RMS else 0
        window_seconds = new_pcm.size / STREAM_SAMPLE_RATE
        speech_threshold = max(
            STREAM_MIN_SPEECH_RMS,
            noise_floor * 2.2,
        )
        if energy < speech_threshold:
            noise_floor = noise_floor * 0.94 + energy * 0.06
            if current_text != "":
                post_roll_pcm = np.concatenate([post_roll_pcm, new_pcm])[
                    -STREAM_POST_ROLL_SAMPLES:
                ]
            else:
                pre_roll_pcm = np.zeros(0, dtype=np.float32)
            silence_seconds += window_seconds
            has_ending_punct = bool(current_text and any(current_text.rstrip().endswith(p) for p in [".", "!", "?", ";", ":"]))
            required_silence = 0.8 if has_ending_punct else STREAM_FINAL_SILENCE_SECONDS
            if current_text != "" and silence_seconds >= required_silence:
                await finalize_current("pause")
            return

        silence_seconds = 0.0
        turn_started = (current_segment_id == 0)
        if turn_started:
            segment_id_counter += 1
            current_segment_id = segment_id_counter
            current_revision = 0
        pre_roll_pcm = np.zeros(0, dtype=np.float32)
        post_roll_pcm = np.zeros(0, dtype=np.float32)
        segment_pcm = np.concatenate([segment_pcm, new_pcm])
        if segment_pcm.size <= STREAM_MAX_ROLLING_SAMPLES:
            sliding_pcm = segment_pcm
        else:
            sliding_pcm = segment_pcm[-STREAM_MAX_ROLLING_SAMPLES:]

        # Concurrency Guard (Anti-backlog): Nếu ASR trước chưa xong, không tạo thêm request xếp hàng
        if asr_in_flight:
            return

        started = time.perf_counter()
        target_lang = session_language if session_language in {"vi", "en", "auto"} else "auto"
        asr_in_flight = True
        try:
            transcript, detected_lang, confidence, rec_mode, speaker_id = (
                await recognize_speech(
                    audio=sliding_pcm,
                    language=target_lang,
                    context="",
                    audio_profile="hybrid",
                    allow_accurate=False,
                    rolling_window=True,
                )
            )
        except Exception as exc:
            logger.warning("[WS Stream] ASR lỗi: %s", exc)
            await send_teacher({"type": "error", "detail": "ASR failed"})
            return
        finally:
            asr_in_flight = False

        if not transcript or not transcript.strip() or confidence < 0.20 or is_speech_hallucination(transcript):
            if turn_started and not current_text:
                current_segment_id = 0
            return

        chunk_id += 1
        current_revision += 1
        asr_sequence += 1
        segment_state = get_segment_state(current_segment_id)
        if segment_state.get("final_committed"):
            return
        if current_revision <= segment_state.get("last_revision", 0):
            return

        # Cập nhật ngôn ngữ thực tế từ ASR
        if session_language == "auto":
            current_language = detected_lang if detected_lang in {"vi", "en"} else "vi"
        else:
            current_language = session_language

        corrected_partial = correction_engine.clean(transcript)
        stabilized = stabilizer.process_partial(corrected_partial)
        if not stabilized.full_text.strip():
            return

        current_text = stabilized.full_text
        current_language_label = detect_language_label(
            stabilized.full_text, current_language
        )
        current_speaker_id = speaker_id
        current_confidence = confidence
        current_mode = rec_mode
        current_latency_ms = round((time.perf_counter() - started) * 1000)
        segment_state["last_revision"] = current_revision

        partial_msg = {
            "session_id": session_id,
            "chunk_id": chunk_id,
            "segment_id": current_segment_id,
            "revision": current_revision,
            "type": "partial",
            "text": stabilized.full_text,
            "transcript": stabilized.full_text,
            "raw_transcript": transcript,
            "display_transcript": stabilized.full_text,
            "stable_text": stabilized.stable_text,
            "unstable_text": stabilized.unstable_text,
            "final": False,
            "is_partial": True,
            "is_new_segment": turn_started,
            "sequence": asr_sequence,
            "timestamp_ms": int(time.time() * 1000),
            "translation": "",
            "language": current_language,
            "language_label": current_language_label,
            "speaker_id": speaker_id,
            "confidence": round(confidence, 3),
            "latency_ms": current_latency_ms,
            "mode": rec_mode,
        }

        # Format Realtime Diagnostic Log:
        dur_str = f"{segment_pcm.size / STREAM_SAMPLE_RATE:.2f}"
        print(f"\n[AUDIO]       chunk_id={chunk_id:03d} duration={dur_str}s")
        print(f"[RAW ASR]     {transcript}")
        print(f"[STABLE]      {stabilized.full_text}")

        await send_teacher(partial_msg)
        await broadcast(partial_msg)

        # Finalize naturally on sentence boundary or when segment reaches natural length
        clause_words = len(stabilized.full_text.split())
        has_punct = any(stabilized.stable_text.rstrip().endswith(p) for p in [".", "!", "?", "...", "…"])
        if (
            (segment_pcm.size >= 6 * STREAM_SAMPLE_RATE and has_punct)
            or (segment_pcm.size >= 12 * STREAM_SAMPLE_RATE and clause_words >= 15)
            or clause_words >= 25
        ):
            await finalize_current("sentence_boundary")

    translation_task = asyncio.create_task(translation_worker())
    receiver_task = asyncio.create_task(receive_events())
    translation_tail_complete = True
    try:
        while True:
            event_type, payload = await event_queue.get()
            control_event = ""
            if event_type == "audio" and payload:
                audio_buffer.extend(payload)
                audio_chunks_received += 1
                audio_bytes_received += len(payload)
                if not first_audio_logged:
                    first_audio_logged = True
                    logger.info(
                        "[WS Stream] Nhận audio đầu tiên từ client: %d bytes (~%.2fs PCM 16kHz)",
                        len(payload),
                        len(payload) / (STREAM_SAMPLE_RATE * 4),
                    )
                    no_audio_warned = False
            else:
                control_event = event_type

            # Cảnh báo nếu kết nối WS đã mở quá 10s mà chưa nhận được audio nào:
            # đó là dấu hiệu AudioWorklet lỗi phía frontend và AI sẽ chỉ có
            # silence để "phỏng đoán".
            if (
                not first_audio_logged
                and not no_audio_warned
                and time.monotonic() - session_opened_at > 10.0
            ):
                no_audio_warned = True
                logger.warning(
                    "[WS Stream] Chưa nhận được audio nào sau 10s – kiểm tra "
                    "AudioWorklet/microphone phía client"
                )

            # Coalesce queued audio so slow hardware processes the freshest
            # rolling window instead of building an ever-growing latency tail.
            while not event_queue.empty():
                queued_type, queued_payload = event_queue.get_nowait()
                if queued_type == "audio" and queued_payload:
                    audio_buffer.extend(queued_payload)
                else:
                    control_event = queued_type
                    break

            minimum_bytes = STREAM_UPDATE_SAMPLES * np.dtype(np.float32).itemsize
            if len(audio_buffer) >= minimum_bytes or (control_event and audio_buffer):
                aligned_length = len(audio_buffer) - (len(audio_buffer) % 4)
                if aligned_length:
                    new_pcm = np.frombuffer(
                        bytes(audio_buffer[:aligned_length]), dtype=np.float32
                    ).copy()
                    del audio_buffer[:aligned_length]
                    await process_audio_window(new_pcm)

            if control_event:
                end_reason = control_event
                break
    except Exception as exc:
        logger.error("[WS Stream] Lỗi không xử lý: %s", exc)
        await send_teacher({"type": "error", "detail": str(exc)})
    finally:
        if current_text != "":
            await finalize_current("session_end")
        try:
            await asyncio.wait_for(
                translation_queue.join(), timeout=STREAM_TRANSLATION_TAIL_SECONDS
            )
        except asyncio.TimeoutError:
            translation_tail_complete = False
            logger.warning("[WS Stream] Translation tail vượt quá %.1fs", STREAM_TRANSLATION_TAIL_SECONDS)

        session_end_msg = {
            "type": "session_end",
            "reason": end_reason,
            "translation_complete": translation_tail_complete,
        }
        await send_teacher(session_end_msg)
        await broadcast(session_end_msg)

        # Tổng kết audio diagnostics: xác nhận server có nhận đủ PCM thật
        # hay không.  Nếu audio_bytes_received == 0 thì mọi phụ đề trong phiên
        # chỉ là hallucination của Whisper trên silence.
        session_seconds = time.monotonic() - session_opened_at
        logger.info(
            "[WS Stream] Thống kê phiên %s: %.1fs • %d chunks (%.1fs audio) • "
            "%d/%d cửa sổ có năng lượng giọng nói",
            session_id[:16],
            session_seconds,
            audio_chunks_received,
            audio_bytes_received / (STREAM_SAMPLE_RATE * 4),
            speech_chunks_detected,
            max(1, speech_chunks_detected + 1),
        )

        await translation_queue.put(None)
        try:
            await asyncio.wait_for(translation_task, timeout=1.0)
        except asyncio.TimeoutError:
            translation_task.cancel()
        receiver_task.cancel()
        await asyncio.gather(receiver_task, return_exceptions=True)
        if teacher_connected:
            try:
                await websocket.close()
            except Exception:
                pass
        async with _stream_sessions_lock:
            _stream_sessions.pop(session_id, None)
        await session_manager.remove_session(session_id)
        logger.info("[WS Stream] Session kết thúc: %s", session_id[:16])
