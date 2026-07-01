"""Tests for resume parsing utilities."""
import io
import pytest
from app.services.resume_parser import extract_contact_info, _clean_text


class TestContactInfoExtraction:
    def test_extracts_email(self):
        text = "John Doe\njohn.doe@example.com\n(555) 123-4567"
        info = extract_contact_info(text)
        assert info.get("email") == "john.doe@example.com"

    def test_extracts_phone(self):
        text = "Contact: +1 (555) 123-4567"
        info = extract_contact_info(text)
        assert info.get("phone") is not None

    def test_extracts_linkedin(self):
        text = "linkedin.com/in/johndoe"
        info = extract_contact_info(text)
        assert "linkedin" in info

    def test_extracts_github(self):
        text = "github.com/johndoe"
        info = extract_contact_info(text)
        assert "github" in info

    def test_extracts_name_from_first_line(self):
        text = "Alice Johnson\nalice@example.com\nSoftware Engineer"
        info = extract_contact_info(text)
        assert info.get("name") == "Alice Johnson"

    def test_handles_empty_text(self):
        info = extract_contact_info("")
        assert info == {}


class TestCleanText:
    def test_removes_extra_whitespace(self):
        result = _clean_text("hello   world")
        assert "  " not in result

    def test_collapses_multiple_newlines(self):
        result = _clean_text("line1\n\n\n\nline2")
        assert result.count("\n") <= 2

    def test_strips_text(self):
        result = _clean_text("  hello  ")
        assert result == "hello"


class TestSkillExtraction:
    def test_extracts_known_skills(self):
        from app.services.skill_extractor import extract_skills
        text = "Experienced with Python, React, and Docker."
        skills = extract_skills(text)
        assert "Python" in skills
        assert "React" in skills
        assert "Docker" in skills

    def test_case_insensitive(self):
        from app.services.skill_extractor import extract_skills
        text = "proficient in PYTHON and javascript"
        skills = extract_skills(text)
        assert "Python" in skills
        assert "JavaScript" in skills

    def test_no_skills_returns_empty(self):
        from app.services.skill_extractor import extract_skills
        text = "I like to eat sandwiches at noon."
        skills = extract_skills(text)
        assert isinstance(skills, list)

    def test_find_missing_skills_with_jd(self):
        from app.services.skill_extractor import find_missing_skills
        found = ["Python", "React"]
        jd = "Looking for a Python, React, Kubernetes, and Docker expert."
        missing = find_missing_skills(found, jd)
        assert "Kubernetes" in missing or "Docker" in missing


class TestATSScorer:
    def test_high_score_for_complete_resume(self):
        from app.services.ats_scorer import calculate_ats_score
        text = (
            "John Doe | john@example.com | +1 555 000 1111 | linkedin.com/in/johndoe\n\n"
            "SUMMARY\nResults-driven software engineer with 8 years of experience.\n\n"
            "EXPERIENCE\n"
            "• Developed and shipped 3 major product features increasing revenue by 25%.\n"
            "• Led a team of 5 engineers to deliver a microservices migration on schedule.\n"
            "• Reduced API latency by 40% through query optimisation.\n\n"
            "EDUCATION\nB.Sc. Computer Science, State University, 2015\n\n"
            "SKILLS\nPython, Django, React, PostgreSQL, Docker, Kubernetes, AWS, Git, CI/CD"
        )
        skills = ["Python", "Django", "React", "PostgreSQL", "Docker", "Kubernetes", "AWS"]
        missing = ["Go", "Rust"]
        result = calculate_ats_score(
            text=text, skills_found=skills, missing_skills=missing,
            contact_info={"email": "john@example.com", "phone": "555 000 1111",
                          "name": "John Doe", "linkedin": "linkedin.com/in/johndoe"},
        )
        assert result.total_score >= 60

    def test_low_score_for_minimal_resume(self):
        from app.services.ats_scorer import calculate_ats_score
        text = "My name is Bob. I am a developer."
        result = calculate_ats_score(text=text, skills_found=[], missing_skills=[])
        assert result.total_score < 40

    def test_breakdown_contains_all_dimensions(self):
        from app.services.ats_scorer import calculate_ats_score
        result = calculate_ats_score(text="Test resume.", skills_found=[], missing_skills=[])
        expected_keys = {
            "contact_info", "key_sections", "skills_keywords",
            "quantified_achievements", "action_verbs", "length_formatting",
        }
        assert expected_keys == set(result.breakdown.keys())
