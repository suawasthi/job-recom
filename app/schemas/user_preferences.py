from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class JobFeedbackRequest(BaseModel):
    job_id: int
    feedback_type: str  # "relevant", "not_relevant", "maybe_later"
    notes: Optional[str] = None

class JobBookmarkRequest(BaseModel):
    job_id: int
    is_bookmarked: bool

class JobHideRequest(BaseModel):
    job_id: int
    is_hidden: bool

class JobComparisonRequest(BaseModel):
    job_ids: List[int]
    comparison_name: Optional[str] = None

class UserJobPreferencesResponse(BaseModel):
    id: int
    user_id: int
    job_id: int
    is_relevant: Optional[bool]
    is_maybe_later: bool
    is_bookmarked: bool
    is_hidden: bool
    feedback_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class JobComparisonResponse(BaseModel):
    id: int
    user_id: int
    comparison_name: Optional[str]
    created_at: datetime
    job_count: int

    class Config:
        from_attributes = True

class JobComparisonDetailResponse(BaseModel):
    id: int
    user_id: int
    comparison_name: Optional[str]
    created_at: datetime
    jobs: List[dict]  # Will contain job details

    class Config:
        from_attributes = True

