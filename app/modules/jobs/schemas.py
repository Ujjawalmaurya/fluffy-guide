"""Jobs module schemas."""
from pydantic import BaseModel
from typing import Optional


class JobCreate(BaseModel):
    title: str
    company: str
    description: Optional[str] = None
    location_state: str
    location_city: Optional[str] = None
    job_type: Optional[str] = None       # full_time, part_time, contract, gig
    work_mode: Optional[str] = None      # remote, onsite, hybrid
    category: str
    required_skills: list[str] = []
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    experience_min: Optional[int] = None
    source_url: Optional[str] = None


class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    location_state: Optional[str] = None
    location_city: Optional[str] = None
    job_type: Optional[str] = None
    work_mode: Optional[str] = None
    category: Optional[str] = None
    required_skills: Optional[list[str]] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    experience_min: Optional[int] = None
    source_url: Optional[str] = None
    is_active: Optional[bool] = None


class JobFilter(BaseModel):
    state: Optional[str] = None
    category: Optional[str] = None
    job_type: Optional[str] = None
    page: int = 1
    limit: int = 20


class JobOut(BaseModel):
    id: str
    title: str
    company: str
    description: Optional[str]
    location_state: str
    location_city: Optional[str]
    job_type: Optional[str]
    work_mode: Optional[str]
    category: str
    required_skills: Optional[list[str]]
    salary_min: Optional[int]
    salary_max: Optional[int]
    experience_min: Optional[int]
    is_active: bool
