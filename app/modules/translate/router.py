from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
from typing import Dict
from app.core.config import settings
from app.core.logger import get_logger

router = APIRouter(prefix="/api/translate", tags=["Translate"])
log = get_logger("TRANSLATE")

# Simple in-memory cache to avoid duplicate API calls
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
    """
    Translates text using SarvamAI. 
    Supported target_lang: "hi" (Hindi), "en" (English)
    """
    cache_key = f"{request.target_lang}:{request.text}"
    if cache_key in translation_cache:
        return TranslateResponse(
            translated_text=translation_cache[cache_key],
            target_lang=request.target_lang
        )

    if not settings.sarvam_api_key:
        # Fallback if API key is missing
        return TranslateResponse(
            translated_text=f"[HI] {request.text}",
            target_lang=request.target_lang
        )

    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "input": request.text,
                "source_language_code": "en-IN" if request.target_lang == "hi" else "hi-IN",
                "target_language_code": "hi-IN" if request.target_lang == "hi" else "en-IN",
                "speaker_gender": "Female",
                "mode": "formal",
                "model": settings.sarvam_model
            }
            
            headers = {"api-subscription-key": settings.sarvam_api_key}
            
            response = await client.post(
                f"{settings.sarvam_base_url}/translate",
                json=payload,
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code != 200:
                log.error(f"SarvamAI Error: {response.text}")
                raise HTTPException(status_code=500, detail="Translation failed")
            
            data = response.json()
            translated_text = data.get("translated_text", "")
            
            # Cache the result
            translation_cache[cache_key] = translated_text
            
            return TranslateResponse(
                translated_text=translated_text,
                target_lang=request.target_lang
            )
            
    except Exception as e:
        log.error(f"Translation exception: {str(e)}")
        # Graceful degradation: return original text if translation fails
        return TranslateResponse(
            translated_text=request.text,
            target_lang=request.target_lang
        )
