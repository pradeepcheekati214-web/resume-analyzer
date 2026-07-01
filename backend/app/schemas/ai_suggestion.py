from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class KeywordImprovement(BaseModel):
    original: str
    improved: str
    reason: str


class GrammarCorrection(BaseModel):
    original: str
    corrected: str
    explanation: str


class AISuggestionCreate(BaseModel):
    analysis_id: str
    regenerate: bool = False


class AISuggestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    analysis_id: str
    provider: str
    model: Optional[str] = None
    status: str
    error_message: Optional[str] = None

    professional_summary: Optional[str] = None
    experience_bullets: Optional[List[str]] = None
    keyword_improvements: Optional[List[Dict[str, Any]]] = None
    grammar_corrections: Optional[List[Dict[str, Any]]] = None
    skills_section: Optional[str] = None
    missing_skills: Optional[List[str]] = None
    formatting_suggestions: Optional[List[str]] = None
    industry_recommendations: Optional[List[str]] = None

    prompt_tokens: int = 0
    completion_tokens: int = 0
    generation_count: int = 1

    created_at: datetime
    updated_at: datetime


class AISuggestionDownload(BaseModel):
    """Flat text representation for download."""
    content: str
    filename: str
