"""
ClassBridge – FastAPI Service chạy Kiến Trúc 2 Module Chuyên Biệt (Port 8000)
Tác giả: Nguyễn Sỹ Tân (MSSV: 29212449741)
"""

import io
import sys
import json
import time
import asyncio
import re
from contextlib import asynccontextmanager
from pathlib import Path

# Tự động nạp môi trường .venv site-packages trước khi import bất kỳ thư viện bên ngoài nào
venv_site = Path("d:/TailieuNPKH/classbridge/backend/ai-service/.venv/Lib/site-packages")
if venv_site.exists() and str(venv_site) not in sys.path:
    sys.path.insert(0, str(venv_site))

import numpy as np
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper.audio import decode_audio

# Đảm bảo Windows console không bao giờ bị sập bởi UnicodeEncodeError (cp1252) khi in emoji/tiếng Việt
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Thêm đường dẫn module vào sys.path để import chuẩn mực
base_dir = Path(__file__).resolve().parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))
trans_dir = base_dir / "04_TRANSLATION_MODULE"
if str(trans_dir) not in sys.path:
    sys.path.insert(0, str(trans_dir))

from unified_speech_recognizer import UnifiedSpeechRecognizer, remove_repeated_phrases
from nmt_translator import NLLBTranslator

# Global models
asr_engine: UnifiedSpeechRecognizer | None = None
translator: NLLBTranslator | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global asr_engine, translator
    print("🚀 Đang nạp Kiến trúc Tinh gọn (Unified ASR GPU + Meta NLLB-200 CPU)...", flush=True)
    asr_engine = UnifiedSpeechRecognizer()
    translator = NLLBTranslator(device="cpu")
    print("✅ Hệ thống ClassBridge đã sẵn sàng phục vụ!", flush=True)
    yield


app = FastAPI(
    title="ClassBridge Unified AI Service (NLLB-200 & Unified ASR)",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "architecture": "Unified ASR + Meta NLLB-200 Bilingual",
        "asr_engine": "Unified Whisper (Multilingual)",
        "translation_engine": "Meta NLLB-200 (Distilled 600M)",
        "features": [
            "speech_to_text",
            "bidirectional_translation",
        ],
    }


@app.post("/v1/transcribe")
async def transcribe(
    audio: UploadFile = File(...),
    source_language: str = Form("auto"),
    context: str = Form(""),
):
    t0 = time.time()
    content = await audio.read()
    audio_np = np.asarray(decode_audio(io.BytesIO(content), sampling_rate=16_000), dtype=np.float32)

    # 1. Nhận diện giọng nói thống nhất (Unified ASR)
    asr_res = asr_engine.transcribe(audio_np, language=source_language, beam_size=5)
    text = asr_res.get("text", "").strip()
    detected_lang = asr_res.get("language", "vi")

    # 2. Dịch song ngữ NLLB-200
    src_trans = "en" if detected_lang == "en" else "vi"
    tgt_trans = "vi" if src_trans == "en" else "en"
    translation = translator.translate(text, source_language=src_trans, target_language=tgt_trans) if text else ""

    latency_ms = int((time.time() - t0) * 1000)
    return {
        "transcript": text,
        "corrected_text": text,
        "source_language": "en" if detected_lang == "en" else "vi",
        "language_label": detected_lang,
        "translation": translation,
        "latency_ms": latency_ms,
        "module_used": asr_res.get("module", "Unified ASR"),
    }


@app.post("/v1/translate")
async def translate_text(request: Request):
    content_type = request.headers.get("content-type", "")
    text = ""
    source_language = "en"
    
    if "application/json" in content_type:
        try:
            data = await request.json()
            text = data.get("text", "")
            source_language = data.get("source_language", "en")
        except Exception:
            pass
    else:
        try:
            form = await request.form()
            text = form.get("text", "")
            source_language = form.get("source_language", "en")
        except Exception:
            pass

    if not text or not str(text).strip():
        return {
            "translation": "",
            "translated_text": "",
            "source_language": source_language,
            "module": "Meta NLLB-200 Translation Module"
        }

    translated = translator.translate(str(text), source_language=source_language)
    return {
        "translation": translated,
        "translated_text": translated,
        "source_language": source_language,
        "module": "Meta NLLB-200 Translation Module",
    }


# =============================================================================
# WebSocket Real-Time Audio Streaming (Nhận diện lời gốc & Dịch sang Tiếng Việt)
# =============================================================================

# Ký tự ngoại lai ngoài song ngữ Anh - Việt (Hàn, Gruzia, CJK, Cyrillic, Ả Rập, Thái,...)
FOREIGN_SCRIPTS_REGEX = re.compile(
    r"[\uac00-\ud7a3\u1100-\u11ff"  # Hangul (Hàn Quốc - ví dụ: 그 메뉴 기회니까 되다)
    r"\u10a0-\u10ff\u1c90-\u1cba"  # Georgian (Gruzia - sinh ra ký tự ღღღღ)
    r"\u4e00-\u9fff\u3400-\u4dbf"  # CJK (Trung Quốc)
    r"\u3040-\u30ff"              # Hiragana / Katakana (Nhật Bản)
    r"\u0400-\u04ff"              # Cyrillic (Nga)
    r"\u0600-\u06ff"              # Arabic (Ả Rập)
    r"\u0e00-\u0e7f]"             # Thai (Thái Lan)
)


def is_valid_speech_text(text: str) -> bool:
    """
    Kiểm tra tính hợp lệ của văn bản nhận dạng:
    - Bỏ qua chuỗi rỗng hoặc chỉ toàn ký tự đặc biệt/dấu câu.
    - Loại bỏ triệt để ký tự ngoại lai ngoài song ngữ Anh - Việt (như tiếng Hàn, Gruzia,...)
    - Bảo toàn 100% mọi từ ngữ người phát âm: Nghe được chữ gì thì hiển thị chữ đó!
    - Chỉ loại bỏ các vòng lặp token bất thường do decoder (ví dụ: 'a a a a a').
    """
    if not text:
        return False
    cleaned = text.strip()

    # 1. Loại bỏ nếu chứa ký tự ngoại lai ngoài song ngữ Anh - Việt (tiếng Hàn, Gruzia,...)
    if FOREIGN_SCRIPTS_REGEX.search(cleaned):
        return False

    # 2. Phải chứa ít nhất một ký tự chữ cái hoặc chữ số
    if not re.search(r"[\w\d]", cleaned, flags=re.UNICODE):
        return False

    words = re.findall(r"\w+", cleaned, flags=re.UNICODE)
    if not words:
        return False

    # 3. Phát hiện vòng lặp từ vô hạn do decoder (ví dụ: "a a a a a")
    if len(words) >= 5:
        unique_words = set(w.lower() for w in words)
        if len(unique_words) <= 1:
            return False

    return True


@app.post("/stream/start")
async def stream_start(request: Request):
    """Khởi tạo phiên nhận dạng trực tiếp (truyền ngôn ngữ nếu có)."""
    lang = "auto"
    try:
        form = await request.form()
        lang = str(form.get("language") or "auto").strip()
    except Exception:
        pass
    session_id = f"sess_{int(time.time() * 1000)}"
    return {
        "status": "ready",
        "session_id": session_id,
        "ws_url": f"/ws/stream/{session_id}?lang={lang}",
    }


@app.websocket("/ws/stream")
@app.websocket("/ws/stream/{session_id}")
async def ws_stream(websocket: WebSocket, session_id: str = "default"):
    """
    Kênh WebSocket nhận diện âm thanh trực tiếp từ Microphone / Audio:
    - Nhận luồng PCM 16kHz (Float32 hoặc Int16)
    - Tự động ngắt câu với bộ đệm âm thanh VAD & sliding pre-roll (bảo toàn trọn vẹn từ mở đầu)
    - Khóa ngôn ngữ chính xác theo lựa chọn người dùng (vi / en / auto)
    - Loại bỏ triệt để từ mẫu & vòng lặp lặp lại
    """
    await websocket.accept()

    # Nhận ngôn ngữ mong muốn ban đầu từ query params hoặc bóc tách từ session_id nếu bị dính
    active_language = websocket.query_params.get("lang", "").strip().lower()
    target_trans_lang = websocket.query_params.get("trans_lang", "auto").strip().lower()
    if ("?lang=" in session_id) or ("%3Flang%3D" in session_id) or ("%3flang%3d" in session_id):
        raw_part = session_id.replace("%3Flang%3D", "?lang=").replace("%3flang%3d", "?lang=")
        parts = raw_part.split("?lang=")
        session_id = parts[0]
        if not active_language and len(parts) > 1:
            active_language = parts[1].strip().lower()
    if not active_language:
        active_language = "auto"
    print(f"🔗 [WS Client Connected] session_id={session_id}, active_language='{active_language}', target_trans='{target_trans_lang}'", flush=True)

    pcm_chunks: list[np.ndarray] = []
    pre_roll_buffer: list[np.ndarray] = []
    speech_frames = 0
    silence_frames = 0
    noise_floor = 0.020  # Mức ồn nền thích ứng ban đầu
    MAX_BUFFER_SAMPLES = int(16000 * 10.0)  # Tăng lên 10.0s để chứa trọn vẹn câu nói/hát dài không bị cắt cụt
    asr_lock = asyncio.Lock()               # Khóa tuần tự ASR để WebSocket loop không bị chặn

    async def transcribe_current_buffer(chunks_to_process: list[np.ndarray]):
        nonlocal noise_floor
        if not chunks_to_process:
            return

        audio_segment = np.concatenate(chunks_to_process)
        # Độ dài tối thiểu 0.3s (4800 mẫu)
        if len(audio_segment) < 4800:
            return

        seg_peak = float(np.max(np.abs(audio_segment)))
        seg_rms = float(np.sqrt(np.mean(audio_segment ** 2)))
        # Bỏ qua nếu mức năng lượng cực thấp (chỉ là tiếng ồn máy tính hoặc khoảng lặng tĩnh)
        if seg_peak < 0.025 and seg_rms < 0.008:
            return

        loop = asyncio.get_running_loop()

        def run_asr():
            try:
                res = asr_engine.transcribe(
                    audio_segment,
                    language=active_language,
                    beam_size=2,  # beam=2: Cân bằng tốc độ GPU (<120ms) và độ chính xác dấu tiếng Việt vượt trội
                )
                text = res.get("text", "").strip()
                detected_lang = res.get("language", "vi") or "vi"

                if not is_valid_speech_text(text):
                    return detected_lang, ""

                print(f"🎤 [Live ASR] {len(audio_segment)/16000:.2f}s (RMS: {seg_rms:.4f}) [{detected_lang}] -> '{text}'", flush=True)
                return detected_lang, text
            except Exception as ex:
                print(f"⚠️ Lỗi ASR: {ex}", flush=True)
                return "vi", ""

        t_start = time.time()
        detected_lang, text = await loop.run_in_executor(None, run_asr)
        if not text or not is_valid_speech_text(text):
            return

        seg_id = int(time.time() * 1000) % 1000000
        ui_lang = "en" if detected_lang == "en" else "vi"
        latency_calc = max(35, int((time.time() - t_start) * 1000))
        print(f"📡 [WS Send] lang={detected_lang} ui={ui_lang} seg={seg_id} | '{text[:60]}'", flush=True)

        # ⚡ GỬI NGAY LỜI GỐC LÊN MÀN HÌNH TỨC THÌ (ĐỘ TRỄ CỰC THẤP, UTF-8 KHÔNG ESCAPE)
        final_msg = {
            "type": "final",
            "session_id": session_id,
            "segment_id": seg_id,
            "speaker_id": 1,
            "transcript": text,
            "stable_text": text,
            "unstable_text": "",
            "translation": "",
            "language": ui_lang,
            "language_label": detected_lang,
            "latency_ms": latency_calc,
        }
        try:
            if getattr(websocket, "client_state", None) and websocket.client_state.name == "CONNECTED":
                await websocket.send_text(json.dumps(final_msg, ensure_ascii=False))
        except Exception:
            return

        # 🌐 DỊCH ASYNC TRONG BACKGROUND ĐỂ KHÔNG CHẶN HIỂN THỊ LỜI GỐC
        async def run_async_translation(src_text: str, detected_lang: str, sid: str, segid: int):
            try:
                # Tự động đảo chiều song ngữ Anh - Việt
                if detected_lang == "en":
                    src_for_trans = "en"
                    tgt_for_trans = "vi"
                else:
                    src_for_trans = "vi"
                    tgt_for_trans = "en"

                trans_res = await loop.run_in_executor(
                    None,
                    lambda: translator.translate(src_text, source_language=src_for_trans, target_language=tgt_for_trans)
                )
                trans_res = remove_repeated_phrases(trans_res)
                # Chỉ gửi bản dịch khi có nội dung và không trùng lặp y hệt lời gốc
                if trans_res and trans_res.strip().lower() != src_text.strip().lower():
                    if getattr(websocket, "client_state", None) and websocket.client_state.name == "CONNECTED":
                        await websocket.send_text(json.dumps({
                            "type": "translation",
                            "session_id": sid,
                            "segment_id": segid,
                            "translation": trans_res,
                            "target_lang": tgt_for_trans,
                        }, ensure_ascii=False))
            except Exception:
                pass

        asyncio.create_task(run_async_translation(text, detected_lang, session_id, seg_id))

    try:
        while True:
            msg = await websocket.receive()
            if msg.get("type") == "websocket.disconnect":
                break

            # Xử lý text frame (ping/pong, chuyển đổi ngôn ngữ, kết thúc phiên)
            if "text" in msg:
                try:
                    data = json.loads(msg["text"])
                    action = data.get("action") or data.get("type")
                    if action == "ping":
                        await websocket.send_text(json.dumps({"type": "pong"}))
                    elif action in ["set_language", "set_mode"]:
                        new_lang = data.get("language") or data.get("mode") or "auto"
                        active_language = str(new_lang).strip().lower()
                        print(f"🔄 [WS Language Changed] session_id={session_id}, active_language='{active_language}'", flush=True)
                        await websocket.send_text(json.dumps({"type": "language_changed", "language": active_language}, ensure_ascii=False))
                    elif action in ["set_translation_target", "set_trans_lang"]:
                        new_target = data.get("target") or data.get("language") or "auto"
                        target_trans_lang = str(new_target).strip().lower()
                        print(f"🔄 [WS Translation Target Changed] session_id={session_id}, target='{target_trans_lang}'", flush=True)
                        await websocket.send_text(json.dumps({"type": "translation_target_changed", "target": target_trans_lang}, ensure_ascii=False))
                    elif action == "end":
                        if len(pcm_chunks) > 0:
                            await transcribe_current_buffer(pcm_chunks)
                        pcm_chunks = []
                        speech_frames = 0
                        silence_frames = 0
                        await websocket.send_text(json.dumps({"type": "session_end"}))
                except Exception:
                    pass

            # Xử lý binary frame (PCM audio 16kHz)
            elif "bytes" in msg:
                pcm_bytes = msg["bytes"]
                if len(pcm_bytes) == 0:
                    continue

                if len(pcm_bytes) % 4 == 0:
                    chunk = np.frombuffer(pcm_bytes, dtype=np.float32)
                elif len(pcm_bytes) % 2 == 0:
                    chunk = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                else:
                    continue

                if len(chunk) == 0:
                    continue

                rms = float(np.sqrt(np.mean(chunk ** 2)))

                # 1. Trạng thái nghỉ (Acoustic Noise Gate):
                if len(pcm_chunks) == 0:
                    # Thích ứng mức ồn phòng liên tục (kẹp trong [0.005, 0.040])
                    noise_floor = min(0.040, max(0.005, 0.95 * noise_floor + 0.05 * rms))
                    # Ngưỡng bắt đầu phát biểu: Vượt tiếng ồn phòng
                    speech_start_threshold = max(0.020, noise_floor * 1.60)

                    if rms < speech_start_threshold:
                        pre_roll_buffer.append(chunk)
                        if len(pre_roll_buffer) > 3:  # Giữ 300ms pre-roll để không bao giờ mất âm đầu
                            pre_roll_buffer.pop(0)
                        continue
                    else:
                        pcm_chunks = list(pre_roll_buffer)
                        pre_roll_buffer.clear()
                        pcm_chunks.append(chunk)
                        speech_frames = 1
                        silence_frames = 0
                        continue

                # 2. Trạng thái đang tích lũy buffer:
                pcm_chunks.append(chunk)
                current_samples = sum(len(c) for c in pcm_chunks)

                # Ngưỡng duy trì tiếng nói
                speech_active_threshold = max(0.014, noise_floor * 1.20)
                if rms >= speech_active_threshold:
                    speech_frames += 1
                    silence_frames = 0
                else:
                    silence_frames += 1

                # 3. Phán đoán ngắt câu âm học:
                should_transcribe = False
                split_at_dip = False

                # Tiêu chuẩn A: Đã phát biểu thực sự (>= 3 frames ~ 300ms) và người nói dừng câu 400ms (4 frames)
                if speech_frames >= 3 and silence_frames >= 4:
                    should_transcribe = True

                # Tiêu chuẩn B: Từ đơn ngắn ('Dạ', 'Vâng', 'Có', 'Sao'...) có >= 2 frames (~200ms) và im lặng 500ms
                elif speech_frames >= 2 and silence_frames >= 5:
                    should_transcribe = True

                # Tiêu chuẩn C: Xả an toàn khi im lặng kéo dài (>= 7 frames ~ 700ms)
                elif silence_frames >= 7:
                    if speech_frames >= 1 and current_samples >= 4800:
                        should_transcribe = True
                    else:
                        pcm_chunks.clear()
                        speech_frames = 0
                        silence_frames = 0
                        continue

                # Tiêu chuẩn D: Nói dài liên tục chạm trần an toàn (10.0s):
                elif current_samples >= MAX_BUFFER_SAMPLES:
                    should_transcribe = True
                    split_at_dip = True

                if should_transcribe:
                    if split_at_dip:
                        # Tìm điểm năng lượng thấp nhất trong 1.5s gần nhất để ngắt tự nhiên giữa 2 từ
                        search_start = max(0, len(pcm_chunks) - 20)
                        search_end = max(1, len(pcm_chunks) - 3)
                        best_split = len(pcm_chunks)
                        min_energy = float("inf")
                        for idx in range(search_start, search_end):
                            c = pcm_chunks[idx]
                            e = float(np.mean(c ** 2))
                            if e < min_energy:
                                min_energy = e
                                best_split = idx

                        to_process = list(pcm_chunks[:best_split])
                        # Giữ lại 400ms overlap (4 chunks) để không bao giờ bị cắt cụt từ nối tiếp
                        overlap_start = max(0, best_split - 4)
                        pcm_chunks = list(pcm_chunks[overlap_start:])
                        speech_frames = max(1, len(pcm_chunks))
                        silence_frames = 0
                    else:
                        # Bảo tồn 100% âm tiết cuối cùng của người nói: Giữ nguyên vẹn toàn bộ buffer, không cắt tỉa
                        to_process = list(pcm_chunks)
                        pcm_chunks.clear()
                        speech_frames = 0
                        silence_frames = 0

                    # ⚡ Xử lý bất đồng bộ tuần tự qua asr_lock: WebSocket loop KHÔNG bao giờ bị nghẽn
                    async def run_safe_transcribe(chunks_buf: list[np.ndarray]):
                        async with asr_lock:
                            await transcribe_current_buffer(chunks_buf)

                    asyncio.create_task(run_safe_transcribe(to_process))
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"ℹ️ WS stream closed: {e}", flush=True)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
