# [AI_GEMINI] Gemini provider
# Used for: resume parsing, gap analysis, roadmap generation

import time
import asyncio
import google.generativeai as genai
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

    async def complete(self, messages: list[dict], language: str = "en", **kwargs) -> str:
        """Generate a response from Gemini."""

        await self._rate_limit_check()

        # Convert OpenAI-style messages to Gemini format
        if isinstance(messages, str):
            contents = messages
        else:
            contents = []

            for msg in messages:
                role = "model" if msg.get("role") == "assistant" else "user"

                contents.append({
                    "role": role,
                    "parts": [msg.get("content", "")]
                })

        for attempt in range(1, self.max_retries + 1):

            try:

                response = await self.model.generate_content_async(contents)

                # Validate response
                if not response or not getattr(response, "text", None):

                    logger.error("[AI_GEMINI] Empty response from Gemini")

                    raise AppError(
                        "GEMINI_EMPTY_RESPONSE",
                        "Gemini returned an empty response"
                    )

                return response.text

            # Gemini rate limit handling
            except google_exceptions.ResourceExhausted:

                if attempt < self.max_retries:

                    wait = 2 ** attempt

                    logger.warning(
                        f"[AI_GEMINI] Rate limited (attempt {attempt}/{self.max_retries}). Waiting {wait}s"
                    )

                    await asyncio.sleep(wait)

                else:

                    logger.error("[AI_GEMINI] Rate limit retries exhausted")

                    raise GeminiRateLimit()

            # Model not found
            except google_exceptions.NotFound:

                logger.error(
                    f"[AI_GEMINI] Model not found: {self.model_name}"
                )

                raise AppError(
                    "GEMINI_MODEL_NOT_FOUND",
                    f"Gemini model '{self.model_name}' is not available."
                )

            # Unexpected errors
            except Exception as e:

                logger.error(
                    f"[AI_GEMINI] Unexpected error: {str(e)[:200]}"
                )

                raise

    async def stream(self, messages: list[dict], language: str = "en"):
        """Streaming wrapper (simple implementation)."""
        result = await self.complete(messages, language)
        yield result

    async def is_available(self) -> bool:
        """Check if Gemini API is available."""

        try:

            await self.model.generate_content_async("Say OK")

            logger.info("[AI_GEMINI] Availability check: True")

            return True

        except Exception:

            logger.warning("[AI_GEMINI] Availability check: False")

            return False