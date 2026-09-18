import pytest

@pytest.fixture
def agentic_ticket_id(client, user_token):
    res = client.post(
        "/api/v1/tickets/",
        json={"title": "Agentic test ticket for RCA swarm", "description": "Analyzing database connection latency", "priority": "High", "category": "Software"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    return res.json()["id"]

def test_get_ticket_proposals(client, agent_token, agentic_ticket_id):
    res = client.get(f"/api/v1/agentic/tickets/{agentic_ticket_id}/proposals", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_trigger_agentic_swarm(client, agent_token, agentic_ticket_id):
    res = client.post(f"/api/v1/agentic/tickets/{agentic_ticket_id}/run-swarm", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    data = res.json()
    assert "agent_name" in data
    assert "mcp_tools_invoked" in data
    assert len(data["mcp_tools_invoked"]) >= 1
    assert data["requires_human_approval"] is True

def test_hitl_approval_gate(client, agent_token, agentic_ticket_id):
    # Trigger proposal
    prop_res = client.post(f"/api/v1/agentic/tickets/{agentic_ticket_id}/run-swarm", headers={"Authorization": f"Bearer {agent_token}"})
    assert prop_res.status_code == 200
    p_id = prop_res.json()["id"]

    # Approve action
    appr_res = client.post(f"/api/v1/agentic/proposals/{p_id}/approve", headers={"Authorization": f"Bearer {agent_token}"})
    assert appr_res.status_code == 200
    assert appr_res.json()["approval_status"] == "approved"

def test_detect_duplicate_tickets(client, agentic_ticket_id):
    res = client.get(f"/api/v1/agentic/tickets/{agentic_ticket_id}/detect-duplicates")
    assert res.status_code == 200
    data = res.json()
    assert "duplicate_candidates" in data
    assert "semantic_similarity" in data

def test_semantic_search(client, agentic_ticket_id):
    payload = {"query": "latency", "limit": 5}
    res = client.post("/api/v1/agentic/semantic-search", json=payload)
    assert res.status_code == 200
    assert "results" in res.json()

def test_enterprise_integrations_status(client, agent_token):
    res = client.get("/api/v1/agentic/integrations", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    data = res.json()
    assert "jira" in data
    assert "github" in data
    assert "datadog" in data

def test_sync_jira_issue(client, agent_token, agentic_ticket_id):
    res = client.post(f"/api/v1/agentic/integrations/sync-jira?ticket_id={agentic_ticket_id}", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    assert "jira_key" in res.json()
    assert "synced" == res.json()["status"]

def test_sso_mfa_config(client):
    res = client.get("/api/v1/agentic/sso-mfa-config")
    assert res.status_code == 200
    data = res.json()
    assert data["provider"] == "Okta"
    assert data["mfa_enforced"] is True
