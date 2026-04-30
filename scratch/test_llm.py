
import asyncio
import sys
import os

# Add backend to path
sys.path.append("/home/um/Stuffs/SANKALP/backend")

from app.modules.ai_chat.providers.ollama_provider import get_ollama_instance
from app.core import llm_config

async def test():
    provider = get_ollama_instance()
    messages = [{"role": "user", "content": "Return a JSON with key 'test' and value 1."}]
    
    print(f"RESUME_PARSE model: {llm_config.RESUME_PARSE.model}")
    print(f"EXTRACTION_MODEL: {llm_config.EXTRACTION_MODEL}")
    
    try:
        # We don't need real Ollama to test the model selection logic in logs
        # but let's see what happens.
        result = await provider.complete_json(
            messages=messages,
            config=llm_config.RESUME_PARSE
        )
        print(f"Result: {result}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test())
