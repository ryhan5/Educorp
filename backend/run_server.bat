@echo off
cd /d "%~dp0"
echo Starting EduCorp Backend...
".\venv\Scripts\python.exe" -m uvicorn app.main:app --reload --port 8000
pause
