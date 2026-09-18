from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.v1.deps import get_current_user, require_admin
from app.models.models import User, SLAPolicy, TicketPriority
from app.schemas.schemas import SLAPolicyCreate, SLAPolicyResponse
from app.services.sla_service import check_and_update_sla_breaches

router = APIRouter(prefix="/sla", tags=["SLA Policies"])

@router.get("/policies", response_model=List[SLAPolicyResponse])
def get_sla_policies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    policies = db.query(SLAPolicy).all()
    return policies

@router.post("/policies", response_model=SLAPolicyResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_sla_policy(
    payload: SLAPolicyCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    existing = db.query(SLAPolicy).filter(SLAPolicy.priority == payload.priority).first()
    if existing:
        existing.response_time_mins = payload.response_time_mins
        existing.resolution_time_mins = payload.resolution_time_mins
        existing.description = payload.description
        db.commit()
        db.refresh(existing)
        return existing
    
    new_policy = SLAPolicy(
        priority=payload.priority,
        response_time_mins=payload.response_time_mins,
        resolution_time_mins=payload.resolution_time_mins,
        description=payload.description
    )
    db.add(new_policy)
    db.commit()
    db.refresh(new_policy)
    return new_policy

@router.post("/trigger-check")
def trigger_sla_check(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    breached_count = check_and_update_sla_breaches(db)
    return {
        "status": "success",
        "breaches_detected": breached_count,
        "message": f"Evaluated open tickets for SLA breaches. Updated {breached_count} tickets."
    }
