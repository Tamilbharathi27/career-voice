from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.services.nlp_service import nlp_service
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/nlp", tags=["NLP Analysis"])

class NLPAnalyzeRequest(BaseModel):
    question_text: str
    transcript: str
    expected_keywords: Optional[List[str]] = None

@router.post("/analyze", response_model=Dict[str, Any])
def analyze_text(
    req: NLPAnalyzeRequest,
    current_user: User = Depends(get_current_user)
):
    """Direct endpoint to analyze text for keyword coverage, STAR structure, and relevance."""
    return nlp_service.analyze_answer(
        question_text=req.question_text,
        transcript=req.transcript,
        expected_keywords=req.expected_keywords
    )
