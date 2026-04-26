from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class SubmitNeedRequest(BaseModel):
    raw_text: str
    location_hint: str | None = None


class AnalyzeRequest(BaseModel):
    need_id: int


class MatchRequest(BaseModel):
    need_id: int


class VerifyImpactRequest(BaseModel):
    need_id: int
    volunteer_id: int
    notes: str | None = None
    photo_url: str | None = None


class AssignRequest(BaseModel):
    need_id: int
    volunteer_id: int


class RegisterVolunteerRequest(BaseModel):
    name: str
    email: str
    role: str = "volunteer"
    skills: str
    latitude: float | None = None
    longitude: float | None = None


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class NeedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    raw_text: str
    category: str
    urgency_score: float
    status: str
    entities: dict
    location_hint: str | None
    submitted_at: datetime


class VolunteerMatchResult(BaseModel):
    volunteer_id: int
    name: str
    skills: list[str]
    match_score: float
    distance_km: float | None


class SubmitNeedResponse(BaseModel):
    need_id: int
    status: str


class AnalyzeResponse(BaseModel):
    entities: dict
    category: str
    urgency_score: float


class MatchResponse(BaseModel):
    matches: list[VolunteerMatchResult]


class VerifyImpactResponse(BaseModel):
    impact_log_id: int
    confirmed: bool


class StatsResponse(BaseModel):
    active_needs: int
    fulfilled_needs: int
    volunteers_registered: int
