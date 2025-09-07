from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    JOB_SEEKER = "job_seeker"
    RECRUITER = "recruiter"

class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: UserRole
    company: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    email_verified: Optional[bool] = False
    firebase_uid: Optional[str] = None

class UserCreate(UserBase):
    password: Optional[str] = None  # Optional for Firebase users

class UserUpdate(BaseModel):
    name: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User
