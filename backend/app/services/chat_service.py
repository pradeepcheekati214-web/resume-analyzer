"""
Chat service — LLM-powered resume assistant with conversation memory.

Flow:
  1. Load resume text (from DB raw_text or S3).
  2. Build system prompt with resume context.
  3. Append last N messages as conversation history.
  4. Call LLM and return assistant reply.
"""
import logging
from typing import List, Optional

from app.services.ai_client import call_llm, parse_json_response

logger = logging.getLogger(__name__)

# How many past messages to include as memory (each message = 1 turn)
MEMORY_WINDOW = 10

SYSTEM_TEMPLATE = """You are an expert AI Resume Coach and Career Advisor.
You are analyzing the following resume for the user.
Your job is to help them improve their resume, understand their ATS score,
identify skill gaps, suggest career paths, and answer any career-related questions.

Always be:
- Specific and actionable
- Professional but friendly
- Concise (2-4 sentences per point unless a longer list is explicitly requested)
- Honest about weaknesses while encouraging

CANDIDATE'S RESUME:
---
{resume_text}
---

ATS SCORE: {ats_score}
SKILLS FOUND: {skills_found}
MISSING SKILLS: {missing_skills}

When asked to "rewrite" anything, produce the rewritten text immediately.
When asked for a list (projects, career paths, questions), use bullet points.
When explaining the ATS score, reference the actual score above.
"""

QUICK_REPLIES = {
    "improve my resume":      "improve_resume",
    "missing skills":         "missing_skills",
    "rewrite my summary":     "rewrite_summary",
    "suggest projects":       "suggest_projects",
    "generate interview questions": "interview_questions",
    "explain my ats score":   "explain_ats",
    "suggest career paths":   "career_paths",
    "career options":         "career_paths",
}


def build_system_prompt(
    resume_text: str,
    ats_score: float = 0,
    skills_found: List[str] = None,
    missing_skills: List[str] = None,
) -> str:
    return SYSTEM_TEMPLATE.format(
        resume_text=resume_text[:4000],
        ats_score=f"{ats_score:.0f}/100" if ats_score else "Not yet analyzed",
        skills_found=", ".join((skills_found or [])[:20]) or "Not extracted yet",
        missing_skills=", ".join((missing_skills or [])[:15]) or "None detected",
    )


def generate_chat_response(
    user_message: str,
    resume_text: str,
    history: List[dict],       # [{"role": "user"|"assistant", "content": "..."}]
    ats_score: float = 0,
    skills_found: List[str] = None,
    missing_skills: List[str] = None,
) -> str:
    """
    Generate an assistant reply using conversation history as memory.
    Falls back to mock if LLM is unavailable.
    """
    system_prompt = build_system_prompt(resume_text, ats_score, skills_found, missing_skills)

    # Build the full prompt with conversation history
    history_text = _format_history(history[-MEMORY_WINDOW:])
    full_prompt = f"""{history_text}

User: {user_message}

Respond as the AI Resume Coach. Be specific, reference the actual resume content above."""

    try:
        response = call_llm(system_prompt, full_prompt)
        content  = response.content.strip()

        # If LLM returned JSON (mock mode), extract the text
        if content.startswith("{") or content.startswith("["):
            parsed = parse_json_response(content)
            content = parsed.get("reply") or parsed.get("message") or parsed.get("result") or str(parsed)

        return content
    except Exception as exc:
        logger.error("Chat LLM call failed: %s", exc)
        return _mock_response(user_message, resume_text, ats_score, skills_found, missing_skills)


def _format_history(history: List[dict]) -> str:
    if not history:
        return ""
    lines = ["Previous conversation:"]
    for msg in history:
        role    = "User" if msg["role"] == "user" else "Assistant"
        content = str(msg["content"])[:300]
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


def _mock_response(
    user_message: str,
    resume_text: str,
    ats_score: float,
    skills_found: List[str],
    missing_skills: List[str],
) -> str:
    """Deterministic mock responses for demo / when no API key is configured."""
    msg_lower = user_message.lower()

    if any(kw in msg_lower for kw in ["improve", "better", "enhance", "optimize"]):
        return (
            "Here are my top suggestions to improve your resume:\n\n"
            "• **Quantify achievements** — Add numbers to every bullet point (e.g., 'Reduced API latency by 40%')\n"
            "• **Strong action verbs** — Start each bullet with words like Built, Engineered, Delivered, Led\n"
            "• **Tailor per role** — Mirror keywords from the job description in your experience section\n"
            "• **Professional summary** — Add a 2-3 sentence summary at the top highlighting your value proposition\n"
            "• **Contact info** — Ensure email, phone, LinkedIn, and GitHub are visible at the top"
        )

    if any(kw in msg_lower for kw in ["missing skill", "skill gap", "what skill"]):
        missing = ", ".join(missing_skills[:8]) if missing_skills else "None detected"
        return (
            f"Based on your resume analysis, here are the missing skills worth adding:\n\n"
            f"**Missing from your resume:** {missing}\n\n"
            "**Recommendations:**\n"
            "• Add any of these you have experience with — even from side projects\n"
            "• For each skill, include a specific project or achievement that demonstrates it\n"
            "• Prioritize the skills that appear most in job descriptions for your target role"
        )

    if any(kw in msg_lower for kw in ["rewrite", "summary", "objective", "profile"]):
        return (
            "Here's a rewritten professional summary based on your resume:\n\n"
            "---\n"
            "Results-driven Software Engineer with hands-on experience building full-stack web applications "
            "using Python, React, FastAPI, and AWS. Proven ability to design and deploy scalable REST APIs, "
            "implement authentication systems, and optimize database performance. "
            "Passionate about clean architecture, developer experience, and delivering measurable impact.\n"
            "---\n\n"
            "Feel free to ask me to adjust the tone, length, or focus for a specific role."
        )

    if any(kw in msg_lower for kw in ["project", "side project", "portfolio", "build"]):
        return (
            "Here are 5 project ideas tailored to your skill set:\n\n"
            "• **Resume Analyzer CLI** — Command-line tool that parses a PDF resume and gives an ATS score (Python + pdfplumber)\n"
            "• **Job Board Scraper** — Scrape job listings and match them to a resume using keyword analysis (Python + FastAPI)\n"
            "• **Portfolio Website** — Personal portfolio with project showcase, blog, and contact form (React + Tailwind)\n"
            "• **URL Shortener** — Full-stack app with analytics dashboard (FastAPI + React + PostgreSQL + Redis)\n"
            "• **Expense Tracker** — Mobile-friendly PWA with charts and CSV export (React + FastAPI + SQLAlchemy)\n\n"
            "Each of these will strengthen your portfolio and can be completed in 1-2 weeks."
        )

    if any(kw in msg_lower for kw in ["interview", "question", "prepare", "practice"]):
        skills_str = ", ".join((skills_found or [])[:6]) or "Python, React, FastAPI"
        return (
            f"Here are 5 interview questions based on your skill set ({skills_str}):\n\n"
            "1. **[Technical - Medium]** Explain the difference between REST and GraphQL. When would you use each?\n"
            "2. **[Python - Easy]** What are Python decorators and how do you use them in FastAPI?\n"
            "3. **[Behavioral]** Describe a time you debugged a critical production issue. Walk me through your approach.\n"
            "4. **[System Design]** How would you design a scalable file upload service on AWS?\n"
            "5. **[Project]** Walk me through the most complex feature you've built. What were the trade-offs?\n\n"
            "Want me to generate questions for a specific role or technology?"
        )

    if any(kw in msg_lower for kw in ["ats", "score", "ats score", "explain"]):
        score = f"{ats_score:.0f}" if ats_score else "unknown"
        return (
            f"Your ATS score is **{score}/100**. Here's what that means:\n\n"
            "**Score breakdown:**\n"
            "• **Contact Info (10 pts)** — Email, phone, LinkedIn are detected\n"
            "• **Key Sections (20 pts)** — Experience, Education, Skills sections found\n"
            "• **Skills & Keywords (30 pts)** — Based on how many required skills match the JD\n"
            "• **Quantified Achievements (15 pts)** — Numbers and metrics in bullet points\n"
            "• **Action Verbs (15 pts)** — Strong verbs starting bullet points\n"
            "• **Formatting (10 pts)** — Length, bullet usage, clean structure\n\n"
            "**To push your score higher:** Add more quantified achievements and mirror keywords from the job description."
        )

    if any(kw in msg_lower for kw in ["career", "path", "role", "job", "switch", "option"]):
        skills_str = ", ".join((skills_found or [])[:5]) or "Python, React"
        return (
            f"Based on your skills ({skills_str}), here are strong career paths:\n\n"
            "• **Full Stack Engineer** — Your Python + React combination is ideal. Target roles at product startups.\n"
            "• **Backend Engineer** — Deepen FastAPI + PostgreSQL + AWS. High demand and strong salaries.\n"
            "• **Cloud/DevOps Engineer** — Expand your AWS knowledge with Kubernetes and Terraform.\n"
            "• **Technical Lead** — With 3-4 more years, your current stack makes you a strong lead candidate.\n"
            "• **Solutions Architect** — AWS certifications (SA-Associate → Professional) open this path.\n\n"
            "Which direction interests you most? I can give specific steps for any of these."
        )

    if any(kw in msg_lower for kw in ["hello", "hi", "hey", "start", "help"]):
        return (
            "Hello! 👋 I'm your AI Resume Coach. I've loaded your resume and I'm ready to help.\n\n"
            "Here's what I can do for you:\n"
            "• **Improve your resume** — section by section feedback\n"
            "• **Identify missing skills** — based on your target role\n"
            "• **Rewrite sections** — professional summary, experience bullets\n"
            "• **Suggest projects** — tailored to your skill set\n"
            "• **Generate interview questions** — for your target role\n"
            "• **Explain your ATS score** — what's dragging it down\n"
            "• **Suggest career paths** — based on your background\n\n"
            "What would you like help with first?"
        )

    # Default
    return (
        f"I've reviewed your resume and I'm happy to help with that.\n\n"
        f"Your resume has {len((skills_found or []))} skills detected"
        f"{' including ' + ', '.join((skills_found or [])[:4]) if skills_found else ''}. "
        f"Could you be more specific about what you'd like me to focus on? "
        f"For example, I can help with:\n"
        "• Improving specific sections\n"
        "• Identifying skill gaps for a target role\n"
        "• Rewriting your summary or bullet points\n"
        "• Suggesting projects or career paths"
    )
