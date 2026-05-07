from typing import Optional, List
from pydantic import Field
from app.schemas.base import BaseSchema
from app.schemas.enums import (
    EducationLevel,
    EducationStream as Stream,
    JobLocationPreference as JobLocationPref,
    TradeSkill,
    ExperienceRange,
    WorkRadius,
    InformalWorkType,
    IncomeRange,
    DigitalLiteracy,
    CompanySize,
    JobType as EmployerWorkType,
    NGOFocusSector,
    NGOBeneficiaryType,
    GovtDept,
    GovtAccessLevel,
    Gender,
    Region
)

class StudentOnboardingRequest(BaseSchema):
    full_name: str = Field(..., min_length=2)
    age: Optional[int] = Field(None, ge=10, le=100)
    gender: Optional[Gender] = None
    state: Region = Field(...)
    city: Optional[str] = None
    preferred_job_location: JobLocationPref = JobLocationPref.ANYWHERE
    education_level: EducationLevel = Field(...)
    stream: Optional[Stream] = None
    institution_name: Optional[str] = None
    career_interests: List[str] = []
    languages_known: List[str] = ["English", "Hindi"]

class BlueCollarOnboardingRequest(BaseSchema):
    full_name: str = Field(..., min_length=2)
    age: Optional[int] = Field(None, ge=18, le=70)
    gender: Optional[Gender] = None
    state: Region = Field(...)
    city: Optional[str] = None
    village_district: Optional[str] = None
    primary_trade: TradeSkill = Field(...)
    secondary_skills: List[str] = []
    years_experience: Optional[ExperienceRange] = None
    is_currently_employed: Optional[str] = None
    preferred_work_radius: WorkRadius = WorkRadius.LOCAL
    owns_smartphone: bool = True
    languages_known: List[str] = ["Hindi"]

class InformalWorkerOnboardingRequest(BaseSchema):
    full_name: str = Field(..., min_length=2)
    age: Optional[int] = Field(None, ge=18, le=75)
    gender: Optional[Gender] = None
    state: Region = Field(...)
    city_village: Optional[str] = None
    current_work_type: InformalWorkType = Field(...)
    monthly_income: Optional[IncomeRange] = None
    digital_literacy: DigitalLiteracy = DigitalLiteracy.BASIC
    owns_smartphone: bool = True
    interests: List[str] = []
    languages_known: List[str] = ["Hindi"]

class EmployerOnboardingRequest(BaseSchema):
    contact_person_name: str = Field(..., min_length=2)
    designation: Optional[str] = None
    company_name: str = Field(..., min_length=2)
    industry_sector: str = Field(...)
    company_size: Optional[CompanySize] = None
    state: Region = Field(...)
    city: str = Field(...)
    roles_hiring_for: List[str] = []
    preferred_skills: List[str] = []
    work_type_offered: Optional[EmployerWorkType] = None

class NGOOnboardingRequest(BaseSchema):
    org_name: str = Field(..., min_length=2)
    registration_number: Optional[str] = None
    focus_sectors: List[NGOFocusSector] = Field(..., min_items=1)
    coverage_areas: List[str] = Field(..., min_items=1)
    beneficiary_types: List[NGOBeneficiaryType] = []
    contact_name: str = Field(..., min_length=2)
    contact_designation: Optional[str] = None

class GovtOfficerOnboardingRequest(BaseSchema):
    full_name: str = Field(..., min_length=2)
    designation: Optional[str] = None
    department: GovtDept = Field(...)
    access_level: GovtAccessLevel = GovtAccessLevel.STATE
    state_jurisdiction: Region = Field(...)
    district_jurisdiction: List[str] = []

class UserTypeRequest(BaseSchema):
    user_type: str

class ProfileRequest(BaseSchema):
    full_name: str
    age: int
    gender: Gender
    state: Region
    city: str
    education_level: EducationLevel
    languages: List[str]

class PreferencesRequest(BaseSchema):
    career_interests: List[str]
    expected_salary_min: Optional[int] = None
    expected_salary_max: Optional[int] = None
    work_type: EmployerWorkType
    willing_to_relocate: bool = False
    target_roles: List[str] = []

class GenerateQuestionsRequest(BaseSchema):
    language: str = "en"

class AnswerRequest(BaseSchema):
    question_id: str
    answer: str

class SubmitAnswersRequest(BaseSchema):
    answers: List[AnswerRequest]
