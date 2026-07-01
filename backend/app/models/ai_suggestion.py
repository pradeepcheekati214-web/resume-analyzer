"""
AI Resume Suggestion model — stores LLM-generated resume improvement suggestions.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, JSON, String, Text, Integer, event
from sqlalchemy.orm import relationship

from app.core.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class AIResumeSuggestion(Base):
    __tablename__ = "resume_ai_suggestions"

    id          = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id    = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    analysis_id = Column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)

    # LLM provider used: openai | bedrock | mock
    provider    = Column(String(20), default="openai", nullable=False)
    model       = Column(String(50), nullable=True)

    # Status: pending | completed | failed
    status      = Column(String(20), default="pending", nullable=False)
    error_message = Column(Text, nullable=True)

    # Structured suggestions stored as JSON
    professional_summary   = Column(Text, nullable=True)
    experience_bullets     = Column(JSON, nullable=True)   # list of improved bullet strings
    keyword_improvements   = Column(JSON, nullable=True)   # [{original, improved, reason}]
    grammar_corrections    = Column(JSON, nullable=True)   # [{original, corrected, explanation}]
    skills_section         = Column(Text, nullable=True)
    missing_skills         = Column(JSON, nullable=True)   # list of strings
    formatting_suggestions = Column(JSON, nullable=True)   # list of strings
    industry_recommendations = Column(JSON, nullable=True) # list of strings

    # Usage tracking
    prompt_tokens     = Column(Integer, default=0, nullable=False)
    completion_tokens = Column(Integer, default=0, nullable=False)
    generation_count  = Column(Integer, default=1, nullable=False)  # how many times regenerated

    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    owner    = relationship("User", backref="ai_suggestions")
    analysis = relationship("Analysis", backref="ai_suggestions")

    def __repr__(self):
        return f"<AIResumeSuggestion id={self.id} status={self.status}>"


@event.listens_for(AIResumeSuggestion, "before_update")
def _ts(mapper, conn, target):
    target.updated_at = _utcnow()
