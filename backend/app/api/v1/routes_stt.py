import os
import uuid
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status

from app.core.config import settings
from app.services.stt_service import stt_service
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/stt", tags=["Speech-To-Text"])

@router.post("/transcribe", response_model=Dict[str, Any])
async def transcribe_audio(
    audio: UploadFile = File(...),
    fallback_text: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """Direct STT transcription endpoint for testing and live speech conversion."""
    temp_filename = f"stt_temp_{uuid.uuid4().hex[:8]}.webm"
    temp_filepath = os.path.join(settings.UPLOAD_DIR, temp_filename)

    try:
        content = await audio.read()
        with open(temp_filepath, "wb") as f:
            f.write(content)

        result = stt_service.transcribe_audio(temp_filepath, fallback_transcript=fallback_text)
        return result
    finally:
        if os.path.exists(temp_filepath):
            try:
                os.remove(temp_filepath)
            except Exception:
                pass
