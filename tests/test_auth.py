import pytest

# 10 Tests for POST /api/v1/auth/login
def test_login_success_form_data(client):
    res = client.post("/api/v1/auth/login", data={"username": "testadmin@example.com", "password": "AdminPass123!"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "testadmin@example.com"
    assert data["user"]["role"] == "admin"

def test_login_invalid_password(client):
    res = client.post("/api/v1/auth/login", data={"username": "testadmin@example.com", "password": "WrongPassword"})
    assert res.status_code == 401
    assert "Invalid email or password" in res.json()["detail"]

def test_login_nonexistent_user(client):
    res = client.post("/api/v1/auth/login", data={"username": "nobody@example.com", "password": "AnyPassword123!"})
    assert res.status_code == 401

def test_login_inactive_user(client):
    res = client.post("/api/v1/auth/login", data={"username": "inactive@example.com", "password": "InactivePass123!"})
    assert res.status_code == 403
    assert "deactivated" in res.json()["detail"]

def test_login_json_success(client):
    res = client.post("/api/v1/auth/login/json", json={"email": "testagent@example.com", "password": "AgentPass123!"})
    assert res.status_code == 200
    assert "access_token" in res.json()
    assert res.json()["user"]["role"] == "agent"

def test_login_json_invalid_credentials(client):
    res = client.post("/api/v1/auth/login/json", json={"email": "testagent@example.com", "password": "BadPassword"})
    assert res.status_code == 401

def test_login_missing_password_field(client):
    res = client.post("/api/v1/auth/login/json", json={"email": "testagent@example.com"})
    assert res.status_code == 422

def test_login_invalid_email_format(client):
    res = client.post("/api/v1/auth/login/json", json={"email": "not-an-email", "password": "password"})
    assert res.status_code == 422

def test_login_empty_body(client):
    res = client.post("/api/v1/auth/login/json", json={})
    assert res.status_code == 422

def test_login_rate_or_header_check(client):
    res = client.post("/api/v1/auth/login", data={"username": "testuser@example.com", "password": "UserPass123!"})
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("application/json")

# 10 Tests for POST /api/v1/auth/register
def test_register_new_user_success(client):
    payload = {
        "name": "New Registered User",
        "email": "newuser@example.com",
        "password": "ValidPassword123!",
        "role": "user",
        "department": "Engineering"
    }
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "newuser@example.com"
    assert data["name"] == "New Registered User"
    assert "id" in data

def test_register_duplicate_email(client):
    payload = {
        "name": "Duplicate User",
        "email": "newuser@example.com",
        "password": "ValidPassword123!",
        "role": "user"
    }
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 400
    assert "already exists" in res.json()["detail"]

def test_register_missing_name(client):
    payload = {"email": "noname@example.com", "password": "password123"}
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 422

def test_register_short_password(client):
    payload = {"name": "Short Pass", "email": "short@example.com", "password": "123"}
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 422

def test_register_invalid_email(client):
    payload = {"name": "Bad Email", "email": "invalid-email-address", "password": "ValidPassword123!"}
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 422

def test_register_with_agent_role(client):
    payload = {"name": "New Agent", "email": "brandnewagent@example.com", "password": "AgentPassword123!", "role": "agent"}
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 201
    assert res.json()["role"] == "agent"

def test_register_empty_body(client):
    res = client.post("/api/v1/auth/register", json={})
    assert res.status_code == 422

def test_register_default_department(client):
    payload = {"name": "No Dept User", "email": "nodept@example.com", "password": "Password123!"}
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 201
    assert res.json()["department"] == "General"

def test_register_whitespaced_name_validation(client):
    payload = {"name": "X", "email": "tinyname@example.com", "password": "Password123!"}
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 422

def test_register_then_login(client):
    email = "flowuser@example.com"
    res = client.post("/api/v1/auth/register", json={"name": "Flow User", "email": email, "password": "FlowPassword123!"})
    assert res.status_code == 201
    res_login = client.post("/api/v1/auth/login", data={"username": email, "password": "FlowPassword123!"})
    assert res_login.status_code == 200
    assert res_login.json()["user"]["email"] == email

# 10 Tests for GET /api/v1/auth/me
def test_get_me_success_admin(client, admin_token):
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "testadmin@example.com"
    assert res.json()["role"] == "admin"

def test_get_me_success_agent(client, agent_token):
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "testagent@example.com"
    assert res.json()["role"] == "agent"

def test_get_me_success_user(client, user_token):
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "testuser@example.com"
    assert res.json()["role"] == "user"

def test_get_me_missing_token(client):
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401

def test_get_me_invalid_token(client):
    res = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid.token.payload"})
    assert res.status_code == 401

def test_get_me_malformed_auth_header(client):
    res = client.get("/api/v1/auth/me", headers={"Authorization": "NotBearer 12345"})
    assert res.status_code == 401

def test_get_me_expired_token(client):
    from app.core.security import create_access_token
    from datetime import timedelta
    expired_token = create_access_token(subject=1, expires_delta=timedelta(minutes=-10))
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert res.status_code == 401

def test_get_me_nonexistent_user_id_in_token(client):
    from app.core.security import create_access_token
    fake_token = create_access_token(subject=999999)
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {fake_token}"})
    assert res.status_code == 401

def test_get_me_inactive_user_token(client):
    from app.core.security import create_access_token
    from tests.conftest import TestingSessionLocal
    # Subject of inactive user
    db = TestingSessionLocal()
    from app.models.models import User
    inactive = db.query(User).filter(User.email == "inactive@example.com").first()
    inactive_token = create_access_token(subject=inactive.id)
    db.close()
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {inactive_token}"})
    assert res.status_code == 403

def test_get_me_verify_fields(client, user_token):
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {user_token}"})
    data = res.json()
    assert "id" in data
    assert "name" in data
    assert "is_active" in data
    assert data["is_active"] is True
