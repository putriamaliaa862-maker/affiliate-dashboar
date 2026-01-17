@echo off
setlocal

TITLE Affiliate Dashboard Launcher

echo ========================================================
echo    AFFILIATE DASHBOARD STARTUP SCRIPT
echo ========================================================
echo.

REM 1. Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running or not installed.
    echo Please start Docker Desktop and try again.
    pause
    exit /b
)

echo [INFO] Docker is running.
echo.

REM 2. Start Services
echo [INFO] Starting services with Docker Compose...
docker-compose up -d --build

if %errorlevel% neq 0 (
    echo [ERROR] Failed to start services.
    pause
    exit /b
)

echo.
echo [INFO] Services started successfully!
echo.

REM 3. Wait for services to initialize (optional but recommended)
echo [INFO] Waiting 10 seconds for services to initialize...
timeout /t 10 /nobreak >nul

REM 4. Open Browser
echo [INFO] Opening Dashboard in your default browser...
start http://localhost:5173

echo.
echo ========================================================
echo    DASHBOARD IS RUNNING
echo    Frontend: http://localhost:5173
echo    Backend:  http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo ========================================================
echo.
echo Press any key to close this window (services will keep running)...
pause >nul
