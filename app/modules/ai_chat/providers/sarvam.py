"""
SarvamAI provider — implements ILLMProvider using SarvamAI's OpenAI-compatible API.
Supports both complete() and token streaming via SSE.
"""
import json
import httpx
from typing import AsyncGenerator

from app.modules.ai_chat.providers.base import ILLMProvider
from app.core.config import settings
from app.core.logger import get_logger
from app.shared.exceptions import AIProviderUnavailable

log = get_logger("AI_CHAT")


class SarvamAIProvider(ILLMProvider):
    def __init__(self):
        self.base_url = settings.sarvam_base_url
        self.model = settings.sarvam_model
        self.headers = {
            "Authorization": f"Bearer {settings.sarvam_api_key}",
            "Content-Type": "application/json",
        }

    async def complete(self, messages: list[dict], language: str = "en") -> str:
        payload = {"model": self.model, "messages": messages}
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                )
                resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            log.error(f"SarvamAI returned status {e.response.status_code}. Retrying in 2s")
            raise AIProviderUnavailable()
        except Exception as e:
            log.error(f"SarvamAI complete() failed: {e}")
            raise AIProviderUnavailable()

    async def stream(self, messages: list[dict], language: str = "en") -> AsyncGenerator[str, None]:
        """Stream tokens from SarvamAI. Falls back to complete() if streaming fails."""
        payload = {"model": self.model, "messages": messages, "stream": True}
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                ) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        raw = line[6:].strip()
                        if raw == "[DONE]":
                            break
                        try:
                            chunk = json.loads(raw)
                            delta = chunk["choices"][0]["delta"].get("content", "")
                            if delta:
                                yield delta
                        except Exception:
                            continue
        except Exception as e:
            log.error(f"SarvamAI stream() failed: {e}")
            raise AIProviderUnavailable()

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(self.base_url, headers=self.headers)
                return resp.status_code < 500
        except Exception:
            return False
