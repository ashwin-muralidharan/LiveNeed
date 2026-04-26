"""Volunteers router for LiveNeed API.

Endpoints:
  POST /register-volunteer – register a new volunteer
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import RegisterVolunteerRequest

router = APIRouter()


@router.post("/register-volunteer")
def register_volunteer(body: RegisterVolunteerRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        name=body.name,
        email=body.email,
        role=body.role,
        skills=body.skills,
        latitude=body.latitude,
        longitude=body.longitude,
        is_active=True,
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"volunteer_id": user.id, "name": user.name, "email": user.email}
