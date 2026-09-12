@echo off
setlocal
cd /d "%~dp0"
if not exist "backend\.venv\Scripts\python.exe" (
  echo Python environment missing. Follow README.md setup first.
  exit /b 1
)
echo ProofApply: http://127.0.0.1:8000
"backend\.venv\Scripts\python.exe" -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --no-access-log
