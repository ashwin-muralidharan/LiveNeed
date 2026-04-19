"""Shared pytest fixtures for LiveNeed backend tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

from database import Base, get_db
import models  # noqa: F401 – registers all ORM models on Base
from main import app

# Use a named in-memory DB so all connections share the same data
TEST_DB_URL = "sqlite:///file::memory:?cache=shared&uri=true"


@pytest.fixture()
def client():
    """FastAPI TestClient backed by a shared in-memory SQLite database."""
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False, "uri": True},
    )

    # Create all tables
    with engine.begin() as conn:
        Base.metadata.create_all(conn)

    TestingSession = sessionmaker(autocommit=False, autoflush=False)

    def override_get_db():
        db = TestingSession(bind=engine)
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

    with engine.begin() as conn:
        Base.metadata.drop_all(conn)
    engine.dispose()
