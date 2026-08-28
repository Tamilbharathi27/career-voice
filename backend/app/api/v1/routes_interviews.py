from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import json

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.interview import InterviewSession, Question, Answer, InterviewStatus
from app.models.evaluation import SessionReport, AnswerEvaluation
from app.schemas.interview import InterviewCreate, InterviewSessionDetail, InterviewSessionSummary, QuestionResponse
from app.core.deps import get_current_user
from app.services.agent_interviewer import agent_interviewer
from app.db.init_db import QUESTION_BANK, DOMAIN_CATALOG

router = APIRouter(prefix="/interviews", tags=["Interviews"])

@router.get("/roles", response_model=List[str])
def get_available_roles():
    """Retrieve list of pre-configured interview roles."""
    return list(DOMAIN_CATALOG.keys())

@router.get("/domains", response_model=Dict[str, Any])
def get_available_domains():
    """Retrieve complete catalog of domains and their specific tech stack options."""
    return DOMAIN_CATALOG

@router.post("/sessions", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_interview_session(
    interview_in: InterviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new mock interview session and initialize the dynamic AI interviewer."""
    tech_stack_str = json.dumps(interview_in.tech_stack) if interview_in.tech_stack else None

    session = InterviewSession(
        user_id=current_user.id,
        role=interview_in.role,
        difficulty=interview_in.difficulty,
        question_count=interview_in.question_count,
        interview_type=interview_in.interview_type,
        tech_stack=tech_stack_str,
        status=InterviewStatus.PENDING.value,
        started_at=datetime.now(timezone.utc)
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Initialize the first dynamic question with Agent Interviewer
    first_question = agent_interviewer.initialize_interview(db, session)

    return {
        "session_id": session.id,
        "role": session.role,
        "difficulty": session.difficulty,
        "question_count": session.question_count,
        "tech_stack": json.loads(session.tech_stack) if session.tech_stack else [],
        "status": session.status,
        "current_question": {
            "id": first_question.id,
            "question_text": first_question.question_text,
            "question_type": first_question.question_type,
            "competency": first_question.competency,
            "order_index": first_question.order_index
        }
    }

@router.get("/sessions", response_model=List[Dict[str, Any]])
def get_user_interview_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all past and active interview sessions for current student."""
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id
    ).order_by(InterviewSession.started_at.desc()).all()

    result = []
    for s in sessions:
        score = s.report.overall_score if s.report else None
        ts = []
        if s.tech_stack:
            try:
                ts = json.loads(s.tech_stack)
            except Exception:
                ts = [s.tech_stack]

        result.append({
            "id": s.id,
            "user_id": s.user_id,
            "role": s.role,
            "difficulty": s.difficulty,
            "question_count": s.question_count,
            "interview_type": s.interview_type,
            "tech_stack": ts,
            "status": s.status,
            "started_at": s.started_at,
            "completed_at": s.completed_at,
            "overall_score": score
        })
    return result

@router.get("/sessions/{session_id}", response_model=Dict[str, Any])
def get_session_detail(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve full details of an interview session, questions, answers, and evaluations."""
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview session not found")

    # Access control: user must own session or be a recruiter
    if session.user_id != current_user.id and current_user.role != UserRole.RECRUITER.value and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this session")

    questions_list = []
    for q in session.questions:
        q_dict = {
            "id": q.id,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "competency": q.competency,
            "order_index": q.order_index,
            "is_followup": q.is_followup,
            "answer": None
        }
        if q.answer:
            eval_dict = None
            if q.answer.evaluation:
                ev = q.answer.evaluation
                eval_dict = {
                    "nlp_score": ev.nlp_score,
                    "voice_score": ev.voice_score,
                    "sentiment_score": ev.sentiment_score,
                    "composite_score": ev.composite_score,
                    "pace_wpm": ev.pace_wpm,
                    "filler_words_count": ev.filler_words_count,
                    "filler_words_breakdown": json.loads(ev.filler_words_breakdown) if ev.filler_words_breakdown else {},
                    "pause_ratio": ev.pause_ratio,
                    "clarity_score": ev.clarity_score,
                    "feedback_text": ev.feedback_text,
                    "strengths": json.loads(ev.strengths) if ev.strengths else [],
                    "improvements": json.loads(ev.improvements) if ev.improvements else [],
                    "suggested_answer": ev.suggested_answer
                }
            q_dict["answer"] = {
                "id": q.answer.id,
                "audio_url": q.answer.audio_url,
                "audio_duration_seconds": q.answer.audio_duration_seconds,
                "transcript": q.answer.transcript,
                "submitted_at": q.answer.submitted_at,
                "evaluation": eval_dict
            }
        questions_list.append(q_dict)

    report_dict = None
    if session.report:
        r = session.report
        report_dict = {
            "overall_score": r.overall_score,
            "technical_score": r.technical_score,
            "communication_score": r.communication_score,
            "confidence_score": r.confidence_score,
            "strengths": json.loads(r.strengths) if r.strengths else [],
            "weaknesses": json.loads(r.weaknesses) if r.weaknesses else [],
            "recommendations": json.loads(r.recommendations) if r.recommendations else [],
            "competency_breakdown": json.loads(r.competency_breakdown) if r.competency_breakdown else {},
            "report_url": r.report_url,
            "generated_at": r.generated_at
        }

    ts = []
    if session.tech_stack:
        try:
            ts = json.loads(session.tech_stack)
        except Exception:
            ts = [session.tech_stack]

    return {
        "id": session.id,
        "user_id": session.user_id,
        "candidate_name": session.user.name if session.user else "Candidate",
        "role": session.role,
        "difficulty": session.difficulty,
        "question_count": session.question_count,
        "interview_type": session.interview_type,
        "tech_stack": ts,
        "status": session.status,
        "current_question_index": session.current_question_index,
        "started_at": session.started_at,
        "completed_at": session.completed_at,
        "questions": questions_list,
        "report": report_dict
    }
