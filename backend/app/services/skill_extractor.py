"""
Skills extraction from resume text using keyword matching and optional spaCy NER.
"""
import logging
import re
from typing import List, Set

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Master skills taxonomy (curated, grouped by domain)
# ---------------------------------------------------------------------------
SKILLS_TAXONOMY: dict[str, list[str]] = {
    "programming_languages": [
        "Python", "JavaScript", "TypeScript", "Java", "C", "C++", "C#", "Go",
        "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB",
        "Perl", "Dart", "Lua", "Haskell", "Elixir", "Clojure", "F#",
    ],
    "web_frontend": [
        "React", "Vue", "Angular", "Svelte", "Next.js", "Nuxt.js", "Gatsby",
        "HTML", "CSS", "SASS", "SCSS", "Tailwind CSS", "Bootstrap", "Material UI",
        "Redux", "Vuex", "GraphQL", "REST API", "WebSockets", "jQuery",
    ],
    "web_backend": [
        "Node.js", "Express", "FastAPI", "Django", "Flask", "Spring Boot",
        "ASP.NET", "Laravel", "Rails", "Gin", "Fiber", "NestJS",
    ],
    "databases": [
        "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis", "Elasticsearch",
        "DynamoDB", "Cassandra", "Oracle", "SQL Server", "CouchDB", "Neo4j",
        "Firestore", "Supabase", "PlanetScale", "SQL", "NoSQL",
    ],
    "cloud_devops": [
        "AWS", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes", "Terraform",
        "Ansible", "Jenkins", "GitHub Actions", "GitLab CI", "CircleCI",
        "CloudFormation", "CDK", "Helm", "Prometheus", "Grafana", "Datadog",
        "New Relic", "Nginx", "Apache", "Linux", "Bash", "Shell scripting",
    ],
    "data_ml": [
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
        "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas", "NumPy",
        "Matplotlib", "Seaborn", "Jupyter", "Spark", "Hadoop", "Airflow",
        "MLflow", "Hugging Face", "OpenCV", "NLTK", "spaCy", "LangChain",
        "Data Analysis", "Data Science", "Statistics", "A/B Testing",
    ],
    "tools": [
        "Git", "GitHub", "GitLab", "Bitbucket", "JIRA", "Confluence",
        "Figma", "Postman", "VS Code", "IntelliJ", "Vim", "Linux", "macOS",
        "Windows", "Webpack", "Vite", "Babel", "ESLint", "Prettier",
    ],
    "methodologies": [
        "Agile", "Scrum", "Kanban", "TDD", "BDD", "CI/CD", "DevOps",
        "Microservices", "Serverless", "Domain-Driven Design", "SOLID",
        "Design Patterns", "Code Review", "Pair Programming",
    ],
    "soft_skills": [
        "Leadership", "Communication", "Teamwork", "Problem Solving",
        "Critical Thinking", "Project Management", "Mentoring",
        "Time Management", "Collaboration",
    ],
}

# Flat lookup: lowercase → canonical name
_SKILL_INDEX: dict[str, str] = {}
for _skills in SKILLS_TAXONOMY.values():
    for _skill in _skills:
        _SKILL_INDEX[_skill.lower()] = _skill


def extract_skills(text: str) -> List[str]:
    """
    Extract skills from resume text.
    Uses case-insensitive whole-word matching against the skills taxonomy.
    """
    found: Set[str] = set()
    text_lower = text.lower()

    for skill_lower, canonical in _SKILL_INDEX.items():
        # Escape special regex chars and use word boundaries
        pattern = r"\b" + re.escape(skill_lower) + r"\b"
        if re.search(pattern, text_lower):
            found.add(canonical)

    # Sort alphabetically for deterministic output
    return sorted(found)


def find_missing_skills(found_skills: List[str], job_description: str = "") -> List[str]:
    """
    Identify skills that appear in the job description but are absent from the resume.
    If no job description is given, return common in-demand skills not in the resume.
    """
    if job_description.strip():
        jd_skills = set(extract_skills(job_description))
        resume_skills = set(found_skills)
        missing = jd_skills - resume_skills
    else:
        # Default: common high-demand skills not found
        DEFAULT_IMPORTANT = [
            "Python", "JavaScript", "SQL", "Git", "Docker", "AWS",
            "React", "Node.js", "PostgreSQL", "Kubernetes", "CI/CD",
            "Agile", "REST API", "TypeScript", "Linux",
        ]
        resume_lower = {s.lower() for s in found_skills}
        missing = {s for s in DEFAULT_IMPORTANT if s.lower() not in resume_lower}

    return sorted(missing)[:20]  # Cap at 20 to avoid overwhelming the user
