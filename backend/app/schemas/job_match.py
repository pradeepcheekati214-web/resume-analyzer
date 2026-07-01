from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class JobMatchCreate(BaseModel):
    resume_id: str
    job_description: str = Field(..., min_length=50)
    job_title: Optional[str] = None
    company_name: Optional[str] = None


class SkillGapItem(BaseModel):
    skill: str
    gap: str
    recommendation: str


class ExperienceGap(BaseModel):
    required_years: Optional[float] = None
    candidate_years: Optional[float] = None
    gap_notes: str = ""


class EducationAnalysis(BaseModel):
    required: Optional[str] = None
    candidate: Optional[str] = None
    match: bool = False
    notes: str = ""


class JobMatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    resume_id: str
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    job_description: str
    status: str
    error_message: Optional[str] = None

    overall_match: float = 0.0
    skills_match: float = 0.0
    experience_match: float = 0.0
    education_match: float = 0.0
    keyword_match: float = 0.0
    ats_compatibility: float = 0.0

    matching_skills: Optional[List[str]] = None
    missing_skills: Optional[List[str]] = None
    missing_keywords: Optional[List[str]] = None
    skill_gap_analysis: Optional[List[Dict[str, Any]]] = None
    experience_gap: Optional[Dict[str, Any]] = None
    education_analysis: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None

    created_at: datetime
    updated_at: datetime


class JobMatchListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    overall_match: float = 0.0
    status: str
    created_at: datetime


class JobMatchList(BaseModel):
    items: List[JobMatchListItem]
    total: int
    page: int
    page_size: int
