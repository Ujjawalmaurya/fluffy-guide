import asyncio
import json
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        # Request OTP
        await client.post("http://localhost:8000/auth/request-otp", json={"email": "vivek4129yadav@gmail.com"})
        
        # Verify OTP (assumes 123456 is generic test OTP or check db)
        # We need to get the real OTP from the DB
        pass

if __name__ == "__main__":
    asyncio.run(main())
