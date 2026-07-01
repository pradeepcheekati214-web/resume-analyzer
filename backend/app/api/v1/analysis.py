"""
Analysis routes — run, retrieve, list history, delete.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.analysis import Analysis
from app.models.resume import Resume
from app.models.user import User
from app.schemas.analysis import AnalysisCreate, AnalysisHistory, AnalysisListItem, AnalysisRead

router = APIRouter()
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Shared helper — called by both this router and resumes router
# ---------------------------------------------------------------------------
async def _run_analysis(
    resume: Resume,
    owner: User,
    db: Session,
    job_description: str = "",
) -> AnalysisRead:
    """
    Full analysis pipeline:
    1. Create an analysis record (status=processing)
    2. Fetch resume bytes (S3 if configured, else raw_text fallback)
    3. Run parser → skill extractor → ATS scorer → suggestion engine
    4. Persist results to DB (and optionally DynamoDB)
    5. Return AnalysisRead schema
    """
    from app.services.analyzer import analyze_resume as run_analyzer

    analysis = Analysis(
        resume_id=resume.id,
        owner_id=owner.id,
        status="processing",
        job_description=job_description,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    try:
        file_bytes = await _get_resume_bytes(resume)

        analysis_data, raw_text, word_count, page_count = run_analyzer(
            file_bytes=file_bytes,
            filename=resume.file_name,
            job_description=job_description,
        )

        # Update resume with extracted text/metadata
        resume.raw_text   = raw_text
        resume.word_count = word_count
        resume.page_count = page_count
        db.commit()

        # Persist analysis results
        for key, value in analysis_data.items():
            setattr(analysis, key, value)
        db.commit()
        db.refresh(analysis)

        # Optional DynamoDB sync
        if _dynamo_enabled():
            try:
                from app.aws.dynamodb_client import save_analysis_to_dynamo
                save_analysis_to_dynamo(analysis, resume)
            except Exception as exc:
                logger.warning("DynamoDB sync failed (non-fatal): %s", exc)

    except HTTPException as exc:
        analysis.status = "failed"
        analysis.error_message = exc.detail
        db.commit()
        db.refresh(analysis)
        raise  # propagate to frontend so it shows the real message
    except Exception as exc:
        logger.exception("Analysis pipeline error for resume %s: %s", resume.id, exc)
        analysis.status = "failed"
        analysis.error_message = str(exc)
        db.commit()
        db.refresh(analysis)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(exc)}",
        )

    return _to_schema(analysis, resume)


async def _get_resume_bytes(resume: Resume) -> bytes:
    """
    Retrieve file bytes for a resume.
    Priority:
      1. In-memory bytes on the object (same-request upload)
      2. Local temp file on disk (cross-request, no S3)
      3. S3 download (when configured)
      4. Raise HTTP 422
    """
    from app.core.config import settings
    import pathlib, tempfile

    # Case 1: bytes cached in memory from this request
    cached = getattr(resume, "_file_bytes", None)
    if cached:
        return cached

    # Case 2: local temp file written during upload
    local_dir = pathlib.Path(tempfile.gettempdir()) / "resume_analyzer_uploads"
    local_file = local_dir / f"{resume.id}.{resume.file_type}"
    if local_file.exists():
        logger.info("Reading resume bytes from local temp file: %s", local_file)
        return local_file.read_bytes()

    # Case 3: fetch from S3
    if resume.s3_key and settings.is_aws_configured:
        from app.aws.s3_client import download_file_from_s3
        return download_file_from_s3(resume.s3_key)

    # Case 4: nothing available
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Resume file not found. Please re-upload and try again.",
    )


def _dynamo_enabled() -> bool:
    from app.core.config import settings
    return bool(settings.is_aws_configured and settings.DYNAMODB_TABLE_NAME)


def _to_schema(analysis: Analysis, resume: Resume) -> AnalysisRead:
    """Build an AnalysisRead Pydantic model from ORM instances."""
    resume_meta = {
        "file_size":  resume.file_size,
        "file_type":  resume.file_type,
        "word_count": resume.word_count,
        "page_count": resume.page_count,
    }
    return AnalysisRead(
        id=analysis.id,
        resume_id=analysis.resume_id,
        status=analysis.status,
        error_message=analysis.error_message,
        file_name=resume.file_name,
        s3_url=resume.s3_url,
        ats_score=analysis.ats_score,
        score_breakdown=analysis.score_breakdown,
        skills_found=analysis.skills_found,
        missing_skills=analysis.missing_skills,
        keywords_matched=analysis.keywords_matched,
        contact_info=analysis.contact_info,
        resume_metadata=resume_meta,
        suggestions=analysis.suggestions,
        created_at=analysis.created_at,
        updated_at=analysis.updated_at,
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@router.get("/history", response_model=AnalysisHistory)
def get_analysis_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Paginated analysis history for the current user."""
    total = (
        db.query(Analysis)
        .filter(Analysis.owner_id == current_user.id)
        .count()
    )
    rows = (
        db.query(Analysis, Resume.file_name)
        .join(Resume, Analysis.resume_id == Resume.id)
        .filter(Analysis.owner_id == current_user.id)
        .order_by(Analysis.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = [
        AnalysisListItem(
            id=a.id,
            resume_id=a.resume_id,
            file_name=file_name,
            ats_score=a.ats_score,
            status=a.status,
            skills_count=a.skills_count or 0,
            missing_count=a.missing_count or 0,
            created_at=a.created_at,
        )
        for a, file_name in rows
    ]

    return AnalysisHistory(items=items, total=total, page=page, page_size=page_size)


@router.get("/{analysis_id}", response_model=AnalysisRead)
def get_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single analysis result by ID."""
    row = (
        db.query(Analysis, Resume)
        .join(Resume, Analysis.resume_id == Resume.id)
        .filter(
            Analysis.id == analysis_id,
            Analysis.owner_id == current_user.id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")
    analysis, resume = row
    return _to_schema(analysis, resume)


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an analysis record."""
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.owner_id == current_user.id,
    ).first()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")
    db.delete(analysis)
    db.commit()
    return None
