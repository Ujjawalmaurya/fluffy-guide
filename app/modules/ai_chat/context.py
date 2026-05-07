from typing import List, Optional
from pydantic import Field
from app.schemas.base import BaseSchema

class BaseContext(BaseSchema):
    version: str = "1.0"
    user_id: str
    role: str
    full_name: str
    state: str
    city: Optional[str] = None
    languages: List[str] = []
    
    # Enriched data
    skills: List[dict] = [] # [{name, level, category}]
    gaps: List[dict] = []   # [{name, priority, reason}]
    strengths: List[dict] = []
    
    # Status flags
    onboarding_done: bool = False
    assessment_done: bool = False

class StudentContext(BaseContext):
    age: Optional[int] = None
    education_level: str
    stream: Optional[str] = None
    institution: Optional[str] = None
    career_interests: List[str] = []

class BlueCollarContext(BaseContext):
    primary_trade: str
    secondary_skills: List[str] = []
    experience: Optional[str] = None
    is_employed: Optional[str] = None
    work_radius: str
    owns_smartphone: bool = True

class InformalWorkerContext(BaseContext):
    work_type: str
    income_range: Optional[str] = None
    digital_literacy: str
    owns_smartphone: bool = True
    interests: List[str] = []

class EmployerContext(BaseSchema):
    version: str = "1.0"
    role: str = "org_employer"
    contact_name: str
    designation: Optional[str] = None
    company_name: str
    industry: str
    size: Optional[str] = None
    location: str
    hiring_roles: List[str] = []
    required_skills: List[str] = []

class NGOContext(BaseSchema):
    version: str = "1.0"
    role: str = "org_ngo"
    org_name: str
    focus_sectors: List[str] = []
    coverage_areas: List[str] = []
    beneficiary_types: List[str] = []
    contact_person: str

class GovtOfficerContext(BaseSchema):
    version: str = "1.0"
    role: str = "org_govt"
    full_name: str
    designation: Optional[str] = None
    department: str
    access_level: str
    jurisdiction: str
