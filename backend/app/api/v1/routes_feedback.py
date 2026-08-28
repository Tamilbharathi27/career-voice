from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.services.feedback_service import feedback_service
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/feedback", tags=["Feedback Generation"])

class FeedbackRequest(BaseModel):
    question_text: str
    transcript: str
    nlp_results: Dict[str, Any]
    voice_results: Dict[str, Any]
    composite_score: float

@router.post("/generate-answer-feedback", response_model=Dict[str, Any])
def generate_feedback(
    req: FeedbackRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate constructive strengths, weaknesses, and model response for an answer."""
    return feedback_service.generate_answer_feedback(
        question_text=req.question_text,
        transcript=req.transcript,
        nlp_res=req.nlp_results,
        voice_res=req.voice_results,
        composite_score=req.composite_score
    )
