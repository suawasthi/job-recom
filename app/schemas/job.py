from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class JobType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    FREELANCE = "freelance"

class JobStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    DRAFT = "draft"

class JobBase(BaseModel):
    title: str
    description: str
    company_name: str
    location: str
    job_type: JobType
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    min_experience_years: Optional[float] = None
    max_experience_years: Optional[float] = None
    education_requirements: Optional[List[str]] = None
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    currency: str = "USD"
    benefits: Optional[List[str]] = None
    remote_work_allowed: str = "No"
    application_deadline: Optional[datetime] = None

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[JobType] = None
    status: Optional[JobStatus] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    min_experience_years: Optional[float] = None
    max_experience_years: Optional[float] = None
    education_requirements: Optional[List[str]] = None
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    benefits: Optional[List[str]] = None
    remote_work_allowed: Optional[str] = None
    application_deadline: Optional[datetime] = None

class Job(JobBase):
    id: int
    recruiter_id: int
    status: JobStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class JobRecommendation(BaseModel):
    job: Job
    match_score: float
    match_reasons: List[str]
    skill_matches: List[str]
    missing_skills: List[str]

class JobApplicationCreate(BaseModel):
    job_id: int
    resume_id: int
    cover_letter: Optional[str] = None

class JobApplication(BaseModel):
    id: int
    job_id: int
    user_id: int
    resume_id: int
    cover_letter: Optional[str] = None
    match_score: float
    status: str
    applied_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class JobSearchFilters(BaseModel):
    location: Optional[str] = None
    job_type: Optional[JobType] = None
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    remote_work_allowed: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[float] = None
