"""
Supabase Client Module for Career Voice Backend
"""
import logging
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger(__name__)

supabase_client: Client = None

def get_supabase_client() -> Client:
    global supabase_client
    if supabase_client is None:
        url = settings.SUPABASE_URL
        key = settings.SUPABASE_SECRET_KEY or settings.SUPABASE_PUBLISHABLE_KEY
        if not url or not key:
            logger.warning("Supabase URL or Key is missing in environment variables.")
            return None
        try:
            supabase_client = create_client(url, key)
            logger.info("Connected to Supabase Client successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            return None
    return supabase_client
