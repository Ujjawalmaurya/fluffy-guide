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
- Use the "options" array ONLY for "mcq" type questions.
- For "rating" type questions, include options like ["1","2","3","4","5"].
- For "text" type questions, the options array MUST be empty []."""

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
    """Call SarvamAI and return parsed question list."""
    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(user_type, state, career_interests, language)

    headers = {
        "Authorization": f"Bearer {settings.sarvam_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.sarvam_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{settings.sarvam_base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        log.error(f"SarvamAI HTTP error: {e.response.status_code} - {e.response.text}")
        raise AIProviderUnavailable()
    except Exception as e:
        log.error(f"SarvamAI request failed: {e}")
        raise AIProviderUnavailable()

    try:
        content = resp.json()["choices"][0]["message"]["content"]
        log.error(f"RAW SARVAM RESPONSE: {content}")
        # Strip markdown code blocks if present
        content = content.strip()
        if "```" in content:
            # Try to extract content between the first and second ```
            parts = content.split("```")
            if len(parts) >= 3:
                content = parts[1]
                if content.startswith("json\n"):
                    content = content[5:]
                elif content.startswith("json"):
                    content = content[4:]
        
        # Additionally find the first [ and last ] in the string to ignore <think> tags or conversational prefixes
        start_idx = content.find("[")
        end_idx = content.rfind("]")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            content = content[start_idx : end_idx + 1]
            
        questions = json.loads(content.strip())
        log.info(f"Generated {len(questions)} questions for {user_type} via SarvamAI")
        return questions
    except Exception as e:
        log.error(f"Failed to parse SarvamAI response: {e}")
        raise AIResponseParseError()
