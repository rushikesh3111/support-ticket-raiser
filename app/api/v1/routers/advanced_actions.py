from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db
from app.api.v1.deps import get_current_user, require_agent_or_admin
from app.models.models import User, Ticket, TicketStatus, UserRole
from app.schemas.advanced_schemas import TicketBulkActionRequest, CSATSurveyCreate
from app.services.audit_service import record_audit, create_notification

router = APIRouter(prefix="/actions", tags=["Advanced Actions"])

@router.post("/tickets/bulk", status_code=status.HTTP_200_OK)
def bulk_ticket_operations(
    payload: TicketBulkActionRequest,
    current_user: User = Depends(require_agent_or_admin),
    db: Session = Depends(get_db)
):
    tickets = db.query(Ticket).filter(Ticket.id.in_(payload.ticket_ids)).all()
    if not tickets:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No matching tickets found")

    updated_count = 0
    now = datetime.utcnow()

    for ticket in tickets:
        if payload.action == "status" and payload.status_value:
            try:
                new_status = TicketStatus(payload.status_value)
                ticket.status = new_status
                if new_status == TicketStatus.RESOLVED:
                    ticket.resolved_at = now
                elif new_status == TicketStatus.CLOSED:
                    ticket.closed_at = now
                ticket.updated_at = now
                record_audit(db, ticket.id, "BULK_STATUS_CHANGE", current_user.id, f"Bulk status set to {new_status.value}")
                updated_count += 1
            except ValueError:
                pass
        
        elif payload.action == "assign" and payload.assignee_id is not None:
            assignee = db.query(User).filter(User.id == payload.assignee_id).first()
            if assignee and assignee.role in [UserRole.AGENT, UserRole.ADMIN]:
                ticket.assigned_to = payload.assignee_id
                ticket.updated_at = now
                record_audit(db, ticket.id, "BULK_ASSIGNED", current_user.id, f"Bulk assigned to {assignee.name}")
                create_notification(db, assignee.id, f"Bulk Assigned Ticket #{ticket.id}", f"Assigned to ticket '{ticket.title}'", ticket.id)
                updated_count += 1

        elif payload.action == "archive" and current_user.role == UserRole.ADMIN:
            ticket.status = TicketStatus.ARCHIVED
            ticket.updated_at = now
            record_audit(db, ticket.id, "ARCHIVED", current_user.id, "Bulk archived by admin")
            updated_count += 1

    db.commit()
    return {"status": "success", "action": payload.action, "updated_count": updated_count}

@router.post("/tickets/{ticket_id}/csat", status_code=status.HTTP_201_CREATED)
def submit_csat_survey(
    ticket_id: int,
    payload: CSATSurveyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    if current_user.role == UserRole.USER and ticket.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    record_audit(
        db,
        ticket_id=ticket.id,
        action="CSAT_SUBMITTED",
        performed_by=current_user.id,
        details=f"Customer CSAT Rating: {payload.score}/5 Stars. Feedback: {payload.feedback or 'None'}",
        meta_info={"score": payload.score, "feedback": payload.feedback}
    )

    return {
        "status": "success",
        "ticket_id": ticket_id,
        "score": payload.score,
        "message": "Thank you for your rating! Feedback recorded."
    }
