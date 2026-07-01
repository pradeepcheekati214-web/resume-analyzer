"""
ATS scoring algorithm.

Scores a resume across multiple dimensions and returns a 0–100 composite score.
"""
import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List

logger = logging.getLogger(__name__)


@dataclass
class ScoringResult:
    total_score: float = 0.0
    breakdown: Dict[str, dict] = field(default_factory=dict)
    keywords_matched: int = 0


# ---------------------------------------------------------------------------
# Section detection patterns
# ---------------------------------------------------------------------------
SECTION_PATTERNS = {
    "experience": re.compile(
        r"\b(experience|work history|employment|professional background|career)\b",
        re.IGNORECASE,
    ),
    "education": re.compile(
        r"\b(education|academic|degree|university|college|bachelor|master|phd)\b",
        re.IGNORECASE,
    ),
    "skills": re.compile(
        r"\b(skills|technologies|technical skills|competencies|expertise|proficiency)\b",
        re.IGNORECASE,
    ),
    "contact": re.compile(
        r"\b(contact|email|phone|linkedin|github|address|location)\b",
        re.IGNORECASE,
    ),
    "summary": re.compile(
        r"\b(summary|objective|profile|about me|overview)\b",
        re.IGNORECASE,
    ),
    "certifications": re.compile(
        r"\b(certifications?|certificates?|licenses?|credentials?)\b",
        re.IGNORECASE,
    ),
    "projects": re.compile(
        r"\b(projects?|portfolio|open.?source|personal projects?)\b",
        re.IGNORECASE,
    ),
}

# Action verbs that indicate strong bullet points
ACTION_VERBS = {
    "achieved", "built", "created", "delivered", "designed", "developed",
    "drove", "engineered", "established", "executed", "improved", "increased",
    "launched", "led", "managed", "optimized", "produced", "reduced",
    "resolved", "scaled", "shipped", "spearheaded", "streamlined",
}

# Quantification patterns (numbers/percentages in context)
QUANTIFICATION_PATTERN = re.compile(
    r"\b\d+[\w%+]*\s*(percent|%|x|times|million|billion|thousand|users|customers|"
    r"hours|days|weeks|months|ms|seconds|kb|mb|gb|tb)?\b",
    re.IGNORECASE,
)


def calculate_ats_score(
    text: str,
    skills_found: List[str],
    missing_skills: List[str],
    job_description: str = "",
    contact_info: dict = None,
) -> ScoringResult:
    """
    Calculate an ATS score with a breakdown across 6 weighted dimensions.

    Dimensions & weights:
      1. Contact Information  — 10 pts
      2. Key Sections         — 20 pts
      3. Skills & Keywords    — 30 pts
      4. Quantified Achievements — 15 pts
      5. Action Verbs         — 15 pts
      6. Length & Formatting  — 10 pts
    """
    contact_info = contact_info or {}
    result = ScoringResult()

    # ── 1. Contact Info (10 pts) ──────────────────────────────────────────
    contact_score = 0
    if contact_info.get("email"):  contact_score += 4
    if contact_info.get("phone"):  contact_score += 3
    if contact_info.get("name"):   contact_score += 2
    if contact_info.get("linkedin") or contact_info.get("github"):
        contact_score += 1
    result.breakdown["contact_info"] = {"score": contact_score, "max": 10}

    # ── 2. Key Sections (20 pts) ─────────────────────────────────────────
    section_score = 0
    section_weights = {
        "experience": 7, "education": 5, "skills": 5,
        "summary": 2, "projects": 1,
    }
    for section, weight in section_weights.items():
        if SECTION_PATTERNS[section].search(text):
            section_score += weight
    result.breakdown["key_sections"] = {"score": min(section_score, 20), "max": 20}

    # ── 3. Skills & Keywords (30 pts) ────────────────────────────────────
    total_skills = len(skills_found) + len(missing_skills)
    if total_skills > 0:
        skill_ratio = len(skills_found) / total_skills
    else:
        skill_ratio = 0.5

    # Keyword matching against JD
    keywords_matched = 0
    if job_description.strip() and skills_found:
        jd_lower = job_description.lower()
        keywords_matched = sum(1 for s in skills_found if s.lower() in jd_lower)
        jd_bonus = min(keywords_matched * 2, 10)
    else:
        jd_bonus = 0

    skills_score = min(int(skill_ratio * 20) + jd_bonus, 30)
    result.keywords_matched = keywords_matched
    result.breakdown["skills_keywords"] = {"score": skills_score, "max": 30}

    # ── 4. Quantified Achievements (15 pts) ──────────────────────────────
    quantification_matches = QUANTIFICATION_PATTERN.findall(text)
    quant_score = min(len(quantification_matches) * 2, 15)
    result.breakdown["quantified_achievements"] = {"score": quant_score, "max": 15}

    # ── 5. Action Verbs (15 pts) ─────────────────────────────────────────
    words_lower = set(re.findall(r"\b\w+\b", text.lower()))
    action_verb_count = len(ACTION_VERBS & words_lower)
    action_score = min(action_verb_count * 2, 15)
    result.breakdown["action_verbs"] = {"score": action_score, "max": 15}

    # ── 6. Length & Formatting (10 pts) ──────────────────────────────────
    word_count = len(text.split())
    format_score = 0
    if 300 <= word_count <= 1200:
        format_score += 6          # Ideal length
    elif 200 <= word_count < 300 or 1200 < word_count <= 1800:
        format_score += 3          # Acceptable
    else:
        format_score += 1          # Too short or very long

    # Bullet point usage
    bullet_count = len(re.findall(r"[•\-\*] ", text))
    if bullet_count >= 10:
        format_score += 4
    elif bullet_count >= 5:
        format_score += 2

    result.breakdown["length_formatting"] = {"score": min(format_score, 10), "max": 10}

    # ── Total ─────────────────────────────────────────────────────────────
    total = sum(v["score"] for v in result.breakdown.values())
    result.total_score = round(min(total, 100), 1)

    return result
