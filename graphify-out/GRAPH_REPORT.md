# Graph Report - backend  (2026-10-03)

## Corpus Check
- 144 files · ~35,216 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1007 nodes · 1927 edges · 69 communities (50 shown, 7 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 38 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c09c7ddb`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- jobs/router.py
- learning_resources/router.py
- onboarding/router.py
- profile/schemas.py
- resume_parser.py
- deterministic/__init__.py
- .__init__
- SkillProfileRepository
- JevProvider
- Settings
- AppError
- government/router.py
- ai_chat/service.py
- resume_analysis/schemas.py
- resume_analysis/router.py
- ResumeAnalysisRepository
- demo/service.py
- GeminiProvider
- config.py
- dashboard/router.py
- logger.py
- ProfileRepository
- question_engine.py
- InterviewService
- CareerIdentityService
- interview/router.py
- demo/schemas.py
- resume_analysis/service.py
- get_ollama_instance
- Onboarding *(all require Bearer token)*
- ILLMProvider
- translate/router.py
- StructuredProfile
- SimpleLogger
- Any
- get_career_identity
- ai_chat/router.py
- related_skills.py
- get_supabase
- analytics/router.py
- analytics/schemas.py
- .verify_otp
- ok
- dashboard/schemas.py
- InterceptHandler
- onboarding/__init__.py
- run_backend.sh
- SkillBridge AI (SANKALP) — Backend
- Tables
- Endpoints
- auth/router.py
- roadmap_builder.py
- Module Architecture
- rules/graphify.md
- workflows/graphify.md
- profile/service.py
- exceptions.py

## God Nodes (most connected - your core abstractions)
1. `get_supabase()` - 38 edges
2. `AppError` - 37 edges
3. `ok()` - 36 edges
4. `get_logger()` - 30 edges
5. `JevProvider` - 23 edges
6. `OnboardingRepository` - 23 edges
7. `ILLMProvider` - 21 edges
8. `StructuredProfile` - 21 edges
9. `Settings` - 21 edges
10. `ProfileService` - 18 edges

## Surprising Connections (you probably didn't know these)
- `benchmark_assessment_scoring()` --uses--> `JevProvider`  [INFERRED]
  scripts/benchmark_jev.py → app/modules/ai_chat/providers/jev_provider.py
- `benchmark_chat_triage()` --uses--> `JevProvider`  [INFERRED]
  scripts/benchmark_jev.py → app/modules/ai_chat/providers/jev_provider.py
- `benchmark_job_matching()` --uses--> `JevProvider`  [INFERRED]
  scripts/benchmark_jev.py → app/modules/ai_chat/providers/jev_provider.py
- `benchmark_pdf_extraction()` --calls--> `extract_resume_bundle()`  [EXTRACTED]
  scripts/benchmark_jev.py → app/modules/resume_analysis/pdf/service.py
- `Settings` --uses--> `AIModel`  [INFERRED]
  app/core/config.py → app/core/ai_models.py

## Import Cycles
- None detected.

## Communities (69 total, 7 thin omitted)

### Community 0 - "jobs/router.py"
Cohesion: 0.09
Nodes (25): JobsRepository, Client, Jobs repository — all DB ops for job_listings table., bulk_create(), create_job(), delete_job(), get_job(), _get_service() (+17 more)

### Community 1 - "learning_resources/router.py"
Cohesion: 0.11
Nodes (30): get_gemini_instance(), Returns a global singleton instance of GeminiProvider., force_run(), get_report(), get_roadmap(), get, post, Returns cached gap analysis report. Recomputes automatically if stale or… (+22 more)

### Community 2 - "onboarding/router.py"
Cohesion: 0.07
Nodes (33): OnboardingRepository, Client, Onboarding repository — all DB queries for onboarding tables. Handles: users,…, generate_questions(), _get_service(), get_state(), process_stream_endpoint(), get (+25 more)

### Community 3 - "profile/schemas.py"
Cohesion: 0.27
Nodes (12): Achievement, ATSBreakdown, ATSScoreOut, BulletRewriteIn, BulletRewriteOut, CompletionScoreOut, IndiaQualifications, ParsedResumeOut (+4 more)

### Community 4 - "resume_parser.py"
Cohesion: 0.09
Nodes (29): detect_achievements(), extract_india_details(), _parse_json(), parse_resume(), Deterministic ATS scoring in <1ms without burning LLM calls., Deterministic Indian qualification and exam extraction in <0.1ms., Deterministic metric-bearing achievement isolation in <0.1ms., rewrite_bullets() (+21 more)

### Community 5 - "deterministic/__init__.py"
Cohesion: 0.12
Nodes (18): extract_contact_info(), Any, contact_parser.py — Zero-hallucination contact information and profile link…, Extracts contact coordinates and URLs deterministically with zero hallucination., extract_indian_regulatory_flags(), Any, flags_parser.py — Indian regulatory flags, demographic bias detection, and…, Detects ATS compliance, cultural biases, and vocational credentials in Indian… (+10 more)

### Community 6 - ".__init__"
Cohesion: 0.11
Nodes (6): AdminUnauthorized, AIQuotaExceeded, AIRateLimit, GapAnalysisNoJobs, GapAnalysisNoSkills, GroqFailed

### Community 7 - "SkillProfileRepository"
Cohesion: 0.12
Nodes (21): _label_to_numeric(), merge_from_assessment(), merge_from_resume(), UUID, Merges skills extracted from completed assessment. Assessment proficiency is…, Convert a proficiency label string to a numeric 1-5 value., Merges Gemini-extracted resume skills into user_skill_profiles. Resolution…, Client (+13 more)

### Community 8 - "JevProvider"
Cohesion: 0.18
Nodes (12): JevProvider, Scores candidate assessment answer on a 1-5 competence scale (<0.01ms)., Jev System One Decision Engine — high-speed non-autoregressive decision model.…, benchmark_assessment_scoring(), benchmark_chat_triage(), benchmark_job_matching(), benchmark_pdf_extraction(), Benchmark PDF extraction latency and character volume. (+4 more)

### Community 10 - "AppError"
Cohesion: 0.12
Nodes (9): GroqProvider, GAP_ANALYSIS_NO_JOBS, GAP_ANALYSIS_NO_SKILLS, AppError, GroqRateLimit, Base for all application-level errors., ResumeGeminiFailed, TokenExpired (+1 more)

### Community 11 - "government/router.py"
Cohesion: 0.09
Nodes (18): government module package., GovernmentRepository, repository.py — Database operations for government monitoring and workforce…, get_global_stats(), get_youth_list(), get, router.py — Government officer portal endpoints. Prefix: /government (mounted…, Returns global workforce statistics for government officers. (+10 more)

### Community 12 - "ai_chat/service.py"
Cohesion: 0.13
Nodes (16): find_matching_grounded_jobs(), Any, grounding.py — Deterministic retrieval pre-flight for grounded job matching.…, Retrieves verified active jobs matching user query and state., build_greeting(), build_system_prompt(), prompts.py — System prompt templates and generators for SkillBridge AI chat., Builds localized personalized system prompt from user profile and preferences. (+8 more)

### Community 13 - "resume_analysis/schemas.py"
Cohesion: 0.23
Nodes (16): build_deterministic_profile(), preflight.py — Zero-LLM preflight orchestrator and deterministic profile…, Builds a rich, valid StructuredProfile entirely from zero-LLM deterministic…, extract_structured_profile(), _parse_ai_education(), _parse_ai_experiences(), _parse_ai_trajectory(), any (+8 more)

### Community 14 - "resume_analysis/router.py"
Cohesion: 0.16
Nodes (14): resume_analysis module package., check_bullet_rate_limit(), increment_bullet_rate_limit(), rate_limiter.py — Rate limiting for LLM bullet improvement calls., Increments the daily bullet improvement count for the user., Checks and updates the daily rate limit for bullet improvements., analyze_resume(), improve_single_bullet() (+6 more)

### Community 15 - "ResumeAnalysisRepository"
Cohesion: 0.13
Nodes (11): Any, Upserts full analysis result to the resume_analysis table., Returns the latest resume analysis record for a user., Returns score metrics and flags for quick dashboard viewing., Auto-syncs extracted skills to user_skill_profiles via skill aggregator., ResumeAnalysisRepository, get_latest_analysis(), get_score_breakdown() (+3 more)

### Community 16 - "demo/service.py"
Cohesion: 0.20
Nodes (8): create_access_token(), create_refresh_token(), Issue new token pair for valid refresh token., personas.py — Pre-seeded demo user profiles for judging and evaluation., DemoService, Any, service.py — Demo login token generator and persona manager., Unauthorized

### Community 17 - "GeminiProvider"
Cohesion: 0.15
Nodes (10): GeminiProvider, Internal helper to build model with specific name and instruction., Generate a response from Gemini, with automatic local Ollama fallback., Execute completion and parse JSON output, handling markdown fences and retrying…, Stream response from Gemini with local Ollama fallback., Check if Gemini or local Ollama is available., Local RPM limiter to prevent hitting API limits., Seamless fallback to local Ollama instance when Gemini fails or hits quota. (+2 more)

### Community 18 - "config.py"
Cohesion: 0.25
Nodes (6): AIModel, get_embedding_model(), Centralized AI model names to avoid hardcoded strings across the codebase., Returns a SentenceTransformer model for local embedding generation. Used for…, Backend config — reads all settings from .env via Pydantic BaseSettings. Single…, Embeds all existing jobs that don't have embeddings.

### Community 19 - "dashboard/router.py"
Cohesion: 0.16
Nodes (7): DashboardRepository, Client, _get_service(), get_summary(), get, Dashboard router — GET /dashboard/summary., DashboardService

### Community 20 - "logger.py"
Cohesion: 0.14
Nodes (15): Supabase client singleton. One connection, shared across the app. Tested on…, get_logger(), decode_token(), Security utilities — OTP generation, JWT create/verify. No password hashing…, Returns payload dict or None if invalid/expired., Returns user_id (sub) from a valid access token, else None., verify_access_token(), Chat repository — all DB ops for chat_messages table. (+7 more)

### Community 21 - "ProfileRepository"
Cohesion: 0.12
Nodes (7): ProfileRepository, Client, Stores or updates detailed multi-model analysis for a user., Fetches daily bullet rewrite count for a user., Increments the daily bullet rewrite count., Resets all bullet rewrite counts (for cron jobs)., _get_service()

### Community 22 - "question_engine.py"
Cohesion: 0.17
Nodes (11): build_system_prompt(), build_user_prompt(), generate_questions(), Question engine — builds SarvamAI prompt, parses returned JSON questions.…, Generate career assessment questions via local Ollama provider., Ensures semantic alignment between question text and answer input type., Sanitize a list of generated questions., sanitize_question() (+3 more)

### Community 23 - "InterviewService"
Cohesion: 0.18
Nodes (8): get_default_questions(), prompts.py — Prompts and fallback questions for mock interviews., Fallback questions when LLM is unavailable., InterviewService, Any, Generates comprehensive HR interview report., Initializes a new interview session and generates questions., Scores candidate answer and returns next question state.

### Community 24 - "CareerIdentityService"
Cohesion: 0.15
Nodes (11): CareerIdentityService, Lazily load SentenceTransformer only when first needed., Synthesizes a professional persona using local Ollama model., Converts text to vector using Ollama nomic-embed-text with SentenceTransformer…, Orchestrates generation, embedding, and saving to Supabase., Pulls skills + preferences from DB and updates user identity lazily., JobRecommendationService, Any (+3 more)

### Community 25 - "interview/router.py"
Cohesion: 0.11
Nodes (17): interview module package., get_interview_report(), get, post, router.py — FastAPI endpoints for AI mock interview sessions. Prefix: /interview, start_interview(), submit_answer(), AnswerRequest (+9 more)

### Community 26 - "demo/schemas.py"
Cohesion: 0.31
Nodes (8): demo_login(), post, DemoLoginData, DemoLoginRequest, DemoLoginResponse, DemoUserResponse, BaseModel, schemas.py — Request and response models for demo authentication.

### Community 27 - "resume_analysis/service.py"
Cohesion: 0.19
Nodes (14): repository.py — Database persistence and skill-sync operations for resume…, QualityScores, ResumeAnalysisResult, _calculate_ats_score(), _calculate_keyword_relevance(), calculate_quality_scores(), _calculate_quantification_score(), _calculate_readability_score() (+6 more)

### Community 28 - "get_ollama_instance"
Cohesion: 0.12
Nodes (11): get_ollama_instance(), OllamaProvider, High-performance local LLM provider powered by Ollama. Supports high context…, Check if local Ollama daemon is reachable., Execute non-streaming completion with high context window., Execute completion and parse JSON output, handling markdown fences and retrying…, Yield response tokens one at a time for fast SSE streaming., service.py — Mock interview question generation, response scoring, and… (+3 more)

### Community 29 - "Onboarding *(all require Bearer token)*"
Cohesion: 0.07
Nodes (29): Admin (requires X-Admin-Secret header), API Reference, Auth, Chat *(requires Bearer token)*, Dashboard *(requires Bearer token)*, DELETE /chat/history, GET /auth/me *(requires Bearer token)*, GET /chat/history (+21 more)

### Community 30 - "ILLMProvider"
Cohesion: 0.21
Nodes (6): ABC, ILLMProvider, ILLMProvider — abstract interface for LLM providers. Interface Segregation:…, Return full response as a string., Yield response tokens one at a time., Quick health check — True if API is reachable.

### Community 31 - "translate/router.py"
Cohesion: 0.27
Nodes (8): post, router.py — Translation API endpoint. Prefix: /api/translate (mounted under…, Translates text using local Ollama model., translate_text(), BaseModel, schemas.py — Request and response models for translation service., TranslateRequest, TranslateResponse

### Community 32 - "StructuredProfile"
Cohesion: 0.15
Nodes (22): get_active_provider(), provider.py — Active LLM provider resolution for resume analysis. Prioritizes…, Returns high-speed Gemini Flash Lite provider when configured, or local Ollama…, BulletImprovement, StructuredProfile, SuggestionSet, batch_improve_bullets(), improve_bullet() (+14 more)

### Community 34 - "Any"
Cohesion: 0.22
Nodes (5): Any, Detects photo mentions, demographic disclosures, and formatting risks in…, Scores mock interview answer on a 1-10 scale with feedback (<0.05ms)., Triage chat message for safety, intent classification, and emergency distress…, Evaluates candidate-job suitability in a single parallel decision pass…

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
Cohesion: 0.14
Nodes (22): get_supabase(), Client, Quick connectivity check — called at startup., test_connection(), compute_gap(), _proficiency_label(), Compares user's skill profile against job market requirements. Returns…, compute_hash() (+14 more)

### Community 39 - "analytics/router.py"
Cohesion: 0.16
Nodes (9): AnalyticsRepository, export_csv(), get_funnel(), get_outcomes(), get_overview(), _get_service(), get_skill_gaps(), get (+1 more)

### Community 40 - "analytics/schemas.py"
Cohesion: 0.53
Nodes (5): AnalyticsOverview, DistrictFunnel, BaseModel, SkillGap, TrainingOutcome

### Community 41 - ".verify_otp"
Cohesion: 0.20
Nodes (5): Verify OTP, upsert user, return JWT tokens + user data., OTPAlreadyUsed, OTPExpired, OTPInvalid, OTPNotFound

### Community 42 - "ok"
Cohesion: 0.22
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
Cohesion: 0.07
Nodes (29): generate_otp(), 6-digit numeric OTP as string (zero-padded)., Returns user_id from a valid refresh token, else None., verify_refresh_token(), EmailService, Sends an OTP email using Resend, or falls back to logger in dev/test., AuthRepository, Client (+21 more)

### Community 63 - "roadmap_builder.py"
Cohesion: 0.67
Nodes (3): build_roadmap(), Fetches matching resources for top 5 gaps, then calls Gemini to generate a…, _strip_fences()

### Community 64 - "Module Architecture"
Cohesion: 0.25
Nodes (7): ai_chat, auth, dashboard, jobs, Module Architecture, onboarding, profile

### Community 70 - "profile/service.py"
Cohesion: 0.29
Nodes (5): ProfileService, Profile service — CRUD, resume parsing, profile completion scoring., RateLimitExceeded, ResumeInvalid, ResumeTooLarge

### Community 71 - "exceptions.py"
Cohesion: 0.23
Nodes (9): health(), get, main.py — app factory. Mounts all routers, registers exception handlers, runs…, startup(), router.py — Pre-seeded demo login personas for hackathon judging. POST…, Custom exception classes and global exception handlers. All errors use the…, register_exception_handlers(), FastAPI (+1 more)

## Knowledge Gaps
- **55 isolated node(s):** `Admin (requires X-Admin-Secret header)`, `DELETE /chat/history`, `GET /auth/me *(requires Bearer token)*`, `GET /chat/history`, `GET /dashboard/summary` (+50 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 414 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_supabase()` connect `get_supabase` to `get_career_identity`, `profile/service.py`, `government/router.py`, `ResumeAnalysisRepository`, `config.py`, `logger.py`, `CareerIdentityService`, `resume_analysis/service.py`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `get_logger()` connect `logger.py` to `jobs/router.py`, `learning_resources/router.py`, `onboarding/router.py`, `ai_chat/router.py`, `get_supabase`, `exceptions.py`, `profile/service.py`, `government/router.py`, `ai_chat/service.py`, `question_engine.py`, `auth/router.py`, `roadmap_builder.py`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `get_ollama_instance()` connect `get_ollama_instance` to `StructuredProfile`, `ai_chat/router.py`, `profile/service.py`, `ai_chat/service.py`, `question_engine.py`, `InterviewService`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `JevProvider` (e.g. with `ChatService` and `ProfileService`) actually correct?**
  _`JevProvider` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Admin (requires X-Admin-Secret header)`, `DELETE /chat/history`, `GET /auth/me *(requires Bearer token)*` to the rest of the system?**
  _55 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `jobs/router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08748615725359911 - nodes in this community are weakly interconnected._
- **Should `learning_resources/router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1051693404634581 - nodes in this community are weakly interconnected._