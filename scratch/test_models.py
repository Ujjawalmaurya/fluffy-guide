import asyncio
import json
import sys
import os

# Add backend to sys.path
sys.path.append("/home/um/Stuffs/SANKALP/backend")

from app.modules.ai_chat.providers.ollama_provider import OllamaProvider
from app.core import llm_config

async def test_models():
    provider = OllamaProvider()
    
    # Mock assessment prompt
    system_prompt = """
You are a skilled career counsellor. Return ONLY this JSON:
{
  "question": "What is your current job?",
  "question_type": "text",
  "options": null,
  "phase": 1,
  "phase_name": "Current Situation",
  "skill_probing": "current_role"
}
Return ONLY raw JSON. No markdown.
"""
    messages = [{"role": "system", "content": system_prompt}]
    
    for model in ["qwen3:4b", "phi4-mini"]:
        print(f"\n--- Testing model: {model} ---")
        try:
            # We use complete directly to see what it returns without the JSON wrapper logic
            response = await provider.complete(messages=messages, model=model, temperature=0.1)
            print(f"Response: '{response}'")
            if not response.strip():
                print("WARNING: EMPTY RESPONSE")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_models())
