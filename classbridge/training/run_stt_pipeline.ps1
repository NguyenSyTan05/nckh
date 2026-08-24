param(
    [switch]$SmokeTest
)

# ClassBridge - Automated STT Fine-Tuning & Export Pipeline
# Script tu dong hoa toan bo tien trinh tu cai dat thu vien, tao sample audio, split dataset, fine-tune LoRA den xuat CTranslate2 INT8

$PYTHON = Join-Path $PSScriptRoot "ai-service\.venv\Scripts\python.exe"
if (-not (Test-Path $PYTHON)) {
    $PYTHON = "python"
}

Write-Host ""
Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host "   ClassBridge AI - AUTOMATED STT FINE-TUNING PIPELINE                   " -ForegroundColor Cyan
Write-Host "=========================================================================" -ForegroundColor Cyan

$extraArgs = ""
if ($SmokeTest) {
    Write-Host "⚠️ SMOKE-TEST MODE ENABLED (Ky thuat pipeline check)" -ForegroundColor Yellow
    $extraArgs = "--smoke-test"
}

# ── Step 0: Dong bo va Cai dat thu vien ──────────────────────────────────────
Write-Host ""
Write-Host "[STEP 0/4] Kiem tra va Cai dat thu vien AI (soundfile, datasets, peft)..." -ForegroundColor Yellow
& $PYTHON -m pip install -r classbridge/training/requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "Thu cai dat truc tiep cac goi quan trong..." -ForegroundColor Yellow
    & $PYTHON -m pip install soundfile sounddevice datasets peft accelerate evaluate jiwer faster-whisper transformers librosa --quiet
}

# ── Step 1: Tao sample audio WAV 16kHz ─────────────────────────────────────────
Write-Host ""
Write-Host "[STEP 1/4] Dang khoi tao mau am thanh benchmark..." -ForegroundColor Yellow
& $PYTHON classbridge/data/create_synthetic_samples.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Loi o Step 1. Dung tien trinh." -ForegroundColor Red
    exit 1
}

# ── Step 2: Chia tap train.jsonl va validation.jsonl ───────────────────────────
Write-Host ""
Write-Host "[STEP 2/4] Dang phan chia dataset train/validation..." -ForegroundColor Yellow
if ($SmokeTest) {
    & $PYTHON classbridge/training/prepare_multilingual_manifest.py --input classbridge/data/bilingual_sample_manifest.jsonl --train classbridge/data/train.jsonl --validation classbridge/data/validation.jsonl --smoke-test
} else {
    & $PYTHON classbridge/training/prepare_multilingual_manifest.py --input classbridge/data/bilingual_sample_manifest.jsonl --train classbridge/data/train.jsonl --validation classbridge/data/validation.jsonl
}
if ($LASTEXITCODE -ne 0) {
    Write-Host "Loi o Step 2. Dung tien trinh." -ForegroundColor Red
    exit 1
}

# ── Step 3: Fine-Tune Whisper LoRA ─────────────────────────────────────────────
Write-Host ""
Write-Host "[STEP 3/4] Bat dau Fine-Tuning Whisper LoRA (openai/whisper-small)..." -ForegroundColor Yellow
if ($SmokeTest) {
    & $PYTHON classbridge/training/finetune_whisper_lora.py --train classbridge/data/train.jsonl --validation classbridge/data/validation.jsonl --model openai/whisper-small --epochs 5 --batch-size 4 --output classbridge/training/outputs/whisper-classbridge-small-lora --smoke-test
} else {
    & $PYTHON classbridge/training/finetune_whisper_lora.py --train classbridge/data/train.jsonl --validation classbridge/data/validation.jsonl --model openai/whisper-small --epochs 5 --batch-size 4 --output classbridge/training/outputs/whisper-classbridge-small-lora
}
if ($LASTEXITCODE -ne 0) {
    Write-Host "Loi o Step 3 (Fine-tuning). Dung tien trinh." -ForegroundColor Red
    exit 1
}

# ── Step 4: Export sang CTranslate2 INT8 ───────────────────────────────────────
Write-Host ""
Write-Host "[STEP 4/4] Dang chuyen doi sang CTranslate2 INT8 cho Web Real-Time..." -ForegroundColor Yellow
& $PYTHON classbridge/training/export_whisper_lora.py --base-model openai/whisper-small --adapter classbridge/training/outputs/whisper-classbridge-small-lora --ct2-output classbridge/ai-service/whisper-multi-accent-ct2
if ($LASTEXITCODE -ne 0) {
    Write-Host "Loi o Step 4 (Export). Dung tien trinh." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=========================================================================" -ForegroundColor Green
Write-Host " HOAN TAT TOAN BO TIEN TRINH HUAN LUYEN VÀ EXPORT MODEL ASR!" -ForegroundColor Green
Write-Host " Thu muc CTranslate2 da duoc tao tai: classbridge/ai-service/whisper-multi-accent-ct2" -ForegroundColor Green
Write-Host " Lan chay tiep theo cua Web AI Service se TU DONG nap mo hinh vua train!" -ForegroundColor Green
Write-Host "=========================================================================" -ForegroundColor Green
