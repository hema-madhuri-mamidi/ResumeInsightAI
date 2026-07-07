"""Section detection for the Version 2 resume parser."""

from __future__ import annotations

import re

from .constants import SECTION_HEADINGS

_ACTIVITY_SECTION_HEADINGS = {
    "activities",
    "activity",
    "activities competitions",
    "activities and competitions",
    "extracurricular",
    "extracurricular activities",
    "achievements activities",
}

_SECTION_BOUNDARY_HEADINGS = {
    "achievements",
    "activities",
    "activity",
    "activities competitions",
    "interests",
    "languages",
    "references",
    "certifications",
    "certificates",
    "awards",
    "leadership",
    "volunteer",
    "projects",
    "experience",
}


def normalize_heading(line: str) -> str:
    """Normalize a heading string for exact matching against known section names."""
    normalized = re.sub(r"\s+", " ", line.strip().lower())
    normalized = normalized.rstrip(":")

    while normalized and normalized[0] in "-•*.:;":
        normalized = normalized[1:].lstrip()

    while normalized and normalized[-1] in "-•*.:;":
        normalized = normalized[:-1].rstrip()

    normalized = re.sub(r"[^a-z0-9]+", " ", normalized).strip()
    return normalized


_SECTION_HEADING_LOOKUP: dict[str, str] = {}
for canonical_key, heading_variants in SECTION_HEADINGS.items():
    for heading in heading_variants:
        _SECTION_HEADING_LOOKUP[normalize_heading(heading)] = canonical_key


def is_section_heading(line: str) -> str | None:
    """Return the canonical section key when the line matches a known heading."""
    normalized_line = normalize_heading(line)
    return _SECTION_HEADING_LOOKUP.get(normalized_line)


def is_activity_heading(line: str) -> bool:
    """Return True for activity-style headings that should terminate certifications parsing."""
    return normalize_heading(line) in _ACTIVITY_SECTION_HEADINGS


def is_section_boundary(line: str) -> bool:
    """Return True for headings that should stop skills parsing immediately."""
    return normalize_heading(line) in _SECTION_BOUNDARY_HEADINGS


def detect_sections(text: str) -> dict[str, list[str]]:
    """Split a resume into logical sections while preserving non-empty content lines."""
    sections: dict[str, list[str]] = {"header": []}
    for section_name in SECTION_HEADINGS:
        sections[section_name] = []

    current_section = "header"

    for raw_line in text.splitlines():
        if not raw_line.strip():
            continue

        section_key = is_section_heading(raw_line)
        if section_key is not None:
            current_section = section_key
            continue

        sections[current_section].append(raw_line)

    return sections
