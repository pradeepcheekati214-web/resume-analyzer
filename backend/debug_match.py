from app.core.database import SessionLocal
from app.models.resume import Resume
from app.models.job_match import JobMatch
from app.services.job_match_engine import analyze_job_match
from app.services.skill_extractor import extract_skills

db = SessionLocal()
resumes = db.query(Resume).all()
print(f"Total resumes: {len(resumes)}")
for r in resumes:
    txt_len = len(r.raw_text or '')
    print(f"  {r.id[:8]} | {r.file_name} | raw_text={txt_len} chars")

matches = db.query(JobMatch).all()
print(f"\nTotal job matches: {len(matches)}")
for m in matches:
    print(f"  {m.id[:8]} | overall={m.overall_match} skills={m.skills_match} keywords={m.keyword_match} status={m.status}")
    if m.error_message:
        print(f"  ERROR: {m.error_message}")

print("\n--- Scoring engine test ---")
sample_jd = "Looking for Python FastAPI React PostgreSQL Docker AWS CI/CD engineer with 3+ years. Bachelor degree required."
sample_resume = "John Doe john@example.com +1 555-1234\nSenior Engineer TechCorp 2020-Present\nBuilt REST APIs Python FastAPI React PostgreSQL Docker AWS Lambda GitHub Actions 5 years\nB.Sc Computer Science\nSKILLS: Python React AWS Docker PostgreSQL FastAPI CI/CD Git"
skills = extract_skills(sample_resume)
print(f"Skills: {skills}")
result = analyze_job_match(sample_resume, sample_jd, skills)
print(f"overall_match:     {result['overall_match']}")
print(f"skills_match:      {result['skills_match']}")
print(f"keyword_match:     {result['keyword_match']}")
print(f"experience_match:  {result['experience_match']}")
print(f"ats_compatibility: {result['ats_compatibility']}")
print(f"education_match:   {result['education_match']}")
print(f"matching_skills:   {result['matching_skills']}")
print(f"missing_skills:    {result['missing_skills'][:5]}")
db.close()
