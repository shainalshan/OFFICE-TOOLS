@echo off
title Office Tools Portal Server
echo ========================================================
echo  OFFICE TOOLS PORTAL SERVER LAUNCHER
echo ========================================================
echo.
echo  COMMAND USED TO START: python manage.py runserver
echo  (This script runs it automatically for you below)
echo.
echo  HOW TO STOP THE SERVER: Press CTRL+C (then Y if asked)
echo.
echo ========================================================
echo.
echo Starting Office Tools Portal...
cd /d "%~dp0"
call venv\Scripts\activate
set DB_USER=postgres
set DB_PASSWORD=postgres
echo Access this on other devices using: http://[YOUR-IP]:7777
python manage.py runserver 0.0.0.0:7777
pause
