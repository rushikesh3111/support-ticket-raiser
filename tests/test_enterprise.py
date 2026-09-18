import pytest

def test_get_auto_routing_rules(client, agent_token):
    res = client.get("/api/v1/enterprise/auto-routing", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    assert "rules" in res.json()

def test_set_auto_routing_rule_admin(client, admin_token):
    payload = {"category": "Billing", "agent_id": 2}
    res = client.post("/api/v1/enterprise/auto-routing", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    assert res.json()["status"] == "success"

def test_set_auto_routing_rule_forbidden_user(client, user_token):
    payload = {"category": "Billing", "agent_id": 2}
    res = client.post("/api/v1/enterprise/auto-routing", json=payload, headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 403

def test_list_webhooks(client, agent_token):
    res = client.get("/api/v1/enterprise/webhooks", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) >= 1

def test_register_webhook_admin(client, admin_token):
    payload = {
        "name": "Custom Integration Webhook",
        "url": "https://api.company.com/webhook/tickets",
        "events": ["ticket.created"]
    }
    res = client.post("/api/v1/enterprise/webhooks", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 201
    assert res.json()["name"] == payload["name"]

def test_test_webhook_dispatch(client, agent_token):
    res = client.post("/api/v1/enterprise/webhooks/wh_slack_it/test", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    assert res.json()["status"] == "delivered"
    assert res.json()["latency_ms"] > 0

def test_system_diagnostics_admin(client, admin_token):
    res = client.get("/api/v1/enterprise/system-diagnostics", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["system_status"] == "OPERATIONAL"
    assert "diagnostics" in data
    assert data["diagnostics"]["total_users"] >= 1
