"""Test question generation with and without job description"""
from app.services.interview_engine import generate_interview_questions

resume = "John Doe Python React AWS FastAPI PostgreSQL Docker Developer 5 years"
jd = "We need a Python FastAPI developer with React, AWS Lambda, PostgreSQL and Docker experience."

print("=== Test 1: With Job Title + Job Description ===")
data = generate_interview_questions(resume, "Software Engineer", jd, ["Python","React","AWS","Docker"])
cats = ["technical_questions","behavioral_questions","hr_questions","project_questions","aws_questions","python_questions","react_questions","database_questions"]
total = sum(len(data.get(c) or []) for c in cats)
print(f"Total questions: {total}")
for c in cats:
    n = len(data.get(c) or [])
    if n: print(f"  {c}: {n}")

print("\n=== Test 2: Job Description only (no title) ===")
data2 = generate_interview_questions(resume, "", jd, ["Python","React","AWS"])
total2 = sum(len(data2.get(c) or []) for c in cats)
print(f"Total questions: {total2}")

print("\n=== Test 3: Long job description ===")
long_jd = """
We are looking for a Senior Software Engineer.
Requirements:
- 5+ years Python experience with FastAPI or Django
- Strong React.js frontend skills
- AWS experience: Lambda, S3, DynamoDB, API Gateway
- PostgreSQL and Redis databases
- Docker and Kubernetes
- CI/CD with GitHub Actions
- Excellent communication and teamwork skills
"""
data3 = generate_interview_questions(resume, "Senior Software Engineer", long_jd, ["Python","React","AWS","Docker","PostgreSQL"])
total3 = sum(len(data3.get(c) or []) for c in cats)
print(f"Total questions: {total3}")
for c in cats:
    n = len(data3.get(c) or [])
    if n: print(f"  {c}: {n}")

print("\nAll tests done!")
