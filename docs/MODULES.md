# Module Architecture

## auth
OTP-based login flow. No passwords — ever. Generates 6-digit OTP, prints to terminal, stores with 10-min TTL. Verifies → upserts user → issues JWT (30min access + 7-day refresh).

## onboarding
5-step wizard: user_type → profile → preferences → AI questions → submit answers. Saves progress in `onboarding_state` table so users can resume. Calls SarvamAI to generate 6 personalized questions. After submit, opens SSE stream for real processing.

## profile
CRUD on `user_profiles`. Resume upload via pdfplumber — extracts text, matches against 150-skill keyword list, stores structured JSON in `profile_enrichments`. Completion score calculated from filled fields.

## dashboard
Aggregation endpoint. Joins user + profile + preferences + latest questionnaire session → builds a single response object with job matches for the user's state.

## jobs
Job listings with state/category/type filters. Admin routes protected by `X-Admin-Secret` header — no separate admin user table. Bulk insert accepts JSON array.

## ai_chat
ILLMProvider interface (base.py) → SarvamAIProvider (sarvam.py). Service injected with provider — swap to MockLLMProvider for testing with zero code changes. Context window: last 10 messages. System prompt varies by language (EN/HI) and user type.
