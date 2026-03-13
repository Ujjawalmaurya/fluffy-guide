import asyncio
from app.modules.ai_chat.providers.openai_provider import get_openai_instance

async def check():
    openai = get_openai_instance()
    # Mock some messages
    messages = [{"role": "user", "content": "Say hello"}]
    try:
        res = await openai.complete(messages)
        print(f"OpenAI Response: {res}")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(check())
