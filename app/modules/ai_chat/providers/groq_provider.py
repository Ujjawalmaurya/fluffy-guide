try:
    import groq
except ImportError:
    groq = None

from typing import AsyncGenerator
from loguru import logger
from app.core.config import settings
from app.modules.ai_chat.providers.base import ILLMProvider
from app.shared.exceptions import AppError

class GroqProvider(ILLMProvider):
    def __init__(self):
        self.api_key = settings.groq_api_key
        self.model_name = settings.groq_model
        if groq is not None and self.api_key:
            self._client = groq.Groq(api_key=self.api_key)
        else:
            self._client = None
            logger.warning("[AI_GROQ] GroqProvider not initialized (missing groq library or api_key)")

    async def complete(self, messages: list[dict], language: str = "en", model_name: str | None = None, **kwargs) -> str:
        if not self._client:
            raise AppError("GROQ_NOT_CONFIGURED", "Groq AI client is not available or groq is not installed.")
        target_model = model_name or self.model_name
        try:
            # Groq's SDK is synchronous, but we can wrap it or just use it as is if it's fast.
            # For consistency with the async ILLMProvider, we use it in a thread or just call it.
            # Here we just call it since Groq is extremely low latency.
            res = self._client.chat.completions.create(
                model=target_model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.1),
                max_tokens=kwargs.get("max_tokens", 1024)
            )
            return res.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"[AI_GROQ] Groq completion failed: {e}")
            raise AppError("GROQ_FAILED", "Groq AI service encountered an error.")

    async def stream(self, messages: list[dict], language: str = "en", model_name: str | None = None) -> AsyncGenerator[str, None]:
        if not self._client:
            raise AppError("GROQ_NOT_CONFIGURED", "Groq AI client is not available or groq is not installed.")
        target_model = model_name or self.model_name
        try:
            stream = self._client.chat.completions.create(
                model=target_model,
                messages=messages,
                stream=True
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            logger.error(f"[AI_GROQ] Groq streaming failed: {e}")
            raise AppError("GROQ_FAILED", "Groq AI service encountered an error during streaming.")

    async def is_available(self) -> bool:
        return bool(self.api_key)
