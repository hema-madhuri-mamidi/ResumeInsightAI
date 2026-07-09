"""Skill gap analysis utilities for parsed resume data."""

from __future__ import annotations

from typing import Any

from .job_match import calculate_job_match
from .skill_guide import SKILL_GUIDE


def _get_skill_guide(skill: str) -> dict[str, str]:
    if skill in SKILL_GUIDE:
        return {
            "skill": skill,
            "reason": SKILL_GUIDE[skill]["reason"],
            "learning_path": SKILL_GUIDE[skill]["learning_path"],
            "estimated_time": SKILL_GUIDE[skill]["estimated_time"],
            "priority": SKILL_GUIDE[skill]["priority"],
        }

    return {
        "skill": skill,
        "reason": "Recommended technology for this job role.",
        "learning_path": "Start with beginner tutorials, then build one practical project.",
        "estimated_time": "Depends on prior experience.",
        "priority": "Medium",
    }


def analyze_skill_gap(parsed_data: dict[str, Any], job_description: str) -> dict[str, Any]:
    """Return missing and recommended skills using the job-match missing-skill list as the source of truth."""
    if not job_description or not job_description.strip():
        return {
            "missing_skills": [],
            "recommended_skills_to_learn": [],
            "priority": "Low",
            "skill_guides": [],
        }

    job_match_result = calculate_job_match(parsed_data, job_description)
    missing_skills = list(job_match_result.get("missing_skills") or [])
    recommended_skills_to_learn = list(missing_skills)
    skill_guides = [_get_skill_guide(skill) for skill in missing_skills]

    if not recommended_skills_to_learn:
        priority = "Low"
    elif len(recommended_skills_to_learn) >= 6:
        priority = "High"
    elif len(recommended_skills_to_learn) >= 3:
        priority = "Medium"
    else:
        priority = "Low"

    return {
        "missing_skills": missing_skills,
        "recommended_skills_to_learn": recommended_skills_to_learn,
        "priority": priority,
        "skill_guides": skill_guides,
    }
