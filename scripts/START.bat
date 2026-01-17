@echo off
REM ==========================================
REM   AFFILIATE DASHBOARD - START SCRIPT
REM   Windows (.bat) - Click to Run
REM ==========================================

setlocal enabledelayedexpansion

:menu
cls
echo.
echo ╔════════════════════════════════════════════════════╗
echo ║   AFFILIATE DASHBOARD - STARTUP MENU               ║
echo ╚════════════════════════════════════════════════════╝
echo.
echo   [1] Start All Services (Docker)
echo   [2] Start Backend Only (Local)
echo   [3] Start Frontend Only (Local)
echo   [4] Create Super Admin (First Time Setup)
echo   [5] Stop All Services
echo   [6] View Logs
echo   [7] Open API Documentation
echo   [8] Exit
echo.
set /p choice="Pilih opsi (1-8): "

if "%choice%"=="1" goto docker_start
if "%choice%"=="2" goto backend_only
if "%choice%"=="3" goto frontend_only
if "%choice%"=="4" goto seed_admin
if "%choice%"=="5" goto stop_services
if "%choice%"=="6" goto view_logs
if "%choice%"=="7" goto open_docs
if "%choice%"=="8" goto end
echo Invalid choice. Please try again.
timeout /t 2 /nobreak >nul
goto menu

REM ==========================================
REM   OPTION 1: Docker Start
REM ==========================================
:docker_start
cls
echo.
echo ╔════════════════════════════════════════════════════╗
echo ║   Starting with Docker Compose...                  ║
echo ╚════════════════════════════════════════════════════╝
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed or not in PATH
    echo.
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    echo.
    pause
    goto menu
)

echo ✓ Docker found
echo.

REM Change to project directory
cd /d "%~dp0"

REM Check if docker-compose.yml exists
if not exist "docker-compose.yml" (
    echo ❌ docker-compose.yml not found
    pause
    goto menu
)

echo 🔨 Building Docker images...
docker-compose build
if errorlevel 1 (
    echo ❌ Build failed
    pause
    goto menu
)
echo ✓ Build completed
echo.

echo 🚀 Starting services...
docker-compose up -d
if errorlevel 1 (
    echo ❌ Failed to start services
    pause
    goto menu
)
echo ✓ Services started
echo.

echo ⏳ Waiting for services to be ready...
timeout /t 15 /nobreak

echo.
echo ✓ Services are running!
echo.
echo 📊 ACCESS POINTS:
echo   Frontend:  http://localhost:5173
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo.

start http://localhost:5173

pause
goto menu

REM ==========================================
REM   OPTION 2: Backend Only (Local)
REM ==========================================
:backend_only
cls
echo.
echo ╔════════════════════════════════════════════════════╗
echo ║   Starting Backend Server...                       ║
echo ╚════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0\backend"

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        echo Make sure Python is installed and in PATH
        pause
        goto menu
    )
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
pip install email-validator dnspython

REM Check if database exists, if not create and seed
if not exist "affiliate.db" (
    echo.
    echo Database not found. Creating and seeding...
    python seed_admin.py
    echo.
)

echo.
echo 🚀 Starting Backend Server on http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
echo.
echo 🔐 Default Login:
echo    Username: admin
echo    Password: Admin123!
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start uvicorn server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
goto menu

REM ==========================================
REM   OPTION 3: Frontend Only (Local)
REM ==========================================
:frontend_only
cls
echo.
echo ╔════════════════════════════════════════════════════╗
echo ║   Starting Frontend Development Server...          ║
echo ╚════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0\frontend"

REM Check if node_modules exists
if not exist "node_modules\" (
    echo Installing dependencies...
    npm install
)

echo.
echo 🚀 Starting Frontend Server on http://localhost:5173
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start vite dev server
npm run dev

pause
goto menu

REM ==========================================
REM   OPTION 4: Seed Super Admin
REM ==========================================
:seed_admin
cls
echo.
echo ╔════════════════════════════════════════════════════╗
echo ║   Creating Super Admin User...                     ║
echo ╚════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0\backend"

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        goto menu
    )
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing required dependencies...
pip install --upgrade pip
pip install -r requirements.txt
pip install email-validator dnspython

echo.
echo Running seed script...
echo.
python seed_admin.py

echo.
echo ✅ Setup complete!
echo.
echo 🔐 Default Login Credentials:
echo    Username: admin
echo    Email:    admin@affiliatedashboard.com
echo    Password: Admin123!
echo.
echo ⚠️  IMPORTANT: Change the default password after first login!
echo    Use: POST /api/users/{id}/change-password
echo.
pause
goto menu

REM ==========================================
REM   OPTION 5: Stop Services
REM ==========================================
:stop_services
cls
echo.
echo ╔════════════════════════════════════════════════════╗
echo ║   Stopping All Services...                         ║
echo ╚════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

docker-compose down

echo.
echo ✓ All services stopped
echo.
pause
goto menu

REM ==========================================
REM   OPTION 6: View Logs
REM ==========================================
:view_logs
cls
echo.
echo ╔════════════════════════════════════════════════════╗
echo ║   Viewing Docker Logs...                           ║
echo ║   Press Ctrl+C to exit logs                        ║
echo ╚════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

docker-compose logs -f

pause
goto menu

REM ==========================================
REM   OPTION 7: Open API Docs
REM ==========================================
:open_docs
cls
echo.
echo 🌐 Opening API Documentation...
echo.

start http://localhost:8000/docs

timeout /t 2 /nobreak >nul
goto menu

REM ==========================================
REM   EXIT
REM ==========================================
:end
cls
echo.
echo ╔════════════════════════════════════════════════════╗
echo ║   Thank you for using Affiliate Dashboard!         ║
echo ╚════════════════════════════════════════════════════╝
echo.
timeout /t 2 /nobreak >nul
exit
