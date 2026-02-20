@echo off
REM ============================================
REM MAC Quality Dashboard - Sync & Push Script
REM Runs email sync then pushes DB to GitHub
REM Scheduled to run every 3 days via Task Scheduler
REM ============================================

cd /d "%~dp0"

echo [%date% %time%] Starting sync... >> sync_log.txt

REM Run the email sync (headless mode)
set HEADLESS=true
"C:\Users\ajimenez\AppData\Local\Programs\Python\Python311\python.exe" main.py >> sync_log.txt 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo [%date% %time%] Sync FAILED with exit code %ERRORLEVEL% >> sync_log.txt
    exit /b 1
)

echo [%date% %time%] Sync completed, pushing to GitHub... >> sync_log.txt

REM Push complaints.db to the data branch
REM Create a temp directory for the data branch
set TMPDIR=%TEMP%\mac_data_push_%RANDOM%
mkdir "%TMPDIR%"

REM Clone just the data branch (or create it)
git clone --depth 1 --branch data https://github.com/Anthonyooo0/MAC_Quality_Dashboard.git "%TMPDIR%" 2>nul
if %ERRORLEVEL% NEQ 0 (
    REM Data branch doesn't exist yet, create it
    mkdir "%TMPDIR%"
    cd /d "%TMPDIR%"
    git init
    git remote add origin https://github.com/Anthonyooo0/MAC_Quality_Dashboard.git
    git checkout --orphan data
) else (
    cd /d "%TMPDIR%"
)

REM Copy the database file
copy /Y "%~dp0complaints.db" "%TMPDIR%\complaints.db" >nul

REM Commit and push
cd /d "%TMPDIR%"
git add complaints.db
git commit -m "Update complaints database %date% %time%" 2>nul
git push origin data --force >> "%~dp0sync_log.txt" 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo [%date% %time%] Git push FAILED >> "%~dp0sync_log.txt"
) else (
    echo [%date% %time%] Successfully pushed to GitHub data branch >> "%~dp0sync_log.txt"
)

REM Cleanup temp directory
cd /d "%~dp0"
rmdir /s /q "%TMPDIR%" 2>nul

echo [%date% %time%] Done. >> sync_log.txt
