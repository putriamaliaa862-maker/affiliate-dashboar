@echo off
echo ========================================
echo  STARTING FULL AFFILIATE DASHBOARD
echo ========================================
echo.
echo This will start both:
echo - Backend (http://127.0.0.1:8000)
echo - Frontend (http://localhost:5174)
echo.
echo Opening 2 terminal windows...
echo.

cd /d C:\workspace\affiliate-dashboard

echo [1/2] Starting Backend...
start "Affiliate Dashboard - BACKEND" cmd /k "START_BACKEND.bat"

echo Waiting 3 seconds for backend to initialize...
timeout /t 3 /nobreak >nul

echo [2/2] Starting Frontend...
start "Affiliate Dashboard - FRONTEND" cmd /k "START_FRONTEND.bat"

echo.
echo ========================================
echo  DONE! Both servers are starting...
echo ========================================
echo.
echo Backend: http://127.0.0.1:8000/docs
echo Frontend: http://localhost:5174
echo.
echo Close the terminal windows to stop servers.
echo This launcher will close in 5 seconds...
echo.

timeout /t 5 /nobreak >nul
exit
