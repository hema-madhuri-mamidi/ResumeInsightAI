"""Experience parser for the Version 2 resume parser."""

from __future__ import annotations

import re
from typing import Any

from . import project_utils

_BULLET_PREFIXES: tuple[str, ...] = ("•", "-", "*")
_MONTHS: tuple[str, ...] = (
    "jan",
    "january",
    "feb",
    "february",
    "mar",
    "march",
    "apr",
    "april",
    "may",
    "jun",
    "june",
    "jul",
    "july",
    "aug",
    "august",
    "sep",
    "sept",
    "september",
    "oct",
    "october",
    "nov",
    "november",
    "dec",
    "december",
)
_SEASONS: tuple[str, ...] = ("spring", "summer", "fall", "winter")
_JOB_TITLE_TOKENS: tuple[str, ...] = (
    "engineer",
    "developer",
    "analyst",
    "manager",
    "lead",
    "intern",
    "consultant",
    "specialist",
    "architect",
    "designer",
    "scientist",
    "director",
    "programmer",
    "admin",
    "administrator",
    "coordinator",
    "officer",
)


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


def _looks_like_duration(line: str) -> bool:
    """Return True when a line looks like an employment duration."""
    cleaned = _clean_text(line)
    if not cleaned:
        return False

    if cleaned.startswith(_BULLET_PREFIXES):
        return False

    lowered = cleaned.lower()
    if any(marker in lowered for marker in ("@", "http://", "https://", "www.")):
        return False

    if re.search(r"\b\d{10}\b", cleaned) or re.search(r"\b(?:\+?\d[\d\s().-]{7,}\d)\b", cleaned):
        return False

    if re.search(r"\b\d{4}\b", cleaned):
        if any(token in lowered for token in ("present", "now", "internship", "trainee", "contract")):
            return True

        if any(token in lowered for token in ("-", "–", "—")):
            return True

        if any(token in lowered for token in _MONTHS + _SEASONS):
            return True

    if any(token in lowered for token in _MONTHS + _SEASONS):
        return True

    return lowered.endswith("internship") or lowered.endswith("internships")


def _looks_like_section_heading(line: str) -> bool:
    """Return True for obvious standalone section headings that should end experience parsing."""
    cleaned = _clean_text(line)
    if not cleaned:
        return False

    normalized = re.sub(r"[^a-z0-9]+", " ", cleaned.lower()).strip()
    if not normalized:
        return False

    headings = {
        "experience",
        "work experience",
        "professional experience",
        "projects",
        "project",
        "skills",
        "technical skills",
        "education",
        "certifications",
        "certificates",
        "activities",
        "achievements",
        "awards",
        "interests",
        "hobbies",
        "interests hobbies",
        "languages",
        "publications",
        "references",
        "referees",
    }
    return normalized in headings


def _looks_like_reference_line(line: str) -> bool:
    """Return True for reference/help lines that should not become experience entries."""
    cleaned = _clean_text(line)
    if not cleaned:
        return False

    lowered = cleaned.lower()
    if lowered.startswith(("references", "referees", "contact details available on request", "available on request")):
        return True

    return lowered.startswith(("contact details", "available on request"))


def _looks_like_template_text(line: str) -> bool:
    """Return True when a line is template/help text that should be ignored."""
    cleaned = _clean_text(line)
    if not cleaned:
        return False

    lowered = cleaned.lower()
    if lowered.startswith(("tip:", "example:", "sample:", "(tip")):
        return True

    if "include" in lowered:
        return True

    if "when applying" in lowered or "advertised roles" in lowered:
        return True

    if "where and how" in lowered or "for example" in lowered or "e.g." in lowered:
        return True

    return False


def _looks_like_contact_line(line: str) -> bool:
    """Return True when a line is obvious contact information rather than experience content."""
    cleaned = _clean_text(line)
    if not cleaned:
        return False

    if re.search(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", cleaned):
        return True

    if re.fullmatch(r"[\+\d().\-\s]{7,}", cleaned) and not re.search(r"[a-zA-Z]", cleaned):
        return True

    return False


def _parse_inline_experience(line: str) -> tuple[str, str, str] | None:
    """Parse a compact line such as '2023-2024 Software Engineer, ABC Pvt Ltd'."""
    cleaned = _clean_text(line)
    if not cleaned or cleaned.startswith(_BULLET_PREFIXES):
        return None

    if "," not in cleaned:
        return None

    duration_part, remainder = [part.strip() for part in cleaned.split(",", 1)]
    if not remainder:
        return None

    title_match = re.match(r"^(?P<duration>.+?)\s+(?P<title>.+)$", duration_part)
    if not title_match:
        return None

    duration = title_match.group("duration").strip()
    title = title_match.group("title").strip()
    company = remainder.strip()

    if not _looks_like_duration(duration) or not _looks_like_job_title(title):
        return None

    return duration, title, company


def _looks_like_company(line: str) -> bool:
    """Return True when a line looks like a company or organization name."""
    cleaned = _clean_text(line)
    if not cleaned:
        return False

    if cleaned.startswith(_BULLET_PREFIXES):
        return False

    lowered = cleaned.lower()
    if any(marker in lowered for marker in ("@", "http://", "https://", "www.")):
        return False

    if re.search(r"\b\d{10}\b", cleaned) or re.search(r"\b(?:\+?\d[\d\s().-]{7,}\d)\b", cleaned):
        return False

    if _looks_like_duration(cleaned):
        return False

    if any(token in lowered for token in _JOB_TITLE_TOKENS):
        return False

    if cleaned.endswith((".", "!", "?")):
        return False

    if len(cleaned.split()) > 8:
        return False

    if len(cleaned) > 60:
        return False

    if re.search(r"[,;|/]", cleaned):
        return False

    return True


def _looks_like_job_title(line: str) -> bool:
    """Return True when a line looks like a job title rather than a description or company."""
    cleaned = _clean_text(line)
    if not cleaned:
        return False

    if cleaned.lower() in {"experience", "work experience", "professional experience"}:
        return False

    if cleaned.startswith(_BULLET_PREFIXES):
        return False

    lowered = cleaned.lower()
    if any(token in lowered for token in _JOB_TITLE_TOKENS):
        return True

    if _looks_like_duration(cleaned) or _looks_like_company(cleaned):
        return False

    if cleaned.endswith((".", "!", "?")):
        return False

    if len(cleaned.split()) > 8:
        return False

    return True


def _looks_like_description(line: str) -> bool:
    """Return True when a line looks like a description bullet or sentence."""
    cleaned = _clean_text(line)
    if not cleaned:
        return False

    if cleaned.startswith(_BULLET_PREFIXES):
        return True

    lowered = cleaned.lower()
    if lowered.startswith(("built", "developed", "created", "designed", "implemented", "engineered", "led", "worked", "used", "responsible", "improved", "delivered", "managed", "maintained", "contributed")):
        return True

    if cleaned.endswith((".", "!", "?")):
        return True

    if len(cleaned.split()) >= 6 and not _looks_like_company(cleaned) and not _looks_like_job_title(cleaned):
        return True

    return False


def _looks_like_technology_line(line: str) -> bool:
    """Return True when a line looks like a technology list."""
    cleaned = _clean_text(line)
    if not cleaned:
        return False

    if cleaned.startswith(_BULLET_PREFIXES):
        return False

    if _looks_like_job_title(cleaned) or _looks_like_company(cleaned) or _looks_like_duration(cleaned):
        return False

    tokens = _split_technologies(cleaned)
    if not tokens:
        return False

    if any(token in cleaned for token in [",", "|", "/", ";", "•"]):
        return len(tokens) >= 2

    technology_hits = sum(1 for token in tokens if token.lower() in project_utils.COMMON_TECHNOLOGIES)
    return technology_hits >= 2


def _start_new_experience(title: str) -> dict[str, Any]:
    """Create a new experience entry with empty metadata."""
    return {
        "title": title,
        "company": "",
        "organization": "",
        "duration": "",
        "technologies": [],
        "description": [],
    }


def _finish_current_experience(current_experience: dict[str, Any] | None, experiences: list[dict[str, Any]]) -> None:
    """Append a completed experience when it has a valid title."""
    if current_experience is None:
        return

    title = _clean_text(str(current_experience.get("title", "")))
    if title:
        experiences.append(current_experience)


def _add_description(current_experience: dict[str, Any] | None, line: str) -> None:
    """Append a description line to the current experience if one exists."""
    if current_experience is None:
        return

    cleaned = _clean_text(line)
    if not cleaned:
        return

    if cleaned.startswith(_BULLET_PREFIXES):
        cleaned = cleaned[1:].lstrip()

    if cleaned:
        current_experience["description"].append(cleaned)


def _add_technologies(current_experience: dict[str, Any] | None, line: str) -> None:
    """Add technologies from a line to the current experience without duplicates."""
    if current_experience is None:
        return

    seen = {item.lower() for item in current_experience["technologies"]}
    for technology in _split_technologies(line):
        cleaned = _clean_text(technology)
        if not cleaned:
            continue

        if cleaned.lower() in seen:
            continue

        current_experience["technologies"].append(cleaned)
        seen.add(cleaned.lower())


def _capture_company_and_duration(current_experience: dict[str, Any] | None, line: str) -> bool:
    """Populate company and duration from a line when the values are separated by a pipe."""
    if current_experience is None:
        return False

    cleaned = _clean_text(line)
    if not cleaned:
        return False

    if "|" not in cleaned:
        return False

    company_part, duration_part = [part.strip() for part in cleaned.split("|", 1)]
    captured = False

    if company_part and not current_experience.get("company") and _looks_like_company(company_part):
        current_experience["company"] = company_part
        current_experience["organization"] = company_part
        captured = True

    if duration_part and not current_experience.get("duration") and _looks_like_duration(duration_part):
        current_experience["duration"] = duration_part
        captured = True

    return captured


def _normalize_experience(experience: dict[str, Any]) -> dict[str, Any]:
    """Normalize an experience entry by cleaning fields and dropping empty values."""
    title = _clean_text(str(experience.get("title", "")))
    company = _clean_text(str(experience.get("company", "")))
    organization = _clean_text(str(experience.get("organization", "")))
    duration = _clean_text(str(experience.get("duration", "")))

    technologies: list[str] = []
    seen_technologies: set[str] = set()
    for item in experience.get("technologies", []):
        cleaned = _clean_text(str(item))
        if not cleaned:
            continue

        lowered = cleaned.lower()
        if lowered in seen_technologies:
            continue

        technologies.append(cleaned)
        seen_technologies.add(lowered)

    descriptions: list[str] = []
    seen_descriptions: set[str] = set()
    for item in experience.get("description", []):
        cleaned = _clean_text(str(item))
        if not cleaned:
            continue

        lowered = cleaned.lower()
        if lowered in seen_descriptions:
            continue

        descriptions.append(cleaned)
        seen_descriptions.add(lowered)

    return {
        "title": title,
        "company": company or organization,
        "organization": organization or company,
        "duration": duration,
        "technologies": technologies,
        "description": descriptions,
    }


def extract_experience(lines: list[str]) -> list[dict[str, Any]]:
    """Extract experiences from an Experience section represented as a list of lines."""
    experiences: list[dict[str, Any]] = []
    current_experience: dict[str, Any] | None = None

    for line in lines:
        cleaned = project_utils.clean_project_line(line)
        if project_utils.is_empty_line(cleaned):
            continue

        if _looks_like_template_text(cleaned) or _looks_like_reference_line(cleaned):
            _finish_current_experience(current_experience, experiences)
            current_experience = None
            continue

        if _looks_like_section_heading(cleaned):
            _finish_current_experience(current_experience, experiences)
            current_experience = None
            continue

        inline_experience = _parse_inline_experience(cleaned)
        if inline_experience and current_experience is None:
            duration, title, company = inline_experience
            current_experience = _start_new_experience(title)
            current_experience["company"] = company
            current_experience["organization"] = company
            current_experience["duration"] = duration
            continue

        if _looks_like_contact_line(cleaned):
            _finish_current_experience(current_experience, experiences)
            current_experience = None
            continue

        if cleaned.startswith(("(tip", "tip:", "example")):
            _finish_current_experience(current_experience, experiences)
            current_experience = None
            continue

        if _looks_like_job_title(cleaned):
            _finish_current_experience(current_experience, experiences)
            current_experience = _start_new_experience(cleaned)
            continue

        if current_experience is None:
            continue

        if _capture_company_and_duration(current_experience, cleaned):
            continue

        if not current_experience.get("company") and _looks_like_company(cleaned):
            current_experience["company"] = cleaned
            current_experience["organization"] = cleaned
            continue

        if not current_experience.get("duration") and _looks_like_duration(cleaned):
            current_experience["duration"] = cleaned
            continue

        if _looks_like_technology_line(cleaned):
            _add_technologies(current_experience, cleaned)
            continue

        if _looks_like_description(cleaned):
            _add_description(current_experience, cleaned)

    _finish_current_experience(current_experience, experiences)

    normalized_experiences = [_normalize_experience(experience) for experience in experiences]
    return [experience for experience in normalized_experiences if experience["title"]]
