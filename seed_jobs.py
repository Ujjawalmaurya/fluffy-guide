import asyncio
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL or SUPABASE_KEY not found in .env")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

JOBS = [
    # Technology - Maharashtra
    {
        "title": "Junior Python Developer",
        "company": "TechSol Mumbai",
        "description": "Looking for a Python developer with knowledge of Django and SQL.",
        "location_state": "Maharashtra",
        "location_city": "Mumbai",
        "job_type": "full_time",
        "work_mode": "onsite",
        "category": "technology",
        "required_skills": ["Python", "Django", "SQL", "Git"],
        "salary_min": 40000,
        "salary_max": 60000,
        "experience_min": 1,
    },
    {
        "title": "Frontend Engineer (React)",
        "company": "Pune Digital",
        "description": "Join our team to build modern web apps using React and TypeScript.",
        "location_state": "Maharashtra",
        "location_city": "Pune",
        "job_type": "full_time",
        "work_mode": "hybrid",
        "category": "technology",
        "required_skills": ["JavaScript", "React", "TypeScript", "HTML", "CSS"],
        "salary_min": 50000,
        "salary_max": 80000,
        "experience_min": 2,
    },
    # Logistics - Maharashtra
    {
        "title": "Delivery Executive",
        "company": "SwiftLog Mumbai",
        "description": "Urgent requirement for delivery executives with own bike.",
        "location_state": "Maharashtra",
        "location_city": "Mumbai",
        "job_type": "gig",
        "work_mode": "onsite",
        "category": "logistics",
        "required_skills": ["Driving", "Navigation", "Communication"],
        "salary_min": 15000,
        "salary_max": 25000,
        "experience_min": 0,
    },
    # Healthcare - Maharashtra
    {
        "title": "Nursing Assistant",
        "company": "City Hospital Nashik",
        "description": "Assist doctors and provide patient care in a busy ward.",
        "location_state": "Maharashtra",
        "location_city": "Nashik",
        "job_type": "full_time",
        "work_mode": "onsite",
        "category": "healthcare",
        "required_skills": ["Patient Care", "First Aid", "Communication"],
        "salary_min": 18000,
        "salary_max": 22000,
        "experience_min": 1,
    },
    # Technology - Karnataka (fallback)
    {
        "title": "Flutter Developer",
        "company": "AppFlow Bangalore",
        "description": "Develop cross-platform apps using Flutter and Dart.",
        "location_state": "Karnataka",
        "location_city": "Bangalore",
        "job_type": "full_time",
        "work_mode": "remote",
        "category": "technology",
        "required_skills": ["Flutter", "Dart", "Mobile", "Git"],
        "salary_min": 60000,
        "salary_max": 100000,
        "experience_min": 2,
    },
    # Manufacturing - Uttar Pradesh
    {
        "title": "Industrial Welder",
        "company": "UP Metals Lucknow",
        "description": "Experienced welder for heavy machinery manufacturing.",
        "location_state": "Uttar Pradesh",
        "location_city": "Lucknow",
        "job_type": "full_time",
        "work_mode": "onsite",
        "category": "manufacturing",
        "required_skills": ["Welding", "Blueprints", "Safety Standards"],
        "salary_min": 20000,
        "salary_max": 35000,
        "experience_min": 3,
    },
    # Retail - Delhi
    {
        "title": "Retail Sales Associate",
        "company": "BigMart Delhi",
        "description": "Customer service and sales in our flagship store.",
        "location_state": "Delhi",
        "location_city": "New Delhi",
        "job_type": "full_time",
        "work_mode": "onsite",
        "category": "retail",
        "required_skills": ["Sales", "Communication", "Inventory"],
        "salary_min": 12000,
        "salary_max": 18000,
        "experience_min": 0,
    },
    # Finance - Maharashtra
    {
        "title": "Accountant",
        "company": "Mumbai FinCorp",
        "description": "Manage books and GST filings using Tally Prime.",
        "location_state": "Maharashtra",
        "location_city": "Mumbai",
        "job_type": "full_time",
        "work_mode": "onsite",
        "category": "finance",
        "required_skills": ["Accounting", "Tally", "GST", "Excel"],
        "salary_min": 25000,
        "salary_max": 40000,
        "experience_min": 2,
    }
]

async def seed():
    print(f"Seeding {len(JOBS)} jobs...")
    try:
        # First clear existing jobs if any (optional, but good for clean seed)
        # supabase.table("job_listings").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        
        result = supabase.table("job_listings").insert(JOBS).execute()
        print(f"Successfully seeded {len(result.data)} jobs.")
    except Exception as e:
        print(f"Error seeding jobs: {e}")

if __name__ == "__main__":
    asyncio.run(seed())
