from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.v1.deps import get_current_user
from app.models.models import User, UserRole, Ticket, Comment, TicketStatus
from app.schemas.schemas import CommentCreate, CommentResponse
from app.services.audit_service import record_audit, create_notification

router = APIRouter(prefix="/tickets/{ticket_id}/comments", tags=["Comments"])

@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def add_comment(
    ticket_id: int,
    payload: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    if ticket.status == TicketStatus.ARCHIVED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot comment on an archived ticket")

    if ticket.status == TicketStatus.CLOSED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot comment on a closed ticket")

    # Regular user cannot post internal notes
    if payload.is_internal and current_user.role == UserRole.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Regular users cannot post internal agent notes"
        )

    # End users can only comment on their own tickets
    if current_user.role == UserRole.USER and ticket.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    now = datetime.utcnow()
    comment = Comment(
        ticket_id=ticket.id,
        author_id=current_user.id,
        message=payload.message.strip(),
        is_internal=payload.is_internal,
        created_at=now
    )
    db.add(comment)

    # Mark first response time if agent responds
    if current_user.role in [UserRole.AGENT, UserRole.ADMIN] and ticket.first_responded_at is None:
        ticket.first_responded_at = now
        # Check if first response breached
        if ticket.response_due_at and now > ticket.response_due_at:
            ticket.is_response_breached = True

    ticket.updated_at = now
    db.commit()
    db.refresh(comment)

    # Audit log
    audit_label = "INTERNAL_NOTE_ADDED" if payload.is_internal else "COMMENT_ADDED"
    record_audit(
        db,
        ticket_id=ticket.id,
        performed_by=current_user.id,
        action=audit_label,
        details=f"Comment added by {current_user.name} ({current_user.role.value})"
    )

    # Notifications
    if current_user.id == ticket.created_by:
        # User commented -> Notify assignee if assigned
        if ticket.assigned_to:
            create_notification(
                db,
                user_id=ticket.assigned_to,
                ticket_id=ticket.id,
                title=f"New comment on #{ticket.id}",
                message=f"User {current_user.name} replied on ticket #{ticket.id}"
            )
    else:
        # Agent commented -> Notify ticket creator (only if not internal note)
        if not payload.is_internal:
            create_notification(
                db,
                user_id=ticket.created_by,
                ticket_id=ticket.id,
                title=f"Agent response on #{ticket.id}",
                message=f"{current_user.name} replied: {payload.message[:50]}..."
            )

    return CommentResponse(
        id=comment.id,
        ticket_id=comment.ticket_id,
        author_id=comment.author_id,
        author_name=current_user.name,
        author_role=current_user.role.value,
        message=comment.message,
        is_internal=comment.is_internal,
        created_at=comment.created_at
    )

@router.get("/", response_model=List[CommentResponse])
def get_comments(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    if current_user.role == UserRole.USER and ticket.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    query = db.query(Comment).filter(Comment.ticket_id == ticket_id)
    if current_user.role == UserRole.USER:
        query = query.filter(Comment.is_internal == False)

    comments = query.order_by(Comment.created_at.asc()).all()
    results = []
    for c in comments:
        results.append(CommentResponse(
            id=c.id,
            ticket_id=c.ticket_id,
            author_id=c.author_id,
            author_name=c.author.name if c.author else "Unknown",
            author_role=c.author.role.value if c.author else "user",
            message=c.message,
            is_internal=c.is_internal,
            created_at=c.created_at
        ))
    return results
