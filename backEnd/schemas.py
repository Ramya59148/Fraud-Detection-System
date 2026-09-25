from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class TextInput(BaseModel):
    text: str = Field(..., min_length=1, description="Text content or message to analyze")
    title: Optional[str] = Field(None, description="Optional title or note")


class EmailInput(BaseModel):
    body: str = Field(..., min_length=1, description="Email body content")
    subject: Optional[str] = Field(None, description="Email subject line")
    sender: Optional[str] = Field(None, description="Sender email address")


class UrlInput(BaseModel):
    url: str = Field(..., min_length=1, description="URL or domain string to inspect")


class ScanResponse(BaseModel):
    id: Optional[str] = None
    scan_id: str
    input_type: str
    input_summary: str
    raw_input: Optional[str] = None
    verdict: str  # SAFE, SUSPICIOUS, FRAUDULENT
    confidence: float
    risk_score: float
    explanation: str
    indicators: List[str] = []
    probabilities: Dict[str, float] = {}
    metadata: Dict[str, Any] = {}
    created_at: Optional[str] = None


class HistoryResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[ScanResponse]


class DashboardStatsResponse(BaseModel):
    total_scans: int
    verdicts: Dict[str, int]
    type_counts: Dict[str, int]
    average_confidence: float
    threats_blocked: int
    recent_scans: List[ScanResponse]


class ModelStatusItem(BaseModel):
    name: str
    type: str
    status: str
    device: str
    details: Dict[str, Any] = {}


class SystemStatusResponse(BaseModel):
    status: str
    models: List[ModelStatusItem]
    device: str
