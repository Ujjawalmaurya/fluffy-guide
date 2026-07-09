from typing import AsyncGenerator

from app.modules.ai_chat.providers.base import ICompletionProvider
from app.modules.ai_chat.repository import ChatRepository
from app.modules.ai_chat.context_builder import build_context_json
from app.modules.ai_chat.prompts import build_system_prompt
from app.core.logger import get_logger

log = get_logger("AI_CHAT")


class ChatService:
    def __init__(self, repo: ChatRepository, provider: ICompletionProvider):
        self.repo = repo
        self.provider = provider

    async def _build_system_prompt(self, user_id: str, language: str) -> str:
        # Fetch fresh data from DB
        data = await self.repo.get_full_user_data(user_id)
        
        # Map to role-aware JSON context
        context_json = build_context_json(data)
        
        role = data.get("user", {}).get("user_type", "individual_youth")
        
        # Build system prompt from template
        return build_system_prompt(role, context_json, language)

    def _merge_consecutive_roles(self, messages: list[dict]) -> list[dict]:
        """Ensures roles alternate (user, assistant, user...). Merges consecutive identical roles."""
        if not messages:
            return []
        
        merged = []
        for msg in messages:
            if merged and merged[-1]["role"] == msg["role"]:
                # Append content with newline
                merged[-1]["content"] += "\n" + msg["content"]
            else:
                merged.append({"role": msg["role"], "content": msg["content"]})
        return merged

    async def stream_message(
        self,
        user_id: str,
        content: str,
        language: str,
    ) -> AsyncGenerator[str, None]:
        # Save user message
        await self.repo.add_message(user_id, "user", content, language)

        history = await self.repo.get_history(user_id, limit=11)
        system_prompt = await self._build_system_prompt(user_id, language)

        raw_messages = [{"role": "system", "content": system_prompt}]
        raw_messages += [{"role": m["role"], "content": m["content"]} for m in history]
        
        # Sarvam AI requirement: First message after system MUST be 'user'.
        while len(raw_messages) > 1 and raw_messages[1]["role"] == "assistant":
            raw_messages.pop(1)

        messages = self._merge_consecutive_roles(raw_messages)

        log.info(f"Chat message for user={user_id}, lang={language}")

        # Stream + collect response
        full_response = []
        
        from app.core import llm_config
        async for token in self.provider.stream(messages, language=language, config=llm_config.CAREER_CHAT):
            full_response.append(token)
            yield token

        # Save assistant response
        if full_response:
            await self.repo.add_message(user_id, "assistant", "".join(full_response), language)

    async def get_history(self, user_id: str) -> list[dict]:
        return await self.repo.get_history(user_id, limit=50)

    async def clear_history(self, user_id: str):
        await self.repo.clear_history(user_id)
