@echo off
echo ========================================
echo  FORCE BACKEND RESTART - Clear Cache
echo ========================================
echo.

cd /d C:\workspace\affiliate-dashboard\backend

echo [1/5] Killing all Python processes on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)
echo Done!
echo.

echo [2/5] Clearing Python cache (__pycache__)...
for /d /r %%d in (__pycache__) do (
    if exist "%%d" (
        echo Deleting: %%d
        rd /s /q "%%d"
    )
)
echo Cache cleared!
echo.

echo [3/5] Deleting .pyc files...
del /s /q *.pyc 2>nul
echo Done!
echo.

echo [4/5] Activating venv...
call venv\Scripts\activate
echo.

echo [5/5] Starting backend with fresh code...
echo.
echo ========================================
echo  Backend will start on:
echo  http://127.0.0.1:8000
echo  Docs: http://127.0.0.1:8000/docs
echo ========================================
echo.

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
