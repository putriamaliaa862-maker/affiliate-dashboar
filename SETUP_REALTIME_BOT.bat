@echo off
REM ========================================
REM SETUP BOT - Initial Setup
REM ========================================

title Setup Shopee Realtime Bot

echo.
echo ========================================
echo   SHOPEE REALTIME BOT - INITIAL SETUP
echo ========================================
echo.

cd /d "C:\workspace\affiliate-dashboard\bots\shopee_realtime_bot"

echo [1/4] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo   ERROR: Node.js not installed!
    echo   Please install Node.js from https://nodejs.org
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('node --version') do echo   Node.js version: %%i
)

echo.
echo [2/4] Installing NPM dependencies...
call npm install
if errorlevel 1 (
    echo   ERROR: npm install failed!
    pause
    exit /b 1
)
echo   Dependencies installed successfully

echo.
echo [3/4] Installing Playwright Chromium...
call npx playwright install chromium
if errorlevel 1 (
    echo   ERROR: Playwright install failed!
    pause
    exit /b 1
)
echo   Playwright Chromium installed

echo.
echo [4/4] Creating required directories...
if not exist "logs" mkdir logs
if not exist "screenshots" mkdir screenshots
if not exist "profiles" mkdir profiles
echo   Directories created

echo.
echo ========================================
echo   SETUP COMPLETE!
echo ========================================
echo.
echo Next steps:
echo   1. Edit config\accounts.json with your Shopee accounts
echo   2. Get your Access Code from Dashboard Settings
echo   3. Run: RUN_REALTIME_BOT_24H.bat YOUR_ACCESS_CODE
echo.
pause
