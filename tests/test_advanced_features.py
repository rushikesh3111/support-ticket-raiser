import pytest

# ----------------- GET /api/v1/kb/ & POST /api/v1/kb/ (10 Tests) -----------------
def test_get_kb_articles_list(client):
    res = client.get("/api/v1/kb/")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_create_kb_article_agent_success(client, agent_token):
    payload = {
        "title": "Configuring Two-Factor Authentication (2FA)",
        "content": "Install Google Authenticator or 1Password. Scan QR code in user profile settings.",
        "category": "IT Support",
        "tags": "2fa, mfa, security, login"
    }
    res = client.post("/api/v1/kb/", json=payload, headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 201
    assert res.json()["title"] == payload["title"]
    assert "id" in res.json()

def test_create_kb_article_admin_success(client, admin_token):
    payload = {
        "title": "Email Migration Guide",
        "content": "Follow the wizard to migrate mailbox from on-prem Exchange to Office 365.",
        "category": "IT Support"
    }
    res = client.post("/api/v1/kb/", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 201

def test_create_kb_article_user_forbidden(client, user_token):
    payload = {
        "title": "Customer attempts writing KB",
        "content": "Content written by customer",
        "category": "General"
    }
    res = client.post("/api/v1/kb/", json=payload, headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 403

def test_create_kb_article_unauthenticated(client):
    payload = {"title": "No auth KB", "content": "Sample content", "category": "IT Support"}
    res = client.post("/api/v1/kb/", json=payload)
    assert res.status_code == 401

def test_search_kb_articles_by_keyword(client):
    res = client.get("/api/v1/kb/?query=VPN")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_search_kb_articles_by_category(client):
    res = client.get("/api/v1/kb/?category=Software")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_get_kb_article_by_id_success(client, agent_token):
    res = client.post(
        "/api/v1/kb/",
        json={"title": "Article To Retrieve", "content": "Article body goes here for test", "category": "Network"},
        headers={"Authorization": f"Bearer {agent_token}"}
    )
    art_id = res.json()["id"]
    get_res = client.get(f"/api/v1/kb/{art_id}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Article To Retrieve"

def test_get_kb_article_not_found(client):
    res = client.get("/api/v1/kb/999999")
    assert res.status_code == 404

def test_create_kb_article_validation_error(client, agent_token):
    res = client.post(
        "/api/v1/kb/",
        json={"title": "Hi", "content": "Short"},
        headers={"Authorization": f"Bearer {agent_token}"}
    )
    assert res.status_code == 422


# ----------------- Bulk Actions & CSAT (10 Tests) -----------------
def test_bulk_status_update(client, agent_token, user_token):
    # Create 2 tickets
    t1 = client.post("/api/v1/tickets/", json={"title": "Bulk ticket 1", "description": "Desc bulk 1"}, headers={"Authorization": f"Bearer {user_token}"}).json()["id"]
    t2 = client.post("/api/v1/tickets/", json={"title": "Bulk ticket 2", "description": "Desc bulk 2"}, headers={"Authorization": f"Bearer {user_token}"}).json()["id"]
    
    payload = {
        "ticket_ids": [t1, t2],
        "action": "status",
        "status_value": "In Progress"
    }
    res = client.post("/api/v1/actions/tickets/bulk", json=payload, headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    assert res.json()["updated_count"] >= 2

def test_bulk_assign_tickets(client, agent_token, user_token):
    t1 = client.post("/api/v1/tickets/", json={"title": "Bulk assign ticket", "description": "Desc bulk assign"}, headers={"Authorization": f"Bearer {user_token}"}).json()["id"]
    payload = {
        "ticket_ids": [t1],
        "action": "assign",
        "assignee_id": 2
    }
    res = client.post("/api/v1/actions/tickets/bulk", json=payload, headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    assert res.json()["updated_count"] == 1

def test_bulk_action_user_forbidden(client, user_token):
    payload = {"ticket_ids": [1], "action": "status", "status_value": "Resolved"}
    res = client.post("/api/v1/actions/tickets/bulk", json=payload, headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 403

def test_bulk_action_unauthenticated(client):
    payload = {"ticket_ids": [1], "action": "status"}
    res = client.post("/api/v1/actions/tickets/bulk", json=payload)
    assert res.status_code == 401

def test_bulk_action_empty_ticket_ids_validation(client, agent_token):
    payload = {"ticket_ids": [], "action": "status"}
    res = client.post("/api/v1/actions/tickets/bulk", json=payload, headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 422

def test_csat_submission_success(client, user_token):
    t_id = client.post("/api/v1/tickets/", json={"title": "Ticket for CSAT", "description": "CSAT rating test"}, headers={"Authorization": f"Bearer {user_token}"}).json()["id"]
    payload = {"score": 5, "feedback": "Superb resolution speed by agent!"}
    res = client.post(f"/api/v1/actions/tickets/{t_id}/csat", json=payload, headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 201
    assert res.json()["score"] == 5

def test_csat_submission_invalid_score_high(client, user_token):
    payload = {"score": 6, "feedback": "Too high"}
    res = client.post("/api/v1/actions/tickets/1/csat", json=payload, headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 422

def test_csat_submission_invalid_score_low(client, user_token):
    payload = {"score": 0, "feedback": "Zero stars"}
    res = client.post("/api/v1/actions/tickets/1/csat", json=payload, headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 422

def test_csat_submission_other_user_forbidden(client, other_user_token):
    res = client.post("/api/v1/actions/tickets/1/csat", json={"score": 4}, headers={"Authorization": f"Bearer {other_user_token}"})
    assert res.status_code == 403

def test_csat_submission_unauthenticated(client):
    res = client.post("/api/v1/actions/tickets/1/csat", json={"score": 5})
    assert res.status_code == 401
