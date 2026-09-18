import pytest

# ----------------- POST /api/v1/tickets/ (10 Tests) -----------------
def test_create_ticket_success(client, user_token):
    payload = {
        "title": "Cannot access internal VPN portal",
        "description": "Getting error 504 gateway timeout when connecting to VPN",
        "category": "Network",
        "priority": "High"
    }
    res = client.post("/api/v1/tickets/", json=payload, headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == payload["title"]
    assert data["status"] == "Open"
    assert data["priority"] == "High"
    assert data["category"] == "Network"
    assert data["response_due_at"] is not None
    assert data["resolution_due_at"] is not None

def test_create_ticket_critical_priority(client, user_token):
    payload = {
        "title": "Payment gateway down",
        "description": "All customer checkouts failing",
        "category": "Billing",
        "priority": "Critical"
    }
    res = client.post("/api/v1/tickets/", json=payload, headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 201
    assert res.json()["priority"] == "Critical"

def test_create_ticket_unauthenticated(client):
    payload = {"title": "Test Ticket", "description": "Description"}
    res = client.post("/api/v1/tickets/", json=payload)
    assert res.status_code == 401

def test_create_ticket_missing_title(client, user_token):
    payload = {"description": "Only description provided", "priority": "Low"}
    res = client.post("/api/v1/tickets/", json=payload, headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 422

def test_create_ticket_missing_description(client, user_token):
    payload = {"title": "Only title provided"}
    res = client.post("/api/v1/tickets/", json=payload, headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 422

def test_create_ticket_short_title(client, user_token):
    payload = {"title": "Hi", "description": "Valid description length"}
    res = client.post("/api/v1/tickets/", json=payload, headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 422

def test_create_ticket_short_description(client, user_token):
    payload = {"title": "Valid Title Here", "description": "123"}
    res = client.post("/api/v1/tickets/", json=payload, headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 422

def test_create_ticket_invalid_category(client, user_token):
    payload = {"title": "Valid Title Here", "description": "Valid description length", "category": "NonExistentCategory"}
    res = client.post("/api/v1/tickets/", json=payload, headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 422

def test_create_ticket_invalid_priority(client, user_token):
    payload = {"title": "Valid Title Here", "description": "Valid description length", "priority": "SuperUrgent"}
    res = client.post("/api/v1/tickets/", json=payload, headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 422

def test_create_ticket_default_category_priority(client, user_token):
    payload = {"title": "Printer paper jam", "description": "Printer on 2nd floor has paper jam"}
    res = client.post("/api/v1/tickets/", json=payload, headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 201
    assert res.json()["category"] == "IT Support"
    assert res.json()["priority"] == "Medium"


# ----------------- GET /api/v1/tickets/ (10 Tests) -----------------
def test_list_tickets_agent_sees_all(client, agent_token):
    res = client.get("/api/v1/tickets/", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1

def test_list_tickets_user_sees_only_own(client, other_user_token):
    res = client.get("/api/v1/tickets/", headers={"Authorization": f"Bearer {other_user_token}"})
    assert res.status_code == 200
    assert res.json()["total"] == 0

def test_list_tickets_unauthenticated(client):
    res = client.get("/api/v1/tickets/")
    assert res.status_code == 401

def test_list_tickets_filter_by_status(client, agent_token):
    res = client.get("/api/v1/tickets/?status=Open", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    for item in res.json()["items"]:
        assert item["status"] == "Open"

def test_list_tickets_filter_by_priority(client, agent_token):
    res = client.get("/api/v1/tickets/?priority=High", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    for item in res.json()["items"]:
        assert item["priority"] == "High"

def test_list_tickets_filter_by_category(client, agent_token):
    res = client.get("/api/v1/tickets/?category=Network", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    for item in res.json()["items"]:
        assert item["category"] == "Network"

def test_list_tickets_search_query(client, agent_token):
    res = client.get("/api/v1/tickets/?search=VPN", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    assert len(res.json()["items"]) >= 1
    assert "VPN" in res.json()["items"][0]["title"]

def test_list_tickets_pagination_limit(client, agent_token):
    res = client.get("/api/v1/tickets/?limit=2&page=1", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    assert len(res.json()["items"]) <= 2

def test_list_tickets_page_out_of_bounds(client, agent_token):
    res = client.get("/api/v1/tickets/?page=9999", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    assert len(res.json()["items"]) == 0

def test_list_tickets_invalid_limit_validation(client, agent_token):
    res = client.get("/api/v1/tickets/?limit=500", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 422


# ----------------- GET /api/v1/tickets/{id} (10 Tests) -----------------
def test_get_ticket_detail_success(client, user_token):
    # User owns ticket 1
    res = client.get("/api/v1/tickets/1", headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 200
    assert res.json()["id"] == 1
    assert "comments" in res.json()
    assert "attachments" in res.json()
    assert "audit_logs" in res.json()

def test_get_ticket_detail_agent_can_access_any(client, agent_token):
    res = client.get("/api/v1/tickets/1", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    assert res.json()["id"] == 1

def test_get_ticket_detail_admin_can_access_any(client, admin_token):
    res = client.get("/api/v1/tickets/1", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    assert res.json()["id"] == 1

def test_get_ticket_detail_other_user_forbidden(client, other_user_token):
    res = client.get("/api/v1/tickets/1", headers={"Authorization": f"Bearer {other_user_token}"})
    assert res.status_code == 403
    assert "Access denied" in res.json()["detail"]

def test_get_ticket_detail_nonexistent_id(client, admin_token):
    res = client.get("/api/v1/tickets/9999", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 404

def test_get_ticket_detail_unauthenticated(client):
    res = client.get("/api/v1/tickets/1")
    assert res.status_code == 401

def test_get_ticket_detail_invalid_id_type(client, admin_token):
    res = client.get("/api/v1/tickets/abc", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 422

def test_get_ticket_detail_audit_log_present(client, admin_token):
    res = client.get("/api/v1/tickets/1", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    assert len(res.json()["audit_logs"]) >= 1

def test_get_ticket_detail_sla_fields_present(client, agent_token):
    res = client.get("/api/v1/tickets/1", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    data = res.json()
    assert "response_due_at" in data
    assert "resolution_due_at" in data
    assert "is_response_breached" in data

def test_get_ticket_detail_creator_name_populated(client, agent_token):
    res = client.get("/api/v1/tickets/1", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    assert res.json()["creator_name"] == "Test User"


# ----------------- PUT /api/v1/tickets/{id} (10 Tests) -----------------
def test_update_ticket_status_to_in_progress(client, agent_token):
    res = client.put(
        "/api/v1/tickets/1",
        json={"status": "In Progress"},
        headers={"Authorization": f"Bearer {agent_token}"}
    )
    assert res.status_code == 200
    assert res.json()["status"] == "In Progress"

def test_update_ticket_assignee(client, agent_token):
    # Agent user id is 2
    res = client.put(
        "/api/v1/tickets/1",
        json={"assigned_to": 2},
        headers={"Authorization": f"Bearer {agent_token}"}
    )
    assert res.status_code == 200
    assert res.json()["assigned_to"] == 2

def test_update_ticket_status_to_resolved(client, agent_token):
    res = client.put(
        "/api/v1/tickets/1",
        json={"status": "Resolved"},
        headers={"Authorization": f"Bearer {agent_token}"}
    )
    assert res.status_code == 200
    assert res.json()["status"] == "Resolved"
    assert res.json()["resolved_at"] is not None

def test_update_ticket_status_to_closed(client, agent_token):
    res = client.put(
        "/api/v1/tickets/1",
        json={"status": "Closed"},
        headers={"Authorization": f"Bearer {agent_token}"}
    )
    assert res.status_code == 200
    assert res.json()["status"] == "Closed"

def test_update_ticket_invalid_transition_from_closed(client, agent_token):
    res = client.put(
        "/api/v1/tickets/1",
        json={"status": "Open"},
        headers={"Authorization": f"Bearer {agent_token}"}
    )
    assert res.status_code == 400
    assert "Invalid state transition" in res.json()["detail"]

def test_update_ticket_regular_user_cannot_change_status(client, user_token):
    # Ticket 2 was created by user
    res = client.put(
        "/api/v1/tickets/2",
        json={"status": "Resolved"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert res.status_code == 403
    assert "not allowed to transition ticket status" in res.json()["detail"]

def test_update_ticket_regular_user_cannot_change_assignee(client, user_token):
    res = client.put(
        "/api/v1/tickets/2",
        json={"assigned_to": 2},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert res.status_code == 403

def test_update_ticket_assign_to_invalid_user_id(client, agent_token):
    res = client.put(
        "/api/v1/tickets/2",
        json={"assigned_to": 99999},
        headers={"Authorization": f"Bearer {agent_token}"}
    )
    assert res.status_code == 400
    assert "Assignee user does not exist" in res.json()["detail"]

def test_update_ticket_assign_to_customer_fails(client, agent_token):
    # Customer user id is 3
    res = client.put(
        "/api/v1/tickets/2",
        json={"assigned_to": 3},
        headers={"Authorization": f"Bearer {agent_token}"}
    )
    assert res.status_code == 400
    assert "only be assigned to Agents or Admins" in res.json()["detail"]

def test_update_ticket_nonexistent(client, agent_token):
    res = client.put(
        "/api/v1/tickets/9999",
        json={"status": "In Progress"},
        headers={"Authorization": f"Bearer {agent_token}"}
    )
    assert res.status_code == 404


# ----------------- DELETE /api/v1/tickets/{id} (10 Tests) -----------------
def test_delete_ticket_admin_success(client, admin_token):
    # Create ticket to delete
    res_create = client.post(
        "/api/v1/tickets/",
        json={"title": "Ticket to be archived", "description": "Testing archive functionality"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    t_id = res_create.json()["id"]

    res_del = client.delete(f"/api/v1/tickets/{t_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_del.status_code == 200
    assert "archived successfully" in res_del.json()["message"]

def test_delete_ticket_already_archived(client, admin_token):
    # Creating ticket then archiving twice
    res_create = client.post(
        "/api/v1/tickets/",
        json={"title": "Ticket to archive twice", "description": "Testing double archive"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    t_id = res_create.json()["id"]
    client.delete(f"/api/v1/tickets/{t_id}", headers={"Authorization": f"Bearer {admin_token}"})
    
    res_del_again = client.delete(f"/api/v1/tickets/{t_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_del_again.status_code == 400
    assert "already archived" in res_del_again.json()["detail"]

def test_delete_ticket_non_admin_forbidden_agent(client, agent_token):
    res = client.delete("/api/v1/tickets/1", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 403
    assert "Admin privileges required" in res.json()["detail"]

def test_delete_ticket_non_admin_forbidden_user(client, user_token):
    res = client.delete("/api/v1/tickets/1", headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 403
    assert "Admin privileges required" in res.json()["detail"]

def test_delete_ticket_unauthenticated(client):
    res = client.delete("/api/v1/tickets/1")
    assert res.status_code == 401

def test_delete_ticket_not_found(client, admin_token):
    res = client.delete("/api/v1/tickets/99999", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 404

def test_delete_ticket_invalid_id_type(client, admin_token):
    res = client.delete("/api/v1/tickets/xyz", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 422

def test_archived_ticket_excluded_from_normal_listing(client, admin_token):
    res = client.get("/api/v1/tickets/", headers={"Authorization": f"Bearer {admin_token}"})
    for t in res.json()["items"]:
        assert t["status"] != "Archived"

def test_archived_ticket_visible_when_explicitly_filtered(client, admin_token):
    res = client.get("/api/v1/tickets/?status=Archived", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    assert len(res.json()["items"]) >= 1

def test_delete_ticket_creates_audit_log(client, admin_token):
    res_create = client.post(
        "/api/v1/tickets/",
        json={"title": "Audit ticket deletion", "description": "Testing audit log creation on delete"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    t_id = res_create.json()["id"]
    client.delete(f"/api/v1/tickets/{t_id}", headers={"Authorization": f"Bearer {admin_token}"})
    
    res_hist = client.get(f"/api/v1/tickets/{t_id}/history", headers={"Authorization": f"Bearer {admin_token}"})
    actions = [item["action"] for item in res_hist.json()]
    assert "ARCHIVED" in actions
