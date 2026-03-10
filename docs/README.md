# Backend Setup

## Requirements
- Python 3.11+
- pip 23+

## Setup

```bash
# 1. Copy env file
cp .env.example .env
# Fill in the values — see variable descriptions below

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up Supabase
# - Create a project at supabase.com
# - Go to Database → SQL Editor → New Query
# - Paste the entire contents of supabase_schema.sql
# - Run it

# 4. Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## .env Variables

| Variable | Description |
|---|---|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_SERVICE_KEY` | *service_role* key (NOT anon key) |
| `JWT_SECRET_KEY` | Random secret, min 32 chars |
| `SARVAM_API_KEY` | SarvamAI API key from api.sarvam.ai |
| `ADMIN_SECRET` | Any string — sent as X-Admin-Secret header |
| `CORS_ORIGINS` | Frontend URL (default: http://localhost:5173) |

## Logs

- Console: colored, real-time
- File: `logs/skillbridge.log` (auto-created, rotates at 10MB, retained 7 days)

## OTP

OTPs are **printed to the terminal**. Check server console after requesting a login.
