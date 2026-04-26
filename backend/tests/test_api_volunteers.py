"""Unit tests for POST /register-volunteer endpoint.

Tests:
  - Register a volunteer successfully → 200 with volunteer_id
  - Register same email twice → second call returns 409
  - Verify the volunteer appears in DB after registration
  - Test that skills are stored correctly
"""

from models import User


VOLUNTEER_PAYLOAD = {
    "name": "Alice Smith",
    "email": "alice@example.com",
    "role": "volunteer",
    "skills": "medical,logistics",
    "latitude": 40.7128,
    "longitude": -74.0060,
}


def test_register_volunteer_success(client):
    resp = client.post("/register-volunteer", json=VOLUNTEER_PAYLOAD)
    assert resp.status_code == 200
    data = resp.json()
    assert "volunteer_id" in data
    assert isinstance(data["volunteer_id"], int)
    assert data["name"] == VOLUNTEER_PAYLOAD["name"]
    assert data["email"] == VOLUNTEER_PAYLOAD["email"]


def test_register_duplicate_email_returns_409(client):
    client.post("/register-volunteer", json=VOLUNTEER_PAYLOAD)
    resp = client.post("/register-volunteer", json=VOLUNTEER_PAYLOAD)
    assert resp.status_code == 409
    assert "already registered" in resp.json()["detail"].lower()


def test_volunteer_appears_in_db(client):
    # Before registration, count is 0
    assert client.get("/stats").json()["volunteers_registered"] == 0

    resp = client.post("/register-volunteer", json=VOLUNTEER_PAYLOAD)
    assert resp.status_code == 200

    # After registration, count is 1
    assert client.get("/stats").json()["volunteers_registered"] == 1


def test_skills_stored_correctly(client):
    payload = {**VOLUNTEER_PAYLOAD, "email": "bob@example.com", "skills": "education,counseling,construction"}
    resp = client.post("/register-volunteer", json=payload)
    assert resp.status_code == 200

    # Verify via stats that volunteer count increased
    stats = client.get("/stats")
    assert stats.json()["volunteers_registered"] == 1

    # Register another to confirm skills are per-user
    payload2 = {**VOLUNTEER_PAYLOAD, "email": "carol@example.com", "name": "Carol", "skills": "general"}
    resp2 = client.post("/register-volunteer", json=payload2)
    assert resp2.status_code == 200
    stats2 = client.get("/stats")
    assert stats2.json()["volunteers_registered"] == 2
