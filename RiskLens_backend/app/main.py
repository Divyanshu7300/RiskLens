from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.core.config import CORS_ORIGINS
from app.api import auth, scan, dashboard, system, history, risk, report
from app.services.scheduler import start_scheduler


# ─────────────────────────────────────────────
# App Instance
# ─────────────────────────────────────────────
app = FastAPI(
    title="PolicyGuard Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# ─────────────────────────────────────────────
# Create Tables (Dev Only)
# ⚠ In production use Alembic migrations
# ─────────────────────────────────────────────
Base.metadata.create_all(bind=engine)


# ─────────────────────────────────────────────
# CORS Configuration (Loaded from .env)
# ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# Include Routers
# ─────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(scan.router)
app.include_router(dashboard.router)
app.include_router(history.router)
app.include_router(system.router)
app.include_router(risk.router)
app.include_router(report.router)


# ─────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "message": "PolicyGuard Backend Running"
    }


# ─────────────────────────────────────────────
# Startup Event
# ─────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    try:
        start_scheduler()
        print("Scheduler started successfully")
    except Exception as e:
        print("Scheduler failed to start:", e)