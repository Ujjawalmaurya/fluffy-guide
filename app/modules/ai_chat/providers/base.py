"""
ILLMProvider — abstract interface for LLM providers.
Interface Segregation: only 3 methods. Swap providers without touching service.py.
"""
from abc import ABC, abstractmethod
from typing import AsyncGenerator


class ILLMProvider(ABC):
    @abstractmethod
    async def complete(self, messages: list[dict], language: str = "en") -> str:
        """Return full response as a string."""

    @abstractmethod
    async def stream(self, messages: list[dict], language: str = "en") -> AsyncGenerator[str, None]:
        """Yield response tokens one at a time."""

    @abstractmethod
    async def is_available(self) -> bool:
        """Quick health check — True if API is reachable."""
