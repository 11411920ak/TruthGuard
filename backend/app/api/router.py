"""API router — aggregates all API routes."""

from fastapi import APIRouter
from app.api.analyze import router as analyze_router
from app.api.results import router as results_router
from app.api.history import router as history_router
from app.api.evaluation import router as evaluation_router

api_router = APIRouter(prefix="/api")

api_router.include_router(analyze_router)
api_router.include_router(results_router)
api_router.include_router(history_router)
api_router.include_router(evaluation_router)


# ── Direct Endpoints (Fact-Check & Image Analysis) ──

from pydantic import BaseModel
from fastapi import UploadFile, File
from app.services.factcheck import search_fact_checks
from app.api.analyze import analyze_image


class ClaimRequest(BaseModel):
    claim: str


@api_router.post("/fact-check", tags=["fact-check"])
def fact_check(request: ClaimRequest):
    """Direct Google Fact Check Tools API query."""
    return search_fact_checks(request.claim)


@api_router.post("/analyze-image", tags=["analyze"])
async def analyze_image_endpoint(file: UploadFile = File(...)):
    """Upload Instagram/Twitter/news screenshot for Gemini Vision claim extraction & verification."""
    return await analyze_image(file)

