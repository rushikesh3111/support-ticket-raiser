from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.v1.deps import get_current_user, require_agent_or_admin
from app.models.models import User, Ticket, Comment, AuditLog, TicketStatus
from app.services.audit_service import record_audit

router = APIRouter(prefix="/canned-responses", tags=["Canned Responses"])

DEFAULT_CANNED_MACROS = [
    {
        "id": 1,
        "title": "Acknowledge & Investigating",
        "category": "General",
        "body": "Hello, thank you for raising this issue. We have acknowledged the ticket and our engineering team is actively investigating. We will update you shortly."
    },
    {
        "id": 2,
        "title": "Request Error Logs / Diagnostic Info",
        "category": "Troubleshooting",
        "body": "Could you please provide the timestamp of the error, browser/OS version, and any relevant console screenshot or log attachments?"
    },
    {
        "id": 3,
        "title": "VPN / Network Cache Reset",
        "category": "Network",
        "body": "Please disconnect from the VPN client, flush DNS using `ipconfig /flushdns`, and reconnect using Cisco AnyConnect."
    },
    {
        "id": 4,
        "title": "Resolution Confirmation & Close",
        "category": "Resolution",
        "body": "We have resolved the root cause of this incident. Please verify on your side and submit the CSAT survey when convenient. Thank you for your patience!"
    }
]

@router.get("/")
def list_canned_responses(
    current_user: User = Depends(get_current_user)
):
    return DEFAULT_CANNED_MACROS
