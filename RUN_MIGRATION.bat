@echo off
echo ========================================
echo  DATABASE MIGRATION RUNNER
echo ========================================
echo.

cd /d C:\workspace\affiliate-dashboard\backend

echo [1/3] Checking Python environment...
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run START_BACKEND.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate
echo Virtual environment activated.
echo.

echo [2/3] Running database migration...
echo Adding access_code column to users table
echo.

python migrate_access_code.py

if errorlevel 1 (
    echo.
    echo ❌ ERROR: Migration failed!
    echo Check the output above for details.
    echo.
    pause
    exit /b 1
)

echo.
echo [3/3] Next steps:
echo 1. Restart backend: uvicorn app.main:app --reload --port 8000
echo 2. Test access code in Settings page
echo.
echo ========================================
echo  DONE!
echo ========================================
echo.

pause
