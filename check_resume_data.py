import asyncio
from app.core.database import get_supabase

async def check_data():
    db = get_supabase()
    user_id = '39b02cdc-616b-4c85-90f5-f1be73b3aa41'
    
    # Check if any analysis exists
    res = db.table("resume_analysis").select("id, created_at").eq("user_id", user_id).execute()
    print(f"ANAYLYSIS_COUNT: {len(res.data)}")
    if res.data:
        print("Latest analysis found.")
    else:
        print("No analysis found for this user.")

if __name__ == "__main__":
    asyncio.run(check_data())
