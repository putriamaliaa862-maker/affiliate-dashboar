@echo off
REM ========================================
REM STOP REALTIME BOT
REM ========================================

title Stop Shopee Realtime Bot

echo.
echo ========================================
echo   STOPPING SHOPEE REALTIME BOT
echo ========================================
echo.

echo [1/3] Killing Node.js processes...
taskkill /f /im node.exe 2>nul
if errorlevel 1 (
    echo   No Node.js processes found
) else (
    echo   Node.js processes terminated
)

echo.
echo [2/3] Killing Chromium browsers...
taskkill /f /im chromium.exe 2>nul
if errorlevel 1 (
    echo   No Chromium processes found
) else (
    echo   Chromium processes terminated
)

echo.
echo [3/3] Killing Chrome (Playwright)...
for /f "tokens=2" %%a in ('tasklist /fi "WINDOWTITLE eq *Playwright*" 2^>nul ^| find "chrome"') do (
    taskkill /f /pid %%a 2>nul
)

echo.
echo ========================================
echo   BOT STOPPED SUCCESSFULLY
echo ========================================
echo.
pause
