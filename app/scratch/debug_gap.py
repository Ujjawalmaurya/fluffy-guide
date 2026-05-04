import asyncio
import os
import sys
from dotenv import load_dotenv

# Load env before other imports
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env")))

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.modules.gap_analysis import gap_engine, service, repository
from app.core.database import get_supabase
from app.core.config import settings

async def debug():
    user_id = "a2972993-e783-466b-8d28-c2c58c278fd5"
    print(f"--- Debugging Gap Analysis for {user_id} ---")
    
    db = get_supabase()
    
    # Check jobs
    jobs = db.table("job_listings").select("*").eq("is_active", True).execute()
    print(f"Total active jobs in DB: {len(jobs.data)}")
    
    # Check user profiles
    profile = db.table("user_profiles").select("*").eq("user_id", user_id).execute()
    print(f"User profile exists: {len(profile.data) > 0}")
    if profile.data:
        print(f"State: {profile.data[0].get('state')}")
        
    # Check user skills
    skills = db.table("user_skill_profiles").select("*").eq("user_id", user_id).execute()
    print(f"User skills exist: {len(skills.data) > 0}")
    
    # Run gap computation
    print("\nRunning gap_engine.compute_gap...")
    res = await gap_engine.compute_gap(user_id)
    print(f"Total jobs analyzed by engine: {res['total_jobs_analyzed']}")
    print(f"Gaps found: {len(res['gaps'])}")
    for g in res['gaps'][:5]:
        print(f"  - Gap: {g['skill_name']} (score: {g['priority_score']})")
    print(f"Strengths found: {len(res['strengths'])}")
    for s in res['strengths']:
        print(f"  - Strength: {s['skill_name']}")
    
    # Check if anything is returned
    if res['total_jobs_analyzed'] == 0:
        print("\nWARNING: Engine returned 0 jobs. Let's see why.")
        # Re-run logic inside compute_gap manually
        state = profile.data[0].get('state') if profile.data else None
        
        # Check specific query
        q = db.table("job_listings").select("id").eq("is_active", True)
        if state:
            q = q.eq("location_state", state)
        r = q.execute()
        print(f"Jobs in {state}: {len(r.data)}")

if __name__ == "__main__":
    asyncio.run(debug())
