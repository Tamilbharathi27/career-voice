import os
import logging
import re
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class STTService:
    """Speech-to-Text Transcription Service supporting local Whisper and resilient fallbacks."""

    def __init__(self):
        self.model = None
        self._model_loaded = False

    def load_local_model(self):
        """Lazy load local Whisper model if available."""
        if self._model_loaded:
            return
        try:
            import whisper
            logger.info(f"Loading local Whisper model '{settings.WHISPER_MODEL_SIZE}'...")
            self.model = whisper.load_model(settings.WHISPER_MODEL_SIZE)
            self._model_loaded = True
            logger.info("Local Whisper model loaded successfully.")
        except Exception as e:
            logger.warning(f"Local whisper package not loaded or failed: {e}. Fallback transcription will be used if needed.")
            self._model_loaded = False

    def transcribe_audio(self, audio_file_path: str, fallback_transcript: Optional[str] = None) -> Dict[str, Any]:
        """Transcribe an audio file into text with duration and confidence metadata."""
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        # If browser explicitly provided live transcribed text
        if fallback_transcript is not None:
            clean_text = fallback_transcript.strip()
            if len(clean_text) > 0:
                return {
                    "transcript": clean_text,
                    "language": "en",
                    "engine": "browser_live_stt",
                    "confidence": 0.95
                }
            else:
                # User sent an explicit empty transcript (e.g. didn't speak into live STT)
                return {
                    "transcript": "",
                    "language": "en",
                    "engine": "empty_input",
                    "confidence": 0.0
                }

        # Try OpenAI Whisper API if configured
        if settings.USE_OPENAI_API and settings.OPENAI_API_KEY:
            try:
                import openai
                client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                with open(audio_file_path, "rb") as audio_file:
                    res = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="en"
                    )
                return {
                    "transcript": res.text.strip(),
                    "language": "en",
                    "engine": "openai_whisper",
                    "confidence": 0.98
                }
            except Exception as e:
                logger.warning(f"OpenAI Whisper API call failed: {e}. Trying local...")

        # Try local Whisper model
        try:
            self.load_local_model()
            if self.model is not None:
                result = self.model.transcribe(audio_file_path)
                return {
                    "transcript": result.get("text", "").strip(),
                    "language": result.get("language", "en"),
                    "engine": "local_whisper",
                    "confidence": 0.92
                }
        except Exception as e:
            logger.warning(f"Local Whisper transcription failed: {e}")

        # Fallback when Whisper model is not loaded and no live transcript was captured
        file_size = os.path.getsize(audio_file_path) if os.path.exists(audio_file_path) else 0
        logger.info(f"STT fallback processing audio file of size {file_size} bytes.")
        return {
            "transcript": "",
            "language": "en",
            "engine": "empty_transcript",
            "confidence": 0.0
        }

stt_service = STTService()
