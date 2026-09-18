import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db.session import engine, Base, SessionLocal
from app.models.models import User, UserRole, TicketPriority
from app.core.security import get_password_hash, decode_token
from app.services.sla_service import init_default_sla_policies
from app.services.websocket_manager import ws_manager

# Import API routers
from app.api.v1.routers import (
    auth,
    users,
    tickets,
    comments,
    attachments,
    sla,
    reports,
    notifications,
    audit,
    kb,
    advanced_actions,
    canned_responses,
    enterprise
)
from app.core.middleware import ProductionSecurityMiddleware

def seed_database():
    db = SessionLocal()
    try:
        # Create default admin
        admin = db.query(User).filter(User.email == "admin@supportdesk.com").first()
        if not admin:
            admin = User(
                name="System Administrator",
                email="admin@supportdesk.com",
                hashed_password=get_password_hash("AdminPass123!"),
                role=UserRole.ADMIN,
                department="IT Operations",
                is_active=True
            )
            db.add(admin)

        # Create default agent
        agent = db.query(User).filter(User.email == "agent@supportdesk.com").first()
        if not agent:
            agent = User(
                name="Sarah Jenkins (Senior Agent)",
                email="agent@supportdesk.com",
                hashed_password=get_password_hash("AgentPass123!"),
                role=UserRole.AGENT,
                department="Technical Support",
                is_active=True
            )
            db.add(agent)

        # Create default regular user
        user = db.query(User).filter(User.email == "user@supportdesk.com").first()
        if not user:
            user = User(
                name="John Raver (Customer)",
                email="user@supportdesk.com",
                hashed_password=get_password_hash("UserPass123!"),
                role=UserRole.USER,
                department="Finance & HR",
                is_active=True
            )
            db.add(user)

        # Seed KB Articles
        from app.models.models import KBArticle
        if db.query(KBArticle).count() == 0:
            articles = [
                KBArticle(
                    title="How to reset your Corporate VPN Credentials",
                    content="To reset your VPN password: 1. Navigate to identity.company.internal. 2. Request OTP via corporate authenticator. 3. Update Cisco AnyConnect password.",
                    category="Network",
                    tags="vpn, network, credentials, remote"
                ),
                KBArticle(
                    title="Resolving 504 Gateway Timeout on Production API",
                    content="If you encounter 504 Gateway Timeout: Verify backend service pod status, check nginx keepalive timeout, and ensure Redis caching layer is reachable.",
                    category="Software",
                    tags="504, gateway, timeout, api, nginx"
                ),
                KBArticle(
                    title="Requesting Access to AWS Cloud Production Console",
                    content="Production AWS console access requires Security Team Approval and Manager Signoff via the Access Request ticket category.",
                    category="Access Request",
                    tags="aws, cloud, iam, access, security"
                ),
                KBArticle(
                    title="Hardware Replacement Protocol for Laptops and Monitors",
                    content="Laptops older than 36 months are eligible for refresh. Submit a ticket under Hardware category with asset serial number tag.",
                    category="Hardware",
                    tags="hardware, laptop, replacement, asset"
                )
            ]
            db.add_all(articles)

        db.commit()
        # Seed SLA policies
        init_default_sla_policies(db)
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield
    # Shutdown

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise-grade Monolithic Support Ticket Raiser & Tracker System per final_support_tic.md",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(tickets.router, prefix=settings.API_V1_STR)
app.include_router(comments.router, prefix=settings.API_V1_STR)
app.include_router(attachments.router, prefix=settings.API_V1_STR)
app.include_router(sla.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)
app.include_router(notifications.router, prefix=settings.API_V1_STR)
app.include_router(audit.router, prefix=settings.API_V1_STR)
app.include_router(kb.router, prefix=settings.API_V1_STR)
app.include_router(advanced_actions.router, prefix=settings.API_V1_STR)
app.include_router(canned_responses.router, prefix=settings.API_V1_STR)
app.include_router(enterprise.router, prefix=settings.API_V1_STR)

# Add Security & Performance Middleware
app.add_middleware(ProductionSecurityMiddleware)

# Mount static uploads if exists
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/static/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Health Check
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "architecture": "FastAPI Monolith"
    }

# Realtime WebSocket Endpoint for Ticket updates
@app.websocket("/ws/tickets/{ticket_id}")
async def ticket_websocket_endpoint(websocket: WebSocket, ticket_id: int, token: str = Query(None)):
    # Basic token check
    if not token:
        await websocket.close(code=1008)
        return
    payload = decode_token(token)
    if not payload:
        await websocket.close(code=1008)
        return

    await ws_manager.connect(ticket_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo or broadcast message
            await ws_manager.broadcast_to_ticket(ticket_id, {
                "event": "ticket_update",
                "ticket_id": ticket_id,
                "data": data
            })
    except WebSocketDisconnect:
        ws_manager.disconnect(ticket_id, websocket)
