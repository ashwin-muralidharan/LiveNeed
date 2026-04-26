"""Urgency scoring module for LiveNeed.

Computes a 0–100 urgency score from NLP signals and submission recency.
"""

from datetime import datetime

from ai.nlp_processor import NLPResult

BASE_CATEGORY_SCORES: dict[str, int] = {
    "safety": 40,
    "medical": 35,
    "shelter": 25,
    "food": 20,
    "education": 10,
    "other": 5,
}

EMERGENCY_KEYWORD_BONUS = 30
RECENCY_BONUS = 10
RECENCY_WINDOW_HOURS = 1


def compute_urgency(nlp_result: NLPResult, submitted_at: datetime) -> float:
    """Compute urgency score from NLP result and submission time.

    Args:
        nlp_result: Structured output from the NLP processor.
        submitted_at: UTC datetime when the need was submitted.

    Returns:
        Urgency score as a float in [0.0, 100.0].
    """
    score = BASE_CATEGORY_SCORES.get(nlp_result.category, 5)

    score += EMERGENCY_KEYWORD_BONUS * len(nlp_result.urgency_signals)

    now = datetime.utcnow()
    hours_elapsed = (now - submitted_at).total_seconds() / 3600
    if hours_elapsed <= RECENCY_WINDOW_HOURS:
        score += RECENCY_BONUS

    return float(max(0, min(100, score)))
