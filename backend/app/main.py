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

# ── Security Headers Middleware ──
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# ── Routes ──
app.include_router(api_router)


@app.get("/api/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """API health check endpoint."""
    return HealthResponse(
        status="ok",
        version="0.1.0",
        project="TruthGuard",
        database="connected",
    )
