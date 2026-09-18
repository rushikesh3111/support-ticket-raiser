from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class KBArticleBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    content: str = Field(..., min_length=10)
    category: str = Field(..., min_length=2, max_length=100)
    tags: Optional[str] = None

class KBArticleCreate(KBArticleBase):
    pass

class KBArticleResponse(KBArticleBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class CSATSurveyCreate(BaseModel):
    score: int = Field(..., ge=1, le=5)  # 1 to 5 stars
    feedback: Optional[str] = None

class TicketBulkActionRequest(BaseModel):
    ticket_ids: List[int] = Field(..., min_items=1)
    action: str = Field(...)  # 'assign', 'status', 'delete'
    status_value: Optional[str] = None
    assignee_id: Optional[int] = None
