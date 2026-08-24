# ================================================================
# ClassBridge - Auto Train: English + Vietnamese (nhanh)
# Dùng whisper-tiny + 100 steps cho tốc độ tối ưu
# ================================================================

Set-Location "D:\TailieuNPKH"

$python = "D:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe"
$trainer = "classbridge/training/train_accent_module.py"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   ClassBridge Auto-Trainer - TIENG ANH + TIENG VIET" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# ── BƯỚC 1: Train Tiếng Anh ─────────────────────────────────────
Write-Host "[1/2] Bat dau train TIENG ANH (whisper-tiny, 100 steps)..." -ForegroundColor Yellow
Write-Host "      Manifest: classbridge/backend/data/manifests/english_accent_samples.jsonl"
Write-Host ""

$t1 = Get-Date
& $python $trainer `
    --train `
    --manifest "classbridge/backend/data/manifests/english_accent_samples.jsonl" `
    --output-dir "classbridge/backend/data/samples" `
    --model "openai/whisper-tiny" `
    --steps 100 `
    --batch-size 1 `
    --language English

$elapsed1 = [int]((Get-Date) - $t1).TotalMinutes
Write-Host ""
if ($LASTEXITCODE -eq 0) {
    Write-Host "[1/2] TIENG ANH hoan tat sau ~$elapsed1 phut!" -ForegroundColor Green
} else {
    Write-Host "[1/2] TIENG ANH gap loi (exit code: $LASTEXITCODE)" -ForegroundColor Red
    Write-Host "      Kiem tra log phia tren de sua loi." -ForegroundColor Red
}

Write-Host ""

# ── BƯỚC 2: Train Tiếng Việt ────────────────────────────────────
Write-Host "[2/2] Bat dau train TIENG VIET (whisper-tiny, 100 steps)..." -ForegroundColor Yellow
Write-Host "      Manifest: classbridge/backend/data/manifests/vimd_all_provinces.jsonl"
Write-Host ""

$t2 = Get-Date
& $python $trainer `
    --train `
    --manifest "classbridge/backend/data/manifests/vimd_all_provinces.jsonl" `
    --output-dir "classbridge/backend/data/samples" `
    --model "openai/whisper-tiny" `
    --steps 100 `
    --batch-size 1 `
    --language Vietnamese

$elapsed2 = [int]((Get-Date) - $t2).TotalMinutes
Write-Host ""
if ($LASTEXITCODE -eq 0) {
    Write-Host "[2/2] TIENG VIET hoan tat sau ~$elapsed2 phut!" -ForegroundColor Green
} else {
    Write-Host "[2/2] TIENG VIET gap loi (exit code: $LASTEXITCODE)" -ForegroundColor Red
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   HOAN TAT! Kiem tra ket qua tai:" -ForegroundColor Green
Write-Host "   D:\TailieuNPKH\classbridge\backend\data\samples\" -ForegroundColor Green
Write-Host "   (Tim cac file adapter_model.bin, adapter_config.json)" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
