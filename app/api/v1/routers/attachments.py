import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.v1.deps import get_current_user
from app.models.models import User, UserRole, Ticket, Attachment
from app.schemas.schemas import AttachmentResponse
from app.core.config import settings
from app.services.audit_service import record_audit

router = APIRouter(tags=["Attachments"])

@router.post("/tickets/{ticket_id}/attachments", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    ticket_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    if current_user.role == UserRole.USER and ticket.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Extension validation
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension '{file_ext}' is not supported. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )

    # Read content to verify size
    contents = await file.read()
    file_size = len(contents)
    if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed limit of {settings.MAX_UPLOAD_SIZE_BYTES // (1024*1024)}MB"
        )

    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    save_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    with open(save_path, "wb") as f:
        f.write(contents)

    attachment = Attachment(
        ticket_id=ticket.id,
        uploaded_by=current_user.id,
        filename=file.filename,
        file_path=save_path,
        file_size=file_size,
        content_type=file.content_type or "application/octet-stream"
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    record_audit(
        db,
        ticket_id=ticket.id,
        performed_by=current_user.id,
        action="ATTACHMENT_UPLOADED",
        details=f"File '{file.filename}' ({file_size} bytes) attached by {current_user.name}"
    )

    return attachment

@router.get("/tickets/{ticket_id}/attachments", response_model=List[AttachmentResponse])
def list_attachments(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    if current_user.role == UserRole.USER and ticket.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return ticket.attachments

@router.get("/attachments/{attachment_id}/download")
def download_attachment(
    attachment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")

    ticket = attachment.ticket
    if current_user.role == UserRole.USER and ticket.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    if not os.path.exists(attachment.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File on disk not found")

    return FileResponse(
        path=attachment.file_path,
        filename=attachment.filename,
        media_type=attachment.content_type
    )
