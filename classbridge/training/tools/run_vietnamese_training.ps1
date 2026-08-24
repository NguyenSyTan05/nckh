# run_vietnamese_training.ps1
# Chạy toàn bộ pipeline huấn luyện tiếng Việt (ViMD)
# Bước 1: Trích xuất WAV từ Parquet -> samples/
# Bước 2: Đồng bộ manifest
# Bước 3: Train LoRA Adapter tiếng Việt
# Dùng cửa sổ PowerShell riêng để không làm gián đoạn train tiếng Anh

Set-Location "D:\TailieuNPKH"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  ClassBridge - Vietnamese ViMD Training Pipeline" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# ── BƯỚC 1: Trích xuất 10 mẫu/tỉnh (63 tỉnh ≈ 630 mẫu) ────────────────────
Write-Host "[Buoc 1/3] Trich xuat WAV ViMD (10 mau/tinh x 63 tinh)..." -ForegroundColor Yellow
python vimd_all_provinces.py --per-province 10 --resume
if ($LASTEXITCODE -ne 0) {
    Write-Host "[LOI] Trich xuat ViMD that bai (exit code $LASTEXITCODE)" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Trich xuat WAV hoan tat!" -ForegroundColor Green
Write-Host ""

# ── BƯỚC 2: Đồng bộ manifest với file WAV thực tế ──────────────────────────
Write-Host "[Buoc 2/3] Dong bo manifest vimd_all_provinces.jsonl..." -ForegroundColor Yellow

$manifest = "classbridge/backend/data/manifests/vimd_all_provinces.jsonl"
$wavCount = (Get-ChildItem "classbridge\backend\data\samples\vimd_*.wav" -ErrorAction SilentlyContinue).Count
Write-Host "  -> Phat hien $wavCount file WAV tieng Viet trong samples/" -ForegroundColor Cyan

if ($wavCount -eq 0) {
    Write-Host "[LOI] Khong co file WAV nao! Hay chay vimd_all_provinces.py truoc." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Manifest san sang: $manifest" -ForegroundColor Green
Write-Host ""

# ── BƯỚC 3: Train LoRA Adapter tiếng Việt ──────────────────────────────────
Write-Host "[Buoc 3/3] Bat dau Train LoRA Adapter tieng Viet..." -ForegroundColor Yellow
Write-Host "  Manifest : $manifest" -ForegroundColor Cyan
Write-Host "  Output   : classbridge/backend/ai-service/whisper-vietnamese-lora" -ForegroundColor Cyan
Write-Host "  Steps    : 300" -ForegroundColor Cyan
Write-Host "  Language : Vietnamese" -ForegroundColor Cyan
Write-Host ""

python classbridge/training/train_accent_module.py `
    --train `
    --manifest $manifest `
    --output-dir "classbridge/backend/ai-service/whisper-vietnamese-lora" `
    --language Vietnamese `
    --batch-size 1 `
    --steps 300

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host "  [HOAN TAT] Vietnamese LoRA Adapter da duoc luu tai:" -ForegroundColor Green
    Write-Host "  classbridge/backend/ai-service/whisper-vietnamese-lora/" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Green
} else {
    Write-Host "[LOI] Train that bai (exit code $LASTEXITCODE)" -ForegroundColor Red
}
