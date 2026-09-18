import pytest

# ----------------- GET /api/v1/reports/sla-compliance (10 Tests) -----------------
def test_sla_compliance_report_agent(client, agent_token):
    res = client.get("/api/v1/reports/sla-compliance", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    data = res.json()
    assert "total_tickets" in data
    assert "compliant_tickets" in data
    assert "compliance_rate" in data
    assert "response_breaches" in data
    assert "resolution_breaches" in data

def test_sla_compliance_report_admin(client, admin_token):
    res = client.get("/api/v1/reports/sla-compliance", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200

def test_sla_compliance_report_regular_user_forbidden(client, user_token):
    res = client.get("/api/v1/reports/sla-compliance", headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 403

def test_sla_compliance_report_unauthenticated(client):
    res = client.get("/api/v1/reports/sla-compliance")
    assert res.status_code == 401

def test_sla_compliance_rate_bounds(client, agent_token):
    res = client.get("/api/v1/reports/sla-compliance", headers={"Authorization": f"Bearer {agent_token}"})
    rate = res.json()["compliance_rate"]
    assert 0.0 <= rate <= 100.0


# ----------------- GET /api/v1/reports/agent-performance (10 Tests) -----------------
def test_agent_performance_report_agent_success(client, agent_token):
    res = client.get("/api/v1/reports/agent-performance", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "agent_id" in data[0]
    assert "agent_name" in data[0]
    assert "assigned_count" in data[0]
    assert "resolved_count" in data[0]
    assert "avg_resolution_mins" in data[0]

def test_agent_performance_report_admin_success(client, admin_token):
    res = client.get("/api/v1/reports/agent-performance", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200

def test_agent_performance_regular_user_forbidden(client, user_token):
    res = client.get("/api/v1/reports/agent-performance", headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 403

def test_agent_performance_unauthenticated(client):
    res = client.get("/api/v1/reports/agent-performance")
    assert res.status_code == 401

def test_agent_performance_metrics_valid_numbers(client, agent_token):
    res = client.get("/api/v1/reports/agent-performance", headers={"Authorization": f"Bearer {agent_token}"})
    for report in res.json():
        assert report["assigned_count"] >= 0
        assert report["resolved_count"] >= 0
        assert report["avg_resolution_mins"] >= 0.0


# ----------------- GET /api/v1/reports/ticket-volume (10 Tests) -----------------
def test_ticket_volume_report_success(client, agent_token):
    res = client.get("/api/v1/reports/ticket-volume", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    data = res.json()
    assert "by_status" in data
    assert "by_priority" in data
    assert "by_category" in data
    assert "total" in data

def test_ticket_volume_report_admin_success(client, admin_token):
    res = client.get("/api/v1/reports/ticket-volume", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200

def test_ticket_volume_regular_user_forbidden(client, user_token):
    res = client.get("/api/v1/reports/ticket-volume", headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 403

def test_ticket_volume_unauthenticated(client):
    res = client.get("/api/v1/reports/ticket-volume")
    assert res.status_code == 401

def test_ticket_volume_categories_match(client, agent_token):
    res = client.get("/api/v1/reports/ticket-volume", headers={"Authorization": f"Bearer {agent_token}"})
    cats = res.json()["by_category"]
    assert "IT Support" in cats
    assert "Hardware" in cats
    assert "Software" in cats
    assert "Network" in cats
