"""Rule-based resume suggestions based on parsed resume sections."""

from __future__ import annotations

from typing import Any

from .ats_score import calculate_ats_score


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return len(value) > 0
    return bool(value)


def _is_detailed_project(project: Any) -> bool:
    if not isinstance(project, dict):
        return False
    return bool(
        _has_value(project.get("description"))
        or _has_value(project.get("description_text"))
        or _has_value(project.get("highlights"))
        or _has_value(project.get("achievements"))
        or _has_value(project.get("technologies"))
        or _has_value(project.get("tech_stack"))
    )


def generate_suggestions(parsed_data: dict[str, Any], ats_score: dict[str, Any] | None = None) -> dict[str, list[str]]:
    """Generate simple, rule-based suggestions from parsed resume data."""
    suggestions: list[str] = []
    section_scores = (ats_score or calculate_ats_score(parsed_data)).get("section_scores", {})

    contact = parsed_data.get("contact") or {}
    if not isinstance(contact, dict):
        contact = {}

    if section_scores.get("contact", 0) < 15:
        if not _has_value(contact.get("name")):
            suggestions.append("Add your full name.")
        if not _has_value(contact.get("email")):
            suggestions.append("Add your email address.")
        if not _has_value(contact.get("phone")):
            suggestions.append("Add your phone number.")
        if not _has_value(contact.get("linkedin")):
            suggestions.append("Add LinkedIn profile")
        if not _has_value(contact.get("github")):
            suggestions.append("Add GitHub profile")
        if not _has_value(contact.get("portfolio")):
            suggestions.append("Add portfolio link")

    education = parsed_data.get("education") or {}
    if not isinstance(education, dict):
        education = {}
    if section_scores.get("education", 0) < 10 and not _has_value(education.get("year")) and not _has_value(education.get("cgpa")) and not _has_value(education.get("percentage")):
        suggestions.append("Include graduation year or CGPA.")

    experience = parsed_data.get("experience") or []
    if not experience:
        suggestions.append("Add experience section")

    projects = parsed_data.get("projects") or []
    if section_scores.get("projects", 0) < 12 and (not isinstance(projects, list) or len(projects) < 2 or not any(_is_detailed_project(project) for project in projects)):
        suggestions.append("Improve your project descriptions by adding technologies and achievements.")

    skills = parsed_data.get("skills") or []
    if section_scores.get("skills", 0) < 12 and (not isinstance(skills, list) or len(skills) < 4):
        suggestions.append("Add more relevant frameworks and technical tools.")

    certifications = parsed_data.get("certifications") or []
    if section_scores.get("certifications", 0) < 6 and not certifications:
        suggestions.append("Add certifications")

    activities = parsed_data.get("activities") or []
    if section_scores.get("activities", 0) < 6 and not activities:
        suggestions.append("Add activities")

    return {"suggestions": suggestions}
