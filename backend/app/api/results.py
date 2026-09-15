"""Results API endpoint — GET /api/results/{id}"""

from fastapi import APIRouter, HTTPException

from urllib.parse import urlparse
from app.schemas.analysis import (
    AnalysisResultResponse,
    ClaimResponse,
    SourceResponse,
    ReasonResponse,
    WebsiteDetails,
)
from app.models.database import Analysis, Claim, get_session_factory
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
                selectinload(Analysis.claims).selectinload(Claim.evidence),
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
        claims = []
        for c in analysis.claims:
            parsed_entities = []
            if getattr(c, "entities", None):
                try:
                    import json
                    parsed_entities = json.loads(c.entities)
                except Exception:
                    parsed_entities = [e.strip() for e in c.entities.split(",") if e.strip()]

            claims.append(
                ClaimResponse(
                    id=c.id,
                    claim_text=c.claim_text,
                    claim_type=c.claim_type,
                    verdict=c.verdict,
                    confidence=c.confidence,
                    entities=parsed_entities if isinstance(parsed_entities, list) else [],
                )
            )

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
            for raw_reason in analysis.result.explanation.split("; "):
                clean_text = raw_reason.strip()
                if not clean_text:
                    continue
                reason_type = "warning"
                if clean_text.startswith("[contradiction] "):
                    reason_type = "contradiction"
                    clean_text = clean_text[len("[contradiction] "):]
                elif clean_text.startswith("[support] "):
                    reason_type = "support"
                    clean_text = clean_text[len("[support] "):]
                elif clean_text.startswith("[warning] "):
                    reason_type = "warning"
                    clean_text = clean_text[len("[warning] "):]
                elif "contradict" in clean_text.lower() or "does not" in clean_text.lower():
                    reason_type = "contradiction"
                elif "confirm" in clean_text.lower() or "support" in clean_text.lower() or "verified" in clean_text.lower():
                    reason_type = "support"

                reasons.append(ReasonResponse(type=reason_type, text=clean_text))

        # Build website details if URL analysis
        website_details = None
        is_url_type = analysis.input_type == "url" or analysis.input_content.strip().startswith(("http://", "https://", "www."))
        if is_url_type:
            raw_url = analysis.input_content.strip()
            norm_url = raw_url if "://" in raw_url else f"https://{raw_url}"
            parsed = urlparse(norm_url)
            domain_name = parsed.hostname or raw_url
            is_https = raw_url.lower().startswith("https://") or parsed.scheme.lower() == "https"

            r_score = analysis.risk_score or 0
            risk_lvl = "LOW" if r_score <= 25 else "MODERATE" if r_score <= 50 else "HIGH" if r_score <= 75 else "CRITICAL"

            collected_signals = []
            for c in analysis.claims:
                for ev in c.evidence:
                    if ev.evidence_text and ev.evidence_text not in collected_signals:
                        collected_signals.append(ev.evidence_text)

            if not collected_signals:
                collected_signals = [r.text for r in reasons]

            website_details = WebsiteDetails(
                domain=domain_name,
                https=is_https,
                page_title=analysis.claims[0].claim_text if analysis.claims else domain_name,
                risk_level=risk_lvl,
                signals=collected_signals,
            )

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
            website_details=website_details,
        )
