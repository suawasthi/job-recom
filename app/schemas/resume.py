from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

class ResumeBase(BaseModel):
    original_filename: str

class ResumeUpload(BaseModel):
    pass  # File will be handled by FastAPI's UploadFile

class ParsedData(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[float] = None
    education: Optional[List[Dict[str, Any]]] = None
    work_experience: Optional[List[Dict[str, Any]]] = None
    projects: Optional[List[Dict[str, Any]]] = None

    class Config:
        extra = "ignore"



class ResumeUpdate(ParsedData):
    pass

class ResumeScore(BaseModel):
    ats_score: float
    completeness_score: float
    keyword_density_score: float
    formatting_score: float
    overall_score: float

class ResumeFeedback(BaseModel):
    warnings: List[str]
    suggestions: List[str]
    missing_fields: List[str]

class Resume(ResumeBase):
    id: int
    user_id: int
    parsed_name: Optional[str] = None
    parsed_email: Optional[str] = None
    parsed_phone: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[float] = None
    education: Optional[List[Dict[str, Any]]] = None
    work_experience: Optional[List[Dict[str, Any]]] = None
    projects: Optional[List[Dict[str, Any]]] = None
    ats_score: float
    completeness_score: float
    keyword_density_score: float
    formatting_score: float
    warnings: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ResumeAnalysis(BaseModel):
    resume: Resume
    score: ResumeScore
    feedback: ResumeFeedback
    parsed_data: ParsedData
