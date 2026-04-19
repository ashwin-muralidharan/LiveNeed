"""Integration tests for Admin endpoints (with JWT auth).

Tests:
  - GET /admin/volunteers — list all volunteers (auth required)
  - PATCH /admin/volunteers/{id} — update volunteer
  - DELETE /admin/volunteers/{id} — remove volunteer
  - GET /admin/needs — list all needs (including fulfilled)
  - PATCH /admin/needs/{id}/status — change need status
  - DELETE /admin/needs/{id} — remove need
  - Unauthenticated access returns 401
  - Auth endpoints: login, register, approve, reject
"""

import pytest
from models import AdminUser, Need, User
from routers.auth import hash_password


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_test_admin(client):
    """Create a test admin directly in DB and return auth headers."""
    from database import get_db
    gen = client.app.dependency_overrides[get_db]()
    db = next(gen)

    # Check if already exists
    existing = db.query(AdminUser).filter(AdminUser.email == "testadmin@example.com").first()
    if existing is None:
        admin = AdminUser(
            email="testadmin@example.com",
            name="Test Admin",
            hashed_password=hash_password("testpass"),
            is_approved=True,
        )
        db.add(admin)
        db.commit()

    # Login to get token
    resp = client.post("/auth/login", json={"email": "testadmin@example.com", "password": "testpass"})
    assert resp.status_code == 200, resp.text
    token = resp.json()["token"]
    return {"Authorization": f"Bearer {token}"}


def _submit_need(client, text="Test need for admin"):
    resp = client.post("/submit-need", json={"raw_text": text})
    assert resp.status_code == 200
    return resp.json()["need_id"]


def _register_vol(client, name="Admin Test Vol", email=None, skills="general"):
    email = email or f"{name.lower().replace(' ', '_')}@example.com"
    resp = client.post("/register-volunteer", json={
        "name": name, "email": email, "role": "volunteer", "skills": skills,
    })
    assert resp.status_code == 200
    return resp.json()["volunteer_id"]


def _get_db(client):
    from database import get_db
    gen = client.app.dependency_overrides[get_db]()
    return next(gen)


# ---------------------------------------------------------------------------
# Auth required — unauthenticated access
# ---------------------------------------------------------------------------

class TestAdminRequiresAuth:
    def test_list_volunteers_no_auth(self, client):
        resp = client.get("/admin/volunteers")
        assert resp.status_code == 401

    def test_list_needs_no_auth(self, client):
        resp = client.get("/admin/needs")
        assert resp.status_code == 401

    def test_delete_need_no_auth(self, client):
        resp = client.delete("/admin/needs/1")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /admin/volunteers
# ---------------------------------------------------------------------------

class TestAdminListVolunteers:
    def test_list_empty(self, client):
        headers = _create_test_admin(client)
        resp = client.get("/admin/volunteers", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_returns_all_fields(self, client):
        headers = _create_test_admin(client)
        _register_vol(client, "Alice", "alice_admin@example.com", "medical,logistics")
        resp = client.get("/admin/volunteers", headers=headers)
        assert resp.status_code == 200
        vols = resp.json()
        assert len(vols) == 1
        v = vols[0]
        assert v["name"] == "Alice"
        assert v["email"] == "alice_admin@example.com"
        assert v["skills"] == "medical,logistics"
        assert v["is_active"] is True
        assert "id" in v
        assert "created_at" in v


# ---------------------------------------------------------------------------
# PATCH /admin/volunteers/{id}
# ---------------------------------------------------------------------------

class TestAdminUpdateVolunteer:
    def test_update_name(self, client):
        headers = _create_test_admin(client)
        vol_id = _register_vol(client, "Original", "orig@example.com")
        resp = client.patch(f"/admin/volunteers/{vol_id}", json={"name": "Updated"}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated"

    def test_deactivate_volunteer(self, client):
        headers = _create_test_admin(client)
        vol_id = _register_vol(client, "Active Vol", "active@example.com")
        resp = client.patch(f"/admin/volunteers/{vol_id}", json={"is_active": False}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False

    def test_update_skills(self, client):
        headers = _create_test_admin(client)
        vol_id = _register_vol(client, "Skill Vol", "skill@example.com", "general")
        resp = client.patch(f"/admin/volunteers/{vol_id}", json={"skills": "medical,education"}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["skills"] == "medical,education"

    def test_update_nonexistent_returns_404(self, client):
        headers = _create_test_admin(client)
        resp = client.patch("/admin/volunteers/99999", json={"name": "Ghost"}, headers=headers)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /admin/volunteers/{id}
# ---------------------------------------------------------------------------

class TestAdminDeleteVolunteer:
    def test_delete_success(self, client):
        headers = _create_test_admin(client)
        vol_id = _register_vol(client, "Delete Me", "delete@example.com")
        resp = client.delete(f"/admin/volunteers/{vol_id}", headers=headers)
        assert resp.status_code == 200
        assert "removed" in resp.json()["message"].lower()

        # Verify gone
        vols = client.get("/admin/volunteers", headers=headers).json()
        assert all(v["id"] != vol_id for v in vols)

    def test_delete_nonexistent_returns_404(self, client):
        headers = _create_test_admin(client)
        resp = client.delete("/admin/volunteers/99999", headers=headers)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /admin/needs
# ---------------------------------------------------------------------------

class TestAdminListNeeds:
    def test_list_empty(self, client):
        headers = _create_test_admin(client)
        resp = client.get("/admin/needs", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_includes_fulfilled(self, client):
        headers = _create_test_admin(client)
        nid = _submit_need(client)
        db = _get_db(client)
        need = db.query(Need).filter(Need.id == nid).first()
        need.status = "fulfilled"
        db.commit()

        resp = client.get("/admin/needs", headers=headers)
        needs = resp.json()
        ids = [n["id"] for n in needs]
        assert nid in ids


# ---------------------------------------------------------------------------
# PATCH /admin/needs/{id}/status
# ---------------------------------------------------------------------------

class TestAdminUpdateNeedStatus:
    def test_change_to_assigned(self, client):
        headers = _create_test_admin(client)
        nid = _submit_need(client)
        resp = client.patch(f"/admin/needs/{nid}/status", json={"status": "assigned"}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["new_status"] == "assigned"
        assert resp.json()["old_status"] == "pending"

    def test_change_to_fulfilled(self, client):
        headers = _create_test_admin(client)
        nid = _submit_need(client)
        resp = client.patch(f"/admin/needs/{nid}/status", json={"status": "fulfilled"}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["new_status"] == "fulfilled"

    def test_invalid_status_returns_422(self, client):
        headers = _create_test_admin(client)
        nid = _submit_need(client)
        resp = client.patch(f"/admin/needs/{nid}/status", json={"status": "invalid"}, headers=headers)
        assert resp.status_code == 422

    def test_nonexistent_need_returns_404(self, client):
        headers = _create_test_admin(client)
        resp = client.patch("/admin/needs/99999/status", json={"status": "pending"}, headers=headers)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /admin/needs/{id}
# ---------------------------------------------------------------------------

class TestAdminDeleteNeed:
    def test_delete_success(self, client):
        headers = _create_test_admin(client)
        nid = _submit_need(client)
        resp = client.delete(f"/admin/needs/{nid}", headers=headers)
        assert resp.status_code == 200
        assert "removed" in resp.json()["message"].lower()

        needs = client.get("/admin/needs", headers=headers).json()
        assert all(n["id"] != nid for n in needs)

    def test_delete_nonexistent_returns_404(self, client):
        headers = _create_test_admin(client)
        resp = client.delete("/admin/needs/99999", headers=headers)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Auth endpoints: register, login, approve, reject
# ---------------------------------------------------------------------------

class TestAuthEndpoints:
    def test_login_success(self, client):
        _create_test_admin(client)
        resp = client.post("/auth/login", json={"email": "testadmin@example.com", "password": "testpass"})
        assert resp.status_code == 200
        data = resp.json()
        assert "token" in data
        assert data["email"] == "testadmin@example.com"

    def test_login_wrong_password(self, client):
        _create_test_admin(client)
        resp = client.post("/auth/login", json={"email": "testadmin@example.com", "password": "wrong"})
        assert resp.status_code == 401

    def test_login_nonexistent_email(self, client):
        resp = client.post("/auth/login", json={"email": "nobody@example.com", "password": "test"})
        assert resp.status_code == 401

    def test_register_pending_approval(self, client):
        resp = client.post("/auth/register", json={"name": "New Admin", "email": "new@example.com", "password": "pass1234"})
        assert resp.status_code == 200
        msg = resp.json()["message"].lower()
        assert "approve" in msg or "pending" in msg

    def test_register_duplicate_email(self, client):
        _create_test_admin(client)
        resp = client.post("/auth/register", json={"name": "Dup", "email": "testadmin@example.com", "password": "pass"})
        assert resp.status_code == 409

    def test_pending_login_returns_403(self, client):
        client.post("/auth/register", json={"name": "Pending", "email": "pending@example.com", "password": "pass1234"})
        resp = client.post("/auth/login", json={"email": "pending@example.com", "password": "pass1234"})
        assert resp.status_code == 403
        assert "pending" in resp.json()["detail"].lower()

    def test_approve_and_login(self, client):
        headers = _create_test_admin(client)
        # Register a new admin
        client.post("/auth/register", json={"name": "Approvee", "email": "approvee@example.com", "password": "pass1234"})

        # List pending
        resp = client.get("/auth/pending", headers=headers)
        assert resp.status_code == 200
        pending = resp.json()
        approvee = next(p for p in pending if p["email"] == "approvee@example.com")

        # Approve
        resp = client.post(f"/auth/approve/{approvee['id']}", headers=headers)
        assert resp.status_code == 200

        # Now they can login
        resp = client.post("/auth/login", json={"email": "approvee@example.com", "password": "pass1234"})
        assert resp.status_code == 200
        assert "token" in resp.json()

    def test_reject_admin(self, client):
        headers = _create_test_admin(client)
        client.post("/auth/register", json={"name": "Rejectee", "email": "rejectee@example.com", "password": "pass1234"})

        pending = client.get("/auth/pending", headers=headers).json()
        rejectee = next(p for p in pending if p["email"] == "rejectee@example.com")

        resp = client.post(f"/auth/reject/{rejectee['id']}", headers=headers)
        assert resp.status_code == 200

        # Can no longer login
        resp = client.post("/auth/login", json={"email": "rejectee@example.com", "password": "pass1234"})
        assert resp.status_code == 401
