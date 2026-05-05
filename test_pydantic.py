from app.schemas.request.job import JobCreateRequest
from app.schemas.enums import JobType
import json

def test_validation():
    # Test with "Full-time" (should fail)
    try:
        data = {
            "title": "Test Job",
            "type": "Full-time",
            "location": "Bhopal"
        }
        req = JobCreateRequest(**data)
        print("Validation success with Full-time (Unexpected!)")
    except Exception as e:
        print(f"Validation failed with Full-time: {e}")

    # Test with "full_time" (should succeed)
    try:
        data = {
            "title": "Test Job",
            "type": "full_time",
            "location": "Bhopal"
        }
        req = JobCreateRequest(**data)
        print("Validation success with full_time")
        print(f"Result: {req.model_dump()}")
    except Exception as e:
        print(f"Validation failed with full_time: {e}")

if __name__ == "__main__":
    test_validation()
