@echo off
REM ========================================
REM RUN REALTIME BOT 24H
REM Shopee Playwright Scraper - 24 Hour Mode
REM ========================================

title Shopee Realtime Bot - 24H Mode

echo.
echo ========================================
echo   SHOPEE REALTIME BOT - 24H MODE
echo ========================================
echo.

cd /d "C:\workspace\affiliate-dashboard\bots\shopee_realtime_bot"

REM Check if node_modules exists
if not exist "node_modules" (
    echo [1/3] Installing NPM dependencies...
    call npm install
    if errorlevel 1 (
        echo ERROR: npm install failed!
        pause
        exit /b 1
    )
    echo.
    echo [2/3] Installing Playwright Chromium...
    call npx playwright install chromium
    if errorlevel 1 (
        echo ERROR: Playwright install failed!
        pause
        exit /b 1
    )
    echo.
) else (
    echo [OK] Dependencies already installed
    echo.
)

REM Set environment variables
if "%1"=="" (
    echo.
    echo ========================================
    echo   ACCESS CODE REQUIRED
    echo ========================================
    echo.
    set /p ACCESS_CODE="Enter your Access Code: "
) else (
    set ACCESS_CODE=%1
)

if "%ACCESS_CODE%"=="" (
    echo ERROR: Access Code cannot be empty!
    pause
    exit /b 1
)

set API_BASE=http://localhost:8000/api
set MAX_WORKERS=5
set SYNC_INTERVAL=60000

echo.
echo ========================================
echo   BOT CONFIGURATION
echo ========================================
echo   API: %API_BASE%
echo   Max Workers: %MAX_WORKERS%
echo   Sync Interval: 60 seconds
echo   Mode: VISIBLE (non-headless)
echo ========================================
echo.
echo Press Ctrl+C to stop the bot.
echo.
echo Starting supervisor...
echo.

REM Start the supervisor
node supervisor.js

echo.
echo Bot stopped.
pause
