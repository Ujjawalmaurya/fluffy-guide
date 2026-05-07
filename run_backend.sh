#!/bin/bash
echo "[SkillBridge AI] Starting backend server..."

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

if [ ! -f .env ]; then
    echo "[ERROR] .env file not found!"
    exit 1
fi

# Try to activate venv (different paths for Windows vs Unix-like shells)
if [ -f venv/bin/activate ]; then
    source venv/bin/activate
elif [ -f venv/Scripts/activate ]; then
    source venv/Scripts/activate
else
    echo "[ERROR] Virtual environment activation script not found!"
    exit 1
fi

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
