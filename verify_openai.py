"""
verify_ollama.py (replaces verify_openai.py)
Run to confirm local Ollama LLMs are working.
Usage: python verify_openai.py
"""
import asyncio
from app.modules.ai_chat.providers.ollama_provider import get_ollama_instance
from app.core.llm_config import (
    PRIMARY_MODEL, EXTRACTION_MODEL,
    CAREER_CHAT, SKILL_EXTRACT
)

async def check():
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  SkillBridge AI — Ollama Verification")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    ollama = get_ollama_instance()

    print("1. Checking Ollama server...")
    health = await ollama.health_check()
    if health["status"] != "healthy":
        print(f"   ✗ Not reachable: {health.get('reason')}")
        print(f"   Fix: run 'ollama serve'")
        return
    print(f"   ✓ Running | models={health['models']}")

    print(f"\n2. Testing {PRIMARY_MODEL} (career chat)...")
    try:
        messages = [{"role": "user", "content": "In one line: what is SkillBridge AI?"}]
        res = await ollama.complete(messages, config=CAREER_CHAT)
        print(f"   ✓ {res[:100]}...")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        print(f"   Fix: ollama pull {PRIMARY_MODEL}")
        return

    print(f"\n3. Testing {EXTRACTION_MODEL} (JSON extraction)...")
    try:
        messages = [{"role": "user", "content": "Skills: Python, Excel. Return JSON: {\"skills\": [...]}"}]
        res = await ollama.complete(messages, config=SKILL_EXTRACT)
        print(f"   ✓ {res[:100]}...")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        print(f"   Fix: ollama pull {EXTRACTION_MODEL}")
        return

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  ✓ All checks passed. Ready.")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

if __name__ == "__main__":
    asyncio.run(check())
