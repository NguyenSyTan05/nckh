@echo off
chcp 65001 > nul
title ClassBridge AI - Automated STT Training Pipeline

echo =========================================================================
echo    ClassBridge AI - AUTOMATED STT FINE-TUNING PIPELINE
echo =========================================================================
echo.

set PYTHON=ai-service\.venv\Scripts\python.exe
if not exist "%PYTHON%" (
    set PYTHON=python
)

echo [STEP 0/4] Kiem tra va cai dat thu vien AI (soundfile, datasets, peft...)...
"%PYTHON%" -m pip install -r classbridge/training/requirements.txt --quiet
if errorlevel 1 (
    "%PYTHON%" -m pip install soundfile sounddevice datasets peft accelerate evaluate jiwer faster-whisper transformers librosa --quiet
)

echo.
echo [STEP 1/4] Khoi tao audio samples benchmark...
"%PYTHON%" classbridge/data/create_synthetic_samples.py
if errorlevel 1 goto error

echo.
echo [STEP 2/4] Phan chia dataset train / validation...
"%PYTHON%" classbridge/training/prepare_multilingual_manifest.py --input classbridge/data/bilingual_sample_manifest.jsonl --train classbridge/data/train.jsonl --validation classbridge/data/validation.jsonl
if errorlevel 1 goto error

echo.
echo [STEP 3/4] Fine-Tuning Whisper LoRA (openai/whisper-small)...
"%PYTHON%" classbridge/training/finetune_whisper_lora.py --train classbridge/data/train.jsonl --validation classbridge/data/validation.jsonl --model openai/whisper-small --epochs 5 --batch-size 4 --output classbridge/training/outputs/whisper-classbridge-small-lora
if errorlevel 1 goto error

echo.
echo [STEP 4/4] Export sang CTranslate2 INT8...
"%PYTHON%" classbridge/training/export_whisper_lora.py --base-model openai/whisper-small --adapter classbridge/training/outputs/whisper-classbridge-small-lora --ct2-output ai-service/whisper-multi-accent-ct2
if errorlevel 1 goto error

echo.
echo =========================================================================
echo HOAN TAT TOAN BO TIEN TRINH HUAN LUYEN STT LORA & EXPORT CTRANSLATE2!
echo Model moi se tu dong duoc nap khi chay ClassBridge Web AI Service.
echo =========================================================================
goto end

:error
echo.
echo ❌ CO LOI XAY RA TRONG QUA TRINH HUAN LUYEN!
pause
exit /b 1

:end
pause
