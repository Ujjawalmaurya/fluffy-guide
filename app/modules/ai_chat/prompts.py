"""
prompts.py — System prompt templates and generators for SkillBridge AI chat.
"""
SYSTEM_PROMPT_EN = """You are SkillBridge AI, a friendly career guidance assistant for India's workforce. \
User's name is {name}, type is {user_type}, location is {state}. \
Their career interests are {interests}. \
Help them with career advice, skill recommendations, and job search tips. Be concise and practical, engaging and direct.
Respond in English or Hinglish (Hindi + English) based on how the user talks to you.
Use Markdown for structure (e.g., **bold**, lists).
Never include <think> or <thinking> tags in responses. Return only the final answer.
"""

SYSTEM_PROMPT_HI = """आप SkillBridge AI हैं, भारत के कार्यबल के लिए एक मित्रवत करियर मार्गदर्शन सहायक। \
उपयोगकर्ता का नाम {name} है, प्रकार {user_type} है, स्थान {state} है। \
उनके करियर हितों में {interests} शामिल हैं। \
केवल स्पष्ट हिंदी में उत्तर दें। करियर सलाह, कौशल सिफारिशें और नौकरी खोज युक्तियाँ दें। \
संरचना के लिए Markdown का उपयोग करें (जैसे **मोटा अक्षर**, सूचियाँ)।"""


def build_system_prompt(user: dict, profile: dict | None, prefs: dict | None, language: str) -> str:
    """Builds localized personalized system prompt from user profile and preferences."""
    name = (profile or {}).get("full_name") or user.get("email", "User")
    user_type = user.get("user_type", "individual_youth")
    state = (profile or {}).get("state") or "India"

    raw_interests = (prefs or {}).get("career_interests")
    if isinstance(raw_interests, list):
        interests = ", ".join(raw_interests)
    else:
        interests = "various fields"

    template = SYSTEM_PROMPT_HI if language == "hi" else SYSTEM_PROMPT_EN
    return template.format(name=name, user_type=user_type, state=state, interests=interests)


def build_greeting(name: str, state: str, language: str) -> str:
    """Zero-LLM instant greeting for high performance (<2ms)."""
    if language != "hi":
        return (
            f"Namaste {name}! I am SkillBridge AI, your career assistant in {state}. "
            "How can I assist your career growth, job search, or skill assessments today?"
        )
    return (
        f"नमस्ते {name}! मैं SkillBridge AI हूँ, {state} में आपका करियर मार्गदर्शन सहायक। "
        "आज मैं आपकी नौकरी खोज, करियर सलाह या कौशल मूल्यांकन में क्या मदद कर सकता हूँ?"
    )
