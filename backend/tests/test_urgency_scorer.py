"""Unit tests for backend/ai/urgency_scorer.py."""

from datetime import datetime, timedelta

import pytest

from ai.nlp_processor import NLPResult
from ai.urgency_scorer import (
    BASE_CATEGORY_SCORES,
    EMERGENCY_KEYWORD_BONUS,
    RECENCY_BONUS,
    compute_urgency,
)


def _result(category: str = "other", urgency_signals: list[str] | None = None) -> NLPResult:
    return NLPResult(category=category, urgency_signals=urgency_signals or [])


def _old() -> datetime:
    """Submission older than the recency window."""
    return datetime.utcnow() - timedelta(hours=2)


def _recent() -> datetime:
    """Submission within the recency window."""
    return datetime.utcnow() - timedelta(minutes=10)


# --- Range tests ---

def test_score_in_range_no_signals():
    score = compute_urgency(_result("other"), _old())
    assert 0 <= score <= 100


def test_score_in_range_safety_recent():
    score = compute_urgency(_result("safety"), _recent())
    assert 0 <= score <= 100


def test_score_in_range_many_keywords():
    signals = ["emergency", "critical", "urgent", "dying", "fire", "attack"]
    score = compute_urgency(_result("safety", signals), _old())
    assert 0 <= score <= 100


# --- Emergency keyword threshold ---

def test_emergency_keyword_produces_high_score():
    # safety(40) + 1 keyword(30) = 70 — minimum case per requirement 3.4
    score = compute_urgency(_result("safety", ["emergency"]), _old())
    assert score >= 70


def test_multiple_emergency_keywords_high_score():
    score = compute_urgency(_result("food", ["urgent", "critical"]), _old())
    assert score >= 70


# --- Category ordering ---

def test_safety_higher_than_education():
    safety_score = compute_urgency(_result("safety"), _old())
    education_score = compute_urgency(_result("education"), _old())
    assert safety_score > education_score


def test_medical_higher_than_food():
    medical_score = compute_urgency(_result("medical"), _old())
    food_score = compute_urgency(_result("food"), _old())
    assert medical_score > food_score


# --- Recency bonus ---

def test_recency_bonus_applied_for_recent_submission():
    old_score = compute_urgency(_result("food"), _old())
    recent_score = compute_urgency(_result("food"), _recent())
    assert recent_score == old_score + RECENCY_BONUS


def test_recency_bonus_not_applied_for_old_submission():
    old_score = compute_urgency(_result("food"), _old())
    expected = float(BASE_CATEGORY_SCORES["food"])
    assert old_score == expected


# --- Cap at 100 ---

def test_score_capped_at_100_with_many_keywords():
    # safety(40) + 6 keywords * 30 = 220 → capped at 100
    signals = ["emergency", "critical", "urgent", "dying", "fire", "attack"]
    score = compute_urgency(_result("safety", signals), _old())
    assert score == 100.0


def test_score_capped_at_100_with_recency():
    signals = ["emergency", "critical", "urgent"]
    score = compute_urgency(_result("safety", signals), _recent())
    assert score == 100.0


# --- Floor at 0 ---

def test_score_floor_is_zero():
    # Normal inputs should never go below 0
    score = compute_urgency(_result("other"), _old())
    assert score >= 0.0


# --- Return type ---

def test_returns_float():
    score = compute_urgency(_result("medical"), _recent())
    assert isinstance(score, float)
