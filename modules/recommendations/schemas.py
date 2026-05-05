from pydantic import BaseModel

class RecommendationResponse(BaseModel):
    success: bool
    data: list
