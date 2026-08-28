from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.session import Base

class AnswerEvaluation(Base):
    __tablename__ = "answer_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    answer_id = Column(Integer, ForeignKey("answers.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Quantitative Scores (0-100)
    nlp_score = Column(Float, default=0.0)             # Relevance, technical accuracy, keywords
    voice_score = Column(Float, default=0.0)           # Pace, pitch, pauses, clarity
    sentiment_score = Column(Float, default=0.0)       # Confidence, tone
    star_score = Column(Float, default=0.0)            # STAR structural adherence
    composite_score = Column(Float, default=0.0)       # Weighted total score

    # Acoustic and speech metrics
    pace_wpm = Column(Float, default=0.0)              # Words per minute
    filler_words_count = Column(Integer, default=0)
    filler_words_breakdown = Column(Text, nullable=True) # JSON e.g. {"um": 2, "like": 1}
    pause_ratio = Column(Float, default=0.0)           # Ratio of silent pauses to speaking time
    clarity_score = Column(Float, default=0.0)

    # Qualitative Feedback
    feedback_text = Column(Text, nullable=True)
    strengths = Column(Text, nullable=True)            # JSON list
    improvements = Column(Text, nullable=True)         # JSON list
    suggested_answer = Column(Text, nullable=True)     # Ideal model response

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    answer = relationship("Answer", back_populates="evaluation")

class SessionReport(Base):
    __tablename__ = "session_reports"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id", ondelete="CASCADE"), unique=True, nullable=False)

    overall_score = Column(Float, default=0.0)
    technical_score = Column(Float, default=0.0)
    communication_score = Column(Float, default=0.0)
    confidence_score = Column(Float, default=0.0)

    strengths = Column(Text, nullable=True)             # JSON list
    weaknesses = Column(Text, nullable=True)            # JSON list
    recommendations = Column(Text, nullable=True)       # JSON list
    competency_breakdown = Column(Text, nullable=True)  # JSON dictionary of competency scores
    
    report_url = Column(String(512), nullable=True)     # Path to generated PDF file
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("InterviewSession", back_populates="report")
