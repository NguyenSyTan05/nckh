$ErrorActionPreference = "Stop"

$aiRoot = Join-Path $PSScriptRoot "ai-service"
$venvRoot = Join-Path $aiRoot ".venv"
$pyvenvConfig = Join-Path $venvRoot "pyvenv.cfg"
$homeLine = Get-Content -LiteralPath $pyvenvConfig |
  Where-Object { $_ -match "^home\s*=" } |
  Select-Object -First 1
if (-not $homeLine) {
  throw "Không đọc được Python home từ $pyvenvConfig"
}

$pythonHome = ($homeLine -split "=", 2)[1].Trim()
$python = Join-Path $pythonHome "python.exe"
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
  throw "Không tìm thấy Python tại $python"
}

$env:VIRTUAL_ENV = $venvRoot
$env:PYTHONPATH = Join-Path $venvRoot "Lib\site-packages"
$env:PATH = "$(Join-Path $venvRoot 'Scripts');$env:PATH"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
Set-Location -LiteralPath $aiRoot
& $python -m uvicorn main:app --host 127.0.0.1 --port 8000
exit $LASTEXITCODE
