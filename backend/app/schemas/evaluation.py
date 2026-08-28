from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class EvaluationResponse(BaseModel):
    id: int
    answer_id: int
    nlp_score: float
    voice_score: float
    sentiment_score: float
    star_score: float
    composite_score: float
    pace_wpm: float
    filler_words_count: int
    filler_words_breakdown: Optional[Dict[str, int]] = None
    pause_ratio: float
    clarity_score: float
    feedback_text: Optional[str] = None
    strengths: Optional[List[str]] = None
    improvements: Optional[List[str]] = None
    suggested_answer: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class VoiceAnalysisResult(BaseModel):
    pace_wpm: float
    filler_words_count: int
    filler_words_breakdown: Dict[str, int]
    pause_ratio: float
    pitch_variance: float
    clarity_score: float
    voice_score: float

class NLPAnalysisResult(BaseModel):
    relevance_score: float
    keyword_coverage_score: float
    star_score: float
    completeness_score: float
    overall_nlp_score: float
    matched_keywords: List[str]
    missing_keywords: List[str]
