import os
import uuid
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.models.interview import InterviewSession, Question
from app.core.deps import get_current_user
from app.services.agent_interviewer import agent_interviewer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["Voice Processing"])

@router.post("/submit-answer", response_model=Dict[str, Any])
async def submit_voice_answer(
    session_id: int = Form(...),
    question_id: int = Form(...),
    duration_seconds: float = Form(0.0),
    live_transcript: Optional[str] = Form(None),
    audio: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload candidate's spoken audio response for the active question.
    Triggers the multi-modal AI pipeline (STT -> Voice Analysis -> NLP -> Scoring -> Dynamic Next Question).
    """
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview session not found")

    if session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to submit to this session")

    # Generate unique audio filename
    file_ext = os.path.splitext(audio.filename)[1] if audio.filename else ".webm"
    if not file_ext or file_ext not in [".webm", ".wav", ".mp3", ".ogg", ".m4a"]:
        file_ext = ".webm"

    saved_filename = f"audio_{session_id}_{question_id}_{uuid.uuid4().hex[:8]}{file_ext}"
    saved_filepath = os.path.join(settings.UPLOAD_DIR, saved_filename)

    # Save audio file to disk
    try:
        content = await audio.read()
        with open(saved_filepath, "wb") as f:
            f.write(content)
    except Exception as e:
        logger.error(f"Failed to write audio file: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save audio file")

    # Relative URL for client retrieval
    audio_url = f"/api/v1/voice/audio/{saved_filename}"

    # Execute Agent Interviewer evaluation & advance state
    try:
        result = agent_interviewer.process_answer_and_advance(
            db=db,
            session_id=session_id,
            question_id=question_id,
            audio_file_path=saved_filepath,
            audio_duration_seconds=duration_seconds,
            provided_transcript=live_transcript
        )
        result["audio_url"] = audio_url
        return result
    except Exception as e:
        logger.error(f"Error during voice evaluation pipeline: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"AI evaluation failed: {str(e)}")

@router.get("/audio/{filename}")
def get_audio_file(filename: str):
    """Retrieve audio recording stream."""
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio recording file not found")

    media_type = "audio/webm"
    if safe_filename.endswith(".wav"):
        media_type = "audio/wav"
    elif safe_filename.endswith(".mp3"):
        media_type = "audio/mpeg"

    return FileResponse(path=file_path, media_type=media_type, filename=safe_filename)
