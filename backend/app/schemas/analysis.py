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


class SourceResponse(BaseModel):
    name: str
    type: Optional[str] = None
    url: Optional[str] = None
    reliability: float = 0.0


class ReasonResponse(BaseModel):
    type: str  # support, contradiction, warning
    text: str


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


class HistoryItemResponse(BaseModel):
    id: str
    input_type: str
    input_content: str
    verdict: str
    confidence: float
    created_at: str


class HistoryResponse(BaseModel):
    analyses: list[HistoryItemResponse] = []
    total: int = 0


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    project: str = "TruthGuard"
