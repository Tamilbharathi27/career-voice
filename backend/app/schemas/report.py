from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class SessionReportResponse(BaseModel):
    id: int
    session_id: int
    overall_score: float
    technical_score: float
    communication_score: float
    confidence_score: float
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    competency_breakdown: Optional[Dict[str, float]] = None
    report_url: Optional[str] = None
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FullInterviewReportResponse(BaseModel):
    session_id: int
    candidate_name: str
    candidate_email: str
    role: str
    difficulty: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    overall_score: float
    technical_score: float
    communication_score: float
    confidence_score: float
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    competency_breakdown: Dict[str, float]
    report_url: Optional[str] = None
    questions_detail: List[Dict[str, Any]]
