from pydantic import BaseModel

class SkillSchema(BaseModel):
    skill_name: str
    proficiency: int
