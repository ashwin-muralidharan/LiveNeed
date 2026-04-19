from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Assignment, ImpactLog, Need
from schemas import VerifyImpactRequest, VerifyImpactResponse

router = APIRouter()


@router.post("/verify-impact", response_model=VerifyImpactResponse)
def verify_impact(request: VerifyImpactRequest, db: Session = Depends(get_db)):
    # Look up the need; 404 if not found
    need = db.query(Need).filter(Need.id == request.need_id).first()
    if need is None:
        raise HTTPException(status_code=404, detail="Need not found")

    # Reject if already fulfilled
    if need.status == "fulfilled":
        raise HTTPException(status_code=409, detail="Need is already fulfilled")

    # Check that an active assignment exists for this volunteer/need pair
    assignment = (
        db.query(Assignment)
        .filter(
            Assignment.need_id == request.need_id,
            Assignment.volunteer_id == request.volunteer_id,
            Assignment.status == "active",
        )
        .first()
    )
    if assignment is None:
        raise HTTPException(status_code=403, detail="Volunteer not assigned to this need")

    # Insert ImpactLog record
    now = datetime.utcnow()
    log = ImpactLog(
        need_id=request.need_id,
        volunteer_id=request.volunteer_id,
        notes=request.notes,
        photo_url=request.photo_url,
        verified_at=now,
    )
    db.add(log)

    # Update Need status to fulfilled
    need.status = "fulfilled"
    need.updated_at = now

    # Update Assignment status to completed
    assignment.status = "completed"

    db.commit()
    db.refresh(log)

    return VerifyImpactResponse(impact_log_id=log.id, confirmed=True)
