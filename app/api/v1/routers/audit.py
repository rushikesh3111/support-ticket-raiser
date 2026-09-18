from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.v1.deps import get_current_user
from app.models.models import User, UserRole, Ticket, AuditLog
from app.schemas.schemas import AuditLogResponse

router = APIRouter(prefix="/tickets/{ticket_id}/history", tags=["Audit Trail"])

@router.get("/", response_model=List[AuditLogResponse])
def get_ticket_history(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    if current_user.role == UserRole.USER and ticket.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    logs = db.query(AuditLog).filter(AuditLog.ticket_id == ticket_id).order_by(AuditLog.timestamp.asc()).all()
    
    result = []
    for log in logs:
        performer_name = "System"
        if log.performed_by:
            u = db.query(User).filter(User.id == log.performed_by).first()
            if u:
                performer_name = u.name
        result.append(AuditLogResponse(
            id=log.id,
            ticket_id=log.ticket_id,
            performed_by=log.performed_by,
            performer_name=performer_name,
            action=log.action,
            details=log.details,
            timestamp=log.timestamp
        ))
    return result
