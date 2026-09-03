# SANKALP Backend

FastAPI backend for SANKALP. It handles login, skill tests, resume checks, gap analysis, and job matching.

---

## Requirements

- Python 3.11 or newer
- pip
- Supabase account
- Ollama (optional, for local AI models)

---

## Installation

### 1. Set Up Virtual Environment

Move to the `backend` folder:

```bash
cd backend
```

Create and activate a virtual environment:

- **Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

- **Windows (Command Prompt):**
  ```cmd
  python -m venv venv
  venv\Scripts\activate
  ```

- **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  venv\Scripts\Activate.ps1
  ```

### 2. Install Packages

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Copy the sample file:

```bash
cp .env.example .env
```

Open `.env` and set your values:

| Variable | Required | Description | Example |
|---|---|---|---|
| `SUPABASE_URL` | Yes | Supabase project URL | `https://xyzproject.supabase.co` |
| `SUPABASE_SERVICE_KEY` | Yes | Supabase `service_role` secret key. Do not use the `anon` key. | `eyJhbGciOi...` |
| `JWT_SECRET_KEY` | Yes | Secret key with at least 32 characters to sign tokens | `random-32-char-secret-key-string` |
| `ADMIN_SECRET` | Yes | Header secret to manage jobs | `your-admin-secret-key` |
| `CORS_ORIGINS` | Yes | Allowed frontend URL | `http://localhost:5173` |
| `OLLAMA_HOST` | No | Base URL for local Ollama service | `http://localhost:11434` |
| `SARVAM_API_KEY` | No | API key for SarvamAI models | `your-sarvam-key` |

### 4. Set Up the Database

1. Open your project on [supabase.com](https://supabase.com).
2. Go to the **SQL Editor** tab.
3. Open [backend/supabase_schema.sql](file:///home/um/Stuffs/SANKALP/backend/supabase_schema.sql).
4. Copy the SQL text. Paste it into the editor.
5. Click **Run**.

---

## Running the Server

Start the server with Uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API Base URL: `http://localhost:8000`
- Swagger UI docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Helper scripts:
- Linux / macOS: `./run_backend.sh`
- Windows: `run_backend.bat`

---

## Local AI Setup (Optional)

You can run AI models locally with Ollama.

1. Start Ollama:
   ```bash
   ollama serve
   ```
2. Pull the required models:
   ```bash
   ollama pull qwen3:4b
   ollama pull qwen2.5:1.5b
   ```

If Ollama is not running, the system uses cloud providers configured in `.env`.

---

## Login Flow

1. The client requests a login code at `POST /auth/request-otp`.
2. The server creates a 6-digit code. The code expires in 10 minutes.
3. The server prints the code to the terminal in local mode.
4. The client sends the code to `POST /auth/verify-otp`.
5. The server checks the code. It returns access and refresh tokens.

---

## Project Structure

```
backend/
├── app/
│   ├── core/           # Database, settings, logging, and AI provider setup
│   ├── modules/        # Domain features (auth, profile, assessment, jobs, chat)
│   ├── schemas/        # Pydantic validation schemas
│   ├── shared/         # Utilities, security helpers, and custom errors
│   └── main.py         # FastAPI application entry point
├── routers/            # Additional route modules
├── supabase_schema.sql # Database schema script
├── migration_002.sql   # Data seed script
├── job_listings_data.sql # Job postings seed script
├── requirements.txt    # Python package list
├── .env.example        # Environment variables template
└── run_backend.sh      # Startup script for Unix systems
```

---

## Troubleshooting

- **Supabase connection fails:**
  - Check `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` in `.env`.
  - Make sure your computer can reach the internet.
- **Missing packages:**
  - Activate your virtual environment first.
  - Run `pip install -r requirements.txt`.
- **Port 8000 in use:**
  - Stop the process using port 8000.
  - Or start uvicorn with `--port 8001`.
- **OLLAMA_NOT_RUNNING warning:**
  - Start Ollama with `ollama serve`.
  - Or add cloud AI keys to `.env`.
