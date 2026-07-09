"""
ICompletionProvider & IStructuredProvider — abstract capability interfaces for LLM providers.
Interface Segregation: separate completion and structured extraction.
"""
from abc import ABC, abstractmethod
from typing import AsyncGenerator


from typing import AsyncIterator

class ICompletionProvider(ABC):
    @abstractmethod
    async def complete(self, prompt: str | list[dict], system_prompt: str = None, **kwargs) -> str:
        """Return full response as a string."""

    @abstractmethod
    async def stream(self, prompt: str | list[dict], system_prompt: str = None, **kwargs) -> AsyncIterator[str]:
        """Yield response tokens one at a time."""

    @abstractmethod
    async def is_available(self) -> bool:
        """Quick health check — True if API is reachable."""


class IStructuredProvider(ABC):
    @abstractmethod
    async def complete_json(self, prompt: str | list[dict] = None, schema = None, system_prompt: str = None, **kwargs) -> dict:
        """Return schema-validated JSON output."""

    @abstractmethod
    async def is_available(self) -> bool:
        """Quick health check — True if API is reachable."""

