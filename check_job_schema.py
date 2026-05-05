import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.schemas.request.job import JobCreateRequest
from pydantic import ValidationError

print("Attempting to create JobCreateRequest with only title...")
try:
    req = JobCreateRequest(title="Test Job")
    print("Success! Fields are optional.")
    print(req.model_dump())
except ValidationError as e:
    print("Failed! Some fields are required.")
    for error in e.errors():
        print(f"Field: {error['loc']}, Type: {error['type']}, Msg: {error['msg']}")
