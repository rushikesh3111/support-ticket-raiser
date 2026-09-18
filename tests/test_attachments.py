import io
import pytest

@pytest.fixture
def attach_ticket_id(client, user_token):
    res = client.post(
        "/api/v1/tickets/",
        json={"title": "Attachment testing ticket", "description": "Used to test file uploads"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    return res.json()["id"]

# ----------------- POST /api/v1/tickets/{id}/attachments (10 Tests) -----------------
def test_upload_attachment_txt_success(client, user_token, attach_ticket_id):
    file_content = b"System log contents for troubleshooting error 500."
    file = io.BytesIO(file_content)
    res = client.post(
        f"/api/v1/tickets/{attach_ticket_id}/attachments",
        files={"file": ("error.log", file, "text/plain")},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert res.status_code == 201
    data = res.json()
    assert data["filename"] == "error.log"
    assert data["file_size"] == len(file_content)
    assert "id" in data

def test_upload_attachment_png_success(client, agent_token, attach_ticket_id):
    file_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    file = io.BytesIO(file_content)
    res = client.post(
        f"/api/v1/tickets/{attach_ticket_id}/attachments",
        files={"file": ("screenshot.png", file, "image/png")},
        headers={"Authorization": f"Bearer {agent_token}"}
    )
    assert res.status_code == 201
    assert res.json()["filename"] == "screenshot.png"

def test_upload_attachment_pdf_success(client, user_token, attach_ticket_id):
    file_content = b"%PDF-1.4 sample invoice or crash dump"
    file = io.BytesIO(file_content)
    res = client.post(
        f"/api/v1/tickets/{attach_ticket_id}/attachments",
        files={"file": ("document.pdf", file, "application/pdf")},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert res.status_code == 201
    assert res.json()["filename"] == "document.pdf"

def test_upload_disallowed_extension(client, user_token, attach_ticket_id):
    file_content = b"malicious executable payload"
    file = io.BytesIO(file_content)
    res = client.post(
        f"/api/v1/tickets/{attach_ticket_id}/attachments",
        files={"file": ("malware.exe", file, "application/octet-stream")},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert res.status_code == 400
    assert "is not supported" in res.json()["detail"]

def test_upload_disallowed_script_extension(client, user_token, attach_ticket_id):
    file = io.BytesIO(b"#!/bin/bash\nrm -rf /")
    res = client.post(
        f"/api/v1/tickets/{attach_ticket_id}/attachments",
        files={"file": ("script.sh", file, "text/x-sh")},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert res.status_code == 400

def test_upload_oversized_file_rejected(client, user_token, attach_ticket_id):
    # 11 MB payload (limit is 10 MB)
    large_payload = b"0" * (11 * 1024 * 1024)
    file = io.BytesIO(large_payload)
    res = client.post(
        f"/api/v1/tickets/{attach_ticket_id}/attachments",
        files={"file": ("huge_dump.log", file, "text/plain")},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert res.status_code == 413
    assert "exceeds maximum allowed limit" in res.json()["detail"]

def test_upload_unauthenticated(client, attach_ticket_id):
    file = io.BytesIO(b"hello")
    res = client.post(
        f"/api/v1/tickets/{attach_ticket_id}/attachments",
        files={"file": ("test.txt", file, "text/plain")}
    )
    assert res.status_code == 401

def test_upload_other_user_forbidden(client, other_user_token, attach_ticket_id):
    file = io.BytesIO(b"other user data")
    res = client.post(
        f"/api/v1/tickets/{attach_ticket_id}/attachments",
        files={"file": ("test.txt", file, "text/plain")},
        headers={"Authorization": f"Bearer {other_user_token}"}
    )
    assert res.status_code == 403

def test_upload_nonexistent_ticket(client, agent_token):
    file = io.BytesIO(b"dummy")
    res = client.post(
        "/api/v1/tickets/99999/attachments",
        files={"file": ("test.txt", file, "text/plain")},
        headers={"Authorization": f"Bearer {agent_token}"}
    )
    assert res.status_code == 404

def test_upload_creates_audit_trail(client, user_token, attach_ticket_id):
    file = io.BytesIO(b"Audit trail verify content")
    res = client.post(
        f"/api/v1/tickets/{attach_ticket_id}/attachments",
        files={"file": ("audit_check.log", file, "text/plain")},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert res.status_code == 201
    
    # Check history
    hist = client.get(f"/api/v1/tickets/{attach_ticket_id}/history", headers={"Authorization": f"Bearer {user_token}"}).json()
    actions = [h["action"] for h in hist]
    assert "ATTACHMENT_UPLOADED" in actions


# ----------------- GET /api/v1/attachments/{id}/download (10 Tests) -----------------
@pytest.fixture
def uploaded_attachment_id(client, user_token, attach_ticket_id):
    file = io.BytesIO(b"Downloadable test file content 12345")
    res = client.post(
        f"/api/v1/tickets/{attach_ticket_id}/attachments",
        files={"file": ("download_sample.txt", file, "text/plain")},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    return res.json()["id"]

def test_download_attachment_owner_success(client, user_token, uploaded_attachment_id):
    res = client.get(f"/api/v1/attachments/{uploaded_attachment_id}/download", headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 200
    assert res.content == b"Downloadable test file content 12345"

def test_download_attachment_agent_success(client, agent_token, uploaded_attachment_id):
    res = client.get(f"/api/v1/attachments/{uploaded_attachment_id}/download", headers={"Authorization": f"Bearer {agent_token}"})
    assert res.status_code == 200
    assert res.content == b"Downloadable test file content 12345"

def test_download_attachment_admin_success(client, admin_token, uploaded_attachment_id):
    res = client.get(f"/api/v1/attachments/{uploaded_attachment_id}/download", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    assert res.content == b"Downloadable test file content 12345"

def test_download_attachment_other_user_forbidden(client, other_user_token, uploaded_attachment_id):
    res = client.get(f"/api/v1/attachments/{uploaded_attachment_id}/download", headers={"Authorization": f"Bearer {other_user_token}"})
    assert res.status_code == 403

def test_download_attachment_unauthenticated(client, uploaded_attachment_id):
    res = client.get(f"/api/v1/attachments/{uploaded_attachment_id}/download")
    assert res.status_code == 401

def test_download_attachment_not_found(client, user_token):
    res = client.get("/api/v1/attachments/99999/download", headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 404

def test_download_attachment_invalid_id_type(client, user_token):
    res = client.get("/api/v1/attachments/xyz/download", headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 422

def test_list_ticket_attachments_endpoint(client, user_token, attach_ticket_id):
    file = io.BytesIO(b"file to list")
    client.post(
        f"/api/v1/tickets/{attach_ticket_id}/attachments",
        files={"file": ("list_sample.txt", file, "text/plain")},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    res = client.get(f"/api/v1/tickets/{attach_ticket_id}/attachments", headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 200
    assert len(res.json()) >= 1

def test_list_ticket_attachments_unauthenticated(client, attach_ticket_id):
    res = client.get(f"/api/v1/tickets/{attach_ticket_id}/attachments")
    assert res.status_code == 401

def test_list_ticket_attachments_other_user_forbidden(client, other_user_token, attach_ticket_id):
    res = client.get(f"/api/v1/tickets/{attach_ticket_id}/attachments", headers={"Authorization": f"Bearer {other_user_token}"})
    assert res.status_code == 403
