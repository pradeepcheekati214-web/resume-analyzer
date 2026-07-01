"""
AI feature routes:
  POST /ai/resume-suggestions          — generate / regenerate AI resume suggestions
  GET  /ai/resume-suggestions/{id}     — get saved suggestions
  POST /ai/job-match                   — analyze resume vs job description
  GET  /ai/job-match/history           — list past job match analyses
  GET  /ai/job-match/{id}              — get a specific job match
  POST /ai/interview/questions         — generate interview question set
  GET  /ai/interview/questions/{id}    — get a question set
  POST /ai/interview/start             — start a mock interview session
  GET  /ai/interview/{id}/next         — get next question
  POST /ai/interview/answer            — submit + evaluate an answer
  POST /ai/interview/{id}/finish       — complete interview & generate result
  GET  /ai/interview/{id}/result       — get final result
  GET  /ai/interview/history           — list past mock interviews
  DELETE /ai/interview/{id}            — delete a mock interview
"""
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.ai_suggestion import AIResumeSuggestion
from app.models.analysis import Analysis
from app.models.interview import InterviewHistory, InterviewQuestionSet, MockAnswer, MockInterview
from app.models.job_match import JobMatch
from app.models.resume import Resume
from app.models.user import User
from app.schemas.ai_suggestion import AISuggestionCreate, AISuggestionRead
from app.schemas.interview import (
    AnswerEvaluation,
    AnswerSubmit,
    InterviewHistoryItem,
    InterviewHistoryList,
    InterviewResult,
    MockInterviewCreate,
    MockInterviewRead,
    NextQuestionResponse,
    QuestionSetCreate,
    QuestionSetRead,
)
from app.schemas.job_match import JobMatchCreate, JobMatchList, JobMatchListItem, JobMatchRead

router = APIRouter()
logger = logging.getLogger(__name__)


# ============================================================================
# FEATURE 1 — AI Resume Suggestions
# ============================================================================

@router.post("/resume-suggestions", response_model=AISuggestionRead, status_code=status.HTTP_201_CREATED)
def create_resume_suggestions(
    payload: AISuggestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate (or regenerate) AI improvement suggestions for a completed analysis."""
    analysis = db.query(Analysis).filter(
        Analysis.id == payload.analysis_id,
        Analysis.owner_id == current_user.id,
    ).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    if analysis.status != "completed":
        raise HTTPException(status_code=400, detail="Analysis is not completed yet.")

    # If regenerating, update existing record; otherwise create new
    existing = db.query(AIResumeSuggestion).filter(
        AIResumeSuggestion.analysis_id == payload.analysis_id,
        AIResumeSuggestion.owner_id == current_user.id,
    ).first()

    if existing and not payload.regenerate:
        return existing

    # Get resume text
    resume = db.query(Resume).filter(Resume.id == analysis.resume_id).first()
    resume_text = (resume.raw_text or "") if resume else ""

    # Call AI service
    from app.services.ai_suggestion_engine import generate_resume_suggestions
    from app.core.config import settings

    provider = settings.AI_PROVIDER

    if existing and payload.regenerate:
        suggestion = existing
        suggestion.generation_count += 1
        suggestion.status = "pending"
        db.commit()
    else:
        suggestion = AIResumeSuggestion(
            owner_id=current_user.id,
            analysis_id=analysis.id,
            provider=provider,
            status="pending",
        )
        db.add(suggestion)
        db.commit()
        db.refresh(suggestion)

    try:
        data = generate_resume_suggestions(
            resume_text=resume_text,
            skills_found=analysis.skills_found or [],
            missing_skills=analysis.missing_skills or [],
            ats_score=analysis.ats_score or 0,
            job_description=analysis.job_description or "",
        )
        meta = data.pop("_meta", {})
        suggestion.professional_summary   = data.get("professional_summary")
        suggestion.experience_bullets     = data.get("experience_bullets")
        suggestion.keyword_improvements   = data.get("keyword_improvements")
        suggestion.grammar_corrections    = data.get("grammar_corrections")
        suggestion.skills_section         = data.get("skills_section")
        suggestion.missing_skills         = data.get("missing_skills")
        suggestion.formatting_suggestions = data.get("formatting_suggestions")
        suggestion.industry_recommendations = data.get("industry_recommendations")
        suggestion.model              = meta.get("model", provider)
        suggestion.prompt_tokens      = meta.get("prompt_tokens", 0)
        suggestion.completion_tokens  = meta.get("completion_tokens", 0)
        suggestion.status             = "completed"
    except Exception as exc:
        logger.exception("AI suggestion generation failed: %s", exc)
        suggestion.status = "failed"
        suggestion.error_message = str(exc)

    db.commit()
    db.refresh(suggestion)
    return suggestion


@router.get("/resume-suggestions/{suggestion_id}", response_model=AISuggestionRead)
def get_resume_suggestions(
    suggestion_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    s = db.query(AIResumeSuggestion).filter(
        AIResumeSuggestion.id == suggestion_id,
        AIResumeSuggestion.owner_id == current_user.id,
    ).first()
    if not s:
        raise HTTPException(status_code=404, detail="Suggestions not found.")
    return s


@router.get("/resume-suggestions/by-analysis/{analysis_id}", response_model=AISuggestionRead)
def get_suggestions_by_analysis(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    s = db.query(AIResumeSuggestion).filter(
        AIResumeSuggestion.analysis_id == analysis_id,
        AIResumeSuggestion.owner_id == current_user.id,
    ).order_by(AIResumeSuggestion.created_at.desc()).first()
    if not s:
        raise HTTPException(status_code=404, detail="No suggestions found for this analysis.")
    return s


# ============================================================================
# FEATURE 2 — Job Match Analyzer
# ============================================================================

@router.post("/job-match", response_model=JobMatchRead, status_code=status.HTTP_201_CREATED)
def create_job_match(
    payload: JobMatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Compare a resume against a job description."""
    resume = db.query(Resume).filter(
        Resume.id == payload.resume_id,
        Resume.owner_id == current_user.id,
    ).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    match = JobMatch(
        owner_id=current_user.id,
        resume_id=resume.id,
        job_title=payload.job_title,
        company_name=payload.company_name,
        job_description=payload.job_description,
        status="processing",
    )
    db.add(match)
    db.commit()
    db.refresh(match)

    try:
        from app.services.job_match_engine import analyze_job_match
        from app.services.skill_extractor import extract_skills
        import pathlib, tempfile

        # Get resume text — try raw_text first, then local temp file
        resume_text = resume.raw_text or ""
        if len(resume_text) < 50:
            local_dir  = pathlib.Path(tempfile.gettempdir()) / "resume_analyzer_uploads"
            local_file = local_dir / f"{resume.id}.{resume.file_type}"
            if local_file.exists():
                from app.services.resume_parser import parse_resume
                parsed = parse_resume(local_file.read_bytes(), resume.file_name)
                resume_text = parsed.raw_text
                # Persist so next call is instant
                resume.raw_text   = parsed.raw_text
                resume.word_count = parsed.word_count
                resume.page_count = parsed.page_count
                db.commit()

        if not resume_text.strip():
            raise ValueError(
                "Resume text is empty. Please re-upload your resume and run "
                "an ATS analysis first so the text can be extracted."
            )

        resume_skills = extract_skills(resume_text)
        data = analyze_job_match(
            resume_text=resume_text,
            job_description=payload.job_description,
            resume_skills=resume_skills,
        )
        match.overall_match      = float(data.get("overall_match", 0))
        match.skills_match       = float(data.get("skills_match", 0))
        match.experience_match   = float(data.get("experience_match", 0))
        match.education_match    = float(data.get("education_match", 0))
        match.keyword_match      = float(data.get("keyword_match", 0))
        match.ats_compatibility  = float(data.get("ats_compatibility", 0))
        match.matching_skills    = data.get("matching_skills")
        match.missing_skills     = data.get("missing_skills")
        match.missing_keywords   = data.get("missing_keywords")
        match.skill_gap_analysis = data.get("skill_gap_analysis")
        match.experience_gap     = data.get("experience_gap")
        match.education_analysis = data.get("education_analysis")
        match.recommendations    = data.get("recommendations")
        match.status             = "completed"
    except Exception as exc:
        logger.exception("Job match failed: %s", exc)
        match.status = "failed"
        match.error_message = str(exc)

    db.commit()
    db.refresh(match)
    return match


@router.get("/job-match/history", response_model=JobMatchList)
def list_job_matches(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total = db.query(JobMatch).filter(JobMatch.owner_id == current_user.id).count()
    items = (
        db.query(JobMatch)
        .filter(JobMatch.owner_id == current_user.id)
        .order_by(JobMatch.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return JobMatchList(items=items, total=total, page=page, page_size=page_size)


@router.get("/job-match/{match_id}", response_model=JobMatchRead)
def get_job_match(
    match_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    match = db.query(JobMatch).filter(
        JobMatch.id == match_id,
        JobMatch.owner_id == current_user.id,
    ).first()
    if not match:
        raise HTTPException(status_code=404, detail="Job match not found.")
    return match


@router.delete("/job-match/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_match(
    match_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    match = db.query(JobMatch).filter(
        JobMatch.id == match_id,
        JobMatch.owner_id == current_user.id,
    ).first()
    if not match:
        raise HTTPException(status_code=404, detail="Job match not found.")
    db.delete(match)
    db.commit()
    return None


# ============================================================================
# FEATURE 3 — Interview Question Generator
# ============================================================================

@router.post("/interview/questions", response_model=QuestionSetRead, status_code=status.HTTP_201_CREATED)
def generate_questions(
    payload: QuestionSetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a tailored interview question set from a resume."""
    resume = db.query(Resume).filter(
        Resume.id == payload.resume_id,
        Resume.owner_id == current_user.id,
    ).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    qs = InterviewQuestionSet(
        owner_id=current_user.id,
        resume_id=resume.id,
        job_title=payload.job_title,
        company_name=payload.company_name,
        job_description=payload.job_description,
        status="processing",
    )
    db.add(qs)
    db.commit()
    db.refresh(qs)

    try:
        from app.services.interview_engine import generate_interview_questions
        from app.services.skill_extractor import extract_skills
        import pathlib, tempfile

        # Get resume text — try DB first, then local temp file
        resume_text = resume.raw_text or ""
        if len(resume_text) < 50:
            local_dir  = pathlib.Path(tempfile.gettempdir()) / "resume_analyzer_uploads"
            local_file = local_dir / f"{resume.id}.{resume.file_type}"
            if local_file.exists():
                from app.services.resume_parser import parse_resume
                parsed = parse_resume(local_file.read_bytes(), resume.file_name)
                resume_text = parsed.raw_text
                resume.raw_text   = parsed.raw_text
                resume.word_count = parsed.word_count
                resume.page_count = parsed.page_count
                db.commit()

        if not resume_text.strip():
            raise ValueError(
                "Resume text is empty. Please re-upload and run an ATS analysis first, "
                "then try generating questions again."
            )

        skills = extract_skills(resume_text)
        data = generate_interview_questions(
            resume_text=resume_text,
            job_title=payload.job_title or "",
            job_description=payload.job_description or "",
            skills=skills,
            company=payload.company_name or "",
        )
        qs.technical_questions  = data.get("technical_questions",  [])
        qs.behavioral_questions = data.get("behavioral_questions",  [])
        qs.hr_questions         = data.get("hr_questions",          [])
        qs.project_questions    = data.get("project_questions",     [])
        qs.aws_questions        = data.get("aws_questions",         [])
        qs.python_questions     = data.get("python_questions",      [])
        qs.react_questions      = data.get("react_questions",       [])
        qs.database_questions   = data.get("database_questions",    [])

        actual_total = sum(
            len(data.get(k) or [])
            for k in [
                "technical_questions", "behavioral_questions", "hr_questions",
                "project_questions",   "aws_questions",        "python_questions",
                "react_questions",     "database_questions",
            ]
        )
        qs.total_questions = actual_total
        qs.status          = "completed"
    except Exception as exc:
        logger.exception("Question generation failed: %s", exc)
        qs.status = "failed"
        qs.error_message = str(exc)

    db.commit()
    db.refresh(qs)
    return qs


@router.get("/interview/questions/{qs_id}", response_model=QuestionSetRead)
def get_question_set(
    qs_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    qs = db.query(InterviewQuestionSet).filter(
        InterviewQuestionSet.id == qs_id,
        InterviewQuestionSet.owner_id == current_user.id,
    ).first()
    if not qs:
        raise HTTPException(status_code=404, detail="Question set not found.")
    return qs


# ============================================================================
# FEATURE 4 — Mock Interview
# ============================================================================

@router.post("/interview/start", response_model=MockInterviewRead, status_code=status.HTTP_201_CREATED)
def start_mock_interview(
    payload: MockInterviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start a new mock interview session from a question set."""
    qs = db.query(InterviewQuestionSet).filter(
        InterviewQuestionSet.id == payload.question_set_id,
        InterviewQuestionSet.owner_id == current_user.id,
    ).first()
    if not qs:
        raise HTTPException(status_code=404, detail="Question set not found.")
    if qs.status != "completed":
        raise HTTPException(status_code=400, detail="Question set is not ready yet.")

    interview = MockInterview(
        owner_id=current_user.id,
        question_set_id=qs.id,
        status="active",
        mode=payload.mode,
        total_questions=qs.total_questions,
        answered=0,
        current_index=0,
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


@router.get("/interview/{interview_id}/next", response_model=NextQuestionResponse)
def get_next_question(
    interview_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the next unanswered question in the interview."""
    interview = _get_active_interview(interview_id, current_user.id, db)
    qs = interview.question_set

    from app.services.interview_engine import flatten_questions
    all_q = flatten_questions({
        "technical_questions":  qs.technical_questions or [],
        "behavioral_questions": qs.behavioral_questions or [],
        "hr_questions":         qs.hr_questions or [],
        "project_questions":    qs.project_questions or [],
        "aws_questions":        qs.aws_questions or [],
        "python_questions":     qs.python_questions or [],
        "react_questions":      qs.react_questions or [],
        "database_questions":   qs.database_questions or [],
    })

    idx = interview.current_index
    if idx >= len(all_q):
        raise HTTPException(status_code=400, detail="All questions have been answered.")

    question = all_q[idx]
    return NextQuestionResponse(
        interview_id=interview.id,
        question_index=idx,
        total_questions=len(all_q),
        question=question,
        is_last=(idx == len(all_q) - 1),
    )


@router.post("/interview/answer", response_model=AnswerEvaluation, status_code=status.HTTP_201_CREATED)
def submit_answer(
    payload: AnswerSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit an answer, evaluate it with AI, and advance the interview."""
    interview = _get_active_interview(payload.interview_id, current_user.id, db)

    from app.services.interview_engine import evaluate_answer
    from app.services.interview_engine import flatten_questions

    # Get expected keywords for the question
    qs = interview.question_set
    all_q = flatten_questions({
        "technical_questions":  qs.technical_questions or [],
        "behavioral_questions": qs.behavioral_questions or [],
        "hr_questions":         qs.hr_questions or [],
        "project_questions":    qs.project_questions or [],
        "aws_questions":        qs.aws_questions or [],
        "python_questions":     qs.python_questions or [],
        "react_questions":      qs.react_questions or [],
        "database_questions":   qs.database_questions or [],
    })
    expected_kw = []
    if payload.question_index < len(all_q):
        expected_kw = all_q[payload.question_index].get("expected_keywords", [])

    # Evaluate
    try:
        eval_data = evaluate_answer(
            question=payload.question_text,
            answer=payload.answer_text,
            category=payload.question_category,
            difficulty=payload.question_difficulty,
            expected_keywords=expected_kw,
        )
    except Exception as exc:
        logger.exception("Answer evaluation failed: %s", exc)
        eval_data = {
            "score": 60.0, "technical_accuracy": 60.0,
            "communication": 60.0, "completeness": 60.0,
            "feedback": "Evaluation temporarily unavailable.",
            "ideal_answer": "", "keywords_used": [], "keywords_missed": [],
        }

    # Persist answer
    answer = MockAnswer(
        interview_id=interview.id,
        owner_id=current_user.id,
        question_index=payload.question_index,
        question_text=payload.question_text,
        question_category=payload.question_category,
        question_difficulty=payload.question_difficulty,
        answer_text=payload.answer_text,
        time_taken_secs=payload.time_taken_secs,
        score=eval_data.get("score"),
        technical_accuracy=eval_data.get("technical_accuracy"),
        communication=eval_data.get("communication"),
        completeness=eval_data.get("completeness"),
        feedback=eval_data.get("feedback"),
        ideal_answer=eval_data.get("ideal_answer"),
        keywords_used=eval_data.get("keywords_used"),
        keywords_missed=eval_data.get("keywords_missed"),
    )
    db.add(answer)

    # Advance interview state
    interview.answered += 1
    interview.current_index = payload.question_index + 1
    db.commit()
    db.refresh(answer)
    return answer


@router.post("/interview/{interview_id}/finish", response_model=InterviewResult)
def finish_interview(
    interview_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Complete the interview and generate the final scored result."""
    interview = db.query(MockInterview).filter(
        MockInterview.id == interview_id,
        MockInterview.owner_id == current_user.id,
    ).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found.")

    answers = (
        db.query(MockAnswer)
        .filter(MockAnswer.interview_id == interview_id)
        .order_by(MockAnswer.question_index)
        .all()
    )

    answer_dicts = [
        {
            "question_category": a.question_category,
            "question_difficulty": a.question_difficulty,
            "score": a.score or 0,
            "technical_accuracy": a.technical_accuracy or 0,
            "communication": a.communication or 0,
            "feedback": a.feedback or "",
        }
        for a in answers
    ]

    from app.services.interview_engine import generate_interview_result
    job_title = (interview.question_set.job_title or "") if interview.question_set else ""
    result_data = generate_interview_result(answer_dicts, job_title=job_title)

    interview.status              = "completed"
    interview.completed_at        = datetime.now(timezone.utc)
    interview.overall_score       = float(result_data.get("overall_score", 0))
    interview.technical_score     = float(result_data.get("technical_score", 0))
    interview.communication_score = float(result_data.get("communication_score", 0))
    interview.confidence_score    = float(result_data.get("confidence_score", 0))
    interview.grammar_score       = float(result_data.get("grammar_score", 0))
    interview.strengths           = result_data.get("strengths", [])
    interview.weaknesses          = result_data.get("weaknesses", [])
    interview.improvements        = result_data.get("improvements", [])
    interview.overall_feedback    = result_data.get("overall_feedback", "")
    db.commit()

    # Save to history
    qs = interview.question_set
    started = interview.started_at
    completed = interview.completed_at or datetime.now(timezone.utc)
    duration = (completed - started).total_seconds() / 60

    history = InterviewHistory(
        owner_id=current_user.id,
        interview_id=interview.id,
        job_title=qs.job_title if qs else None,
        total_questions=interview.answered,
        overall_score=interview.overall_score,
        technical_score=interview.technical_score,
        communication_score=interview.communication_score,
        duration_minutes=round(duration, 1),
        passed=(interview.overall_score or 0) >= 60,
    )
    db.add(history)
    db.commit()
    db.refresh(interview)

    answer_list = [
        {
            "id": a.id,
            "question_index": a.question_index,
            "question_text": a.question_text,
            "question_category": a.question_category,
            "question_difficulty": a.question_difficulty,
            "answer_text": a.answer_text,
            "score": a.score,
            "technical_accuracy": a.technical_accuracy,
            "communication": a.communication,
            "completeness": a.completeness,
            "feedback": a.feedback,
            "ideal_answer": a.ideal_answer,
            "keywords_used": a.keywords_used,
            "keywords_missed": a.keywords_missed,
            "time_taken_secs": a.time_taken_secs,
            "created_at": a.created_at.isoformat(),
        }
        for a in answers
    ]

    return InterviewResult(
        id=interview.id,
        status=interview.status,
        total_questions=interview.total_questions,
        answered=interview.answered,
        overall_score=interview.overall_score,
        technical_score=interview.technical_score,
        communication_score=interview.communication_score,
        confidence_score=interview.confidence_score,
        grammar_score=interview.grammar_score,
        strengths=interview.strengths,
        weaknesses=interview.weaknesses,
        improvements=interview.improvements,
        overall_feedback=interview.overall_feedback,
        answers=answer_list,
        started_at=interview.started_at,
        completed_at=interview.completed_at,
    )


@router.get("/interview/{interview_id}/result", response_model=InterviewResult)
def get_interview_result(
    interview_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    interview = db.query(MockInterview).filter(
        MockInterview.id == interview_id,
        MockInterview.owner_id == current_user.id,
    ).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found.")

    answers = (
        db.query(MockAnswer)
        .filter(MockAnswer.interview_id == interview_id)
        .order_by(MockAnswer.question_index)
        .all()
    )
    answer_list = [
        {
            "id": a.id,
            "question_index": a.question_index,
            "question_text": a.question_text,
            "question_category": a.question_category,
            "question_difficulty": a.question_difficulty,
            "answer_text": a.answer_text,
            "score": a.score,
            "technical_accuracy": a.technical_accuracy,
            "communication": a.communication,
            "completeness": a.completeness,
            "feedback": a.feedback,
            "ideal_answer": a.ideal_answer,
            "keywords_used": a.keywords_used,
            "keywords_missed": a.keywords_missed,
            "time_taken_secs": a.time_taken_secs,
            "created_at": a.created_at.isoformat(),
        }
        for a in answers
    ]
    return InterviewResult(
        id=interview.id,
        status=interview.status,
        total_questions=interview.total_questions,
        answered=interview.answered,
        overall_score=interview.overall_score,
        technical_score=interview.technical_score,
        communication_score=interview.communication_score,
        confidence_score=interview.confidence_score,
        grammar_score=interview.grammar_score,
        strengths=interview.strengths,
        weaknesses=interview.weaknesses,
        improvements=interview.improvements,
        overall_feedback=interview.overall_feedback,
        answers=answer_list,
        started_at=interview.started_at,
        completed_at=interview.completed_at,
    )


@router.get("/interview/history/list", response_model=InterviewHistoryList)
def get_interview_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total = db.query(InterviewHistory).filter(InterviewHistory.owner_id == current_user.id).count()
    items = (
        db.query(InterviewHistory)
        .filter(InterviewHistory.owner_id == current_user.id)
        .order_by(InterviewHistory.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return InterviewHistoryList(items=items, total=total, page=page, page_size=page_size)


@router.delete("/interview/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview(
    interview_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    interview = db.query(MockInterview).filter(
        MockInterview.id == interview_id,
        MockInterview.owner_id == current_user.id,
    ).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found.")
    db.delete(interview)
    db.commit()
    return None


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _get_active_interview(interview_id: str, user_id: str, db: Session) -> MockInterview:
    interview = db.query(MockInterview).filter(
        MockInterview.id == interview_id,
        MockInterview.owner_id == user_id,
    ).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found.")
    if interview.status != "active":
        raise HTTPException(status_code=400, detail="Interview is not active.")
    return interview
