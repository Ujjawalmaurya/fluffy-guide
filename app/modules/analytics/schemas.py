from pydantic import BaseModel
from datetime import datetime

class AnalyticsOverview(BaseModel):
    total_users: int
    active_jobs: int
    completion_rate: float
    onboarding_rate: float

class DistrictFunnel(BaseModel):
    state: str
    city: str
    registered: int
    onboarded: int
    assessed: int

class SkillGap(BaseModel):
    skill_name: str
    demand: int
    supply: int
    gap: int

class TrainingOutcome(BaseModel):
    month: datetime
    completions: int
