"""
Verification test for centralized schemas.
Ensures all centralized schemas can be imported and instantiated with sample data.
"""
import sys
from pydantic import ValidationError

# Request Schemas
from app.schemas.request.auth import SignupRequest, OTPVerifyRequest
from app.schemas.request.profile import ProfileUpdateRequest
from app.schemas.request.job import JobCreateRequest
from app.schemas.request.assessment import AssessmentAnswerRequest

# Response Schemas
from app.schemas.response.auth import TokenResponse, UserAuthResponse
from app.schemas.response.profile import ProfileResponse
from app.schemas.response.job import JobResponse
from app.schemas.response.assessment import StartAssessmentResponse, AnswerResponse
from app.schemas.response.user import UserDashboardResponse

def test_auth_request():
    req = SignupRequest(email="test@example.com", role="individual_youth")
    assert req.email == "test@example.com"
    
def test_profile_update():
    # education_level is an enum, but pydantic handles string conversion if matched
    req = ProfileUpdateRequest(full_name="Raj", age=25)
    assert req.full_name == "Raj"
    
def test_job_create():
    req = JobCreateRequest(
        title="Software Engineer",
        company="Tech Corp",
        location_state="Karnataka",
        category="Tech"
    )
    assert req.title == "Software Engineer"

def test_dashboard_response():
    data = {
        "profile": {
            "id": "user_123",
            "email": "test@example.com",
            "full_name": "Test User",
            "career_stage": "fresher",
            "age": 25,
            "gender": "male",
            "state": "karnataka",
            "city": "Bengaluru",
            "education_level": "graduate",
            "languages": ["english"],
            "avatar_url": None,
            "onboarding_done": True,
            "profile_complete_percentage": 100
        },
        "progress_summary": {
            "courses_completed": 0,
            "assessments_taken": 0,
            "skills_verified": 0
        },
        "top_recommendations": [],
        "notifications_count": 0
    }
    try:
        resp = UserDashboardResponse.model_validate(data)
        assert resp.profile.full_name == "Test User"
    except ValidationError as e:
        print(f"Validation failed for UserDashboardResponse: {e}")
        raise

if __name__ == "__main__":
    # Simple manual run
    test_auth_request()
    test_profile_update()
    test_job_create()
    test_dashboard_response()
    print("All schema verification tests passed!")
