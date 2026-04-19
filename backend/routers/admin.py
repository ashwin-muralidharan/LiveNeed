"""Admin router for LiveNeed API.

Endpoints:
  GET    /admin/volunteers          – list all volunteers
  PATCH  /admin/volunteers/{id}     – update volunteer (activate/deactivate, update skills)
  DELETE /admin/volunteers/{id}     – remove a volunteer
  GET    /admin/needs               – list ALL needs (including fulfilled)
  PATCH  /admin/needs/{id}/status   – update need status manually
  DELETE /admin/needs/{id}          – remove a need
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import AdminUser, Assignment, ImpactLog, Need, User
from routers.auth import get_current_admin

router = APIRouter(prefix="/admin", tags=["admin"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class UpdateVolunteerRequest(BaseModel):
    name: str | None = None
    skills: str | None = None
    is_active: bool | None = None
    latitude: float | None = None
    longitude: float | None = None


class UpdateNeedStatusRequest(BaseModel):
    status: str  # pending | assigned | fulfilled


# ---------------------------------------------------------------------------
# Volunteer endpoints
# ---------------------------------------------------------------------------

@router.get("/volunteers")
def list_volunteers(admin: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    volunteers = db.query(User).order_by(User.created_at.desc()).all()
    return [
        {
            "id": v.id,
            "name": v.name,
            "email": v.email,
            "role": v.role,
            "skills": v.skills,
            "latitude": v.latitude,
            "longitude": v.longitude,
            "is_active": v.is_active,
            "created_at": v.created_at.isoformat() if v.created_at else None,
        }
        for v in volunteers
    ]


@router.patch("/volunteers/{volunteer_id}")
def update_volunteer(volunteer_id: int, body: UpdateVolunteerRequest, admin: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    volunteer = db.query(User).filter(User.id == volunteer_id).first()
    if volunteer is None:
        raise HTTPException(status_code=404, detail="Volunteer not found")

    if body.name is not None:
        volunteer.name = body.name
    if body.skills is not None:
        volunteer.skills = body.skills
    if body.is_active is not None:
        volunteer.is_active = body.is_active
    if body.latitude is not None:
        volunteer.latitude = body.latitude
    if body.longitude is not None:
        volunteer.longitude = body.longitude

    db.commit()
    db.refresh(volunteer)

    return {
        "id": volunteer.id,
        "name": volunteer.name,
        "email": volunteer.email,
        "skills": volunteer.skills,
        "is_active": volunteer.is_active,
        "message": "Volunteer updated successfully",
    }


@router.delete("/volunteers/{volunteer_id}")
def delete_volunteer(volunteer_id: int, admin: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    volunteer = db.query(User).filter(User.id == volunteer_id).first()
    if volunteer is None:
        raise HTTPException(status_code=404, detail="Volunteer not found")

    # Remove related assignments first
    db.query(Assignment).filter(Assignment.volunteer_id == volunteer_id).delete()
    db.query(ImpactLog).filter(ImpactLog.volunteer_id == volunteer_id).delete()
    db.delete(volunteer)
    db.commit()

    return {"message": f"Volunteer '{volunteer.name}' removed successfully"}


# ---------------------------------------------------------------------------
# Need endpoints
# ---------------------------------------------------------------------------

@router.get("/needs")
def list_all_needs(admin: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    needs = db.query(Need).order_by(Need.urgency_score.desc()).all()
    return [
        {
            "id": n.id,
            "raw_text": n.raw_text,
            "category": n.category,
            "urgency_score": n.urgency_score,
            "status": n.status,
            "entities": n.entities,
            "location_hint": n.location_hint,
            "submitted_at": n.submitted_at.isoformat() if n.submitted_at else None,
            "updated_at": n.updated_at.isoformat() if n.updated_at else None,
        }
        for n in needs
    ]


@router.patch("/needs/{need_id}/status")
def update_need_status(need_id: int, body: UpdateNeedStatusRequest, admin: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    need = db.query(Need).filter(Need.id == need_id).first()
    if need is None:
        raise HTTPException(status_code=404, detail="Need not found")

    valid_statuses = {"pending", "assigned", "fulfilled"}
    if body.status not in valid_statuses:
        raise HTTPException(status_code=422, detail=f"Status must be one of: {', '.join(valid_statuses)}")

    old_status = need.status
    need.status = body.status
    need.updated_at = datetime.utcnow()
    db.commit()

    return {
        "id": need.id,
        "old_status": old_status,
        "new_status": body.status,
        "message": f"Need status updated from '{old_status}' to '{body.status}'",
    }


@router.delete("/needs/{need_id}")
def delete_need(need_id: int, admin: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    need = db.query(Need).filter(Need.id == need_id).first()
    if need is None:
        raise HTTPException(status_code=404, detail="Need not found")

    # Remove related records
    db.query(Assignment).filter(Assignment.need_id == need_id).delete()
    db.query(ImpactLog).filter(ImpactLog.need_id == need_id).delete()
    db.delete(need)
    db.commit()

    return {"message": f"Need #{need_id} removed successfully"}
