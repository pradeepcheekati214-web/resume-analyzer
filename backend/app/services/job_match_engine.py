"""
Job Match engine — deterministic scoring + optional LLM enrichment.

Scoring weights:
  Skills Match      40%
  Keyword Match     30%
  Experience Match  20%
  ATS Compatibility 10%
  Overall = weighted average of above 4
  Education is reported separately (doesn't affect overall)
"""
import logging
import re
from typing import List

from app.services.ai_client import call_llm, parse_json_response
from app.services.skill_extractor import extract_skills

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert technical recruiter. Analyze resume vs job description.
Return ONLY valid JSON — no markdown, no explanation."""


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def analyze_job_match(
    resume_text: str,
    job_description: str,
    resume_skills: List[str],
) -> dict:
    """
    Step 1 — compute all numeric scores deterministically (never 0 unless truly 0).
    Step 2 — call LLM for text-only enrichment (gap analysis, recommendations).
    Step 3 — merge and return.
    """
    # ── Deterministic scores ─────────────────────────────────────────────
    jd_skills   = extract_skills(job_description)
    matching    = [s for s in resume_skills if s in jd_skills]
    missing     = [s for s in jd_skills    if s not in resume_skills]

    skills_match   = _skills_score(resume_skills, jd_skills, matching)
    keyword_match  = _keyword_score(resume_text, job_description)
    exp_match      = _experience_score(resume_text, job_description)
    ats_score      = _ats_score(resume_text, resume_skills, jd_skills)
    edu_match      = _education_score(resume_text, job_description)

    overall = round(
        skills_match  * 0.40 +
        keyword_match * 0.30 +
        exp_match     * 0.20 +
        ats_score     * 0.10,
        1,
    )

    base = {
        "overall_match":     overall,
        "skills_match":      round(skills_match,  1),
        "experience_match":  round(exp_match,     1),
        "education_match":   round(edu_match,     1),
        "keyword_match":     round(keyword_match, 1),
        "ats_compatibility": round(ats_score,     1),
        "matching_skills":   matching,
        "missing_skills":    missing[:15],
        "missing_keywords":  [],
        "skill_gap_analysis": [],
        "experience_gap":    {},
        "education_analysis": {},
        "recommendations":   [],
    }

    # ── LLM enrichment (text fields only) ───────────────────────────────
    try:
        enriched = _llm_enrich(
            resume_text=resume_text,
            job_description=job_description,
            matching=matching,
            missing=missing,
            scores=base,
        )
        # Only overwrite text fields — never overwrite numeric scores
        for key in (
            "missing_keywords", "skill_gap_analysis",
            "experience_gap", "education_analysis", "recommendations",
        ):
            val = enriched.get(key)
            if val:
                base[key] = val
    except Exception as exc:
        logger.warning("LLM enrichment failed (non-fatal): %s", exc)

    return base


# ---------------------------------------------------------------------------
# Deterministic scoring functions
# ---------------------------------------------------------------------------
def _skills_score(resume_skills: list, jd_skills: list, matching: list) -> float:
    """Percentage of JD-required skills found in resume."""
    if not jd_skills:
        # No skills detected in JD — score based on resume breadth
        return min(len(resume_skills) * 5, 80)
    return round(len(matching) / len(jd_skills) * 100, 1)


def _keyword_score(resume_text: str, job_description: str) -> float:
    """
    Bag-of-words overlap between resume and JD.
    Uses content words (length >= 4) to avoid noise from stop-words.
    """
    def _words(text: str):
        return {
            w.lower() for w in re.findall(r'\b[a-zA-Z]{4,}\b', text)
            if w.lower() not in _STOPWORDS
        }

    resume_words = _words(resume_text)
    jd_words     = _words(job_description)

    if not jd_words:
        return 50.0

    overlap = resume_words & jd_words
    # Jaccard-like score weighted toward JD coverage
    score = len(overlap) / len(jd_words) * 100
    return round(min(score, 100), 1)


def _experience_score(resume_text: str, job_description: str) -> float:
    """
    Estimate experience match based on years mentioned in JD vs resume.
    Falls back to section-presence heuristic.
    """
    required = _extract_years(job_description)
    candidate = _extract_years(resume_text)

    if required and candidate:
        if candidate >= required:
            return 100.0
        ratio = candidate / required
        return round(min(ratio * 100, 95), 1)

    # Heuristic: presence of experience/work sections
    has_exp = bool(re.search(
        r'\b(experience|work history|employment|engineer|developer|analyst)\b',
        resume_text, re.IGNORECASE
    ))
    jd_level = _detect_level(job_description)

    if not has_exp:
        return 30.0
    if jd_level == "senior":
        return 65.0
    if jd_level == "junior":
        return 85.0
    return 70.0


def _ats_score(resume_text: str, resume_skills: list, jd_skills: list) -> float:
    """
    ATS compatibility: checks formatting signals and keyword density.
    """
    score = 50.0

    # Has contact info
    if re.search(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}', resume_text):
        score += 10
    # Has key sections
    if re.search(r'\b(experience|education|skills)\b', resume_text, re.IGNORECASE):
        score += 10
    # Has bullet points
    if len(re.findall(r'[•\-\*] ', resume_text)) >= 5:
        score += 10
    # Skill keyword density
    if jd_skills:
        density = len([s for s in resume_skills if s in jd_skills]) / max(len(jd_skills), 1)
        score += density * 20

    return round(min(score, 100), 1)


def _education_score(resume_text: str, job_description: str) -> float:
    """Check if education level in resume matches JD requirement."""
    degree_levels = {
        "phd": 4, "doctorate": 4,
        "master": 3, "m.sc": 3, "m.s.": 3, "mba": 3,
        "bachelor": 2, "b.sc": 2, "b.s.": 2, "b.e": 2, "b.tech": 2,
        "associate": 1, "diploma": 1,
    }

    def _max_level(text):
        text_lower = text.lower()
        found = [v for k, v in degree_levels.items() if k in text_lower]
        return max(found) if found else 0

    resume_level = _max_level(resume_text)
    jd_level     = _max_level(job_description)

    if jd_level == 0:
        return 80.0    # JD doesn't specify — assume fine
    if resume_level == 0:
        return 40.0    # Resume mentions no degree
    if resume_level >= jd_level:
        return 100.0
    gap = jd_level - resume_level
    return round(max(100 - gap * 25, 30), 1)


# ---------------------------------------------------------------------------
# LLM enrichment — text fields only, scores never touched
# ---------------------------------------------------------------------------
def _llm_enrich(
    resume_text: str,
    job_description: str,
    matching: list,
    missing: list,
    scores: dict,
) -> dict:
    prompt = f"""Analyze this resume vs job description.

RESUME (first 1500 chars): {resume_text[:1500]}
JOB DESCRIPTION (first 1500 chars): {job_description[:1500]}
MATCHING SKILLS: {', '.join(matching[:15])}
MISSING SKILLS: {', '.join(missing[:15])}
COMPUTED SCORES: overall={scores['overall_match']}%, skills={scores['skills_match']}%, experience={scores['experience_match']}%

Return ONLY a JSON object with these keys (no scores — they are already computed):
{{
  "missing_keywords": ["kw1", "kw2", ...],
  "skill_gap_analysis": [{{"skill": "...", "gap": "...", "recommendation": "..."}}],
  "experience_gap": {{"required_years": <float|null>, "candidate_years": <float|null>, "gap_notes": "..."}},
  "education_analysis": {{"required": "...", "candidate": "...", "match": <bool>, "notes": "..."}},
  "recommendations": ["rec1", "rec2", "rec3", "rec4", "rec5"]
}}"""

    response = call_llm(SYSTEM_PROMPT, prompt)
    return parse_json_response(response.content)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _extract_years(text: str):
    """Extract the largest 'N years' number mentioned in text."""
    matches = re.findall(
        r'(\d+)\+?\s*(?:years?|yrs?)(?:\s+of)?\s*(?:experience|exp)?',
        text, re.IGNORECASE,
    )
    if not matches:
        return None
    return max(int(m) for m in matches)


def _detect_level(text: str) -> str:
    text_lower = text.lower()
    if any(w in text_lower for w in ['senior', 'lead', 'principal', 'staff', 'sr.']):
        return 'senior'
    if any(w in text_lower for w in ['junior', 'entry', 'associate', 'jr.']):
        return 'junior'
    return 'mid'


_STOPWORDS = {
    'that', 'this', 'with', 'from', 'have', 'will', 'your', 'they',
    'been', 'more', 'when', 'what', 'some', 'also', 'into', 'than',
    'then', 'them', 'these', 'such', 'each', 'which', 'their', 'there',
    'able', 'about', 'across', 'after', 'against', 'along', 'among',
    'around', 'before', 'being', 'between', 'both', 'come', 'could',
    'does', 'during', 'either', 'every', 'following', 'further',
    'given', 'good', 'great', 'help', 'here', 'high', 'however',
    'include', 'including', 'itself', 'just', 'keep', 'knowledge',
    'large', 'like', 'long', 'look', 'make', 'many', 'most', 'much',
    'must', 'need', 'never', 'next', 'only', 'other', 'over', 'part',
    'plus', 'provide', 'required', 'role', 'same', 'should', 'since',
    'strong', 'take', 'through', 'time', 'together', 'under', 'used',
    'using', 'various', 'very', 'want', 'well', 'were', 'where',
    'while', 'within', 'work', 'would', 'year', 'years',
}
