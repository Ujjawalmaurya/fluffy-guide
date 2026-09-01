# Backend Documentation

> For the main setup instructions, see the [Backend README](file:///home/um/Stuffs/SANKALP/backend/README.md).

## Requirements
- Python 3.10+ (Python 3.11 recommended)
- pip
- Supabase account

## Quick Setup

```bash
# 1. Copy env file
cp .env.example .env

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install packages
pip install -r requirements.txt

# 4. Set up database in Supabase
# - Open supabase.com -> SQL Editor -> New Query
# - Paste contents of supabase_schema.sql and click Run

# 5. Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables (`.env`)

| Variable | Description |
|---|---|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Supabase `service_role` secret key (not anon key) |
| `JWT_SECRET_KEY` | Secret key for signing tokens (min 32 characters) |
| `ADMIN_SECRET` | Secret password for job administration API |
| `CORS_ORIGINS` | Frontend URL (`http://localhost:5173`) |
| `OLLAMA_HOST` | Local Ollama address (`http://localhost:11434`) |
| `SARVAM_API_KEY` | SarvamAI API key for Indian language support |

## Logs
- Terminal Console: Live colored log messages
- File: `logs/skillbridge.log` (auto-rotates at 10MB)

## Login OTP
The 6-digit login code is printed directly in the **backend terminal window**.
