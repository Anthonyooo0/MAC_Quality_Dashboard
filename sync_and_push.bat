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

REM Always push to GitHub regardless of sync exit code
REM (Gemini timeouts cause non-zero exit but data is still processed)
echo [%date% %time%] Sync completed, pushing to GitHub... >> sync_log.txt

"C:\Users\ajimenez\AppData\Local\Programs\Python\Python311\python.exe" push_db.py >> sync_log.txt 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo [%date% %time%] Push FAILED >> sync_log.txt
) else (
    echo [%date% %time%] Successfully pushed to GitHub data branch >> sync_log.txt
)

echo [%date% %time%] Done. >> sync_log.txt
