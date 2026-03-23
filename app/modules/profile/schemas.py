"""Profile module schemas."""
from pydantic import BaseModel
from typing import Optional


class ProfileUpdateIn(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    education_level: Optional[str] = None
    languages: Optional[list[str]] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None


class ParsedResumeOut(BaseModel):
    skills_found: list[dict]
    education_hints: list[dict]
    experience_hints: list[dict]
    experience_level: Optional[str] = None
    strengths: Optional[list[str]] = None
    weaknesses: Optional[list[str]] = None
    career_suggestions: Optional[list[str]] = None
    skill_gap_analysis: Optional[str] = None


class ProfileOut(BaseModel):
    id: str
    user_id: str
    full_name: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    state: Optional[str]
    city: Optional[str]
    education_level: Optional[str]
    languages: Optional[list[str]]
    phone: Optional[str]
    avatar_url: Optional[str]


class CompletionScoreOut(BaseModel):
    score: int
    filled_fields: list[str]
    missing_fields: list[str]


class ATSBreakdown(BaseModel):
    formatting: int
    keywords: int
    impact: int


class ATSScoreOut(BaseModel):
    score: int
    breakdown: ATSBreakdown


class IndiaQualifications(BaseModel):
    exams: list[str]
    certificates: list[str]


class Achievement(BaseModel):
    title: str
    impact: str


class ResumeAnalysisOut(BaseModel):
    parser_result: dict
    india_qualifications: IndiaQualifications
    achievements: list[Achievement]
    ats_score: ATSScoreOut
    suggestions: list[str]


class BulletRewriteIn(BaseModel):
    bullets: list[str]


class BulletRewriteIn(BaseModel):
    bullets: list[str]

class BulletRewriteOut(BaseModel):
    rewritten_bullets: list[str]
    remaining_daily_rewrites: int
