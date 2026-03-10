"""
AI chat service — manages context window, builds system prompt, streams via LLM provider.
Dependency-injected: receives ILLMProvider, so test with MockLLMProvider if needed.
"""
from typing import AsyncGenerator

from app.modules.ai_chat.providers.base import ILLMProvider
from app.modules.ai_chat.repository import ChatRepository
from app.core.logger import get_logger

log = get_logger("AI_CHAT")

SYSTEM_PROMPT_EN = """You are SkillBridge AI, a friendly career guidance assistant for India's workforce. \
User's name is {name}, type is {user_type}, location is {state}. \
Their career interests are {interests}. \
Help them with career advice, skill recommendations, and job search tips. Be concise and practical."""

SYSTEM_PROMPT_HI = """आप SkillBridge AI हैं, भारत के कार्यबल के लिए एक मित्रवत करियर मार्गदर्शन सहायक। \
उपयोगकर्ता का नाम {name} है, प्रकार {user_type} है, स्थान {state} है। \
उनके करियर हितों में {interests} शामिल हैं। \
केवल हिंदी में उत्तर दें। करियर सलाह, कौशल सिफारिशें और नौकरी खोज युक्तियाँ दें। प्रोत्साहित करें।"""


class ChatService:
    def __init__(self, repo: ChatRepository, provider: ILLMProvider):
        self.repo = repo
        self.provider = provider

    def _build_system_prompt(self, user: dict, profile: dict | None, prefs: dict | None, language: str) -> str:
        name = (profile or {}).get("full_name") or user.get("email", "User")
        user_type = user.get("user_type", "individual_youth")
        state = (profile or {}).get("state", "India")
        interests = ", ".join((prefs or {}).get("career_interests", [])) or "various fields"

        template = SYSTEM_PROMPT_HI if language == "hi" else SYSTEM_PROMPT_EN
        return template.format(name=name, user_type=user_type, state=state, interests=interests)

    async def stream_message(
        self,
        user_id: str,
        content: str,
        language: str,
        user: dict,
        profile: dict | None,
        prefs: dict | None,
    ) -> AsyncGenerator[str, None]:
        # Save user message
        self.repo.add_message(user_id, "user", content, language)

        # Build context: system prompt + last 10 messages
        history = self.repo.get_history(user_id, limit=11)  # includes the one we just added
        system_prompt = self._build_system_prompt(user, profile, prefs, language)

        messages = [{"role": "system", "content": system_prompt}]
        messages += [{"role": m["role"], "content": m["content"]} for m in history]

        log.info(f"Chat message for user={user_id}, lang={language}")

        # Stream + collect response
        full_response = []
        async for token in self.provider.stream(messages, language):
            full_response.append(token)
            yield token

        # Save assistant response
        if full_response:
            self.repo.add_message(user_id, "assistant", "".join(full_response), language)

    def get_history(self, user_id: str) -> list[dict]:
        return self.repo.get_history(user_id, limit=50)

    def clear_history(self, user_id: str):
        self.repo.clear_history(user_id)
