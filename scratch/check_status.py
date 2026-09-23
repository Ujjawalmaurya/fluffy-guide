import asyncio
from app.core.database import get_supabase

async def check():
    db = get_supabase()
    user_id = '39b02cdc-616b-4c85-90f5-f1be73b3aa41'
    
    res = db.table("questionnaire_sessions").select("id, is_complete").eq("user_id", user_id).execute()
    print(f"SESSION_COUNT: {len(res.data)}")
    for s in res.data:
        print(f"Session {s['id']}: is_complete={s['is_complete']}")

if __name__ == "__main__":
    asyncio.run(check())
