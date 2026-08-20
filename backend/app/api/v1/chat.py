"""
AI Resume Chatbot API routes.

POST   /chat/start-session         — create a new chat session
POST   /chat/send-message          — send a message + get AI reply
GET    /chat/history/{session_id}  — full session with messages
GET    /chat/sessions              — list all sessions for user
DELETE /chat/session/{session_id}  — delete session + messages
"""
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.analysis import Analysis
from app.models.chat import ChatMessage, ChatSession
from app.models.resume import Resume
from app.models.user import User
from app.schemas.chat import (
    ChatHistoryResponse,
    ChatMessageRead,
    ChatSessionCreate,
    ChatSessionList,
    ChatSessionRead,
    SendMessageRequest,
    SendMessageResponse,
)
from app.services.chat_service import generate_chat_response

router = APIRouter()
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _get_resume_context(resume: Resume, db: Session) -> dict:
    """Return resume text + latest analysis scores for the AI context."""
    resume_text = resume.raw_text or ""

    # Try fetching latest analysis for scores
    analysis = (
        db.query(Analysis)
        .filter(Analysis.resume_id == resume.id, Analysis.status == "completed")
        .order_by(Analysis.created_at.desc())
        .first()
    )

    # If resume has no text, try S3
    if len(resume_text) < 50 and resume.s3_key:
        try:
            import pathlib, tempfile
            from app.core.config import settings
            local_dir  = pathlib.Path(tempfile.gettempdir()) / "resume_analyzer_uploads"
            local_file = local_dir / f"{resume.id}.{resume.file_type}"
            if local_file.exists():
                from app.services.resume_parser import parse_resume
                parsed = parse_resume(local_file.read_bytes(), resume.file_name)
                resume_text = parsed.raw_text
            elif settings.is_aws_configured:
                from app.aws.s3_client import download_file_from_s3
                from app.services.resume_parser import parse_resume
                file_bytes = download_file_from_s3(resume.s3_key)
                parsed = parse_resume(file_bytes, resume.file_name)
                resume_text = parsed.raw_text
        except Exception as exc:
            logger.warning("Could not load resume text for chat: %s", exc)

    return {
        "resume_text":    resume_text,
        "ats_score":      analysis.ats_score      if analysis else 0,
        "skills_found":   analysis.skills_found   if analysis else [],
        "missing_skills": analysis.missing_skills if analysis else [],
    }


def _session_read(session: ChatSession, db: Session) -> ChatSessionRead:
    count = db.query(func.count(ChatMessage.id)).filter(
        ChatMessage.session_id == session.id
    ).scalar() or 0
    data = ChatSessionRead.model_validate(session)
    data.message_count = count
    return data


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@router.post("/start-session", response_model=ChatSessionRead, status_code=status.HTTP_201_CREATED)
def start_session(
    payload: ChatSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new chat session tied to a specific resume."""
    resume = db.query(Resume).filter(
        Resume.id == payload.resume_id,
        Resume.owner_id == current_user.id,
    ).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    title = payload.title or f"Chat – {resume.file_name[:30]}"
    session = ChatSession(
        user_id=current_user.id,
        resume_id=resume.id,
        title=title,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Inject a welcome message from the assistant
    ctx = _get_resume_context(resume, db)
    welcome = (
        f"Hello! 👋 I've loaded **{resume.file_name}** and I'm ready to help.\n\n"
        + (f"Your current ATS score is **{ctx['ats_score']:.0f}/100**. " if ctx['ats_score'] else "")
        + (f"I detected {len(ctx['skills_found'])} skills on your resume. " if ctx['skills_found'] else "")
        + "\n\nYou can ask me anything about your resume. Try:\n"
        "• *How can I improve my resume?*\n"
        "• *What skills am I missing?*\n"
        "• *Rewrite my professional summary*\n"
        "• *Suggest projects for my skill set*\n"
        "• *Generate interview questions*"
    )
    welcome_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        message=welcome,
    )
    db.add(welcome_msg)
    db.commit()
    db.refresh(session)

    logger.info("Chat session started: %s user=%s resume=%s", session.id, current_user.id, resume.id)
    return _session_read(session, db)


@router.post("/send-message", response_model=SendMessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    payload: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a user message and receive an AI reply."""
    session = db.query(ChatSession).filter(
        ChatSession.id == payload.session_id,
        ChatSession.user_id == current_user.id,
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found.")

    # Save user message first
    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        message=payload.message,
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # Get conversation history (excluding the just-saved message)
    history_rows = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.session_id == session.id,
            ChatMessage.id != user_msg.id,
        )
        .order_by(ChatMessage.created_at)
        .all()
    )
    history = [{"role": m.role, "content": m.message} for m in history_rows]

    # Load resume context
    resume = db.query(Resume).filter(Resume.id == session.resume_id).first()
    ctx    = _get_resume_context(resume, db) if resume else {}

    # Generate AI response
    reply_text = generate_chat_response(
        user_message=payload.message,
        resume_text=ctx.get("resume_text", ""),
        history=history,
        ats_score=ctx.get("ats_score", 0),
        skills_found=ctx.get("skills_found", []),
        missing_skills=ctx.get("missing_skills", []),
    )

    # Save assistant reply
    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        message=reply_text,
    )
    db.add(assistant_msg)

    # Update session timestamp
    session.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user_msg)
    db.refresh(assistant_msg)

    return SendMessageResponse(
        user_message=ChatMessageRead.model_validate(user_msg),
        assistant_message=ChatMessageRead.model_validate(assistant_msg),
    )


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
def get_history(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a session and all its messages."""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id,
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found.")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    return ChatHistoryResponse(
        session=_session_read(session, db),
        messages=[ChatMessageRead.model_validate(m) for m in messages],
    )


@router.get("/sessions", response_model=ChatSessionList)
def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all chat sessions for the current user, newest first."""
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )
    return ChatSessionList(
        items=[_session_read(s, db) for s in sessions],
        total=len(sessions),
    )


@router.delete("/session/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a chat session and all its messages."""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id,
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found.")
    db.delete(session)
    db.commit()
    return None
