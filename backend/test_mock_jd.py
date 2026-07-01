from app.services.ai_client import _call_mock
import json

# Test 1: without JD
r1 = _call_mock("You are a senior technical interviewer.", "Generate interview questions for this candidate.\nTARGET ROLE: Software Engineer\nJOB DESCRIPTION: \nKEY SKILLS: Python, React")
d1 = json.loads(r1.content)
total1 = sum(len(d1.get(k) or []) for k in ["technical_questions","behavioral_questions","hr_questions","project_questions","aws_questions","python_questions","react_questions","database_questions"])
print(f"Test 1 (no JD):     {total1} questions, tech[0]={d1['technical_questions'][0]['question'][:60]}")

# Test 2: with React JD
r2 = _call_mock("You are a senior technical interviewer.", "Generate interview questions.\nTARGET ROLE: Frontend Engineer\nJOB DESCRIPTION: We need a React.js developer with CSS and UI experience.\nKEY SKILLS: React, CSS")
d2 = json.loads(r2.content)
total2 = sum(len(d2.get(k) or []) for k in ["technical_questions","behavioral_questions","hr_questions","project_questions","aws_questions","python_questions","react_questions","database_questions"])
print(f"Test 2 (React JD):  {total2} questions, tech[0]={d2['technical_questions'][0]['question'][:60]}")

# Test 3: with ML JD
r3 = _call_mock("You are a senior technical interviewer.", "Generate interview questions.\nTARGET ROLE: Data Scientist\nJOB DESCRIPTION: Machine learning engineer with TensorFlow and PyTorch experience required.\nKEY SKILLS: Python, ML")
d3 = json.loads(r3.content)
total3 = sum(len(d3.get(k) or []) for k in ["technical_questions","behavioral_questions","hr_questions","project_questions","aws_questions","python_questions","react_questions","database_questions"])
print(f"Test 3 (ML JD):     {total3} questions, tech[0]={d3['technical_questions'][0]['question'][:60]}")

# Test 4: with DevOps JD  
r4 = _call_mock("You are a senior technical interviewer.", "Generate interview questions.\nTARGET ROLE: DevOps Engineer\nJOB DESCRIPTION: Kubernetes Terraform Jenkins DevOps CI/CD deployment engineer required.\nKEY SKILLS: Kubernetes, Terraform")
d4 = json.loads(r4.content)
total4 = sum(len(d4.get(k) or []) for k in ["technical_questions","behavioral_questions","hr_questions","project_questions","aws_questions","python_questions","react_questions","database_questions"])
print(f"Test 4 (DevOps JD): {total4} questions, tech[0]={d4['technical_questions'][0]['question'][:60]}")

print("\nAll mock JD tests passed!")
