@echo off
cd /d %~dp0
if not exist ".venv\Scripts\pythonw.exe" (
  echo Virtual environment not found. Create it first:
  echo   python -m venv .venv
  echo   .venv\Scripts\python -m pip install -r requirements.txt
  exit /b 1
)
start "" ".venv\Scripts\pythonw.exe" "app.py"
exit /b 0
