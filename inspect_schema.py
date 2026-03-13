import asyncio
from app.core.database import get_supabase

async def inspect():
    db = get_supabase()
    # Get a single row to see columns and example data
    res = db.table("job_listings").select("*").limit(1).execute()
    if res.data:
        print("COLUMNS:")
        for k, v in res.data[0].items():
            print(f"{k}: {type(v).__name__} (Example: {v})")
    else:
        print("No jobs found to inspect.")

if __name__ == "__main__":
    asyncio.run(inspect())
