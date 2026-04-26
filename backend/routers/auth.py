"""Authentication router for Admin access.

Endpoints:
  POST /auth/login              – login with email+password, returns JWT
  POST /auth/register           – register new admin (pending approval)
  GET  /auth/me                 – get current admin info
  GET  /auth/pending            – list pending admin registrations (auth required)
  POST /auth/approve/{admin_id} – approve a pending admin (auth required)
  POST /auth/reject/{admin_id}  – reject a pending admin (auth required)
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import AdminUser

router = APIRouter(prefix="/auth", tags=["auth"])

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SECRET_KEY = "liveneed-hackathon-secret-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(admin_id: int, email: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {"sub": str(admin_id), "email": email, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_admin(
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> AdminUser:
    """Dependency: extracts and validates JWT, returns the AdminUser."""
    if creds is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        admin_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    admin = db.query(AdminUser).filter(AdminUser.id == admin_id).first()
    if admin is None or not admin.is_approved:
        raise HTTPException(status_code=401, detail="Admin not found or not approved")
    return admin


# ---------------------------------------------------------------------------
# Seed default admins on first import
# ---------------------------------------------------------------------------

def seed_default_admins(db: Session):
    """Create the two default admin accounts if they don't exist."""
    defaults = [
        {"email": "maneesh@gmail.com", "name": "Maneesh", "password": "12345"},
        {"email": "ashwin@gmail.com", "name": "Ashwin", "password": "12345"},
    ]
    for d in defaults:
        existing = db.query(AdminUser).filter(AdminUser.email == d["email"]).first()
        if existing is None:
            admin = AdminUser(
                email=d["email"],
                name=d["name"],
                hashed_password=hash_password(d["password"]),
                is_approved=True,
                created_at=datetime.utcnow(),
            )
            db.add(admin)
    db.commit()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    admin = db.query(AdminUser).filter(AdminUser.email == body.email).first()
    if admin is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not verify_password(body.password, admin.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not admin.is_approved:
        raise HTTPException(status_code=403, detail="Your account is pending approval from an existing admin")

    token = create_token(admin.id, admin.email)
    return {
        "token": token,
        "admin_id": admin.id,
        "name": admin.name,
        "email": admin.email,
    }


@router.post("/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if not body.name.strip() or not body.email.strip() or not body.password.strip():
        raise HTTPException(status_code=422, detail="All fields are required")
    if len(body.password) < 4:
        raise HTTPException(status_code=422, detail="Password must be at least 4 characters")

    existing = db.query(AdminUser).filter(AdminUser.email == body.email).first()
    if existing is not None:
        raise HTTPException(status_code=409, detail="Email already registered")

    admin = AdminUser(
        email=body.email.strip(),
        name=body.name.strip(),
        hashed_password=hash_password(body.password),
        is_approved=False,
        created_at=datetime.utcnow(),
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    return {
        "message": "Registration submitted. An existing admin must approve your account.",
        "admin_id": admin.id,
        "name": admin.name,
        "email": admin.email,
    }


@router.get("/me")
def get_me(admin: AdminUser = Depends(get_current_admin)):
    return {"admin_id": admin.id, "name": admin.name, "email": admin.email}


@router.get("/pending")
def list_pending(admin: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    pending = db.query(AdminUser).filter(AdminUser.is_approved == False).all()
    return [
        {"id": p.id, "name": p.name, "email": p.email, "created_at": p.created_at.isoformat() if p.created_at else None}
        for p in pending
    ]


@router.post("/approve/{admin_id}")
def approve_admin(admin_id: int, admin: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    target = db.query(AdminUser).filter(AdminUser.id == admin_id).first()
    if target is None:
        raise HTTPException(status_code=404, detail="Admin not found")
    if target.is_approved:
        raise HTTPException(status_code=409, detail="Already approved")
    target.is_approved = True
    db.commit()
    return {"message": f"Admin '{target.name}' approved successfully"}


@router.post("/reject/{admin_id}")
def reject_admin(admin_id: int, admin: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    target = db.query(AdminUser).filter(AdminUser.id == admin_id).first()
    if target is None:
        raise HTTPException(status_code=404, detail="Admin not found")
    db.delete(target)
    db.commit()
    return {"message": f"Admin registration for '{target.name}' rejected and removed"}
