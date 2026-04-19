"""Integration tests for POST /verify-impact endpoint.

Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 8.5
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from models import Assignment, Need, ImpactLog


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_db(client: TestClient) -> Session:
    """Retrieve the test DB session from the app's dependency override."""
    from main import app
    from database import get_db
    gen = app.dependency_overrides[get_db]()
    return next(gen)


def _submit_need(client: TestClient, text: str = "Urgent food needed") -> int:
    resp = client.post("/submit-need", json={"raw_text": text})
    assert resp.status_code == 200, resp.text
    return resp.json()["need_id"]


def _register_volunteer(client: TestClient, email: str = "vol@example.com") -> int:
    resp = client.post(
        "/register-volunteer",
        json={
            "name": "Test Volunteer",
            "email": email,
            "role": "volunteer",
            "skills": "general",
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["volunteer_id"]


def _create_assignment(db: Session, need_id: int, volunteer_id: int) -> Assignment:
    assignment = Assignment(need_id=need_id, volunteer_id=volunteer_id, status="active")
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestVerifyImpact:
    def test_happy_path(self, client: TestClient):
        """Submit need → register volunteer → create assignment → verify impact → 200."""
        need_id = _submit_need(client)
        volunteer_id = _register_volunteer(client)
        db = _get_db(client)
        _create_assignment(db, need_id, volunteer_id)

        resp = client.post(
            "/verify-impact",
            json={"need_id": need_id, "volunteer_id": volunteer_id, "notes": "Delivered food"},
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["confirmed"] is True
        assert isinstance(data["impact_log_id"], int)
        assert data["impact_log_id"] > 0

    def test_need_status_fulfilled_after_proof(self, client: TestClient):
        """Need status should be 'fulfilled' after successful proof submission."""
        need_id = _submit_need(client, "Medical supplies needed")
        volunteer_id = _register_volunteer(client, "vol2@example.com")
        db = _get_db(client)
        _create_assignment(db, need_id, volunteer_id)

        resp = client.post(
            "/verify-impact",
            json={"need_id": need_id, "volunteer_id": volunteer_id},
        )
        assert resp.status_code == 200, resp.text

        # Verify need status in DB
        db.expire_all()
        need = db.query(Need).filter(Need.id == need_id).first()
        assert need.status == "fulfilled"

    def test_duplicate_proof_returns_409(self, client: TestClient):
        """Submitting proof for an already-fulfilled need returns 409."""
        need_id = _submit_need(client, "Shelter needed urgently")
        volunteer_id = _register_volunteer(client, "vol3@example.com")
        db = _get_db(client)
        _create_assignment(db, need_id, volunteer_id)

        # First proof — should succeed
        resp1 = client.post(
            "/verify-impact",
            json={"need_id": need_id, "volunteer_id": volunteer_id},
        )
        assert resp1.status_code == 200, resp1.text

        # Second proof — should return 409
        resp2 = client.post(
            "/verify-impact",
            json={"need_id": need_id, "volunteer_id": volunteer_id},
        )
        assert resp2.status_code == 409
        assert "already fulfilled" in resp2.json()["detail"]

    def test_unassigned_volunteer_returns_403(self, client: TestClient):
        """Proof by a volunteer not assigned to the need returns 403."""
        need_id = _submit_need(client, "Education materials needed")
        volunteer_id = _register_volunteer(client, "vol4@example.com")
        # No assignment created

        resp = client.post(
            "/verify-impact",
            json={"need_id": need_id, "volunteer_id": volunteer_id},
        )
        assert resp.status_code == 403
        assert "not assigned" in resp.json()["detail"]

    def test_nonexistent_need_returns_404(self, client: TestClient):
        """Proof for a non-existent need returns 404."""
        volunteer_id = _register_volunteer(client, "vol5@example.com")

        resp = client.post(
            "/verify-impact",
            json={"need_id": 99999, "volunteer_id": volunteer_id},
        )
        assert resp.status_code == 404
        assert "Need not found" in resp.json()["detail"]
