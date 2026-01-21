@echo off
echo ========================================
echo  STARTING AFFILIATE DASHBOARD FRONTEND
echo ========================================
echo.

cd /d C:\workspace\affiliate-dashboard\frontend

echo [1/5] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found! Install Node.js 18+ first.
    pause
    exit /b 1
)
node --version
echo.

echo [2/5] Checking npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: npm not found!
    pause
    exit /b 1
)
npm --version
echo.

echo [3/5] Checking node_modules...
if not exist "node_modules\" (
    echo node_modules not found. Installing...
    npm install
    if errorlevel 1 (
        echo ERROR: npm install failed!
        pause
        exit /b 1
    )
    echo Dependencies installed!
) else (
    echo node_modules exists.
)
echo.

echo [4/5] Starting frontend dev server...
echo.
echo ========================================
echo  Frontend running on:
echo  http://localhost:5174
echo ========================================
echo.
echo Press CTRL+C to stop the server
echo.

npm run dev -- --host --port 5174
