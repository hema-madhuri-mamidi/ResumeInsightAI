"""Rule-based resume suggestions based on parsed resume sections."""

from __future__ import annotations

from typing import Any


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return len(value) > 0
    return bool(value)


def generate_suggestions(parsed_data: dict[str, Any]) -> dict[str, list[str]]:
    """Generate simple, rule-based suggestions from parsed resume data."""
    suggestions: list[str] = []

    contact = parsed_data.get("contact") or {}
    if not isinstance(contact, dict):
        contact = {}

    if not _has_value(contact.get("linkedin")):
        suggestions.append("Add LinkedIn profile")
    if not _has_value(contact.get("github")):
        suggestions.append("Add GitHub profile")
    if not _has_value(contact.get("portfolio")):
        suggestions.append("Add portfolio link")

    experience = parsed_data.get("experience") or []
    if not experience:
        suggestions.append("Add experience section")

    projects = parsed_data.get("projects") or []
    if not isinstance(projects, list) or len(projects) < 3:
        suggestions.append("Add more projects")

    skills = parsed_data.get("skills") or []
    if not isinstance(skills, list) or len(skills) < 5:
        suggestions.append("Add more skills")

    certifications = parsed_data.get("certifications") or []
    if not certifications:
        suggestions.append("Add certifications")

    activities = parsed_data.get("activities") or []
    if not activities:
        suggestions.append("Add activities")

    return {"suggestions": suggestions}
