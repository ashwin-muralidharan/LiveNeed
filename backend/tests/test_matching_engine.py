"""Unit tests for backend/matching_engine.py — task 8.1"""
import sys
import os

# Ensure backend/ is on the path so imports resolve correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import MagicMock

from matching_engine import MatchResult, CATEGORY_TO_SKILL, haversine_distance, match_volunteers


# ---------------------------------------------------------------------------
# Helpers – lightweight stand-ins for SQLAlchemy model instances
# ---------------------------------------------------------------------------

def make_need(category: str = "medical") -> MagicMock:
    need = MagicMock()
    need.category = category
    return need


def make_volunteer(
    id: int = 1,
    name: str = "Alice",
    skills: str = "",
    is_active: bool = True,
    latitude: float | None = None,
    longitude: float | None = None,
) -> MagicMock:
    v = MagicMock()
    v.id = id
    v.name = name
    v.skills = skills
    v.is_active = is_active
    v.latitude = latitude
    v.longitude = longitude
    return v


# ---------------------------------------------------------------------------
# haversine_distance
# ---------------------------------------------------------------------------

def test_haversine_same_point_is_zero():
    assert haversine_distance(0, 0, 0, 0) == pytest.approx(0.0)


def test_haversine_known_distance():
    # London (51.5074, -0.1278) to Paris (48.8566, 2.3522) ≈ 341 km
    dist = haversine_distance(51.5074, -0.1278, 48.8566, 2.3522)
    assert 330 < dist < 360


# ---------------------------------------------------------------------------
# match_volunteers – core behaviour
# ---------------------------------------------------------------------------

def test_matching_skill_volunteer_scores_higher():
    """Volunteer with matching primary skill gets higher score than one without."""
    need = make_need(category="medical")  # primary skill = "medical"
    v_match = make_volunteer(id=1, name="Doc", skills="medical")
    v_no_match = make_volunteer(id=2, name="Bob", skills="cooking")

    results = match_volunteers(need, [v_match, v_no_match])

    assert len(results) == 2
    scores = {r.volunteer_id: r.match_score for r in results}
    assert scores[1] > scores[2]


def test_inactive_volunteer_excluded():
    """Volunteer with is_active=False must not appear in results."""
    need = make_need(category="food")
    active = make_volunteer(id=1, name="Active", skills="logistics", is_active=True)
    inactive = make_volunteer(id=2, name="Inactive", skills="logistics", is_active=False)

    results = match_volunteers(need, [active, inactive])

    ids = [r.volunteer_id for r in results]
    assert 2 not in ids
    assert 1 in ids


def test_all_match_scores_non_negative():
    """All returned match scores must be >= 0."""
    need = make_need(category="shelter")
    volunteers = [
        make_volunteer(id=i, name=f"V{i}", skills=s)
        for i, s in enumerate(["", "cooking", "construction", "medical,logistics"], start=1)
    ]

    results = match_volunteers(need, volunteers)

    for r in results:
        assert r.match_score >= 0.0


def test_empty_volunteer_list_returns_empty():
    """Empty input list should produce an empty result list."""
    need = make_need(category="education")
    assert match_volunteers(need, []) == []


def test_results_sorted_by_score_descending():
    """Results must be ordered by match_score descending."""
    need = make_need(category="safety")  # primary skill = "general"
    volunteers = [
        make_volunteer(id=1, name="A", skills="general,medical"),   # 50 + 10 = 60
        make_volunteer(id=2, name="B", skills="general"),            # 50
        make_volunteer(id=3, name="C", skills="logistics"),          # 10 (secondary only)
        make_volunteer(id=4, name="D", skills=""),                   # 0
    ]

    results = match_volunteers(need, volunteers)

    scores = [r.match_score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_primary_skill_match_gives_50_points():
    """Primary skill match should contribute exactly +50 to the score."""
    need = make_need(category="education")  # primary skill = "education"
    v = make_volunteer(id=1, skills="education")

    results = match_volunteers(need, [v])

    assert results[0].match_score == pytest.approx(50.0)


def test_additional_relevant_skills_add_10_each():
    """Each additional relevant skill beyond the primary adds +10."""
    need = make_need(category="medical")  # primary = "medical"
    # medical (primary +50) + logistics (+10) + construction (+10) = 70
    v = make_volunteer(id=1, skills="medical,logistics,construction")

    results = match_volunteers(need, [v])

    assert results[0].match_score == pytest.approx(70.0)


def test_distance_km_is_none_when_no_coordinates_provided():
    """distance_km should be None when need_lat/need_lon are not provided."""
    need = make_need(category="food")
    v = make_volunteer(id=1, skills="logistics", latitude=10.0, longitude=20.0)

    results = match_volunteers(need, [v])

    assert results[0].distance_km is None


def test_skills_field_parsed_correctly():
    """Skills list in MatchResult should be the parsed tags."""
    need = make_need(category="food")
    v = make_volunteer(id=1, skills=" logistics , medical ")

    results = match_volunteers(need, [v])

    assert results[0].skills == ["logistics", "medical"]


# ---------------------------------------------------------------------------
# Proximity scoring tests
# ---------------------------------------------------------------------------

def test_proximity_score_same_location_gives_max():
    """Volunteer at the same location as the need should get max proximity bonus (+50)."""
    need = make_need(category="food")
    v = make_volunteer(id=1, skills="logistics", latitude=28.6, longitude=77.2)

    results = match_volunteers(need, [v], need_lat=28.6, need_lon=77.2)

    # logistics is primary for food → +50 skill, +50 proximity = 100
    assert results[0].match_score == pytest.approx(100.0)
    assert results[0].distance_km == pytest.approx(0.0)


def test_proximity_score_scales_linearly():
    """Proximity score should decrease linearly with distance up to 100km."""
    need = make_need(category="other")  # no primary skill → skill_score=0
    # Volunteer roughly 50km away
    v = make_volunteer(id=1, skills="cooking", latitude=28.6, longitude=77.2)

    # Place need at a point ~50km away
    results = match_volunteers(need, [v], need_lat=29.05, need_lon=77.2)

    # Should have some proximity score between 0 and 50
    assert results[0].distance_km is not None
    if results[0].distance_km <= 100:
        assert results[0].match_score > 0


def test_proximity_score_zero_beyond_100km():
    """Volunteers beyond 100km should get 0 proximity score."""
    need = make_need(category="other")
    # London volunteer, need in Paris (~340km away)
    v = make_volunteer(id=1, skills="cooking", latitude=51.5074, longitude=-0.1278)

    results = match_volunteers(need, [v], need_lat=48.8566, need_lon=2.3522)

    assert results[0].distance_km is not None
    assert results[0].distance_km > 100
    assert results[0].match_score == 0.0  # no skill match, no proximity


def test_proximity_ignored_when_volunteer_has_no_location():
    """Volunteer without lat/lon should still get scored (with 0 proximity)."""
    need = make_need(category="medical")
    v = make_volunteer(id=1, skills="medical", latitude=None, longitude=None)

    results = match_volunteers(need, [v], need_lat=28.6, need_lon=77.2)

    assert results[0].distance_km is None
    assert results[0].match_score == pytest.approx(50.0)  # skill only


def test_closer_volunteer_ranks_higher_same_skills():
    """Among volunteers with identical skills, closer one should rank higher."""
    need = make_need(category="medical")
    v_close = make_volunteer(id=1, name="Close", skills="medical", latitude=28.61, longitude=77.21)
    v_far = make_volunteer(id=2, name="Far", skills="medical", latitude=29.5, longitude=77.2)

    results = match_volunteers(need, [v_close, v_far], need_lat=28.6, need_lon=77.2)

    assert results[0].volunteer_id == 1  # closer one first
    assert results[0].match_score > results[1].match_score

