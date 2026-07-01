"""
Run this once to apply any missing column additions to the SQLite DB.
Usage: venv\Scripts\python.exe migrate_db.py
"""
import sqlalchemy as sa
from app.core.database import Base, engine
from app.models import user, resume, analysis
from app.models import ai_suggestion, job_match, interview  # noqa

# Create any missing tables
Base.metadata.create_all(bind=engine)
print("Tables ensured.")

# Add missing columns individually (SQLite does not support multi-column ADD)
migrations = [
    ("interview_questions", "company_name", "VARCHAR(255)"),
]

insp = sa.inspect(engine)
with engine.connect() as conn:
    for table, col, col_type in migrations:
        try:
            existing = [c["name"] for c in insp.get_columns(table)]
            if col not in existing:
                conn.execute(sa.text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
                conn.commit()
                print(f"  Added column: {table}.{col}")
            else:
                print(f"  Already exists: {table}.{col}")
        except Exception as e:
            print(f"  Skip {table}.{col}: {e}")

print("Migration complete.")
