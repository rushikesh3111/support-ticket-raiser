import pytest

def test_parse_inbound_support_email(client):
    payload = {
        "sender_email": "newcustomer.inbound@company.com",
        "sender_name": "David Inbound",
        "subject": "Exchange server mailbox synchronization error",
        "body_plain": "Getting sync error 0x80040115 when opening Outlook.",
        "category": "Software",
        "priority": "High"
    }
    res = client.post("/api/v1/compliance/inbound-email", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "ticket_created"
    assert "ticket_id" in data
    assert "[Email Inbound]" in data["title"]
    assert data["sla_response_due"] is not None

def test_gdpr_right_to_erasure(client, admin_token):
    # First create a user to erase
    register_res = client.post(
        "/api/v1/auth/register",
        json={"name": "GDPR Subject", "email": "gdpr.subject@example.com", "password": "PassPassword123!"}
    )
    assert register_res.status_code == 201

    # Execute erasure
    res = client.post(
        "/api/v1/compliance/gdpr/erasure?user_email=gdpr.subject@example.com",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
    assert res.json()["status"] == "erasure_completed"
    assert "purged" in res.json()["message"]

def test_gdpr_erasure_admin_forbidden(client, admin_token):
    res = client.post(
        "/api/v1/compliance/gdpr/erasure?user_email=testadmin@example.com",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 400
    assert "Administrators cannot be erased" in res.json()["detail"]

def test_gdpr_erasure_non_admin_forbidden(client, agent_token):
    res = client.post(
        "/api/v1/compliance/gdpr/erasure?user_email=testuser@example.com",
        headers={"Authorization": f"Bearer {agent_token}"}
    )
    assert res.status_code == 403
