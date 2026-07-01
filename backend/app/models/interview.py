"""
Interview models — questions, mock interviews, answers, history.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, JSON, String, Text, event
)
from sqlalchemy.orm import relationship

from app.core.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Interview Question Set
# ---------------------------------------------------------------------------
class InterviewQuestionSet(Base):
    """A generated set of interview questions for a resume + job description."""
    __tablename__ = "interview_questions"

    id          = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id    = Column(String(36), ForeignKey("users.id",    ondelete="CASCADE"), nullable=False, index=True)
    resume_id   = Column(String(36), ForeignKey("resumes.id",  ondelete="CASCADE"), nullable=False, index=True)

    job_title       = Column(String(255), nullable=True)
    company_name    = Column(String(255), nullable=True)
    job_description = Column(Text, nullable=True)

    # Questions by category — each is a list of {question, difficulty, category, tips}
    technical_questions  = Column(JSON, nullable=True)
    behavioral_questions = Column(JSON, nullable=True)
    hr_questions         = Column(JSON, nullable=True)
    project_questions    = Column(JSON, nullable=True)
    aws_questions        = Column(JSON, nullable=True)
    python_questions     = Column(JSON, nullable=True)
    react_questions      = Column(JSON, nullable=True)
    database_questions   = Column(JSON, nullable=True)

    total_questions  = Column(Integer, default=0, nullable=False)
    status           = Column(String(20), default="completed", nullable=False)
    error_message    = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    owner  = relationship("User",   backref="question_sets")
    resume = relationship("Resume", backref="question_sets")
    mock_interviews = relationship("MockInterview", back_populates="question_set", cascade="all, delete-orphan")


@event.listens_for(InterviewQuestionSet, "before_update")
def _ts_qs(mapper, conn, target):
    target.updated_at = _utcnow()


# ---------------------------------------------------------------------------
# Mock Interview Session
# ---------------------------------------------------------------------------
class MockInterview(Base):
    """A complete mock interview session."""
    __tablename__ = "mock_interviews"

    id               = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id         = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_set_id  = Column(String(36), ForeignKey("interview_questions.id", ondelete="CASCADE"), nullable=False)

    # Status: active | completed | abandoned
    status           = Column(String(20), default="active", nullable=False)
    mode             = Column(String(10), default="text", nullable=False)  # text | voice (future)

    total_questions  = Column(Integer, default=0, nullable=False)
    answered         = Column(Integer, default=0, nullable=False)
    current_index    = Column(Integer, default=0, nullable=False)

    # Final scores (filled when status=completed)
    overall_score       = Column(Float, nullable=True)
    technical_score     = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=True)
    confidence_score    = Column(Float, nullable=True)
    grammar_score       = Column(Float, nullable=True)

    # Summary
    strengths       = Column(JSON, nullable=True)   # list of strings
    weaknesses      = Column(JSON, nullable=True)   # list of strings
    improvements    = Column(JSON, nullable=True)   # list of strings
    overall_feedback= Column(Text, nullable=True)

    started_at   = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at   = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at   = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    owner        = relationship("User",                 backref="mock_interviews")
    question_set = relationship("InterviewQuestionSet", back_populates="mock_interviews")
    answers      = relationship("MockAnswer",           back_populates="interview", cascade="all, delete-orphan")


@event.listens_for(MockInterview, "before_update")
def _ts_mi(mapper, conn, target):
    target.updated_at = _utcnow()


# ---------------------------------------------------------------------------
# Individual Answer
# ---------------------------------------------------------------------------
class MockAnswer(Base):
    """A single answer given during a mock interview."""
    __tablename__ = "mock_answers"

    id           = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_id = Column(String(36), ForeignKey("mock_interviews.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id     = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    question_index    = Column(Integer, nullable=False)
    question_text     = Column(Text, nullable=False)
    question_category = Column(String(50), nullable=True)
    question_difficulty = Column(String(10), default="medium", nullable=False)

    answer_text     = Column(Text, nullable=False)
    time_taken_secs = Column(Integer, default=0, nullable=False)

    # AI evaluation
    score           = Column(Float, nullable=True)    # 0–100
    technical_accuracy = Column(Float, nullable=True)
    communication   = Column(Float, nullable=True)
    completeness    = Column(Float, nullable=True)
    feedback        = Column(Text, nullable=True)
    ideal_answer    = Column(Text, nullable=True)
    keywords_used   = Column(JSON, nullable=True)
    keywords_missed = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    interview = relationship("MockInterview", back_populates="answers")
    owner     = relationship("User", backref="mock_answers")


# ---------------------------------------------------------------------------
# Interview History (lightweight summary for dashboard)
# ---------------------------------------------------------------------------
class InterviewHistory(Base):
    __tablename__ = "interview_history"

    id           = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id     = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    interview_id = Column(String(36), ForeignKey("mock_interviews.id", ondelete="CASCADE"), nullable=False)

    job_title          = Column(String(255), nullable=True)
    total_questions    = Column(Integer, default=0)
    overall_score      = Column(Float, nullable=True)
    technical_score    = Column(Float, nullable=True)
    communication_score= Column(Float, nullable=True)
    duration_minutes   = Column(Float, nullable=True)
    passed             = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    owner = relationship("User", backref="interview_history")
