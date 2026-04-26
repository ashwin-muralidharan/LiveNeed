"""Integration tests for the needs API endpoints.

Tests:
  - POST /submit-need with valid text returns 200 and need_id
  - POST /submit-need with whitespace-only returns 422
  - POST /analyze returns entities, category, urgency_score
  - GET  /prioritize returns needs sorted by urgency_score DESC
  - GET  /stats returns correct counts
"""

import json


def test_submit_need_valid(client):
    resp = client.post("/submit-need", json={"raw_text": "We need food and water urgently"})
    assert resp.status_code == 200
    data = resp.json()
    assert "need_id" in data
    assert isinstance(data["need_id"], int)
    assert data["status"] == "pending"


def test_submit_need_whitespace_only(client):
    for text in ["   ", "\t\n", " "]:
        resp = client.post("/submit-need", json={"raw_text": text})
        assert resp.status_code == 422
        assert "empty" in resp.json()["detail"].lower()


def test_submit_need_empty_string(client):
    resp = client.post("/submit-need", json={"raw_text": ""})
    assert resp.status_code == 422


def test_analyze_returns_nlp_fields(client):
    # Submit a need first
    submit = client.post("/submit-need", json={"raw_text": "urgent medical help needed at the hospital"})
    assert submit.status_code == 200
    need_id = submit.json()["need_id"]

    resp = client.post("/analyze", json={"need_id": need_id})
    assert resp.status_code == 200
    data = resp.json()
    assert "entities" in data
    assert "category" in data
    assert "urgency_score" in data
    assert isinstance(data["entities"], dict)
    assert data["category"] in {"food", "medical", "shelter", "safety", "education", "other"}
    assert 0 <= data["urgency_score"] <= 100


def test_analyze_not_found(client):
    resp = client.post("/analyze", json={"need_id": 9999})
    assert resp.status_code == 404


def test_prioritize_sorted_desc(client):
    # Submit and analyze several needs with different urgency profiles
    texts = [
        "food needed",                          # low urgency
        "emergency fire attack critical now",   # high urgency
        "shelter for displaced families",       # medium urgency
    ]
    for text in texts:
        r = client.post("/submit-need", json={"raw_text": text})
        assert r.status_code == 200
        need_id = r.json()["need_id"]
        client.post("/analyze", json={"need_id": need_id})

    resp = client.get("/prioritize")
    assert resp.status_code == 200
    needs = resp.json()
    assert len(needs) >= 3

    scores = [n["urgency_score"] for n in needs]
    for i in range(len(scores) - 1):
        assert scores[i] >= scores[i + 1], (
            f"Not sorted DESC at index {i}: {scores[i]} < {scores[i+1]}"
        )


def test_prioritize_excludes_fulfilled(client):
    from database import get_db
    from models import Need
    from datetime import datetime

    # Submit a need and manually mark it fulfilled via DB
    r = client.post("/submit-need", json={"raw_text": "need shelter"})
    need_id = r.json()["need_id"]

    # Use the overridden DB to update status
    db_gen = client.app.dependency_overrides[get_db]()
    db = next(db_gen)
    need = db.query(Need).filter(Need.id == need_id).first()
    need.status = "fulfilled"
    db.commit()
    try:
        next(db_gen)
    except StopIteration:
        pass

    resp = client.get("/prioritize")
    ids = [n["id"] for n in resp.json()]
    assert need_id not in ids


def test_stats_counts(client):
    # Initially everything is zero
    resp = client.get("/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["active_needs"] == 0
    assert data["fulfilled_needs"] == 0
    assert data["volunteers_registered"] == 0

    # Add a need
    client.post("/submit-need", json={"raw_text": "food needed"})
    resp = client.get("/stats")
    data = resp.json()
    assert data["active_needs"] == 1
    assert data["fulfilled_needs"] == 0
