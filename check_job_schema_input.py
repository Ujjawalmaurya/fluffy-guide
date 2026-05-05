import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.schemas.request.job import JobCreateRequest
from pydantic import ValidationError

input_data = {
    'title': 'Star Pawan ', 
    'location': 'Andman', 
    'type': 'full_time', 
    'salary': '27000', 
    'description': 'pawn know all the basic types f jobs And their interest. thats it.'
}

print(f"Attempting to create JobCreateRequest with input: {input_data}")
try:
    req = JobCreateRequest.model_validate(input_data)
    print("Success!")
    print(req.model_dump())
except ValidationError as e:
    print("Failed!")
    for error in e.errors():
        print(f"Field: {error['loc']}, Type: {error['type']}, Msg: {error['msg']}")
