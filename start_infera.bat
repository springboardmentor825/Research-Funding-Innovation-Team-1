@echo off
title Infera Launcher
echo ============================================
echo   Infera - starting all services
echo ============================================

echo [1/3] Starting MySQL (port 3307)...
start "Infera MySQL" /min "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe" --defaults-file=Z:\Infy\.mysql-dev\my.ini

:waitmysql
ping -n 3 127.0.0.1 >nul
netstat -an | findstr :3307 | findstr LISTENING >nul
if errorlevel 1 goto waitmysql
echo       MySQL is up.

echo [2/3] Starting Backend API (port 8000)...
start "Infera Backend" /min cmd /c "cd /d Z:\Infy\backend && .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

echo [3/3] Starting Frontend (port 5173)...
start "Infera Frontend" /min cmd /c "cd /d Z:\Infy\frontend && npm run dev"

echo.
echo Waiting for services to come online...
ping -n 12 127.0.0.1 >nul

echo ============================================
echo   Infera is live:
echo     Website  : http://localhost:5173
echo     API docs : http://127.0.0.1:8000/docs
echo     Login    : demo@research.org / DemoPass123!
echo ============================================
start http://localhost:5173
