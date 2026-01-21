@echo off
echo ========================================
echo  QUICK START - FRONTEND + BROWSER
echo ========================================
echo.

cd /d C:\workspace\affiliate-dashboard\frontend

echo [1/2] Starting frontend server...
echo.

REM Start frontend in new window
start "Affiliate Dashboard - Frontend" cmd /k "npm run dev -- --host --port 5174"

echo [2/2] Waiting for server to start...
timeout /t 5 /nobreak >nul

echo.
echo Opening browser...
start http://localhost:5174/login

echo.
echo ========================================
echo  DONE!
echo ========================================
echo.
echo Frontend server running in separate window
echo Browser opened to login page
echo.
echo To stop: Close the "Frontend" terminal window
echo.

pause
