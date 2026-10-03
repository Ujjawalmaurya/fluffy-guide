# Graph Report - backend  (2026-10-03)

## Corpus Check
- 180 files · ~56,193 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1298 nodes · 2513 edges · 91 communities (68 shown, 10 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 104 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `00ddc5b5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- jobs/router.py
- learning_resources/router.py
- onboarding/router.py
- resume_analysis/schemas.py
- resume_parser.py
- deterministic/__init__.py
- JevProvider
- SkillProfileRepository
- pdf/service.py
- Settings
- BaseSchema
- GovernmentRepository
- .stream_message
- enums.py
- resume_analysis/router.py
- ResumeAnalysisRepository
- auth/service.py
- GeminiProvider
- ok
- Region
- learning_resources/repository.py
- profile/router.py
- response_models.py
- interview/service.py
- .update_user_identity
- interview/router.py
- demo/router.py
- resume_analysis/service.py
- .complete
- Onboarding *(all require Bearer token)*
- ai_chat/service.py
- translate/router.py
- StructuredProfile
- SimpleLogger
- onboarding/service.py
- Any
- ai_chat/router.py
- related_skills.py
- get_supabase
- schemas/base.py
- analytics/schemas.py
- exceptions.py
- generate_questions
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
- logger.py
- context.py
- get_career_identity
- request/auth.py
- career_path.py
- JobRecommendationService
- list_resources
- skill_profile.py
- response/user.py
- find_matching_grounded_jobs
- sort_blocks_layout_aware
- TranslateService
- start_ollama.sh
- career.py
- response/auth.py
- llm_config.py
- sse_processor.py
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
- `benchmark_pdf_extraction()` --calls--> `extract_resume_bundle()`  [EXTRACTED]
  scripts/benchmark_jev.py → app/modules/resume_analysis/pdf/service.py
- `Settings` --uses--> `AIModel`  [INFERRED]
  app/core/config.py → app/core/ai_models.py

## Import Cycles
- None detected.

## Communities (91 total, 10 thin omitted)

### Community 0 - "jobs/router.py"
Cohesion: 0.09
Nodes (24): JobsRepository, Client, bulk_create(), create_job(), delete_job(), get_job(), _get_service(), list_jobs() (+16 more)

### Community 1 - "learning_resources/router.py"
Cohesion: 0.25
Nodes (12): bulk_create(), create(), update(), admin_bulk_upload(), admin_create(), admin_update(), patch, post (+4 more)

### Community 2 - "onboarding/router.py"
Cohesion: 0.19
Nodes (13): generate_questions(), _get_service(), get_state(), process_stream_endpoint(), get, post, Onboarding router — HTTP layer only. Calls service for business logic, returns…, save_preferences() (+5 more)

### Community 3 - "resume_analysis/schemas.py"
Cohesion: 0.23
Nodes (16): build_deterministic_profile(), preflight.py — Zero-LLM preflight orchestrator and deterministic profile…, Builds a rich, valid StructuredProfile entirely from zero-LLM deterministic…, extract_structured_profile(), _parse_ai_education(), _parse_ai_experiences(), _parse_ai_trajectory(), any (+8 more)

### Community 4 - "resume_parser.py"
Cohesion: 0.20
Nodes (10): detect_achievements(), extract_india_details(), _parse_json(), parse_resume(), Deterministic ATS scoring in <1ms without burning LLM calls., Deterministic Indian qualification and exam extraction in <0.1ms., Deterministic metric-bearing achievement isolation in <0.1ms., rewrite_bullets() (+2 more)

### Community 5 - "deterministic/__init__.py"
Cohesion: 0.12
Nodes (18): extract_contact_info(), Any, contact_parser.py — Zero-hallucination contact information and profile link…, Extracts contact coordinates and URLs deterministically with zero hallucination., extract_indian_regulatory_flags(), Any, flags_parser.py — Indian regulatory flags, demographic bias detection, and…, Detects ATS compliance, cultural biases, and vocational credentials in Indian… (+10 more)

### Community 6 - "JevProvider"
Cohesion: 0.18
Nodes (12): JevProvider, Scores candidate assessment answer on a 1-5 competence scale (<0.01ms)., Jev System One Decision Engine — high-speed non-autoregressive decision model.…, benchmark_assessment_scoring(), benchmark_chat_triage(), benchmark_job_matching(), benchmark_pdf_extraction(), Benchmark PDF extraction latency and character volume. (+4 more)

### Community 7 - "SkillProfileRepository"
Cohesion: 0.06
Nodes (29): DashboardRepository, Client, _get_service(), get_summary(), get, DashboardService, JobRecommendationEngine, _label_to_numeric() (+21 more)

### Community 8 - "pdf/service.py"
Cohesion: 0.20
Nodes (15): extract_pdf_content(), extractor.py — High-speed PyMuPDF extraction engine with layout-aware column…, High-speed PyMuPDF extraction engine with layout-aware column de-jumbling.…, extract_contact_info(), section_parser.py — Segment resume text into canonical sections and extract…, Extract candidate contact details and online profiles from text and extracted…, Segment resume into canonical sections using boundary detection., segment_sections() (+7 more)

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

### Community 14 - "resume_analysis/router.py"
Cohesion: 0.16
Nodes (14): resume_analysis module package., check_bullet_rate_limit(), increment_bullet_rate_limit(), rate_limiter.py — Rate limiting for LLM bullet improvement calls., Increments the daily bullet improvement count for the user., Checks and updates the daily rate limit for bullet improvements., analyze_resume(), improve_single_bullet() (+6 more)

### Community 15 - "ResumeAnalysisRepository"
Cohesion: 0.13
Nodes (11): Any, Upserts full analysis result to the resume_analysis table., Returns the latest resume analysis record for a user., Returns score metrics and flags for quick dashboard viewing., Auto-syncs extracted skills to user_skill_profiles via skill aggregator., ResumeAnalysisRepository, get_latest_analysis(), get_score_breakdown() (+3 more)

### Community 16 - "auth/service.py"
Cohesion: 0.12
Nodes (16): AIModel, get_embedding_model(), Centralized AI model names to avoid hardcoded strings across the codebase., Returns a SentenceTransformer model for local embedding generation. Used for…, Backend config — reads all settings from .env via Pydantic BaseSettings. Single…, create_access_token(), create_refresh_token(), generate_otp() (+8 more)

### Community 17 - "GeminiProvider"
Cohesion: 0.13
Nodes (12): GeminiProvider, get_gemini_instance(), Internal helper to build model with specific name and instruction., Generate a response from Gemini, with automatic local Ollama fallback., Execute completion and parse JSON output, handling markdown fences and retrying…, Stream response from Gemini with local Ollama fallback., Check if Gemini or local Ollama is available., Returns a global singleton instance of GeminiProvider. (+4 more)

### Community 18 - "ok"
Cohesion: 0.14
Nodes (13): AnalyticsRepository, export_csv(), get_funnel(), get_outcomes(), get_overview(), _get_service(), get_skill_gaps(), get (+5 more)

### Community 19 - "Region"
Cohesion: 0.09
Nodes (29): EducationLevel, Gender, Language, Gender identification., Region, ProfileRequest, StudentOnboardingRequest, ProfileUpdateRequest (+21 more)

### Community 20 - "learning_resources/repository.py"
Cohesion: 0.24
Nodes (8): build_roadmap(), Fetches matching resources for top 5 gaps, then calls Gemini to generate a…, _strip_fences(), find_by_skill_tag(), Finds active resources where skill_tags contains the given tag. Uses PostgreSQL…, soft_delete(), admin_delete(), delete

### Community 21 - "profile/router.py"
Cohesion: 0.06
Nodes (36): ProfileRepository, Client, Profile repository — all DB queries for profile and enrichment tables., Stores or updates detailed multi-model analysis for a user., Fetches daily bullet rewrite count for a user., Increments the daily bullet rewrite count., Resets all bullet rewrite counts (for cron jobs)., get_completion() (+28 more)

### Community 22 - "response_models.py"
Cohesion: 0.15
Nodes (13): force_run(), get_report(), get_roadmap(), get, post, Returns cached gap analysis report. Recomputes automatically if stale or…, Forces a fresh recompute regardless of cache state. Called when user clicks…, Returns only the roadmap portion of the current report. (+5 more)

### Community 23 - "interview/service.py"
Cohesion: 0.17
Nodes (9): get_default_questions(), prompts.py — Prompts and fallback questions for mock interviews., Fallback questions when LLM is unavailable., InterviewService, Any, service.py — Mock interview question generation, response scoring, and…, Generates comprehensive HR interview report., Initializes a new interview session and generates questions. (+1 more)

### Community 24 - ".update_user_identity"
Cohesion: 0.20
Nodes (5): Lazily load SentenceTransformer only when first needed., Synthesizes a professional persona using local Ollama model., Converts text to vector using Ollama nomic-embed-text with SentenceTransformer…, Orchestrates generation, embedding, and saving to Supabase., Pulls skills + preferences from DB and updates user identity lazily.

### Community 25 - "interview/router.py"
Cohesion: 0.12
Nodes (15): AnswerRequest, interview module package., get_interview_report(), get, post, router.py — FastAPI endpoints for AI mock interview sessions. Prefix: /interview, start_interview(), submit_answer() (+7 more)

### Community 26 - "demo/router.py"
Cohesion: 0.22
Nodes (10): personas.py — Pre-seeded demo user profiles for judging and evaluation., demo_login(), post, router.py — Pre-seeded demo login personas for hackathon judging. POST…, DemoLoginData, DemoLoginRequest, DemoLoginResponse, DemoUserResponse (+2 more)

### Community 27 - "resume_analysis/service.py"
Cohesion: 0.19
Nodes (14): repository.py — Database persistence and skill-sync operations for resume…, QualityScores, ResumeAnalysisResult, _calculate_ats_score(), _calculate_keyword_relevance(), calculate_quality_scores(), _calculate_quantification_score(), _calculate_readability_score() (+6 more)

### Community 29 - "Onboarding *(all require Bearer token)*"
Cohesion: 0.07
Nodes (29): Admin (requires X-Admin-Secret header), API Reference, Auth, Chat *(requires Bearer token)*, Dashboard *(requires Bearer token)*, DELETE /chat/history, GET /auth/me *(requires Bearer token)*, GET /chat/history (+21 more)

### Community 30 - "ai_chat/service.py"
Cohesion: 0.13
Nodes (13): ABC, ILLMProvider, ILLMProvider — abstract interface for LLM providers. Interface Segregation:…, Return full response as a string., Yield response tokens one at a time., Quick health check — True if API is reachable., get_ollama_instance(), OllamaProvider (+5 more)

### Community 31 - "translate/router.py"
Cohesion: 0.27
Nodes (8): post, router.py — Translation API endpoint. Prefix: /api/translate (mounted under…, Translates text using local Ollama model., translate_text(), BaseModel, schemas.py — Request and response models for translation service., TranslateRequest, TranslateResponse

### Community 32 - "StructuredProfile"
Cohesion: 0.15
Nodes (22): get_active_provider(), provider.py — Active LLM provider resolution for resume analysis. Prioritizes…, Returns high-speed Gemini Flash Lite provider when configured, or local Ollama…, BulletImprovement, StructuredProfile, SuggestionSet, batch_improve_bullets(), improve_bullet() (+14 more)

### Community 34 - "onboarding/service.py"
Cohesion: 0.23
Nodes (11): set_user_type(), AnswerItem, GenerateQuestionsIn, OnboardingStateOut, PreferencesIn, BaseModel, QuestionOut, Onboarding schemas — Pydantic models for all 5 steps. (+3 more)

### Community 35 - "Any"
Cohesion: 0.22
Nodes (5): Any, Detects photo mentions, demographic disclosures, and formatting risks in…, Scores mock interview answer on a 1-10 scale with feedback (<0.05ms)., Triage chat message for safety, intent classification, and emergency distress…, Evaluates candidate-job suitability in a single parallel decision pass…

### Community 36 - "ai_chat/router.py"
Cohesion: 0.11
Nodes (17): ChatRepository, Client, clear_history(), get_history(), _get_prefs(), _get_profile(), _get_service(), delete (+9 more)

### Community 37 - "related_skills.py"
Cohesion: 0.39
Nodes (7): _get_client(), get_related_skills(), BaseModel, post, related_skills.py — POST /api/skills/related Uses Groq Llama3 to suggest…, RelatedSkillsRequest, RelatedSkillsResponse

### Community 38 - "get_supabase"
Cohesion: 0.18
Nodes (15): get_supabase(), Client, Supabase client singleton. One connection, shared across the app. Tested on…, Quick connectivity check — called at startup., test_connection(), startup(), compute_hash(), Produces a deterministic hash of the user's skill profile state. Hash inputs:… (+7 more)

### Community 39 - "schemas/base.py"
Cohesion: 0.08
Nodes (19): SkillBridge AI — Base Schema Common Pydantic configuration for all models., ChatRequest, AI Chat Request Schemas Handles messages sent to the AI assistant., Request message for AI chat., Resume Request Schemas Handles resume analysis and improvement requests., Raw resume text analysis request., Resume improvement request based on target job., ResumeAnalysisRequest (+11 more)

### Community 40 - "analytics/schemas.py"
Cohesion: 0.53
Nodes (5): AnalyticsOverview, DistrictFunnel, BaseModel, SkillGap, TrainingOutcome

### Community 41 - "exceptions.py"
Cohesion: 0.07
Nodes (22): GroqProvider, AdminUnauthorized, AIProviderUnavailable, AIQuotaExceeded, AIRateLimit, AIResponseParseError, AppError, GapAnalysisNoJobs (+14 more)

### Community 42 - "generate_questions"
Cohesion: 0.25
Nodes (8): build_system_prompt(), build_user_prompt(), generate_questions(), Generate career assessment questions via local Ollama provider., Ensures semantic alignment between question text and answer input type., Sanitize a list of generated questions., sanitize_question(), sanitize_question_list()

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
Cohesion: 0.08
Nodes (26): decode_token(), Returns payload dict or None if invalid/expired., Returns user_id from a valid refresh token, else None., verify_refresh_token(), EmailService, Sends an OTP email using Resend, or falls back to logger in dev/test., AuthRepository, Client (+18 more)

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

### Community 70 - "llm_inputs.py"
Cohesion: 0.13
Nodes (10): CareerGuidanceLLMInput, MockInterviewLLMInput, LLM Input Schemas Lean, prompt-ready models for LLM calls., Context for career guidance prompts., Converts model to a clean string for prompts., Context for resume analysis prompts., Context for mock interview prompts., Context for roadmap generation prompts. (+2 more)

### Community 71 - "logger.py"
Cohesion: 0.08
Nodes (29): get_logger(), Returns user_id (sub) from a valid access token, else None., verify_access_token(), health(), get, main.py — app factory. Mounts all routers, registers exception handlers, runs…, Chat repository — all DB ops for chat_messages table., Dashboard repository — joins across profile, preferences, questionnaire, and… (+21 more)

### Community 72 - "context.py"
Cohesion: 0.42
Nodes (10): BaseContext, BlueCollarContext, build_context_json(), Any, Main entry point to build the context JSON for the LLM. 'data' is the…, EmployerContext, GovtOfficerContext, InformalWorkerContext (+2 more)

### Community 73 - "get_career_identity"
Cohesion: 0.25
Nodes (9): get_career_identity(), get_job_recommendations(), Any, get, post, Get personalized job recommendations for the current user. Uses AI-generated…, Force a re-generation of the user's career identity persona and embedding.…, Fetches the current user's AI-generated career persona. (+1 more)

### Community 74 - "request/auth.py"
Cohesion: 0.20
Nodes (9): OTPRequest, OTPVerifyRequest, Authentication Request Schemas Handles login, registration, and session…, Request a one-time password., Initial signup with role selection., Verify OTP and get tokens., Request new access token using refresh token., SignupRequest (+1 more)

### Community 75 - "career_path.py"
Cohesion: 0.20
Nodes (9): CareerPathResponse, Career Path Response Schemas Recommendations and week-by-week roadmaps., Specific role recommendation., List of recommended career paths., Weekly step in a learning roadmap., Complete week-by-week roadmap., RecommendedRole, RoadmapResponse (+1 more)

### Community 76 - "JobRecommendationService"
Cohesion: 0.28
Nodes (6): JobRecommendationService, Any, Handles job recommendations using vector similarity and hybrid matching…, Embeds all existing jobs that don't have embeddings., Fetches top job recommendations for a user based on their career identity., Simple keyword/category fallback when vector search fails or has no matches.

### Community 77 - "list_resources"
Cohesion: 0.33
Nodes (6): get_all_filtered(), get_by_id(), get_resource(), list_resources(), get, Public endpoint — returns active resources with optional filters.

### Community 78 - "skill_profile.py"
Cohesion: 0.25
Nodes (7): Skill Profile Response Schemas Detailed skill sets, proficiencies, and…, A single skill entry., Full skill profile for a user., High-level summary of a user's skills., SkillItemResponse, SkillProfileResponse, SkillSummaryResponse

### Community 79 - "response/user.py"
Cohesion: 0.25
Nodes (7): DashboardLocationSchema, DashboardUserSchema, User Response Schemas Safe public fields and dashboard summaries., Public profile information., Dashboard summary for the user., UserDashboardResponse, UserProfileResponse

### Community 80 - "find_matching_grounded_jobs"
Cohesion: 0.40
Nodes (4): find_matching_grounded_jobs(), Any, grounding.py — Deterministic retrieval pre-flight for grounded job matching.…, Retrieves verified active jobs matching user query and state.

### Community 81 - "sort_blocks_layout_aware"
Cohesion: 0.50
Nodes (3): block_sorter.py — Layout-aware PDF text block ordering and column de-jumbling., Sorts blocks preserving natural reading order. Separates full-width…, sort_blocks_layout_aware()

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

### Community 91 - "sse_processor.py"
Cohesion: 0.38
Nodes (6): _extract_skills_from_text(), process_stream(), SSE processor — streams real processing events after answer submission. Each…, Keyword match against common workforce skills plus comma-separated token…, Stream SSE events. Each step does real work., _sse_event()

### Community 92 - "llm_json_utils.py"
Cohesion: 0.40
Nodes (4): clean_and_extract_json_text(), parse_healed_json(), Parses JSON with healing strategies for common LLM syntax errors., Cleans response text, finds JSON boundaries, and attempts to close open…

### Community 95 - ".empty_strings_to_none"
Cohesion: 0.50
Nodes (3): Any, Globally convert empty strings or whitespace-only strings to None., model_validator

## Knowledge Gaps
- **62 isolated node(s):** `TaskConfig`, `run_backend.sh script`, `start_ollama.sh script`, `OLLAMA_DEBUG`, `OLLAMA_MAX_LOADED_MODELS` (+57 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 534 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `JevProvider` connect `JevProvider` to `Any`, `ai_chat/router.py`, `logger.py`, `JobRecommendationService`, `profile/router.py`, `ai_chat/service.py`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Why does `get_logger()` connect `logger.py` to `jobs/router.py`, `learning_resources/router.py`, `onboarding/service.py`, `ai_chat/router.py`, `get_supabase`, `exceptions.py`, `auth/service.py`, `learning_resources/repository.py`, `profile/router.py`, `ai_chat/service.py`, `sse_processor.py`, `auth/router.py`, `gap_engine.py`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Why does `get_supabase()` connect `get_supabase` to `learning_resources/router.py`, `logger.py`, `get_career_identity`, `GovernmentRepository`, `JobRecommendationService`, `list_resources`, `ResumeAnalysisRepository`, `learning_resources/repository.py`, `profile/router.py`, `.update_user_identity`, `resume_analysis/service.py`, `gap_engine.py`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **What connects `TaskConfig`, `run_backend.sh script`, `start_ollama.sh script` to the rest of the system?**
  _62 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `jobs/router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09146341463414634 - nodes in this community are weakly interconnected._
- **Should `deterministic/__init__.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1225296442687747 - nodes in this community are weakly interconnected._
- **Should `SkillProfileRepository` be split into smaller, more focused modules?**
  _Cohesion score 0.0641025641025641 - nodes in this community are weakly interconnected._