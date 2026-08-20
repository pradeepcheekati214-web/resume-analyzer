from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Session schemas
# ---------------------------------------------------------------------------
class ChatSessionCreate(BaseModel):
    resume_id: str
    title: Optional[str] = "New Chat"


class ChatSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    resume_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0   # populated in route


class ChatSessionList(BaseModel):
    items: List[ChatSessionRead]
    total: int


# ---------------------------------------------------------------------------
# Message schemas
# ---------------------------------------------------------------------------
class ChatMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    role: str
    message: str
    created_at: datetime


class SendMessageRequest(BaseModel):
    session_id: str
    message: str = Field(..., min_length=1, max_length=4000)


class SendMessageResponse(BaseModel):
    user_message:      ChatMessageRead
    assistant_message: ChatMessageRead


class ChatHistoryResponse(BaseModel):
    session:  ChatSessionRead
    messages: List[ChatMessageRead]
