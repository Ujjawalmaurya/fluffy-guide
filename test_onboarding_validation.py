
import sys
from pydantic import ValidationError
from app.modules.onboarding.schemas import BlueCollarOnboardingIn, TradeSkill, ExperienceRange, WorkRadius

def test_validation():
    print("Testing BlueCollarOnboardingIn validation...")
    
    # Valid data
    valid_data = {
        "full_name": "Mohan Das",
        "age": 28,
        "gender": "Male",
        "state": "Maharashtra",
        "city": "Mumbai",
        "village_district": "",
        "primary_trade": "Electrician",
        "secondary_skills": [],
        "years_experience": "1-3",  # This should now work!
        "is_currently_employed": "No",
        "preferred_work_radius": "Local",
        "owns_smartphone": True,
        "languages_known": ["Hindi"]
    }
    
    try:
        BlueCollarOnboardingIn(**valid_data)
        print("✅ Validation PASSED for '1-3'")
    except ValidationError as e:
        print(f"❌ Validation FAILED for '1-3': {e}")

    # Invalid data (old format)
    invalid_data = valid_data.copy()
    invalid_data["years_experience"] = "1-3 years"
    
    try:
        BlueCollarOnboardingIn(**invalid_data)
        print("❌ Validation PASSED for '1-3 years' (Expected it to FAIL now)")
    except ValidationError as e:
        print("✅ Validation FAILED for '1-3 years' as expected.")

if __name__ == "__main__":
    test_validation()
