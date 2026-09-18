from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, Field
from app.models.models import UserRole, TicketStatus, TicketPriority, TicketCategory

# ----------------- User Schemas -----------------
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    role: UserRole = UserRole.USER
    department: Optional[str] = "General"

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# ----------------- Comment Schemas -----------------
class CommentCreate(BaseModel):
    message: str = Field(..., min_length=1)
    is_internal: bool = False

class CommentResponse(BaseModel):
    id: int
    ticket_id: int
    author_id: int
    author_name: Optional[str] = None
    author_role: Optional[str] = None
    message: str
    is_internal: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------- Attachment Schemas -----------------
class AttachmentResponse(BaseModel):
    id: int
    ticket_id: int
    uploaded_by: int
    filename: str
    file_size: int
    content_type: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

# ----------------- Audit Schemas -----------------
class AuditLogResponse(BaseModel):
    id: int
    ticket_id: int
    performed_by: Optional[int] = None
    performer_name: Optional[str] = None
    action: str
    details: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

# ----------------- Ticket Schemas -----------------
class TicketCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=5)
    category: TicketCategory = TicketCategory.IT_SUPPORT
    priority: TicketPriority = TicketPriority.MEDIUM

class TicketUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, min_length=5)
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    category: Optional[TicketCategory] = None
    assigned_to: Optional[int] = None

class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    status: TicketStatus
    priority: TicketPriority
    category: TicketCategory
    created_by: int
    assigned_to: Optional[int] = None
    creator_name: Optional[str] = None
    assignee_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    response_due_at: Optional[datetime] = None
    resolution_due_at: Optional[datetime] = None
    first_responded_at: Optional[datetime] = None
    is_response_breached: bool
    is_resolution_breached: bool

    class Config:
        from_attributes = True

class TicketDetailResponse(TicketResponse):
    comments: List[CommentResponse] = []
    attachments: List[AttachmentResponse] = []
    audit_logs: List[AuditLogResponse] = []

class TicketListResponse(BaseModel):
    items: List[TicketResponse]
    total: int
    page: int
    limit: int
    pages: int

# ----------------- SLA Schemas -----------------
class SLAPolicyBase(BaseModel):
    priority: TicketPriority
    response_time_mins: int = Field(..., gt=0)
    resolution_time_mins: int = Field(..., gt=0)
    description: Optional[str] = None

class SLAPolicyCreate(SLAPolicyBase):
    pass

class SLAPolicyResponse(SLAPolicyBase):
    id: int

    class Config:
        from_attributes = True

# ----------------- Notification Schemas -----------------
class NotificationResponse(BaseModel):
    id: int
    ticket_id: Optional[int] = None
    title: str
    message: str
    channel: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------- Reporting Schemas -----------------
class SLAComplianceReport(BaseModel):
    total_tickets: int
    compliant_tickets: int
    breached_tickets: int
    compliance_rate: float
    response_breaches: int
    resolution_breaches: int

class AgentPerformanceReport(BaseModel):
    agent_id: int
    agent_name: str
    assigned_count: int
    resolved_count: int
    avg_resolution_mins: float

class TicketVolumeReport(BaseModel):
    by_status: dict
    by_priority: dict
    by_category: dict
    total: int
