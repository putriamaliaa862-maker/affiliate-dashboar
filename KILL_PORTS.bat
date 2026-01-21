@echo off
echo ========================================
echo  KILLING PORTS - Affiliate Dashboard
echo ========================================
echo.

cd /d C:\workspace\affiliate-dashboard

echo [1/2] Killing processes on port 8000 (Backend)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Found process: %%a
    taskkill /F /PID %%a >nul 2>&1
    if errorlevel 1 (
        echo Failed to kill %%a
    ) else (
        echo Killed %%a
    )
)
echo ✅ Port 8000 cleaned
echo.

echo [2/2] Killing processes on port 5174 (Frontend)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5174 ^| findstr LISTENING') do (
    echo Found process: %%a
    taskkill /F /PID %%a >nul 2>&1
    if errorlevel 1 (
        echo Failed to kill %%a
    ) else (
        echo Killed %%a
    )
)
echo ✅ Port 5174 cleaned
echo.

echo ========================================
echo  PORTS ARE NOW FREE!
echo ========================================
echo.
echo You can now run START_ALL.bat
echo.

pause
