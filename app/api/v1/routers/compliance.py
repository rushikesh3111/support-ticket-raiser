from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.v1.deps import get_current_user, require_admin
from app.models.models import User, Ticket, Comment, AuditLog, TicketStatus, TicketPriority, TicketCategory, UserRole
from app.services.audit_service import record_audit, create_notification
from app.services.sla_service import calculate_sla_deadlines
from app.api.v1.routers.enterprise import AUTO_ROUTING_TABLE

router = APIRouter(prefix="/compliance", tags=["Enterprise Compliance & Inbound Channels"])

class InboundEmailPayload(BaseModel):
    sender_email: EmailStr
    sender_name: str
    subject: str
    body_plain: str
    category: Optional[TicketCategory] = TicketCategory.IT_SUPPORT
    priority: Optional[TicketPriority] = TicketPriority.MEDIUM

class ErasureRequestResponse(BaseModel):
    status: str
    email: str
    anonymized_tickets_count: int
    anonymized_comments_count: int
    message: str

@router.post("/inbound-email", status_code=status.HTTP_201_CREATED)
def parse_inbound_support_email(
    payload: InboundEmailPayload,
    db: Session = Depends(get_db)
):
    """
    Simulates inbound email-to-ticket ingestion gateway (SendGrid Inbound Parse / AWS SES / Mailgun webhook).
    Automatically registers new users if unknown, or maps to existing user profile.
    """
    # 1. Match or provision customer identity
    user = db.query(User).filter(User.email == payload.sender_email).first()
    if not user:
        from app.core.security import get_password_hash
        user = User(
            name=payload.sender_name,
            email=payload.sender_email,
            hashed_password=get_password_hash("InboundTempPass123!"),
            role=UserRole.USER,
            department="Inbound Email",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 2. SLA & intelligent queue assignment
    now = datetime.utcnow()
    resp_due, resol_due = calculate_sla_deadlines(db, payload.priority, now)
    assigned_agent_id = AUTO_ROUTING_TABLE.get(payload.category.value, None)

    ticket = Ticket(
        title=f"[Email Inbound] {payload.subject}",
        description=payload.body_plain,
        category=payload.category,
        priority=payload.priority,
        status=TicketStatus.OPEN,
        created_by=user.id,
        assigned_to=assigned_agent_id,
        created_at=now,
        updated_at=now,
        response_due_at=resp_due,
        resolution_due_at=resol_due,
        is_response_breached=False,
        is_resolution_breached=False
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    record_audit(
        db,
        ticket_id=ticket.id,
        performed_by=user.id,
        action="INBOUND_EMAIL_PARSED",
        details=f"Ticket ingested via inbound gateway from {payload.sender_email}"
    )

    if assigned_agent_id:
        create_notification(
            db,
            user_id=assigned_agent_id,
            ticket_id=ticket.id,
            title=f"Inbound Email Ticket #{ticket.id}",
            message=f"Received: '{payload.subject}' from {payload.sender_name}"
        )

    return {
        "status": "ticket_created",
        "ticket_id": ticket.id,
        "title": ticket.title,
        "assigned_to": ticket.assigned_to,
        "sla_response_due": ticket.response_due_at.isoformat()
    }

@router.post("/gdpr/erasure", response_model=ErasureRequestResponse)
def execute_gdpr_right_to_erasure(
    user_email: EmailStr,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Executes GDPR Right-to-Erasure (Data Retention / Anonymization Policy).
    Anonymizes customer PII across user profile, ticket narratives, and comments.
    """
    target_user = db.query(User).filter(User.email == user_email).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if target_user.role == UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="System Administrators cannot be erased")

    # 1. Anonymize user profile
    anonymized_tag = f"anonymized_user_{target_user.id}@gdpr-erased.local"
    target_user.name = f"GDPR Anonymized User #{target_user.id}"
    target_user.email = anonymized_tag
    target_user.is_active = False
    target_user.department = "Anonymized"

    # 2. Anonymize tickets created by this user
    tickets = db.query(Ticket).filter(Ticket.created_by == target_user.id).all()
    ticket_count = len(tickets)
    for t in tickets:
        t.description = "[CONTENT SCRUBBED PURSUANT TO GDPR RIGHT TO ERASURE COMPLIANCE]"
        record_audit(db, t.id, "GDPR_ANONYMIZED", current_user.id, "Requester PII redacted")

    # 3. Anonymize comments written by this user
    comments = db.query(Comment).filter(Comment.author_id == target_user.id).all()
    comment_count = len(comments)
    for c in comments:
        c.message = "[COMMENT SCRUBBED PURSUANT TO GDPR DATA RETENTION POLICY]"

    db.commit()

    return ErasureRequestResponse(
        status="erasure_completed",
        email=user_email,
        anonymized_tickets_count=ticket_count,
        anonymized_comments_count=comment_count,
        message="Subject identity anonymized, PII masked, and user account purged."
    )
