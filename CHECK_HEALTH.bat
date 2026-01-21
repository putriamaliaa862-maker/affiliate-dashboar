@echo off
echo ========================================
echo  HEALTH CHECK - Affiliate Dashboard
echo ========================================
echo.

cd /d C:\workspace\affiliate-dashboard

echo Checking backend and frontend status...
echo.

set BACKEND_OK=0
set FRONTEND_OK=0

echo [1/2] Checking Backend (http://localhost:8000/health)...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing -TimeoutSec 3; if ($response.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend OK - Running on port 8000
    set BACKEND_OK=1
) else (
    echo ❌ Backend DOWN - Not responding on port 8000
)
echo.

echo [2/2] Checking Frontend (http://localhost:5174)...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5174' -UseBasicParsing -TimeoutSec 3; if ($response.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend OK - Running on port 5174
    set FRONTEND_OK=1
) else (
    echo ❌ Frontend DOWN - Not responding on port 5174
)
echo.

echo ========================================
echo  RESULTS
echo ========================================
if %BACKEND_OK% equ 1 if %FRONTEND_OK% equ 1 (
    echo ✅ ALL SYSTEMS GO!
    echo.
    echo Backend Health: http://localhost:8000/health
    echo Backend Docs: http://localhost:8000/docs
    echo Frontend: http://localhost:5174
) else (
    echo ❌ SOME SERVICES ARE DOWN
    echo.
    echo 💡 Quick Fix:
    echo    1. Run KILL_PORTS.bat
    echo    2. Run START_ALL.bat
    echo.
    echo Or just run RESET_ALL.bat for full reset
)
echo.

pause
