"""
AI Resume Suggestion engine — generates LLM-powered resume improvements.
"""
import logging
from typing import Optional

from app.services.ai_client import call_llm, parse_json_response

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert resume coach and career advisor with 15 years of experience.
You help professionals optimize their resumes for ATS systems and human recruiters.
Always respond with valid JSON matching the exact schema requested.
Be specific, actionable, and professional."""


def generate_resume_suggestions(
    resume_text: str,
    skills_found: list,
    missing_skills: list,
    ats_score: float,
    job_description: str = "",
) -> dict:
    """Call the LLM and return structured suggestion data."""

    context = f"""
RESUME TEXT:
{resume_text[:3000]}

CURRENT ATS SCORE: {ats_score}/100
SKILLS FOUND: {', '.join(skills_found[:20])}
MISSING SKILLS: {', '.join(missing_skills[:15])}
JOB DESCRIPTION: {job_description[:1000] if job_description else 'Not provided'}
"""

    user_prompt = f"""Analyze this resume and provide comprehensive improvement suggestions.

{context}

Return a JSON object with EXACTLY these keys:
{{
  "professional_summary": "improved 3-4 sentence professional summary",
  "experience_bullets": ["improved bullet 1", "improved bullet 2", ...],
  "keyword_improvements": [{{"original": "...", "improved": "...", "reason": "..."}}],
  "grammar_corrections": [{{"original": "...", "corrected": "...", "explanation": "..."}}],
  "skills_section": "formatted skills section text",
  "missing_skills": ["skill1", "skill2"],
  "formatting_suggestions": ["suggestion1", "suggestion2"],
  "industry_recommendations": ["recommendation1", "recommendation2"]
}}"""

    response = call_llm(SYSTEM_PROMPT, user_prompt)
    data = parse_json_response(response.content)
    data["_meta"] = {
        "prompt_tokens": response.prompt_tokens,
        "completion_tokens": response.completion_tokens,
        "model": response.model,
    }
    return data


def suggestion_to_text(suggestion) -> str:
    """Convert AIResumeSuggestion model to downloadable plain text."""
    lines = ["=" * 60, "AI RESUME IMPROVEMENT SUGGESTIONS", "=" * 60, ""]

    if suggestion.professional_summary:
        lines += ["PROFESSIONAL SUMMARY", "-" * 30, suggestion.professional_summary, ""]

    if suggestion.experience_bullets:
        lines += ["IMPROVED EXPERIENCE BULLETS", "-" * 30]
        for i, b in enumerate(suggestion.experience_bullets, 1):
            lines.append(f"  {i}. {b}")
        lines.append("")

    if suggestion.skills_section:
        lines += ["OPTIMIZED SKILLS SECTION", "-" * 30, suggestion.skills_section, ""]

    if suggestion.missing_skills:
        lines += ["MISSING SKILLS TO ADD", "-" * 30]
        for s in suggestion.missing_skills:
            lines.append(f"  • {s}")
        lines.append("")

    if suggestion.keyword_improvements:
        lines += ["KEYWORD IMPROVEMENTS", "-" * 30]
        for k in suggestion.keyword_improvements:
            lines.append(f"  Before: {k.get('original', '')}")
            lines.append(f"  After:  {k.get('improved', '')}")
            lines.append(f"  Why:    {k.get('reason', '')}")
            lines.append("")

    if suggestion.formatting_suggestions:
        lines += ["FORMATTING SUGGESTIONS", "-" * 30]
        for s in suggestion.formatting_suggestions:
            lines.append(f"  • {s}")
        lines.append("")

    if suggestion.industry_recommendations:
        lines += ["INDUSTRY RECOMMENDATIONS", "-" * 30]
        for r in suggestion.industry_recommendations:
            lines.append(f"  • {r}")
        lines.append("")

    return "\n".join(lines)
