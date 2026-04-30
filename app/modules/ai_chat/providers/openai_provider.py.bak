# [AI_OPENAI] OpenAI provider implementation
# Used for: Career Skill Assessment

import time
import asyncio
from typing import AsyncGenerator
from openai import AsyncOpenAI
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

class OpenAIProvider(ILLMProvider):
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.model_name = settings.openai_model or "gpt-4o-mini"
        self.max_retries = settings.openai_max_retries
        self.rpm_limit = settings.openai_rpm_limit
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.call_timestamps = []

        logger.info(f"[AI_OPENAI] OpenAIProvider initialized with model: {self.model_name}")

    async def _rate_limit_check(self):
        """Simple RPM limiter."""
        now = time.time()
        self.call_timestamps = [ts for ts in self.call_timestamps if now - ts < 60]
        
        if len(self.call_timestamps) >= self.rpm_limit:
            oldest = self.call_timestamps[0]
            sleep_seconds = 60 - (now - oldest)
            if sleep_seconds > 0:
                logger.warning(f"[AI_OPENAI] RPM limit hit ({self.rpm_limit}). Waiting {sleep_seconds:.1f}s")
                await asyncio.sleep(sleep_seconds)
        
        self.call_timestamps.append(time.time())

    async def complete(self, messages: list[dict], language: str = "en", **kwargs) -> str:
        """Generate a response from OpenAI."""
        await self._rate_limit_check()
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"[AI_OPENAI] Completion failed: {str(e)}")
            raise AppError("OPENAI_ERROR", f"OpenAI call failed: {str(e)}")

    async def stream(self, messages: list[dict], language: str = "en") -> AsyncGenerator[str, None]:
        """Stream response from OpenAI."""
        await self._rate_limit_check()
        
        try:
            stream = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stream=True
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"[AI_OPENAI] Streaming failed: {str(e)}")
            raise AppError("OPENAI_STREAM_ERROR", f"OpenAI stream failed: {str(e)}")

    async def is_available(self) -> bool:
        """Health check."""
        try:
            # Quick cheap call to check connectivity
            await self.client.models.list()
            return True
        except Exception:
            return False
