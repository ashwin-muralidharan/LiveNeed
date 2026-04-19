from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from matching_engine import match_volunteers
from models import Assignment, Need, User
from schemas import MatchRequest, MatchResponse, VolunteerMatchResult

router = APIRouter()


@router.post("/match", response_model=MatchResponse)
def match(request: MatchRequest, db: Session = Depends(get_db)):
    # Look up the need; 404 if not found
    need = db.query(Need).filter(Need.id == request.need_id).first()
    if need is None:
        raise HTTPException(status_code=404, detail="Need not found")

    # Find volunteer IDs that already have an active assignment
    busy_volunteer_ids = {
        row.volunteer_id
        for row in db.query(Assignment.volunteer_id)
        .filter(Assignment.status == "active")
        .all()
    }

    # Query all active volunteers who are not already assigned
    available_volunteers = (
        db.query(User)
        .filter(User.is_active == True)  # noqa: E712
        .filter(User.id.notin_(busy_volunteer_ids))
        .all()
    )

    # Score and rank
    results = match_volunteers(need, available_volunteers)

    matches = [
        VolunteerMatchResult(
            volunteer_id=r.volunteer_id,
            name=r.name,
            skills=r.skills,
            match_score=r.match_score,
            distance_km=r.distance_km,
        )
        for r in results
    ]

    return MatchResponse(matches=matches)
