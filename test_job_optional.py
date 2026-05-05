
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.schemas.request.job import JobCreateRequest
from pydantic import ValidationError

input_data = {
    'title': 'Test Job',
    'location': 'Test Location',
    'type': 'full_time'
}

print(f"Input: {input_data}")
try:
    req = JobCreateRequest.model_validate(input_data)
    print("Success!")
    print(req.model_dump())
except ValidationError as e:
    print("Failed!")
    print(e)
