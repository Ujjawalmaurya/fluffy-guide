"""
Question engine — builds SarvamAI prompt, parses returned JSON questions.
Isolated here so question format can change without touching service.py.
"""
import json
import httpx
from app.core.config import settings
from app.core.logger import get_logger
from app.shared.exceptions import AIProviderUnavailable, AIResponseParseError

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
    return """You are a career assessment expert for India's workforce.
Your task is to generate exactly 6 career assessment questions based on the user's profile.

CRITICAL INSTRUCTION: You MUST return ONLY a valid JSON array. Do not include any conversational text, explanations, or formatting blocks.
The JSON array must have this exact structure:
[
  {
    "id": "q1",
    "question": "...",
    "type": "text|mcq|rating",
    "options": ["...", "..."]
  }
]

Rules:
- Questions should assess current skills, work experience, and career goals.
- STRICT ALIGNMENT: If a question asks to describe, explain, or answer in words, type MUST be "text" and options MUST be [].
- Rating questions MUST strictly be phrased as a rating scale (e.g. "Rate your experience with X from 1 to 5:"). NEVER ask for a description or words if type is "rating".
- For "rating", options MUST be ["1","2","3","4","5"].
- For "mcq", options MUST contain 3 to 5 realistic choices.
- For "text", options MUST be []."""

def build_user_prompt(user_type: str, state: str, career_interests: list[str], language: str) -> str:
    hint = USER_TYPE_HINTS.get(user_type, "Ask about skills, goals, and work experience.")
    interests_str = ", ".join(career_interests) if career_interests else "general workforce"
    lang_instruction = "Respond in Hindi only." if language == "hi" else "Respond in English."

    return f"""Profile: {user_type} in {state}
Interests: {interests_str}
Language: {lang_instruction}

Context: {hint}
Generate the 6 questions now."""


async def generate_questions(user_type: str, state: str, career_interests: list[str], language: str) -> list[dict]:
    """Generate career assessment questions via local Ollama provider."""
    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(user_type, state, career_interests, language)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        from app.modules.ai_chat.providers.ollama_provider import get_ollama_instance
        ollama = get_ollama_instance()
        questions = await ollama.complete_json(messages, temperature=0.5, max_tokens=1500)
        if isinstance(questions, dict) and "questions" in questions:
            questions = questions["questions"]
        elif not isinstance(questions, list):
            questions = []

        from app.modules.onboarding.question_sanitizer import sanitize_question_list
        questions = sanitize_question_list(questions)
        log.info(f"Generated {len(questions)} questions for {user_type} via local Ollama ({ollama.model})")
        return questions
    except Exception as e:
        log.error(f"Failed to generate questions with local Ollama: {e}")
        fallback = [
            {"id": "q1", "question": "Describe your daily work responsibilities and the primary tools you use.", "type": "text", "options": []},
            {"id": "q2", "question": "On a scale of 1 to 5, rate your proficiency with computer applications.", "type": "rating", "options": ["1", "2", "3", "4", "5"]},
            {"id": "q3", "question": "Which work environment suits you best?", "type": "mcq", "options": ["Office desk work", "Field and on-site", "Hybrid / remote", "Factory or workshop"]},
            {"id": "q4", "question": "In a few words, tell us about a challenging project or task you completed.", "type": "text", "options": []},
            {"id": "q5", "question": "What is your main career goal for the next 12 to 24 months?", "type": "text", "options": []},
            {"id": "q6", "question": "On a scale of 1 to 5, rate your confidence in learning new technical skills quickly.", "type": "rating", "options": ["1", "2", "3", "4", "5"]},
        ]
        from app.modules.onboarding.question_sanitizer import sanitize_question_list
        return sanitize_question_list(fallback)
