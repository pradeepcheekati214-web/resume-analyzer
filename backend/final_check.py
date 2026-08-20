"""Full completeness check. Run: venv\Scripts\python.exe final_check.py"""
import sys
errors = []

def ok(msg): print(f"  [OK] {msg}")
def fail(msg): print(f"  [FAIL] {msg}"); errors.append(msg)

print("=" * 55)
print("BACKEND COMPLETENESS CHECK")
print("=" * 55)

# 1. Models
print("\n[Models]")
try:
    from app.models.user import User
    from app.models.resume import Resume
    from app.models.analysis import Analysis
    from app.models.ai_suggestion import AIResumeSuggestion
    from app.models.job_match import JobMatch
    from app.models.interview import InterviewQuestionSet, MockInterview, MockAnswer, InterviewHistory
    from app.models.chat import ChatSession, ChatMessage
    ok("All 9 models imported")
except Exception as e:
    fail(f"Models: {e}")

# 2. Schemas
print("\n[Schemas]")
try:
    from app.schemas.user import UserCreate, UserRead
    from app.schemas.resume import ResumeRead
    from app.schemas.analysis import AnalysisRead
    from app.schemas.ai_suggestion import AISuggestionRead
    from app.schemas.job_match import JobMatchRead
    from app.schemas.interview import QuestionSetRead, MockInterviewRead, InterviewResult
    from app.schemas.chat import ChatSessionRead, ChatMessageRead, SendMessageResponse
    ok("All schemas imported")
except Exception as e:
    fail(f"Schemas: {e}")

# 3. Services
print("\n[Services]")
try:
    from app.services.resume_parser import parse_resume
    from app.services.skill_extractor import extract_skills
    from app.services.ats_scorer import calculate_ats_score
    from app.services.analyzer import analyze_resume
    from app.services.suggestion_engine import generate_suggestions
    from app.services.ai_client import call_llm
    from app.services.ai_suggestion_engine import generate_resume_suggestions
    from app.services.job_match_engine import analyze_job_match
    from app.services.interview_engine import generate_interview_questions, evaluate_answer
    from app.services.chat_service import generate_chat_response
    ok("All 10 services imported")
except Exception as e:
    fail(f"Services: {e}")

# 4. API routes
print("\n[API Routes]")
try:
    from app.api.v1 import router
    route_paths = [r.path for r in router.routes]
    expected = [
        "/auth/register", "/auth/login",
        "/resumes/upload", "/resumes/{resume_id}/analyze",
        "/analysis/history", "/analysis/{analysis_id}",
        "/ai/resume-suggestions", "/ai/job-match", "/ai/job-match/history",
        "/ai/interview/questions", "/ai/interview/start",
        "/ai/interview/answer", "/ai/interview/{interview_id}/finish",
        "/ai/interview/{interview_id}/result",
        "/chat/start-session", "/chat/send-message",
        "/chat/history/{session_id}", "/chat/sessions",
        "/chat/session/{session_id}",
        "/users/profile",
    ]
    missing_routes = [r for r in expected if r not in route_paths]
    if missing_routes:
        fail(f"Missing routes: {missing_routes}")
    else:
        ok(f"{len(route_paths)} routes registered, all expected routes present")
except Exception as e:
    fail(f"Routes: {e}")

# 5. DB tables
print("\n[Database Tables]")
try:
    import sqlalchemy as sa
    from app.core.database import engine, Base
    from app.models import user, resume, analysis, ai_suggestion, job_match, interview, chat
    Base.metadata.create_all(bind=engine)
    tables = sorted(sa.inspect(engine).get_table_names())
    expected_tables = [
        "users", "resumes", "analyses",
        "resume_ai_suggestions", "job_matches",
        "interview_questions", "mock_interviews", "mock_answers", "interview_history",
        "chat_sessions", "chat_messages",
    ]
    missing_tables = [t for t in expected_tables if t not in tables]
    if missing_tables:
        fail(f"Missing tables: {missing_tables}")
    else:
        ok(f"All {len(expected_tables)} expected tables present")
    print(f"     Tables: {tables}")
except Exception as e:
    fail(f"DB: {e}")

# 6. Mock LLM (chat response)
print("\n[Mock LLM - Chat]")
try:
    from app.services.chat_service import generate_chat_response
    resp = generate_chat_response(
        user_message="How can I improve my resume?",
        resume_text="John Doe - Python React FastAPI Developer",
        history=[],
        ats_score=72,
        skills_found=["Python", "React"],
        missing_skills=["Kubernetes"],
    )
    assert len(resp) > 50, "Response too short"
    ok(f"Chat response: {len(resp)} chars")
except Exception as e:
    fail(f"Chat mock: {e}")

# 7. Mock LLM (questions)
print("\n[Mock LLM - Interview Questions]")
try:
    from app.services.interview_engine import generate_interview_questions
    data = generate_interview_questions(
        "Python React FastAPI Developer with AWS SQL Docker Git",
        "Associate Software Engineer", "", ["Python","React","AWS","SQL"]
    )
    cats = ["technical_questions","python_questions","react_questions","aws_questions","database_questions"]
    total = sum(len(data.get(c) or []) for c in cats)
    assert total > 0, "No questions generated"
    ok(f"Generated {total} relevant questions")
    # Verify new fields
    for c in cats:
        for q in (data.get(c) or []):
            for field in ["expected_answer","key_points","follow_up_questions"]:
                assert field in q, f"Missing {field} in {c}"
    ok("All questions have expected_answer, key_points, follow_up_questions")
except Exception as e:
    fail(f"Interview questions: {e}")

# 8. Config
print("\n[Config]")
try:
    from app.core.config import settings
    ok(f"AI_PROVIDER: {settings.AI_PROVIDER}")
    ok(f"DATABASE_URL: {settings.DATABASE_URL[:30]}...")
    ok(f"AWS configured: {settings.is_aws_configured}")
except Exception as e:
    fail(f"Config: {e}")

print("\n" + "=" * 55)
if errors:
    print(f"FAILED: {len(errors)} error(s):")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print(f"ALL CHECKS PASSED - Backend is complete!")
    print("=" * 55)
