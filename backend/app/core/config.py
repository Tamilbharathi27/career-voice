import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Career Voice"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security & JWT
    JWT_SECRET_KEY: str = "career_voice_super_secret_jwt_key_2026_change_in_production"
    JWT_REFRESH_SECRET_KEY: str = "career_voice_super_secret_refresh_jwt_key_2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database (Supabase PostgreSQL)
    DATABASE_URL: str = "postgresql://postgres:Pavi%402107%402010@db.nmxhyfyuzvmatpdszxee.supabase.co:5432/postgres"
    
    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["*"]

    # File Storage
    STORAGE_DIR: str = os.path.join(os.getcwd(), "storage")
    UPLOAD_DIR: str = os.path.join(os.getcwd(), "storage", "audio")
    REPORT_DIR: str = os.path.join(os.getcwd(), "storage", "reports")

    # AI & Speech Configuration
    WHISPER_MODEL_SIZE: str = "base"
    USE_OPENAI_API: bool = False
    OPENAI_API_KEY: str = ""
    USE_GEMINI_API: bool = False
    GEMINI_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Supabase Configuration
    SUPABASE_URL: str = ""
    SUPABASE_PUBLISHABLE_KEY: str = ""
    SUPABASE_SECRET_KEY: str = ""
    SUPABASE_JWKS_URL: str = ""

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="allow"
    )

settings = Settings()

# Ensure storage directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.REPORT_DIR, exist_ok=True)
