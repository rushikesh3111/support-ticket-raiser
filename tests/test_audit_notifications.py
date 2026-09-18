import pytest

# ----------------- GET /api/v1/tickets/{id}/history (10 Tests) -----------------
@pytest.fixture
def audit_ticket_id(client, user_token):
    res = client.post(
        "/api/v1/tickets/",
        json={"title": "Audit verification ticket", "description": "Check full action trail"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    return res.json()["id"]

def test_audit_history_creation_entry(client, user_token, audit_ticket_id):
    res = client.get(f"/api/v1/tickets/{audit_ticket_id}/history", headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) >= 1
    assert logs[0]["action"] == "CREATED"
    assert logs[0]["ticket_id"] == audit_ticket_id

def test_audit_history_records_status_update(client, agent_token, audit_ticket_id):
    client.put(f"/api/v1/tickets/{audit_ticket_id}", json={"status": "In Progress"}, headers={"Authorization": f"Bearer {agent_token}"})
    res = client.get(f"/api/v1/tickets/{audit_ticket_id}/history", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    actions = [log["action"] for log in res.json()]
    assert "UPDATED" in actions

def test_audit_history_records_assignment(client, agent_token, audit_ticket_id):
    client.put(f"/api/v1/tickets/{audit_ticket_id}", json={"assigned_to": 2}, headers={"Authorization": f"Bearer {agent_token}"})
    res = client.get(f"/api/v1/tickets/{audit_ticket_id}/history", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    details = [log["details"] for log in res.json() if log["details"]]
    assert any("assigned to" in d for d in details)

def test_audit_history_records_comment(client, user_token, audit_ticket_id):
    client.post(f"/api/v1/tickets/{audit_ticket_id}/comments/", json={"message": "Audit trace comment"}, headers={"Authorization": f"Bearer {user_token}"})
    res = client.get(f"/api/v1/tickets/{audit_ticket_id}/history", headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 200
    actions = [log["action"] for log in res.json()]
    assert "COMMENT_ADDED" in actions

def test_audit_history_admin_can_view(client, admin_token, audit_ticket_id):
    res = client.get(f"/api/v1/tickets/{audit_ticket_id}/history", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200

def test_audit_history_other_user_forbidden(client, other_user_token, audit_ticket_id):
    res = client.get(f"/api/v1/tickets/{audit_ticket_id}/history", headers={"Authorization": f"Bearer {other_user_token}"})
    assert res.status_code == 403

def test_audit_history_unauthenticated(client, audit_ticket_id):
    res = client.get(f"/api/v1/tickets/{audit_ticket_id}/history")
    assert res.status_code == 401

def test_audit_history_nonexistent_ticket(client, agent_token):
    res = client.get("/api/v1/tickets/99999/history", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 404

def test_audit_history_invalid_ticket_id(client, agent_token):
    res = client.get("/api/v1/tickets/abc/history", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 422

def test_audit_history_timestamp_order(client, agent_token, audit_ticket_id):
    res = client.get(f"/api/v1/tickets/{audit_ticket_id}/history", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    logs = res.json()
    if len(logs) > 1:
        for i in range(len(logs) - 1):
            assert logs[i]["timestamp"] <= logs[i+1]["timestamp"]


# ----------------- Notifications Endpoints (10 Tests) -----------------
def test_get_notifications_agent_success(client, agent_token):
    res = client.get("/api/v1/notifications/", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_get_notifications_user_success(client, user_token):
    res = client.get("/api/v1/notifications/", headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_get_notifications_unauthenticated(client):
    res = client.get("/api/v1/notifications/")
    assert res.status_code == 401

def test_ticket_creation_generates_agent_notifications(client, user_token, agent_token):
    # User creates ticket
    res = client.post(
        "/api/v1/tickets/",
        json={"title": "Check agent notification generation", "description": "Triggering notif"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    t_id = res.json()["id"]

    # Agent checks notifications
    res_notif = client.get("/api/v1/notifications/", headers={"Authorization": f"Bearer {agent_token}"})
    assert res_notif.status_code == 200
    notifs = res_notif.json()
    ticket_notif = [n for n in notifs if n.get("ticket_id") == t_id]
    assert len(ticket_notif) >= 1

def test_mark_notification_read(client, agent_token):
    notifs = client.get("/api/v1/notifications/", headers={"Authorization": f"Bearer {agent_token}"}).json()
    if notifs:
        n_id = notifs[0]["id"]
        res = client.put(f"/api/v1/notifications/{n_id}/read", headers={"Authorization": f"Bearer {agent_token}"})
        assert res.status_code == 200
        assert res.json()["is_read"] is True

def test_mark_all_notifications_read(client, agent_token):
    res = client.put("/api/v1/notifications/read-all", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    assert "marked as read" in res.json()["message"]

def test_mark_notification_read_nonexistent(client, agent_token):
    res = client.put("/api/v1/notifications/99999/read", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 404

def test_mark_notification_read_unauthenticated(client):
    res = client.put("/api/v1/notifications/1/read")
    assert res.status_code == 401

def test_mark_notification_read_other_user_forbidden(client, other_user_token):
    # Other user tries to mark notification belonging to agent or user
    res = client.put("/api/v1/notifications/1/read", headers={"Authorization": f"Bearer {other_user_token}"})
    # Will be 404 because query filters by user_id
    assert res.status_code == 404

def test_notification_schema_integrity(client, agent_token):
    res = client.get("/api/v1/notifications/", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    if len(res.json()) > 0:
        n = res.json()[0]
        for field in ["id", "title", "message", "channel", "is_read", "created_at"]:
            assert field in n
