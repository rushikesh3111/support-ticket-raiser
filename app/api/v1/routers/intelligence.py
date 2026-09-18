from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.v1.deps import get_current_user, require_admin, require_agent_or_admin
from app.models.models import User, Ticket, Comment, AuditLog, TicketStatus, TicketPriority, TicketCategory, UserRole
from app.services.audit_service import record_audit, create_notification

router = APIRouter(prefix="/intelligence", tags=["AI & Automation"])

class AIAnalysisResponse(BaseModel):
    ticket_id: int
    sentiment: str
    urgency_score: int  # 1-100
    suggested_category: str
    suggested_priority: str
    confidence_score: float
    recommended_sop: str
    suggested_reply: str

class WorkflowRuleCreate(BaseModel):
    name: str = Field(..., min_length=3)
    trigger_event: str = "ticket.created"  # ticket.created, sla.warning, priority.critical
    condition_field: str = "priority"
    condition_value: str = "Critical"
    action_type: str = "escalate_notification"  # auto_assign, escalate_notification, tag_vip

WORKFLOW_RULES = [
    {
        "id": "wf_1",
        "name": "Auto-Escalate Critical Payment & Database Failures",
        "trigger_event": "ticket.created",
        "condition_field": "priority",
        "condition_value": "Critical",
        "action_type": "notify_oncall_engineer",
        "is_active": True
    },
    {
        "id": "wf_2",
        "name": "High Urgency Customer Sentiment Warning",
        "trigger_event": "sentiment.negative",
        "condition_field": "sentiment",
        "condition_value": "Frustrated",
        "action_type": "elevate_priority_high",
        "is_active": True
    },
    {
        "id": "wf_3",
        "name": "SLA 75% Expiry Warning Alert",
        "trigger_event": "sla.warning",
        "condition_field": "time_left_pct",
        "condition_value": "< 25%",
        "action_type": "alert_team_lead",
        "is_active": True
    }
]

@router.get("/workflows")
def list_workflow_rules(
    current_user: User = Depends(require_agent_or_admin)
):
    return WORKFLOW_RULES

@router.post("/workflows", status_code=status.HTTP_201_CREATED)
def create_workflow_rule(
    payload: WorkflowRuleCreate,
    current_user: User = Depends(require_admin)
):
    new_rule = {
        "id": f"wf_{len(WORKFLOW_RULES) + 1}",
        "name": payload.name,
        "trigger_event": payload.trigger_event,
        "condition_field": payload.condition_field,
        "condition_value": payload.condition_value,
        "action_type": payload.action_type,
        "is_active": True
    }
    WORKFLOW_RULES.append(new_rule)
    return new_rule

@router.get("/tickets/{ticket_id}/ai-triage", response_model=AIAnalysisResponse)
def analyze_ticket_with_ai(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    text_lower = f"{ticket.title} {ticket.description}".lower()

    # Rule-based NLP heuristics
    if any(k in text_lower for k in ["crash", "down", "outage", "production", "urgent", "failed", "emergency"]):
        sentiment = "High Frustration / Urgency"
        urgency = 94
        s_priority = "Critical"
    elif any(k in text_lower for k in ["slow", "error", "bug", "cannot", "issue", "problem"]):
        sentiment = "Moderately Concerned"
        urgency = 65
        s_priority = "High"
    else:
        sentiment = "Neutral / Inquisitive"
        urgency = 32
        s_priority = "Medium"

    # Category prediction
    if any(k in text_lower for k in ["vpn", "wifi", "dns", "gateway", "ip", "connection"]):
        s_category = "Network"
        sop = "SOP-NET-402: Check AnyConnect logs, flush DNS, verify gateway ping."
        reply = "Hello! Our automated diagnostics indicate a possible network route or gateway mismatch. Please verify if reconnecting through AnyConnect solves the timeout."
    elif any(k in text_lower for k in ["laptop", "screen", "keyboard", "monitor", "cable", "mouse"]):
        s_category = "Hardware"
        sop = "SOP-HW-101: Verify asset serial number and schedule hardware diagnostics."
        reply = "Hi there, we've registered your hardware query. Please ensure the asset tag barcode on the bottom of the device is readily accessible."
    elif any(k in text_lower for k in ["bill", "invoice", "payment", "card", "charge"]):
        s_category = "Billing"
        sop = "SOP-FIN-204: Inspect Stripe/charge gateway transaction ID."
        reply = "Thank you for reaching out regarding billing. Our accounts team has been notified to inspect the payment gateway receipt."
    else:
        s_category = "IT Support"
        sop = "SOP-GEN-001: General triaging and tier-1 ticket resolution."
        reply = "Hello, thank you for providing the context. Our engineering team is reviewing your report and will update you shortly."

    return AIAnalysisResponse(
        ticket_id=ticket.id,
        sentiment=sentiment,
        urgency_score=urgency,
        suggested_category=s_category,
        suggested_priority=s_priority,
        confidence_score=0.96,
        recommended_sop=sop,
        suggested_reply=reply
    )
