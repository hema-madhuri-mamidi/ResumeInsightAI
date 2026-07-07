"""Main entry point for the Version 2 resume parser."""

from __future__ import annotations

from typing import Any

from .activity_parser import extract_activities
from .certification_parser import extract_certifications
from .contact_parser import extract_contact_info
from .education_parser import extract_education
from .experience_parser import extract_experience
from .name_parser import extract_name
from .project_parser import extract_projects
from .section_detector import detect_sections
from .skills_parser import extract_skills


def parse_resume(text: str) -> dict[str, Any]:
    """
    Parse a resume text into a structured, JSON-like dictionary.

    TODO: Implement orchestration and output normalization in Version 2.
    """
    sections = detect_sections(text)

    header_lines = sections.get("header", [])

    return {
        "name": extract_name(header_lines),
        "contact": extract_contact_info(header_lines),
        "education": extract_education(sections.get("education", [])),
        "projects": extract_projects(sections.get("projects", [])),
        "experience": extract_experience(sections.get("experience", [])),
        "skills": extract_skills(sections.get("skills", [])),
        "certifications": extract_certifications(sections.get("certifications", [])),
        "activities": extract_activities(sections.get("activities", [])),
    }
