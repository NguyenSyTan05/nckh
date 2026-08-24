# ============================================================
# ClassBridge - Cleanup Script
# Xoa tat ca file log, pid va stub Python thua
# Chay: powershell -ExecutionPolicy Bypass -File cleanup_files.ps1
# ============================================================

Set-Location "D:\TailieuNPKH"
$total = 0

Write-Host "" 
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  ClassBridge - Don dep file thua" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# -- 1. Xoa *.log trong ai-service/ ----------------------------------
Write-Host "[1/4] Xoa *.log trong classbridge/backend/ai-service/..." -ForegroundColor Yellow
$logs1 = Get-ChildItem "classbridge\backend\ai-service\*.log" -ErrorAction SilentlyContinue
foreach ($f in $logs1) {
    Remove-Item $f.FullName -Force -ErrorAction SilentlyContinue
    Write-Host "  - $($f.Name)" -ForegroundColor DarkGray
    $total++
}
Write-Host "  -> Da xoa $($logs1.Count) file log" -ForegroundColor Green

# -- 2. Xoa *.pid trong ai-service/ ----------------------------------
Write-Host ""
Write-Host "[2/4] Xoa *.pid trong classbridge/backend/ai-service/..." -ForegroundColor Yellow
$pids1 = Get-ChildItem "classbridge\backend\ai-service\*.pid" -ErrorAction SilentlyContinue
foreach ($f in $pids1) {
    Remove-Item $f.FullName -Force -ErrorAction SilentlyContinue
    Write-Host "  - $($f.Name)" -ForegroundColor DarkGray
    $total++
}
Write-Host "  -> Da xoa $($pids1.Count) file pid" -ForegroundColor Green

# -- 3. Xoa *.log trong classbridge/ (root) --------------------------
Write-Host ""
Write-Host "[3/4] Xoa *.log trong classbridge/ (root)..." -ForegroundColor Yellow
$logs2 = Get-ChildItem "classbridge\*.log" -ErrorAction SilentlyContinue
foreach ($f in $logs2) {
    Remove-Item $f.FullName -Force -ErrorAction SilentlyContinue
    Write-Host "  - $($f.Name)" -ForegroundColor DarkGray
    $total++
}
Write-Host "  -> Da xoa $($logs2.Count) file log" -ForegroundColor Green

# -- 4. Xoa stub Python files trong ai-service/ ----------------------
Write-Host ""
Write-Host "[4/4] Xoa file stub Python (chi redirect) trong ai-service/..." -ForegroundColor Yellow
$stubs = @(
    "classbridge\backend\ai-service\train_accent_module.py",
    "classbridge\backend\ai-service\train_translation_module.py",
    "classbridge\backend\ai-service\train_master_manager.py",
    "classbridge\backend\ai-service\record_and_train_voice.py"
)
foreach ($f in $stubs) {
    if (Test-Path $f) {
        Remove-Item $f -Force -ErrorAction SilentlyContinue
        Write-Host "  - $([System.IO.Path]::GetFileName($f))" -ForegroundColor DarkGray
        $total++
    }
}
Write-Host "  -> Da xoa stub files" -ForegroundColor Green

# -- Tong ket --------------------------------------------------------
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  HOAN TAT! Tong cong da xoa: $total file" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
