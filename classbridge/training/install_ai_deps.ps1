# ClassBridge - Script Cài Đặt Thư Viện AI (Chạy 1 lần duy nhất)
# Cách chạy: .\install_ai_deps.ps1
# Hoặc: powershell -ExecutionPolicy Bypass -File install_ai_deps.ps1

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "   ClassBridge - Cai Dat Thu Vien AI (Training & STT Module)" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# Tim Python venv
$VENV_PYTHON = Join-Path $PSScriptRoot "..\backend\ai-service\.venv\Scripts\python.exe"
$SYS_PYTHON = "python"

if (Test-Path $VENV_PYTHON) {
    $PYTHON = $VENV_PYTHON
    Write-Host "  [OK] Dung Python venv: $PYTHON" -ForegroundColor Green
} else {
    $PYTHON = $SYS_PYTHON
    Write-Host "  [!]  Khong tim thay venv, dung Python he thong: $PYTHON" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  -> Dang kiem tra phac cac thu vien hien co..." -ForegroundColor Gray

# Kiem tra da cai chua
$CHECK = & $PYTHON -c "import faster_whisper; print('OK')" 2>$null
if ($CHECK -eq "OK") {
    Write-Host "  [OK] faster-whisper da duoc cai dat!" -ForegroundColor Green
    $NEED_INSTALL = $false
} else {
    $NEED_INSTALL = $true
}

if ($NEED_INSTALL) {
    Write-Host ""
    Write-Host "  -> Dang cai dat cac thu vien AI can thiet..." -ForegroundColor Yellow
    Write-Host "     (Qua trinh nay co the mat 5-15 phut lan dau)" -ForegroundColor Gray
    Write-Host ""

    # Nang cap pip truoc
    & $PYTHON -m pip install --upgrade pip --quiet

    # Cai dat cac thu vien theo thu tu phu thuoc
    $PACKAGES = @(
        "numpy>=1.24.0",
        "soundfile>=0.12.1",
        "sounddevice>=0.4.6",
        "torch>=2.1.0",
        "torchaudio>=2.1.0",
        "faster-whisper>=1.0.0",
        "transformers>=4.40.0",
        "peft>=0.10.0",
        "datasets>=2.18.0",
        "accelerate>=0.28.0",
        "evaluate>=0.4.0",
        "jiwer>=3.0.0",
        "sacrebleu>=2.3.0",
        "huggingface_hub>=0.22.0",
        "librosa>=0.10.0"
    )

    foreach ($pkg in $PACKAGES) {
        $pkgName = $pkg.Split(">")[0].Split("=")[0]
        Write-Host "  -> Cai: $pkgName ..." -ForegroundColor Gray -NoNewline
        $result = & $PYTHON -m pip install "$pkg" --quiet 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host " [OK]" -ForegroundColor Green
        } else {
            Write-Host " [WARN: $result]" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "  -> Kiem tra ket qua cai dat..." -ForegroundColor Gray

$CHECKS = @(
    @{name="numpy";         cmd="import numpy; print(numpy.__version__)"},
    @{name="torch";         cmd="import torch; print(torch.__version__)"},
    @{name="faster_whisper";cmd="import faster_whisper; print('OK')"},
    @{name="transformers";  cmd="import transformers; print(transformers.__version__)"},
    @{name="peft";          cmd="import peft; print(peft.__version__)"},
    @{name="datasets";      cmd="import datasets; print(datasets.__version__)"},
    @{name="sounddevice";   cmd="import sounddevice; print(sounddevice.__version__)"},
    @{name="soundfile";     cmd="import soundfile; print(soundfile.__version__)"},
    @{name="jiwer";         cmd="import jiwer; print('OK')"}
)

$ALL_OK = $true
foreach ($check in $CHECKS) {
    $ver = & $PYTHON -c $check.cmd 2>$null
    if ($ver) {
        Write-Host ("  [OK] {0,-18} v{1}" -f $check.name, $ver) -ForegroundColor Green
    } else {
        Write-Host ("  [!!] {0,-18} CHUA DUOC CAI" -f $check.name) -ForegroundColor Red
        $ALL_OK = $false
    }
}

Write-Host ""
if ($ALL_OK) {
    Write-Host "=================================================================" -ForegroundColor Green
    Write-Host "   TAT CA THU VIEN DA SAN SANG! Ban co the chay:" -ForegroundColor Green
    Write-Host "   npm run train  --> Huan luyen AI" -ForegroundColor Green
    Write-Host "   npm run dev    --> Chay ung dung" -ForegroundColor Green
    Write-Host "=================================================================" -ForegroundColor Green
} else {
    Write-Host "=================================================================" -ForegroundColor Yellow
    Write-Host "   MOT SO THU VIEN CHUA DUOC CAI. Hay chay thu cong:" -ForegroundColor Yellow
    Write-Host "   $PYTHON -m pip install -r training\requirements.txt" -ForegroundColor Yellow
    Write-Host "=================================================================" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Nhan Enter de dong..."
