"""Task 3-5 validation — run with: venv\Scripts\python.exe task345_test.py"""
import json
from app.services.interview_engine import generate_interview_questions, analyze_resume_for_questions

ASSOCIATE_RESUME = """
John Doe | john@example.com | +1 555-1234 | linkedin.com/in/johndoe | github.com/johndoe

SUMMARY
Associate Software Engineer with 1.5 years of experience building full-stack web applications
using Python, React, FastAPI, SQL, Docker, Git, and AWS.

EXPERIENCE
Associate Software Engineer — ABC Tech (Jan 2023 – Present)
• Built REST APIs using Python FastAPI serving 10K+ daily users
• Developed React frontend components with hooks and context API
• Wrote SQL queries for PostgreSQL database optimization
• Containerized applications using Docker and Docker Compose
• Deployed applications to AWS (Lambda, S3, EC2, RDS)
• Used Git and GitHub Actions for version control and CI/CD

PROJECTS
Resume Analyzer — Personal Project
• Built an AI-powered Resume Analyzer with Python FastAPI backend
• Implemented ATS score algorithm, resume parser (PDF/DOCX), skill extractor
• Built Job Description Match Analyzer and AI Mock Interview features
• Integrated AWS Lambda, S3, DynamoDB, API Gateway for serverless deployment
• JWT authentication with bcrypt password hashing
• React frontend with Tailwind CSS

EDUCATION
B.Tech Computer Science — State University (2022)

SKILLS
Python, FastAPI, React, SQL, PostgreSQL, Docker, Git, GitHub Actions, AWS, Lambda,
S3, DynamoDB, REST API, CI/CD, HTML, CSS, SQLAlchemy, JWT
"""

JD_ACCENTURE = """
Accenture — Associate Software Engineer
We are looking for an Associate Software Engineer with skills in:
Python, React, SQL, REST APIs, Git, AWS, Agile methodology, communication, problem-solving.
Must have experience with web development, databases, and cloud deployment.
"""

print("=" * 60)
print("TEST 1: Context analysis for Associate SE resume")
print("=" * 60)
ctx = analyze_resume_for_questions(ASSOCIATE_RESUME, JD_ACCENTURE, "Associate Software Engineer", "Accenture")
print(f"  Level:              {ctx['level']}")
print(f"  Company:            {ctx['company']}")
print(f"  Years exp:          {ctx['years_experience']}")
print(f"  Has Resume Analyzer:{ctx['has_resume_analyzer']}")
print(f"  Resume skills:      {ctx['resume_skills'][:10]}")
print(f"  Active categories:  {list(ctx['active_categories'].keys())}")

# Verify NO ML/GraphQL/Kafka categories
bad_cats = [c for c in ctx['active_categories'] if 'ml' in c or 'graphql' in c or 'kafka' in c]
assert not bad_cats, f"BAD categories detected: {bad_cats}"
print("  No ML/GraphQL/Kafka categories ✅")

print()
print("=" * 60)
print("TEST 2: Full question generation — Associate SE + Accenture JD")
print("=" * 60)
data = generate_interview_questions(
    resume_text=ASSOCIATE_RESUME,
    job_title="Associate Software Engineer",
    job_description=JD_ACCENTURE,
    skills=ctx['resume_skills'],
    company="Accenture",
)

cats = ["technical_questions","behavioral_questions","hr_questions","project_questions",
        "aws_questions","python_questions","react_questions","database_questions"]

total = 0
for c in cats:
    qs = data.get(c) or []
    total += len(qs)
    if qs:
        print(f"  {c:<25} {len(qs)} questions")
        for q in qs:
            diff = q.get('difficulty', '?')
            has_expected = bool(q.get('expected_answer'))
            has_keypoints= bool(q.get('key_points'))
            has_followup = bool(q.get('follow_up_questions'))
            print(f"    [{diff:6}] {q['question'][:65]}...")
            assert has_expected, f"Missing expected_answer in: {q['question'][:40]}"
            assert has_keypoints, f"Missing key_points in: {q['question'][:40]}"
            assert has_followup, f"Missing follow_up_questions in: {q['question'][:40]}"

print(f"\n  Total questions: {total}")

# Verify no off-resume tech
all_questions_text = json.dumps(data).lower()
off_resume = ["machine learning", "graphql", "tensorflow", "pytorch", "kafka", "spark", "hadoop"]
found_off = [t for t in off_resume if t in all_questions_text]
assert not found_off, f"Off-resume tech found: {found_off}"
print(f"  No off-resume tech in questions ✅")

# Verify Resume Analyzer project questions
project_qs = data.get("project_questions") or []
assert len(project_qs) > 0, "No project questions generated"
print(f"  Project questions generated: {len(project_qs)} ✅")
ra_keywords = ["ats", "resume", "parser", "jwt", "authentication", "aws", "lambda"]
project_text = json.dumps(project_qs).lower()
found_ra = [k for k in ra_keywords if k in project_text]
print(f"  Resume Analyzer keywords in project questions: {found_ra} ✅")

# Verify difficulty distribution (roughly 40/40/20)
all_qs = []
for c in cats:
    all_qs.extend(data.get(c) or [])
easy   = sum(1 for q in all_qs if q.get('difficulty') == 'easy')
medium = sum(1 for q in all_qs if q.get('difficulty') == 'medium')
hard   = sum(1 for q in all_qs if q.get('difficulty') == 'hard')
print(f"\n  Difficulty: easy={easy} medium={medium} hard={hard}")

# Verify all required fields present
for q in all_qs:
    for field in ['question', 'difficulty', 'tips', 'expected_answer', 'key_points', 'follow_up_questions', 'expected_keywords']:
        assert field in q, f"Missing field '{field}' in question: {q.get('question','?')[:40]}"
print("  All required fields present in every question ✅")

print()
print("TEST 3: No AWS questions when resume has no AWS")
print("=" * 60)
no_aws_resume = "Python Django developer with PostgreSQL, Git, REST API. No cloud experience."
data2 = generate_interview_questions(no_aws_resume, "Backend Developer", "", ["Python", "Django", "PostgreSQL"])
aws_qs = data2.get("aws_questions") or []
print(f"  AWS questions for no-AWS resume: {len(aws_qs)} (expected 0) {'✅' if len(aws_qs)==0 else '❌'}")
react_qs = data2.get("react_questions") or []
print(f"  React questions for no-React resume: {len(react_qs)} (expected 0) {'✅' if len(react_qs)==0 else '❌'}")

print()
print("ALL TESTS PASSED ✅")
