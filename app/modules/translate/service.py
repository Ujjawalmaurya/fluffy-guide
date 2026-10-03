"""
service.py — Text translation using local Ollama model with in-memory caching.
"""
from typing import Dict
from loguru import logger
from app.modules.ai_chat.providers.ollama_provider import get_ollama_instance

_translation_cache: Dict[str, str] = {}


class TranslateService:
    def __init__(self):
        self.ollama = get_ollama_instance()

    async def translate(self, text: str, target_lang: str = "hi") -> str:
        """Translates text into target language (default Hindi) with cache lookups."""
        cache_key = f"{target_lang}:{text}"
        if cache_key in _translation_cache:
            return _translation_cache[cache_key]

        target_lang_name = "Hindi" if target_lang == "hi" else "English"
        prompt = (
            f"Translate the following text into natural, fluent {target_lang_name}. "
            f"Return ONLY the translation without any notes, preamble, or quotes.\n\n"
            f"Text:\n{text}"
        )

        try:
            translated = await self.ollama.complete(
                [{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500,
            )
            clean_translated = translated.strip().strip('"').strip("'")
            _translation_cache[cache_key] = clean_translated
            return clean_translated
        except Exception as e:
            logger.error(f"[TRANSLATE] Local translation error: {e}")
            return text
