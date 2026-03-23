"""
CareerIdentityService — The engine that understands who the user is.
1. Generates a 'Career Identity' (persona) from skills, experiences, and intents.
2. Converts that identity into a vector embedding for fast matching.
"""
import asyncio
from typing import List, Optional
import groq

from app.core.config import settings
from app.core.logger import get_logger
from app.core.database import get_supabase

log = get_logger("CAREER_IDENTITY")

class CareerIdentityService:
    def __init__(self):
        # Lazy-loaded — do NOT import/instantiate at module level to avoid
        # loading the 90MB model on every uvicorn hot-reload.
        self._encoder = None
        self._groq = None
        self.model = settings.groq_model

    def _get_encoder(self):
        """Lazily load SentenceTransformer only when first needed."""
        if self._encoder is None:
            from sentence_transformers import SentenceTransformer
            log.info("Loading SentenceTransformer model (first use)...")
            self._encoder = SentenceTransformer('all-MiniLM-L6-v2')
        return self._encoder

    def _get_groq(self):
        """Lazily initialise Groq client."""
        if self._groq is None:
            self._groq = groq.Groq(api_key=settings.groq_api_key)
        return self._groq

    def build_career_identity(self, skills: List[str], experience: str, intent: str) -> str:
        """
        Uses Llama-3-70B on Groq to synthesize a professional persona.
        This provides context that raw keywords lack.
        """
        prompt = f"""
        Represent this professional based on:
        Skills: {", ".join(skills)}
        Experience: {experience}
        Career Goal: {intent}
        
        Create a 2-3 sentence 'Career Identity' that captures their core expertise and trajectory.
        Focus on their suitability for the Indian job market. 
        Don't use corporate fluff—be direct and specific.
        """
        
        try:
            res = self._get_groq().chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            identity = res.choices[0].message.content.strip()
            log.info(f"Generated identity: {identity[:50]}...")
            return identity
        except Exception as e:
            log.error(f"Groq generation failed: {e}")
            # Fallback to simple concatenation if LLM fails
            return f"Professional skilled in {', '.join(skills[:5])} with experience in {experience}. Goal: {intent}"

    def embed_text(self, text: str) -> List[float]:
        """Converts text to vector using local SentenceTransformer."""
        embedding = self._get_encoder().encode(text).tolist()
        return embedding

    async def update_user_identity(self, user_id: str, skills: List[str], experience: str, intent: str):
        """Orchestrates generation, embedding, and saving to Supabase."""
        identity = self.build_career_identity(skills, experience, intent)
        vector = self.embed_text(identity)
        
        db = get_supabase()
        res = db.table("user_profiles").update({
            "career_identity": identity,
            "identity_embedding": vector
        }).eq("user_id", user_id).execute()
        
        if res.data:
            log.info(f"Updated career identity for user {user_id}")
        else:
            log.error(f"Failed to update user {user_id}: {res}")

# Lazy singleton — instantiated here but model loads only on first use
career_identity_service = CareerIdentityService()
