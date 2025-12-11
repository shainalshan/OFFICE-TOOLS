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
cd /d "c:\Users\Shalu\.gemini\antigravity\scratch\office_tools_portal"
call venv\Scripts\activate
python manage.py runserver 0.0.0.0:8000
pause
