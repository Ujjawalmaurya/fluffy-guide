import asyncio
from app.modules.onboarding.question_engine import generate_questions
async def main():
    try:
        res = await generate_questions("individual_youth", "UP", ["technology"], "en")
        print("SUCCESS", res)
    except Exception as e:
        print("ERROR", e)

asyncio.run(main())
