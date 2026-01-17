@echo off
setlocal
TITLE Affiliate Dashboard - Local Launcher

cd /d "%~dp0"

echo ========================================================
echo    AFFILIATE DASHBOARD - LOCAL STARTUP
echo ========================================================
echo.

REM --- CHECK PREREQUISITES ---
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b
)
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH.
    pause
    exit /b
)

REM --- BACKEND SETUP & START ---
echo [INFO] Starting Backend...

REM 1. Create venv if missing
if not exist "backend\venv" (
    echo [SETUP] Creating Python virtual environment...
    python -m venv backend\venv
)

REM 2. Configure Environment (Force SQLite for local)
if not exist "backend\.env" (
    echo [SETUP] Creating local configuration for SQLite...
    (
        echo DATABASE_URL=sqlite:///./affiliate.db
        echo SECRET_KEY=dev-secret-key-123
        echo APP_NAME=Affiliate Dashboard
        echo DEBUG=True
        echo # Shopee API placeholders
        echo SHOPEE_PARTNER_ID=
        echo SHOPEE_PARTNER_KEY=
    ) > backend\.env
    echo [INFO] created backend\.env with SQLite settings.
)

REM 3. Start Backend Server
REM We start the backend in a new window.
start "Affiliate Backend" cmd /k "cd backend && call venv\Scripts\activate && echo [INFO] Installing dependencies... && pip install --upgrade pip && pip install -r requirements.txt && pip install email-validator dnspython && (if not exist affiliate.db (echo [INFO] Creating database and super admin... && python seed_admin.py)) && echo. && echo [INFO] Starting Server... && echo. && echo 🔐 Default Login: admin / Admin123! && echo. && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM --- FRONTEND SETUP & START ---
echo [INFO] Starting Frontend...
REM Start frontend in a new window.
start "Affiliate Frontend" cmd /k "cd frontend && if not exist node_modules (echo [SETUP] Installing npm packages... && npm install) else (echo [INFO] Packages already installed.) && npm run dev"

REM --- BROWSER ---
echo [INFO] Waiting 15 seconds for services to initialize...
timeout /t 15 /nobreak >nul

echo [INFO] Opening Dashboard...
start http://localhost:5173
start http://localhost:8000/docs

echo.
echo ========================================================
echo    SYSTEM RUNNING LOCALLY
echo    - Backend Window: Logs for API (wait for 'Application startup complete')
echo    - Frontend Window: Logs for UI
echo    - Browser: http://localhost:5173
echo.
echo    Troubleshooting:
echo    If the site doesn't load, check the two other windows for errors.
echo    If 'Connection refused', the backend is still starting up.
echo ========================================================
echo.
pause
