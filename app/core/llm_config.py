"""
SkillBridge AI — LLM Configuration
All model configs hardcoded for local hardware optimization.
Hardware: GTX 1050 Mobile 4GB VRAM → using sub-3GB models for high speed.
"""
import os
from dataclasses import dataclass

# ── Ollama Server ─────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434") + "/v1"
OLLAMA_API_KEY = "ollama"

# ── Recommended Models (Ranked by Speed/VRAM) ──────────────────
# 1. qwen2.5:0.5b-instruct-q4_K_M (~400MB) -> Fastest for scoring/gaps
# 2. phi4-mini:latest (~2.5GB) -> Best for resumes/roadmaps (replaces phi3)
# 3. gemma2:2b-instruct-q4_K_M (~1.6GB) -> Best for interview/advice
# 4. qwen2.5:1.5b-instruct-q4_K_M (~1GB) -> All-rounder

PRIMARY_MODEL = "qwen2.5:1.5b-instruct-q4_K_M"
EXTRACTION_MODEL = "qwen2.5:1.5b-instruct-q4_K_M" 
EMBEDDINGS_MODEL = "nomic-embed-text:latest"

GLOBAL_RULES = """
ROLE: You are an elite backend AI engineer building SkillBridge — an AI-powered 
career guidance and upskilling platform for India (Skill India / Digital India mission).

HARD RULES — NEVER VIOLATE:
1. Return ONLY valid JSON. Zero prose. Zero markdown. Zero explanation.
2. Match schema EXACTLY as defined per task. No extra fields.
3. All arrays: max 3–5 items unless schema specifies otherwise.
4. All strings: concise. Max 10 words unless specified.
5. Temperature mindset: deterministic, factual, no creativity unless asked.
6. If data missing → use null. Never hallucinate values.
7. Optimize every output for downstream Pydantic parsing.
"""

@dataclass(frozen=True)
class TaskConfig:
    model: str
    temperature: float
    max_tokens: int
    context_window: int
    task_name: str

# ── Module-Specific Optimization ──────────────────────────────

# MODULE 1: Skill Gap Analyzer (num_predict: 150)
GAP_ANALYSIS = TaskConfig(
    model="qwen2.5:0.5b-instruct-q4_K_M", temperature=0.1,
    max_tokens=150, context_window=1024,
    task_name="skill_gap_analysis"
)

# MODULE 2: Career Recommendation Engine (num_predict: 250)
CAREER_REC = TaskConfig(
    model="gemma2:2b-instruct-q4_K_M", temperature=0.1,
    max_tokens=250, context_window=1024,
    task_name="career_recommendation"
)

# MODULE 3: Learning Roadmap (num_predict: 2000)
ROADMAP = TaskConfig(
    model="qwen2.5:1.5b-instruct-q4_K_M", temperature=0.1,
    max_tokens=2000, context_window=4096,
    task_name="learning_roadmap"
)

# MODULE 4: Resume Analyzer (num_predict: 400)
RESUME_PARSE = TaskConfig(
    model="qwen2.5:1.5b-instruct-q4_K_M", temperature=0.1,
    max_tokens=400, context_window=2048,
    task_name="resume_analysis"
)

# MODULE 5: Interview Questions (num_predict: 400)
MOCK_INTERVIEW = TaskConfig(
    model="gemma2:2b-instruct-q4_K_M", temperature=0.15,
    max_tokens=400, context_window=4096,
    task_name="interview_generation"
)

# MODULE 6: Interview Evaluator (num_predict: 120)
INTERVIEW_EVAL = TaskConfig(
    model="qwen2.5:0.5b-instruct-q4_K_M", temperature=0.1,
    max_tokens=120, context_window=2048,
    task_name="interview_evaluation"
)

# MODULE 7: Job Match Scorer (num_predict: 150)
JOB_RANKING = TaskConfig(
    model="qwen2.5:0.5b-instruct-q4_K_M", temperature=0.1,
    max_tokens=150, context_window=2048,
    task_name="job_matching"
)

# MODULE 8: Blue-Collar Guide (num_predict: 200)
VOCATIONAL_GUIDE = TaskConfig(
    model="qwen2.5:1.5b-instruct-q4_K_M", temperature=0.1,
    max_tokens=200, context_window=2048,
    task_name="vocational_guidance"
)

# MODULE 9: Skill Extractor (num_predict: 1000)
SKILL_EXTRACT = TaskConfig(
    model="phi4-mini:latest", temperature=0.0,
    max_tokens=1000, context_window=4096,
    task_name="skill_extraction"
)

# MODULE 10: Resume Bullet Improver (num_predict: 150)
BULLET_IMPROVE = TaskConfig(
    model="qwen2.5:1.5b-instruct-q4_K_M", temperature=0.1,
    max_tokens=150, context_window=1024,
    task_name="bullet_improvement"
)

# MODULE 11: Adaptive Assessment (num_predict: 200)
ASSESSMENT = TaskConfig(
    model="gemma2:2b-instruct-q4_K_M", temperature=0.2,
    max_tokens=200, context_window=4096,
    task_name="adaptive_assessment"
)

# Legacy / Misc
CAREER_CHAT = TaskConfig(
    model=PRIMARY_MODEL, temperature=0.7,
    max_tokens=512, context_window=4096,
    task_name="career_guidance_chat"
)

# ── Task Registry ─────────────────────────────────────────────
LLM_TASKS = {
    "gap_analysis": GAP_ANALYSIS,
    "career_rec": CAREER_REC,
    "roadmap": ROADMAP,
    "resume": RESUME_PARSE,
    "interview": MOCK_INTERVIEW,
    "interview_eval": INTERVIEW_EVAL,
    "job_ranking": JOB_RANKING,
    "vocational_guide": VOCATIONAL_GUIDE,
    "chat": CAREER_CHAT,
    "bullet_improve": BULLET_IMPROVE,
    "skill_extract": SKILL_EXTRACT,
    "assessment": ASSESSMENT,
    "assessment_extraction": SKILL_EXTRACT
}

# ── Runtime Config ────────────────────────────────────────────
OLLAMA_PARAMS = {
    "num_ctx": 2048,
    "num_predict": 256,
    "temperature": 0.1,
    "top_p": 0.9,
    "repeat_penalty": 1.1,
    "num_thread": 6,  # Balanced for GTX 1050 Mobile
    "num_gpu": 999
}

MAX_RETRIES = 2
RETRY_DELAY = 1.0
HEALTH_MODEL = PRIMARY_MODEL
