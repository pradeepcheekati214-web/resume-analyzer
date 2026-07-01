"""
Analysis database model.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, event
from sqlalchemy.orm import relationship

from app.core.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class Analysis(Base):
    __tablename__ = "analyses"

    id        = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(String(36), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id  = Column(String(36), ForeignKey("users.id",   ondelete="CASCADE"), nullable=False, index=True)

    status        = Column(String(20), default="pending", nullable=False)
    error_message = Column(Text, nullable=True)

    ats_score       = Column(Float,   nullable=True)
    score_breakdown = Column(JSON,    nullable=True)

    skills_found     = Column(JSON,    nullable=True)
    missing_skills   = Column(JSON,    nullable=True)
    keywords_matched = Column(Integer, nullable=True)

    contact_info    = Column(JSON, nullable=True)
    suggestions     = Column(JSON, nullable=True)
    job_description = Column(Text, nullable=True)

    skills_count  = Column(Integer, default=0, nullable=False)
    missing_count = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    resume = relationship("Resume", back_populates="analyses")
    owner  = relationship("User",   back_populates="analyses")

    def __repr__(self):
        return f"<Analysis id={self.id} ats_score={self.ats_score} status={self.status}>"


@event.listens_for(Analysis, "before_update")
def _update_analysis_timestamp(mapper, connection, target):
    target.updated_at = _utcnow()
