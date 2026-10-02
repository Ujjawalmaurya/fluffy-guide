# Graph Report - backend  (2026-10-03)

## Corpus Check
- 145 files · ~33,947 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1006 nodes · 1943 edges · 77 communities (51 shown, 14 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 43 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b9825dba`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- jobs/router.py
- learning_resources/router.py
- onboarding/router.py
- profile/service.py
- JevProvider
- deterministic/__init__.py
- .__init__
- SkillProfileRepository
- OnboardingRepository
- Settings
- AppError
- GovernmentRepository
- .stream_message
- resume_analysis/schemas.py
- resume_analysis/router.py
- ResumeAnalysisRepository
- security.py
- GeminiProvider
- ai_models.py
- DashboardRepository
- logger.py
- ProfileRepository
- question_engine.py
- interview/service.py
- CareerIdentityService
- interview/router.py
- demo/router.py
- resume_analysis/service.py
- ai_chat/service.py
- Onboarding *(all require Bearer token)*
- .complete
- translate/router.py
- StructuredProfile
- SimpleLogger
- find_matching_grounded_jobs
- get_career_identity
- ai_chat/router.py
- related_skills.py
- get_supabase
- ok
- analytics/schemas.py
- exceptions.py
- profile/router.py
- dashboard/schemas.py
- InterceptHandler
- onboarding/__init__.py
- run_backend.sh
- SkillBridge AI (SANKALP) — Backend
- Tables
- Endpoints
- auth/router.py
- AuthRepository
- Module Architecture
- resume_parser.py
- AnalyticsRepository
- rules/graphify.md
- workflows/graphify.md
- session_store.py
- .upload_resume
- test_connection
- generate_otp
- government/repository.py
- TranslateService
- health
- government/__init__.py

## God Nodes (most connected - your core abstractions)
1. `get_supabase()` - 38 edges
2. `AppError` - 37 edges
3. `ok()` - 36 edges
4. `get_logger()` - 32 edges
5. `JevProvider` - 23 edges
6. `OnboardingRepository` - 23 edges
7. `Settings` - 21 edges
8. `ILLMProvider` - 21 edges
9. `StructuredProfile` - 21 edges
10. `ProfileService` - 18 edges

## Surprising Connections (you probably didn't know these)
- `benchmark_assessment_scoring()` --uses--> `JevProvider`  [INFERRED]
  scripts/benchmark_jev.py → app/modules/ai_chat/providers/jev_provider.py
- `benchmark_chat_triage()` --uses--> `JevProvider`  [INFERRED]
  scripts/benchmark_jev.py → app/modules/ai_chat/providers/jev_provider.py
- `benchmark_job_matching()` --uses--> `JevProvider`  [INFERRED]
  scripts/benchmark_jev.py → app/modules/ai_chat/providers/jev_provider.py
- `Settings` --uses--> `AIModel`  [INFERRED]
  app/core/config.py → app/core/ai_models.py
- `ChatService` --uses--> `ILLMProvider`  [INFERRED]
  app/modules/ai_chat/service.py → app/modules/ai_chat/providers/base.py

## Import Cycles
- None detected.

## Communities (77 total, 14 thin omitted)

### Community 0 - "jobs/router.py"
Cohesion: 0.08
Nodes (25): JobsRepository, Client, Jobs repository — all DB ops for job_listings table., bulk_create(), create_job(), delete_job(), get_job(), _get_service() (+17 more)

### Community 1 - "learning_resources/router.py"
Cohesion: 0.13
Nodes (25): force_run(), get_report(), get_roadmap(), get, post, Returns cached gap analysis report. Recomputes automatically if stale or…, Forces a fresh recompute regardless of cache state. Called when user clicks…, Returns only the roadmap portion of the current report. (+17 more)

### Community 2 - "onboarding/router.py"
Cohesion: 0.15
Nodes (21): generate_questions(), _get_service(), post, Onboarding router — HTTP layer only. Calls service for business logic, returns…, save_preferences(), save_profile(), set_user_type(), submit_answers() (+13 more)

### Community 3 - "profile/service.py"
Cohesion: 0.24
Nodes (13): Achievement, ATSBreakdown, ATSScoreOut, BulletRewriteOut, CompletionScoreOut, IndiaQualifications, ParsedResumeOut, ProfileOut (+5 more)

### Community 4 - "JevProvider"
Cohesion: 0.07
Nodes (35): JevProvider, Any, Detects photo mentions, demographic disclosures, and formatting risks in…, Scores candidate assessment answer on a 1-5 competence scale (<0.01ms)., Scores mock interview answer on a 1-10 scale with feedback (<0.05ms)., Triage chat message for safety, intent classification, and emergency distress…, Evaluates candidate-job suitability in a single parallel decision pass…, Jev System One Decision Engine — high-speed non-autoregressive decision model.… (+27 more)

### Community 5 - "deterministic/__init__.py"
Cohesion: 0.12
Nodes (18): extract_contact_info(), Any, contact_parser.py — Zero-hallucination contact information and profile link…, Extracts contact coordinates and URLs deterministically with zero hallucination., extract_indian_regulatory_flags(), Any, flags_parser.py — Indian regulatory flags, demographic bias detection, and…, Detects ATS compliance, cultural biases, and vocational credentials in Indian… (+10 more)

### Community 6 - ".__init__"
Cohesion: 0.09
Nodes (9): parse_resume(), AIProviderUnavailable, AIQuotaExceeded, AIRateLimit, GapAnalysisNoJobs, GeminiParseError, GroqFailed, ResumeGeminiFailed (+1 more)

### Community 7 - "SkillProfileRepository"
Cohesion: 0.11
Nodes (22): Auto-syncs extracted skills to user_skill_profiles via skill aggregator., _label_to_numeric(), merge_from_assessment(), merge_from_resume(), UUID, Merges skills extracted from completed assessment. Assessment proficiency is…, Convert a proficiency label string to a numeric 1-5 value., Merges Gemini-extracted resume skills into user_skill_profiles. Resolution… (+14 more)

### Community 8 - "OnboardingRepository"
Cohesion: 0.09
Nodes (11): OnboardingRepository, Client, get_state(), process_stream_endpoint(), get, _extract_skills_from_text(), process_stream(), SSE processor — streams real processing events after answer submission. Each… (+3 more)

### Community 10 - "AppError"
Cohesion: 0.10
Nodes (11): GroqProvider, GAP_ANALYSIS_NO_JOBS, GAP_ANALYSIS_NO_SKILLS, AdminUnauthorized, AIResponseParseError, AppError, GapAnalysisNoSkills, GroqRateLimit (+3 more)

### Community 11 - "GovernmentRepository"
Cohesion: 0.14
Nodes (10): GovernmentRepository, get_global_stats(), get_youth_list(), get, Returns global workforce statistics for government officers., Returns a list of youth profiles for monitoring., GovernmentService, Any (+2 more)

### Community 12 - ".stream_message"
Cohesion: 0.15
Nodes (11): build_greeting(), build_system_prompt(), prompts.py — System prompt templates and generators for SkillBridge AI chat., Builds localized personalized system prompt from user profile and preferences., Zero-LLM instant greeting for high performance (<2ms)., Semantic Multi-Provider Router: Prefer Gemini Flash if available; fallback to…, filter_thinking_stream(), merge_consecutive_roles() (+3 more)

### Community 13 - "resume_analysis/schemas.py"
Cohesion: 0.23
Nodes (16): build_deterministic_profile(), preflight.py — Zero-LLM preflight orchestrator and deterministic profile…, Builds a rich, valid StructuredProfile entirely from zero-LLM deterministic…, extract_structured_profile(), _parse_ai_education(), _parse_ai_experiences(), _parse_ai_trajectory(), any (+8 more)

### Community 14 - "resume_analysis/router.py"
Cohesion: 0.16
Nodes (14): resume_analysis module package., check_bullet_rate_limit(), increment_bullet_rate_limit(), rate_limiter.py — Rate limiting for LLM bullet improvement calls., Increments the daily bullet improvement count for the user., Checks and updates the daily rate limit for bullet improvements., analyze_resume(), improve_single_bullet() (+6 more)

### Community 15 - "ResumeAnalysisRepository"
Cohesion: 0.13
Nodes (12): Any, repository.py — Database persistence and skill-sync operations for resume…, Upserts full analysis result to the resume_analysis table., Returns the latest resume analysis record for a user., Returns score metrics and flags for quick dashboard viewing., ResumeAnalysisRepository, get_latest_analysis(), get_score_breakdown() (+4 more)

### Community 16 - "security.py"
Cohesion: 0.19
Nodes (11): create_access_token(), create_refresh_token(), decode_token(), Security utilities — OTP generation, JWT create/verify. No password hashing…, Returns payload dict or None if invalid/expired., Returns user_id from a valid refresh token, else None., verify_refresh_token(), Issue new token pair for valid refresh token. (+3 more)

### Community 17 - "GeminiProvider"
Cohesion: 0.12
Nodes (13): GeminiProvider, get_gemini_instance(), Internal helper to build model with specific name and instruction., Generate a response from Gemini, with automatic local Ollama fallback., Execute completion and parse JSON output, handling markdown fences and retrying…, Stream response from Gemini with local Ollama fallback., Check if Gemini or local Ollama is available., Returns a global singleton instance of GeminiProvider. (+5 more)

### Community 18 - "ai_models.py"
Cohesion: 0.29
Nodes (5): AIModel, get_embedding_model(), Centralized AI model names to avoid hardcoded strings across the codebase., Returns a SentenceTransformer model for local embedding generation. Used for…, Embeds all existing jobs that don't have embeddings.

### Community 19 - "DashboardRepository"
Cohesion: 0.15
Nodes (6): DashboardRepository, Client, _get_service(), get_summary(), get, DashboardService

### Community 20 - "logger.py"
Cohesion: 0.11
Nodes (21): Backend config — reads all settings from .env via Pydantic BaseSettings. Single…, Supabase client singleton. One connection, shared across the app. Tested on…, get_logger(), main.py — app factory. Mounts all routers, registers exception handlers, runs…, Chat repository — all DB ops for chat_messages table., Dashboard repository — joins across profile, preferences, questionnaire, and…, Dashboard router — GET /dashboard/summary., Dashboard service — aggregates data from multiple tables into a single summary. (+13 more)

### Community 21 - "ProfileRepository"
Cohesion: 0.12
Nodes (7): ProfileRepository, Client, Stores or updates detailed multi-model analysis for a user., Fetches daily bullet rewrite count for a user., Increments the daily bullet rewrite count., Resets all bullet rewrite counts (for cron jobs)., _get_service()

### Community 22 - "question_engine.py"
Cohesion: 0.25
Nodes (9): build_system_prompt(), build_user_prompt(), generate_questions(), Question engine — builds SarvamAI prompt, parses returned JSON questions.…, Generate career assessment questions via local Ollama provider., Ensures semantic alignment between question text and answer input type., Sanitize a list of generated questions., sanitize_question() (+1 more)

### Community 23 - "interview/service.py"
Cohesion: 0.17
Nodes (9): get_default_questions(), prompts.py — Prompts and fallback questions for mock interviews., Fallback questions when LLM is unavailable., InterviewService, Any, service.py — Mock interview question generation, response scoring, and…, Generates comprehensive HR interview report., Initializes a new interview session and generates questions. (+1 more)

### Community 24 - "CareerIdentityService"
Cohesion: 0.15
Nodes (11): CareerIdentityService, Lazily load SentenceTransformer only when first needed., Synthesizes a professional persona using local Ollama model., Converts text to vector using Ollama nomic-embed-text with SentenceTransformer…, Orchestrates generation, embedding, and saving to Supabase., Pulls skills + preferences from DB and updates user identity lazily., JobRecommendationService, Any (+3 more)

### Community 25 - "interview/router.py"
Cohesion: 0.14
Nodes (16): Returns user_id (sub) from a valid access token, else None., verify_access_token(), interview module package., get_interview_report(), get, post, router.py — FastAPI endpoints for AI mock interview sessions. Prefix: /interview, start_interview() (+8 more)

### Community 26 - "demo/router.py"
Cohesion: 0.22
Nodes (10): personas.py — Pre-seeded demo user profiles for judging and evaluation., demo_login(), post, router.py — Pre-seeded demo login personas for hackathon judging. POST…, DemoLoginData, DemoLoginRequest, DemoLoginResponse, DemoUserResponse (+2 more)

### Community 27 - "resume_analysis/service.py"
Cohesion: 0.22
Nodes (13): QualityScores, SuggestionSet, _calculate_ats_score(), _calculate_keyword_relevance(), calculate_quality_scores(), _calculate_quantification_score(), _calculate_readability_score(), _calculate_section_completeness() (+5 more)

### Community 28 - "ai_chat/service.py"
Cohesion: 0.13
Nodes (13): ABC, ILLMProvider, ILLMProvider — abstract interface for LLM providers. Interface Segregation:…, Return full response as a string., Yield response tokens one at a time., Quick health check — True if API is reachable., get_ollama_instance(), OllamaProvider (+5 more)

### Community 29 - "Onboarding *(all require Bearer token)*"
Cohesion: 0.07
Nodes (29): Admin (requires X-Admin-Secret header), API Reference, Auth, Chat *(requires Bearer token)*, Dashboard *(requires Bearer token)*, DELETE /chat/history, GET /auth/me *(requires Bearer token)*, GET /chat/history (+21 more)

### Community 31 - "translate/router.py"
Cohesion: 0.27
Nodes (8): post, router.py — Translation API endpoint. Prefix: /api/translate (mounted under…, Translates text using local Ollama model., translate_text(), BaseModel, schemas.py — Request and response models for translation service., TranslateRequest, TranslateResponse

### Community 32 - "StructuredProfile"
Cohesion: 0.16
Nodes (20): get_active_provider(), Returns high-speed Gemini Flash Lite provider when configured, or local Ollama…, BulletImprovement, StructuredProfile, batch_improve_bullets(), improve_bullet(), bullet_enhancer.py — Weak resume bullet point improvement via LLM with…, Uses active LLM provider (Ollama / Gemini fallback) to improve a single resume… (+12 more)

### Community 34 - "find_matching_grounded_jobs"
Cohesion: 0.40
Nodes (4): find_matching_grounded_jobs(), Any, grounding.py — Deterministic retrieval pre-flight for grounded job matching.…, Retrieves verified active jobs matching user query and state.

### Community 35 - "get_career_identity"
Cohesion: 0.25
Nodes (9): get_career_identity(), get_job_recommendations(), Any, get, post, Get personalized job recommendations for the current user. Uses AI-generated…, Force a re-generation of the user's career identity persona and embedding.…, Fetches the current user's AI-generated career persona. (+1 more)

### Community 36 - "ai_chat/router.py"
Cohesion: 0.11
Nodes (17): ChatRepository, Client, clear_history(), get_history(), _get_prefs(), _get_profile(), _get_service(), delete (+9 more)

### Community 37 - "related_skills.py"
Cohesion: 0.39
Nodes (7): _get_client(), get_related_skills(), BaseModel, post, related_skills.py — POST /api/skills/related Uses Groq Llama3 to suggest…, RelatedSkillsRequest, RelatedSkillsResponse

### Community 38 - "get_supabase"
Cohesion: 0.13
Nodes (23): get_supabase(), Client, compute_gap(), _proficiency_label(), Compares user's skill profile against job market requirements. Returns…, compute_hash(), Produces a deterministic hash of the user's skill profile state. Hash inputs:…, get_by_user_id() (+15 more)

### Community 39 - "ok"
Cohesion: 0.16
Nodes (15): export_csv(), get_funnel(), get_outcomes(), get_overview(), _get_service(), get_skill_gaps(), get, AnalyticsService (+7 more)

### Community 40 - "analytics/schemas.py"
Cohesion: 0.53
Nodes (5): AnalyticsOverview, DistrictFunnel, BaseModel, SkillGap, TrainingOutcome

### Community 41 - "exceptions.py"
Cohesion: 0.24
Nodes (11): EmailService, Sends an OTP email using Resend, or falls back to logger in dev/test., AuthService, Auth service — OTP generation/verification, token issuance. Coordinates between…, Verify OTP, upsert user, return JWT tokens + user data., OTPAlreadyUsed, OTPExpired, OTPInvalid (+3 more)

### Community 42 - "profile/router.py"
Cohesion: 0.17
Nodes (13): get_completion(), get_profile(), get, patch, post, UploadFile, Profile router — GET/PATCH /profile/me, POST /profile/resume, GET…, rewrite_bullets() (+5 more)

### Community 43 - "dashboard/schemas.py"
Cohesion: 0.67
Nodes (3): DashboardSummary, JobMatchOut, BaseModel

### Community 59 - "SkillBridge AI (SANKALP) — Backend"
Cohesion: 0.15
Nodes (12): Architecture, Engineering, Environment Variables, Getting Started, Installation, Key Modules, Prerequisites, Project (+4 more)

### Community 60 - "Tables"
Cohesion: 0.20
Nodes (9): Database Schema, ER Diagram (ASCII), job_listings, onboarding_state, otp_store, profile_enrichments, questionnaire_sessions, Tables (+1 more)

### Community 61 - "Endpoints"
Cohesion: 0.20
Nodes (9): Endpoints, `GET /api/v1/resume/analysis`, `GET /api/v1/resume/score-breakdown`, `POST /api/v1/resume/analyze`, `POST /api/v1/resume/improve-bullet`, Resume Analysis Module, Scoring Algorithm, Technical Stack (+1 more)

### Community 62 - "auth/router.py"
Cohesion: 0.23
Nodes (13): post, Auth router — HTTP endpoints only. Parses request → calls service → returns…, refresh_tokens(), request_otp(), verify_otp(), OTPRequest, OTPVerify, BaseModel (+5 more)

### Community 63 - "AuthRepository"
Cohesion: 0.17
Nodes (4): AuthRepository, Client, Auth repository — all database queries for auth operations. No business logic…, _get_service()

### Community 64 - "Module Architecture"
Cohesion: 0.25
Nodes (7): ai_chat, auth, dashboard, jobs, Module Architecture, onboarding, profile

### Community 65 - "resume_parser.py"
Cohesion: 0.25
Nodes (8): detect_achievements(), extract_india_details(), _parse_json(), Deterministic ATS scoring in <1ms without burning LLM calls., Deterministic Indian qualification and exam extraction in <0.1ms., Deterministic metric-bearing achievement isolation in <0.1ms., rewrite_bullets(), score_ats()

### Community 69 - "session_store.py"
Cohesion: 0.33
Nodes (3): InterviewSessionStore, Any, session_store.py — Thread-safe in-memory store for active mock interview…

### Community 71 - "test_connection"
Cohesion: 0.50
Nodes (4): Quick connectivity check — called at startup., test_connection(), startup(), on_event

### Community 72 - "generate_otp"
Cohesion: 0.50
Nodes (3): generate_otp(), 6-digit numeric OTP as string (zero-padded)., Generate OTP, store it, send via email. Returns the OTP (for logging only).

## Knowledge Gaps
- **55 isolated node(s):** `run_backend.sh script`, `graphify`, `Workflow: graphify`, `TL;DR`, `Project` (+50 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 413 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GeminiProvider` connect `GeminiProvider` to `ai_chat/service.py`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `get_supabase()` connect `get_supabase` to `profile/service.py`, `get_career_identity`, `.upload_resume`, `test_connection`, `government/repository.py`, `GovernmentRepository`, `ResumeAnalysisRepository`, `ai_models.py`, `logger.py`, `CareerIdentityService`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `ILLMProvider` connect `ai_chat/service.py` to `resume_parser.py`, `ai_chat/router.py`, `.__init__`, `AppError`, `.stream_message`, `GeminiProvider`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `JevProvider` (e.g. with `ChatService` and `ProfileService`) actually correct?**
  _`JevProvider` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `run_backend.sh script`, `graphify`, `Workflow: graphify` to the rest of the system?**
  _55 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `jobs/router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08456659619450317 - nodes in this community are weakly interconnected._
- **Should `learning_resources/router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1282051282051282 - nodes in this community are weakly interconnected._