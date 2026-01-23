@echo off
setlocal
title System Restore In Progress

set "BACKUP_ZIP=%~1"
set "DEST_DIR=%~2"

if "%BACKUP_ZIP%"=="" (
    echo Error: No backup file specified.
    pause
    exit /b 1
)

if "%DEST_DIR%"=="" (
    echo Error: No destination directory specified.
    pause
    exit /b 1
)

echo ========================================================
echo        OFFICE TOOLS PORTAL - SYSTEM RESTORE
echo ========================================================
echo.
echo [1/5] Stopping Server...
taskkill /F /IM python.exe
timeout /t 3 /nobreak >nul

echo [2/5] Extracting Backup...
echo Source: %BACKUP_ZIP%
echo Destination: %DEST_DIR%
powershell -command "Expand-Archive -Path '%BACKUP_ZIP%' -DestinationPath '%DEST_DIR%' -Force"

echo [3/5] Restoring Database...
echo Please wait, this may take a moment...
set "DUMP_FILE=%DEST_DIR%\db_dump.sql"

if exist "%DUMP_FILE%" (
    rem Variables DB_USER, DB_NAME etc should be set by the caller environment
    "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U %DB_USER% -h %DB_HOST% -p %DB_PORT% %DB_NAME% < "%DUMP_FILE%"
    if errorlevel 1 (
        echo Warning: Database restore reported errors.
    ) else (
        echo Database restore completed.
    )
    del "%DUMP_FILE%"
) else (
    echo Warning: db_dump.sql not found in backup. Skipping DB restore.
)

echo [4/5] Running Migrations (Just in case)...
cd /d "%DEST_DIR%"
call venv\Scripts\activate
python manage.py migrate

echo [5/5] Restarting Server...
start "Office Tools Portal Server" cmd /c "Run_Server.bat"

echo.
echo ========================================================
echo        RESTORE COMPLETED SUCCESSFULLY
echo ========================================================
echo.
echo You may close this window.
timeout /t 10
exit
