param (
    [string]$Mode = ""
)

$ErrorActionPreference = "Stop"
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding = [System.Text.Encoding]::UTF8
} catch {}

$projectRoot = $PSScriptRoot
$webRoot = Join-Path $projectRoot "frontend"
$backendRoot = Join-Path $projectRoot "backend"
$aiRoot = Join-Path $backendRoot "ai-service"
$venvRoot = Join-Path $aiRoot ".venv"
$sitePackages = Join-Path $venvRoot "Lib\site-packages"
$pyvenvConfig = Join-Path $venvRoot "pyvenv.cfg"

if (-not (Test-Path -LiteralPath $pyvenvConfig -PathType Leaf)) {
  throw "Khong tim thay moi truong Python tai $venvRoot"
}

$homeLine = Get-Content -LiteralPath $pyvenvConfig |
  Where-Object { $_ -match "^home\s*=" } |
  Select-Object -First 1
if (-not $homeLine) {
  throw "Khong doc duoc Python home tu pyvenv.cfg"
}

$pythonHome = ($homeLine -split "=", 2)[1].Trim()
# On this Windows installation the venv launcher hands execution to its base
# interpreter and exits, leaving the supervisor with a stale PID. Launch the
# base executable directly while VIRTUAL_ENV/PYTHONPATH below keep the venv
# packages active, so the monitored PID is the actual Uvicorn process.
$python = Join-Path $pythonHome "python.exe"
$npm = (Get-Command npm.cmd).Source
$node = (Get-Command node.exe).Source
$vinextCli = Join-Path $webRoot "node_modules\vinext\dist\cli.js"
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
  throw "Khong tim thay Python tai $python"
}

$env:VIRTUAL_ENV = $venvRoot
$env:PYTHONPATH = $sitePackages
$env:PATH = "$(Join-Path $venvRoot 'Scripts');$env:PATH"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"

# Low-latency classroom profile. Avoid running several PyTorch generations on
# the same CPU at once; it increases contention and makes every translation
# slower. A shorter rolling ASR window and greedy decoding keep live captions
# close to the speaker while the accurate models remain available offline.
if (-not $env:WHISPER_DEVICE) { $env:WHISPER_DEVICE = "cuda" }
if (-not $env:WHISPER_COMPUTE_TYPE) { $env:WHISPER_COMPUTE_TYPE = "int8_float16" }
# Unified ASR & NLLB-200 Architecture Configuration
$systranSmall = "C:\Users\Nguyen Sy Tan\.cache\huggingface\hub\models--Systran--faster-whisper-small\snapshots\536b0662742c02347bc0e980a01041f333bce120"
if (-not $env:WHISPER_MODEL) {
  if (Test-Path -LiteralPath $systranSmall) {
    $env:WHISPER_MODEL = $systranSmall
  } else {
    $env:WHISPER_MODEL = "small"
  }
}
if (-not $env:WHISPER_VI_MODEL) {
  $env:WHISPER_VI_MODEL = $env:WHISPER_MODEL
}
if (-not $env:WHISPER_EN_MODEL) {
  $env:WHISPER_EN_MODEL = $env:WHISPER_MODEL
}
if (-not $env:WHISPER_CPU_THREADS) { $env:WHISPER_CPU_THREADS = "8" }
if (-not $env:WHISPER_BEAM_SIZE) { $env:WHISPER_BEAM_SIZE = "1" }
if (-not $env:WHISPER_MUSIC_BEAM_SIZE) { $env:WHISPER_MUSIC_BEAM_SIZE = "1" }
if (-not $env:WHISPER_ACCURATE_BEAM_SIZE) { $env:WHISPER_ACCURATE_BEAM_SIZE = "2" }
if (-not $env:STREAM_UPDATE_SECONDS) { $env:STREAM_UPDATE_SECONDS = "0.3" }
if (-not $env:STREAM_ROLLING_SECONDS) { $env:STREAM_ROLLING_SECONDS = "8" }
if (-not $env:STREAM_FINAL_SILENCE_SECONDS) { $env:STREAM_FINAL_SILENCE_SECONDS = "2.5" }
if (-not $env:STREAM_FINAL_WORDS) { $env:STREAM_FINAL_WORDS = "80" }
if (-not $env:STREAM_FINAL_ACCURATE) { $env:STREAM_FINAL_ACCURATE = "true" }
if (-not $env:WHISPER_RETRY_CONFIDENCE) { $env:WHISPER_RETRY_CONFIDENCE = "0.38" }
if (-not $env:WHISPER_VI_RETRY_CONFIDENCE) { $env:WHISPER_VI_RETRY_CONFIDENCE = "0.42" }
if (-not $env:TRANSLATION_CPU_THREADS) { $env:TRANSLATION_CPU_THREADS = "4" }
if (-not $env:TRANSLATION_NUM_WORKERS) { $env:TRANSLATION_NUM_WORKERS = "1" }
if (-not $env:TRANSLATION_MAX_NEW_TOKENS) { $env:TRANSLATION_MAX_NEW_TOKENS = "64" }
if (-not $env:TRANSLATION_USE_ENSEMBLE) { $env:TRANSLATION_USE_ENSEMBLE = "true" }

function Stop-ProcessTree([int]$ProcessId) {
  $children = Get-CimInstance Win32_Process -Filter "ParentProcessId=$ProcessId" -ErrorAction SilentlyContinue
  foreach ($child in $children) {
    Stop-ProcessTree -ProcessId $child.ProcessId
  }
  Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue
}

function Start-FullApp {
    Write-Host "`n[START] Dang khoi dong ClassBridge System (AI Service + Web App)..." -ForegroundColor Green
    $aiProcess = $null
    $webProcess = $null
    try {
      # Stop only processes recorded by a previous ClassBridge run or holding required ports.
      foreach ($pidFile in @(
        (Join-Path $webRoot "runtime-supervised-web.pid"),
        (Join-Path $aiRoot "runtime-supervised-ai.pid")
      )) {
        if (Test-Path -LiteralPath $pidFile -PathType Leaf) {
          $oldPid = Get-Content -LiteralPath $pidFile -ErrorAction SilentlyContinue
          if ($oldPid -match '^\d+$') {
            Stop-ProcessTree -ProcessId ([int]$oldPid)
          }
          Remove-Item -LiteralPath $pidFile -Force -ErrorAction SilentlyContinue
        }
      }

      # Đảm bảo giải phóng hoàn toàn port 8000 và port 3000 trước khi khởi động
      $portProcesses = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
        Where-Object { $_.LocalPort -in 8000, 3000 } |
        Select-Object -ExpandProperty OwningProcess -Unique
      foreach ($procId in $portProcesses) {
        if ($procId -gt 0) {
          Stop-ProcessTree -ProcessId $procId
        }
      }
      Start-Sleep -Seconds 1

      Write-Host "  -> Dang khoi dong AI Service (Port 8000 - Kien Truc 2-Module)..." -ForegroundColor Yellow
      $aiProcess = Start-Process -FilePath $python `
        -ArgumentList @("-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000") `
        -WorkingDirectory $aiRoot `
        -RedirectStandardOutput (Join-Path $aiRoot "runtime-supervised-ai.out.log") `
        -RedirectStandardError (Join-Path $aiRoot "runtime-supervised-ai.err.log") `
        -WindowStyle Hidden `
        -PassThru
      Set-Content -LiteralPath (Join-Path $aiRoot "runtime-supervised-ai.pid") -Value $aiProcess.Id

      $aiReady = $false
      for ($attempt = 0; $attempt -lt 180; $attempt++) {
        try {
          $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 1 -ErrorAction Stop
          if ($health.status -eq "ok") {
            $aiReady = $true
            break
          }
        } catch {}

        # Nếu tiến trình launcher đã kết thúc nhưng tiến trình con đang giữ port 8000
        if ($aiProcess.HasExited) {
          $portConn = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
          if ($portConn) {
            $realPid = $portConn.OwningProcess | Select-Object -First 1
            if ($realPid -gt 0) {
              $aiProcess = Get-Process -Id $realPid -ErrorAction SilentlyContinue
              Set-Content -LiteralPath (Join-Path $aiRoot "runtime-supervised-ai.pid") -Value $realPid
            }
          } else {
            # Kiểm tra xem có log lỗi thực sự không
            $errContent = ""
            $errLogPath = Join-Path $aiRoot "runtime-supervised-ai.err.log"
            if (Test-Path $errLogPath) {
              $errContent = (Get-Content $errLogPath -Raw -ErrorAction SilentlyContinue).Trim()
            }
            if ($errContent -match "Traceback|ModuleNotFoundError|SyntaxError|ImportError") {
              throw "AI da dung trong luc khoi dong: $errContent"
            }
          }
        }
        Start-Sleep -Seconds 1
      }
      if (-not $aiReady) {
        throw "AI khong san sang sau 60 giay."
      }
      Write-Host "  [OK] AI Service da san sang!" -ForegroundColor Green

      Write-Host "  -> Dang build Web App..." -ForegroundColor Yellow
      Remove-Item -LiteralPath (Join-Path $webRoot "dist") -Recurse -Force -ErrorAction SilentlyContinue
      & $npm --prefix $webRoot run build
      if ($LASTEXITCODE -ne 0) {
        throw "Build Web that bai."
      }

      Write-Host "  -> Dang khoi dong Web App (Port 3000)..." -ForegroundColor Yellow
      # Run the Windows asset compatibility patch before starting vinext.
      # Starting through npm.cmd creates a short-lived wrapper process on
      # Windows, so monitoring that PID incorrectly reports that the web app
      # stopped while its Node child is still serving port 3000.
      & $node (Join-Path $webRoot "scripts\patch-vinext-windows-static.mjs")
      if ($LASTEXITCODE -ne 0) {
        throw "Khong the ap dung ban va static asset cho Windows."
      }
      $webProcess = Start-Process -FilePath $node `
        -ArgumentList @($vinextCli, "start", "-H", "0.0.0.0", "-p", "3000") `
        -WorkingDirectory $webRoot `
        -RedirectStandardOutput (Join-Path $webRoot "runtime-supervised-web.out.log") `
        -RedirectStandardError (Join-Path $webRoot "runtime-supervised-web.err.log") `
        -WindowStyle Hidden `
        -PassThru
      Set-Content -LiteralPath (Join-Path $webRoot "runtime-supervised-web.pid") -Value $webProcess.Id

      $webReady = $false
      for ($attempt = 0; $attempt -lt 60; $attempt++) {
        if ($webProcess.HasExited) {
          throw "Web da dung trong luc khoi dong. Xem runtime-supervised-web.err.log."
        }
        try {
          $response = Invoke-WebRequest -Uri "http://127.0.0.1:3000" -TimeoutSec 1 -UseBasicParsing
          if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
            $webReady = $true
            break
          }
        } catch {
          Start-Sleep -Seconds 1
        }
      }
      if (-not $webReady) {
        throw "Web khong san sang sau 180 giay."
      }
      Write-Host "  [OK] Web App da san sang!" -ForegroundColor Green

      Write-Host "`n=========================================================================" -ForegroundColor Cyan
      Write-Host " [SUCCESS] ClassBridge AI (Unified ASR + Meta NLLB-200) da hoat dong thanh cong!" -ForegroundColor Green
      Write-Host "   Web App: http://localhost:3000" -ForegroundColor Cyan
      Write-Host "   Unified AI Service (NLLB-200 & Unified ASR): http://localhost:8000" -ForegroundColor Cyan
      Write-Host " (Nhan Ctrl+C de dung he thong)" -ForegroundColor Gray
      Write-Host "=========================================================================`n" -ForegroundColor Cyan

      $failedAiChecks = 0
      $failedWebChecks = 0
      while ($true) {
        Start-Sleep -Seconds 5


        # Kiem tra trang thai phuc vu HTTP
        $aiOk = $false
        if ($null -ne $aiProcess -and -not $aiProcess.HasExited) {
          $aiOk = $true
        } else {
          try {
            $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 3 -ErrorAction Stop
            if ($health.status -eq "ok") { $aiOk = $true }
          } catch {
            $aiPort = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
            if ($aiPort) { $aiOk = $true }
          }
        }

        if ($aiOk) {
          $failedAiChecks = 0
        } else {
          $failedAiChecks++
          if ($failedAiChecks -ge 12) {
            throw "AI Service (Port 8000) khong phan hoi sau 60 giay."
          }
        }

        $webOk = $false
        if ($null -ne $webProcess -and -not $webProcess.HasExited) {
          $webOk = $true
        } else {
          try {
            $res = Invoke-WebRequest -Uri "http://127.0.0.1:3000" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
            if ($res.StatusCode -ge 200 -and $res.StatusCode -lt 500) { $webOk = $true }
          } catch {
            $webPort = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue
            if ($webPort) { $webOk = $true }
          }
        }

        if ($webOk) {
          $failedWebChecks = 0
        } else {
          $failedWebChecks++
          if ($failedWebChecks -ge 12) {
            throw "Web App (Port 3000) khong phan hoi sau 60 giay."
          }
        }
      }


    } finally {
      foreach ($process in @($webProcess, $aiProcess)) {
        if ($null -ne $process -and -not $process.HasExited) {
          Stop-ProcessTree -ProcessId $process.Id
        }
      }
      Remove-Item -LiteralPath (Join-Path $webRoot "runtime-supervised-web.pid") -Force -ErrorAction SilentlyContinue
      Remove-Item -LiteralPath (Join-Path $aiRoot "runtime-supervised-ai.pid") -Force -ErrorAction SilentlyContinue
    }
}

function Start-TrainAI {
    Write-Host "`n[TRAIN] Kich hoat Trinh Quan Ly Train AI ClassBridge..." -ForegroundColor Cyan
    $trainingRoot = Join-Path $projectRoot "training"
    Set-Location -LiteralPath $trainingRoot
    & $python "train_master_manager.py"
}

function Start-TrainVoice {
    Write-Host "`n[TRAIN] Kich hoat Huấn Luyện Giọng Nói Cá Nhân (Personalized Voice Fine-Tuner)..." -ForegroundColor Cyan
    $trainingRoot = Join-Path $projectRoot "training"
    Set-Location -LiteralPath $trainingRoot
    & $python "record_and_train_voice.py"
}

function Start-TrainAccent {
    Write-Host "`n[TRAIN] Kich hoat Huấn Luyện Đa Giọng Vùng Miền & Tiếng Anh Quốc Tế..." -ForegroundColor Cyan
    $trainingRoot = Join-Path $projectRoot "training"
    Set-Location -LiteralPath $trainingRoot
    & $python "train_accent_module.py"
}

function Start-TrainDTU {
    Write-Host "`n[TRAIN] Kich hoat Fine-Tune Whisper Nâng Cao DTU (LoRA r=32 + DTU Vocab)..." -ForegroundColor Cyan
    $trainingRoot = Join-Path $projectRoot "training"
    Set-Location -LiteralPath $trainingRoot
    & $python "finetune_whisper_lora.py" --curriculum --balance-languages
}

function Start-RecordDataset {
    Write-Host "`n[RECORD] Kich hoat Thu Thập Dữ Liệu Giọng Nói ClassBridge..." -ForegroundColor Cyan
    $trainingRoot = Join-Path $projectRoot "training"
    Set-Location -LiteralPath $trainingRoot
    & $python "record_classbridge_dataset.py"
}

# Main Selection Logic
if ($Mode -eq "run") {
    Start-FullApp
} elseif ($Mode -eq "train") {
    Start-TrainAI
} elseif ($Mode -eq "voice") {
    Start-TrainVoice
} elseif ($Mode -eq "accent") {
    Start-TrainAccent
} elseif ($Mode -eq "dtu") {
    Start-TrainDTU
} elseif ($Mode -eq "record") {
    Start-RecordDataset
} else {
    Write-Host "`n=========================================================================" -ForegroundColor Cyan
    Write-Host "         CLASSBRIDGE AI - UNIFIED MASTER CONTROL SYSTEM                  " -ForegroundColor Green
    Write-Host "=========================================================================" -ForegroundColor Cyan
    Write-Host " Lua chon che do chay:" -ForegroundColor Yellow
    Write-Host "   [1] Chay Toan Bo Ung Dung ClassBridge (Web App + AI Service)" -ForegroundColor White
    Write-Host "   [2] Kich hoat Trinh Train AI & Danh Gia Mo Hinh (Train Master Manager)" -ForegroundColor White
    Write-Host "   [3] Train Giong Noi Ca Nhan (Thu am & Fine-tune 15 cau truc tiep)" -ForegroundColor White
    Write-Host "   [4] Train Da Giong Vung Mien & Tieng Anh Giong Viet (Multi-Accent ASR)" -ForegroundColor White
    Write-Host "   [5] Train Whisper Nang Cao DTU (LoRA r=32 + DTU Academic Vocab)" -ForegroundColor White
    Write-Host "   [6] Thu du lieu nguoi Viet noi tieng Anh (Teacher + Support)" -ForegroundColor White
    Write-Host "   [0] Thoat" -ForegroundColor Gray
    Write-Host "=========================================================================" -ForegroundColor Cyan
    
    $choice = Read-Host "-> Nhap lua chon cua ban (Mac dinh 1)"
    if ($choice -eq "" -or $choice -eq "1") {
        Start-FullApp
    } elseif ($choice -eq "2") {
        Start-TrainAI
    } elseif ($choice -eq "3") {
        Start-TrainVoice
    } elseif ($choice -eq "4") {
        Start-TrainAccent
    } elseif ($choice -eq "5") {
        Start-TrainDTU
    } elseif ($choice -eq "6") {
        Start-RecordDataset
    } else {
        Write-Host "Cam on ban da su dung ClassBridge!" -ForegroundColor Green
    }
}
