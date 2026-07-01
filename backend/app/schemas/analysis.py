from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ScoreBreakdownItem(BaseModel):
    score: float
    max: float = 100.0


class Suggestion(BaseModel):
    title: str
    description: str
    priority: str = "medium"   # high | medium | low
    example: Optional[str] = None


class ContactInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None


class ResumeMetadata(BaseModel):
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    word_count: Optional[int] = None
    page_count: Optional[int] = None


class AnalysisCreate(BaseModel):
    job_description: Optional[str] = Field(None, max_length=10000)


class AnalysisRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    resume_id: str
    status: str
    error_message: Optional[str] = None

    # File info (joined from Resume)
    file_name: Optional[str] = None
    s3_url: Optional[str] = None

    # Scores
    ats_score: Optional[float] = None
    score_breakdown: Optional[Dict[str, Any]] = None

    # Skills
    skills_found: Optional[List[str]] = None
    missing_skills: Optional[List[str]] = None
    keywords_matched: Optional[int] = None

    # Contact
    contact_info: Optional[Dict[str, Any]] = None

    # Resume metadata
    resume_metadata: Optional[Dict[str, Any]] = None

    # Suggestions
    suggestions: Optional[List[Dict[str, Any]]] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime


class AnalysisListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    resume_id: str
    file_name: Optional[str] = None
    ats_score: Optional[float] = None
    status: str
    skills_count: int = 0
    missing_count: int = 0
    created_at: datetime


class AnalysisHistory(BaseModel):
    items: List[AnalysisListItem]
    total: int
    page: int
    page_size: int
