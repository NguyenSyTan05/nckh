@echo off
cd /d "d:\TailieuNPKH\classbridge\backend\ai-service"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
set PYTHONUNBUFFERED=1

:: Giải phóng port 8000 nếu đang có process cũ chạy
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
  if not "%%a"=="0" taskkill /F /PID %%a >nul 2>&1
)

:: Khởi chạy backend qua cmd /c bên trong start /b
start "ClassBridge_AI" /b cmd /c ".venv\Scripts\python.exe main.py > runtime-supervised-ai.out.log 2> runtime-supervised-ai.err.log"
echo AI Service daemon launched.
