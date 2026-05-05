from pydantic import BaseModel

class AssessmentSchema(BaseModel):
    id: str
    user_id: str
