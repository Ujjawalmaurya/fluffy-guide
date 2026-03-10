"""Onboarding schemas — Pydantic models for all 5 steps."""
from pydantic import BaseModel
from typing import Optional


class UserTypeIn(BaseModel):
    user_type: str  # one of the 6 user type strings


class ProfileIn(BaseModel):
    full_name: str
    age: int
    gender: str
    state: str
    city: str
    education_level: str
    languages: list[str]


class PreferencesIn(BaseModel):
    career_interests: list[str]
    expected_salary_min: Optional[int] = None
    expected_salary_max: Optional[int] = None
    work_type: str
    willing_to_relocate: bool = False
    target_roles: list[str] = []


class GenerateQuestionsIn(BaseModel):
    language: str = "en"  # 'en' or 'hi'


class AnswerItem(BaseModel):
    question_id: str
    question_text: str
    answer: str


class SubmitAnswersIn(BaseModel):
    answers: list[AnswerItem]


class QuestionOut(BaseModel):
    id: str
    question: str
    type: str           # 'text', 'mcq', 'rating'
    options: list[str] = []


class OnboardingStateOut(BaseModel):
    current_step: int
    completed_steps: list[int]
    step_data: dict
