"""
Resume database model.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, event
from sqlalchemy.orm import relationship

from app.core.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class Resume(Base):
    __tablename__ = "resumes"

    id         = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id   = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    file_name  = Column(String(255), nullable=False)
    file_type  = Column(String(10),  nullable=False)
    file_size  = Column(Integer,     nullable=True)
    s3_key     = Column(String(512), nullable=True)
    s3_url     = Column(Text,        nullable=True)

    raw_text   = Column(Text,    nullable=True)
    word_count = Column(Integer, nullable=True)
    page_count = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    owner    = relationship("User",     back_populates="resumes")
    analyses = relationship("Analysis", back_populates="resume", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Resume id={self.id} file_name={self.file_name}>"


@event.listens_for(Resume, "before_update")
def _update_resume_timestamp(mapper, connection, target):
    target.updated_at = _utcnow()
