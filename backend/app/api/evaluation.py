"""Evaluation API endpoints — GET /api/evaluation/metrics and POST /api/evaluation/run"""

from fastapi import APIRouter
from app.evaluation.evaluator import run_benchmark_evaluation, get_cached_or_default_metrics

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.get("/metrics")
async def get_metrics():
    """Retrieve current classification accuracy, F1-scores, and confusion matrix."""
    return get_cached_or_default_metrics()


@router.post("/run")
async def run_benchmark():
    """Execute live evaluation benchmark across all ground-truth test cases."""
    return await run_benchmark_evaluation()
