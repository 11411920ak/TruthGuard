"""API router — aggregates all API routes."""

from fastapi import APIRouter
from app.api.analyze import router as analyze_router
from app.api.results import router as results_router
from app.api.history import router as history_router

api_router = APIRouter(prefix="/api")

api_router.include_router(analyze_router)
api_router.include_router(results_router)
api_router.include_router(history_router)
