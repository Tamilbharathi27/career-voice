from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum

class InterviewStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class InterviewDifficulty(str, enum.Enum):
    ENTRY = "entry"
    INTERMEDIATE = "intermediate"
    SENIOR = "senior"

class QuestionType(str, enum.Enum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SITUATIONAL = "situational"
    SYSTEM_DESIGN = "system_design"
    FOLLOW_UP = "follow_up"

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(255), nullable=False) # e.g. Frontend Engineer, Full Stack, Data Scientist
    difficulty = Column(String(50), default=InterviewDifficulty.INTERMEDIATE.value, nullable=False)
    question_count = Column(Integer, default=3, nullable=False)
    interview_type = Column(String(50), default="mixed", nullable=False) # technical, behavioral, mixed
    tech_stack = Column(Text, nullable=True) # JSON array or string of technologies selected by candidate
    status = Column(String(50), default=InterviewStatus.PENDING.value, nullable=False)
    current_question_index = Column(Integer, default=0, nullable=False)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="interviews")
    questions = relationship("Question", back_populates="session", cascade="all, delete-orphan", order_by="Question.order_index")
    report = relationship("SessionReport", back_populates="session", uselist=False, cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), default=QuestionType.TECHNICAL.value, nullable=False)
    competency = Column(String(100), nullable=True) # e.g. Problem Solving, Architecture, Communication
    expected_keywords = Column(Text, nullable=True) # JSON list or comma separated
    order_index = Column(Integer, nullable=False)
    is_followup = Column(Boolean, default=False)
    parent_question_id = Column(Integer, ForeignKey("questions.id", ondelete="SET NULL"), nullable=True)

    session = relationship("InterviewSession", back_populates="questions")
    answer = relationship("Answer", back_populates="question", uselist=False, cascade="all, delete-orphan")

class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), unique=True, nullable=False)
    audio_url = Column(String(512), nullable=True)
    audio_duration_seconds = Column(Float, default=0.0)
    transcript = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    question = relationship("Question", back_populates="answer")
    evaluation = relationship("AnswerEvaluation", back_populates="answer", uselist=False, cascade="all, delete-orphan")
