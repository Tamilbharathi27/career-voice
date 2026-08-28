from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class InterviewCreate(BaseModel):
    role: str = Field(..., json_schema_extra={"example": "Full Stack Engineer"})
    difficulty: str = Field("intermediate", json_schema_extra={"example": "intermediate"})
    question_count: int = Field(3, ge=1, le=10)
    interview_type: str = Field("mixed", json_schema_extra={"example": "mixed"})
    tech_stack: Optional[List[str]] = Field(default=[], json_schema_extra={"example": ["MERN Stack", "React.js", "Node.js"]})

class QuestionResponse(BaseModel):
    id: int
    session_id: int
    question_text: str
    question_type: str
    competency: Optional[str] = None
    expected_keywords: Optional[str] = None
    order_index: int
    is_followup: bool = False
    parent_question_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class AnswerCreate(BaseModel):
    transcript: Optional[str] = None
    audio_url: Optional[str] = None
    audio_duration_seconds: Optional[float] = 0.0

class AnswerResponse(BaseModel):
    id: int
    question_id: int
    audio_url: Optional[str] = None
    audio_duration_seconds: float = 0.0
    transcript: Optional[str] = None
    submitted_at: datetime
    evaluation: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

class InterviewSessionDetail(BaseModel):
    id: int
    user_id: int
    role: str
    difficulty: str
    question_count: int
    interview_type: str
    tech_stack: Optional[str] = None
    status: str
    current_question_index: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    questions: List[QuestionResponse] = []
    report: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

class InterviewSessionSummary(BaseModel):
    id: int
    user_id: int
    role: str
    difficulty: str
    question_count: int
    interview_type: str
    tech_stack: Optional[str] = None
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    overall_score: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)
