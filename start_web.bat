@echo off
cd /d "%~dp0"
echo =========================================================
echo   Starting AI Job Search Web App
echo   Local URL: http://localhost:5000/ai-job-search
echo =========================================================
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe run_web.py
) else (
    python run_web.py
)
pause
