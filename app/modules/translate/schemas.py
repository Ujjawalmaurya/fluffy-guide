"""
schemas.py — Request and response models for translation service.
"""
from pydantic import BaseModel


class TranslateRequest(BaseModel):
    text: str
    target_lang: str = "hi"


class TranslateResponse(BaseModel):
    translated_text: str
    source_lang: str = "en"
    target_lang: str
