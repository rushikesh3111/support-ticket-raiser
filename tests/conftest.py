import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import Base, get_db
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.models import User, UserRole, Ticket, TicketStatus, TicketPriority, TicketCategory
from app.services.sla_service import init_default_sla_policies

# Use a separate SQLite database for testing
TEST_DB_URL = "sqlite:///./test_support_desk.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    
    db = TestingSessionLocal()
    # Seed users
    admin = User(
        name="Test Admin",
        email="testadmin@example.com",
        hashed_password=get_password_hash("AdminPass123!"),
        role=UserRole.ADMIN,
        department="IT",
        is_active=True
    )
    agent = User(
        name="Test Agent",
        email="testagent@example.com",
        hashed_password=get_password_hash("AgentPass123!"),
        role=UserRole.AGENT,
        department="Support",
        is_active=True
    )
    user = User(
        name="Test User",
        email="testuser@example.com",
        hashed_password=get_password_hash("UserPass123!"),
        role=UserRole.USER,
        department="Sales",
        is_active=True
    )
    user2 = User(
        name="Other User",
        email="otheruser@example.com",
        hashed_password=get_password_hash("OtherPass123!"),
        role=UserRole.USER,
        department="Marketing",
        is_active=True
    )
    inactive = User(
        name="Inactive User",
        email="inactive@example.com",
        hashed_password=get_password_hash("InactivePass123!"),
        role=UserRole.USER,
        department="Sales",
        is_active=False
    )
    db.add_all([admin, agent, user, user2, inactive])
    db.commit()
    init_default_sla_policies(db)
    db.close()
    
    yield
    
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_support_desk.db"):
        try:
            os.remove("./test_support_desk.db")
        except Exception:
            pass

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def admin_token(client):
    res = client.post("/api/v1/auth/login", data={"username": "testadmin@example.com", "password": "AdminPass123!"})
    return res.json()["access_token"]

@pytest.fixture
def agent_token(client):
    res = client.post("/api/v1/auth/login", data={"username": "testagent@example.com", "password": "AgentPass123!"})
    return res.json()["access_token"]

@pytest.fixture
def user_token(client):
    res = client.post("/api/v1/auth/login", data={"username": "testuser@example.com", "password": "UserPass123!"})
    return res.json()["access_token"]

@pytest.fixture
def other_user_token(client):
    res = client.post("/api/v1/auth/login", data={"username": "otheruser@example.com", "password": "OtherPass123!"})
    return res.json()["access_token"]
