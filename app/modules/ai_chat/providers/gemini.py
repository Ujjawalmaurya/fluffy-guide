# [AI_GEMINI] Gemini provider
# Used for: resume parsing, gap analysis, roadmap generation

import time
import asyncio
import google.generativeai as genai
from typing import AsyncGenerator
from google.api_core import exceptions as google_exceptions

from loguru import logger
from app.core.config import settings
from app.modules.ai_chat.providers.base import ILLMProvider
from app.shared.exceptions import AppError, GeminiRateLimit

_gemini_instance = None


def get_gemini_instance():
    """Returns a global singleton instance of GeminiProvider."""
    global _gemini_instance
    if _gemini_instance is None:
        _gemini_instance = GeminiProvider()
    return _gemini_instance


class GeminiProvider(ILLMProvider):

    def __init__(self):
        self.api_key = settings.gemini_api_key

        # Stable Gemini model alias
        self.model_name = "gemini-3-flash-preview"

        self.max_retries = settings.gemini_max_retries
        self.rpm_limit = settings.gemini_rpm_limit
        self.call_timestamps = []

        genai.configure(api_key=self.api_key)

        self.model = genai.GenerativeModel(self.model_name)

        logger.info(
            f"[AI_GEMINI] GeminiProvider initialized with model: {self.model_name}"
        )

    async def _rate_limit_check(self):
        """Local RPM limiter to prevent hitting API limits."""
        now = time.time()

        # Keep only last 60 seconds timestamps
        self.call_timestamps = [
            ts for ts in self.call_timestamps if now - ts < 60
        ]

        if len(self.call_timestamps) >= self.rpm_limit:

            oldest = self.call_timestamps[0]
            sleep_seconds = 60 - (now - oldest)

            if sleep_seconds > 0:
                logger.warning(
                    f"[AI_GEMINI] RPM limit approaching ({self.rpm_limit}). Waiting {sleep_seconds:.1f}s"
                )
                await asyncio.sleep(sleep_seconds)

        self.call_timestamps.append(time.time())


    async def _build_model(self, system_instruction: str | None = None):
        """Builds or re-builds the model instance if system instruction changes."""
        # Note: In production, we might want to cache models per instruction if they repeat
        return genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_instruction
        )

    async def complete(self, messages: list[dict], language: str = "en", **kwargs) -> str:
        """Generate a response from Gemini."""
        await self._rate_limit_check()

        system_msg = next((m["content"] for m in messages if m["role"] == "system"), None)
        chat_msgs = [m for m in messages if m["role"] != "system"]

        # Convert to Gemini format
        contents = []
        for msg in chat_msgs:
            role = "model" if msg.get("role") == "assistant" else "user"
            contents.append({"role": role, "parts": [msg.get("content", "")]})

        # Generate
        model = await self._build_model(system_msg)
        for attempt in range(1, self.max_retries + 1):
            try:
                response = await model.generate_content_async(contents)
                if not response or not getattr(response, "text", None):
                    raise AppError("GEMINI_EMPTY_RESPONSE", "Gemini returned an empty response")
                return response.text
            except google_exceptions.ResourceExhausted:
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise GeminiRateLimit()
            except Exception as e:
                logger.error(f"[AI_GEMINI] Error: {e}")
                raise

    async def stream(self, messages: list[dict], language: str = "en") -> AsyncGenerator[str, None]:
        """Real streaming from Gemini."""
        await self._rate_limit_check()

        system_msg = next((m["content"] for m in messages if m["role"] == "system"), None)
        chat_msgs = [m for m in messages if m["role"] != "system"]

        contents = []
        for msg in chat_msgs:
            role = "model" if msg.get("role") == "assistant" else "user"
            contents.append({"role": role, "parts": [msg.get("content", "")]})

        model = await self._build_model(system_msg)
        try:
            async for chunk in await model.generate_content_async(contents, stream=True):
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"[AI_GEMINI] Streaming error: {e}")
            raise

    async def is_available(self) -> bool:
        """Check if Gemini API is available."""

        try:

            await self.model.generate_content_async("Say OK")

            logger.info("[AI_GEMINI] Availability check: True")

            return True

        except Exception:

            logger.warning("[AI_GEMINI] Availability check: False")

            return False