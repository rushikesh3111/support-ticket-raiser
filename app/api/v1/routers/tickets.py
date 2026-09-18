import math
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.session import get_db
from app.api.v1.deps import get_current_user
from app.models.models import User, UserRole, Ticket, TicketStatus, TicketPriority, TicketCategory
from app.schemas.schemas import TicketCreate, TicketUpdate, TicketResponse, TicketDetailResponse, TicketListResponse
from app.services.sla_service import calculate_sla_deadlines
from app.services.audit_service import record_audit, create_notification

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    payload: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    created_now = datetime.utcnow()
    resp_due, resol_due = calculate_sla_deadlines(db, payload.priority, created_now)

    ticket = Ticket(
        title=payload.title,
        description=payload.description,
        category=payload.category,
        priority=payload.priority,
        status=TicketStatus.OPEN,
        created_by=current_user.id,
        created_at=created_now,
        updated_at=created_now,
        response_due_at=resp_due,
        resolution_due_at=resol_due,
        is_response_breached=False,
        is_resolution_breached=False
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    # Audit log
    record_audit(
        db,
        ticket_id=ticket.id,
        performed_by=current_user.id,
        action="CREATED",
        details=f"Ticket #{ticket.id} created with priority '{ticket.priority.value}' by {current_user.name}"
    )

    # Notify active agents/admins
    agents = db.query(User).filter(User.role.in_([UserRole.AGENT, UserRole.ADMIN]), User.is_active == True).all()
    for agent in agents:
        create_notification(
            db,
            user_id=agent.id,
            ticket_id=ticket.id,
            title=f"New Ticket #{ticket.id}",
            message=f"New ticket created: {ticket.title} [{ticket.priority.value}]"
        )

    res = TicketResponse.model_validate(ticket)
    res.creator_name = current_user.name
    return res

@router.get("/", response_model=TicketListResponse)
def list_tickets(
    status: Optional[TicketStatus] = None,
    priority: Optional[TicketPriority] = None,
    category: Optional[TicketCategory] = None,
    assigned_to: Optional[int] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Ticket)

    # RBAC filtering: Normal users can only see their own tickets
    if current_user.role == UserRole.USER:
        query = query.filter(Ticket.created_by == current_user.id)
    
    # Hide archived tickets from standard list unless explicit status is requested
    if status:
        query = query.filter(Ticket.status == status)
    else:
        query = query.filter(Ticket.status != TicketStatus.ARCHIVED)

    if priority:
        query = query.filter(Ticket.priority == priority)
    if category:
        query = query.filter(Ticket.category == category)
    if assigned_to:
        query = query.filter(Ticket.assigned_to == assigned_to)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Ticket.title.ilike(search_pattern),
                Ticket.description.ilike(search_pattern)
            )
        )

    total = query.count()
    pages = math.ceil(total / limit) if total > 0 else 1
    offset = (page - 1) * limit
    tickets = query.order_by(Ticket.created_at.desc()).offset(offset).limit(limit).all()

    items = []
    for t in tickets:
        item = TicketResponse.model_validate(t)
        if t.creator:
            item.creator_name = t.creator.name
        if t.assignee:
            item.assignee_name = t.assignee.name
        items.append(item)

    return TicketListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )

@router.get("/{ticket_id}", response_model=TicketDetailResponse)
def get_ticket_detail(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    # RBAC ownership check: End-user can only view their own ticket
    if current_user.role == UserRole.USER and ticket.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You cannot view tickets raised by other users"
        )

    res = TicketDetailResponse.model_validate(ticket)
    if ticket.creator:
        res.creator_name = ticket.creator.name
    if ticket.assignee:
        res.assignee_name = ticket.assignee.name

    # Filter internal comments for normal users
    visible_comments = []
    for c in ticket.comments:
        if c.is_internal and current_user.role == UserRole.USER:
            continue
        c_item = {
            "id": c.id,
            "ticket_id": c.ticket_id,
            "author_id": c.author_id,
            "author_name": c.author.name if c.author else "Unknown",
            "author_role": c.author.role.value if c.author else "user",
            "message": c.message,
            "is_internal": c.is_internal,
            "created_at": c.created_at
        }
        visible_comments.append(c_item)
    res.comments = visible_comments

    # Attachments
    res.attachments = [
        {
            "id": a.id,
            "ticket_id": a.ticket_id,
            "uploaded_by": a.uploaded_by,
            "filename": a.filename,
            "file_size": a.file_size,
            "content_type": a.content_type,
            "uploaded_at": a.uploaded_at
        }
        for a in ticket.attachments
    ]

    # Audit logs
    res.audit_logs = [
        {
            "id": l.id,
            "ticket_id": l.ticket_id,
            "performed_by": l.performed_by,
            "performer_name": l.ticket.creator.name if l.ticket and l.ticket.creator else "System",
            "action": l.action,
            "details": l.details,
            "timestamp": l.timestamp
        }
        for l in ticket.audit_logs
    ]

    return res

@router.put("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    payload: TicketUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    # End users cannot modify status/assignee
    if current_user.role == UserRole.USER:
        if ticket.created_by != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        if payload.status is not None or payload.assigned_to is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Customers/Users are not allowed to transition ticket status or change assignments"
            )

    # Valid status transitions rule check
    valid_transitions = {
        TicketStatus.OPEN: [TicketStatus.IN_PROGRESS, TicketStatus.ON_HOLD, TicketStatus.RESOLVED, TicketStatus.CLOSED],
        TicketStatus.IN_PROGRESS: [TicketStatus.ON_HOLD, TicketStatus.RESOLVED, TicketStatus.CLOSED],
        TicketStatus.ON_HOLD: [TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED, TicketStatus.CLOSED],
        TicketStatus.RESOLVED: [TicketStatus.CLOSED, TicketStatus.IN_PROGRESS],
        TicketStatus.CLOSED: [],  # Cannot reopen closed tickets directly
        TicketStatus.ARCHIVED: []
    }

    now = datetime.utcnow()
    changes = []

    if payload.title is not None and payload.title != ticket.title:
        changes.append(f"title: '{ticket.title}' -> '{payload.title}'")
        ticket.title = payload.title

    if payload.description is not None and payload.description != ticket.description:
        changes.append("description updated")
        ticket.description = payload.description

    if payload.category is not None and payload.category != ticket.category:
        changes.append(f"category: '{ticket.category.value}' -> '{payload.category.value}'")
        ticket.category = payload.category

    if payload.priority is not None and payload.priority != ticket.priority:
        changes.append(f"priority: '{ticket.priority.value}' -> '{payload.priority.value}'")
        ticket.priority = payload.priority
        # Recalculate SLA
        resp_due, resol_due = calculate_sla_deadlines(db, payload.priority, ticket.created_at)
        ticket.response_due_at = resp_due
        ticket.resolution_due_at = resol_due

    if payload.assigned_to is not None and payload.assigned_to != ticket.assigned_to:
        assignee = db.query(User).filter(User.id == payload.assigned_to).first()
        if not assignee:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assignee user does not exist")
        if assignee.role == UserRole.USER:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tickets can only be assigned to Agents or Admins")
        changes.append(f"assigned to: '{assignee.name}'")
        ticket.assigned_to = payload.assigned_to
        create_notification(
            db,
            user_id=assignee.id,
            ticket_id=ticket.id,
            title=f"Assigned to Ticket #{ticket.id}",
            message=f"You have been assigned to ticket '{ticket.title}'"
        )

    if payload.status is not None and payload.status != ticket.status:
        # Validate status transition
        allowed = valid_transitions.get(ticket.status, [])
        if payload.status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid state transition from '{ticket.status.value}' to '{payload.status.value}'"
            )
        
        changes.append(f"status: '{ticket.status.value}' -> '{payload.status.value}'")
        ticket.status = payload.status
        
        if payload.status == TicketStatus.RESOLVED:
            ticket.resolved_at = now
        elif payload.status == TicketStatus.CLOSED:
            ticket.closed_at = now

        # Notify ticket creator
        create_notification(
            db,
            user_id=ticket.created_by,
            ticket_id=ticket.id,
            title=f"Ticket #{ticket.id} Updated",
            message=f"Your ticket '{ticket.title}' status was updated to '{payload.status.value}'"
        )

    ticket.updated_at = now
    db.commit()
    db.refresh(ticket)

    if changes:
        record_audit(
            db,
            ticket_id=ticket.id,
            performed_by=current_user.id,
            action="UPDATED",
            details=f"Updated: {'; '.join(changes)}"
        )

    res = TicketResponse.model_validate(ticket)
    if ticket.creator:
        res.creator_name = ticket.creator.name
    if ticket.assignee:
        res.assignee_name = ticket.assignee.name
    return res

@router.delete("/{ticket_id}", status_code=status.HTTP_200_OK)
def archive_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only admin can archive
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to archive or soft-delete tickets"
        )

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    if ticket.status == TicketStatus.ARCHIVED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ticket is already archived")

    ticket.status = TicketStatus.ARCHIVED
    ticket.updated_at = datetime.utcnow()
    db.commit()

    record_audit(
        db,
        ticket_id=ticket.id,
        performed_by=current_user.id,
        action="ARCHIVED",
        details="Ticket soft-deleted and marked as archived by Admin"
    )

    return {"message": f"Ticket #{ticket_id} has been archived successfully"}
