"""
router.py — Translation API endpoint.
Prefix: /api/translate (mounted under /api/v1 in main.py)
"""
from fastapi import APIRouter
from app.modules.translate.schemas import TranslateRequest, TranslateResponse
from app.modules.translate.service import TranslateService

router = APIRouter(prefix="/api/translate", tags=["Translate"])
service = TranslateService()


@router.post("", response_model=TranslateResponse)
async def translate_text(request: TranslateRequest):
    """Translates text using local Ollama model."""
    translated = await service.translate(request.text, request.target_lang)
    return TranslateResponse(
        translated_text=translated,
        target_lang=request.target_lang,
    )
