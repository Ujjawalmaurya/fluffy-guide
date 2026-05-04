"""
ML Feature Schemas
Numeric feature vectors for ML pipelines.
"""
from typing import List
from app.schemas.base import BaseSchema


class UserFeatureVector(BaseSchema):
    """Numeric representation of user skills/experience for matching."""
    skill_ids: List[int]
    experience_years: float
    education_level_numeric: int
    location_encoded: int
    preferred_salary_min: float = 0.0


class JobFeatureVector(BaseSchema):
    """Numeric representation of job requirements."""
    required_skill_ids: List[int]
    min_experience: float
    required_education_numeric: int
    location_encoded: int
    salary_offered_min: float


class SkillGapFeatureVector(BaseSchema):
    """Input features for gap priority model."""
    user_skill_levels: List[float]
    market_demand_scores: List[float]
    time_to_learn_est: List[float]
