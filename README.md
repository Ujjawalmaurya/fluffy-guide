# SkillBridge AI (SANKALP) — Backend

FastAPI backend powering the SANKALP AI career guidance and job matching platform.

---

## TL;DR

- **What**: Python 3.11 + FastAPI service powering career guidance, adaptive assessments, ATS resume parsing, and job matching.
- **Stack**: FastAPI, Pydantic v2, Uvicorn, Supabase (PostgreSQL), PyMuPDF / pdfplumber.
- **AI Orchestration**: Multi-provider fallback across Gemini, Groq, SarvamAI (Indian languages), and local Ollama models.
- **Key Features**: Passwordless OTP authentication, Server-Sent Events (SSE) streaming, asynchronous PDF ATS parsing, and macro workforce analytics.

---

## Project

- **Problem**: Job seekers lack structured evaluation, submit resumes that fail ATS filters, and struggle to find targeted training for local job vacancies.
- **Solution**: High-throughput REST API and streaming engine that processes conversational skill evaluations, scores PDF resumes against ATS rules, maps skill gaps to learning resources, and indexes localised employment openings.

---

## Architecture

- **FastAPI Core**: Async route handlers with dependency injection for authentication, database sessions, and provider management.
- **Supabase / PostgreSQL**: Relational schema with JSONB columns for flexible skill matrices, profile enrichments, and assessment logs.
- **AI Provider Layer**: Pluggable provider interface (`ILLMProvider`) supporting Gemini, Groq, SarvamAI (for Indic translations), and local LLMs with runtime fallback.
- **Document Processing Pipeline**: Multi-stage PDF extraction engine combining PyMuPDF, pdfplumber, and pytesseract OCR fallback.
- **Real-Time Streaming**: Native Server-Sent Events (`StreamingResponse`) emitting token-by-token question evaluation and onboarding pipeline state.

---

## Engineering

- **Passwordless Auth**: Time-limited 6-digit OTP verification issuing HS256-signed JWT access and refresh tokens. Zero plaintext passwords stored.
- **Adaptive Evaluation Engine**: Dynamic prompt sequencing that evaluates answer depth, adjusts question difficulty iteratively, and scores candidate capabilities across multiple competency phases.
- **Resilient ATS Parsing**: Heuristic and regex-driven section extraction that scores formatting, keyword relevance, and impact phrasing while extracting structured profile attributes.
- **Asynchronous Stream Management**: Event streaming pipeline (`sse_processor.py`) designed to handle dropped client connections gracefully and report pipeline progress without blocking worker threads.
- **Admin & Analytics Isolation**: Lightweight `X-Admin-Secret` header authorization for administrative job CRUD; SQL aggregation views for government workforce insights without heavyweight table locking.

---

## What I Learned

- **Streaming Stability**: Handling SSE streams through FastAPI requires cautious connection monitoring; unhandled client disconnects can leave background inference tasks running indefinitely.
- **Document Ingestion Reality**: Production resumes vary wildly in encoding and layout; a multi-tiered pipeline (PyMuPDF for speed, pdfplumber for tables, OCR fallback) is required for reliable text extraction.
- **Provider Decoupling**: Abstracting LLM vendors behind a unified provider protocol enables zero-downtime swaps during third-party API rate limits or latency spikes.

---

## Getting Started

### Prerequisites

- Python 3.11+
- pip 23+
- Supabase account with schema applied

### Installation

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API Base: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### Environment Variables

| Variable | Description |
|---|---|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Supabase `service_role` secret key |
| `JWT_SECRET_KEY` | 32+ character random secret for HS256 JWT tokens |
| `ADMIN_SECRET` | Header secret for administrative CRUD (`X-Admin-Secret`) |
| `SARVAM_API_KEY` | SarvamAI API key for Indian language translation |
| `GROQ_API_KEY` | Groq Cloud API key for low-latency LLM inference |
| `GEMINI_API_KEY` | Google Gemini API key for assessment reasoning |
| `CORS_ORIGINS` | Comma-separated frontend origins (default: `http://localhost:5173`) |

---

## Key Modules

| Module | Route Prefix | Responsibility |
|---|---|---|
| `auth` | `/api/v1/auth` | OTP creation, verification, and JWT issuance |
| `onboarding` | `/api/v1/onboarding` | 5-step wizard and SSE AI streaming pipeline |
| `profile` | `/api/v1/profile` | Candidate profile CRUD and resume attachment |
| `resume_analysis` | `/api/v1/resume` | ATS scoring, bullet suggestions, and extraction |
| `assessment` | `/api/v1/assessment` | Adaptive conversational skill evaluation |
| `gap_analysis` | `/api/v1/gap-analysis` | Skill deficit calculation and weekly roadmaps |
| `jobs` | `/api/v1/jobs` | Job listings, skill-matched search, and admin CRUD |
| `interview` | `/api/v1/interview` | AI mock interview session simulator |
| `government` | `/api/v1/government` | Workforce analytics and district placement metrics |
