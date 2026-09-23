from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict
from app.modules.ai_chat.providers.ollama_provider import get_ollama_instance
from app.core.logger import get_logger

router = APIRouter(prefix="/api/translate", tags=["Translate"])
log = get_logger("TRANSLATE")

translation_cache: Dict[str, str] = {}


class TranslateRequest(BaseModel):
    text: str
    target_lang: str = "hi"


class TranslateResponse(BaseModel):
    translated_text: str
    source_lang: str = "en"
    target_lang: str


@router.post("", response_model=TranslateResponse)
async def translate_text(request: TranslateRequest):
    """Translates text using local Ollama model."""
    cache_key = f"{request.target_lang}:{request.text}"
    if cache_key in translation_cache:
        return TranslateResponse(
            translated_text=translation_cache[cache_key],
            target_lang=request.target_lang
        )

    target_lang_name = "Hindi" if request.target_lang == "hi" else "English"
    prompt = (
        f"Translate the following text into natural, fluent {target_lang_name}. "
        f"Return ONLY the translation without any notes, preamble, or quotes.\n\n"
        f"Text:\n{request.text}"
    )

    try:
        ollama = get_ollama_instance()
        translated = await ollama.complete([{"role": "user", "content": prompt}], temperature=0.1, max_tokens=500)
        translated_clean = translated.strip().strip('"').strip("'")
        translation_cache[cache_key] = translated_clean
        return TranslateResponse(
            translated_text=translated_clean,
            target_lang=request.target_lang
        )
    except Exception as e:
        log.error(f"Local translation exception: {e}")
        return TranslateResponse(
            translated_text=request.text,
            target_lang=request.target_lang
        )
