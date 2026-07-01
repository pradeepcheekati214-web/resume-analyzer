"""Quick smoke test for AI features — run with: venv\Scripts\python.exe check_ai.py"""
import sys

print("Checking AI feature imports...")

try:
    from app.core.config import settings
    print(f"  AI_PROVIDER: {settings.AI_PROVIDER}")
    print(f"  OPENAI_API_KEY set: {bool(settings.OPENAI_API_KEY)}")
except Exception as e:
    print(f"  ERROR config: {e}"); sys.exit(1)

try:
    from app.models.ai_suggestion import AIResumeSuggestion
    from app.models.job_match import JobMatch
    from app.models.interview import InterviewQuestionSet, MockInterview, MockAnswer, InterviewHistory
    print("  Models: OK")
except Exception as e:
    print(f"  ERROR models: {e}"); sys.exit(1)

try:
    from app.services.ai_client import call_llm
    from app.services.ai_suggestion_engine import generate_resume_suggestions
    from app.services.job_match_engine import analyze_job_match
    from app.services.interview_engine import generate_interview_questions, evaluate_answer
    print("  Services: OK")
except Exception as e:
    print(f"  ERROR services: {e}"); sys.exit(1)

try:
    from app.api.v1.ai import router
    routes = [r.path for r in router.routes]
    print(f"  API routes: {len(routes)} registered")
    for r in routes:
        print(f"    {r}")
except Exception as e:
    print(f"  ERROR routes: {e}"); sys.exit(1)

try:
    # Test mock LLM
    response = call_llm("You are a helpful assistant.", "Provide resume suggestion")
    import json
    data = json.loads(response.content)
    print(f"  Mock LLM: OK — keys: {list(data.keys())[:4]}")
except Exception as e:
    print(f"  ERROR mock LLM: {e}"); sys.exit(1)

try:
    # Test DB table creation
    from app.core.database import Base, engine
    Base.metadata.create_all(bind=engine)
    from sqlalchemy import inspect
    insp = inspect(engine)
    tables = insp.get_table_names()
    ai_tables = [t for t in tables if t in ('resume_ai_suggestions','job_matches','interview_questions','mock_interviews','mock_answers','interview_history')]
    print(f"  DB tables created: {ai_tables}")
except Exception as e:
    print(f"  ERROR DB: {e}"); sys.exit(1)

print("\nAll checks passed!")
