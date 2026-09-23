import json
import httpx
from typing import AsyncGenerator, Optional
from loguru import logger

from app.core.config import settings
from app.modules.ai_chat.providers.base import ILLMProvider

_ollama_instance = None


def get_ollama_instance() -> "OllamaProvider":
    global _ollama_instance
    if _ollama_instance is None:
        _ollama_instance = OllamaProvider()
    return _ollama_instance


class OllamaProvider(ILLMProvider):
    """
    High-performance local LLM provider powered by Ollama.
    Supports high context windows (32k-128k), streaming SSE, and structured JSON parsing.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        context_length: Optional[int] = None,
    ):
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.ollama_model
        self.context_length = context_length or getattr(settings, "ollama_context_length", 32768)

    async def is_available(self) -> bool:
        """Check if local Ollama daemon is reachable."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    async def complete(self, messages: list[dict], language: str = "en", **kwargs) -> str:
        """Execute non-streaming completion with high context window."""
        temperature = kwargs.get("temperature", 0.3)
        max_tokens = kwargs.get("max_tokens", 2048)

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_ctx": self.context_length,
                "num_predict": max_tokens,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                res = await client.post(f"{self.base_url}/api/chat", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    content = data.get("message", {}).get("content", "")
                    return content.strip()
                logger.error(f"[OLLAMA] Completion error: {res.status_code} - {res.text[:120]}")
        except Exception as e:
            logger.error(f"[OLLAMA] Request failed: {e}")

        raise RuntimeError(f"Local Ollama ({self.model}) execution failed")

    async def complete_json(self, messages: list[dict], **kwargs) -> dict:
        """Execute completion and parse JSON output, handling markdown fences and retrying if necessary."""
        raw = await self.complete(messages, **kwargs)
        clean = raw.strip()
        if clean.startswith("```"):
            lines = clean.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            clean = "\n".join(lines).strip()

        # Isolate bounding brackets if surrounded by conversational prose
        first_bracket = min(
            (idx for idx in [clean.find("{"), clean.find("[")] if idx != -1),
            default=-1,
        )
        last_bracket = max(clean.rfind("}"), clean.rfind("]"))
        if first_bracket != -1 and last_bracket > first_bracket:
            clean = clean[first_bracket : last_bracket + 1]

        return json.loads(clean)

    async def stream(self, messages: list[dict], language: str = "en") -> AsyncGenerator[str, None]:
        """Yield response tokens one at a time for fast SSE streaming."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": 0.5,
                "num_ctx": self.context_length,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as response:
                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        try:
                            chunk = json.loads(line)
                            content = chunk.get("message", {}).get("content", "")
                            if content:
                                yield content
                            if chunk.get("done", False):
                                break
                        except Exception:
                            continue
        except Exception as e:
            logger.error(f"[OLLAMA] Stream interrupted: {e}")
            yield " [Response interrupted due to local model timeout]"
