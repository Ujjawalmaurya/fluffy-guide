@echo off
REM Windows batch script to run the backend
echo [SkillBridge AI] Starting backend server...

cd /d %~dp0

if not exist .env (
    echo [ERROR] .env file not found!
    echo Please create one based on .env.example
    pause
    exit /b 1
)

if not exist venv (
    echo [ERROR] Virtual environment 'venv' not found!
    echo Please create it using: python -m venv venv
    pause
    exit /b 1
)

call venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause
