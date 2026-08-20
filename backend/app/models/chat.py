"""
Chat models — sessions and messages for AI Resume Chatbot.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, event
from sqlalchemy.orm import relationship

from app.core.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class ChatSession(Base):
    """A named conversation between a user and their resume."""
    __tablename__ = "chat_sessions"

    id        = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id   = Column(String(36), ForeignKey("users.id",   ondelete="CASCADE"), nullable=False, index=True)
    resume_id = Column(String(36), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    title     = Column(String(255), nullable=False, default="New Chat")

    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    user     = relationship("User",   backref="chat_sessions")
    resume   = relationship("Resume", backref="chat_sessions")
    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )

    def __repr__(self):
        return f"<ChatSession id={self.id} title={self.title!r}>"


@event.listens_for(ChatSession, "before_update")
def _ts_session(mapper, conn, target):
    target.updated_at = _utcnow()


class ChatMessage(Base):
    """A single message within a chat session."""
    __tablename__ = "chat_messages"

    id         = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role       = Column(String(20), nullable=False)   # "user" | "assistant"
    message    = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage id={self.id} role={self.role} len={len(self.message)}>"
