import pytest

# ----------------- GET /api/v1/sla/policies & POST /api/v1/sla/policies (10 Tests) -----------------
def test_get_sla_policies_success(client, agent_token):
    res = client.get("/api/v1/sla/policies", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) >= 4  # Critical, High, Medium, Low seeded

def test_get_sla_policies_unauthenticated(client):
    res = client.get("/api/v1/sla/policies")
    assert res.status_code == 401

def test_get_sla_policies_has_all_priorities(client, user_token):
    res = client.get("/api/v1/sla/policies", headers={"Authorization": f"Bearer {user_token}"})
    priorities = [p["priority"] for p in res.json()]
    assert "Critical" in priorities
    assert "High" in priorities
    assert "Medium" in priorities
    assert "Low" in priorities

def test_create_or_update_sla_policy_admin(client, admin_token):
    payload = {
        "priority": "Critical",
        "response_time_mins": 25,
        "resolution_time_mins": 90,
        "description": "Updated Critical SLA"
    }
    res = client.post("/api/v1/sla/policies", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 201
    assert res.json()["response_time_mins"] == 25
    assert res.json()["resolution_time_mins"] == 90

def test_create_or_update_sla_policy_agent_forbidden(client, agent_token):
    payload = {"priority": "Low", "response_time_mins": 500, "resolution_time_mins": 3000}
    res = client.post("/api/v1/sla/policies", json=payload, headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 403
    assert "Operation not permitted" in res.json()["detail"]

def test_create_or_update_sla_policy_user_forbidden(client, user_token):
    payload = {"priority": "Low", "response_time_mins": 500, "resolution_time_mins": 3000}
    res = client.post("/api/v1/sla/policies", json=payload, headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 403

def test_create_sla_policy_invalid_times(client, admin_token):
    payload = {"priority": "Medium", "response_time_mins": -10, "resolution_time_mins": 0}
    res = client.post("/api/v1/sla/policies", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 422

def test_create_sla_policy_invalid_priority_enum(client, admin_token):
    payload = {"priority": "UltraSuperUrgent", "response_time_mins": 10, "resolution_time_mins": 30}
    res = client.post("/api/v1/sla/policies", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 422

def test_trigger_sla_check_endpoint(client, agent_token):
    res = client.post("/api/v1/sla/trigger-check", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    assert res.json()["status"] == "success"
    assert "breaches_detected" in res.json()

def test_trigger_sla_check_unauthenticated(client):
    res = client.post("/api/v1/sla/trigger-check")
    assert res.status_code == 401
