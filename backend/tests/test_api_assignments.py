"""Integration tests for POST /assign and GET /assignments endpoints.

Tests:
  - POST /assign with valid need_id and volunteer_id returns 200
  - POST /assign with non-existent need returns 404
  - POST /assign with non-existent volunteer returns 404
  - POST /assign on already-fulfilled need returns 409
  - POST /assign duplicate assignment returns 409
  - POST /assign with inactive volunteer returns 409
  - POST /assign updates need status to "assigned"
  - GET /assignments returns active assignments
  - GET /assignments excludes completed assignments
  - Full workflow: submit → analyze → match → assign → verify-impact
"""

import pytest
from models import Assignment, Need, User
from datetime import datetime


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _submit_need(client, text="Urgent food needed in downtown"):
    resp = client.post("/submit-need", json={"raw_text": text})
    assert resp.status_code == 200, resp.text
    return resp.json()["need_id"]


def _register_volunteer(client, name="Test Vol", email=None, skills="general"):
    email = email or f"{name.lower().replace(' ', '_')}_{id(name)}@example.com"
    resp = client.post("/register-volunteer", json={
        "name": name, "email": email, "role": "volunteer", "skills": skills,
    })
    assert resp.status_code == 200, resp.text
    return resp.json()["volunteer_id"]


def _get_db(client):
    from database import get_db
    gen = client.app.dependency_overrides[get_db]()
    return next(gen)


# ---------------------------------------------------------------------------
# POST /assign
# ---------------------------------------------------------------------------

class TestAssignEndpoint:
    def test_assign_success(self, client):
        """Assign a volunteer to a need → 200 with assignment_id."""
        need_id = _submit_need(client)
        vol_id = _register_volunteer(client, "Alice", "alice_assign@example.com")

        resp = client.post("/assign", json={"need_id": need_id, "volunteer_id": vol_id})
        assert resp.status_code == 200
        data = resp.json()
        assert "assignment_id" in data
        assert isinstance(data["assignment_id"], int)
        assert data["need_id"] == need_id
        assert data["volunteer_id"] == vol_id
        assert data["status"] == "active"

    def test_assign_nonexistent_need_returns_404(self, client):
        vol_id = _register_volunteer(client, "Bob", "bob_404@example.com")
        resp = client.post("/assign", json={"need_id": 99999, "volunteer_id": vol_id})
        assert resp.status_code == 404
        assert "Need not found" in resp.json()["detail"]

    def test_assign_nonexistent_volunteer_returns_404(self, client):
        need_id = _submit_need(client)
        resp = client.post("/assign", json={"need_id": need_id, "volunteer_id": 99999})
        assert resp.status_code == 404
        assert "Volunteer not found" in resp.json()["detail"]

    def test_assign_fulfilled_need_returns_409(self, client):
        """Cannot assign a volunteer to an already-fulfilled need."""
        need_id = _submit_need(client)
        vol_id = _register_volunteer(client, "Carol", "carol_409@example.com")

        # Manually mark need as fulfilled
        db = _get_db(client)
        need = db.query(Need).filter(Need.id == need_id).first()
        need.status = "fulfilled"
        db.commit()

        resp = client.post("/assign", json={"need_id": need_id, "volunteer_id": vol_id})
        assert resp.status_code == 409
        assert "already fulfilled" in resp.json()["detail"]

    def test_assign_duplicate_returns_409(self, client):
        """Same volunteer assigned to same need twice returns 409."""
        need_id = _submit_need(client)
        vol_id = _register_volunteer(client, "Dave", "dave_dup@example.com")

        resp1 = client.post("/assign", json={"need_id": need_id, "volunteer_id": vol_id})
        assert resp1.status_code == 200

        resp2 = client.post("/assign", json={"need_id": need_id, "volunteer_id": vol_id})
        assert resp2.status_code == 409
        assert "already assigned" in resp2.json()["detail"].lower()

    def test_assign_inactive_volunteer_returns_409(self, client):
        """Cannot assign an inactive volunteer."""
        need_id = _submit_need(client)
        vol_id = _register_volunteer(client, "Eve", "eve_inactive@example.com")

        # Deactivate the volunteer
        db = _get_db(client)
        user = db.query(User).filter(User.id == vol_id).first()
        user.is_active = False
        db.commit()

        resp = client.post("/assign", json={"need_id": need_id, "volunteer_id": vol_id})
        assert resp.status_code == 409
        assert "inactive" in resp.json()["detail"].lower()

    def test_assign_updates_need_status(self, client):
        """After assignment, need status should change to 'assigned'."""
        need_id = _submit_need(client)
        vol_id = _register_volunteer(client, "Frank", "frank_status@example.com")

        client.post("/assign", json={"need_id": need_id, "volunteer_id": vol_id})

        db = _get_db(client)
        db.expire_all()
        need = db.query(Need).filter(Need.id == need_id).first()
        assert need.status == "assigned"


# ---------------------------------------------------------------------------
# GET /assignments
# ---------------------------------------------------------------------------

class TestListAssignments:
    def test_list_assignments_empty(self, client):
        resp = client.get("/assignments")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_assignments_returns_active(self, client):
        need_id = _submit_need(client)
        vol_id = _register_volunteer(client, "Grace", "grace_list@example.com")
        client.post("/assign", json={"need_id": need_id, "volunteer_id": vol_id})

        resp = client.get("/assignments")
        assert resp.status_code == 200
        assignments = resp.json()
        assert len(assignments) == 1
        assert assignments[0]["need_id"] == need_id
        assert assignments[0]["volunteer_id"] == vol_id
        assert assignments[0]["status"] == "active"

    def test_list_assignments_excludes_completed(self, client):
        """After verify-impact, assignment becomes 'completed' and shouldn't appear."""
        need_id = _submit_need(client)
        vol_id = _register_volunteer(client, "Hank", "hank_completed@example.com")

        # Assign
        client.post("/assign", json={"need_id": need_id, "volunteer_id": vol_id})

        # Verify impact → marks assignment as completed
        client.post("/verify-impact", json={
            "need_id": need_id, "volunteer_id": vol_id, "notes": "Done"
        })

        resp = client.get("/assignments")
        assignments = resp.json()
        need_ids = [a["need_id"] for a in assignments]
        assert need_id not in need_ids


# ---------------------------------------------------------------------------
# Full workflow integration test
# ---------------------------------------------------------------------------

class TestFullWorkflow:
    def test_submit_analyze_match_assign_verify(self, client):
        """End-to-end: submit → analyze → match → assign → verify-impact."""
        # 1. Submit a need
        resp = client.post("/submit-need", json={
            "raw_text": "Emergency medical help needed urgently at the hospital",
            "location_hint": "City Hospital"
        })
        assert resp.status_code == 200
        need_id = resp.json()["need_id"]

        # 2. Analyze the need
        resp = client.post("/analyze", json={"need_id": need_id})
        assert resp.status_code == 200
        analysis = resp.json()
        assert analysis["category"] in {"food", "medical", "shelter", "safety", "education", "other"}
        assert 0 <= analysis["urgency_score"] <= 100

        # 3. Register a volunteer
        vol_id = _register_volunteer(client, "Dr. Kim", "drkim@example.com", "medical,general")

        # 4. Find matching volunteers
        resp = client.post("/match", json={"need_id": need_id})
        assert resp.status_code == 200
        matches = resp.json()["matches"]
        assert len(matches) >= 1
        assert any(m["volunteer_id"] == vol_id for m in matches)

        # 5. Assign the volunteer
        resp = client.post("/assign", json={"need_id": need_id, "volunteer_id": vol_id})
        assert resp.status_code == 200

        # 6. Verify active assignment exists
        resp = client.get("/assignments")
        assert any(a["need_id"] == need_id for a in resp.json())

        # 7. Verify impact
        resp = client.post("/verify-impact", json={
            "need_id": need_id, "volunteer_id": vol_id,
            "notes": "Patient treated successfully"
        })
        assert resp.status_code == 200
        assert resp.json()["confirmed"] is True

        # 8. Verify stats updated
        stats = client.get("/stats").json()
        assert stats["fulfilled_needs"] >= 1

        # 9. Verify need no longer in active prioritize list
        needs = client.get("/prioritize").json()
        active_ids = [n["id"] for n in needs]
        assert need_id not in active_ids
