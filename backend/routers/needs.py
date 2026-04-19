"""Needs router for LiveNeed API.

Endpoints:
  POST /submit-need  – accept and persist a new community need
  POST /analyze      – run NLP + urgency scoring on a need
  GET  /prioritize   – return active needs sorted by urgency DESC
  GET  /stats        – return summary counts
"""

import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ai.nlp_processor import process_need_text
from ai.urgency_scorer import compute_urgency
from database import get_db
from models import Need, User
from schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    NeedResponse,
    StatsResponse,
    SubmitNeedRequest,
    SubmitNeedResponse,
)

router = APIRouter()


@router.post("/submit-need", response_model=SubmitNeedResponse)
def submit_need(body: SubmitNeedRequest, db: Session = Depends(get_db)):
    if not body.raw_text.strip():
        raise HTTPException(status_code=422, detail="Need description cannot be empty")

    now = datetime.utcnow()
    need = Need(
        raw_text=body.raw_text,
        location_hint=body.location_hint,
        status="pending",
        submitted_at=now,
        updated_at=now,
    )
    db.add(need)
    db.commit()
    db.refresh(need)
    return SubmitNeedResponse(need_id=need.id, status="pending")


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(body: AnalyzeRequest, db: Session = Depends(get_db)):
    need = db.query(Need).filter(Need.id == body.need_id).first()
    if need is None:
        raise HTTPException(status_code=404, detail="Need not found")

    nlp_result = process_need_text(need.raw_text)
    score = compute_urgency(nlp_result, need.submitted_at)

    need.category = nlp_result.category
    need.urgency_score = score
    need.entities = json.dumps(nlp_result.entities)
    need.updated_at = datetime.utcnow()
    db.commit()

    return AnalyzeResponse(
        entities=nlp_result.entities,
        category=nlp_result.category,
        urgency_score=score,
    )


@router.get("/prioritize", response_model=list[NeedResponse])
def prioritize(db: Session = Depends(get_db)):
    needs = (
        db.query(Need)
        .filter(Need.status != "fulfilled")
        .order_by(Need.urgency_score.desc())
        .all()
    )
    results = []
    for need in needs:
        try:
            entities = json.loads(need.entities) if need.entities else {}
        except (json.JSONDecodeError, TypeError):
            entities = {}
        results.append(
            NeedResponse(
                id=need.id,
                raw_text=need.raw_text,
                category=need.category,
                urgency_score=need.urgency_score,
                status=need.status,
                entities=entities,
                location_hint=need.location_hint,
                submitted_at=need.submitted_at,
            )
        )
    return results


@router.get("/stats", response_model=StatsResponse)
def stats(db: Session = Depends(get_db)):
    active_needs = db.query(Need).filter(Need.status != "fulfilled").count()
    fulfilled_needs = db.query(Need).filter(Need.status == "fulfilled").count()
    volunteers_registered = db.query(User).count()
    return StatsResponse(
        active_needs=active_needs,
        fulfilled_needs=fulfilled_needs,
        volunteers_registered=volunteers_registered,
    )
