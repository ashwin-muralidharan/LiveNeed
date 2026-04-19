"""Integration tests for POST /match endpoint.

Tests:
  - POST /match with valid need_id returns 200 with matches list
  - POST /match with invalid need_id returns 404
  - Volunteer with matching skill appears in results
  - Volunteer with active assignment is excluded from results
  - Results are sorted by match_score descending
"""

import pytest
from models import Assignment, Need, User
from datetime import datetime


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_need(client, text="urgent medical help needed", category="medical"):
    """Submit and analyze a need, returning its ID."""
    r = client.post("/submit-need", json={"raw_text": text})
    assert r.status_code == 200
    need_id = r.json()["need_id"]
    # Force the category via direct DB manipulation after analyze
    client.post("/analyze", json={"need_id": need_id})
    return need_id


def _register_volunteer(client, name="Alice", email=None, skills="medical", lat=None, lon=None):
    email = email or f"{name.lower().replace(' ', '_')}@example.com"
    payload = {"name": name, "email": email, "skills": skills, "role": "volunteer"}
    if lat is not None:
        payload["latitude"] = lat
    if lon is not None:
        payload["longitude"] = lon
    r = client.post("/register-volunteer", json=payload)
    assert r.status_code == 200
    return r.json()["volunteer_id"]


def _set_need_category(client, need_id: int, category: str):
    """Directly update a need's category via the test DB."""
    from database import get_db
    db_gen = client.app.dependency_overrides[get_db]()
    db = next(db_gen)
    need = db.query(Need).filter(Need.id == need_id).first()
    need.category = category
    db.commit()
    try:
        next(db_gen)
    except StopIteration:
        pass


def _create_active_assignment(client, need_id: int, volunteer_id: int):
    """Insert an active Assignment record directly into the test DB."""
    from database import get_db
    db_gen = client.app.dependency_overrides[get_db]()
    db = next(db_gen)
    assignment = Assignment(
        need_id=need_id,
        volunteer_id=volunteer_id,
        assigned_at=datetime.utcnow(),
        status="active",
    )
    db.add(assignment)
    db.commit()
    try:
        next(db_gen)
    except StopIteration:
        pass


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_match_valid_need_returns_200(client):
    need_id = _create_need(client)
    resp = client.post("/match", json={"need_id": need_id})
    assert resp.status_code == 200
    data = resp.json()
    assert "matches" in data
    assert isinstance(data["matches"], list)


def test_match_invalid_need_returns_404(client):
    resp = client.post("/match", json={"need_id": 99999})
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_match_volunteer_with_matching_skill_appears(client):
    # Create a medical need
    need_id = _create_need(client, text="urgent medical help needed")
    _set_need_category(client, need_id, "medical")

    # Register a volunteer with the matching skill (medical)
    vol_id = _register_volunteer(client, name="Dr. Bob", email="drbob@example.com", skills="medical")

    resp = client.post("/match", json={"need_id": need_id})
    assert resp.status_code == 200
    matches = resp.json()["matches"]
    assert len(matches) >= 1

    volunteer_ids = [m["volunteer_id"] for m in matches]
    assert vol_id in volunteer_ids

    # The matching volunteer should have a higher score than non-matching ones
    matched = next(m for m in matches if m["volunteer_id"] == vol_id)
    assert matched["match_score"] >= 50  # primary skill match gives +50


def test_match_volunteer_with_active_assignment_excluded(client):
    # Create two needs
    need1_id = _create_need(client, text="first medical need")
    need2_id = _create_need(client, text="second medical need")
    _set_need_category(client, need1_id, "medical")
    _set_need_category(client, need2_id, "medical")

    # Register a volunteer
    vol_id = _register_volunteer(client, name="Carol", email="carol@example.com", skills="medical")

    # Assign the volunteer to need1 (active assignment)
    _create_active_assignment(client, need_id=need1_id, volunteer_id=vol_id)

    # Match for need2 — the volunteer should NOT appear
    resp = client.post("/match", json={"need_id": need2_id})
    assert resp.status_code == 200
    matches = resp.json()["matches"]
    volunteer_ids = [m["volunteer_id"] for m in matches]
    assert vol_id not in volunteer_ids


def test_match_results_sorted_by_score_descending(client):
    need_id = _create_need(client, text="urgent medical help")
    _set_need_category(client, need_id, "medical")

    # Register volunteers with different skill sets
    _register_volunteer(client, name="Med Expert", email="med@example.com", skills="medical,logistics,education")
    _register_volunteer(client, name="Generalist", email="gen@example.com", skills="general")
    _register_volunteer(client, name="Logistics", email="log@example.com", skills="logistics")

    resp = client.post("/match", json={"need_id": need_id})
    assert resp.status_code == 200
    matches = resp.json()["matches"]
    assert len(matches) >= 2

    scores = [m["match_score"] for m in matches]
    for i in range(len(scores) - 1):
        assert scores[i] >= scores[i + 1], (
            f"Results not sorted DESC at index {i}: {scores[i]} < {scores[i+1]}"
        )


def test_match_no_volunteers_returns_empty_list(client):
    need_id = _create_need(client, text="need food supplies")
    resp = client.post("/match", json={"need_id": need_id})
    assert resp.status_code == 200
    assert resp.json()["matches"] == []
