"""
ClassBridge – FastAPI Service chạy Kiến Trúc 2 Module Chuyên Biệt (Port 8000)
Tác giả: Nguyễn Sỹ Tân (MSSV: 29212449741)
"""

import io
import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

import importlib.util
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np

# Thêm dependencies
venv_site = Path("d:/TailieuNPKH/classbridge/backend/ai-service/.venv/Lib/site-packages")
if venv_site.exists():
    sys.path.insert(0, str(venv_site))

def load_module_from_path(module_name: str, file_path: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

base_dir = Path(__file__).resolve().parent
router_mod = load_module_from_path("language_router", str(base_dir / "01_AUDIO_ROUTER/language_router.py"))
vi_mod = load_module_from_path("vi_speech_recognizer", str(base_dir / "02_MODULE_VI_SPECIALIST/vi_speech_recognizer.py"))
en_mod = load_module_from_path("en_speech_recognizer", str(base_dir / "03_MODULE_EN_SPECIALIST/en_speech_recognizer.py"))
trans_mod = load_module_from_path("nmt_translator", str(base_dir / "04_TRANSLATION_MODULE/nmt_translator.py"))

AudioLanguageRouter = router_mod.AudioLanguageRouter
VietnameseSpeechRecognizer = vi_mod.VietnameseSpeechRecognizer
EnglishSpeechRecognizer = en_mod.EnglishSpeechRecognizer
DualTranslator = trans_mod.DualTranslator

app = FastAPI(title="ClassBridge 2-Module Dual-Specialist AI Service", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global models
router: AudioLanguageRouter | None = None
vi_specialist: VietnameseSpeechRecognizer | None = None
en_specialist: EnglishSpeechRecognizer | None = None
translator: DualTranslator | None = None


@app.on_event("startup")
def load_all_modules():
    global router, vi_specialist, en_specialist, translator
    print("🚀 Đang nạp Kiến trúc 2 Module Chuyên Biệt vào GPU...")
    router = AudioLanguageRouter()
    vi_specialist = VietnameseSpeechRecognizer()
    en_specialist = EnglishSpeechRecognizer()
    translator = DualTranslator()
    print("✅ Đã sẵn sàng phục vụ Kiến trúc 2 Module!")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "architecture": "Dual-Specialist (2 Modules)",
        "module_1": "Vietnamese Speech Specialist",
        "module_2": "English & Accent Specialist",
        "router": "Active (< 3ms)",
        "translation": "EnViT5 LoRA",
    }


@app.post("/v1/transcribe")
async def transcribe(
    audio: UploadFile = File(...),
    source_language: str = Form("auto"),
    context: str = Form(""),
):
    content = await audio.read()
    from faster_whisper.audio import decode_audio
    audio_np = np.asarray(decode_audio(io.BytesIO(content), sampling_rate=16_000), dtype=np.float32)

    # 1. Định tuyến ngôn ngữ tự động
    if source_language == "auto":
        target_lang, prob = router.detect_and_route(audio_np, vi_specialist.model)
    else:
        target_lang = source_language

    # 2. Xử lý bởi Module chuyên biệt
    if target_lang == "vi":
        asr_res = vi_specialist.transcribe(audio_np, beam_size=1)
    else:
        asr_res = en_specialist.transcribe(audio_np, beam_size=1)

    # 3. Dịch song ngữ
    translation = translator.translate(asr_res["text"], source_language=target_lang)

    return {
        "transcript": asr_res["text"],
        "corrected_text": asr_res["text"],
        "source_language": target_lang,
        "translation": translation,
        "module_used": asr_res["module"],
    }


from fastapi import Request

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
            "module": "EnViT5 Dual-Translation Module"
        }

    translated = translator.translate(str(text), source_language=source_language)
    return {
        "translation": translated,
        "translated_text": translated,
        "source_language": source_language,
        "module": "EnViT5 Dual-Translation Module",
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
