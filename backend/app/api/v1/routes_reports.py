import os
import json
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.interview import InterviewSession, Question
from app.models.evaluation import SessionReport
from app.core.deps import get_current_user, require_recruiter
from app.services.report_service import report_service

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/sessions/{session_id}", response_model=Dict[str, Any])
def get_session_report(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve full structured report for a completed session."""
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview session not found")

    if session.user_id != current_user.id and current_user.role != UserRole.RECRUITER.value and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    report = db.query(SessionReport).filter(SessionReport.session_id == session_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not generated yet for this session")

    # Load question-level evaluations
    questions = db.query(Question).filter(Question.session_id == session_id).order_by(Question.order_index).all()
    questions_data = []
    for q in questions:
        q_item = {
            "id": q.id,
            "question_text": q.question_text,
            "competency": q.competency,
            "order_index": q.order_index,
            "is_followup": q.is_followup,
            "transcript": q.answer.transcript if q.answer else None,
            "audio_url": q.answer.audio_url if q.answer else None,
            "duration": q.answer.audio_duration_seconds if q.answer else 0.0,
            "evaluation": None
        }
        if q.answer and q.answer.evaluation:
            ev = q.answer.evaluation
            q_item["evaluation"] = {
                "composite_score": ev.composite_score,
                "nlp_score": ev.nlp_score,
                "voice_score": ev.voice_score,
                "sentiment_score": ev.sentiment_score,
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
        questions_data.append(q_item)

    candidate_name = session.user.name if session.user else "Candidate"
    candidate_email = session.user.email if session.user else ""

    return {
        "session_id": session.id,
        "candidate_id": session.user_id,
        "candidate_name": candidate_name,
        "candidate_email": candidate_email,
        "role": session.role,
        "difficulty": session.difficulty,
        "status": session.status,
        "started_at": session.started_at,
        "completed_at": session.completed_at,
        "overall_score": report.overall_score,
        "technical_score": report.technical_score,
        "communication_score": report.communication_score,
        "confidence_score": report.confidence_score,
        "strengths": json.loads(report.strengths) if report.strengths else [],
        "weaknesses": json.loads(report.weaknesses) if report.weaknesses else [],
        "recommendations": json.loads(report.recommendations) if report.recommendations else [],
        "competency_breakdown": json.loads(report.competency_breakdown) if report.competency_breakdown else {},
        "report_url": report.report_url,
        "questions_detail": questions_data
    }

@router.get("/sessions/{session_id}/pdf")
def download_pdf_report(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate and stream PDF report download."""
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview session not found")

    if session.user_id != current_user.id and current_user.role != UserRole.RECRUITER.value and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    pdf_path = report_service.generate_pdf_report(db, session_id)
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not generate PDF")

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"CareerVoice_Report_{session_id}.pdf"
    )

@router.get("/recruiter/candidates", response_model=List[Dict[str, Any]])
def get_recruiter_candidate_reports(
    current_user: User = Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    """Recruiter endpoint: Aggregate all candidate sessions and performance summaries."""
    sessions = db.query(InterviewSession).filter(InterviewSession.status == "completed").all()
    results = []

    for s in sessions:
        report = s.report
        results.append({
            "session_id": s.id,
            "candidate_id": s.user_id,
            "candidate_name": s.user.name if s.user else "Candidate",
            "candidate_email": s.user.email if s.user else "",
            "role": s.role,
            "difficulty": s.difficulty,
            "completed_at": s.completed_at,
            "overall_score": report.overall_score if report else 0.0,
            "technical_score": report.technical_score if report else 0.0,
            "communication_score": report.communication_score if report else 0.0,
            "confidence_score": report.confidence_score if report else 0.0,
            "questions_count": len(s.questions)
        })

    return results
