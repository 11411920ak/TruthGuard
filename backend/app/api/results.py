"""Results API endpoint — GET /api/results/{id}"""

from fastapi import APIRouter, HTTPException

from app.schemas.analysis import AnalysisResultResponse, ClaimResponse, SourceResponse, ReasonResponse
from app.models.database import Analysis, get_session_factory
from app.config import get_settings
from sqlalchemy import select
from sqlalchemy.orm import selectinload

router = APIRouter(tags=["results"])


@router.get("/results/{analysis_id}", response_model=AnalysisResultResponse)
async def get_result(analysis_id: str):
    """Retrieve the full analysis result by ID."""
    settings = get_settings()
    session_factory = get_session_factory(settings.database_url)

    async with session_factory() as session:
        stmt = (
            select(Analysis)
            .options(
                selectinload(Analysis.claims),
                selectinload(Analysis.sources),
                selectinload(Analysis.result),
            )
            .where(Analysis.id == analysis_id)
        )
        result = await session.execute(stmt)
        analysis = result.scalar_one_or_none()

        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        if analysis.status != "completed":
            raise HTTPException(status_code=202, detail="Analysis still in progress")

        # Build response
        claims = [
            ClaimResponse(
                id=c.id,
                claim_text=c.claim_text,
                claim_type=c.claim_type,
                verdict=c.verdict,
                confidence=c.confidence,
            )
            for c in analysis.claims
        ]

        sources = [
            SourceResponse(
                name=s.title or "Unknown Source",
                type=s.source_type,
                url=s.url,
                reliability=s.reliability_score or 0.0,
            )
            for s in analysis.sources
        ]

        # Build reasons from the result explanation
        reasons = []
        if analysis.result and analysis.result.explanation:
            for reason_text in analysis.result.explanation.split("; "):
                reason_type = "warning"
                if "contradict" in reason_text.lower() or "does not" in reason_text.lower():
                    reason_type = "contradiction"
                elif "confirm" in reason_text.lower() or "support" in reason_text.lower():
                    reason_type = "support"
                reasons.append(ReasonResponse(type=reason_type, text=reason_text))

        return AnalysisResultResponse(
            id=analysis.id,
            input_type=analysis.input_type,
            input_content=analysis.input_content,
            verdict=analysis.verdict or "UNVERIFIED",
            confidence=analysis.confidence or 0,
            risk_score=analysis.risk_score or 0,
            evidence_coverage=analysis.evidence_coverage or 0,
            created_at=analysis.created_at.isoformat() if analysis.created_at else "",
            claims=claims,
            reasons=reasons,
            sources=sources,
            recommendation=analysis.result.recommendation if analysis.result else "",
        )
