from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ResumeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    file_name: str
    file_type: str
    file_size: Optional[int] = None
    s3_url: Optional[str] = None
    word_count: Optional[int] = None
    page_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class ResumeList(BaseModel):
    items: list[ResumeRead]
    total: int
    page: int
    page_size: int
