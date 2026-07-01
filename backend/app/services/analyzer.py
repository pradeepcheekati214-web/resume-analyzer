"""
Main analysis orchestrator — combines parsing, skills extraction, ATS scoring, suggestions.
"""
import logging
from typing import Tuple

from app.services.resume_parser import parse_resume
from app.services.skill_extractor import extract_skills, find_missing_skills
from app.services.ats_scorer import calculate_ats_score
from app.services.suggestion_engine import generate_suggestions

logger = logging.getLogger(__name__)


def analyze_resume(
    file_bytes: bytes,
    filename: str,
    job_description: str = "",
) -> Tuple[dict, str, int, int]:
    """
    Full resume analysis pipeline.

    Returns: (analysis_data, raw_text, word_count, page_count)
      - analysis_data: dict ready to be stored in DB
      - raw_text, word_count, page_count: for Resume record
    """
    # 1. Parse
    parsed = parse_resume(file_bytes, filename)

    # 2. Extract skills
    skills = extract_skills(parsed.raw_text)
    missing = find_missing_skills(skills, job_description)

    # 3. Score
    scoring = calculate_ats_score(
        text=parsed.raw_text,
        skills_found=skills,
        missing_skills=missing,
        job_description=job_description,
        contact_info=parsed.contact_info,
    )

    # 4. Generate suggestions
    suggestions = generate_suggestions(
        text=parsed.raw_text,
        skills_found=skills,
        missing_skills=missing,
        score_breakdown=scoring.breakdown,
        contact_info=parsed.contact_info,
    )

    # Assemble analysis result
    analysis_data = {
        "status": "completed",
        "ats_score": scoring.total_score,
        "score_breakdown": scoring.breakdown,
        "skills_found": skills,
        "missing_skills": missing,
        "keywords_matched": scoring.keywords_matched,
        "contact_info": parsed.contact_info,
        "suggestions": suggestions,
        "skills_count": len(skills),
        "missing_count": len(missing),
    }

    return (
        analysis_data,
        parsed.raw_text,
        parsed.word_count,
        parsed.page_count,
    )
