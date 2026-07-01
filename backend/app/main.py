"""
Resume Analyzer — FastAPI application entry point.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import router as api_v1_router

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup; clean up on shutdown."""
    logger.info("Starting up Resume Analyzer API…")
    await init_db()
    yield
    logger.info("Shutting down Resume Analyzer API.")


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------
def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "AI-powered Resume Analyzer API. "
            "Upload resumes, get ATS scores, skills analysis, and improvement suggestions."
        ),
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # ── Middleware ──────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if settings.APP_ENV == "production":
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*.amazonaws.com", "localhost"])

    # ── Exception handlers ──────────────────────────────────────────────────
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = []
        for e in exc.errors():
            # loc can contain strings and ints (e.g. ("body", 0, "field"))
            loc_parts = [str(part) for part in e.get("loc", [])]
            # Skip internal FastAPI loc parts like "body" at index 0
            field = ".".join(loc_parts[1:]) if len(loc_parts) > 1 else ".".join(loc_parts)
            errors.append({"field": field or "body", "message": e["msg"]})
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": errors[0]["message"] if len(errors) == 1 else "Validation error", "errors": errors},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        import traceback
        tb = traceback.format_exc()
        logger.exception("Unhandled exception: %s", exc)
        # Show full error in development to aid debugging
        if settings.DEBUG:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": str(exc), "traceback": tb},
            )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An internal server error occurred."},
        )

    # ── Routers ─────────────────────────────────────────────────────────────
    app.include_router(api_v1_router, prefix="/api/v1")

    # ── Health check ────────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "ok", "version": settings.APP_VERSION}

    return app


app = create_app()
