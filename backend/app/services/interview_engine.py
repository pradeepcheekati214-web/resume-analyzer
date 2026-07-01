"""
Interview engine — resume-aware, JD-aware question generation.

Rules:
  - ONLY generate questions for technologies present in the resume OR job description.
  - Never generate ML/GraphQL/AI questions unless they appear in the resume/JD.
  - Categories are dynamically built from the candidate's actual skill set.
  - Difficulty distribution: 40% Easy, 40% Medium, 20% Hard.
  - Each question has: question, difficulty, expected_answer, key_points, follow_up_questions.
"""
import logging
import re
from typing import List, Dict, Optional
from app.services.ai_client import call_llm, parse_json_response

logger = logging.getLogger(__name__)

QUESTION_SYSTEM = """You are a senior technical interviewer.
STRICT RULE: Only generate questions about technologies explicitly found in the resume or job description.
Never invent technologies or ask about things not mentioned.
Always respond with valid JSON only — no markdown, no explanation."""

EVAL_SYSTEM = """You are an expert interview coach. Evaluate answers fairly and constructively.
Always respond with valid JSON only."""


# ---------------------------------------------------------------------------
# Resume analysis helpers
# ---------------------------------------------------------------------------

# Map of skill → category key
SKILL_CATEGORY_MAP: Dict[str, str] = {
    # Python ecosystem
    "python": "python_questions", "fastapi": "python_questions",
    "django": "python_questions", "flask": "python_questions",
    "celery": "python_questions", "pytest": "python_questions",
    "pydantic": "python_questions", "sqlalchemy": "python_questions",

    # React / Frontend
    "react": "react_questions", "react.js": "react_questions",
    "next.js": "react_questions", "typescript": "react_questions",
    "javascript": "react_questions", "html": "react_questions",
    "css": "react_questions", "tailwind": "react_questions",
    "redux": "react_questions", "vite": "react_questions",

    # AWS
    "aws": "aws_questions", "lambda": "aws_questions",
    "s3": "aws_questions", "ec2": "aws_questions",
    "rds": "aws_questions", "dynamodb": "aws_questions",
    "api gateway": "aws_questions", "cloudwatch": "aws_questions",
    "cognito": "aws_questions", "cloudfront": "aws_questions",
    "ecs": "aws_questions", "eks": "aws_questions",
    "cdk": "aws_questions", "terraform": "aws_questions",

    # Database
    "sql": "database_questions", "postgresql": "database_questions",
    "mysql": "database_questions", "sqlite": "database_questions",
    "mongodb": "database_questions", "redis": "database_questions",
    "elasticsearch": "database_questions", "nosql": "database_questions",

    # DevOps / Tools
    "docker": "technical_questions", "kubernetes": "technical_questions",
    "git": "technical_questions", "github": "technical_questions",
    "ci/cd": "technical_questions", "github actions": "technical_questions",
    "jenkins": "technical_questions", "linux": "technical_questions",
    "rest api": "technical_questions", "fastapi": "technical_questions",
}

# Company-specific priority skills
COMPANY_PRIORITIES: Dict[str, List[str]] = {
    "accenture":   ["Python", "Java", "SQL", "React", "REST API", "Git", "AWS", "Agile"],
    "infosys":     ["Java", "Python", "SQL", "Spring", "REST API", "Agile"],
    "tcs":         ["Java", "Python", "SQL", "Spring Boot", "REST API", "Testing"],
    "wipro":       ["Java", "Python", "SQL", "AWS", "REST API", "Agile"],
    "cognizant":   ["Java", "Python", "SQL", "AWS", "React", "REST API"],
    "amazon":      ["Python", "Java", "AWS", "System Design", "SQL", "Leadership"],
    "google":      ["Python", "Go", "System Design", "Algorithms", "SQL"],
    "microsoft":   ["Python", "C#", ".NET", "Azure", "SQL", "System Design"],
    "meta":        ["Python", "React", "System Design", "SQL", "Distributed Systems"],
}

# Projects that indicate Resume Analyzer project
RESUME_ANALYZER_KEYWORDS = [
    "resume analyzer", "ats score", "resume parser", "skill extractor",
    "job match", "mock interview", "ai resume", "resume analysis",
]


def analyze_resume_for_questions(
    resume_text: str,
    job_description: str = "",
    job_title: str = "",
    company: str = "",
) -> dict:
    """
    Analyse resume + JD and return a structured context dict for question generation.
    This is purely algorithmic — no LLM call needed here.
    """
    text_lower = resume_text.lower()
    jd_lower   = (job_description or "").lower()
    combined   = text_lower + " " + jd_lower

    from app.services.skill_extractor import extract_skills
    resume_skills = extract_skills(resume_text)
    jd_skills     = extract_skills(job_description) if job_description else []

    # All skills relevant to this candidate
    all_skills = list({s.lower() for s in (resume_skills + jd_skills)})

    # Determine which categories to generate (only if skill present)
    active_categories: Dict[str, List[str]] = {}
    for skill_lower, cat_key in SKILL_CATEGORY_MAP.items():
        if skill_lower in combined:
            if cat_key not in active_categories:
                active_categories[cat_key] = []
            active_categories[cat_key].append(skill_lower)

    # Always include behavioral and HR
    active_categories["behavioral_questions"] = ["behavioral"]
    active_categories["hr_questions"]         = ["hr"]

    # Project detection
    has_resume_analyzer = any(kw in combined for kw in RESUME_ANALYZER_KEYWORDS)
    projects = _extract_projects(resume_text)

    # Company detection
    company_lower = company.lower() if company else ""
    for comp_name in COMPANY_PRIORITIES:
        if comp_name in jd_lower or comp_name in company_lower:
            company_lower = comp_name
            break

    # Experience level
    level = _detect_level(resume_text + " " + (job_title or ""))

    # Years of experience
    years = _extract_years(resume_text)

    return {
        "resume_skills":       resume_skills,
        "jd_skills":           jd_skills,
        "active_categories":   active_categories,
        "has_resume_analyzer": has_resume_analyzer,
        "projects":            projects,
        "company":             company_lower,
        "level":               level,
        "years_experience":    years,
        "job_title":           job_title or "Software Engineer",
    }


# ---------------------------------------------------------------------------
# Main question generation
# ---------------------------------------------------------------------------
def generate_interview_questions(
    resume_text: str,
    job_title: str = "",
    job_description: str = "",
    skills: list = None,
    company: str = "",
) -> dict:
    """
    Generate resume-aware, JD-aware interview questions.
    Only asks about skills actually present in the resume or JD.
    """
    skills = skills or []

    # Analyse resume context
    ctx = analyze_resume_for_questions(
        resume_text=resume_text,
        job_description=job_description,
        job_title=job_title,
        company=company,
    )

    # Build the prompt with strict rules
    prompt = _build_question_prompt(ctx, resume_text, job_description)

    response = call_llm(QUESTION_SYSTEM, prompt)
    data = parse_json_response(response.content)

    # Ensure all category keys exist
    all_cat_keys = [
        "technical_questions", "behavioral_questions", "hr_questions",
        "project_questions", "aws_questions", "python_questions",
        "react_questions", "database_questions",
    ]
    for key in all_cat_keys:
        if key not in data:
            data[key] = []

    # Strip categories not relevant to this resume/JD
    for key in all_cat_keys:
        if key not in ctx["active_categories"] and key not in ("behavioral_questions", "hr_questions", "project_questions"):
            if not _category_relevant(key, ctx):
                data[key] = []

    # Renumber sequentially
    idx = 1
    for cat_key in all_cat_keys:
        for q in data.get(cat_key) or []:
            q["id"] = idx
            idx += 1

    data["total"] = idx - 1
    return data


def _build_question_prompt(ctx: dict, resume_text: str, job_description: str) -> str:
    active_cats = list(ctx["active_categories"].keys())
    company_note = ""
    if ctx["company"] in COMPANY_PRIORITIES:
        priorities = ", ".join(COMPANY_PRIORITIES[ctx["company"]])
        company_note = f"\nCOMPANY PRIORITIES for {ctx['company'].title()}: {priorities}"

    project_note = ""
    if ctx["has_resume_analyzer"]:
        project_note = """
DETECTED PROJECT: Resume Analyzer
Generate project-specific questions covering:
- ATS score algorithm design
- Resume parsing (PDF/DOCX)
- Skill extraction logic
- Job Description Match Analyzer
- AI Suggestions pipeline
- Database design (SQLAlchemy models)
- JWT authentication flow
- AWS deployment (Lambda, S3, DynamoDB)
"""
    elif ctx["projects"]:
        project_note = f"\nDETECTED PROJECTS: {', '.join(ctx['projects'][:3])}\nGenerate questions specific to these projects."

    return f"""Generate interview questions STRICTLY based on the candidate's resume and job description.

CANDIDATE LEVEL: {ctx['level']} ({ctx['years_experience'] or 'unknown'} years)
TARGET ROLE: {ctx['job_title']}
RESUME SKILLS: {', '.join(ctx['resume_skills'][:25])}
JD SKILLS: {', '.join(ctx['jd_skills'][:20])}
ACTIVE CATEGORIES: {', '.join(active_cats)}{company_note}{project_note}

RESUME (key sections):
{resume_text[:2500]}

JOB DESCRIPTION:
{(job_description or 'Not provided')[:1500]}

STRICT RULES:
1. ONLY generate questions about technologies in the resume or JD above.
2. DO NOT generate Machine Learning, GraphQL, Kafka, or any tech NOT in the resume/JD.
3. Leave categories EMPTY ([]) if the technology is not in resume or JD.
4. Difficulty distribution per category: 40% easy, 40% medium, 20% hard.
5. Generate 2-4 questions per active category.
6. Each question must be specific to THIS candidate's experience level and skills.

Return a JSON object with EXACTLY these keys:
{{
  "technical_questions":  [q, ...],
  "behavioral_questions": [q, ...],
  "hr_questions":         [q, ...],
  "project_questions":    [q, ...],
  "aws_questions":        [q, ...],
  "python_questions":     [q, ...],
  "react_questions":      [q, ...],
  "database_questions":   [q, ...]
}}

Each question object must have ALL these keys:
{{
  "id": <int>,
  "question": "specific question text",
  "category": "category_name",
  "difficulty": "easy|medium|hard",
  "tips": "how to approach this question",
  "expected_answer": "what a good answer covers in 2-3 sentences",
  "key_points": ["point1", "point2", "point3"],
  "follow_up_questions": ["follow-up 1", "follow-up 2"],
  "expected_keywords": ["kw1", "kw2", "kw3"]
}}"""


def _category_relevant(cat_key: str, ctx: dict) -> bool:
    """Check if a category should have questions for this candidate."""
    cat_skill_map = {
        "python_questions":   ["python", "fastapi", "django", "flask"],
        "react_questions":    ["react", "javascript", "typescript", "next.js"],
        "aws_questions":      ["aws", "lambda", "s3", "ec2", "dynamodb", "cloudwatch"],
        "database_questions": ["sql", "postgresql", "mysql", "mongodb", "redis"],
        "technical_questions":["docker", "git", "ci/cd", "rest api", "kubernetes"],
    }
    required = cat_skill_map.get(cat_key, [])
    if not required:
        return True
    combined = " ".join(ctx["resume_skills"] + ctx["jd_skills"]).lower()
    return any(s in combined for s in required)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _extract_projects(resume_text: str) -> List[str]:
    """Extract project names from resume."""
    projects = []
    project_section = re.findall(
        r'(?:projects?|portfolio)[:\s]*\n(.*?)(?:\n\n|\Z)',
        resume_text, re.IGNORECASE | re.DOTALL
    )
    for section in project_section:
        names = re.findall(r'[A-Z][a-zA-Z\s]{3,30}(?:App|System|API|Platform|Tool|Analyzer|Manager|Bot)?', section)
        projects.extend(names[:5])
    return list(set(projects))[:5]


def _extract_years(text: str) -> Optional[int]:
    matches = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)(?:\s+of)?\s*(?:experience|exp)?', text, re.IGNORECASE)
    if not matches:
        return None
    return max(int(m) for m in matches)


def _detect_level(text: str) -> str:
    text_lower = text.lower()
    if any(w in text_lower for w in ['senior', 'lead', 'principal', 'staff', 'sr.']):
        return 'Senior'
    if any(w in text_lower for w in ['junior', 'entry level', 'associate', 'jr.', 'fresher', 'graduate']):
        return 'Junior/Associate'
    return 'Mid-level'


def flatten_questions(question_set_data: dict) -> list:
    """Return all questions as a flat ordered list."""
    categories = [
        "technical_questions", "behavioral_questions", "hr_questions",
        "project_questions", "aws_questions", "python_questions",
        "react_questions", "database_questions",
    ]
    flat = []
    for cat in categories:
        for q in question_set_data.get(cat) or []:
            flat.append(q)
    return sorted(flat, key=lambda q: q.get("id", 0))


# ---------------------------------------------------------------------------
# Answer Evaluation
# ---------------------------------------------------------------------------
def evaluate_answer(
    question: str,
    answer: str,
    category: str,
    difficulty: str,
    expected_keywords: list = None,
    expected_answer: str = "",
    key_points: list = None,
) -> dict:
    expected_keywords = expected_keywords or []
    key_points        = key_points or []

    prompt = f"""Evaluate this interview answer.

QUESTION: {question}
CATEGORY: {category}
DIFFICULTY: {difficulty}
EXPECTED ANSWER OUTLINE: {expected_answer}
KEY POINTS TO COVER: {', '.join(key_points)}
EXPECTED KEYWORDS: {', '.join(expected_keywords)}

CANDIDATE'S ANSWER:
{answer[:1500]}

Return ONLY JSON:
{{
  "score": <0-100>,
  "technical_accuracy": <0-100>,
  "communication": <0-100>,
  "completeness": <0-100>,
  "feedback": "2-3 sentences of specific, constructive feedback",
  "ideal_answer": "what a complete answer would cover",
  "keywords_used": ["kw1", ...],
  "keywords_missed": ["kw1", ...]
}}"""

    response = call_llm(EVAL_SYSTEM, prompt)
    return parse_json_response(response.content)


# ---------------------------------------------------------------------------
# Final Interview Result
# ---------------------------------------------------------------------------
def generate_interview_result(answers: list, job_title: str = "") -> dict:
    if not answers:
        return _empty_result()

    avg_score = sum(a.get("score", 0) for a in answers) / len(answers)
    avg_tech  = sum(a.get("technical_accuracy", 0) for a in answers) / len(answers)
    avg_comm  = sum(a.get("communication", 0) for a in answers) / len(answers)

    prompt = f"""Synthesize these interview evaluations into a final report.

JOB TITLE: {job_title or 'Software Engineer'}
QUESTIONS ANSWERED: {len(answers)}
AVG SCORE: {avg_score:.1f}/100
AVG TECHNICAL: {avg_tech:.1f}/100
AVG COMMUNICATION: {avg_comm:.1f}/100

SUMMARIES:
{_format_answer_summaries(answers)}

Return ONLY JSON:
{{
  "overall_score": <0-100>,
  "technical_score": <0-100>,
  "communication_score": <0-100>,
  "confidence_score": <0-100>,
  "grammar_score": <0-100>,
  "strengths": ["strength1", "strength2", "strength3"],
  "weaknesses": ["weakness1", "weakness2"],
  "improvements": ["action1", "action2", "action3"],
  "overall_feedback": "3-4 sentence comprehensive assessment"
}}"""

    response = call_llm(EVAL_SYSTEM, prompt)
    return parse_json_response(response.content)


def _format_answer_summaries(answers: list) -> str:
    lines = []
    for i, a in enumerate(answers[:10], 1):
        lines.append(
            f"Q{i} [{a.get('question_category','?')}/{a.get('question_difficulty','?')}]: "
            f"score={a.get('score',0):.0f} feedback={str(a.get('feedback',''))[:80]}"
        )
    return "\n".join(lines)


def _empty_result() -> dict:
    return {
        "overall_score": 0, "technical_score": 0, "communication_score": 0,
        "confidence_score": 0, "grammar_score": 0,
        "strengths": [], "weaknesses": [], "improvements": [],
        "overall_feedback": "No answers were submitted.",
    }
