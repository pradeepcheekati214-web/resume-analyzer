"""
Full HTTP API test — tests register, login, upload, analyze end-to-end.
Run with: venv\Scripts\python.exe test_api.py
"""
import requests
import pathlib
import tempfile
import json

BASE = "http://localhost:8000/api/v1"

EMAIL    = "apitest99@test.com"
PASSWORD = "TestPass123"

print("=" * 60)

# 1. Register
print("1. Registering user...")
r = requests.post(f"{BASE}/auth/register", json={
    "email": EMAIL, "password": PASSWORD, "full_name": "API Test"
})
if r.status_code == 409:
    print("   User already exists, continuing...")
elif r.status_code == 201:
    print(f"   ✅ Registered: {r.json()['email']}")
else:
    print(f"   ❌ Register failed: {r.status_code} {r.text}")

# 2. Login
print("2. Logging in...")
r = requests.post(f"{BASE}/auth/login", data={
    "username": EMAIL, "password": PASSWORD
})
if r.status_code != 200:
    print(f"   ❌ Login failed: {r.status_code} {r.text}")
    exit(1)
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"   ✅ Token: {token[:30]}...")

# 3. Create a sample PDF-like content and upload
print("3. Uploading resume...")
sample_resume = b"""%PDF-1.4
John Smith
john.smith@email.com | +1 555-000-1234 | linkedin.com/in/johnsmith

SUMMARY
Software Engineer with 6 years of Python, React, AWS experience.

EXPERIENCE
Senior Engineer - TechCo (2020-Present)
- Built REST APIs using Python FastAPI serving 100K daily users
- Deployed on AWS Lambda, S3, DynamoDB
- Reduced load time by 50% with React optimizations
- Led team of 4 engineers using Agile/Scrum

SKILLS
Python, JavaScript, React, FastAPI, AWS, Docker, PostgreSQL, Git, CI/CD

EDUCATION
B.Sc. Computer Science - University 2018
"""

# Write as a .txt file (our parser handles text extraction)
tmp_file = pathlib.Path(tempfile.gettempdir()) / "test_upload_resume.txt"
tmp_file.write_bytes(sample_resume)

# Upload as PDF mimetype
with open(tmp_file, "rb") as f:
    r = requests.post(f"{BASE}/resumes/upload",
        files={"file": ("my_resume.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        headers=headers
    )

if r.status_code != 201:
    print(f"   ❌ Upload failed: {r.status_code} {r.text}")
    exit(1)

resume_id = r.json()["id"]
print(f"   ✅ Uploaded: id={resume_id}")

# 4. Check temp file was saved
upload_dir = pathlib.Path(tempfile.gettempdir()) / "resume_analyzer_uploads"
saved_files = list(upload_dir.glob(f"{resume_id}.*"))
print(f"   Temp file saved: {saved_files}")

# 5. Analyze
print("4. Analyzing resume...")
r = requests.post(f"{BASE}/resumes/{resume_id}/analyze",
    json={"job_description": ""},
    headers=headers
)

if r.status_code not in (200, 202):
    print(f"   ❌ Analyze failed: {r.status_code} {r.text}")
    exit(1)

data = r.json()
print(f"   Status:        {data.get('status')}")
print(f"   ATS Score:     {data.get('ats_score')}")
print(f"   Skills Found:  {len(data.get('skills_found') or [])}")
print(f"   Missing:       {len(data.get('missing_skills') or [])}")
print(f"   Suggestions:   {len(data.get('suggestions') or [])}")
print(f"   Error:         {data.get('error_message')}")

if data.get("ats_score") and data["ats_score"] > 0:
    print("\n✅ FULL PIPELINE WORKS!")
else:
    print("\n❌ Score is 0 — check error_message above")
    print(f"\nFull response:\n{json.dumps(data, indent=2, default=str)}")
