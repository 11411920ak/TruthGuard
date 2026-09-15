"""History & Analytics API endpoints — GET /api/history and GET /api/history/stats"""

from typing import Optional
from fastapi import APIRouter, Query
from sqlalchemy import select

from app.schemas.analysis import (
    HistoryResponse,
    HistoryItemResponse,
    DashboardStatsResponse,
)
from app.models.database import Analysis, get_session_factory
from app.config import get_settings

router = APIRouter(tags=["history"])


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    search: Optional[str] = Query(None, description="Search term in input content"),
    input_type: Optional[str] = Query(None, description="Filter by input modality (text, url, image, video, social)"),
    verdict: Optional[str] = Query(None, description="Filter by verdict"),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Retrieve past analyses with optional filtering, search, and pagination."""
    settings = get_settings()
    session_factory = get_session_factory(settings.database_url)

    async with session_factory() as session:
        stmt = (
            select(Analysis)
            .where(Analysis.status == "completed")
            .order_by(Analysis.created_at.desc())
        )

        if input_type and input_type.lower() != "all":
            stmt = stmt.where(Analysis.input_type == input_type.lower())

        if verdict and verdict.upper() != "ALL":
            stmt = stmt.where(Analysis.verdict == verdict.upper())

        if search and search.strip():
            term = f"%{search.strip()}%"
            stmt = stmt.where(Analysis.input_content.ilike(term))

        stmt = stmt.offset(offset).limit(limit)
        result = await session.execute(stmt)
        analyses = result.scalars().all()

        items = [
            HistoryItemResponse(
                id=a.id,
                input_type=a.input_type,
                input_content=a.input_content[:200],  # Truncate for list view
                verdict=a.verdict or "UNVERIFIED",
                confidence=a.confidence or 0.0,
                risk_score=a.risk_score or 0.0,
                created_at=a.created_at.isoformat() if a.created_at else "",
            )
            for a in analyses
        ]

        return HistoryResponse(analyses=items, total=len(items))


@router.get("/history/stats", response_model=DashboardStatsResponse)
async def get_history_stats():
    """Aggregate high-level forensics metrics and threat intelligence for the dashboard."""
    settings = get_settings()
    session_factory = get_session_factory(settings.database_url)

    async with session_factory() as session:
        stmt = (
            select(Analysis)
            .where(Analysis.status == "completed")
            .order_by(Analysis.created_at.desc())
        )
        result = await session.execute(stmt)
        analyses = result.scalars().all()

        total = len(analyses)
        if total == 0:
            return DashboardStatsResponse()

        verdict_counts = {
            "LIKELY_TRUE": 0,
            "LIKELY_FALSE": 0,
            "SUSPICIOUS": 0,
            "UNVERIFIED": 0,
        }
        type_counts = {
            "text": 0,
            "url": 0,
            "image": 0,
            "video": 0,
            "social": 0,
        }

        total_conf = 0.0
        total_risk = 0.0
        threat_snippets = []

        for a in analyses:
            # Verdict counts
            v = (a.verdict or "UNVERIFIED").upper()
            if v in verdict_counts:
                verdict_counts[v] += 1
            else:
                verdict_counts["UNVERIFIED"] += 1

            # Modality counts
            t = (a.input_type or "text").lower()
            if t in type_counts:
                type_counts[t] += 1
            else:
                type_counts["text"] += 1

            total_conf += a.confidence or 0.0
            total_risk += a.risk_score or 0.0

            # Collect recent high-risk threats
            if v in ("LIKELY_FALSE", "SUSPICIOUS") and len(threat_snippets) < 5:
                clean_content = a.input_content.replace("\n", " ").strip()
                if clean_content and len(clean_content) > 10:
                    snippet = clean_content[:80] + ("..." if len(clean_content) > 80 else "")
                    if snippet not in threat_snippets:
                        threat_snippets.append(snippet)

        avg_conf = round(total_conf / total, 1) if total > 0 else 0.0
        avg_risk = round(total_risk / total, 1) if total > 0 else 0.0

        return DashboardStatsResponse(
            total_scans=total,
            verdict_counts=verdict_counts,
            type_counts=type_counts,
            avg_confidence=avg_conf,
            avg_risk_score=avg_risk,
            recent_threats=threat_snippets,
        )
