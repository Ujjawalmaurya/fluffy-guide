import asyncio
from app.core.database import get_supabase
from app.modules.dashboard.repository import DashboardRepository

async def verify_matches():
    db = get_supabase()
    repo = DashboardRepository(db)
    
    # Mock user data
    skills = ["Flutter", "GenAI", "MVC", "Prompt Engineering", "Python"]
    interests = ["technology", "software development"]
    state = "Karnataka"
    
    matches = repo.get_job_matches(state, interests, user_skills=skills, limit=5)
    
    print("\nTOP MATCHES FOR TECH PROFILE:")
    for i, m in enumerate(matches):
        print(f"{i+1}. {m['title']} @ {m['company']} (Score: {m['match_score']})")
        print(f"   Skills: {m['required_skills']}")

if __name__ == "__main__":
    asyncio.run(verify_matches())
