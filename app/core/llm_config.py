"""
SkillBridge AI — LLM Configuration
All model configs hardcoded for local hardware optimization.
Hardware: RTX 4050 Mobile 6GB VRAM → using consolidated 2-model split.
"""
import os
from dataclasses import dataclass

# ── Ollama Server ─────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434") + "/v1"
OLLAMA_API_KEY = "ollama"

# ── Consolidated Models ────────────────────────────────────────
REASONING_MODEL = "qwen3:4b"
EXTRACTION_MODEL = "qwen2.5:1.5b"
EMBEDDING_MODEL = "nomic-embed-text:latest"

# Keep backward-compatibility aliases if any system checks refer to them
PRIMARY_MODEL = REASONING_MODEL
EMBEDDINGS_MODEL = EMBEDDING_MODEL

CONCISENESS_INSTRUCTION = "Be concise. Maximum 3 sentences per point. No preamble. No repetition."

EXTRACTION_RULES = f"""
ROLE: You are an elite backend AI engineer building SkillBridge.

HARD RULES — NEVER VIOLATE:
1. Return ONLY valid JSON. Zero prose. Zero markdown. Zero explanation.
2. Match schema EXACTLY. No extra fields.
3. Temperature mindset: deterministic, factual, no creativity.
4. If data missing → use null. Never hallucinate.

{CONCISENESS_INSTRUCTION}
"""

CHAT_RULES = f"""
ROLE: You are SkillBridge AI, a sharp, open-minded career mentor.
STYLE: Punchy notes, high agency, zero corporate fluff.

{CONCISENESS_INSTRUCTION}
"""

@dataclass(frozen=True)
class TaskConfig:
    model: str
    temperature: float
    max_tokens: int
    context_window: int
    task_name: str

# ── Module-Specific Optimization ──────────────────────────────
# Extraction-tier calls are capped lower (roughly 200–300 tokens)
# Reasoning-tier calls are capped higher (roughly 600–800 tokens)

# MODULE 1: Skill Gap Analyzer (Reasoning)
GAP_ANALYSIS = TaskConfig(
    model=REASONING_MODEL, temperature=0.1,
    max_tokens=2500, context_window=4096,
    task_name="skill_gap_analysis"
)

# MODULE 2: Career Recommendation Engine (Reasoning)
CAREER_REC = TaskConfig(
    model=REASONING_MODEL, temperature=0.1,
    max_tokens=2500, context_window=4096,
    task_name="career_recommendation"
)

# MODULE 3: Learning Roadmap (Extraction)
ROADMAP = TaskConfig(
    model=EXTRACTION_MODEL, temperature=0.1,
    max_tokens=2048, context_window=4096,
    task_name="learning_roadmap"
)

# MODULE 4: Resume Analyzer (Extraction)
RESUME_PARSE = TaskConfig(
    model=EXTRACTION_MODEL, temperature=0.1,
    max_tokens=1500, context_window=4096,
    task_name="resume_analysis"
)

# MODULE 5: Interview Questions (Reasoning)
MOCK_INTERVIEW = TaskConfig(
    model=REASONING_MODEL, temperature=0.4,
    max_tokens=2500, context_window=4096,
    task_name="interview_generation"
)

# MODULE 6: Interview Evaluator (Extraction)
INTERVIEW_EVAL = TaskConfig(
    model=EXTRACTION_MODEL, temperature=0.1,
    max_tokens=300, context_window=2048,
    task_name="interview_evaluation"
)

# MODULE 7: Job Match Scorer (Reasoning)
JOB_RANKING = TaskConfig(
    model=REASONING_MODEL, temperature=0.1,
    max_tokens=2500, context_window=4096,
    task_name="job_matching"
)

# MODULE 8: Blue-Collar Guide (Reasoning)
VOCATIONAL_GUIDE = TaskConfig(
    model=REASONING_MODEL, temperature=0.1,
    max_tokens=2500, context_window=4096,
    task_name="vocational_guidance"
)

# MODULE 9: Skill Extractor (Extraction)
SKILL_EXTRACT = TaskConfig(
    model=EXTRACTION_MODEL, temperature=0.0,
    max_tokens=300, context_window=4096,
    task_name="skill_extraction"
)

# MODULE 10: Resume Bullet Improver (Extraction)
BULLET_IMPROVE = TaskConfig(
    model=EXTRACTION_MODEL, temperature=0.1,
    max_tokens=300, context_window=1024,
    task_name="bullet_improvement"
)

# MODULE 11: Adaptive Assessment (Extraction)
ASSESSMENT = TaskConfig(
    model=EXTRACTION_MODEL, temperature=0.4,
    max_tokens=500, context_window=4096,
    task_name="adaptive_assessment"
)

# MODULE 13: Assessment Extraction (Reasoning)
ASSESSMENT_EXTRACTION = TaskConfig(
    model=EXTRACTION_MODEL, temperature=0.1,
    max_tokens=1500, context_window=4096,
    task_name="assessment_extraction"
)

# Legacy / Misc (Reasoning)
CAREER_CHAT = TaskConfig(
    model=REASONING_MODEL, temperature=0.85,
    max_tokens=2500, context_window=4096,
    task_name="career_guidance_chat"
)

# MODULE 12: Onboarding Question Generator (Extraction)
ONBOARDING_Q_GEN = TaskConfig(
    model=EXTRACTION_MODEL, temperature=0.7,
    max_tokens=300, context_window=2048,
    task_name="onboarding_question_generation"
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
    "assessment_extraction": ASSESSMENT_EXTRACTION,
    "onboarding": ONBOARDING_Q_GEN
}

# ── Runtime Config ────────────────────────────────────────────
OLLAMA_PARAMS = {
    "num_ctx": 4096,  # Context size
    "num_predict": 256,
    "temperature": 0.1,
    "top_p": 0.9,
    "repeat_penalty": 1.1,
    "num_thread": 6,  # Balanced for RTX 4050 Mobile
    "num_gpu": 999
}

MAX_RETRIES = 2
RETRY_DELAY = 1.0
HEALTH_MODEL = REASONING_MODEL
