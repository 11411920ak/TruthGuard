"""History API endpoint — GET /api/history"""

from fastapi import APIRouter

from app.schemas.analysis import HistoryResponse, HistoryItemResponse
from app.models.database import Analysis, get_session_factory
from app.config import get_settings
from sqlalchemy import select

router = APIRouter(tags=["history"])


@router.get("/history", response_model=HistoryResponse)
async def get_history():
    """Retrieve all past analyses (most recent first)."""
    settings = get_settings()
    session_factory = get_session_factory(settings.database_url)

    async with session_factory() as session:
        stmt = (
            select(Analysis)
            .where(Analysis.status == "completed")
            .order_by(Analysis.created_at.desc())
            .limit(50)
        )
        result = await session.execute(stmt)
        analyses = result.scalars().all()

        items = [
            HistoryItemResponse(
                id=a.id,
                input_type=a.input_type,
                input_content=a.input_content[:200],  # Truncate for list view
                verdict=a.verdict or "UNVERIFIED",
                confidence=a.confidence or 0,
                created_at=a.created_at.isoformat() if a.created_at else "",
            )
            for a in analyses
        ]

        return HistoryResponse(analyses=items, total=len(items))
