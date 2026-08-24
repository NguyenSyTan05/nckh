"""
ClassBridge - Live Speech-to-Text Demo (EN & VI)
# pyrefly: ignore-all-errors
Nhận diện giọng nói Tiếng Anh & Tiếng Việt trực tiếp từ micro, ghi ra chữ ngay lập tức.

Cách chạy:
    python live_stt_demo.py
    python live_stt_demo.py --language vi      # Ép buộc Tiếng Việt
    python live_stt_demo.py --language en      # Ép buộc Tiếng Anh
    python live_stt_demo.py --language auto    # Tự động phát hiện

Yêu cầu:
    pip install faster-whisper sounddevice numpy
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Any, List, Tuple, Dict
import logging

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("classbridge.live_stt")

# ── Tự động chèn virtualenv ───────────────────────────────────────────────────
_VENV = Path(__file__).resolve().parent.parent / "backend" / "ai-service" / ".venv" / "Lib" / "site-packages"
if _VENV.exists() and str(_VENV) not in sys.path:
    sys.path.insert(0, str(_VENV))
# ─────────────────────────────────────────────────────────────────────────────

SAMPLE_RATE = 16_000       # Whisper yêu cầu 16kHz
CHUNK_SECONDS = 2.5        # Thu âm theo từng đoạn 2.5 giây (thay đổi nhỏ để giảm độ trễ)
SILENCE_THRESHOLD = 0.008  # Ngưỡng năng lượng (tránh nhận khi im lặng)
MIN_VI_PROB = 0.35         # Ngưỡng xác suất tối thiểu để nhận diện là Tiếng Việt

# Streaming capture parameters
AUDIO_QUEUE_MAX = 32       # Số khung audio giữ trong queue trước khi drop
SESSION_FLUSH_EVERY = 10   # Lưu log phiên sau mỗi N câu để tránh mất dữ liệu


def load_model(model_size: str = "base") -> object:
    """Nạp mô hình Whisper CTranslate2 / faster-whisper.

    Ưu tiên thứ tự:
      1) CTranslate2 export (ct2)
      2) Merged PyTorch model (whisper-voice-fine-tuned-merged)
      3) Adapter directory (whisper-voice-fine-tuned) — _cảnh báo nếu chưa merged_
      4) remote HF model size
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("❌ Thiếu thư viện: pip install faster-whisper")
        sys.exit(1)

    # Model locations
    _ai_dir = Path(__file__).resolve().parent.parent / "backend" / "ai-service"
    _ct2_dir = _ai_dir / "whisper-multi-accent-ct2"
    _merged_dir = _ai_dir / "whisper-voice-fine-tuned-merged"
    _voice_dir = _ai_dir / "whisper-voice-fine-tuned"

    # Prefer ct2, then merged, then adapter, then HF size
    if _ct2_dir.exists():
        model_path = str(_ct2_dir)
        logger.info("Dùng mô hình ClassBridge CTranslate2: %s", _ct2_dir)
    elif _merged_dir.exists():
        model_path = str(_merged_dir)
        print(f"🎯 Dùng mô hình ClassBridge đã hợp nhất: {_merged_dir}")
    elif _voice_dir.exists():
        model_path = str(_voice_dir)
        print("⚠️ Dùng adapter LoRA chưa hợp nhất — khuyến nghị tạo CT2/merged để có hiệu năng tốt hơn")
    else:
        model_path = model_size
        print(f"📥 Dùng mô hình Whisper gốc: {model_size}")

    # Device / compute selection
    try:
        import torch
        has_cuda = torch.cuda.is_available()
    except Exception:
        has_cuda = False

    device = "cuda" if has_cuda else "cpu"
    compute_type = "float16" if has_cuda else "int8"

    model = WhisperModel(
        model_path,
        device=device,
        compute_type=compute_type,
        cpu_threads=2,
        num_workers=1,
    )
    print(f"✅ Mô hình Whisper đã sẵn sàng! (device={device}, compute_type={compute_type})\n")
    return model


def detect_language(model: object, audio_data: object) -> tuple[str, float, float]:
    """
    Phát hiện ngôn ngữ từ đoạn âm thanh.
    Trả về: (ngôn_ngữ, xác_suất_vi, xác_suất_en)
    Chỉ cho phép 'vi' hoặc 'en' — chặn hoàn toàn mọi ngoại ngữ khác.
    """
    import numpy as np
    audio_np = np.array(audio_data, dtype=np.float32)

    _, lang_probs = model.detect_language(audio_np)
    vi_prob = lang_probs.get("vi", 0.0)
    en_prob = lang_probs.get("en", 0.0)

    # Chỉ nhận vi hoặc en — ngăn hoàn toàn Tây Ban Nha, Pháp, v.v.
    if vi_prob >= en_prob:
        return "vi", vi_prob, en_prob
    else:
        return "en", en_prob, vi_prob


def transcribe_chunk(
    model: object,
    audio_data: list,
    forced_language: Optional[str] = None,
) -> tuple[str, str, float]:
    """
    Phiên âm đoạn âm thanh.
    Trả về: (văn_bản, ngôn_ngữ, confidence)
    """
    import numpy as np
    audio_np = np.array(audio_data, dtype=np.float32)

    # Kiểm tra năng lượng âm thanh — bỏ qua nếu im lặng
    energy = float(np.sqrt(np.mean(audio_np ** 2)))
    if energy < SILENCE_THRESHOLD:
        return "", "silence", 0.0

    # Xác định ngôn ngữ
    if forced_language in ("vi", "en"):
        lang = forced_language
        vi_p, en_p = (1.0, 0.0) if lang == "vi" else (0.0, 1.0)
    else:
        lang, vi_p, en_p = detect_language(model, audio_np)

    # Phiên âm với ngôn ngữ đã xác định
    segments, info = model.transcribe(
        audio_np,
        language=lang,
        task="transcribe",
        beam_size=1,
        best_of=1,
        temperature=0.0,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 300},
        condition_on_previous_text=False,
        without_timestamps=True,
    )

    texts = [seg.text.strip() for seg in segments if seg.text.strip()]
    full_text = " ".join(texts)

    avg_logprob = info.all_language_probs[0][1] if info.all_language_probs else 0.0
    confidence = max(vi_p, en_p)

    return full_text, lang, confidence


def _record_using_blocking(sd: object, seconds: float = CHUNK_SECONDS) -> list:
    """Thu âm một đoạn từ micro (fallback blocking implementation)."""
    import numpy as np
    frames = sd.rec(
        int(seconds * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        blocking=True,
    )
    return frames.flatten().tolist()


def _start_input_stream(q: "queue.Queue[list]") -> object:
    """Khởi tạo sounddevice InputStream và đưa khung audio vào queue.
    Trả về đối tượng stream để caller có thể đóng khi cần.
    """
    import sounddevice as sd

    def callback(indata, frames, time, status):
        try:
            q.put(indata.copy(), block=False)
        except Exception:
            # Queue đầy -> drop frame
            pass

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        callback=callback,
    )
    stream.start()
    return stream


def _collect_frames_from_queue(q: "queue.Queue[list]", seconds: float = CHUNK_SECONDS) -> list:
    """Thu thập đủ khung từ queue để tạo thành một đoạn có độ dài `seconds`.
    Nếu queue rỗng trong 1s, trả về empty list.
    """
    import numpy as np
    import time

    required = int(seconds * SAMPLE_RATE)
    buffers = []
    collected = 0
    start = time.time()
    while collected < required and (time.time() - start) < (seconds + 1.0):
        try:
            chunk = q.get(timeout=0.5)
            arr = chunk.flatten()
            buffers.append(arr)
            collected += arr.shape[0]
        except Exception:
            # timeout or empty
            continue

    if not buffers:
        return []

    data = np.concatenate(buffers, axis=0)[:required]
    return data.astype("float32").tolist()


def print_result(text: str, lang: str, confidence: float, line_num: int) -> None:
    """In kết quả phiên âm ra màn hình."""
    lang_label = "🇻🇳 VI" if lang == "vi" else "🇺🇸 EN"
    conf_bar = "█" * int(confidence * 10) + "░" * (10 - int(confidence * 10))
    print(f"\n[{line_num:04d}] {lang_label} | [{conf_bar}] {confidence:.0%}")
    print(f"       📝 {text}")


def run_live_stt(language: str = "auto", model_size: str = "base", dry_run: bool = False) -> None:
    """Vòng lặp chính: liên tục thu âm và phiên âm thời gian thực.

    Sử dụng InputStream + queue để tránh mất khung audio khi model đang chờ xử lý.
    """
    try:
        import sounddevice as sd
        import queue
    except ImportError:
        logger.error("Thiếu thư viện: pip install sounddevice")
        sys.exit(1)

    logger.info("%s", "=" * 65)
    logger.info("  🎙️  ClassBridge - NHẬN DIỆN GIỌNG NÓI THỜI GIAN THỰC")
    logger.info("%s", "=" * 65)
    logger.info("  Ngôn ngữ : %s", ('Tự động (Anh/Việt)' if language == 'auto' else language.upper()))
    logger.info("  Mô hình  : Whisper %s", model_size)
    logger.info("  Micro    : Thiết bị mặc định của hệ thống")
    logger.info("%s", "=" * 65)
    logger.info("  👉 Hãy nói vào micro. Nhấn Ctrl+C để dừng.\n")

    # Prepare session state
    forced_lang = language if language in ("vi", "en") else None
    line_num = 0
    session_log: list[dict] = []

    if dry_run:
        # Simulated run: do not load heavy models or open microphone.
        print("🔬 Chạy ở chế độ DRY-RUN (giả lập). Không dùng micro, không nạp mô hình thực.)")

        class _MockInfo:
            def __init__(self, lang='vi', prob=0.95):
                self.all_language_probs = [(lang, prob)]

        class _MockSeg:
            def __init__(self, text):
                self.text = text

        class _MockModel:
            def detect_language(self, audio_np):
                return None, {'vi': 0.95, 'en': 0.05}

            def transcribe(self, audio_np, **kwargs):
                # Return a simulated transcription and confidence info
                return [_MockSeg("Đây là bản demo giả lập." )], _MockInfo()

        model = _MockModel()

        # Simulate a few chunks to exercise the pipeline
        for i in range(1, 6):
            text, detected_lang, confidence = transcribe_chunk(model, [], forced_lang)
            if text and detected_lang not in ("silence", ""):
                line_num += 1
                print_result(text, detected_lang, confidence, line_num)
                session_log.append({
                    "line": line_num,
                    "lang": detected_lang,
                    "text": text,
                    "confidence": round(confidence, 3),
                })
        # Save simulated session and exit
        _save_session_log(session_log)
        return

    # Start audio input stream into a queue (non-blocking capture)
    q: "queue.Queue[list]" = queue.Queue(maxsize=AUDIO_QUEUE_MAX)
    stream = None
    try:
        stream = _start_input_stream(q)
    except Exception as e:
        logger.warning("Không thể khởi tạo InputStream, chuyển sang chế độ blocking: %s", e)
        stream = None

    try:
        while True:
            if stream is not None:
                audio = _collect_frames_from_queue(q, CHUNK_SECONDS)
                if not audio:
                    # nothing captured — sleep briefly
                    import time
                    time.sleep(0.1)
                    continue
            else:
                # fallback blocking record
                import sounddevice as sd
                audio = _record_using_blocking(sd, CHUNK_SECONDS)

            try:
                text, detected_lang, confidence = transcribe_chunk(model, audio, forced_lang)
            except Exception as exc:
                logger.exception("Lỗi khi phiên âm chunk: %s", exc)
                continue

            if text and detected_lang not in ("silence", ""):
                line_num += 1
                print_result(text, detected_lang, confidence, line_num)
                session_log.append({
                    "line": line_num,
                    "lang": detected_lang,
                    "text": text,
                    "confidence": round(confidence, 3),
                })

                # Periodically flush session log to disk to avoid data loss
                if line_num % SESSION_FLUSH_EVERY == 0:
                    _save_session_log(session_log)

    except KeyboardInterrupt:
        logger.info("%s", "\n\n" + ('=' * 65))
        logger.info("  📊 Kết thúc phiên: %d câu được nhận diện", line_num)
        logger.info("%s", '=' * 65)
        _save_session_log(session_log)
    finally:
        try:
            if stream is not None:
                stream.stop()
                stream.close()
        except Exception:
            logger.debug("Lỗi khi đóng stream", exc_info=True)


def _save_session_log(log: list[dict]) -> None:
    """Lưu log phiên làm việc ra file JSON."""
    import json
    from datetime import datetime

    if not log:
        return

    _out_dir = Path(__file__).resolve().parent.parent / "data"
    _out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    _path = _out_dir / f"stt_session_{timestamp}.json"

    with open(_path, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Log đã lưu tại: {_path}")

    # Hiển thị bản tóm tắt
    vi_count = sum(1 for r in log if r["lang"] == "vi")
    en_count = sum(1 for r in log if r["lang"] == "en")
    print(f"   Tiếng Việt: {vi_count} câu | Tiếng Anh: {en_count} câu")
    print("\n📄 Toàn bộ lời thoại:")
    for r in log:
        prefix = "🇻🇳" if r["lang"] == "vi" else "🇺🇸"
        print(f"   {prefix} {r['text']}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ClassBridge Live Speech-to-Text (EN & VI)"
    )
    parser.add_argument(
        "--language", "-l",
        choices=["auto", "vi", "en"],
        default="auto",
        help="Ngôn ngữ nhận diện: auto (tự động), vi (Tiếng Việt), en (Tiếng Anh)",
    )
    parser.add_argument(
        "--model", "-m",
        default="base",
        choices=["tiny", "base", "small", "medium"],
        help="Kích thước mô hình Whisper (mặc định: base)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="Chạy ở chế độ giả lập mà không dùng micro hoặc nạp mô hình thực",
    )
    args = parser.parse_args()
    run_live_stt(language=args.language, model_size=args.model, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
