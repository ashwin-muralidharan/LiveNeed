"""Gemini-powered chatbot router for LiveNeed.

Uses Gemini Function Calling to let users:
  1. Register as a volunteer
  2. Submit a need/report
  3. Check report status by ID

Endpoint:
  POST /chat  – send a message, get an AI response
"""

import json
import time
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

import google.generativeai as genai

from database import get_db
from models import Need, User, Assignment
from ai.nlp_processor import process_need_text
from ai.urgency_scorer import compute_urgency

router = APIRouter(prefix="/chat", tags=["chatbot"])

# ---------------------------------------------------------------------------
# ⚠️  PASTE YOUR GEMINI API KEY HERE  ⚠️
# ---------------------------------------------------------------------------
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
# ---------------------------------------------------------------------------

genai.configure(api_key=GEMINI_API_KEY)

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    history: list[dict] | None = None   # [{"role": "user"/"model", "text": "..."}]


class ChatResponse(BaseModel):
    reply: str
    action_taken: str | None = None     # e.g. "registered_volunteer", "submitted_report"


# ---------------------------------------------------------------------------
# Tool functions (executed by the backend when Gemini requests them)
# ---------------------------------------------------------------------------

def register_volunteer(name: str, email: str, skills: str, db: Session) -> dict:
    """Register a new volunteer in the LiveNeed platform."""
    # Check duplicate
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return {"success": False, "error": f"A volunteer with email {email} is already registered."}

    user = User(
        name=name,
        email=email,
        role="volunteer",
        skills=skills,
        is_active=True,
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "success": True,
        "volunteer_id": user.id,
        "name": user.name,
        "email": user.email,
        "skills": user.skills,
        "message": f"Volunteer '{name}' registered successfully with ID #{user.id}."
    }


def submit_report(description: str, location: str | None, db: Session) -> dict:
    """Submit a new community need/report and run NLP analysis."""
    if not description.strip():
        return {"success": False, "error": "Report description cannot be empty."}

    now = datetime.utcnow()
    need = Need(
        raw_text=description,
        location_hint=location,
        status="pending",
        submitted_at=now,
        updated_at=now,
    )
    db.add(need)
    db.commit()
    db.refresh(need)

    # Run NLP analysis and urgency scoring (reuse existing AI pipeline)
    nlp_result = process_need_text(description)
    score = compute_urgency(nlp_result, now)

    need.category = nlp_result.category
    need.urgency_score = score
    need.entities = json.dumps(nlp_result.entities)
    need.updated_at = datetime.utcnow()
    db.commit()

    return {
        "success": True,
        "report_id": need.id,
        "category": need.category,
        "urgency_score": need.urgency_score,
        "status": need.status,
        "message": f"Report submitted successfully! Your unique Report ID is #{need.id}. Category: {need.category}, Urgency: {need.urgency_score}/100."
    }


def get_report_status(report_id: int, db: Session) -> dict:
    """Look up a report by its unique ID and return full status details."""
    need = db.query(Need).filter(Need.id == report_id).first()
    if need is None:
        return {"success": False, "error": f"No report found with ID #{report_id}."}

    result = {
        "success": True,
        "report_id": need.id,
        "description": need.raw_text,
        "category": need.category,
        "urgency_score": need.urgency_score,
        "status": need.status,
        "location": need.location_hint or "Not specified",
        "submitted_at": need.submitted_at.isoformat() if need.submitted_at else None,
        "assigned_volunteer": None,
    }

    # Check if a volunteer is assigned
    assignment = (
        db.query(Assignment)
        .filter(Assignment.need_id == report_id, Assignment.status == "active")
        .first()
    )
    if assignment:
        volunteer = db.query(User).filter(User.id == assignment.volunteer_id).first()
        if volunteer:
            result["assigned_volunteer"] = {
                "id": volunteer.id,
                "name": volunteer.name,
                "email": volunteer.email,
                "skills": volunteer.skills,
            }

    return result


# ---------------------------------------------------------------------------
# Gemini tool declarations
# ---------------------------------------------------------------------------

tools = [
    genai.protos.Tool(
        function_declarations=[
            genai.protos.FunctionDeclaration(
                name="register_volunteer",
                description="Register a new volunteer on the LiveNeed platform. Call this when the user wants to sign up as a volunteer. You must collect their name, email, and skills before calling this function.",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "name": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="Full name of the volunteer"
                        ),
                        "email": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="Email address of the volunteer"
                        ),
                        "skills": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="Comma-separated list of skills (e.g. 'medical,logistics,general'). Valid skills: medical, logistics, general, construction, education"
                        ),
                    },
                    required=["name", "email", "skills"],
                ),
            ),
            genai.protos.FunctionDeclaration(
                name="submit_report",
                description="Submit a new community need or emergency report. Call this when the user describes a situation that needs help. Capture the full description and any mentioned location.",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "description": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="Full description of the need or emergency situation"
                        ),
                        "location": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="Location where help is needed (address, area name, or landmark). Can be empty if not mentioned."
                        ),
                    },
                    required=["description"],
                ),
            ),
            genai.protos.FunctionDeclaration(
                name="get_report_status",
                description="Check the status of an existing report by its unique Report ID number. Call this when the user wants to know the status of a specific report.",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "report_id": genai.protos.Schema(
                            type=genai.protos.Type.INTEGER,
                            description="The unique report/need ID number"
                        ),
                    },
                    required=["report_id"],
                ),
            ),
        ]
    )
]

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are LiveNeed Assistant, an AI-powered helper for the LiveNeed community resource platform.

Your capabilities:
1. **Register Volunteers** — Help people sign up as volunteers. You need their name, email, and skills (medical, logistics, general, construction, education). Ask for any missing details before registering.
2. **Submit Reports** — Help people report community needs or emergencies. Capture a clear description and location. After submitting, always tell them their unique Report ID so they can track it.
3. **Check Report Status** — Look up any report by its ID number. Share the category, urgency score, current status, and whether a volunteer has been assigned.

Guidelines:
- Be friendly, concise, and helpful.
- When a user wants to volunteer, ask for their name, email, and skills one at a time if not all provided.
- When a user reports a need, ask clarifying questions if the description is too vague.
- Always confirm actions with the user before executing.
- If a user types just a number, treat it as a report ID lookup.
- Format responses clearly with relevant details.
- Do NOT make up data — only use information returned by the tool functions.
"""

# ---------------------------------------------------------------------------
# Chat endpoint
# ---------------------------------------------------------------------------

@router.post("", response_model=ChatResponse)
def chat(body: ChatRequest, db: Session = Depends(get_db)):
    """Process a chat message and return an AI response."""

    # Check if API key is configured
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        return ChatResponse(
            reply="⚠️ The Gemini API key has not been configured yet. Please add your API key in `backend/routers/chatbot.py` (line 33) to enable the chatbot.",
            action_taken=None,
        )

    try:
        # Try multiple models in order of preference (fallback if quota exhausted)
        models_to_try = ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.0-flash"]
        last_error = None

        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    tools=tools,
                    system_instruction=SYSTEM_PROMPT,
                )

                # Build conversation history for Gemini
                gemini_history = []
                if body.history:
                    for msg in body.history:
                        role = msg.get("role", "user")
                        text = msg.get("text", "")
                        if role in ("user", "model") and text:
                            gemini_history.append(
                                genai.protos.Content(
                                    role=role,
                                    parts=[genai.protos.Part(text=text)]
                                )
                            )

                # Start chat with history
                chat_session = model.start_chat(history=gemini_history)

                # Send with retry for rate limits (max 2 retries)
                response = None
                for attempt in range(3):
                    try:
                        response = chat_session.send_message(body.message)
                        break
                    except Exception as retry_err:
                        if "429" in str(retry_err) and attempt < 2:
                            time.sleep(2 * (attempt + 1))  # wait 2s, 4s
                            continue
                        raise

                if response is None:
                    continue

                # If we got here, the model worked — break out of the model loop
                break

            except Exception as model_err:
                last_error = model_err
                err_str = str(model_err)
                if "429" in err_str or "404" in err_str:
                    continue  # try next model
                raise  # non-quota error, raise immediately
        else:
            # All models exhausted
            return ChatResponse(
                reply="⚠️ The Gemini API is temporarily rate-limited. Please wait 30-60 seconds and try again. All free-tier models have been tried.",
                action_taken=None,
            )

        action_taken = None

        # Handle function calls (Gemini may request tool execution)
        while response.candidates[0].content.parts[0].function_call.name:
            fc = response.candidates[0].content.parts[0].function_call
            fn_name = fc.name
            fn_args = dict(fc.args)

            # Execute the requested function
            if fn_name == "register_volunteer":
                fn_result = register_volunteer(
                    name=fn_args.get("name", ""),
                    email=fn_args.get("email", ""),
                    skills=fn_args.get("skills", "general"),
                    db=db,
                )
                action_taken = "registered_volunteer"

            elif fn_name == "submit_report":
                fn_result = submit_report(
                    description=fn_args.get("description", ""),
                    location=fn_args.get("location"),
                    db=db,
                )
                action_taken = "submitted_report"

            elif fn_name == "get_report_status":
                fn_result = get_report_status(
                    report_id=int(fn_args.get("report_id", 0)),
                    db=db,
                )
                action_taken = "checked_status"

            else:
                fn_result = {"error": f"Unknown function: {fn_name}"}

            # Send the function result back to Gemini
            response = chat_session.send_message(
                genai.protos.Content(
                    parts=[
                        genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=fn_name,
                                response={"result": fn_result},
                            )
                        )
                    ]
                )
            )

            # Check if there's another function call (chained calls)
            try:
                if not response.candidates[0].content.parts[0].function_call.name:
                    break
            except (AttributeError, IndexError):
                break

        # Extract the final text response
        reply_text = ""
        for part in response.candidates[0].content.parts:
            if part.text:
                reply_text += part.text

        if not reply_text:
            reply_text = "I'm sorry, I couldn't process that request. Could you try rephrasing?"

        return ChatResponse(reply=reply_text, action_taken=action_taken)

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            return ChatResponse(
                reply="⚠️ Rate limit reached. Please wait about 30-60 seconds and try again.",
                action_taken=None,
            )
        if "API_KEY" in error_msg.upper() or "403" in error_msg or "401" in error_msg:
            return ChatResponse(
                reply="⚠️ There's an issue with the Gemini API key. Please check that the key in `backend/routers/chatbot.py` is valid and has the Generative Language API enabled.",
                action_taken=None,
            )
        return ChatResponse(
            reply=f"I encountered an error while processing your message. Please try again. (Error: {error_msg})",
            action_taken=None,
        )
