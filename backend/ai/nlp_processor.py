"""NLP processing module for LiveNeed.

Extracts entities, classifies need category, and identifies urgency signals
from raw need text using spaCy's en_core_web_sm model.
"""

from dataclasses import dataclass, field

import spacy

# Load model once at module level to avoid repeated overhead
try:
    _nlp = spacy.load("en_core_web_sm")
except OSError:
    _nlp = None

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "food":      ["food", "hungry", "starving", "meal", "water", "nutrition"],
    "medical":   ["medical", "doctor", "hospital", "injury", "sick", "medicine", "ambulance"],
    "shelter":   ["shelter", "homeless", "housing", "roof", "flood", "displaced"],
    "safety":    ["danger", "violence", "fire", "attack", "threat", "unsafe"],
    "education": ["school", "learning", "children", "books", "teacher", "class"],
}

EMERGENCY_KEYWORDS: list[str] = [
    "emergency", "critical", "urgent", "dying", "fire", "attack"
]


@dataclass
class NLPResult:
    entities: dict = field(default_factory=lambda: {"location": [], "person": [], "org": []})
    category: str = "other"
    urgency_signals: list[str] = field(default_factory=list)


def _default_result() -> NLPResult:
    return NLPResult(
        entities={"location": [], "person": [], "org": []},
        category="other",
        urgency_signals=[],
    )


def process_need_text(text: str) -> NLPResult:
    """Process raw need text and return structured NLP result.

    Args:
        text: Raw need description submitted by a reporter.

    Returns:
        NLPResult with extracted entities, classified category, and urgency signals.
        Returns a default NLPResult on any error — never raises.
    """
    try:
        if _nlp is None:
            return _default_result()

        doc = _nlp(text)
        lower_text = text.lower()

        # Extract named entities
        entities: dict[str, list[str]] = {"location": [], "person": [], "org": []}
        for ent in doc.ents:
            if ent.label_ == "GPE":
                entities["location"].append(ent.text)
            elif ent.label_ == "PERSON":
                entities["person"].append(ent.text)
            elif ent.label_ == "ORG":
                entities["org"].append(ent.text)

        # Classify category — first match wins
        category = "other"
        for cat, keywords in CATEGORY_KEYWORDS.items():
            if any(kw in lower_text for kw in keywords):
                category = cat
                break

        # Extract urgency signals
        urgency_signals = [kw for kw in EMERGENCY_KEYWORDS if kw in lower_text]

        return NLPResult(
            entities=entities,
            category=category,
            urgency_signals=urgency_signals,
        )

    except Exception:
        return _default_result()
