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
    "activities": 10,
}


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return len(value) > 0
    return bool(value)


def _normalize_text(value: Any) -> str:
    return str(value or "").strip().lower()


def _score_contact(contact: Any) -> int:
    if not isinstance(contact, dict):
        return 0

    field_scores = {
        "name": 2,
        "email": 3,
        "phone": 3,
        "linkedin": 2,
        "github": 2,
        "portfolio": 3,
    }
    score = 0

    if _has_value(contact.get("name")):
        score += field_scores["name"]
    if _has_value(contact.get("email")):
        score += field_scores["email"]
    if _has_value(contact.get("phone")):
        score += field_scores["phone"]
    if _has_value(contact.get("linkedin")):
        score += field_scores["linkedin"]
    if _has_value(contact.get("github")):
        score += field_scores["github"]
    if _has_value(contact.get("portfolio")):
        score += field_scores["portfolio"]

    return min(WEIGHTS["contact"], score)


def _score_education(education: Any) -> int:
    if not isinstance(education, dict):
        return 0

    checks = [
        ("degree", 4),
        ("college", 4),
        ("branch", 3),
        ("cgpa", 2),
        ("percentage", 2),
        ("year", 2),
    ]
    score = 0

    for field_name, weight in checks:
        if _has_value(education.get(field_name)):
            score += weight

    return min(WEIGHTS["education"], score)


def _score_skills(skills: Any) -> int:
    if not isinstance(skills, list):
        return 0

    if not skills:
        return 0

    technical_skills = [skill for skill in skills if isinstance(skill, str) and skill.strip()]
    if not technical_skills:
        return 0

    score = 0
    if len(technical_skills) >= 8:
        score += 8
    elif len(technical_skills) >= 5:
        score += 6
    elif len(technical_skills) >= 3:
        score += 4
    else:
        score += 2

    if any(_normalize_text(skill) in {"python", "java", "javascript", "react", "node", "sql", "aws", "docker", "flask", "django"} for skill in technical_skills):
        score += 6

    if len(technical_skills) >= 4 and any("framework" not in _normalize_text(skill) and any(token in _normalize_text(skill) for token in ["react", "flask", "django", "spring", "node", "fastapi"]) for skill in technical_skills):
        score += 4

    if len(technical_skills) >= 4 and any(_normalize_text(skill) in {"git", "github", "docker", "aws", "jira", "linux", "sql"} for skill in technical_skills):
        score += 2

    return min(WEIGHTS["skills"], score)


def _score_projects(projects: Any) -> int:
    if not isinstance(projects, list) or not projects:
        return 0

    score = 0
    detailed_projects = 0
    for project in projects:
        if not isinstance(project, dict):
            continue

        title = _has_value(project.get("title")) or _has_value(project.get("name"))
        description = _has_value(project.get("description")) or _has_value(project.get("description_text"))
        technologies = _has_value(project.get("technologies")) or _has_value(project.get("tech_stack"))
        highlights = _has_value(project.get("highlights")) or _has_value(project.get("achievements"))

        if title:
            score += 4
        if description:
            score += 6
        if technologies:
            score += 5
        if highlights:
            score += 5

        if title and description and technologies and highlights:
            detailed_projects += 1

    if len(projects) >= 2:
        score += 5

    if detailed_projects >= 2:
        score += 5

    return min(WEIGHTS["projects"], score)


def _score_experience(experience: Any) -> int:
    if not isinstance(experience, list) or not experience:
        return 0

    score = 0
    for entry in experience:
        if not isinstance(entry, dict):
            continue
        if _has_value(entry.get("title")) or _has_value(entry.get("role")):
            score += 4
        if _has_value(entry.get("organization")) or _has_value(entry.get("company")):
            score += 3
        if _has_value(entry.get("duration")) or _has_value(entry.get("period")):
            score += 3
        if _has_value(entry.get("description")) or _has_value(entry.get("highlights")):
            score += 5
        if any(_has_value(entry.get(key)) for key in ["internship", "research", "freelancing", "hackathon", "opensource", "project"]):
            score += 2
        break

    return min(WEIGHTS["experience"], score)


def _score_certifications(certifications: Any) -> int:
    if not isinstance(certifications, list):
        return 0

    if not certifications:
        return 0

    score = 0
    if len(certifications) >= 2:
        score += 4
    elif len(certifications) >= 1:
        score += 2

    if any(_has_value(item) for item in certifications):
        score += 3

    if len(certifications) >= 2:
        score += 3

    return min(WEIGHTS["certifications"], score)


def _score_activities(activities: Any) -> int:
    if not isinstance(activities, list):
        return 0

    if not activities:
        return 0

    score = 0
    if len(activities) >= 3:
        score += 6
    elif len(activities) >= 2:
        score += 4
    elif len(activities) >= 1:
        score += 2

    normalized = [_normalize_text(item) for item in activities if _has_value(item)]
    if any(keyword in normalized for keyword in ["hackathon", "leadership", "volunteer", "competition", "club", "award", "opensource"]):
        score += 4

    return min(WEIGHTS["activities"], score)


def _build_strengths(section_scores: dict[str, int], parsed_data: dict[str, Any]) -> list[str]:
    strengths: list[str] = []

    if section_scores["projects"] >= 18:
        strengths.append("Strong technical projects")
    if section_scores["skills"] >= 12:
        strengths.append("Good technical skill set")
    if section_scores["certifications"] >= 6:
        strengths.append("Professional certifications")
    if section_scores["experience"] >= 8:
        strengths.append("Work experience present")
    if section_scores["contact"] >= 10:
        strengths.append("Contact details are complete")
    if section_scores["activities"] >= 6:
        strengths.append("Notable activities and achievements")

    if not strengths:
        strengths.append("Resume contains basic parsed information")

    return strengths


def _build_improvements(section_scores: dict[str, int], parsed_data: dict[str, Any]) -> list[str]:
    improvements: list[str] = []
    contact = parsed_data.get("contact") or {}
    if not isinstance(contact, dict):
        contact = {}

    if section_scores["experience"] < 8:
        improvements.append("Add professional experience")

    github = contact.get("github")
    linkedin = contact.get("linkedin")
    portfolio = contact.get("portfolio")

    if not _has_value(contact.get("email")):
        improvements.append("Add your email address.")
    if not _has_value(contact.get("phone")):
        improvements.append("Add your phone number.")
    if not _has_value(github):
        improvements.append("GitHub link could not be verified. Ensure the full GitHub URL is visible and ATS-readable.")
    if not _has_value(linkedin):
        improvements.append("LinkedIn link could not be verified. Ensure the full LinkedIn URL is visible and ATS-readable.")
    if not _has_value(portfolio):
        improvements.append("Portfolio link could not be verified. Ensure the full portfolio URL is visible and ATS-readable.")

    if section_scores["projects"] < 12:
        improvements.append("Improve your project descriptions by adding technologies and achievements.")
    if section_scores["skills"] < 12:
        improvements.append("Add more relevant frameworks and technical tools.")
    if section_scores["education"] < 10:
        improvements.append("Include graduation year or CGPA.")
    if section_scores["activities"] < 4:
        improvements.append("Add hackathons, leadership roles, or volunteering highlights.")

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
        "activities": _score_activities(parsed_data.get("activities")),
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
