@echo off
echo ========================================
echo  RESET MODE - Affiliate Dashboard
echo ========================================
echo.
echo Full system reset incoming...
echo Gas pol reset semua! 🚀
echo.

cd /d C:\workspace\affiliate-dashboard

REM Check if required files exist
if not exist "KILL_PORTS.bat" (
    echo ❌ ERROR: KILL_PORTS.bat not found!
    echo Please make sure all .bat files are in the root folder.
    pause
    exit /b 1
)

if not exist "START_ALL.bat" (
    echo ❌ ERROR: START_ALL.bat not found!
    echo Please make sure all .bat files are in the root folder.
    pause
    exit /b 1
)

if not exist "CHECK_HEALTH.bat" (
    echo ❌ ERROR: CHECK_HEALTH.bat not found!
    echo Please make sure all .bat files are in the root folder.
    pause
    exit /b 1
)

echo [1/7] Cleaning ports...
call KILL_PORTS.bat
echo.

echo [2/7] Waiting 2 seconds...
timeout /t 2 /nobreak >nul
echo Sip, lanjut! ✅
echo.

echo [3/7] Starting backend and frontend...
start "Affiliate Dashboard - BACKEND" cmd /k "START_BACKEND.bat"
timeout /t 2 /nobreak >nul
start "Affiliate Dashboard - FRONTEND" cmd /k "START_FRONTEND.bat"
echo Servers launching... 🚀
echo.

echo [4/7] Waiting 8 seconds for servers to boot...
echo This might take a moment, grab some coffee ☕
timeout /t 8 /nobreak >nul
echo.

echo [5/7] Health check...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/health' -UseBasicParsing -TimeoutSec 3; if ($response.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend OK
    set BACKEND_OK=1
) else (
    echo ⚠️  Backend not ready yet, might need more time
    set BACKEND_OK=0
)

powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5174' -UseBasicParsing -TimeoutSec 3; if ($response.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend OK
    set FRONTEND_OK=1
) else (
    echo ⚠️  Frontend not ready yet, might need more time
    set FRONTEND_OK=0
)
echo.

echo [6/7] Opening browsers...
timeout /t 2 /nobreak >nul
echo Opening Frontend Dashboard...
start http://localhost:5174
timeout /t 1 /nobreak >nul
echo Opening Backend API Docs...
start http://127.0.0.1:8000/docs
echo.

echo [7/7] DONE! 🎉
echo ========================================
echo  AFFILIATE DASHBOARD IS LIVE!
echo ========================================
echo.
echo Frontend: http://localhost:5174
echo Backend Docs: http://127.0.0.1:8000/docs
echo.
echo Check the 2 terminal windows for logs.
echo Close terminals to stop servers.
echo.
echo 💡 Troubleshooting:
echo    - If pages don't load, wait 10 more seconds
echo    - Run CHECK_HEALTH.bat to verify
echo    - Check terminal windows for errors
echo.

pause
