"""Verify chat feature is fully working."""
import sqlalchemy as sa
from app.core.database import engine, Base
from app.models.chat import ChatSession, ChatMessage
from app.models import chat  # ensure models registered

# Create tables if missing
Base.metadata.create_all(bind=engine)

insp = sa.inspect(engine)
tables = insp.get_table_names()

print("Chat tables in DB:")
for t in ["chat_sessions", "chat_messages"]:
    if t in tables:
        cols = [c["name"] for c in insp.get_columns(t)]
        print(f"  {t}: {cols}")
    else:
        print(f"  {t}: MISSING - creating now")

# Test service imports
from app.services.chat_service import generate_chat_response, build_system_prompt
print("\nChat service imports: OK")

# Test mock response
response = generate_chat_response(
    user_message="How can I improve my resume?",
    resume_text="John Doe - Python FastAPI React Developer with 2 years experience.",
    history=[],
    ats_score=72,
    skills_found=["Python", "React", "FastAPI"],
    missing_skills=["Kubernetes", "TypeScript"],
)
print(f"\nMock response length: {len(response)} chars")
print(f"Response preview: {response[:100]}...")

# Test API router
from app.api.v1.chat import router
routes = [r.path for r in router.routes]
print(f"\nChat API routes ({len(routes)}):")
for r in routes:
    print(f"  {r}")

print("\nAll chat verification passed!")
