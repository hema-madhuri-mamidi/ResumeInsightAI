"""Rule-based ATS scoring utilities for parsed resume data."""

from __future__ import annotations

from typing import Any


WEIGHTS = {
    "contact": 15,
    "education": 15,
    "skills": 20,
    "projects": 25,
    "experience": 15,
    "certifications": 10,
}


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return len(value) > 0
    return bool(value)


def _score_contact(contact: Any) -> int:
    if not isinstance(contact, dict):
        return 0

    present_fields = [
        _has_value(contact.get("email")),
        _has_value(contact.get("phone")),
        _has_value(contact.get("github")),
        _has_value(contact.get("linkedin")),
    ]

    if all(present_fields[:2]):
        return WEIGHTS["contact"]
    if sum(present_fields[:2]) == 1:
        return 8
    if any(present_fields[:2]):
        return 5
    return 0


def _score_education(education: Any) -> int:
    if not isinstance(education, dict):
        return 0

    present_fields = [
        _has_value(education.get("degree")),
        _has_value(education.get("branch")),
        _has_value(education.get("college")),
    ]

    if all(present_fields):
        return WEIGHTS["education"]
    if sum(present_fields) >= 2:
        return 10
    if any(present_fields):
        return 5
    return 0


def _score_skills(skills: Any) -> int:
    if not isinstance(skills, list):
        return 0

    if not skills:
        return 0

    if len(skills) >= 5:
        return WEIGHTS["skills"]
    if len(skills) >= 3:
        return WEIGHTS["skills"]
    if len(skills) >= 1:
        return 10
    return 0


def _score_projects(projects: Any) -> int:
    if not isinstance(projects, list):
        return 0

    if not projects:
        return 0

    first_project = projects[0]
    if isinstance(first_project, dict):
        has_title = _has_value(first_project.get("title")) or _has_value(first_project.get("name"))
        has_details = _has_value(first_project.get("description")) or _has_value(first_project.get("technologies"))
        if has_title and has_details:
            return WEIGHTS["projects"]
        if has_title or has_details:
            return 15

    return WEIGHTS["projects"]


def _score_experience(experience: Any) -> int:
    if not isinstance(experience, list):
        return 0

    if not experience:
        return 0

    first_entry = experience[0]
    if isinstance(first_entry, dict):
        has_title = _has_value(first_entry.get("title"))
        has_org = _has_value(first_entry.get("organization"))
        has_duration = _has_value(first_entry.get("duration"))
        if has_title and has_org and has_duration:
            return WEIGHTS["experience"]
        if has_title or has_org or has_duration:
            return 10

    return WEIGHTS["experience"]


def _score_certifications(certifications: Any) -> int:
    if not isinstance(certifications, list):
        return 0

    if not certifications:
        return 0

    return 10


def _build_strengths(section_scores: dict[str, int], parsed_data: dict[str, Any]) -> list[str]:
    strengths: list[str] = []

    if section_scores["projects"] >= 20:
        strengths.append("Strong technical projects")
    if section_scores["skills"] >= 15:
        strengths.append("Good technical skill set")
    if section_scores["certifications"] >= 10:
        strengths.append("Professional certifications")
    if section_scores["experience"] >= 10:
        strengths.append("Work experience present")
    if section_scores["contact"] >= 10:
        strengths.append("Contact details are complete")

    if not strengths:
        strengths.append("Resume contains basic parsed information")

    return strengths


def _build_improvements(section_scores: dict[str, int], parsed_data: dict[str, Any]) -> list[str]:
    improvements: list[str] = []
    contact = parsed_data.get("contact") or {}
    if not isinstance(contact, dict):
        contact = {}

    if section_scores["experience"] < 10:
        improvements.append("Add professional experience")

    github = contact.get("github")
    linkedin = contact.get("linkedin")
    portfolio = contact.get("portfolio")

    if not _has_value(github):
        improvements.append("GitHub link could not be verified. Ensure the full GitHub URL is visible and ATS-readable.")
    if not _has_value(linkedin):
        improvements.append("LinkedIn link could not be verified. Ensure the full LinkedIn URL is visible and ATS-readable.")
    if not _has_value(portfolio):
        improvements.append("Portfolio link could not be verified. Ensure the full portfolio URL is visible and ATS-readable.")

    if section_scores["projects"] < 15:
        improvements.append("Add more project examples")
    if section_scores["skills"] < 15:
        improvements.append("Expand technical skill list")
    if section_scores["education"] < 15:
        improvements.append("Add degree or university details")

    return improvements


def calculate_ats_score(parsed_data: dict[str, Any]) -> dict[str, Any]:
    """Calculate a simple ATS score and summary from parsed resume sections."""
    section_scores = {
        "contact": _score_contact(parsed_data.get("contact")),
        "education": _score_education(parsed_data.get("education")),
        "skills": _score_skills(parsed_data.get("skills")),
        "projects": _score_projects(parsed_data.get("projects")),
        "experience": _score_experience(parsed_data.get("experience")),
        "certifications": _score_certifications(parsed_data.get("certifications")),
    }

    overall_score = sum(section_scores.values())
    if overall_score > 100:
        overall_score = 100

    strengths = _build_strengths(section_scores, parsed_data)
    improvements = _build_improvements(section_scores, parsed_data)

    return {
        "overall_score": overall_score,
        "section_scores": section_scores,
        "strengths": strengths,
        "improvements": improvements,
    }
