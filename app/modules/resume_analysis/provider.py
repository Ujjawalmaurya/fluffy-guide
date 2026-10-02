"""
provider.py — Active LLM provider resolution for resume analysis.
Prioritizes high-speed Gemini Flash Lite; falls back to local Ollama.
"""
from typing import Optional
from loguru import logger


async def get_active_provider():
    """Returns high-speed Gemini Flash Lite provider when configured, or local Ollama fallback."""
    try:
        from app.core.config import settings
        if getattr(settings, "gemini_api_key", None):
            from app.modules.ai_chat.providers.gemini import get_gemini_instance
            gemini = get_gemini_instance()
            if gemini.model is not None:
                return gemini
    except Exception as e:
        logger.warning(f"[RESUME_ANALYSIS] Gemini provider check failed: {e}")

    try:
        from app.modules.ai_chat.providers.ollama_provider import get_ollama_instance
        ollama = get_ollama_instance()
        if await ollama.is_available():
            return ollama
    except Exception as e:
        logger.warning(f"[RESUME_ANALYSIS] Ollama provider check failed: {e}")

    return None
