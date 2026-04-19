"""Assignments router for LiveNeed API.

Endpoints:
  POST /assign       – assign a volunteer to a need
  GET  /assignments  – list all active assignments
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Assignment, Need, User
from schemas import AssignRequest

router = APIRouter()


@router.post("/assign")
def assign_volunteer(body: AssignRequest, db: Session = Depends(get_db)):
    # Look up the need
    need = db.query(Need).filter(Need.id == body.need_id).first()
    if need is None:
        raise HTTPException(status_code=404, detail="Need not found")

    if need.status == "fulfilled":
        raise HTTPException(status_code=409, detail="Need is already fulfilled")

    # Look up the volunteer
    volunteer = db.query(User).filter(User.id == body.volunteer_id).first()
    if volunteer is None:
        raise HTTPException(status_code=404, detail="Volunteer not found")

    if not volunteer.is_active:
        raise HTTPException(status_code=409, detail="Volunteer is inactive")

    # Check for existing active assignment
    existing = (
        db.query(Assignment)
        .filter(
            Assignment.need_id == body.need_id,
            Assignment.volunteer_id == body.volunteer_id,
            Assignment.status == "active",
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Volunteer already assigned to this need")

    assignment = Assignment(
        need_id=body.need_id,
        volunteer_id=body.volunteer_id,
        assigned_at=datetime.utcnow(),
        status="active",
    )
    db.add(assignment)

    # Update need status
    need.status = "assigned"
    need.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(assignment)

    return {
        "assignment_id": assignment.id,
        "need_id": assignment.need_id,
        "volunteer_id": assignment.volunteer_id,
        "status": assignment.status,
    }


@router.get("/assignments")
def list_assignments(db: Session = Depends(get_db)):
    assignments = (
        db.query(Assignment)
        .filter(Assignment.status == "active")
        .all()
    )
    return [
        {
            "assignment_id": a.id,
            "need_id": a.need_id,
            "volunteer_id": a.volunteer_id,
            "assigned_at": a.assigned_at.isoformat() if a.assigned_at else None,
            "status": a.status,
        }
        for a in assignments
    ]
