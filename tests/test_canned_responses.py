import pytest

def test_list_canned_responses_agent(client, agent_token):
    res = client.get("/api/v1/canned-responses/", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 4
    assert any("Acknowledge" in c["title"] for c in data)

def test_list_canned_responses_user(client, user_token):
    res = client.get("/api/v1/canned-responses/", headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 200

def test_list_canned_responses_unauthenticated(client):
    res = client.get("/api/v1/canned-responses/")
    assert res.status_code == 401

def test_canned_responses_schema(client, agent_token):
    res = client.get("/api/v1/canned-responses/", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    for macro in res.json():
        assert "id" in macro
        assert "title" in macro
        assert "category" in macro
        assert "body" in macro
