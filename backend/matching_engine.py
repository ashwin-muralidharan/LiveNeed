from __future__ import annotations

import math
from dataclasses import dataclass

from models import Need, User

CATEGORY_TO_SKILL = {
    "medical":   "medical",
    "food":      "logistics",
    "shelter":   "construction",
    "safety":    "general",
    "education": "education",
}

MAX_PROXIMITY_SCORE = 50.0
MAX_DISTANCE_KM = 100.0


@dataclass
class MatchResult:
    volunteer_id: int
    name: str
    skills: list[str]
    match_score: float
    distance_km: float | None


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the great-circle distance in km between two lat/lon points."""
    R = 6371.0  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def match_volunteers(
    need: Need,
    volunteers: list[User],
    need_lat: float | None = None,
    need_lon: float | None = None,
) -> list[MatchResult]:
    """Score and rank volunteers for a given need.

    Scoring:
      skill_score     = +50 if primary skill matches; +10 per additional relevant tag
      proximity_score = max +50 for same location, linearly scaled to 0 at 100 km
      match_score     = skill_score + proximity_score  (always >= 0)

    Inactive volunteers are excluded.
    Results are sorted by match_score descending.
    """
    primary_skill = CATEGORY_TO_SKILL.get(need.category, "")
    # All skill values are considered "relevant" for secondary bonus
    relevant_skills = set(CATEGORY_TO_SKILL.values())

    results: list[MatchResult] = []

    for volunteer in volunteers:
        if not volunteer.is_active:
            continue

        # Parse comma-separated skill tags, strip whitespace
        raw_skills = volunteer.skills or ""
        skill_tags = [s.strip().lower() for s in raw_skills.split(",") if s.strip()]

        # Skill scoring
        skill_score = 0.0
        if primary_skill and primary_skill in skill_tags:
            skill_score += 50
            # +10 for each additional relevant tag beyond the primary
            for tag in skill_tags:
                if tag != primary_skill and tag in relevant_skills:
                    skill_score += 10
        else:
            # No primary match — still award secondary bonuses for any relevant tags
            for tag in skill_tags:
                if tag in relevant_skills:
                    skill_score += 10

        # Proximity scoring using Haversine distance
        proximity_score = 0.0
        distance_km: float | None = None

        if (
            need_lat is not None
            and need_lon is not None
            and volunteer.latitude is not None
            and volunteer.longitude is not None
        ):
            distance_km = haversine_distance(
                need_lat, need_lon, volunteer.latitude, volunteer.longitude
            )
            if distance_km <= MAX_DISTANCE_KM:
                proximity_score = MAX_PROXIMITY_SCORE * (
                    1.0 - distance_km / MAX_DISTANCE_KM
                )
            # Beyond MAX_DISTANCE_KM → proximity_score stays 0

        match_score = max(0.0, skill_score + proximity_score)

        results.append(
            MatchResult(
                volunteer_id=volunteer.id,
                name=volunteer.name,
                skills=skill_tags,
                match_score=match_score,
                distance_km=distance_km,
            )
        )

    results.sort(key=lambda r: r.match_score, reverse=True)
    return results
