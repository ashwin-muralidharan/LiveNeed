from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routers import needs, matching, impact, volunteers, assignments, admin, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # Seed default admin accounts
    from database import SessionLocal
    from routers.auth import seed_default_admins
    db = SessionLocal()
    try:
        seed_default_admins(db)
    finally:
        db.close()
    yield


app = FastAPI(title="LiveNeed API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(needs.router)
app.include_router(matching.router)
app.include_router(impact.router)
app.include_router(volunteers.router)
app.include_router(assignments.router)
app.include_router(admin.router)
app.include_router(auth.router)

