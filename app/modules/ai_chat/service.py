"""
service.py — AI chat service. Manages conversation context, groundings, and streaming generation.
"""
from typing import AsyncGenerator
from app.modules.ai_chat.providers.base import ILLMProvider
from app.modules.ai_chat.providers.ollama_provider import get_ollama_instance
from app.modules.ai_chat.providers.jev_provider import JevProvider
from app.modules.ai_chat.repository import ChatRepository
from app.core.logger import get_logger
from app.modules.ai_chat.prompts import build_system_prompt, build_greeting
from app.modules.ai_chat.grounding import find_matching_grounded_jobs
from app.modules.ai_chat.stream_filter import merge_consecutive_roles, filter_thinking_stream

log = get_logger("AI_CHAT")


class ChatService:
    def __init__(self, repo: ChatRepository):
        self.repo = repo
        self.provider = get_ollama_instance()
        self.jev = JevProvider()

    def _get_provider(self, language: str) -> ILLMProvider:
        """Semantic Multi-Provider Router: Prefer Gemini Flash if available; fallback to Ollama."""
        try:
            from app.modules.ai_chat.providers.gemini import get_gemini_instance
            gemini = get_gemini_instance()
            if gemini.model is not None:
                return gemini
        except Exception:
            pass
        return self.provider

    async def stream_message(
        self,
        user_id: str,
        content: str,
        language: str,
        user: dict,
        profile: dict | None,
        prefs: dict | None,
    ) -> AsyncGenerator[str, None]:
        self.repo.add_message(user_id, "user", content, language)

        # Jev System 1 Guardrail & Triage
        triage = await self.jev.check_chat_guardrails(content)
        if not triage.get("is_safe", True):
            yield "I am here to help you with your career and professional growth. Please let me know how I can support your learning or job search goals."
            return

        if triage.get("is_distress", False):
            yield "It sounds like you are going through a very tough time. Please reach out to trusted friends, family, or professional helpline services. Your well-being comes first."
            return

        intent = triage.get("intent", "career_guidance")
        name = (profile or {}).get("full_name") or user.get("email", "there").split("@")[0].title()
        state = (profile or {}).get("state") or "India"

        # Tier 0 Semantic Fast Path: Instant Greeting with 0 LLM calls (<2ms)
        if intent == "greeting" and len(content.split()) <= 4:
            greeting_text = build_greeting(name, state, language)
            self.repo.add_message(user_id, "assistant", greeting_text, language)
            yield greeting_text
            return

        history = self.repo.get_history(user_id, limit=11)
        system_prompt = build_system_prompt(user, profile, prefs, language)

        # Grounding with active DB jobs
        if intent == "job_search":
            grounded_jobs = find_matching_grounded_jobs(content, state)
            if grounded_jobs:
                job_lines = [
                    f"- {j.get('title')} at {j.get('company')} ({j.get('location_city')}, {j.get('location_state')}) | Salary: ₹{j.get('salary_min', 0):,}-₹{j.get('salary_max', 0):,}/mo | Skills: {', '.join(j.get('required_skills', []))}"
                    for j in grounded_jobs
                ]
                system_prompt += (
                    "\n\n[VERIFIED ACTIVE JOB OPENINGS IN DATABASE]:\n"
                    + "\n".join(job_lines)
                    + "\n\nInstruction: Recommend and quote these verified openings directly to the user. Do not invent fake jobs or placeholder companies."
                )

        raw_messages = [{"role": "system", "content": system_prompt}]
        raw_messages += [{"role": m["role"], "content": m["content"]} for m in history]

        while len(raw_messages) > 1 and raw_messages[1]["role"] == "assistant":
            raw_messages.pop(1)

        messages = merge_consecutive_roles(raw_messages)
        log.info(f"Chat message for user={user_id}, lang={language}")

        provider = self._get_provider(language)
        raw_stream = provider.stream(messages, language)

        full_response = []
        async for chunk in filter_thinking_stream(raw_stream):
            full_response.append(chunk)
            yield chunk

        if full_response:
            self.repo.add_message(user_id, "assistant", "".join(full_response), language)

    def get_history(self, user_id: str) -> list[dict]:
        return self.repo.get_history(user_id, limit=50)

    def clear_history(self, user_id: str):
        self.repo.clear_history(user_id)
