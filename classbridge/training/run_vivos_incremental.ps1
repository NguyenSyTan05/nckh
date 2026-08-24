$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root "backend\ai-service\.venv\Scripts\python.exe"
$archive = Join-Path $PSScriptRoot "data\downloads\vivos.tar.gz"
$extract = Join-Path $PSScriptRoot "data\vivos"
$vivosTrain = Join-Path $PSScriptRoot "stages\vivos_increment_train.jsonl"
$vivosValidation = Join-Path $PSScriptRoot "stages\vivos_increment_validation.jsonl"
$stage = Join-Path $PSScriptRoot "stages\vivos_micro9_train.jsonl"
$validation = Join-Path $PSScriptRoot "stages\vivos_micro9_validation.jsonl"
$adapter = Join-Path $PSScriptRoot "outputs\decoder-micro9-vivos-lora"
$merged = Join-Path $PSScriptRoot "outputs\decoder-micro9-vivos-merged"
$ct2 = Join-Path $PSScriptRoot "outputs\decoder-micro9-vivos-ct2"

$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"
$env:HF_DATASETS_CACHE = Join-Path $PSScriptRoot "cache\datasets-v2"
$env:PYTHONIOENCODING = "utf-8"

New-Item -ItemType Directory -Path (Split-Path $archive), (Split-Path $stage) -Force | Out-Null
Write-Output "[1/6] Downloading/resuming VIVOS..."
$downloadUrl = "https://zenodo.org/records/7068130/files/vivos.tar.gz"
$expectedArchiveBytes = 1474408300
$expectedArchiveSha256 = "147477F7A7702CBAFC2EE3808D1C142989D0DBC8D9FCE8E07D5F329D5119E4CA"
$downloaded = (
  (Test-Path -LiteralPath $archive -PathType Leaf) -and
  ((Get-Item -LiteralPath $archive).Length -eq $expectedArchiveBytes) -and
  ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash -eq $expectedArchiveSha256)
)
if ($downloaded) {
  Write-Output "VIVOS archive is already complete and checksum-valid; skipping download."
}
for ($attempt = 1; $attempt -le 120; $attempt++) {
  if ($downloaded) { break }
  Write-Output "Download pass $attempt/120 (resume enabled)..."
  & curl.exe -L --fail --retry 12 --retry-all-errors --retry-delay 10 `
    --connect-timeout 30 --continue-at - --output $archive $downloadUrl
  if ($LASTEXITCODE -eq 0) {
    $downloaded = $true
    break
  }
  Write-Output "Network interrupted; retaining partial archive and retrying in 30 seconds."
  Start-Sleep -Seconds 30
}
if (-not $downloaded) { throw "VIVOS download failed after all resume attempts" }

Write-Output "[2/6] Verifying and preparing speaker-disjoint data..."
& $python (Join-Path $PSScriptRoot "prepare_vivos_incremental.py") `
  --archive $archive --extract-dir $extract `
  --train-output $vivosTrain --validation-output $vivosValidation `
  --max-per-speaker 12 --validation-speakers 8
if ($LASTEXITCODE -ne 0) { throw "VIVOS preparation failed" }

Write-Output "[3/6] Building a balanced 64 EN + 64 VI micro-stage..."
function Convert-TrainingRow($row) {
  $audioPath = if ($row.audio_path) { [string]$row.audio_path } else { [string]$row.audio }
  [ordered]@{
    audio = $audioPath
    audio_path = $audioPath
    text = [string]$row.text
    speaker_id = [string]$row.speaker_id
    accent = [string]$row.accent
    region = [string]$row.region
    language = [string]$row.language
    split = [string]$row.split
    source = [string]$row.source
    dataset = [string]$row.dataset
    duration_seconds = [double]$row.duration_seconds
  }
}
$baseRows = Get-Content (Join-Path $PSScriptRoot "stages\stage1_train.jsonl") |
  ForEach-Object { $_ | ConvertFrom-Json }
$english = $baseRows | Where-Object { $_.language -eq "en" } | Select-Object -First 64
$vietnamese = Get-Content $vivosTrain | ForEach-Object { $_ | ConvertFrom-Json } |
  Select-Object -First 64
@($english) + @($vietnamese) |
  ForEach-Object { Convert-TrainingRow $_ | ConvertTo-Json -Compress } |
  Set-Content -LiteralPath $stage -Encoding utf8
Get-Content (Join-Path $PSScriptRoot "stages\validation.jsonl"), $vivosValidation |
  ForEach-Object { Convert-TrainingRow ($_ | ConvertFrom-Json) | ConvertTo-Json -Compress } |
  Set-Content -LiteralPath $validation -Encoding utf8

Write-Output "[4/6] Training decoder-only candidate..."
& $python -u (Join-Path $PSScriptRoot "finetune_whisper_lora.py") `
  --train $stage --validation $validation --output $adapter `
  --resume-adapter (Join-Path $PSScriptRoot "outputs\decoder-micro1-whisper-small-lora") `
  --epochs 1 --batch-size 1 --gradient-accumulation 8 --learning-rate 0.000005 `
  --lora-rank 8 --lora-alpha 16 --lora-target-modules q_proj v_proj `
  --decoder-only --no-balance-languages --augmentation-probability 0.10 `
  --no-curriculum --skip-trainer-validation
if ($LASTEXITCODE -ne 0) { throw "VIVOS candidate training failed" }

Write-Output "[5/6] Exporting CT2 candidate..."
& $python (Join-Path $PSScriptRoot "export_whisper_lora.py") `
  --base-model openai/whisper-small --adapter $adapter `
  --merged-output $merged --ct2-output $ct2
if ($LASTEXITCODE -ne 0) { throw "VIVOS candidate export failed" }

Write-Output "[6/6] Evaluating old and new unseen speakers..."
& $python (Join-Path $root "test\tools\evaluate_ct2_asr.py") `
  --model $ct2 --manifest $validation
if ($LASTEXITCODE -ne 0) { throw "VIVOS candidate evaluation failed" }
Write-Output "DONE: candidate kept in training outputs; production was not changed."
