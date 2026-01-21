@echo off
echo ========================================
echo  STARTING AFFILIATE DASHBOARD BACKEND
echo ========================================
echo.

cd /d C:\workspace\affiliate-dashboard\backend

echo [1/7] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Install Python 3.11+ first.
    pause
    exit /b 1
)
python --version
echo.

echo [2/7] Checking virtual environment...
if not exist "venv\" (
    echo Virtual environment not found. Creating...
    python -m venv venv
    echo Virtual environment created!
) else (
    echo Virtual environment exists.
)
echo.

echo [3/7] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate venv
    pause
    exit /b 1
)
echo Activated!
echo.

echo [4/7] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo.

echo [5/7] Installing dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt --quiet
    echo Dependencies installed!
) else (
    echo WARNING: requirements.txt not found, skipping...
)
echo.

echo [6/7] Starting backend server...
echo.
echo ========================================
echo  Backend running on:
echo  http://127.0.0.1:8000
echo  API Docs: http://127.0.0.1:8000/docs
echo ========================================
echo.
echo Press CTRL+C to stop the server
echo.

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

if errorlevel 1 (
    echo.
    echo ERROR: Backend failed to start!
    echo Check the error above.
    pause
    exit /b 1
)
