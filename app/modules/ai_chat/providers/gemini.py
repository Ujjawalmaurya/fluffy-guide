# [AI_GEMINI] Gemini provider with local Ollama fallback
# Primary: Gemini Flash API (fast, structured generation)
# Fallback: Local Ollama (qwen2.5:1.5b) when quota exceeded or offline

import time
import json
import asyncio
import httpx
from typing import AsyncGenerator

try:
    import google.generativeai as genai
    from google.api_core import exceptions as google_exceptions
except ImportError:
    genai = None
    google_exceptions = None

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
        self.model_name = "gemini-3.5-flash-lite"
        self.max_retries = settings.gemini_max_retries
        self.rpm_limit = settings.gemini_rpm_limit
        self.call_timestamps = []

        if genai is None or not self.api_key:
            self.model = None
            logger.warning("[AI_GEMINI] Gemini API key missing or SDK not installed. Will use Ollama fallback.")
            return

        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"[AI_GEMINI] GeminiProvider initialized with model: {self.model_name}")
        except Exception as e:
            self.model = None
            logger.warning(f"[AI_GEMINI] Gemini init error: {e}. Will use Ollama fallback.")

    async def _rate_limit_check(self):
        """Local RPM limiter to prevent hitting API limits."""
        now = time.time()
        self.call_timestamps = [ts for ts in self.call_timestamps if now - ts < 60]

        if len(self.call_timestamps) >= self.rpm_limit:
            oldest = self.call_timestamps[0]
            sleep_seconds = 60 - (now - oldest)
            if sleep_seconds > 0:
                logger.warning(f"[AI_GEMINI] RPM limit approaching ({self.rpm_limit}). Waiting {sleep_seconds:.1f}s")
                await asyncio.sleep(sleep_seconds)

        self.call_timestamps.append(time.time())

    async def _fallback_to_ollama(self, messages: list[dict], **kwargs) -> str:
        """Seamless fallback to local Ollama instance when Gemini fails or hits quota."""
        base_url = settings.ollama_base_url
        model = settings.ollama_model
        try:
            logger.info(f"[AI_FALLBACK] Calling local Ollama ({model}) at {base_url}...")
            async with httpx.AsyncClient(timeout=45.0) as client:
                res = await client.post(
                    f"{base_url}/v1/chat/completions",
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": kwargs.get("temperature", 0.2),
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    content = data["choices"][0]["message"]["content"]
                    logger.info("[AI_FALLBACK] Local Ollama responded successfully.")
                    return content
                else:
                    logger.warning(f"[AI_FALLBACK] Ollama returned status {res.status_code}: {res.text[:100]}")
        except Exception as err:
            logger.warning(f"[AI_FALLBACK] Ollama connection failed: {err}")

        raise GeminiRateLimit()

    async def _stream_fallback_to_ollama(self, messages: list[dict]) -> AsyncGenerator[str, None]:
        """Seamless stream fallback to local Ollama instance."""
        base_url = settings.ollama_base_url
        model = settings.ollama_model
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                async with client.stream(
                    "POST",
                    f"{base_url}/v1/chat/completions",
                    json={"model": model, "messages": messages, "stream": True}
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            chunk_data = line[6:].strip()
                            if chunk_data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(chunk_data)
                                text = chunk["choices"][0]["delta"].get("content", "")
                                if text:
                                    yield text
                            except Exception:
                                continue
        except Exception as e:
            logger.error(f"[AI_FALLBACK] Ollama stream failed: {e}")

    async def _build_model_with_name(self, model_name: str, system_instruction: str | None = None):
        """Internal helper to build model with specific name and instruction."""
        if genai is None or not self.api_key:
            return None
        try:
            return genai.GenerativeModel(model_name=model_name, system_instruction=system_instruction)
        except Exception:
            return None

    async def complete(self, messages: list[dict], language: str = "en", model_name: str | None = None, **kwargs) -> str:
        """Generate a response from Gemini, with automatic local Ollama fallback."""
        if not self.model or genai is None:
            return await self._fallback_to_ollama(messages, **kwargs)

        await self._rate_limit_check()

        system_msg = next((m["content"] for m in messages if m["role"] == "system"), None)
        chat_msgs = [m for m in messages if m["role"] != "system"]

        contents = []
        for msg in chat_msgs:
            role = "model" if msg.get("role") == "assistant" else "user"
            contents.append({"role": role, "parts": [msg.get("content", "")]})

        if not contents:
            contents.append({"role": "user", "parts": ["Please proceed based on the system instructions."]})

        target_model = model_name or self.model_name
        model = await self._build_model_with_name(target_model, system_msg)
        if model is None:
            return await self._fallback_to_ollama(messages, **kwargs)

        try:
            response = await model.generate_content_async(contents)
            if response and getattr(response, "text", None):
                return response.text
        except Exception as e:
            err_name = type(e).__name__
            logger.warning(f"[AI_GEMINI] Gemini call failed ({err_name}: {e}). Triggering Ollama fallback.")
            return await self._fallback_to_ollama(messages, **kwargs)

        return await self._fallback_to_ollama(messages, **kwargs)

    async def stream(self, messages: list[dict], language: str = "en", model_name: str | None = None) -> AsyncGenerator[str, None]:
        """Stream response from Gemini with local Ollama fallback."""
        if not self.model or genai is None:
            async for chunk in self._stream_fallback_to_ollama(messages):
                yield chunk
            return

        await self._rate_limit_check()

        system_msg = next((m["content"] for m in messages if m["role"] == "system"), None)
        chat_msgs = [m for m in messages if m["role"] != "system"]

        contents = []
        for msg in chat_msgs:
            role = "model" if msg.get("role") == "assistant" else "user"
            contents.append({"role": role, "parts": [msg.get("content", "")]})

        if not contents:
            contents.append({"role": "user", "parts": ["Please proceed."]})

        target_model = model_name or self.model_name
        model = await self._build_model_with_name(target_model, system_msg)
        if model is None:
            async for chunk in self._stream_fallback_to_ollama(messages):
                yield chunk
            return

        try:
            async for chunk in await model.generate_content_async(contents, stream=True):
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.warning(f"[AI_GEMINI] Gemini stream failed: {e}. Switching to Ollama stream.")
            async for chunk in self._stream_fallback_to_ollama(messages):
                yield chunk

    async def is_available(self) -> bool:
        """Check if Gemini or local Ollama is available."""
        if self.model is not None:
            try:
                await self.model.generate_content_async("Say OK")
                return True
            except Exception:
                pass

        # Check local Ollama health
        try:
            import httpx
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{settings.ollama_base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False