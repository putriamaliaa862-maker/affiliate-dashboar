@echo off
echo ========================================
echo  QUICK START - FULL STACK
echo ========================================
echo.

cd /d C:\workspace\affiliate-dashboard

echo [1/3] Starting backend server...
start "Affiliate Dashboard - Backend" cmd /k "cd backend && venv\Scripts\activate && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

echo [2/3] Waiting for backend...
timeout /t 3 /nobreak >nul

echo [3/3] Starting frontend server...
start "Affiliate Dashboard - Frontend" cmd /k "cd frontend && npm run dev -- --host --port 5174"

echo.
echo Waiting for servers to start...
timeout /t 7 /nobreak >nul

echo.
echo Opening browser...
start http://localhost:5174/login

echo.
echo ========================================
echo  DONE!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5174
echo Docs: http://localhost:8000/docs
echo.
echo Two terminal windows opened:
echo - Backend (port 8000)
echo - Frontend (port 5174)
echo.
echo To stop: Close both terminal windows
echo.

pause
