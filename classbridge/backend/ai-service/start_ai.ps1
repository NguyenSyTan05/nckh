$aiRoot = "d:\TailieuNPKH\classbridge\backend\ai-service"
$venvRoot = Join-Path $aiRoot ".venv"
$sitePackages = Join-Path $venvRoot "Lib\site-packages"
$python = Join-Path $venvRoot "Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = "C:\Users\Nguyen Sy Tan\AppData\Local\Programs\Python\Python311\python.exe"
}

$env:VIRTUAL_ENV = $venvRoot
$env:PYTHONPATH = "$aiRoot;$sitePackages"
$env:PATH = "$(Join-Path $venvRoot 'Scripts');$env:PATH"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
$env:PYTHONUNBUFFERED = "1"

# 1. Dọn tiến trình cũ ghi trong pid file
$pidFile = Join-Path $aiRoot "runtime-supervised-ai.pid"
if (Test-Path $pidFile) {
  $oldPid = (Get-Content $pidFile -ErrorAction SilentlyContinue).Trim()
  if ($oldPid -match '^\d+$') {
    Stop-Process -Id ([int]$oldPid) -Force -ErrorAction SilentlyContinue
  }
}

# 2. Dọn bất kỳ tiến trình nào đang chiếm dụng port 8000
$activeConn = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($activeConn) {
  foreach ($p in $activeConn) {
    if ($p -gt 0) { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue }
  }
}
Start-Sleep -Milliseconds 500

# 3. Khởi chạy AI Service nền độc lập
$outLog = Join-Path $aiRoot "runtime-supervised-ai.out.log"
$errLog = Join-Path $aiRoot "runtime-supervised-ai.err.log"
$proc = Start-Process -FilePath $python `
  -ArgumentList @("-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000") `
  -WorkingDirectory $aiRoot `
  -RedirectStandardOutput $outLog `
  -RedirectStandardError $errLog `
  -WindowStyle Hidden `
  -PassThru

Set-Content -LiteralPath $pidFile -Value $proc.Id
Write-Host "AI Service started permanently with PID: $($proc.Id)"
