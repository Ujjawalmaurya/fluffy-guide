# [AI_OPENAI] OpenAI gpt-4o-mini provider.
# Used for: adaptive assessment question generation ONLY.
# Never used for: resume parsing or gap analysis (that is Gemini).

import time
import asyncio
from openai import AsyncOpenAI, RateLimitError, AuthenticationError
from loguru import logger

from app.core.config import settings
from app.modules.ai_chat.providers.base import ILLMProvider
from app.shared.exceptions import AppError

_openai_instance = None


def get_openai_instance():
    """Returns a global singleton instance of OpenAIProvider."""
    global _openai_instance
    if _openai_instance is None:
        _openai_instance = OpenAIProvider()
    return _openai_instance

class OpenAIRateLimitError(AppError):
    def __init__(self):
        super().__init__(
            status_code=429,
            error_code="OPENAI_RATE_LIMIT",
            message="Your assessment is paused briefly. Resuming automatically..."
        )

class OpenAIQuotaExceededError(AppError):
    def __init__(self):
        super().__init__(
            status_code=503,
            error_code="OPENAI_QUOTA_EXCEEDED",
            message="Assessment service is temporarily unavailable. Please try again in a few hours."
        )

class OpenAIProvider(ILLMProvider):
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model
        self.max_retries = settings.openai_max_retries
        self.rpm_limit = settings.openai_rpm_limit
        self.call_timestamps = []
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        logger.info(f"[AI_OPENAI] [INFO] OpenAIProvider initialized. model={self.model}")

    async def _rate_limit_check(self):
        now = time.time()
        self.call_timestamps = [ts for ts in self.call_timestamps if now - ts < 60]
        
        if len(self.call_timestamps) >= self.rpm_limit:
            oldest_timestamp = self.call_timestamps[0]
            sleep_seconds = 60 - (now - oldest_timestamp)
            if sleep_seconds > 0:
                logger.warning(f"[AI_OPENAI] [WARNING] RPM limit ({self.rpm_limit}). Waiting {sleep_seconds:.1f}s")
                await asyncio.sleep(sleep_seconds)
                
        self.call_timestamps.append(time.time())

    async def complete(self, messages: list[dict], language: str = "en", **kwargs) -> str:
        # Prompt definition specifically asked for `language` in ILLMProvider but `max_tokens: int = 300` in OpenAIProvider complete signature.
        # We will keep the kwargs from the instruction though ILLMProvider defines something else.
        max_tokens = kwargs.get("max_tokens", 300)
        
        await self._rate_limit_check()
        
        backoff_times = [2, 4, 8]
        
        for attempt in range(1, self.max_retries + 1):
            logger.info(f"[AI_OPENAI] [INFO] API call #{attempt} this minute")
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
                
            except RateLimitError as e:
                # Check for quota
                err_msg = str(e).lower()
                if "insufficient_quota" in err_msg:
                    raise OpenAIQuotaExceededError()
                    
                logger.warning(f"[AI_OPENAI] [WARNING] Rate limited on attempt {attempt}")
                if attempt <= self.max_retries:
                    wait_time = backoff_times[attempt - 1] if attempt <= len(backoff_times) else 8
                    await asyncio.sleep(wait_time)
                continue
                
            except AuthenticationError:
                logger.error("[AI_OPENAI] [ERROR] Invalid API key")
                raise # Raise immediately
                
        raise OpenAIRateLimitError()

    async def stream(self, messages: list[dict], language: str = "en"):
        res = await self.complete(messages, language)
        yield res

    async def is_available(self) -> bool:
        try:
            await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Say OK"}],
                max_tokens=5
            )
            logger.info(f"[AI_OPENAI] [INFO] Availability check: True")
            return True
        except Exception:
            logger.info(f"[AI_OPENAI] [INFO] Availability check: False")
            return False
