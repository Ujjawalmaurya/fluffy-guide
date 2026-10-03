# Graph Report - backend  (2026-10-03)

## Corpus Check
- 181 files · ~56,573 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1302 nodes · 2519 edges · 90 communities (67 shown, 10 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 104 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `60fd04bf`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- jobs/router.py
- AuthRepository
- onboarding/router.py
- llm_extractor.py
- resume_parser.py
- resume_analysis/schemas.py
- logger.py
- SkillProfileRepository
- JevProvider
- Settings
- BaseSchema
- GovernmentRepository
- .stream_message
- enums.py
- email_service.py
- ResumeAnalysisRepository
- ai_models.py
- learning_resources/router.py
- ok
- Region
- find_matching_grounded_jobs
- ProfileRepository
- test_connection
- interview/service.py
- .update_user_identity
- interview/schemas.py
- demo/router.py
- StructuredProfile
- .complete
- Onboarding *(all require Bearer token)*
- ai_chat/service.py
- translate/router.py
- suggester/service.py
- SimpleLogger
- profile/schemas.py
- ChatService
- ai_chat/router.py
- related_skills.py
- get_supabase
- schemas/base.py
- analytics/schemas.py
- exceptions.py
- question_engine.py
- dashboard/schemas.py
- InterceptHandler
- onboarding/__init__.py
- run_backend.sh
- SkillBridge AI (SANKALP) — Backend
- Tables
- Endpoints
- auth/router.py
- gap_engine.py
- Module Architecture
- response/assessment.py
- JobType
- rules/graphify.md
- workflows/graphify.md
- OnboardingRepository
- llm_inputs.py
- main.py
- context.py
- recommendations/router.py
- request/auth.py
- career_path.py
- profile/service.py
- AppError
- skill_profile.py
- response/user.py
- .verify_otp
- JobsRepository
- session_store.py
- start_ollama.sh
- career.py
- response/auth.py
- llm_config.py
- llm_json_utils.py
- .empty_strings_to_none

## God Nodes (most connected - your core abstractions)
1. `BaseSchema` - 125 edges
2. `get_supabase()` - 38 edges
3. `AppError` - 37 edges
4. `ok()` - 36 edges
5. `get_logger()` - 32 edges
6. `CaseInsensitiveEnum` - 31 edges
7. `JevProvider` - 23 edges
8. `OnboardingRepository` - 23 edges
9. `Settings` - 21 edges
10. `ILLMProvider` - 21 edges

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

## Communities (90 total, 10 thin omitted)

### Community 0 - "jobs/router.py"
Cohesion: 0.13
Nodes (22): bulk_create(), create_job(), delete_job(), get_job(), _get_service(), list_jobs(), delete, get (+14 more)

### Community 2 - "onboarding/router.py"
Cohesion: 0.16
Nodes (22): generate_questions(), _get_service(), get_state(), post, Onboarding router — HTTP layer only. Calls service for business logic, returns…, save_preferences(), save_profile(), set_user_type() (+14 more)

### Community 3 - "llm_extractor.py"
Cohesion: 0.27
Nodes (8): extract_structured_profile(), _parse_ai_education(), _parse_ai_experiences(), _parse_ai_trajectory(), any, llm_extractor.py — Scoped LLM resume synthesis and schema merger. Merges…, High-performance resume extraction pipeline. Phase 1: Deterministic Pre-Flight…, prompts.py — AI synthesis prompts for resume analysis, bullet enhancement, and…

### Community 4 - "resume_parser.py"
Cohesion: 0.25
Nodes (8): detect_achievements(), extract_india_details(), _parse_json(), Deterministic ATS scoring in <1ms without burning LLM calls., Deterministic Indian qualification and exam extraction in <0.1ms., Deterministic metric-bearing achievement isolation in <0.1ms., rewrite_bullets(), score_ats()

### Community 5 - "resume_analysis/schemas.py"
Cohesion: 0.11
Nodes (27): extract_contact_info(), Any, contact_parser.py — Zero-hallucination contact information and profile link…, Extracts contact coordinates and URLs deterministically with zero hallucination., extract_indian_regulatory_flags(), Any, flags_parser.py — Indian regulatory flags, demographic bias detection, and…, Detects ATS compliance, cultural biases, and vocational credentials in Indian… (+19 more)

### Community 6 - "logger.py"
Cohesion: 0.15
Nodes (11): Supabase client singleton. One connection, shared across the app. Tested on…, get_logger(), Chat repository — all DB ops for chat_messages table., Auth repository — all database queries for auth operations. No business logic…, Auth service — OTP generation/verification, token issuance. Coordinates between…, Dashboard repository — joins across profile, preferences, questionnaire, and…, Dashboard service — aggregates data from multiple tables into a single summary., Jobs repository — all DB ops for job_listings table. (+3 more)

### Community 7 - "SkillProfileRepository"
Cohesion: 0.06
Nodes (27): DashboardRepository, Client, _get_service(), DashboardService, JobRecommendationEngine, _label_to_numeric(), merge_from_assessment(), merge_from_resume() (+19 more)

### Community 8 - "JevProvider"
Cohesion: 0.07
Nodes (35): JevProvider, Any, Detects photo mentions, demographic disclosures, and formatting risks in…, Scores candidate assessment answer on a 1-5 competence scale (<0.01ms)., Scores mock interview answer on a 1-10 scale with feedback (<0.05ms)., Triage chat message for safety, intent classification, and emergency distress…, Evaluates candidate-job suitability in a single parallel decision pass…, Jev System One Decision Engine — high-speed non-autoregressive decision model.… (+27 more)

### Community 10 - "BaseSchema"
Cohesion: 0.06
Nodes (44): BaseSchema, BaseModel, Base schema for all SkillBridge AI models. Enforces strict whitespace…, Helper to extend base config without losing settings., AssessmentBatchLLMOutput, AssessmentQuestionLLMOutput, CareerGuidanceLLMOutput, LLM Output Schemas Parsed and validated models from LLM responses. (+36 more)

### Community 11 - "GovernmentRepository"
Cohesion: 0.13
Nodes (11): GovernmentRepository, get_global_stats(), get_youth_list(), get, Returns global workforce statistics for government officers., Returns a list of youth profiles for monitoring., GovernmentService, Any (+3 more)

### Community 12 - ".stream_message"
Cohesion: 0.15
Nodes (11): build_greeting(), build_system_prompt(), prompts.py — System prompt templates and generators for SkillBridge AI chat., Builds localized personalized system prompt from user profile and preferences., Zero-LLM instant greeting for high performance (<2ms)., Semantic Multi-Provider Router: Prefer Gemini Flash if available; fallback to…, filter_thinking_stream(), merge_consecutive_roles() (+3 more)

### Community 13 - "enums.py"
Cohesion: 0.12
Nodes (33): AssessmentType, CareerStage, CaseInsensitiveEnum, CompanySize, DigitalLiteracy, EducationStream, ExperienceRange, GovtAccessLevel (+25 more)

### Community 14 - "email_service.py"
Cohesion: 0.24
Nodes (5): EmailService, Sends an OTP email using Resend, or falls back to logger in dev/test., build_otp_email(), email_templates.py — Clean, responsive email templates for SANKALP auth., Returns (subject, html_content, text_content) for an OTP verification email.…

### Community 15 - "ResumeAnalysisRepository"
Cohesion: 0.09
Nodes (19): Any, Upserts full analysis result to the resume_analysis table., Returns the latest resume analysis record for a user., Returns score metrics and flags for quick dashboard viewing., Auto-syncs extracted skills to user_skill_profiles via skill aggregator., ResumeAnalysisRepository, analyze_resume(), get_latest_analysis() (+11 more)

### Community 16 - "ai_models.py"
Cohesion: 0.29
Nodes (5): AIModel, get_embedding_model(), Centralized AI model names to avoid hardcoded strings across the codebase., Returns a SentenceTransformer model for local embedding generation. Used for…, Embeds all existing jobs that don't have embeddings.

### Community 17 - "learning_resources/router.py"
Cohesion: 0.06
Nodes (38): GeminiProvider, get_gemini_instance(), Internal helper to build model with specific name and instruction., Generate a response from Gemini, with automatic local Ollama fallback., Execute completion and parse JSON output, handling markdown fences and retrying…, Stream response from Gemini with local Ollama fallback., Check if Gemini or local Ollama is available., Returns a global singleton instance of GeminiProvider. (+30 more)

### Community 18 - "ok"
Cohesion: 0.10
Nodes (20): AnalyticsRepository, export_csv(), get_funnel(), get_outcomes(), get_overview(), _get_service(), get_skill_gaps(), get (+12 more)

### Community 19 - "Region"
Cohesion: 0.09
Nodes (29): EducationLevel, Gender, Language, Gender identification., Region, ProfileRequest, StudentOnboardingRequest, ProfileUpdateRequest (+21 more)

### Community 20 - "find_matching_grounded_jobs"
Cohesion: 0.40
Nodes (4): find_matching_grounded_jobs(), Any, grounding.py — Deterministic retrieval pre-flight for grounded job matching.…, Retrieves verified active jobs matching user query and state.

### Community 21 - "ProfileRepository"
Cohesion: 0.13
Nodes (7): ProfileRepository, Client, Stores or updates detailed multi-model analysis for a user., Fetches daily bullet rewrite count for a user., Increments the daily bullet rewrite count., Resets all bullet rewrite counts (for cron jobs)., _get_service()

### Community 22 - "test_connection"
Cohesion: 0.50
Nodes (4): Quick connectivity check — called at startup., test_connection(), startup(), on_event

### Community 23 - "interview/service.py"
Cohesion: 0.17
Nodes (9): get_default_questions(), prompts.py — Prompts and fallback questions for mock interviews., Fallback questions when LLM is unavailable., InterviewService, Any, service.py — Mock interview question generation, response scoring, and…, Generates comprehensive HR interview report., Initializes a new interview session and generates questions. (+1 more)

### Community 24 - ".update_user_identity"
Cohesion: 0.20
Nodes (5): Lazily load SentenceTransformer only when first needed., Synthesizes a professional persona using local Ollama model., Converts text to vector using Ollama nomic-embed-text with SentenceTransformer…, Orchestrates generation, embedding, and saving to Supabase., Pulls skills + preferences from DB and updates user identity lazily.

### Community 25 - "interview/schemas.py"
Cohesion: 0.25
Nodes (8): AnswerRequest, post, start_interview(), submit_answer(), AnswerRequest, BaseModel, schemas.py — Request and response models for mock interviews., StartRequest

### Community 26 - "demo/router.py"
Cohesion: 0.13
Nodes (16): create_access_token(), create_refresh_token(), Issue new token pair for valid refresh token., personas.py — Pre-seeded demo user profiles for judging and evaluation., demo_login(), post, router.py — Pre-seeded demo login personas for hackathon judging. POST…, DemoLoginData (+8 more)

### Community 27 - "StructuredProfile"
Cohesion: 0.27
Nodes (12): repository.py — Database persistence and skill-sync operations for resume…, QualityScores, StructuredProfile, _calculate_ats_score(), _calculate_keyword_relevance(), calculate_quality_scores(), _calculate_quantification_score(), _calculate_readability_score() (+4 more)

### Community 29 - "Onboarding *(all require Bearer token)*"
Cohesion: 0.07
Nodes (29): Admin (requires X-Admin-Secret header), API Reference, Auth, Chat *(requires Bearer token)*, Dashboard *(requires Bearer token)*, DELETE /chat/history, GET /auth/me *(requires Bearer token)*, GET /chat/history (+21 more)

### Community 30 - "ai_chat/service.py"
Cohesion: 0.14
Nodes (12): ABC, ILLMProvider, ILLMProvider — abstract interface for LLM providers. Interface Segregation:…, Return full response as a string., Yield response tokens one at a time., Quick health check — True if API is reachable., get_ollama_instance(), OllamaProvider (+4 more)

### Community 31 - "translate/router.py"
Cohesion: 0.16
Nodes (11): post, router.py — Translation API endpoint. Prefix: /api/translate (mounted under…, Translates text using local Ollama model., translate_text(), BaseModel, schemas.py — Request and response models for translation service., TranslateRequest, TranslateResponse (+3 more)

### Community 32 - "suggester/service.py"
Cohesion: 0.14
Nodes (20): get_active_provider(), provider.py — Active LLM provider resolution for resume analysis. Prioritizes…, Returns high-speed Gemini Flash Lite provider when configured, or local Ollama…, BulletImprovement, batch_improve_bullets(), improve_bullet(), bullet_enhancer.py — Weak resume bullet point improvement via LLM with…, Uses active LLM provider (Ollama / Gemini fallback) to improve a single resume… (+12 more)

### Community 34 - "profile/schemas.py"
Cohesion: 0.22
Nodes (14): post, rewrite_bullets(), Achievement, ATSBreakdown, ATSScoreOut, BulletRewriteIn, CompletionScoreOut, IndiaQualifications (+6 more)

### Community 35 - "ChatService"
Cohesion: 0.22
Nodes (4): ChatRepository, Client, _get_service(), ChatService

### Community 36 - "ai_chat/router.py"
Cohesion: 0.13
Nodes (16): clear_history(), get_history(), _get_prefs(), _get_profile(), delete, get, post, AI chat router — SSE streaming response, history, and clear. (+8 more)

### Community 37 - "related_skills.py"
Cohesion: 0.39
Nodes (7): _get_client(), get_related_skills(), BaseModel, post, related_skills.py — POST /api/skills/related Uses Groq Llama3 to suggest…, RelatedSkillsRequest, RelatedSkillsResponse

### Community 38 - "get_supabase"
Cohesion: 0.14
Nodes (20): get_supabase(), Client, compute_hash(), Produces a deterministic hash of the user's skill profile state. Hash inputs:…, get_by_user_id(), mark_stale(), upsert(), build_roadmap() (+12 more)

### Community 39 - "schemas/base.py"
Cohesion: 0.08
Nodes (19): SkillBridge AI — Base Schema Common Pydantic configuration for all models., ChatRequest, AI Chat Request Schemas Handles messages sent to the AI assistant., Request message for AI chat., Resume Request Schemas Handles resume analysis and improvement requests., Raw resume text analysis request., Resume improvement request based on target job., ResumeAnalysisRequest (+11 more)

### Community 40 - "analytics/schemas.py"
Cohesion: 0.53
Nodes (5): AnalyticsOverview, DistrictFunnel, BaseModel, SkillGap, TrainingOutcome

### Community 41 - "exceptions.py"
Cohesion: 0.10
Nodes (13): parse_resume(), AIQuotaExceeded, AIRateLimit, GapAnalysisNoJobs, GapAnalysisNoSkills, GeminiParseError, GroqFailed, GroqRateLimit (+5 more)

### Community 42 - "question_engine.py"
Cohesion: 0.17
Nodes (11): build_system_prompt(), build_user_prompt(), generate_questions(), Question engine — builds SarvamAI prompt, parses returned JSON questions.…, Generate career assessment questions via local Ollama provider., Ensures semantic alignment between question text and answer input type., Sanitize a list of generated questions., sanitize_question() (+3 more)

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
Cohesion: 0.13
Nodes (23): generate_otp(), 6-digit numeric OTP as string (zero-padded)., Returns user_id from a valid refresh token, else None., verify_refresh_token(), get_me(), _get_service(), get, post (+15 more)

### Community 63 - "gap_engine.py"
Cohesion: 0.36
Nodes (5): compute_gap(), GAP_ANALYSIS_NO_JOBS, GAP_ANALYSIS_NO_SKILLS, _proficiency_label(), Compares user's skill profile against job market requirements. Returns…

### Community 64 - "Module Architecture"
Cohesion: 0.25
Nodes (7): ai_chat, auth, dashboard, jobs, Module Architecture, onboarding, profile

### Community 65 - "response/assessment.py"
Cohesion: 0.10
Nodes (19): AnswerResponse, AssessmentBatchResponse, AssessmentHistoryItem, AssessmentResultResponse, AssessmentStatusResponse, ImprovementArea, LatestAssessmentResponse, QuestionResponse (+11 more)

### Community 66 - "JobType"
Cohesion: 0.16
Nodes (17): JobType, WorkMode, JobCreateRequest, JobFilterRequest, JobMatchRequest, JobSearchRequest, JobUpdateRequest, Job Request Schemas Handles job creation, searching, and matching. (+9 more)

### Community 69 - "OnboardingRepository"
Cohesion: 0.08
Nodes (9): OnboardingRepository, Client, process_stream_endpoint(), get, _extract_skills_from_text(), process_stream(), Keyword match against common workforce skills plus comma-separated token…, Stream SSE events. Each step does real work. (+1 more)

### Community 70 - "llm_inputs.py"
Cohesion: 0.13
Nodes (10): CareerGuidanceLLMInput, MockInterviewLLMInput, LLM Input Schemas Lean, prompt-ready models for LLM calls., Context for career guidance prompts., Converts model to a clean string for prompts., Context for resume analysis prompts., Context for mock interview prompts., Context for roadmap generation prompts. (+2 more)

### Community 71 - "main.py"
Cohesion: 0.07
Nodes (36): Backend config — reads all settings from .env via Pydantic BaseSettings. Single…, decode_token(), Security utilities — OTP generation, JWT create/verify. No password hashing…, Returns payload dict or None if invalid/expired., Returns user_id (sub) from a valid access token, else None., verify_access_token(), health(), get (+28 more)

### Community 72 - "context.py"
Cohesion: 0.42
Nodes (10): BaseContext, BlueCollarContext, build_context_json(), Any, Main entry point to build the context JSON for the LLM. 'data' is the…, EmployerContext, GovtOfficerContext, InformalWorkerContext (+2 more)

### Community 73 - "recommendations/router.py"
Cohesion: 0.13
Nodes (18): CareerIdentityService, career_identity.py — Synthesizes user career identity persona and vector…, get_career_identity(), get_job_recommendations(), Any, get, post, router.py — Personalized job recommendations and career identity endpoints.… (+10 more)

### Community 74 - "request/auth.py"
Cohesion: 0.20
Nodes (9): OTPRequest, OTPVerifyRequest, Authentication Request Schemas Handles login, registration, and session…, Request a one-time password., Initial signup with role selection., Verify OTP and get tokens., Request new access token using refresh token., SignupRequest (+1 more)

### Community 75 - "career_path.py"
Cohesion: 0.20
Nodes (9): CareerPathResponse, Career Path Response Schemas Recommendations and week-by-week roadmaps., Specific role recommendation., List of recommended career paths., Weekly step in a learning roadmap., Complete week-by-week roadmap., RecommendedRole, RoadmapResponse (+1 more)

### Community 76 - "profile/service.py"
Cohesion: 0.20
Nodes (6): BulletRewriteOut, ProfileService, Profile service — CRUD, resume parsing, profile completion scoring., RateLimitExceeded, ResumeInvalid, ResumeTooLarge

### Community 77 - "AppError"
Cohesion: 0.21
Nodes (5): GroqProvider, AdminUnauthorized, AppError, Base for all application-level errors., Exception

### Community 78 - "skill_profile.py"
Cohesion: 0.25
Nodes (7): Skill Profile Response Schemas Detailed skill sets, proficiencies, and…, A single skill entry., Full skill profile for a user., High-level summary of a user's skills., SkillItemResponse, SkillProfileResponse, SkillSummaryResponse

### Community 79 - "response/user.py"
Cohesion: 0.25
Nodes (7): DashboardLocationSchema, DashboardUserSchema, User Response Schemas Safe public fields and dashboard summaries., Public profile information., Dashboard summary for the user., UserDashboardResponse, UserProfileResponse

### Community 80 - ".verify_otp"
Cohesion: 0.20
Nodes (5): Verify OTP, upsert user, return JWT tokens + user data., OTPAlreadyUsed, OTPExpired, OTPInvalid, OTPNotFound

### Community 82 - "session_store.py"
Cohesion: 0.33
Nodes (3): InterviewSessionStore, Any, session_store.py — Thread-safe in-memory store for active mock interview…

### Community 86 - "start_ollama.sh"
Cohesion: 0.29
Nodes (6): OLLAMA_DEBUG, OLLAMA_KEEP_ALIVE, OLLAMA_MAX_LOADED_MODELS, OLLAMA_NUM_PARALLEL, OLLAMA_VULKAN, start_ollama.sh script

### Community 88 - "career.py"
Cohesion: 0.33
Nodes (5): CareerGuidanceRequest, Career Request Schemas Handles career guidance and roadmap generation., Request for AI career guidance., Request for a week-by-week learning roadmap., RoadmapRequest

### Community 89 - "response/auth.py"
Cohesion: 0.33
Nodes (5): Authentication Response Schemas Safe public fields and session tokens., Access and refresh tokens., User info returned after authentication., TokenResponse, UserAuthResponse

### Community 90 - "llm_config.py"
Cohesion: 0.40
Nodes (4): _detect_use_rtx_4050(), SkillBridge AI — LLM Configuration Hardware-profile aware: supports RTX 4050…, Returns True for RTX 4050 Mobile (6GB VRAM), False for GTX 1050 Mobile (4GB…, TaskConfig

### Community 92 - "llm_json_utils.py"
Cohesion: 0.40
Nodes (4): clean_and_extract_json_text(), parse_healed_json(), Parses JSON with healing strategies for common LLM syntax errors., Cleans response text, finds JSON boundaries, and attempts to close open…

### Community 95 - ".empty_strings_to_none"
Cohesion: 0.50
Nodes (3): Any, Globally convert empty strings or whitespace-only strings to None., model_validator

## Knowledge Gaps
- **62 isolated node(s):** `TaskConfig`, `run_backend.sh script`, `start_ollama.sh script`, `OLLAMA_DEBUG`, `OLLAMA_MAX_LOADED_MODELS` (+57 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 536 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `JevProvider` connect `JevProvider` to `recommendations/router.py`, `ChatService`, `profile/service.py`, `ai_chat/service.py`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Why does `get_supabase()` connect `get_supabase` to `logger.py`, `main.py`, `recommendations/router.py`, `GovernmentRepository`, `profile/service.py`, `ResumeAnalysisRepository`, `ai_models.py`, `learning_resources/router.py`, `test_connection`, `.update_user_identity`, `StructuredProfile`, `gap_engine.py`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `get_logger()` connect `logger.py` to `jobs/router.py`, `onboarding/router.py`, `ai_chat/router.py`, `get_supabase`, `main.py`, `recommendations/router.py`, `question_engine.py`, `exceptions.py`, `profile/service.py`, `email_service.py`, `learning_resources/router.py`, `ai_chat/service.py`, `gap_engine.py`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **What connects `TaskConfig`, `run_backend.sh script`, `start_ollama.sh script` to the rest of the system?**
  _62 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `jobs/router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12701612903225806 - nodes in this community are weakly interconnected._
- **Should `resume_analysis/schemas.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1140819964349376 - nodes in this community are weakly interconnected._
- **Should `logger.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14855072463768115 - nodes in this community are weakly interconnected._