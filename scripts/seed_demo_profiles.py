import os
import json
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(url, key)

personas = [
    {
        "email": "demo.ramesh@sankalp.ai",
        "id": "daa14278-f26b-4404-95cc-5eb169925fed",
        "profile": {
            "full_name": "Ramesh Verma",
            "age": 24,
            "gender": "male",
            "state": "Madhya Pradesh",
            "city": "Indore",
            "education_level": "Bachelor",
            "languages": ["Hindi", "English"]
        },
        "preferences": {
            "career_interests": ["technology", "logistics"],
            "expected_salary_min": 15000,
            "expected_salary_max": 35000,
            "work_type": "hybrid",
            "willing_to_relocate": True,
            "target_roles": ["Software Developer", "IT Support"],
            "skill_tags": ["Python", "JavaScript", "SQL", "Linux"]
        }
    },
    {
        "email": "demo.priya@sankalp.ai",
        "id": "cea951a5-b448-4dc4-8c37-b83d1d5b689b",
        "profile": {
            "full_name": "Priya Sharma",
            "age": 28,
            "gender": "female",
            "state": "Maharashtra",
            "city": "Pune",
            "education_level": "Masters",
            "languages": ["Hindi", "English", "Marathi"]
        },
        "preferences": {
            "career_interests": ["healthcare", "education"],
            "expected_salary_min": 25000,
            "expected_salary_max": 60000,
            "work_type": "onsite",
            "willing_to_relocate": False,
            "target_roles": ["Staff Nurse", "Clinical Coordinator"],
            "skill_tags": ["Patient Care", "Pharmacology", "Medical Records", "First Aid"]
        }
    },
    {
        "email": "demo.officer@sankalp.ai",
        "id": "52001edf-a140-4d78-9e33-4705ffeed9e8",
        "profile": {
            "full_name": "Ravi Officer",
            "age": 40,
            "gender": "male",
            "state": "Delhi",
            "city": "New Delhi",
            "education_level": "Masters",
            "languages": ["Hindi", "English"]
        },
        "preferences": {
            "career_interests": ["finance", "general"],
            "expected_salary_min": 50000,
            "expected_salary_max": 100000,
            "work_type": "onsite",
            "willing_to_relocate": False,
            "target_roles": ["Policy Analyst", "Program Manager"],
            "skill_tags": ["Data Analysis", "Policy", "MS Office", "Communication"]
        },
        "type": "government"
    }
]

for p in personas:
    uid = p["id"]
    print(f"Seeding profile for {p['email']} ({uid})...")
    
    # Prepare data for user_profiles
    profile_info = {
        "full_name": p["profile"].get("full_name"),
        "age": p["profile"].get("age"),
        "education_level": p["profile"].get("education_level"),
        "state": p["profile"].get("state", "Karnataka"),
        "city": p["profile"].get("city", "Bangalore"),
        "languages": p["profile"].get("languages", ["English", "Hindi"]),
        "career_identity": p["profile"].get("career_identity", "Professional")
    }
    
    # Prepare data for user_preferences
    pref_info = {
        "career_interests": p["preferences"].get("career_interests", []),
        "expected_salary_min": p["preferences"].get("expected_salary_min", 300000),
        "expected_salary_max": p["preferences"].get("expected_salary_max", 800000),
        "work_type": p["preferences"].get("work_type", "Full-time"),
        "target_roles": p["preferences"].get("target_roles", [])
    }
    
    # Upsert user_profiles
    profile_data = {"user_id": uid, **profile_info}
    supabase.table("user_profiles").upsert(profile_data, on_conflict="user_id").execute()
    
    # Upsert user_preferences
    pref_data = {"user_id": uid, **pref_info}
    supabase.table("user_preferences").upsert(pref_data, on_conflict="user_id").execute()
    
    print(f"Done for {p['email']}")

print("All demo profiles seeded successfully!")
