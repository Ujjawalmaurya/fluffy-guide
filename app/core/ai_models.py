"""
Centralized AI model names to avoid hardcoded strings across the codebase.
"""

class AIModel:
    # OpenAI
    GPT_4O_MINI = "gpt-4o-mini"
    
    # Gemini
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    
    # Groq / Llama
    LLAMA_3_3_70B = "llama-3.3-70b-versatile"
    LLAMA_3_1_8B = "llama-3.1-8b-instant"
    
    # SarvamAI
    SARVAM_DEFAULT = "sarvam-m"
    
    # Aliases from 2.md
    GROQ_FAST = LLAMA_3_1_8B
    GEMINI_FLASH_LITE = "gemini-2.0-flash-lite-preview-02-05" # Latest flash-lite
    GEMINI_PRO = "gemini-1.5-pro"
    GEMINI_FLASH = "gemini-1.5-flash"

def get_embedding_model():
    """
    Returns a SentenceTransformer model for local embedding generation.
    Used for career identity and job matching (384-dim).
    """
    from sentence_transformers import SentenceTransformer
    # We use a singleton-like pattern via lru_cache or just a global
    if not hasattr(get_embedding_model, "_model"):
        get_embedding_model._model = SentenceTransformer('all-MiniLM-L6-v2')
    return get_embedding_model._model
