from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)          # "volunteer" | "coordinator"
    skills = Column(String, nullable=False)        # comma-separated tags
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Need(Base):
    __tablename__ = "needs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    raw_text = Column(String, nullable=False)
    category = Column(String, default="other", nullable=False)
    urgency_score = Column(Float, default=0.0, nullable=False)
    entities = Column(String, default="{}", nullable=False)    # JSON string
    status = Column(String, default="pending", nullable=False) # pending|assigned|fulfilled
    location_hint = Column(String, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    need_id = Column(Integer, ForeignKey("needs.id"), nullable=False)
    volunteer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String, default="active", nullable=False)  # active|completed


class ImpactLog(Base):
    __tablename__ = "impact_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    need_id = Column(Integer, ForeignKey("needs.id"), nullable=False)
    volunteer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    notes = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)
    verified_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_approved = Column(Boolean, default=False, nullable=False)  # needs approval from existing admin
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

