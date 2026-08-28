import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.nlp_service import nlp_service
from app.services.voice_analysis_service import voice_analysis_service
from app.services.scoring_service import scoring_service

client = TestClient(app)

def test_nlp_answer_analysis():
    question = "How do you optimize React applications for high performance?"
    transcript = "In my last project, we were working on an analytics dashboard. I was tasked with reducing re-renders. I implemented React.memo and useCallback, and virtualized long lists. As a result, frame rate improved by 50%."
    keywords = ["React", "memo", "useCallback", "virtualized"]
    
    result = nlp_service.analyze_answer(question, transcript, keywords)
    assert result["overall_nlp_score"] > 70.0
    assert result["star_score"] >= 75.0
    assert len(result["matched_keywords"]) >= 3

def test_filler_word_detection():
    transcript = "Um, so yeah, I think basically we like used Redis for caching, you know?"
    breakdown, count = voice_analysis_service._detect_filler_words(transcript)
    assert count >= 4
    assert "um" in breakdown
    assert "like" in breakdown

def test_composite_scoring():
    score = scoring_service.calculate_answer_score(
        nlp_score=85.0,
        voice_score=90.0,
        sentiment_score=80.0,
        star_score=95.0
    )
    assert 80.0 <= score <= 92.0
