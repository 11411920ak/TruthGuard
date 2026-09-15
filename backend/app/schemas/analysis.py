"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── Request Schemas ──

class TextAnalyzeRequest(BaseModel):
    content: str = Field(..., min_length=5, max_length=10000, description="Text content to analyze")


class UrlAnalyzeRequest(BaseModel):
    url: str = Field(..., min_length=5, max_length=2000, description="URL to analyze")


# ── Response Schemas ──

class ClaimResponse(BaseModel):
    id: int
    claim_text: str
    claim_type: Optional[str] = None
    verdict: Optional[str] = None
    confidence: Optional[float] = None
    entities: list[str] = []


class SourceResponse(BaseModel):
    name: str
    type: Optional[str] = None
    url: Optional[str] = None
    reliability: float = 0.0


class ReasonResponse(BaseModel):
    type: str  # support, contradiction, warning
    text: str


class WebsiteDetails(BaseModel):
    domain: str
    https: bool = True
    page_title: Optional[str] = None
    risk_level: Optional[str] = None
    signals: list[str] = []


class SocialDetails(BaseModel):
    platform: str
    handles: list[str] = []
    hashtags: list[str] = []
    impersonation_risk: str = "NONE"
    impersonation_flags: list[str] = []
    manipulation_level: str = "LOW"
    manipulation_score: float = 0.0
    manipulation_signals: list[str] = []
    embedded_url: Optional[str] = None


class VideoDetails(BaseModel):
    filename: str
    duration: float = 0.0
    fps: float = 0.0
    resolution: str = "Unknown"
    frame_count: int = 0
    keyframes_sampled: int = 0
    on_screen_text: Optional[str] = None
    sensationalism_level: str = "LOW"
    sensationalism_score: float = 0.0
    sensationalism_signals: list[str] = []
    embedded_url: Optional[str] = None


class AnalysisStartResponse(BaseModel):
    id: str
    status: str
    message: str


class AnalysisResultResponse(BaseModel):
    id: str
    input_type: str
    input_content: str
    verdict: str
    confidence: float
    risk_score: float
    evidence_coverage: float
    created_at: str
    claims: list[ClaimResponse] = []
    reasons: list[ReasonResponse] = []
    sources: list[SourceResponse] = []
    recommendation: str = ""
    website_details: Optional[WebsiteDetails] = None
    ocr_text: Optional[str] = None
    embedded_url: Optional[str] = None
    social_details: Optional[SocialDetails] = None
    video_details: Optional[VideoDetails] = None


class HistoryItemResponse(BaseModel):
    id: str
    input_type: str
    input_content: str
    verdict: str
    confidence: float
    risk_score: float = 0.0
    created_at: str


class DashboardStatsResponse(BaseModel):
    total_scans: int = 0
    verdict_counts: dict[str, int] = {}
    type_counts: dict[str, int] = {}
    avg_confidence: float = 0.0
    avg_risk_score: float = 0.0
    recent_threats: list[str] = []


class HistoryResponse(BaseModel):
    analyses: list[HistoryItemResponse] = []
    total: int = 0


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    project: str = "TruthGuard"
