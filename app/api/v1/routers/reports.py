from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.api.v1.deps import get_current_user, require_agent_or_admin
from app.models.models import User, UserRole, Ticket, TicketStatus, TicketPriority, TicketCategory
from app.schemas.schemas import SLAComplianceReport, AgentPerformanceReport, TicketVolumeReport

router = APIRouter(prefix="/reports", tags=["Reporting & Analytics"])

@router.get("/sla-compliance", response_model=SLAComplianceReport)
def get_sla_compliance_report(
    current_user: User = Depends(require_agent_or_admin),
    db: Session = Depends(get_db)
):
    total = db.query(Ticket).filter(Ticket.status != TicketStatus.ARCHIVED).count()
    if total == 0:
        return SLAComplianceReport(
            total_tickets=0,
            compliant_tickets=0,
            breached_tickets=0,
            compliance_rate=100.0,
            response_breaches=0,
            resolution_breaches=0
        )

    resp_breaches = db.query(Ticket).filter(
        Ticket.status != TicketStatus.ARCHIVED,
        Ticket.is_response_breached == True
    ).count()

    resol_breaches = db.query(Ticket).filter(
        Ticket.status != TicketStatus.ARCHIVED,
        Ticket.is_resolution_breached == True
    ).count()

    # Breached overall = either response or resolution breached
    breached_total = db.query(Ticket).filter(
        Ticket.status != TicketStatus.ARCHIVED,
        (Ticket.is_response_breached == True) | (Ticket.is_resolution_breached == True)
    ).count()

    compliant = total - breached_total
    compliance_rate = round((compliant / total) * 100.0, 2)

    return SLAComplianceReport(
        total_tickets=total,
        compliant_tickets=compliant,
        breached_tickets=breached_total,
        compliance_rate=compliance_rate,
        response_breaches=resp_breaches,
        resolution_breaches=resol_breaches
    )

@router.get("/agent-performance", response_model=List[AgentPerformanceReport])
def get_agent_performance_report(
    current_user: User = Depends(require_agent_or_admin),
    db: Session = Depends(get_db)
):
    agents = db.query(User).filter(User.role.in_([UserRole.AGENT, UserRole.ADMIN])).all()
    results = []

    for agent in agents:
        assigned_tickets = db.query(Ticket).filter(Ticket.assigned_to == agent.id).all()
        assigned_count = len(assigned_tickets)
        
        resolved_tickets = [t for t in assigned_tickets if t.status in [TicketStatus.RESOLVED, TicketStatus.CLOSED] and t.resolved_at]
        resolved_count = len(resolved_tickets)

        total_mins = 0
        for t in resolved_tickets:
            diff = (t.resolved_at - t.created_at).total_seconds() / 60.0
            total_mins += max(0, diff)
        
        avg_resolution = round(total_mins / resolved_count, 1) if resolved_count > 0 else 0.0

        results.append(AgentPerformanceReport(
            agent_id=agent.id,
            agent_name=agent.name,
            assigned_count=assigned_count,
            resolved_count=resolved_count,
            avg_resolution_mins=avg_resolution
        ))

    return results

@router.get("/ticket-volume", response_model=TicketVolumeReport)
def get_ticket_volume_report(
    current_user: User = Depends(require_agent_or_admin),
    db: Session = Depends(get_db)
):
    tickets = db.query(Ticket).filter(Ticket.status != TicketStatus.ARCHIVED).all()
    total = len(tickets)

    by_status = {}
    for s in TicketStatus:
        if s != TicketStatus.ARCHIVED:
            by_status[s.value] = 0

    by_priority = {p.value: 0 for p in TicketPriority}
    by_category = {c.value: 0 for c in TicketCategory}

    for t in tickets:
        if t.status.value in by_status:
            by_status[t.status.value] += 1
        if t.priority.value in by_priority:
            by_priority[t.priority.value] += 1
        if t.category.value in by_category:
            by_category[t.category.value] += 1

    return TicketVolumeReport(
        by_status=by_status,
        by_priority=by_priority,
        by_category=by_category,
        total=total
    )
