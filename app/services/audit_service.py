from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import AuditLog, Notification, User, Ticket

def record_audit(
    db: Session,
    ticket_id: int,
    action: str,
    performed_by: Optional[int] = None,
    details: Optional[str] = None,
    meta_info: Optional[Dict[str, Any]] = None
) -> AuditLog:
    log = AuditLog(
        ticket_id=ticket_id,
        performed_by=performed_by,
        action=action,
        details=details,
        meta_info=meta_info,
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    ticket_id: Optional[int] = None,
    channel: str = "in-app"
) -> Notification:
    notif = Notification(
        user_id=user_id,
        ticket_id=ticket_id,
        title=title,
        message=message,
        channel=channel,
        is_read=False,
        created_at=datetime.utcnow()
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif
