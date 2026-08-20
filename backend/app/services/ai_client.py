"""
LLM client — wraps OpenAI, Amazon Bedrock, and a deterministic mock fallback.
Select the provider via AI_PROVIDER env var: openai | bedrock | mock
"""
import json
import logging
import re
from dataclasses import dataclass
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    model: str = ""


def call_llm(system_prompt: str, user_prompt: str) -> LLMResponse:
    """Dispatch to the configured LLM provider. Falls back to mock on any error."""
    provider = settings.AI_PROVIDER.lower()
    try:
        if provider == "openai":
            return _call_openai(system_prompt, user_prompt)
        elif provider == "bedrock":
            return _call_bedrock(system_prompt, user_prompt)
        else:
            return _call_mock(system_prompt, user_prompt)
    except Exception as exc:
        logger.warning("LLM provider '%s' failed: %s — falling back to mock", provider, exc)
        return _call_mock(system_prompt, user_prompt)


# ---------------------------------------------------------------------------
# OpenAI
# ---------------------------------------------------------------------------
def _call_openai(system_prompt: str, user_prompt: str) -> LLMResponse:
    try:
        import openai
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            max_tokens=settings.AI_MAX_TOKENS,
            temperature=settings.AI_TEMPERATURE,
            response_format={"type": "json_object"},
        )
        msg = response.choices[0].message.content or "{}"
        return LLMResponse(
            content=msg,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            model=settings.OPENAI_MODEL,
        )
    except Exception as exc:
        logger.error("OpenAI call failed: %s", exc)
        raise


# ---------------------------------------------------------------------------
# Amazon Bedrock (Claude)
# ---------------------------------------------------------------------------
def _call_bedrock(system_prompt: str, user_prompt: str) -> LLMResponse:
    try:
        import boto3
        client = boto3.client(
            "bedrock-runtime",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": settings.AI_MAX_TOKENS,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        })
        response = client.invoke_model(
            modelId=settings.AWS_BEDROCK_MODEL_ID,
            body=body,
            contentType="application/json",
            accept="application/json",
        )
        result = json.loads(response["body"].read())
        content = result.get("content", [{}])[0].get("text", "{}")
        usage = result.get("usage", {})
        return LLMResponse(
            content=content,
            prompt_tokens=usage.get("input_tokens", 0),
            completion_tokens=usage.get("output_tokens", 0),
            model=settings.AWS_BEDROCK_MODEL_ID,
        )
    except Exception as exc:
        logger.error("Bedrock call failed: %s", exc)
        raise


# ---------------------------------------------------------------------------
# Mock (deterministic, no API key needed)
# ---------------------------------------------------------------------------
def _call_mock(system_prompt: str, user_prompt: str) -> LLMResponse:
    """
    Fully dynamic mock — parses the prompt to extract resume skills, JD, and
    company name, then generates contextually relevant questions.
    Never invents technologies not found in the prompt.
    """
    prompt_lower = (system_prompt + " " + user_prompt).lower()

    if "professional_summary" in prompt_lower or "resume suggestion" in prompt_lower:
        content = json.dumps(_mock_suggestion_payload())
    elif "missing_keywords" in prompt_lower or "skill_gap_analysis" in prompt_lower:
        content = json.dumps(_mock_job_match_payload(user_prompt))
    elif "technical_questions" in prompt_lower or "interview question" in prompt_lower:
        content = json.dumps(_mock_questions_payload_dynamic(user_prompt))
    elif "technical_accuracy" in prompt_lower and "completeness" in prompt_lower:
        content = json.dumps(_mock_evaluation_payload())
    elif "overall_score" in prompt_lower and "strengths" in prompt_lower:
        content = json.dumps(_mock_result_payload())
    elif "resume coach" in prompt_lower or "candidate's resume" in prompt_lower or "ats score" in prompt_lower:
        # Chat mode — return plain text, not JSON
        content = _mock_chat_response(user_prompt)
    else:
        content = json.dumps({"result": "mock response"})

    return LLMResponse(content=content, model="mock", prompt_tokens=100, completion_tokens=400)


def _mock_suggestion_payload() -> dict:
    return {
        "professional_summary": (
            "Results-driven Software Engineer with 5+ years of experience designing and "
            "delivering scalable web applications using Python, React, and AWS. "
            "Proven track record of reducing system latency by 40% and leading cross-functional "
            "teams to ship features on time. Passionate about clean architecture and developer experience."
        ),
        "experience_bullets": [
            "Architected and deployed 15+ RESTful APIs using FastAPI, serving 50K+ daily active users with 99.9% uptime.",
            "Reduced application load time by 42% through React performance optimizations and CDN caching strategies.",
            "Led migration of monolithic application to microservices, cutting deployment frequency from weekly to daily.",
            "Mentored 3 junior engineers, conducting weekly code reviews that improved team code quality by 35%.",
            "Implemented CI/CD pipelines with GitHub Actions, reducing deployment time from 45 minutes to 8 minutes.",
        ],
        "keyword_improvements": [
            {"original": "worked on APIs", "improved": "engineered RESTful APIs", "reason": "Action verb + specificity"},
            {"original": "helped with deployments", "improved": "orchestrated Docker/Kubernetes deployments", "reason": "Quantify + use tech keywords"},
            {"original": "fixed bugs", "improved": "resolved 95% of P1 incidents within SLA", "reason": "Measurable outcome"},
        ],
        "grammar_corrections": [
            {"original": "Responsible for building", "corrected": "Built", "explanation": "Use active voice — stronger and more concise"},
            {"original": "Was involved in", "corrected": "Contributed to", "explanation": "Avoid passive constructs"},
        ],
        "skills_section": (
            "**Languages:** Python, JavaScript, TypeScript, SQL, Bash\n"
            "**Frameworks:** FastAPI, React, Node.js, Django\n"
            "**Cloud & DevOps:** AWS (Lambda, S3, DynamoDB, CloudWatch), Docker, Kubernetes, Terraform\n"
            "**Databases:** PostgreSQL, MySQL, Redis, DynamoDB\n"
            "**Tools:** Git, GitHub Actions, JIRA, Postman, VS Code"
        ),
        "missing_skills": ["Terraform", "Kubernetes", "TypeScript", "System Design", "GraphQL"],
        "formatting_suggestions": [
            "Use consistent date formats throughout (e.g. Jan 2021 – Present).",
            "Add a LinkedIn URL and GitHub profile to your contact section.",
            "Keep the resume to 1–2 pages — remove roles older than 10 years.",
            "Use bullet points for all experience entries — avoid paragraph blocks.",
            "Ensure section headers are clearly distinguished (bold, capitalized).",
        ],
        "industry_recommendations": [
            "For software engineering roles, highlight measurable impact in every bullet point.",
            "Include open-source contributions or side projects with GitHub links.",
            "Add AWS certifications prominently — they're highly valued for cloud roles.",
            "Tailor your summary for each job application to match the job title.",
            "Include a 'Key Achievements' or 'Projects' section to stand out.",
        ],
    }


def _mock_job_match_payload(prompt: str) -> dict:
    return {
        "overall_match": 72,
        "skills_match": 78,
        "experience_match": 70,
        "education_match": 85,
        "keyword_match": 65,
        "ats_compatibility": 74,
        "matching_skills": ["Python", "FastAPI", "React", "AWS", "Docker", "PostgreSQL", "Git", "CI/CD"],
        "missing_skills": ["Kubernetes", "Terraform", "TypeScript", "GraphQL", "Redis"],
        "missing_keywords": ["scalable", "microservices", "distributed systems", "on-call", "SLO"],
        "skill_gap_analysis": [
            {"skill": "Kubernetes", "gap": "Not mentioned in resume", "recommendation": "Add any K8s experience or take a certification"},
            {"skill": "Terraform", "gap": "IaC not demonstrated", "recommendation": "Highlight any infrastructure automation work"},
            {"skill": "TypeScript", "gap": "Only JavaScript listed", "recommendation": "Add TypeScript if you have experience with it"},
        ],
        "experience_gap": {
            "required_years": 5,
            "candidate_years": 4,
            "gap_notes": "Candidate is 1 year short of the requirement. Strong project portfolio can compensate."
        },
        "education_analysis": {
            "required": "Bachelor's in Computer Science or related field",
            "candidate": "B.Sc. Computer Science",
            "match": True,
            "notes": "Education requirements are fully met."
        },
        "recommendations": [
            "Add Kubernetes and Terraform to your skills section if you have any experience.",
            "Include keywords like 'microservices' and 'distributed systems' in your experience bullets.",
            "Quantify your AWS experience — mention specific services (Lambda, ECS, RDS).",
            "Add a section for certifications if you hold any AWS or cloud credentials.",
            "Tailor your professional summary to include the exact job title from the posting.",
        ],
    }


def _mock_questions_payload_dynamic(prompt: str = "") -> dict:
    """
    Fully dynamic mock question generator.
    Parses the prompt to extract:
      - resume skills
      - job description
      - company
      - candidate level
    Then generates ONLY questions relevant to those skills.
    Never generates questions for tech not present in the prompt.
    """
    p = prompt.lower()

    # ── Parse skills from prompt ──────────────────────────────────────────
    def _has(*keywords):
        return any(k in p for k in keywords)

    has_python  = _has("python")
    has_fastapi = _has("fastapi")
    has_django  = _has("django")
    has_flask   = _has("flask")
    has_react   = _has("react", "react.js")
    has_js      = _has("javascript", "typescript", "js ")
    has_aws     = _has("aws", "lambda", "s3 ", "ec2", "dynamodb", "cloudwatch")
    has_sql     = _has("sql", "postgresql", "mysql", "sqlite")
    has_mongo   = _has("mongodb", "nosql", "mongo")
    has_docker  = _has("docker")
    has_git     = _has("git", "github")
    has_rest    = _has("rest api", "restful", "rest")
    has_cicd    = _has("ci/cd", "github actions", "jenkins")
    has_k8s     = _has("kubernetes", "k8s")
    has_resume_analyzer = _has("resume analyzer", "ats score", "resume parser",
                               "skill extractor", "job match", "mock interview")

    # ── Company detection ────────────────────────────────────────────────
    company = ""
    for c in ["accenture", "infosys", "tcs", "wipro", "cognizant", "amazon", "google", "microsoft"]:
        if c in p:
            company = c
            break

    # ── Level detection ──────────────────────────────────────────────────
    is_junior = _has("associate", "junior", "entry level", "fresher", "graduate", "jr.")
    is_senior = _has("senior", "lead", "principal", "staff", "sr.")
    level = "Junior/Associate" if is_junior else "Senior" if is_senior else "Mid-level"

    # ── ID counter ───────────────────────────────────────────────────────
    _id = [1]
    def nxt():
        val = _id[0]; _id[0] += 1; return val

    # ── Question builder ─────────────────────────────────────────────────
    def q(question, cat, difficulty, tips, expected_answer, key_points, follow_up, keywords):
        return {
            "id": nxt(),
            "question": question,
            "category": cat,
            "difficulty": difficulty,
            "tips": tips,
            "expected_answer": expected_answer,
            "key_points": key_points,
            "follow_up_questions": follow_up,
            "expected_keywords": keywords,
        }

    # ── Technical (general — always include if docker/git/rest present) ──
    tech = []
    if has_rest:
        tech.append(q(
            "Explain the difference between GET, POST, PUT, and DELETE HTTP methods in REST APIs.",
            "technical", "easy",
            "Cover idempotency and when to use each.",
            "GET retrieves data, POST creates, PUT updates/replaces, DELETE removes. GET and DELETE are idempotent.",
            ["GET=read", "POST=create", "PUT=replace", "PATCH=partial update", "DELETE=remove", "idempotency"],
            ["What is the difference between PUT and PATCH?", "How do you handle REST API versioning?"],
            ["REST", "HTTP", "idempotent", "stateless", "CRUD"]
        ))
    if has_docker:
        tech.append(q(
            "What is Docker and how does containerization differ from traditional virtual machines?",
            "technical", "easy",
            "Explain layers, images, containers, and the lightweight nature of containers.",
            "Docker uses OS-level virtualisation via containers that share the host kernel, making them lighter than VMs which run a full OS.",
            ["image vs container", "Dockerfile", "layers", "kernel sharing", "docker-compose"],
            ["What is a Dockerfile?", "How do you reduce Docker image size?"],
            ["container", "image", "Dockerfile", "lightweight", "virtualisation"]
        ))
    if has_git:
        tech.append(q(
            "Explain the Git workflow you follow in a team environment. What is the difference between merge and rebase?",
            "technical", "easy" if is_junior else "medium",
            "Mention branching strategy, pull requests, and code review.",
            "Typical flow: feature branch → PR → code review → merge to main. Merge preserves history; rebase creates linear history.",
            ["feature branch", "pull request", "merge", "rebase", "linear history", "code review"],
            ["How do you resolve a merge conflict?", "What is git cherry-pick?"],
            ["branch", "merge", "rebase", "PR", "commit", "history"]
        ))
    if has_cicd:
        tech.append(q(
            "How does CI/CD improve software development? Walk me through a pipeline you have set up.",
            "technical", "medium",
            "Describe the stages: build, test, lint, deploy.",
            "CI runs automated tests on every commit; CD deploys passing builds automatically. Reduces manual errors and speeds delivery.",
            ["automated tests", "build stages", "deployment", "GitHub Actions", "rollback"],
            ["How do you handle a failed deployment?", "How do you manage secrets in CI/CD?"],
            ["CI/CD", "automated", "pipeline", "deploy", "test", "lint"]
        ))

    # ── Python questions ─────────────────────────────────────────────────
    python_qs = []
    if has_python:
        python_qs.append(q(
            "Explain the difference between a list and a tuple in Python. When would you use each?",
            "python", "easy",
            "Focus on mutability, performance, and use cases.",
            "Lists are mutable, tuples are immutable. Use tuples for fixed data (coordinates, DB records) and lists when you need to modify the collection.",
            ["mutable vs immutable", "performance", "hashable", "use cases"],
            ["Can a tuple contain mutable objects?", "What are named tuples?"],
            ["mutable", "immutable", "tuple", "list", "hashable"]
        ))
        python_qs.append(q(
            "What are Python decorators? Write a simple decorator that measures function execution time.",
            "python", "medium",
            "Show the @wraps decorator to preserve function metadata.",
            "A decorator is a function that takes another function, adds behaviour, and returns a new function. Use functools.wraps to preserve metadata.",
            ["closure", "@wraps", "functools", "wrapper", "higher-order function"],
            ["What is the difference between @property and a regular method?", "How do class decorators work?"],
            ["decorator", "wrapper", "functools", "wraps", "closure"]
        ))
    if has_fastapi:
        python_qs.append(q(
            "How does FastAPI handle request validation? What role does Pydantic play?",
            "python", "medium",
            "Mention Pydantic models, automatic docs, and type hints.",
            "FastAPI uses Pydantic models to validate incoming request data automatically. Invalid data returns a 422 error with field-level details. Type hints drive OpenAPI schema generation.",
            ["Pydantic", "type hints", "422 validation", "request body", "response model"],
            ["How do you handle optional fields in a Pydantic model?", "How does FastAPI compare to Flask for validation?"],
            ["Pydantic", "validation", "type hints", "422", "schema"]
        ))
        python_qs.append(q(
            "What is dependency injection in FastAPI? Give a real example from your project.",
            "python", "medium" if not is_junior else "hard",
            "Reference the Depends() system and how it handles DB sessions.",
            "FastAPI's Depends() injects shared resources (DB sessions, auth) into route handlers. This promotes reusability and testability.",
            ["Depends()", "DB session", "get_db", "reusability", "testability"],
            ["How do you test routes that use Depends()?", "How do you handle async dependencies?"],
            ["Depends", "inject", "db session", "middleware", "reusable"]
        ))

    # ── React questions ──────────────────────────────────────────────────
    react_qs = []
    if has_react:
        react_qs.append(q(
            "Explain the difference between useState and useEffect hooks in React.",
            "react", "easy",
            "Give a concrete example of when you'd use each.",
            "useState manages local component state; useEffect handles side effects (API calls, subscriptions, DOM updates) after render.",
            ["state management", "side effects", "dependency array", "cleanup", "re-render"],
            ["When does useEffect run with an empty dependency array?", "What is the cleanup function in useEffect?"],
            ["useState", "useEffect", "side effects", "dependency array", "re-render"]
        ))
        react_qs.append(q(
            "What is React's virtual DOM and how does reconciliation work?",
            "react", "medium",
            "Explain diffing and why keys matter in lists.",
            "React keeps a virtual DOM in memory and diffs it with the previous version. Only changed nodes are updated in the real DOM, improving performance.",
            ["diffing", "fiber", "keys", "reconciliation", "performance"],
            ["Why is using array index as a key bad practice?", "What is React.memo?"],
            ["Virtual DOM", "diffing", "reconciliation", "keys", "fiber"]
        ))
        if not is_junior:
            react_qs.append(q(
                "How do you optimise a React component that re-renders too frequently?",
                "react", "hard",
                "Mention React.memo, useMemo, useCallback, and profiling tools.",
                "Use React.memo to prevent re-renders if props haven't changed; useMemo for expensive calculations; useCallback for stable function references. Profile with React DevTools.",
                ["React.memo", "useMemo", "useCallback", "profiling", "shallow comparison"],
                ["What is the difference between useMemo and useCallback?", "When would you use React.lazy()?"],
                ["React.memo", "useMemo", "useCallback", "re-render", "performance"]
            ))

    # ── AWS questions ────────────────────────────────────────────────────
    aws_qs = []
    if has_aws:
        aws_qs.append(q(
            "What is AWS Lambda and what are its key benefits for backend development?",
            "aws", "easy",
            "Focus on serverless, auto-scaling, and cost model.",
            "Lambda runs code on-demand without provisioning servers. Auto-scales instantly, charges only for execution time, integrates natively with API Gateway, S3, and DynamoDB.",
            ["serverless", "auto-scaling", "cold start", "execution timeout", "pay-per-use"],
            ["What is a Lambda cold start and how do you mitigate it?", "What are Lambda layers?"],
            ["serverless", "auto-scale", "cold start", "API Gateway", "trigger"]
        ))
        aws_qs.append(q(
            "Explain the difference between S3 and DynamoDB. When would you use each for this project?",
            "aws", "medium",
            "S3=file/blob storage, DynamoDB=NoSQL key-value/document store.",
            "S3 is object storage for files (resumes, images). DynamoDB is a NoSQL database for structured JSON data with millisecond latency at scale.",
            ["object storage", "NoSQL", "key-value", "partition key", "sort key", "scalability"],
            ["How do you secure an S3 bucket?", "What is DynamoDB's single-table design?"],
            ["S3", "DynamoDB", "object storage", "NoSQL", "partition key"]
        ))
        if not is_junior:
            aws_qs.append(q(
                "How would you design a secure, scalable architecture for this Resume Analyzer app on AWS?",
                "aws", "hard",
                "Walk through each service and why you chose it.",
                "API Gateway → Lambda (FastAPI+Mangum) → S3 (resumes) + DynamoDB (results). Cognito for auth, CloudWatch for monitoring. CDK for IaC.",
                ["API Gateway", "Lambda", "S3", "DynamoDB", "Cognito", "CloudWatch", "CDK", "IAM"],
                ["How would you handle Lambda cold starts for the API?", "How do you manage secrets in Lambda?"],
                ["API Gateway", "Lambda", "S3", "DynamoDB", "Cognito", "IAM", "CloudWatch"]
            ))

    # ── Database questions ───────────────────────────────────────────────
    db_qs = []
    if has_sql:
        db_qs.append(q(
            "Explain the difference between INNER JOIN, LEFT JOIN, and RIGHT JOIN with a practical example.",
            "database", "easy",
            "Use a simple users/orders example.",
            "INNER JOIN returns rows with matches in both tables. LEFT JOIN returns all left rows + matched right. RIGHT JOIN is the reverse.",
            ["INNER JOIN", "LEFT JOIN", "NULL", "matching rows", "cartesian product"],
            ["When would you use a FULL OUTER JOIN?", "What is the difference between WHERE and HAVING?"],
            ["JOIN", "INNER", "LEFT", "NULL", "rows", "matching"]
        ))
        db_qs.append(q(
            "What is database indexing and when would you add an index to a column?",
            "database", "medium",
            "Cover B-tree structure, read vs write trade-off.",
            "Indexes speed up reads by creating a sorted data structure (B-tree). Add indexes on frequently queried or joined columns. Avoid over-indexing as it slows writes.",
            ["B-tree", "read speed", "write overhead", "query planner", "composite index", "EXPLAIN"],
            ["What is a covering index?", "How do you find slow queries in PostgreSQL?"],
            ["index", "B-tree", "read", "write", "query planner", "performance"]
        ))
    if has_mongo:
        db_qs.append(q(
            "What are the key differences between SQL and NoSQL databases? When would you choose MongoDB?",
            "database", "medium",
            "Compare schema, scalability, and use cases.",
            "SQL has fixed schema, ACID transactions, great for relational data. MongoDB is schema-flexible, scales horizontally, great for document/hierarchical data.",
            ["schema", "ACID", "horizontal scaling", "document model", "flexible"],
            ["What is a MongoDB index?", "How does MongoDB handle transactions?"],
            ["SQL", "NoSQL", "schema", "ACID", "document", "horizontal scaling"]
        ))

    # ── Project-specific questions ───────────────────────────────────────
    project_qs = []
    if has_resume_analyzer:
        project_qs = [
            q("Walk me through how your Resume Analyzer calculates the ATS score. What factors does it consider?",
              "project", "medium",
              "Cover the 6 scoring dimensions: contact info, sections, skills, quantified achievements, action verbs, formatting.",
              "The ATS scorer checks 6 weighted dimensions: contact info (10pts), key sections (20pts), skills/keywords (30pts), quantified achievements (15pts), action verbs (15pts), length/formatting (10pts).",
              ["weighted scoring", "contact info", "sections", "keywords", "action verbs", "formatting"],
              ["How would you improve the ATS scoring algorithm?", "How do you handle resumes in different formats?"],
              ["ATS", "weighted", "scoring", "sections", "keywords"]
            ),
            q("Explain how your resume parser handles both PDF and DOCX files. What libraries do you use?",
              "project", "easy",
              "Mention pdfplumber, PyPDF2, python-docx and the fallback chain.",
              "PDF files are parsed with pdfplumber (primary) with PyPDF2 as fallback. DOCX uses python-docx to extract paragraphs and table text. Both fall back to plain text decoding.",
              ["pdfplumber", "python-docx", "fallback chain", "text extraction", "file bytes"],
              ["How do you handle scanned PDFs?", "What happens if the PDF is corrupted?"],
              ["pdfplumber", "python-docx", "PyPDF2", "text extraction", "fallback"]
            ),
            q("How is authentication implemented in your Resume Analyzer? Walk through the login flow.",
              "project", "medium",
              "Mention JWT, bcrypt, access/refresh tokens, and the FastAPI OAuth2 flow.",
              "User logs in → bcrypt verifies password → create JWT access token (30min) + refresh token (7 days) → frontend stores in localStorage → each request sends Bearer token in Authorization header.",
              ["JWT", "bcrypt", "access token", "refresh token", "OAuth2", "Bearer"],
              ["How do you invalidate a JWT on logout?", "Why did you choose JWT over session-based auth?"],
              ["JWT", "bcrypt", "access token", "refresh token", "Bearer", "401"]
            ),
        ]
    else:
        # Generic project question based on resume
        project_qs = [
            q(f"Walk me through your most complex project. What was the architecture and what challenges did you solve?",
              "project", "hard",
              "Use STAR method: Situation, Task, Action, Result. Quantify the impact.",
              "A strong answer covers the problem, your specific technical decisions, any challenges overcome, and measurable outcomes (performance improvement, users served, cost saved).",
              ["architecture", "trade-offs", "scalability", "outcome", "impact"],
              ["What would you do differently now?", "How did you handle testing for this project?"],
              ["architecture", "trade-offs", "impact", "scalability", "challenges"]
            ),
        ]

    # ── Behavioral questions ─────────────────────────────────────────────
    behavioral = [
        q("Tell me about a time you faced a challenging technical problem. How did you approach solving it?",
          "behavioral", "medium",
          "Use the STAR method. Focus on your problem-solving process, not just the outcome.",
          "Describe a specific technical challenge, your systematic approach to debugging/solving, resources used, and the successful resolution with impact.",
          ["STAR method", "problem-solving", "debugging approach", "collaboration", "outcome"],
          ["What would you do differently?", "How did it affect the team?"],
          ["STAR", "problem", "approach", "debugging", "outcome"]
        ),
        q("Describe a situation where you had to learn a new technology quickly. How did you do it?",
          "behavioral", "easy",
          "Show your learning strategy, resourcefulness, and adaptability.",
          "Describe the technology, your learning approach (docs, tutorials, projects), timeline, and how you applied it successfully.",
          ["learning strategy", "documentation", "side projects", "adaptability", "resourcefulness"],
          ["How do you stay current with new technologies?", "What resources do you use to learn?"],
          ["learning", "adaptability", "documentation", "practice", "timeline"]
        ),
    ]
    if company == "accenture":
        behavioral.append(q(
            "Accenture values client relationships. Tell me about a time you communicated a complex technical concept to a non-technical stakeholder.",
            "behavioral", "medium",
            "Use concrete example — avoid jargon, show empathy and clarity.",
            "Describe the stakeholder, the technical concept, how you simplified the explanation using analogies or visuals, and the positive outcome.",
            ["simplification", "analogies", "empathy", "clear communication", "outcome"],
            ["How do you handle a stakeholder who disagrees with your technical recommendation?"],
            ["communication", "simplify", "stakeholder", "clarity", "non-technical"]
        ))

    # ── HR questions ────────────────────────────────────────────────────
    role_name = "Associate Software Engineer" if is_junior else "Software Engineer"
    hr_qs = [
        q(f"Why are you applying for the {role_name} position? What excites you about this role?",
          "hr", "easy",
          "Be specific about the role, company, and how it aligns with your goals.",
          "A strong answer connects your skills to the role requirements, shows genuine interest in the company/product, and ties to your career goals.",
          ["role alignment", "career goals", "company values", "genuine interest"],
          ["Where do you see yourself in 3 years?"],
          ["motivation", "career", "growth", "role", "company"]
        ),
        q("What are your greatest strengths as a developer, and how have you applied them recently?",
          "hr", "easy",
          "Give a specific example for each strength — avoid generic answers.",
          "Name 2-3 specific technical or soft skills, then provide concrete examples of how you applied them with measurable outcomes.",
          ["specific examples", "measurable outcomes", "self-awareness", "relevance to role"],
          ["What is one area you are actively improving?"],
          ["strengths", "examples", "outcomes", "skills", "relevant"]
        ),
    ]

    result = {
        "technical_questions":  tech if tech else [],
        "behavioral_questions": behavioral,
        "hr_questions":         hr_qs,
        "project_questions":    project_qs,
        "aws_questions":        aws_qs if has_aws else [],
        "python_questions":     python_qs if has_python else [],
        "react_questions":      react_qs if has_react else [],
        "database_questions":   db_qs if (has_sql or has_mongo) else [],
    }

    total = sum(len(v) for v in result.values())
    result["total"] = total
    return result



def _mock_chat_response(prompt: str) -> str:
    """Return context-aware plain text chat responses for mock mode."""
    p = prompt.lower()

    if any(kw in p for kw in ["improve", "better", "enhance"]):
        return (
            "Here are my top suggestions to improve your resume:\n\n"
            "• **Quantify achievements** — Add numbers to every bullet (e.g., 'Reduced API latency by 40%')\n"
            "• **Strong action verbs** — Start each bullet with: Built, Engineered, Delivered, Led\n"
            "• **Tailor per role** — Mirror keywords from each job description\n"
            "• **Professional summary** — Add a 2-3 sentence summary highlighting your value\n"
            "• **Contact info** — Ensure email, phone, LinkedIn, and GitHub are visible at the top"
        )
    if any(kw in p for kw in ["missing skill", "skill gap", "what skill"]):
        return (
            "Based on your resume, consider adding these skills:\n\n"
            "• **Kubernetes** — Increasingly required for backend/devops roles\n"
            "• **TypeScript** — Standard in modern React/Node.js projects\n"
            "• **System Design** — Mention any architecture decisions you've made\n"
            "• **CI/CD** — Highlight any GitHub Actions or Jenkins pipelines you've built\n\n"
            "Add any of these you have experience with, even from side projects."
        )
    if any(kw in p for kw in ["rewrite", "summary", "objective"]):
        return (
            "Here's a rewritten professional summary:\n\n"
            "---\n"
            "Results-driven Software Engineer with hands-on experience building full-stack web applications "
            "using Python, React, FastAPI, and AWS. Proven ability to design scalable REST APIs, implement "
            "authentication systems, and optimize database performance. Passionate about clean architecture "
            "and delivering measurable business impact.\n"
            "---\n\n"
            "Ask me to adjust the tone, length, or target role."
        )
    if any(kw in p for kw in ["project", "side project", "portfolio"]):
        return (
            "Here are 5 project ideas tailored to your skill set:\n\n"
            "• **URL Shortener with Analytics** — FastAPI + React + PostgreSQL + Redis\n"
            "• **Job Board Scraper** — Python + FastAPI + Beautiful Soup + React dashboard\n"
            "• **Expense Tracker PWA** — React + FastAPI + SQLAlchemy + Chart.js\n"
            "• **Resume Parser CLI** — Python + pdfplumber + click (open source it!)\n"
            "• **Real-time Chat App** — FastAPI WebSockets + React + PostgreSQL\n\n"
            "Each can be completed in 1-2 weeks and makes a strong portfolio piece."
        )
    if any(kw in p for kw in ["interview", "question", "prepare"]):
        return (
            "Here are 5 personalised interview questions:\n\n"
            "1. **[Technical]** Explain FastAPI's dependency injection. Show a real example.\n"
            "2. **[Python]** What are async/await and when would you use them in FastAPI?\n"
            "3. **[React]** Explain useState vs useReducer. When would you choose each?\n"
            "4. **[AWS]** How would you design a serverless file upload flow using S3 + Lambda?\n"
            "5. **[Behavioral]** Describe a production bug you fixed. Walk me through your debugging process.\n\n"
            "Want questions for a specific role or technology?"
        )
    if any(kw in p for kw in ["ats", "score", "explain"]):
        return (
            "Your ATS score reflects how well your resume is parsed and ranked by Applicant Tracking Systems.\n\n"
            "**The 6 scoring dimensions:**\n"
            "• **Contact Info (10 pts)** — Email, phone, LinkedIn visibility\n"
            "• **Key Sections (20 pts)** — Experience, Education, Skills clearly labeled\n"
            "• **Skills & Keywords (30 pts)** — Match with job description keywords\n"
            "• **Quantified Achievements (15 pts)** — Numbers and metrics in bullets\n"
            "• **Action Verbs (15 pts)** — Strong verbs starting each bullet\n"
            "• **Formatting (10 pts)** — Length, bullet usage, clean structure\n\n"
            "To push your score above 80: add more quantified achievements and mirror the exact keywords from job postings."
        )
    if any(kw in p for kw in ["career", "path", "role", "switch"]):
        return (
            "Based on your skill set, here are strong career directions:\n\n"
            "• **Full Stack Engineer** — Your Python + React combo is ideal for product companies\n"
            "• **Backend Engineer** — Deepen FastAPI + PostgreSQL + AWS for high-demand backend roles\n"
            "• **Cloud/DevOps Engineer** — Expand with Kubernetes + Terraform + AWS certifications\n"
            "• **Technical Lead** — With 3-4 more years, your stack positions you well for lead roles\n"
            "• **Solutions Architect** — AWS SA-Associate → Professional is a clear path\n\n"
            "Which direction interests you? I can outline specific next steps."
        )
    if any(kw in p for kw in ["hello", "hi", "hey", "help", "start"]):
        return (
            "Hello! 👋 I'm your AI Resume Coach. I've loaded your resume and I'm ready to help.\n\n"
            "**Here's what I can do:**\n"
            "• Improve your resume section by section\n"
            "• Identify missing skills for your target role\n"
            "• Rewrite your summary or experience bullets\n"
            "• Suggest projects to strengthen your portfolio\n"
            "• Generate interview questions\n"
            "• Explain your ATS score\n"
            "• Suggest career paths\n\n"
            "What would you like to work on first?"
        )
    return (
        "I've reviewed your resume and I'm happy to help with that. "
        "Could you be more specific? I can help with improving your resume, "
        "identifying missing skills, rewriting sections, suggesting projects, "
        "generating interview questions, or exploring career paths."
    )


def _mock_evaluation_payload() -> dict:
    return {
        "score": 72.0,
        "technical_accuracy": 75.0,
        "communication": 70.0,
        "completeness": 68.0,
        "feedback": (
            "Good answer that covers the core concepts. You correctly identified the main components "
            "and demonstrated practical understanding. To improve, add a concrete example from your "
            "experience and quantify the impact. Your communication was clear but could be more structured."
        ),
        "ideal_answer": (
            "An ideal answer would: (1) define the core concept clearly in 1-2 sentences, "
            "(2) explain how you've applied it in practice with a specific example, "
            "(3) mention trade-offs or alternatives, and (4) conclude with the measurable outcome."
        ),
        "keywords_used": ["API", "scalable", "performance"],
        "keywords_missed": ["trade-offs", "benchmarks", "monitoring"],
    }


def _mock_result_payload() -> dict:
    return {
        "overall_score": 74.5,
        "technical_score": 76.0,
        "communication_score": 73.0,
        "confidence_score": 72.0,
        "grammar_score": 80.0,
        "strengths": [
            "Strong technical knowledge in backend development",
            "Clear and structured communication style",
            "Good understanding of cloud architecture concepts",
        ],
        "weaknesses": [
            "Answers could be more concise — aim for 2-3 minutes per question",
            "Could provide more quantified examples from past experience",
            "Some behavioral answers lacked specific outcomes",
        ],
        "improvements": [
            "Use the STAR method for every behavioral question",
            "Prepare 3-4 quantified achievement stories in advance",
            "Practice system design questions with whiteboards",
            "Study AWS services more deeply — focus on Lambda, ECS, and RDS",
        ],
        "overall_feedback": (
            "Strong overall performance. You demonstrated solid technical fundamentals and "
            "communicated your experience clearly. The main areas to improve are adding more "
            "measurable outcomes to your answers and being more concise. With focused preparation "
            "on the identified gaps, you'd be well-positioned for this role."
        ),
    }


def parse_json_response(content: str) -> dict:
    """Safely parse LLM JSON response, handling markdown code fences."""
    content = content.strip()
    # Strip ```json ... ``` fences if present
    content = re.sub(r"^```(?:json)?\s*", "", content, flags=re.MULTILINE)
    content = re.sub(r"\s*```$", "", content, flags=re.MULTILINE)
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Try to extract first JSON object
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        logger.error("Failed to parse LLM JSON: %s…", content[:200])
        return {}
