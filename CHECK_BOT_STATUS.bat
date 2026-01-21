@echo off
REM ========================================
REM CHECK BOT STATUS
REM ========================================

title Check Bot Status

echo.
echo ========================================
echo   SHOPEE REALTIME BOT - STATUS CHECK
echo ========================================
echo.

REM Check if node is running
echo [1/4] Checking Node.js processes...
tasklist /fi "imagename eq node.exe" 2>nul | find /i "node.exe" >nul
if %errorlevel% equ 0 (
    echo   [OK] Node.js is running
) else (
    echo   [--] Node.js is NOT running
)

echo.
echo [2/4] Checking Chromium browsers...
tasklist /fi "imagename eq chromium.exe" 2>nul | find /i "chromium.exe" >nul
if %errorlevel% equ 0 (
    echo   [OK] Chromium browsers active
) else (
    echo   [--] No Chromium browsers found
)

echo.
echo [3/4] Checking API endpoint...
curl -s -o nul -w "   HTTP Status: %%{http_code}\n" http://localhost:8000/health

echo.
echo [4/4] Checking latest log...
echo.

set LOGS_DIR=bots\shopee_realtime_bot\logs
if exist "%LOGS_DIR%" (
    for /f "delims=" %%i in ('dir /b /od "%LOGS_DIR%\*.log" 2^>nul') do set LATEST_LOG=%%i
    if defined LATEST_LOG (
        echo Latest log: %LOGS_DIR%\%LATEST_LOG%
        echo ----------------------------------------
        type "%LOGS_DIR%\%LATEST_LOG%" 2>nul | more /e
    ) else (
        echo   No log files found
    )
) else (
    echo   Logs directory not found
)

echo.
echo ========================================
pause
