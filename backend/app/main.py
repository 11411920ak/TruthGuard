"""
TruthGuard — FastAPI Backend

AI-Based Digital Content Verification & Scam Detection System.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.router import api_router
from app.models.database import init_db
from app.schemas.analysis import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    settings = get_settings()
    # Create database tables on startup
    await init_db(settings.database_url)
    print("[OK] Database initialized")
    print(f"[TruthGuard] API running at http://{settings.host}:{settings.port}")
    yield
    print("[TruthGuard] API shutting down")


app = FastAPI(
    title="TruthGuard API",
    description="AI-Based Digital Content Verification & Scam Detection System",
    version="0.1.0",
    lifespan=lifespan,
)

# ── CORS ──
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ──
app.include_router(api_router)


@app.get("/api/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """API health check endpoint."""
    return HealthResponse()
