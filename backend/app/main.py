import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.session import engine, SessionLocal
from app.db.init_db import init_db
from app.api.v1 import (
    routes_auth,
    routes_users,
    routes_interviews,
    routes_voice,
    routes_stt,
    routes_nlp,
    routes_scoring,
    routes_feedback,
    routes_reports
)

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("careervoice")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("Initializing Career Voice Database and Seeding initial assets...")
    db = SessionLocal()
    try:
        init_db(db)
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
    finally:
        db.close()
    yield
    logger.info("Career Voice API shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Career Voice — Agentic AI Voice Interview Platform API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"/docs",
    redoc_url=f"/redoc",
    lifespan=lifespan
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"],
    allow_origin_regex=r"https://.*\.vercel\.app",  # Allow all Vercel deployments and preview URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 Routers
app.include_router(routes_auth.router, prefix=settings.API_V1_STR)
app.include_router(routes_users.router, prefix=settings.API_V1_STR)
app.include_router(routes_interviews.router, prefix=settings.API_V1_STR)
app.include_router(routes_voice.router, prefix=settings.API_V1_STR)
app.include_router(routes_stt.router, prefix=settings.API_V1_STR)
app.include_router(routes_nlp.router, prefix=settings.API_V1_STR)
app.include_router(routes_scoring.router, prefix=settings.API_V1_STR)
app.include_router(routes_feedback.router, prefix=settings.API_V1_STR)
app.include_router(routes_reports.router, prefix=settings.API_V1_STR)

# Mount Static Storage
app.mount("/storage", StaticFiles(directory=settings.STORAGE_DIR), name="storage")

@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint for container orchestrators and monitoring."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.get("/", tags=["System"])
def root():
    """Root redirect to API documentation."""
    return {
        "message": "Welcome to Career Voice API. Visit /docs for OpenAPI documentation.",
        "version": settings.VERSION,
        "health": "/health"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unexpected backend errors."""
    logger.error(f"Unhandled server error on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please check server logs."}
    )
