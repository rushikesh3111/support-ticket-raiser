from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.models import Ticket, SLAPolicy, TicketPriority, TicketStatus
from app.services.audit_service import create_notification, record_audit

DEFAULT_SLA = {
    TicketPriority.CRITICAL: {"response": 30, "resolution": 120, "desc": "Critical outage or system failure"},
    TicketPriority.HIGH: {"response": 60, "resolution": 240, "desc": "High severity customer impact"},
    TicketPriority.MEDIUM: {"response": 240, "resolution": 1440, "desc": "Standard general issue (24 hrs)"},
    TicketPriority.LOW: {"response": 480, "resolution": 2880, "desc": "Low urgency request or question (48 hrs)"},
}

def init_default_sla_policies(db: Session):
    for prio, times in DEFAULT_SLA.items():
        existing = db.query(SLAPolicy).filter(SLAPolicy.priority == prio).first()
        if not existing:
            policy = SLAPolicy(
                priority=prio,
                response_time_mins=times["response"],
                resolution_time_mins=times["resolution"],
                description=times["desc"]
            )
            db.add(policy)
    db.commit()

def calculate_sla_deadlines(db: Session, priority: TicketPriority, created_at: datetime):
    policy = db.query(SLAPolicy).filter(SLAPolicy.priority == priority).first()
    if policy:
        resp_mins = policy.response_time_mins
        resol_mins = policy.resolution_time_mins
    else:
        fallback = DEFAULT_SLA.get(priority, {"response": 240, "resolution": 1440})
        resp_mins = fallback["response"]
        resol_mins = fallback["resolution"]

    response_due = created_at + timedelta(minutes=resp_mins)
    resolution_due = created_at + timedelta(minutes=resol_mins)
    return response_due, resolution_due

def check_and_update_sla_breaches(db: Session) -> int:
    now = datetime.utcnow()
    tickets = db.query(Ticket).filter(
        Ticket.status.notin_([TicketStatus.RESOLVED, TicketStatus.CLOSED, TicketStatus.ARCHIVED])
    ).all()

    breached_count = 0
    for ticket in tickets:
        modified = False
        # Response breach
        if ticket.first_responded_at is None and ticket.response_due_at and now > ticket.response_due_at:
            if not ticket.is_response_breached:
                ticket.is_response_breached = True
                modified = True
                breached_count += 1
                record_audit(
                    db,
                    ticket_id=ticket.id,
                    action="SLA_RESPONSE_BREACH",
                    details=f"Ticket exceeded response deadline of {ticket.response_due_at.isoformat()}"
                )
                if ticket.assigned_to:
                    create_notification(
                        db,
                        user_id=ticket.assigned_to,
                        title=f"SLA Response Breach: #{ticket.id}",
                        message=f"Ticket #{ticket.id} '{ticket.title}' breached first response SLA deadline.",
                        ticket_id=ticket.id
                    )

        # Resolution breach
        if ticket.resolution_due_at and now > ticket.resolution_due_at:
            if not ticket.is_resolution_breached:
                ticket.is_resolution_breached = True
                modified = True
                breached_count += 1
                record_audit(
                    db,
                    ticket_id=ticket.id,
                    action="SLA_RESOLUTION_BREACH",
                    details=f"Ticket exceeded resolution deadline of {ticket.resolution_due_at.isoformat()}"
                )
                if ticket.assigned_to:
                    create_notification(
                        db,
                        user_id=ticket.assigned_to,
                        title=f"SLA Resolution Breach: #{ticket.id}",
                        message=f"Ticket #{ticket.id} '{ticket.title}' breached resolution SLA deadline.",
                        ticket_id=ticket.id
                    )

        if modified:
            db.add(ticket)

    if breached_count > 0:
        db.commit()

    return breached_count
