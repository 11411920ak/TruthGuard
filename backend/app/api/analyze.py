"""Analysis API endpoints — POST /api/analyze/*"""

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.schemas.analysis import (
    TextAnalyzeRequest,
    UrlAnalyzeRequest,
    AnalysisStartResponse,
)
from app.models.database import Analysis, get_session_factory
from app.services.analysis_service import run_analysis
from app.config import get_settings

router = APIRouter(prefix="/analyze", tags=["analyze"])


from typing import Optional

async def _create_analysis(
    input_type: str,
    input_content: str,
    image_bytes: Optional[bytes] = None,
) -> AnalysisStartResponse:
    """Create an analysis record and run the pipeline."""
    settings = get_settings()
    session_factory = get_session_factory(settings.database_url)

    async with session_factory() as session:
        analysis = Analysis(
            input_type=input_type,
            input_content=input_content,
            status="processing",
        )
        session.add(analysis)
        await session.commit()
        await session.refresh(analysis)
        analysis_id = analysis.id

    # Run analysis
    await run_analysis(analysis_id, input_type, input_content, image_bytes=image_bytes)

    return AnalysisStartResponse(
        id=analysis_id,
        status="completed",
        message="Analysis completed successfully",
    )


@router.post("/text", response_model=AnalysisStartResponse)
async def analyze_text(request: TextAnalyzeRequest):
    """Analyze a text claim or statement."""
    return await _create_analysis("text", request.content)


@router.post("/url", response_model=AnalysisStartResponse)
async def analyze_url(request: UrlAnalyzeRequest):
    """Analyze a URL/website."""
    return await _create_analysis("url", request.url)


@router.post("/image", response_model=AnalysisStartResponse)
async def analyze_image(file: UploadFile = File(...)):
    """Analyze an uploaded image/screenshot."""
    # Validate file type
    if file.content_type and not (file.content_type.startswith("image/") or file.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp"))):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Validate file size (max 10MB)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be under 10MB")

    return await _create_analysis("image", f"[Screenshot: {file.filename}]", image_bytes=contents)


@router.post("/video", response_model=AnalysisStartResponse)
async def analyze_video(file: UploadFile = File(...)):
    """Analyze an uploaded video."""
    # Validate file type
    if file.content_type and not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")

    # Validate file size (max 100MB)
    contents = await file.read()
    if len(contents) > 100 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be under 100MB")

    # For now, use filename. In later phases: audio extraction → STT → claims
    return await _create_analysis("video", f"[Video: {file.filename}]")
