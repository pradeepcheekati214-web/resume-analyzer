from app.services.interview_engine import generate_interview_questions, flatten_questions

data = generate_interview_questions(
    resume_text="John Doe, Python Developer, React, AWS, FastAPI, Docker",
    job_title="Software Engineer",
    job_description="",
    skills=["Python", "React", "AWS", "Docker"]
)

cats = [
    'technical_questions','behavioral_questions','hr_questions','project_questions',
    'aws_questions','python_questions','react_questions','database_questions'
]

total = 0
for c in cats:
    n = len(data.get(c) or [])
    total += n
    print(f"  {c}: {n}")

print(f"\n  data['total'] key: {data.get('total')}")
print(f"  actual count:      {total}")

flat = flatten_questions(data)
print(f"  flatten_questions: {len(flat)}")
print("\nSample question:", flat[0] if flat else "NONE")
