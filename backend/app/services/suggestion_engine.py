"""
Generate improvement suggestions based on ATS score breakdown and resume content.
"""
import re
from typing import List


def generate_suggestions(
    text: str,
    skills_found: List[str],
    missing_skills: List[str],
    score_breakdown: dict,
    contact_info: dict,
) -> List[dict]:
    """
    Return a list of prioritised suggestions:
      { title, description, priority (high|medium|low), example }
    """
    suggestions = []
    breakdown = score_breakdown or {}

    # ── Contact information ───────────────────────────────────────────────
    if not contact_info.get("email"):
        suggestions.append({
            "title": "Add your email address",
            "description": "ATS systems and recruiters need your email to contact you. Make sure it's clearly visible at the top of your resume.",
            "priority": "high",
            "example": "john.doe@gmail.com",
        })
    if not contact_info.get("phone"):
        suggestions.append({
            "title": "Add a phone number",
            "description": "Include a professional phone number. Recruiters often call before emailing.",
            "priority": "high",
            "example": "+1 (555) 123-4567",
        })
    if not contact_info.get("linkedin"):
        suggestions.append({
            "title": "Add your LinkedIn profile",
            "description": "A LinkedIn URL lets recruiters verify your profile and see endorsements. It increases trust significantly.",
            "priority": "medium",
            "example": "linkedin.com/in/johndoe",
        })

    # ── Missing sections ──────────────────────────────────────────────────
    sections_score = breakdown.get("key_sections", {}).get("score", 0)
    if sections_score < 15:
        if not re.search(r"\b(summary|objective|profile)\b", text, re.IGNORECASE):
            suggestions.append({
                "title": "Add a professional summary",
                "description": "A 2–4 sentence summary at the top tells the recruiter who you are and what you bring. It's often the first thing read.",
                "priority": "high",
                "example": "Results-driven software engineer with 5+ years building scalable web applications using Python and React.",
            })
        if not re.search(r"\b(experience|work history)\b", text, re.IGNORECASE):
            suggestions.append({
                "title": "Add a work experience section",
                "description": "The experience section is the most weight-heavy part of any resume. Label it clearly so ATS can find it.",
                "priority": "high",
            })

    # ── Quantified achievements ───────────────────────────────────────────
    quant_score = breakdown.get("quantified_achievements", {}).get("score", 0)
    if quant_score < 8:
        suggestions.append({
            "title": "Quantify your achievements",
            "description": "Numbers make your impact concrete and memorable. Replace vague claims with measurable results wherever possible.",
            "priority": "high",
            "example": "Reduced API response time by 40% → Reduced API response time by 40%, cutting p95 latency from 800ms to 480ms.",
        })

    # ── Action verbs ──────────────────────────────────────────────────────
    action_score = breakdown.get("action_verbs", {}).get("score", 0)
    if action_score < 8:
        suggestions.append({
            "title": "Start bullet points with strong action verbs",
            "description": "Begin each responsibility with a powerful action verb. Passive phrasing weakens impact and scores poorly in ATS.",
            "priority": "medium",
            "example": "Instead of 'Responsible for building APIs', use 'Engineered RESTful APIs that served 50K daily requests.'",
        })

    # ── Missing skills ────────────────────────────────────────────────────
    if len(missing_skills) > 5:
        top_missing = ", ".join(missing_skills[:5])
        suggestions.append({
            "title": "Add missing in-demand skills",
            "description": f"Your resume is missing several commonly expected keywords. If you have experience with these, add them: {top_missing}.",
            "priority": "medium",
        })

    # ── Formatting ────────────────────────────────────────────────────────
    format_score = breakdown.get("length_formatting", {}).get("score", 0)
    word_count = len(text.split())
    if word_count < 300:
        suggestions.append({
            "title": "Expand your resume content",
            "description": f"Your resume has only ~{word_count} words, which is too brief. Aim for 400–800 words to give ATS enough content to parse.",
            "priority": "high",
        })
    elif word_count > 1500:
        suggestions.append({
            "title": "Trim your resume to 1–2 pages",
            "description": f"At ~{word_count} words your resume may be too long. Focus on the last 10 years and remove outdated or irrelevant roles.",
            "priority": "medium",
        })

    # Bullet points
    bullet_count = len(re.findall(r"[•\-\*] ", text))
    if bullet_count < 5:
        suggestions.append({
            "title": "Use bullet points for experience descriptions",
            "description": "Bullet points are easier for both ATS and humans to scan. Convert paragraph descriptions into concise bullets.",
            "priority": "medium",
            "example": "• Built and maintained React components used by 20K+ users daily.",
        })

    # ── Tailoring ─────────────────────────────────────────────────────────
    suggestions.append({
        "title": "Tailor your resume for each job",
        "description": "Mirror keywords and phrases from the job description. ATS systems rank resumes higher when they closely match the posting.",
        "priority": "low",
    })

    # Deduplicate and return top 10
    seen = set()
    unique = []
    for s in suggestions:
        key = s["title"]
        if key not in seen:
            seen.add(key)
            unique.append(s)

    return unique[:10]
