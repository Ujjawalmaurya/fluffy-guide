"""
SkillBridge AI — LLM Configuration
All model configs hardcoded. Do not move to .env.
Hardware: GTX 1050 Mobile 6GB VRAM → use sub-6GB models only.
Runtime: Ollama local server.
To migrate to cloud API: swap OLLAMA_BASE_URL and API_KEY only.
"""
from dataclasses import dataclass
import os

# ── Ollama server ─────────────────────────────────────────────
# Host allowed in .env since it differs per machine.
# Default points to local Ollama instance.
# Future: swap to API provider here (e.g., OpenAI or Gemini)
OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434") + "/v1"
OLLAMA_API_KEY = "ollama"   # Ollama ignores this but openai client needs it

# ── Models ────────────────────────────────────────────────────
# qwen3:4b — best multilingual (Hindi+English) under 6GB VRAM
# phi4-mini — fast, precise structured JSON extraction
# nomic-embed-text — CPU embeddings, no VRAM needed
PRIMARY_MODEL      = "qwen3:4b"
EXTRACTION_MODEL   = "phi4-mini"
EMBEDDINGS_MODEL   = "nomic-embed-text"

# ── Per-task configs ──────────────────────────────────────────
@dataclass(frozen=True)
class TaskConfig:
    model: str
    temperature: float
    max_tokens: int
    context_window: int
    task_name: str

CAREER_CHAT = TaskConfig(
    model=PRIMARY_MODEL, temperature=0.7,
    max_tokens=512, context_window=2048,
    task_name="career_guidance_chat"
)
ASSESSMENT_QUESTIONS = TaskConfig(
    model=PRIMARY_MODEL, temperature=0.5,
    max_tokens=400, context_window=2048,
    task_name="skill_assessment_generation"
)
GAP_ANALYSIS = TaskConfig(
    model=PRIMARY_MODEL, temperature=0.4,
    max_tokens=600, context_window=2048,
    task_name="gap_analysis_narration"
)
ROADMAP = TaskConfig(
    model=PRIMARY_MODEL, temperature=0.4,
    max_tokens=800, context_window=2048,
    task_name="roadmap_narration"
)
RESUME_PARSE = TaskConfig(
    model=EXTRACTION_MODEL, temperature=0.1,
    max_tokens=1000, context_window=4096,
    task_name="resume_parsing"
)
SKILL_EXTRACT = TaskConfig(
    model=EXTRACTION_MODEL, temperature=0.1,
    max_tokens=500, context_window=4096,
    task_name="skill_extraction"
)
MOCK_INTERVIEW = TaskConfig(
    model=PRIMARY_MODEL, temperature=0.6,
    max_tokens=400, context_window=2048,
    task_name="mock_interview"
)

BULLET_IMPROVE = TaskConfig(
    model=EXTRACTION_MODEL, temperature=0.7,
    max_tokens=256, context_window=2048,
    task_name="resume_bullet_improvement"
)

# ── Task Registry ─────────────────────────────────────────────
# Used by modules for dynamic lookups
LLM_TASKS = {
    "chat": CAREER_CHAT,
    "assessment": ASSESSMENT_QUESTIONS,
    "assessment_extraction": SKILL_EXTRACT,
    "gap_analysis": GAP_ANALYSIS,
    "roadmap": ROADMAP,
    "resume": RESUME_PARSE,
    "skill_extract": SKILL_EXTRACT,
    "interview": MOCK_INTERVIEW,
    "bullet_improve": BULLET_IMPROVE
}

# ── Retry ─────────────────────────────────────────────────────
MAX_RETRIES = 2
RETRY_DELAY = 1.0

# ── Health check ──────────────────────────────────────────────
HEALTH_MODEL = PRIMARY_MODEL
