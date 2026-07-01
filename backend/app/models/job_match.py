"""
Job Match model — stores results of resume vs job description comparison.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, event
from sqlalchemy.orm import relationship

from app.core.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class JobMatch(Base):
    __tablename__ = "job_matches"

    id          = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id    = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id   = Column(String(36), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)

    # Input
    job_title       = Column(String(255), nullable=True)
    company_name    = Column(String(255), nullable=True)
    job_description = Column(Text, nullable=False)

    # Match results
    overall_match      = Column(Float, default=0.0, nullable=False)   # 0–100
    skills_match       = Column(Float, default=0.0, nullable=False)
    experience_match   = Column(Float, default=0.0, nullable=False)
    education_match    = Column(Float, default=0.0, nullable=False)
    keyword_match      = Column(Float, default=0.0, nullable=False)
    ats_compatibility  = Column(Float, default=0.0, nullable=False)

    # Detailed results
    matching_skills    = Column(JSON, nullable=True)   # list of strings
    missing_skills     = Column(JSON, nullable=True)   # list of strings
    missing_keywords   = Column(JSON, nullable=True)   # list of strings
    skill_gap_analysis = Column(JSON, nullable=True)   # [{skill, gap, recommendation}]
    experience_gap     = Column(JSON, nullable=True)   # {required_years, candidate_years, gap_notes}
    education_analysis = Column(JSON, nullable=True)   # {required, candidate, match}
    recommendations    = Column(JSON, nullable=True)   # list of strings

    status = Column(String(20), default="completed", nullable=False)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    owner  = relationship("User",   backref="job_matches")
    resume = relationship("Resume", backref="job_matches")

    def __repr__(self):
        return f"<JobMatch id={self.id} overall={self.overall_match}>"


@event.listens_for(JobMatch, "before_update")
def _ts(mapper, conn, target):
    target.updated_at = _utcnow()
