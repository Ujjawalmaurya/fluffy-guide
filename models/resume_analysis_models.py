from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal, Union

class ExperienceEntry(BaseModel):
    company: str = "Unknown Company"
    role: str = "Role not specified"
    duration_months: int = 0
    seniority_level: Literal["junior", "mid", "senior", "lead", "unclear"] = "unclear"
    skills_used: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    achievement_ratio: float = 0.0

class EducationEntry(BaseModel):
    degree: str = "Degree not specified"
    institution: str = "Institution not specified"
    year: Optional[int] = None
    specialization: Optional[str] = None
    is_vocational: bool = False
    is_certified: bool = False

class CareerTrajectory(BaseModel):
    direction: Literal["ascending", "lateral", "descending", "unclear"] = "unclear"
    average_tenure_months: float = 0.0
    has_gaps: bool = False
    gap_periods: List[str] = Field(default_factory=list)
    total_experience_months: int = 0
    summary: Optional[str] = None

class Skill(BaseModel):
    name: str
    level: Optional[Literal["beginner", "intermediate", "advanced"]] = "intermediate"

class StructuredProfile(BaseModel):
    full_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    has_photo_mentioned: bool = False
    has_caste_religion_info: bool = False
    skills: List[Skill] = Field(default_factory=list)
    skill_levels: Dict[str, Literal["beginner", "intermediate", "advanced"]] = Field(default_factory=dict)
    soft_skills_inferred: List[str] = Field(default_factory=list)
    experiences: List[ExperienceEntry] = Field(default_factory=list)
    education: List[EducationEntry] = Field(default_factory=list)
    career_trajectory: Union[CareerTrajectory, str, dict, None] = Field(default=None)
    languages_known: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    has_linkedin: bool = False
    has_github: bool = False
    has_summary_section: bool = False
    inferred_target_roles: List[str] = Field(default_factory=list)

class QualityScores(BaseModel):
    ats_compatibility: int = 0
    quantification_score: int = 0
    section_completeness: int = 0
    readability_score: int = 0
    keyword_relevance: Optional[int] = None
    overall: int = 0
    ats_issues: List[str] = Field(default_factory=list)
    missing_sections: List[str] = Field(default_factory=list)

class BulletImprovement(BaseModel):
    original: str
    improved: str
    reason: str

class ImproveBulletRequest(BaseModel):
    bullet: str
    target_roles: List[str] = Field(default_factory=list)

class SuggestionSet(BaseModel):
    summary_generated: str = ""
    bullet_improvements: List[BulletImprovement] = Field(default_factory=list)
    skills_to_add: List[str] = Field(default_factory=list)
    skills_to_reframe: Dict[str, str] = Field(default_factory=dict)
    sections_to_add: List[str] = Field(default_factory=list)
    india_specific_flags: List[str] = Field(default_factory=list)
    transferable_skills_detected: List[str] = Field(default_factory=list)

class ResumeAnalysisResult(BaseModel):
    user_id: str
    structured_profile: StructuredProfile = Field(default_factory=StructuredProfile)
    quality_scores: QualityScores = Field(default_factory=QualityScores)
    suggestions: SuggestionSet = Field(default_factory=SuggestionSet)
    overall_score: int = 0
    target_roles: List[str] = Field(default_factory=list)
    india_flags: List[str] = Field(default_factory=list)
    raw_text: Optional[str] = None
