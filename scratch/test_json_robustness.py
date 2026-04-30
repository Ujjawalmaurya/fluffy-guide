import asyncio
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append("/home/um/Stuffs/SANKALP/backend")

from app.modules.ai_chat.providers.ollama_provider import OllamaProvider
from app.core.config import settings

async def test_json_extraction():
    provider = OllamaProvider()
    
    # Simple test case for structured output
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Return ONLY JSON."},
        {"role": "user", "content": "Generate a profile for a software engineer. Return a JSON with 'name', 'skills' (list), and 'experience_years' (int)."}
    ]
    
    print("Testing JSON extraction with qwen3:4b...")
    try:
        result = await provider.complete_json(
            messages=messages,
            model="qwen3:4b",
            task="test_extraction"
        )
        print("Result:", result)
    except Exception as e:
        print("Failed with qwen3:4b:", e)

    print("\nTesting JSON extraction with phi4-mini...")
    try:
        result = await provider.complete_json(
            messages=messages,
            model="phi4-mini",
            task="test_extraction"
        )
        print("Result:", result)
    except Exception as e:
        print("Failed with phi4-mini:", e)

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(test_json_extraction())
