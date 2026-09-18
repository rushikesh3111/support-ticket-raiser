import pytest

def test_list_workflow_rules(client, agent_token):
    res = client.get("/api/v1/intelligence/workflows", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) >= 3

def test_create_workflow_rule_admin(client, admin_token):
    payload = {
        "name": "Auto Escalation Rule 99",
        "trigger_event": "ticket.created",
        "condition_field": "priority",
        "condition_value": "Critical",
        "action_type": "tag_vip"
    }
    res = client.post("/api/v1/intelligence/workflows", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 201
    assert res.json()["name"] == payload["name"]

def test_create_workflow_rule_user_forbidden(client, user_token):
    payload = {
        "name": "User Rule Attempt",
        "trigger_event": "ticket.created",
        "condition_field": "priority",
        "condition_value": "High",
        "action_type": "auto_assign"
    }
    res = client.post("/api/v1/intelligence/workflows", json=payload, headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 403

def test_ai_ticket_triage_analysis(client, user_token, agent_token):
    # First create a ticket so it exists in test DB
    create_res = client.post(
        "/api/v1/tickets/",
        json={"title": "VPN gateway outage failure in production", "description": "Crash error 500 occurred", "priority": "High"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    t_id = create_res.json()["id"]

    res = client.get(f"/api/v1/intelligence/tickets/{t_id}/ai-triage", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    data = res.json()
    assert "sentiment" in data
    assert "urgency_score" in data
    assert "suggested_category" in data
    assert "suggested_reply" in data
    assert data["confidence_score"] > 0.8
