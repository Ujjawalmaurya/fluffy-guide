from enum import Enum
from typing import Optional, List
from pydantic import Field
from app.schemas.base import BaseSchema

class EducationLevel(str, Enum):
    TEN = "10th"
    TWELVE = "12th"
    GRADUATE = "Graduate"
    POSTGRADUATE = "Postgraduate"
    DROPOUT = "Dropout"

class Stream(str, Enum):
    SCIENCE = "Science"
    COMMERCE = "Commerce"
    ARTS = "Arts"
    VOCATIONAL = "Vocational"
    OTHER = "Other"

class JobLocationPref(str, Enum):
    SAME_CITY = "Same City"
    STATE = "State"
    ANYWHERE = "Anywhere"

class TradeSkill(str, Enum):
    ELECTRICIAN = "Electrician"
    PLUMBER = "Plumber"
    CARPENTER = "Carpenter"
    WELDER = "Welder"
    MASON = "Mason"
    PAINTER = "Painter"
    MECHANIC = "Mechanic"
    OTHER = "Other"

class ExperienceRange(str, Enum):
    ZERO_ONE = "0-1"
    ONE_THREE = "1-3"
    THREE_FIVE = "3-5"
    FIVE_PLUS = "5+"

class WorkRadius(str, Enum):
    LOCAL = "Local"
    DISTRICT = "District"
    STATE = "State"
    ANYWHERE = "Anywhere"

class InformalWorkType(str, Enum):
    STREET_VENDOR = "Street Vendor"
    DOMESTIC_WORKER = "Domestic Worker"
    DAILY_WAGE = "Daily Wage Labor"
    HOME_BASED = "Home-based Work"
    AGRICULTURAL = "Agricultural Work"
    OTHER = "Other"

class IncomeRange(str, Enum):
    BELOW_5K = "Below 5k"
    FROM_5K_10K = "5k-10k"
    FROM_10K_20K = "10k-20k"
    ABOVE_20K = "Above 20k"

class DigitalLiteracy(str, Enum):
    NONE = "None"
    BASIC = "Basic smartphone use"
    APPS = "Can use apps"
    COMFORTABLE = "Comfortable with internet"

class CompanySize(str, Enum):
    TINY = "1-10"
    SMALL = "11-50"
    MEDIUM = "51-200"
    LARGE = "200+"

class EmployerWorkType(str, Enum):
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    APPRENTICESHIP = "Apprenticeship"

class NGOFocusSector(str, Enum):
    SKILLING = "Skilling"
    EMPLOYMENT = "Employment"
    WOMEN_EMPOWERMENT = "Women Empowerment"
    YOUTH_DEVELOPMENT = "Youth Development"
    DIGITAL_LITERACY = "Digital Literacy"
    OTHER = "Other"

class NGOBeneficiaryType(str, Enum):
    YOUTH = "Youth"
    WOMEN = "Women"
    BLUE_COLLAR = "Blue Collar"
    INFORMAL = "Informal Workers"
    ALL = "All"

class GovtDept(str, Enum):
    LABOUR = "Labour"
    SKILL_DEVELOPMENT = "Skill Development"
    EDUCATION = "Education"
    OTHER = "Other"

class GovtAccessLevel(str, Enum):
    DISTRICT = "District"
    STATE = "State"
    NATIONAL = "National"

class StudentOnboardingRequest(BaseSchema):
    full_name: str = Field(..., min_length=2)
    age: Optional[int] = Field(None, ge=10, le=100)
    gender: Optional[str] = None
    state: str = Field(...)
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
    gender: Optional[str] = None
    state: str = Field(...)
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
    gender: Optional[str] = None
    state: str = Field(...)
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
    state: str = Field(...)
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
    state_jurisdiction: str = Field(...)
    district_jurisdiction: List[str] = []

class UserTypeRequest(BaseSchema):
    user_type: str

class ProfileRequest(BaseSchema):
    full_name: str
    age: int
    gender: str
    state: str
    city: str
    education_level: str
    languages: List[str]

class PreferencesRequest(BaseSchema):
    career_interests: List[str]
    expected_salary_min: Optional[int] = None
    expected_salary_max: Optional[int] = None
    work_type: str
    willing_to_relocate: bool = False
    target_roles: List[str] = []

class GenerateQuestionsRequest(BaseSchema):
    language: str = "en"

class AnswerRequest(BaseSchema):
    question_id: str
    answer: str

class SubmitAnswersRequest(BaseSchema):
    answers: List[AnswerRequest]
