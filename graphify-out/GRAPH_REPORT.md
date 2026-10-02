# Graph Report - backend  (2026-10-03)

## Corpus Check
- 149 files · ~35,050 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1032 nodes · 1969 edges · 69 communities (47 shown, 10 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 43 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f20ee575`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- jobs/router.py
- learning_resources/router.py
- onboarding/router.py
- profile/router.py
- JevProvider
- preflight.py
- resume_parser.py
- SkillProfileRepository
- suggester/service.py
- Settings
- exceptions.py
- GovernmentRepository
- ai_chat/service.py
- resume_analysis/router.py
- ResumeAnalysisRepository
- ok
- auth/router.py
- GeminiProvider
- auth/service.py
- dashboard/router.py
- logger.py
- dependencies.py
- TranslateService
- interview/router.py
- CareerIdentityService
- main.py
- demo/router.py
- StructuredProfile
- ILLMProvider
- Onboarding *(all require Bearer token)*
- .complete
- translate/router.py
- AuthRepository
- SimpleLogger
- InterviewService
- get_career_identity
- ai_chat/router.py
- related_skills.py
- get_supabase
- JobsRepository
- analytics/schemas.py
- JobsService
- SkillBridge AI (SANKALP) — Backend
- dashboard/schemas.py
- InterceptHandler
- onboarding/__init__.py
- run_backend.sh
- SkillBridge AI (SANKALP) — Backend
- Tables
- Endpoints
- AnalyticsRepository
- 3. Detailed Benchmark Findings
- Module Architecture
- roadmap_builder.py
- generate_otp
- rules/graphify.md
- workflows/graphify.md

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
- `Settings` --uses--> `AIModel`  [INFERRED]
  backend/app/core/config.py → backend/app/core/ai_models.py
- `ChatService` --uses--> `ILLMProvider`  [INFERRED]
  backend/app/modules/ai_chat/service.py → backend/app/modules/ai_chat/providers/base.py
- `detect_achievements()` --uses--> `ILLMProvider`  [INFERRED]
  backend/app/modules/profile/resume_parser.py → backend/app/modules/ai_chat/providers/base.py
- `extract_india_details()` --uses--> `ILLMProvider`  [INFERRED]
  backend/app/modules/profile/resume_parser.py → backend/app/modules/ai_chat/providers/base.py
- `parse_resume()` --uses--> `ILLMProvider`  [INFERRED]
  backend/app/modules/profile/resume_parser.py → backend/app/modules/ai_chat/providers/base.py

## Import Cycles
- None detected.

## Communities (69 total, 10 thin omitted)

### Community 0 - "jobs/router.py"
Cohesion: 0.21
Nodes (15): bulk_create(), create_job(), get_job(), list_jobs(), get, post, Jobs router — public listing + admin CRUD. Admin routes protected by X-Admin-…, JobCreate (+7 more)

### Community 1 - "learning_resources/router.py"
Cohesion: 0.15
Nodes (23): bulk_create(), create(), get_all_filtered(), get_by_id(), soft_delete(), update(), admin_bulk_upload(), admin_create() (+15 more)

### Community 2 - "onboarding/router.py"
Cohesion: 0.05
Nodes (40): build_system_prompt(), build_user_prompt(), generate_questions(), Question engine — builds SarvamAI prompt, parses returned JSON questions.…, Generate career assessment questions via local Ollama provider., Ensures semantic alignment between question text and answer input type., Sanitize a list of generated questions., sanitize_question() (+32 more)

### Community 3 - "profile/router.py"
Cohesion: 0.07
Nodes (35): ProfileRepository, Client, Stores or updates detailed multi-model analysis for a user., Fetches daily bullet rewrite count for a user., Increments the daily bullet rewrite count., Resets all bullet rewrite counts (for cron jobs)., get_completion(), get_profile() (+27 more)

### Community 4 - "JevProvider"
Cohesion: 0.11
Nodes (17): JevProvider, Any, Detects photo mentions, demographic disclosures, and formatting risks in…, Scores candidate assessment answer on a 1-5 competence scale (<0.01ms)., Scores mock interview answer on a 1-10 scale with feedback (<0.05ms)., Triage chat message for safety, intent classification, and emergency distress…, Evaluates candidate-job suitability in a single parallel decision pass…, Jev System One Decision Engine — high-speed non-autoregressive decision model.… (+9 more)

### Community 5 - "preflight.py"
Cohesion: 0.10
Nodes (32): extract_contact_info(), Any, contact_parser.py — Zero-hallucination contact information and profile link…, Extracts contact coordinates and URLs deterministically with zero hallucination., extract_indian_regulatory_flags(), Any, flags_parser.py — Indian regulatory flags, demographic bias detection, and…, Detects ATS compliance, cultural biases, and vocational credentials in Indian… (+24 more)

### Community 6 - "resume_parser.py"
Cohesion: 0.09
Nodes (28): detect_achievements(), extract_india_details(), _parse_json(), parse_resume(), Deterministic ATS scoring in <1ms without burning LLM calls., Deterministic Indian qualification and exam extraction in <0.1ms., Deterministic metric-bearing achievement isolation in <0.1ms., rewrite_bullets() (+20 more)

### Community 7 - "SkillProfileRepository"
Cohesion: 0.12
Nodes (21): _label_to_numeric(), merge_from_assessment(), merge_from_resume(), UUID, Merges skills extracted from completed assessment. Assessment proficiency is…, Convert a proficiency label string to a numeric 1-5 value., Merges Gemini-extracted resume skills into user_skill_profiles. Resolution…, Client (+13 more)

### Community 8 - "suggester/service.py"
Cohesion: 0.12
Nodes (20): prompts.py — AI synthesis prompts for resume analysis, bullet enhancement, and…, get_active_provider(), provider.py — Active LLM provider resolution for resume analysis. Prioritizes…, Returns high-speed Gemini Flash Lite provider when configured, or local Ollama…, SuggestionSet, Complete production-grade analyzer pipeline. Fail-safe operation: always…, batch_improve_bullets(), bullet_enhancer.py — Weak resume bullet point improvement via LLM with… (+12 more)

### Community 10 - "exceptions.py"
Cohesion: 0.08
Nodes (19): GroqProvider, AdminUnauthorized, AIProviderUnavailable, AIQuotaExceeded, AIRateLimit, AIResponseParseError, AppError, GapAnalysisNoJobs (+11 more)

### Community 11 - "GovernmentRepository"
Cohesion: 0.13
Nodes (11): GovernmentRepository, get_global_stats(), get_youth_list(), get, Returns global workforce statistics for government officers., Returns a list of youth profiles for monitoring., GovernmentService, Any (+3 more)

### Community 12 - "ai_chat/service.py"
Cohesion: 0.13
Nodes (16): find_matching_grounded_jobs(), Any, grounding.py — Deterministic retrieval pre-flight for grounded job matching.…, Retrieves verified active jobs matching user query and state., build_greeting(), build_system_prompt(), prompts.py — System prompt templates and generators for SkillBridge AI chat., Builds localized personalized system prompt from user profile and preferences. (+8 more)

### Community 13 - "resume_analysis/router.py"
Cohesion: 0.16
Nodes (16): resume_analysis module package., check_bullet_rate_limit(), increment_bullet_rate_limit(), rate_limiter.py — Rate limiting for LLM bullet improvement calls., Increments the daily bullet improvement count for the user., Checks and updates the daily rate limit for bullet improvements., repository.py — Database persistence and skill-sync operations for resume…, improve_single_bullet() (+8 more)

### Community 14 - "ResumeAnalysisRepository"
Cohesion: 0.11
Nodes (16): Any, Upserts full analysis result to the resume_analysis table., Returns the latest resume analysis record for a user., Returns score metrics and flags for quick dashboard viewing., Auto-syncs extracted skills to user_skill_profiles via skill aggregator., ResumeAnalysisRepository, analyze_resume(), get_latest_analysis() (+8 more)

### Community 15 - "ok"
Cohesion: 0.14
Nodes (16): export_csv(), get_funnel(), get_outcomes(), get_overview(), get_skill_gaps(), get, AnalyticsService, get_me() (+8 more)

### Community 16 - "auth/router.py"
Cohesion: 0.21
Nodes (17): Returns user_id from a valid refresh token, else None., verify_refresh_token(), _get_service(), post, Auth router — HTTP endpoints only. Parses request → calls service → returns…, refresh_tokens(), request_otp(), verify_otp() (+9 more)

### Community 17 - "GeminiProvider"
Cohesion: 0.13
Nodes (12): GeminiProvider, get_gemini_instance(), Internal helper to build model with specific name and instruction., Generate a response from Gemini, with automatic local Ollama fallback., Execute completion and parse JSON output, handling markdown fences and retrying…, Stream response from Gemini with local Ollama fallback., Check if Gemini or local Ollama is available., Returns a global singleton instance of GeminiProvider. (+4 more)

### Community 18 - "auth/service.py"
Cohesion: 0.15
Nodes (7): Backend config — reads all settings from .env via Pydantic BaseSettings. Single…, Auth service — OTP generation/verification, token issuance. Coordinates between…, EmailService, Sends an OTP email using Resend, or falls back to logger in dev/test., OTPExpired, OTPInvalid, Unauthorized

### Community 19 - "dashboard/router.py"
Cohesion: 0.14
Nodes (9): DashboardRepository, Client, Dashboard repository — joins across profile, preferences, questionnaire, and…, _get_service(), get_summary(), get, Dashboard router — GET /dashboard/summary., DashboardService (+1 more)

### Community 20 - "logger.py"
Cohesion: 0.15
Nodes (12): Supabase client singleton. One connection, shared across the app. Tested on…, get_logger(), Chat repository — all DB ops for chat_messages table., compute_gap(), GAP_ANALYSIS_NO_JOBS, GAP_ANALYSIS_NO_SKILLS, _proficiency_label(), Compares user's skill profile against job market requirements. Returns… (+4 more)

### Community 21 - "dependencies.py"
Cohesion: 0.13
Nodes (15): create_access_token(), create_refresh_token(), decode_token(), Security utilities — OTP generation, JWT create/verify. No password hashing…, Returns payload dict or None if invalid/expired., Returns user_id (sub) from a valid access token, else None., verify_access_token(), Verify OTP, upsert user, return JWT tokens + user data. (+7 more)

### Community 23 - "interview/router.py"
Cohesion: 0.11
Nodes (17): interview module package., get_interview_report(), get, post, router.py — FastAPI endpoints for AI mock interview sessions. Prefix: /interview, start_interview(), submit_answer(), AnswerRequest (+9 more)

### Community 24 - "CareerIdentityService"
Cohesion: 0.08
Nodes (19): AIModel, get_embedding_model(), Centralized AI model names to avoid hardcoded strings across the codebase., Returns a SentenceTransformer model for local embedding generation. Used for…, CareerIdentityService, Lazily load SentenceTransformer only when first needed., Synthesizes a professional persona using local Ollama model., Converts text to vector using Ollama nomic-embed-text with SentenceTransformer… (+11 more)

### Community 25 - "main.py"
Cohesion: 0.11
Nodes (16): Quick connectivity check — called at startup., test_connection(), health(), get, main.py — app factory. Mounts all routers, registers exception handlers, runs…, startup(), force_run(), post (+8 more)

### Community 26 - "demo/router.py"
Cohesion: 0.22
Nodes (10): personas.py — Pre-seeded demo user profiles for judging and evaluation., demo_login(), post, router.py — Pre-seeded demo login personas for hackathon judging. POST…, DemoLoginData, DemoLoginRequest, DemoLoginResponse, DemoUserResponse (+2 more)

### Community 27 - "StructuredProfile"
Cohesion: 0.32
Nodes (11): QualityScores, StructuredProfile, _calculate_ats_score(), _calculate_keyword_relevance(), calculate_quality_scores(), _calculate_quantification_score(), _calculate_readability_score(), _calculate_section_completeness() (+3 more)

### Community 28 - "ILLMProvider"
Cohesion: 0.12
Nodes (13): ABC, ILLMProvider, ILLMProvider — abstract interface for LLM providers. Interface Segregation:…, Return full response as a string., Yield response tokens one at a time., Quick health check — True if API is reachable., get_ollama_instance(), OllamaProvider (+5 more)

### Community 29 - "Onboarding *(all require Bearer token)*"
Cohesion: 0.07
Nodes (29): Admin (requires X-Admin-Secret header), API Reference, Auth, Chat *(requires Bearer token)*, Dashboard *(requires Bearer token)*, DELETE /chat/history, GET /auth/me *(requires Bearer token)*, GET /chat/history (+21 more)

### Community 31 - "translate/router.py"
Cohesion: 0.27
Nodes (8): post, router.py — Translation API endpoint. Prefix: /api/translate (mounted under…, Translates text using local Ollama model., translate_text(), BaseModel, schemas.py — Request and response models for translation service., TranslateRequest, TranslateResponse

### Community 32 - "AuthRepository"
Cohesion: 0.17
Nodes (3): AuthRepository, Client, Auth repository — all database queries for auth operations. No business logic…

### Community 34 - "InterviewService"
Cohesion: 0.18
Nodes (8): get_default_questions(), prompts.py — Prompts and fallback questions for mock interviews., Fallback questions when LLM is unavailable., InterviewService, Any, Generates comprehensive HR interview report., Initializes a new interview session and generates questions., Scores candidate answer and returns next question state.

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
Cohesion: 0.19
Nodes (14): get_supabase(), Client, compute_hash(), Produces a deterministic hash of the user's skill profile state. Hash inputs:…, get_by_user_id(), mark_stale(), upsert(), get_report() (+6 more)

### Community 39 - "JobsRepository"
Cohesion: 0.15
Nodes (4): JobsRepository, Client, Jobs repository — all DB ops for job_listings table., _get_service()

### Community 40 - "analytics/schemas.py"
Cohesion: 0.53
Nodes (5): AnalyticsOverview, DistrictFunnel, BaseModel, SkillGap, TrainingOutcome

### Community 41 - "JobsService"
Cohesion: 0.19
Nodes (6): delete_job(), delete, patch, update_job(), JobsService, JobNotFound

### Community 42 - "SkillBridge AI (SANKALP) — Backend"
Cohesion: 0.15
Nodes (12): Architecture, Engineering, Environment Variables, Getting Started, Installation, Key Modules, Prerequisites, Project (+4 more)

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

### Community 63 - "3. Detailed Benchmark Findings"
Cohesion: 0.22
Nodes (8): 1. Executive Summary, 2. Before vs After Performance Deltas, 3.1 PDF Extraction (Test Asset: 10-page Deck / 2.56 MB), 3.2 Chat Guardrail Triage (`typesafe-ai/jev`), 3.3 Job Match Scoring, 3.4 Question Flow Alignment, 3. Detailed Benchmark Findings, SANKALP Decision Engine & Extraction Benchmark Report

### Community 64 - "Module Architecture"
Cohesion: 0.25
Nodes (7): ai_chat, auth, dashboard, jobs, Module Architecture, onboarding, profile

### Community 65 - "roadmap_builder.py"
Cohesion: 0.40
Nodes (5): build_roadmap(), Fetches matching resources for top 5 gaps, then calls Gemini to generate a…, _strip_fences(), find_by_skill_tag(), Finds active resources where skill_tags contains the given tag. Uses PostgreSQL…

### Community 66 - "generate_otp"
Cohesion: 0.50
Nodes (3): generate_otp(), 6-digit numeric OTP as string (zero-padded)., Generate OTP, store it, send via email. Returns the OTP (for logging only).

## Knowledge Gaps
- **71 isolated node(s):** `run_backend.sh script`, `graphify`, `Workflow: graphify`, `TL;DR`, `Project` (+66 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 433 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GeminiProvider` connect `GeminiProvider` to `ILLMProvider`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `get_logger()` connect `logger.py` to `AuthRepository`, `roadmap_builder.py`, `jobs/router.py`, `learning_resources/router.py`, `ai_chat/router.py`, `onboarding/router.py`, `profile/router.py`, `JobsRepository`, `exceptions.py`, `ai_chat/service.py`, `auth/service.py`, `dashboard/router.py`, `dependencies.py`, `main.py`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Why does `get_supabase()` connect `get_supabase` to `roadmap_builder.py`, `learning_resources/router.py`, `profile/router.py`, `get_career_identity`, `GovernmentRepository`, `resume_analysis/router.py`, `logger.py`, `dependencies.py`, `CareerIdentityService`, `main.py`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `JevProvider` (e.g. with `ChatService` and `ProfileService`) actually correct?**
  _`JevProvider` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `run_backend.sh script`, `graphify`, `Workflow: graphify` to the rest of the system?**
  _71 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `onboarding/router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.053555750658472345 - nodes in this community are weakly interconnected._
- **Should `profile/router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0660377358490566 - nodes in this community are weakly interconnected._