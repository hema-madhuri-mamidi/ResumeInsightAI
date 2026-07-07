"""Project parser for the Version 2 resume parser."""

from __future__ import annotations

from typing import Any

from . import project_utils


def _clean_text(value: str) -> str:
    """Return a trimmed string with internal whitespace collapsed."""
    return " ".join(value.split())


def _split_technologies(line: str) -> list[str]:
    """Split a technology line into a clean ordered list of technologies."""
    cleaned = _clean_text(line)
    if not cleaned:
        return []

    separators = [",", "|", "/", ";", "•"]
    for separator in separators:
        if separator in cleaned:
            parts = [part.strip() for part in cleaned.split(separator)]
            return [token for token in parts if token]

    return [token for token in cleaned.split() if token]


def _looks_like_section_heading(line: str) -> bool:
    """Return True when a line looks like a section heading rather than a project title."""
    cleaned = _clean_text(line).lower()
    return cleaned in {"projects", "project", "projects section", "project section"}


def _looks_like_single_token_technology(line: str) -> bool:
    """Return True for single-token technology-like lines such as Python or Chart.js."""
    cleaned = _clean_text(line)
    if not cleaned or " " in cleaned:
        return False

    lowered = cleaned.lower()
    if lowered in {"projects", "project"}:
        return False

    if lowered in project_utils.COMMON_TECHNOLOGIES:
        return True

    if "." in cleaned or "/" in cleaned or "-" in cleaned:
        return True

    return False


def _looks_like_new_project_title(line: str, current_project: dict[str, Any] | None) -> bool:
    """Return True when a line should start a new project entry."""
    cleaned = project_utils.clean_project_line(line)
    if not cleaned:
        return False

    if project_utils.looks_like_technology_line(cleaned):
        return False

    if _looks_like_single_token_technology(cleaned):
        return False

    if not project_utils.looks_like_project_title(cleaned):
        return False

    if current_project is None:
        return True

    return project_utils._strip_link_metadata(cleaned) != current_project.get("title")


def _start_new_project(title: str) -> dict[str, Any]:
    """Create a new project entry with empty description and technologies."""
    return {
        "title": project_utils._strip_link_metadata(title),
        "technologies": [],
        "description": [],
    }


def _finish_current_project(current_project: dict[str, Any] | None, projects: list[dict[str, Any]]) -> None:
    """Append a completed project to the list when it has a valid title."""
    if current_project is None:
        return

    title = _clean_text(str(current_project.get("title", "")))
    if not title:
        return

    projects.append(current_project)


def _add_description(current_project: dict[str, Any] | None, line: str) -> None:
    """Append a description line to the current project if one exists."""
    if current_project is None:
        return

    cleaned = _clean_text(line)
    if not cleaned:
        return

    if cleaned.startswith(project_utils._BULLET_PREFIXES):
        cleaned = cleaned[1:].lstrip()

    current_project["description"].append(cleaned)


def _add_technologies(current_project: dict[str, Any] | None, line: str) -> None:
    """Add technologies from a line to the current project without duplicates."""
    if current_project is None:
        return

    seen = {item.lower() for item in current_project["technologies"]}
    for technology in _split_technologies(line):
        cleaned = _clean_text(technology)
        if not cleaned:
            continue

        cleaned = project_utils._strip_link_metadata(cleaned)
        if not cleaned:
            continue

        if cleaned.lower() in seen:
            continue

        current_project["technologies"].append(cleaned)
        seen.add(cleaned.lower())


def _normalize_project(project: dict[str, Any]) -> dict[str, Any]:
    """Normalize a project entry by cleaning its fields and dropping empty values."""
    title = _clean_text(str(project.get("title", "")))
    technologies = [_clean_text(item) for item in project.get("technologies", []) if _clean_text(item)]
    descriptions = [_clean_text(item) for item in project.get("description", []) if _clean_text(item)]

    return {
        "title": title,
        "technologies": technologies,
        "description": descriptions,
    }


def extract_projects(lines: list[str]) -> list[dict[str, Any]]:
    """Extract projects from a Projects section represented as a list of lines."""
    projects: list[dict[str, Any]] = []
    current_project: dict[str, Any] | None = None

    for line in lines:
        cleaned = project_utils.clean_project_line(line)
        if project_utils.is_empty_line(cleaned):
            continue

        if _looks_like_section_heading(cleaned):
            continue

        if project_utils.looks_like_new_section(cleaned):
            break

        if current_project is not None and (
            project_utils.looks_like_technology_line(cleaned)
            or _looks_like_single_token_technology(cleaned)
            or project_utils._looks_like_technology_heavy_line(cleaned)
        ):
            if not project_utils.looks_like_project_title(cleaned):
                _add_technologies(current_project, cleaned)
                continue

        if _looks_like_new_project_title(cleaned, current_project):
            _finish_current_project(current_project, projects)
            current_project = _start_new_project(cleaned)
            continue

        if current_project is None:
            continue

        if project_utils.looks_like_description(cleaned):
            _add_description(current_project, cleaned)

    _finish_current_project(current_project, projects)

    normalized_projects = [_normalize_project(project) for project in projects]
    return [project for project in normalized_projects if project["title"]]
