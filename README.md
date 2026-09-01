# SANKALP Backend

This is the backend server for **SANKALP (SkillBridge AI)**.  
It is built with **Python**, **FastAPI**, **Supabase (PostgreSQL)**, and **AI models (Ollama / SarvamAI / OpenAI)**.

It handles user login, skill assessment, resume checking, learning roadmaps, and job matching.

---

## 📋 What You Need First (Prerequisites)

Make sure you have installed on your computer:
- **Python 3.10+** (Python 3.11 recommended): [Download Python](https://www.python.org/downloads/)
- **pip** (Python package installer, comes with Python)
- **Supabase Account** (free cloud database): [supabase.com](https://supabase.com)
- *(Optional)* **Ollama** for running AI models locally on your PC: [ollama.com](https://ollama.com)

---

## 🚀 Quick Setup Guide (Step-by-Step)

### Step 1: Open the Backend Directory
Open your terminal and navigate to the `backend` folder:
```bash
cd backend
```

---

### Step 2: Create and Activate Virtual Environment
A virtual environment keeps your Python packages separate and clean.

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**On Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

*(You will see `(venv)` at the start of your terminal line when it is active.)*

---

### Step 3: Install Required Packages
Run this command to install all dependencies:
```bash
pip install -r requirements.txt
```

---

### Step 4: Configure Environment Variables (`.env`)
1. Make a copy of `.env.example` and name it `.env`:
   ```bash
   cp .env.example .env
   ```
   *(On Windows Command Prompt: `copy .env.example .env`)*

2. Open `.env` in your text editor and set your values:

| Variable | What it means | Example / Default |
|---|---|---|
| `SUPABASE_URL` | Your Supabase project URL | `https://xyzproject.supabase.co` |
| `SUPABASE_SERVICE_KEY` | Supabase **service_role** key (Secret key) | `eyJhbGciOi...` |
| `JWT_SECRET_KEY` | A secret password to sign user tokens (at least 32 characters) | `random-32-character-secret-key-here` |
| `ADMIN_SECRET` | Secret key for adding or editing jobs | `your-admin-secret-here` |
| `CORS_ORIGINS` | Allowed frontend URL | `http://localhost:5173` |
| `OLLAMA_HOST` | URL where local Ollama runs | `http://localhost:11434` |
| `SARVAM_API_KEY` | (Optional) SarvamAI API key | `your-sarvam-api-key` |

> ⚠️ **Important:** Use the **service_role** key for `SUPABASE_SERVICE_KEY`, NOT the public `anon` key.

---

### Step 5: Setup the Database in Supabase
1. Log in to [supabase.com](https://supabase.com) and open your project.
2. Click on **SQL Editor** on the left menu.
3. Click **New Query**.
4. Open the file [`supabase_schema.sql`](file:///home/um/Stuffs/SANKALP/backend/supabase_schema.sql) in this folder, copy all text, and paste it into the Supabase SQL editor.
5. Click **Run**. All necessary tables and security rules will be created.

---

### Step 6 (Optional): Start Ollama for Local AI
If you are using local AI models:
1. Open a new terminal window and run:
   ```bash
   ollama serve
   ```
2. In another terminal, download the two required models:
   ```bash
   ollama pull qwen3:4b
   ollama pull qwen2.5:1.5b
   ```

---

### Step 7: Start the Backend Server
Run this command in the backend folder:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or run the helper script:
- **Linux/Mac:** `./run_backend.sh`
- **Windows:** `run_backend.bat`

Your backend is now running at:
👉 **`http://localhost:8000`**

Interactive API documentation is available at:
👉 **`http://localhost:8000/docs`**

---

## 🔑 How Login (OTP) Works

1. SANKALP uses **passwordless OTP (One-Time Password)** login.
2. When you request a login code from the frontend, the 6-digit OTP code is **printed directly in your backend terminal console**.
3. Look at your running backend terminal, find the 6-digit number, and type it into the frontend.

---

## 📁 Backend Folder Structure

```
backend/
├── app/
│   ├── core/           # Configuration, database connection, logging, LLM settings
│   ├── modules/        # Feature modules (auth, profile, assessment, jobs, chat)
│   ├── schemas/        # Data validation schemas (Pydantic models)
│   ├── shared/         # Shared utilities, error handlers, dependencies
│   └── main.py         # Main entry point for FastAPI
├── routers/            # Additional API routes (e.g. resume analysis)
├── supabase_schema.sql # Database creation script
├── requirements.txt    # List of Python dependencies
├── .env.example        # Example configuration file
└── run_backend.sh      # Quick startup script for Linux/macOS
```

---

## ❓ Common Problems and Fixes

- **Error: `Supabase connection failed on startup`**
  - Check that `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` in `.env` are correct.
  - Make sure your computer is connected to the internet.

- **Error: `No module named 'fastapi'`**
  - Your virtual environment is not active. Run `source venv/bin/activate` (or Windows `venv\Scripts\activate`) and try again.

- **Error: `Address already in use (port 8000)`**
  - Another app is using port 8000. Stop that app or run uvicorn on another port with `--port 8001`.

- **Warning: `OLLAMA_NOT_RUNNING` on startup**
  - Ollama is not running in the background. Start it with `ollama serve`, or check if you have internet-based AI keys set in `.env`.
