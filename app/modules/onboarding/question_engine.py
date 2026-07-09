"""
Question engine — builds prompt, parses returned JSON questions via Ollama.
Isolated here so question format can change without touching service.py.
"""
from app.core.logger import get_logger
from app.core import llm_config
from app.modules.ai_chat.providers.base import IStructuredProvider

log = get_logger("ONBOARDING")

# User type → tailored instructions inserted into the prompt
USER_TYPE_HINTS = {
    "individual_youth": "Ask about education, projects, technical interests, and career aspirations.",
    "individual_bluecollar": "Ask about tools used, certifications, daily work tasks, and years of experience.",
    "individual_informal": "Ask about existing business or work, digital tools used, and income goals.",
    "org_ngo": "Ask about target beneficiaries, training programs offered, and placement metrics.",
    "org_employer": "Ask about hiring needs, required skills, and preferred candidate profiles.",
    "org_govt": "Ask about skill gap areas being monitored, target regions, and data needs.",
}


def build_system_prompt() -> str:
    return f"""ROLE: You are an elite career assessment expert for SkillBridge AI, focusing on India's underserved workforce.

TASK: Generate exactly 6 career assessment questions based on the user's profile.

JSON STRUCTURE:
[
  {{
    "id": "q1",
    "question": "...",
    "type": "text|mcq|rating",
    "options": ["...", "..."]
  }}
]

RULES:
- Questions should assess current skills, work experience, and career goals.
- Use "mcq" ONLY if options are fixed.
- For "rating", use ["1","2","3","4","5"].
- For "text", options MUST be [].
- Language MUST match the user's requested language.

{llm_config.CONCISENESS_INSTRUCTION}
"""

def build_user_prompt(user_type: str, state: str, career_interests: list[str], language: str) -> str:
    hint = USER_TYPE_HINTS.get(user_type, "Ask about skills, goals, and work experience.")
    interests_str = ", ".join(
        str(i.get("label") if isinstance(i, dict) else i)
        for i in career_interests
    ) if career_interests else "general workforce"
    lang_instruction = "Respond in Hindi." if language == "hi" else "Respond in English."

    return f"""USER PROFILE:
- Type: {user_type}
- State: {state}
- Interests: {interests_str}
- Language: {lang_instruction}

CONTEXT: {hint}
Generate 6 questions now."""


async def generate_questions(
    llm_provider: IStructuredProvider,
    user_type: str, 
    state: str, 
    career_interests: list[str], 
    language: str
) -> list[dict]:
    """Call local LLM and return parsed question list."""
    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(user_type, state, career_interests, language)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    questions = await llm_provider.complete_json(
        messages=messages,
        config=llm_config.ONBOARDING_Q_GEN
    )

    log.info(f"Generated {len(questions)} questions for {user_type} via Ollama ({llm_config.ONBOARDING_Q_GEN.model})")
    return questions
