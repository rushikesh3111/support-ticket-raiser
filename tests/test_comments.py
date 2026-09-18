import pytest

# ----------------- POST /api/v1/tickets/{id}/comments (10 Tests) -----------------
@pytest.fixture
def active_ticket_id(client, user_token):
    res = client.post(
        "/api/v1/tickets/",
        json={"title": "Ticket for commenting tests", "description": "Comment functionality validation"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    return res.json()["id"]

def test_add_comment_by_creator_success(client, user_token, active_ticket_id):
    res = client.post(
        f"/api/v1/tickets/{active_ticket_id}/comments/",
        json={"message": "Here is additional context regarding the issue."},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert res.status_code == 201
    data = res.json()
    assert data["message"] == "Here is additional context regarding the issue."
    assert data["is_internal"] is False
    assert data["author_name"] == "Test User"

def test_add_comment_by_agent_success(client, agent_token, active_ticket_id):
    res = client.post(
        f"/api/v1/tickets/{active_ticket_id}/comments/",
        json={"message": "We are looking into this right away."},
        headers={"Authorization": f"Bearer {agent_token}"}
    )
    assert res.status_code == 201
    assert res.json()["author_role"] == "agent"

def test_add_internal_note_by_agent(client, agent_token, active_ticket_id):
    res = client.post(
        f"/api/v1/tickets/{active_ticket_id}/comments/",
        json={"message": "Internal note: Escalating to tier 2 network admin.", "is_internal": True},
        headers={"Authorization": f"Bearer {agent_token}"}
    )
    assert res.status_code == 201
    assert res.json()["is_internal"] is True

def test_regular_user_cannot_post_internal_note(client, user_token, active_ticket_id):
    res = client.post(
        f"/api/v1/tickets/{active_ticket_id}/comments/",
        json={"message": "Attempting internal note as user", "is_internal": True},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert res.status_code == 403
    assert "Regular users cannot post internal agent notes" in res.json()["detail"]

def test_add_comment_empty_message(client, user_token, active_ticket_id):
    res = client.post(
        f"/api/v1/tickets/{active_ticket_id}/comments/",
        json={"message": ""},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert res.status_code == 422

def test_add_comment_unauthenticated(client, active_ticket_id):
    res = client.post(
        f"/api/v1/tickets/{active_ticket_id}/comments/",
        json={"message": "No auth header"}
    )
    assert res.status_code == 401

def test_add_comment_other_user_forbidden(client, other_user_token, active_ticket_id):
    res = client.post(
        f"/api/v1/tickets/{active_ticket_id}/comments/",
        json={"message": "Trying to comment on another user's ticket"},
        headers={"Authorization": f"Bearer {other_user_token}"}
    )
    assert res.status_code == 403
    assert "Access denied" in res.json()["detail"]

def test_add_comment_nonexistent_ticket(client, agent_token):
    res = client.post(
        "/api/v1/tickets/99999/comments/",
        json={"message": "Comment on ghost ticket"},
        headers={"Authorization": f"Bearer {agent_token}"}
    )
    assert res.status_code == 404

def test_add_comment_on_closed_ticket_blocked(client, agent_token, active_ticket_id):
    # Transition ticket to closed
    client.put(f"/api/v1/tickets/{active_ticket_id}", json={"status": "In Progress"}, headers={"Authorization": f"Bearer {agent_token}"})
    client.put(f"/api/v1/tickets/{active_ticket_id}", json={"status": "Resolved"}, headers={"Authorization": f"Bearer {agent_token}"})
    client.put(f"/api/v1/tickets/{active_ticket_id}", json={"status": "Closed"}, headers={"Authorization": f"Bearer {agent_token}"})

    res = client.post(
        f"/api/v1/tickets/{active_ticket_id}/comments/",
        json={"message": "Trying to comment after ticket is closed"},
        headers={"Authorization": f"Bearer {agent_token}"}
    )
    assert res.status_code == 400
    assert "Cannot comment on a closed ticket" in res.json()["detail"]

def test_add_comment_sets_first_responded_at(client, user_token, agent_token):
    res = client.post(
        "/api/v1/tickets/",
        json={"title": "Ticket SLA response timestamp test", "description": "Verify first_responded_at"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    t_id = res.json()["id"]
    
    # Agent posts response
    client.post(
        f"/api/v1/tickets/{t_id}/comments/",
        json={"message": "Agent first response acknowledging issue"},
        headers={"Authorization": f"Bearer {agent_token}"}
    )
    
    # Check ticket details
    t_detail = client.get(f"/api/v1/tickets/{t_id}", headers={"Authorization": f"Bearer {agent_token}"}).json()
    assert t_detail["first_responded_at"] is not None


# ----------------- GET /api/v1/tickets/{id}/comments (10 Tests) -----------------
def test_get_comments_list_success(client, agent_token, active_ticket_id):
    client.post(
        f"/api/v1/tickets/{active_ticket_id}/comments/",
        json={"message": "First message for list check"},
        headers={"Authorization": f"Bearer {agent_token}"}
    )
    res = client.get(f"/api/v1/tickets/{active_ticket_id}/comments/", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) >= 1

def test_get_comments_user_cannot_see_internal_notes(client, user_token, agent_token):
    # Create ticket
    t_res = client.post(
        "/api/v1/tickets/",
        json={"title": "Internal notes hiding test", "description": "Testing privacy of internal notes"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    t_id = t_res.json()["id"]
    # Agent adds regular comment and internal note
    client.post(f"/api/v1/tickets/{t_id}/comments/", json={"message": "Public comment"}, headers={"Authorization": f"Bearer {agent_token}"})
    client.post(f"/api/v1/tickets/{t_id}/comments/", json={"message": "Private note 123", "is_internal": True}, headers={"Authorization": f"Bearer {agent_token}"})

    # User fetches comments
    u_res = client.get(f"/api/v1/tickets/{t_id}/comments/", headers={"Authorization": f"Bearer {user_token}"})
    assert u_res.status_code == 200
    comments = u_res.json()
    assert len(comments) == 1
    assert comments[0]["message"] == "Public comment"
    for c in comments:
        assert c["is_internal"] is False

def test_get_comments_agent_sees_internal_notes(client, user_token, agent_token):
    t_res = client.post(
        "/api/v1/tickets/",
        json={"title": "Agent internal note visibility", "description": "Testing visibility"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    t_id = t_res.json()["id"]
    client.post(f"/api/v1/tickets/{t_id}/comments/", json={"message": "Public comment"}, headers={"Authorization": f"Bearer {agent_token}"})
    client.post(f"/api/v1/tickets/{t_id}/comments/", json={"message": "Private note 456", "is_internal": True}, headers={"Authorization": f"Bearer {agent_token}"})

    a_res = client.get(f"/api/v1/tickets/{t_id}/comments/", headers={"Authorization": f"Bearer {agent_token}"})
    assert a_res.status_code == 200
    assert len(a_res.json()) == 2
    has_internal = any(c["is_internal"] for c in a_res.json())
    assert has_internal is True

def test_get_comments_unauthenticated(client, active_ticket_id):
    res = client.get(f"/api/v1/tickets/{active_ticket_id}/comments/")
    assert res.status_code == 401

def test_get_comments_other_user_forbidden(client, other_user_token, active_ticket_id):
    res = client.get(f"/api/v1/tickets/{active_ticket_id}/comments/", headers={"Authorization": f"Bearer {other_user_token}"})
    assert res.status_code == 403

def test_get_comments_nonexistent_ticket(client, agent_token):
    res = client.get("/api/v1/tickets/99999/comments/", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 404

def test_get_comments_invalid_ticket_id_type(client, agent_token):
    res = client.get("/api/v1/tickets/invalid/comments/", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 422

def test_get_comments_chronological_order(client, agent_token, active_ticket_id):
    res = client.get(f"/api/v1/tickets/{active_ticket_id}/comments/", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    comments = res.json()
    if len(comments) > 1:
        for i in range(len(comments) - 1):
            assert comments[i]["created_at"] <= comments[i+1]["created_at"]

def test_get_comments_empty_for_fresh_ticket(client, user_token):
    res = client.post(
        "/api/v1/tickets/",
        json={"title": "Fresh ticket no comments", "description": "Checking empty comments response"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    t_id = res.json()["id"]
    c_res = client.get(f"/api/v1/tickets/{t_id}/comments/", headers={"Authorization": f"Bearer {user_token}"})
    assert c_res.status_code == 200
    assert c_res.json() == []

def test_get_comments_response_schema_integrity(client, agent_token, active_ticket_id):
    client.post(
        f"/api/v1/tickets/{active_ticket_id}/comments/",
        json={"message": "Schema check message"},
        headers={"Authorization": f"Bearer {agent_token}"}
    )
    res = client.get(f"/api/v1/tickets/{active_ticket_id}/comments/", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    c = res.json()[0]
    for field in ["id", "ticket_id", "author_id", "author_name", "author_role", "message", "is_internal", "created_at"]:
        assert field in c
