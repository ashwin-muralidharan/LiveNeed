"""Unit tests for backend/ai/nlp_processor.py"""

import pytest
from ai.nlp_processor import (
    NLPResult,
    CATEGORY_KEYWORDS,
    EMERGENCY_KEYWORDS,
    process_need_text,
)


def test_returns_nlp_result_instance():
    result = process_need_text("We need food and water urgently.")
    assert isinstance(result, NLPResult)


def test_category_food():
    result = process_need_text("People are hungry and need a meal.")
    assert result.category == "food"


def test_category_medical():
    result = process_need_text("There is an injured person who needs a doctor.")
    assert result.category == "medical"


def test_category_shelter():
    result = process_need_text("Families are homeless after the flood.")
    assert result.category == "shelter"


def test_category_safety():
    result = process_need_text("There is danger and violence in the area.")
    assert result.category == "safety"


def test_category_education():
    result = process_need_text("Children need school books and a teacher.")
    assert result.category == "education"


def test_category_defaults_to_other():
    result = process_need_text("Something happened and we need help.")
    assert result.category == "other"


def test_urgency_signals_detected():
    result = process_need_text("This is an emergency, someone is dying.")
    assert "emergency" in result.urgency_signals
    assert "dying" in result.urgency_signals


def test_urgency_signals_empty_when_none():
    result = process_need_text("We need some food supplies.")
    assert result.urgency_signals == []


def test_entities_structure():
    result = process_need_text("Help needed in New York.")
    assert "location" in result.entities
    assert "person" in result.entities
    assert "org" in result.entities
    assert isinstance(result.entities["location"], list)


def test_entities_location_extracted():
    result = process_need_text("There is a flood in London.")
    assert "London" in result.entities["location"]


def test_empty_string_returns_default():
    result = process_need_text("")
    assert result.category == "other"
    assert result.urgency_signals == []
    assert result.entities == {"location": [], "person": [], "org": []}


def test_no_unhandled_exception_on_weird_input():
    # Should never raise
    result = process_need_text("\x00\xff\n\t" * 50)
    assert isinstance(result, NLPResult)


def test_category_first_match_wins():
    # "food" keywords appear before "medical" in CATEGORY_KEYWORDS
    result = process_need_text("hungry and sick")
    assert result.category == "food"
