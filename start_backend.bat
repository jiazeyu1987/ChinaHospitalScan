  @echo off
  cd /d "%~dp0"

  echo Starting hospital scanner service...
  call ../venv/Scripts/Activate.ps1 2>nul || call ../venv/Scripts/activate.bat

if %errorlevel% neq 0 (
    echo Error: Virtual environment not found or not activated
    echo Please make sure the virtual environment exists in '../venv' folder
    pause
    exit /b 1
)

  python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

  pause