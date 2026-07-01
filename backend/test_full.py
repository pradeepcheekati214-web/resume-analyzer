"""
Quick end-to-end test — run with:
  cd backend
  venv\Scripts\python.exe test_full.py
"""
import sys, json, pathlib, tempfile

# ── Test the parser + analyzer directly (no HTTP) ──────────────────────────
print("=" * 60)
print("TEST 1: Direct resume parsing + analysis")
print("=" * 60)

# Create a sample DOCX-like text resume as plain bytes
sample_text = b"""John Doe
john.doe@email.com | +1 555-123-4567 | linkedin.com/in/johndoe

SUMMARY
Results-driven Software Engineer with 5 years of experience building
scalable web applications using Python, React and AWS.

EXPERIENCE
Senior Software Engineer - TechCorp (2021-Present)
- Developed REST APIs using Python FastAPI serving 50K daily users
- Built React frontend reducing page load time by 40%
- Deployed microservices on AWS Lambda and Docker
- Managed PostgreSQL and DynamoDB databases
- Implemented CI/CD pipelines using GitHub Actions

Software Engineer - StartupXYZ (2019-2021)
- Built full-stack features using Django and JavaScript
- Worked with SQL, Redis and Elasticsearch
- Used Git, Agile/Scrum methodologies

EDUCATION
B.Sc. Computer Science - State University (2019)

SKILLS
Python, JavaScript, TypeScript, React, Node.js, FastAPI, Django
AWS, Docker, Kubernetes, PostgreSQL, MySQL, Redis, DynamoDB
Git, GitHub Actions, CI/CD, Agile, REST API, Linux, Bash
Machine Learning, TensorFlow, Pandas, NumPy
"""

# Write to a temp .txt file (we'll parse as text)
tmp = pathlib.Path(tempfile.gettempdir()) / "test_resume.txt"
tmp.write_bytes(sample_text)
print(f"Sample resume written to: {tmp}")

try:
    # Test skill extraction directly
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    from app.services.skill_extractor import extract_skills, find_missing_skills
    
    text = sample_text.decode("utf-8")
    skills = extract_skills(text)
    missing = find_missing_skills(skills, "")
    
    print(f"\nSkills found ({len(skills)}): {skills[:10]}...")
    print(f"Missing skills ({len(missing)}): {missing[:5]}...")
    
    # Test ATS scorer
    from app.services.ats_scorer import calculate_ats_score
    from app.services.resume_parser import extract_contact_info
    
    contact = extract_contact_info(text)
    print(f"\nContact info: {contact}")
    
    result = calculate_ats_score(
        text=text,
        skills_found=skills,
        missing_skills=missing,
        contact_info=contact,
    )
    print(f"\nATS Score: {result.total_score}")
    print(f"Breakdown: {json.dumps(result.breakdown, indent=2)}")
    
    if result.total_score > 0:
        print("\n✅ TEST PASSED — Analysis pipeline works correctly")
    else:
        print("\n❌ TEST FAILED — Score is 0, something is wrong")

except Exception as e:
    import traceback
    print(f"\n❌ ERROR: {e}")
    traceback.print_exc()

# ── Test PDF parsing ────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("TEST 2: PDF parsing check")
print("=" * 60)
try:
    import pdfplumber
    print("✅ pdfplumber imported OK")
except ImportError:
    print("❌ pdfplumber NOT installed — run: pip install pdfplumber")

try:
    from docx import Document
    print("✅ python-docx imported OK")
except ImportError:
    print("❌ python-docx NOT installed — run: pip install python-docx")

# ── Test temp file saving ────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("TEST 3: Temp file saving")
print("=" * 60)
upload_dir = pathlib.Path(tempfile.gettempdir()) / "resume_analyzer_uploads"
upload_dir.mkdir(exist_ok=True)
test_file = upload_dir / "test_resume.pdf"
test_file.write_bytes(b"test")
print(f"✅ Temp dir writable: {upload_dir}")
test_file.unlink()
