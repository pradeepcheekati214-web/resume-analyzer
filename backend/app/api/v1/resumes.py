"""
Resume upload and management routes.
"""
import logging
import os
import tempfile
import pathlib

from fastapi import APIRouter, Body, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.resume import Resume
from app.models.user import User
from app.schemas.resume import ResumeList, ResumeRead

router = APIRouter()
logger = logging.getLogger(__name__)

# Local temp storage directory — used when S3 is not configured
_LOCAL_UPLOAD_DIR = pathlib.Path(tempfile.gettempdir()) / "resume_analyzer_uploads"
_LOCAL_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _local_path(resume_id: str, ext: str) -> pathlib.Path:
    return _LOCAL_UPLOAD_DIR / f"{resume_id}.{ext}"


def _validate_file(file: UploadFile) -> None:
    """Validate only by file extension — MIME types vary by OS and browser."""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '{ext}'. Please upload a PDF or DOCX file.",
        )


@router.post("/upload", response_model=ResumeRead, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a resume file (PDF or DOCX)."""
    _validate_file(file)

    file_bytes = await file.read()
    if len(file_bytes) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB} MB.",
        )

    ext = os.path.splitext(file.filename or "file")[1].lower().lstrip(".")

    # Try S3 first; fall back to local disk
    s3_key = None
    s3_url = None
    if settings.is_aws_configured:
        try:
            from app.aws.s3_client import upload_file_to_s3
            s3_key, s3_url = upload_file_to_s3(
                file_bytes=file_bytes,
                filename=file.filename,
                user_id=current_user.id,
                content_type=file.content_type or "application/octet-stream",
            )
        except Exception as exc:
            logger.warning("S3 upload failed, saving locally: %s", exc)

    # Create the DB record first so we have the ID
    resume = Resume(
        owner_id=current_user.id,
        file_name=file.filename,
        file_type=ext,
        file_size=len(file_bytes),
        s3_key=s3_key,
        s3_url=s3_url,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    # Always save to local disk so the analyze endpoint can read it
    # (cheap and safe — cleaned up after analysis or on restart)
    local_file = _local_path(resume.id, ext)
    local_file.write_bytes(file_bytes)
    logger.info("Resume saved locally: %s", local_file)

    logger.info("Resume uploaded: id=%s user=%s", resume.id, current_user.id)
    return resume


@router.get("/", response_model=ResumeList)
def list_resumes(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all resumes for the current user (paginated)."""
    total = db.query(Resume).filter(Resume.owner_id == current_user.id).count()
    resumes = (
        db.query(Resume)
        .filter(Resume.owner_id == current_user.id)
        .order_by(Resume.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return ResumeList(items=resumes, total=total, page=page, page_size=page_size)


@router.get("/{resume_id}", response_model=ResumeRead)
def get_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific resume by ID."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id, Resume.owner_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")
    return resume


@router.post("/{resume_id}/analyze")
async def analyze_resume_endpoint(
    resume_id: str,
    payload: dict = Body(default={}),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Trigger full analysis for an uploaded resume."""
    from app.api.v1.analysis import _run_analysis

    resume = db.query(Resume).filter(
        Resume.id == resume_id, Resume.owner_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")

    job_description = (payload or {}).get("job_description", "")
    return await _run_analysis(resume, current_user, db, job_description)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a resume and its analyses."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id, Resume.owner_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")

    # Clean up S3
    if resume.s3_key and settings.is_aws_configured:
        try:
            from app.aws.s3_client import delete_file_from_s3
            delete_file_from_s3(resume.s3_key)
        except Exception as exc:
            logger.warning("S3 delete failed: %s", exc)

    # Clean up local temp file
    local_file = _local_path(resume.id, resume.file_type)
    if local_file.exists():
        local_file.unlink()

    db.delete(resume)
    db.commit()
    return None
