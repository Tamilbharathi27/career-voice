from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.services.scoring_service import scoring_service
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/scoring", tags=["ML Scoring"])

class ScoreCalculateRequest(BaseModel):
    nlp_score: float
    voice_score: float
    sentiment_score: float
    star_score: float

class SessionScoreRequest(BaseModel):
    evaluations: List[Dict[str, Any]]
    questions: List[Dict[str, Any]]

@router.post("/calculate-answer", response_model=Dict[str, float])
def calculate_answer_score(
    req: ScoreCalculateRequest,
    current_user: User = Depends(get_current_user)
):
    """Calculate composite score for a single answer."""
    composite = scoring_service.calculate_answer_score(
        nlp_score=req.nlp_score,
        voice_score=req.voice_score,
        sentiment_score=req.sentiment_score,
        star_score=req.star_score
    )
    return {"composite_score": composite}

@router.post("/calculate-session", response_model=Dict[str, Any])
def calculate_session_score(
    req: SessionScoreRequest,
    current_user: User = Depends(get_current_user)
):
    """Calculate aggregate scores across an entire interview session."""
    return scoring_service.calculate_session_summary(
        answer_evaluations=req.evaluations,
        questions=req.questions
    )
