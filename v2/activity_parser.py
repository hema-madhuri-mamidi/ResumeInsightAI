"""Activity extraction for the Version 2 resume parser."""

from __future__ import annotations

import re

# Compiled regex patterns used by the activity parser.
PAGE_NUMBER_PATTERN = re.compile(r"^\d+$")
URL_PATTERN = re.compile(r"https?://[^\s]+|www\.[^\s]+")
EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}(?!\d)")
BULLET_PATTERN = re.compile(r"^(?:[•\-*]+|\d+[.)-]?|\d{1,2}[.)-])\s*")
MULTISPACE_PATTERN = re.compile(r"\s+")
CONTINUATION_PREFIXES = (
    "participant",
    "member",
    "leader",
    "coordinator",
    "volunteer",
    "organizer",
    "team",
    "committee",
    "mentor",
    "intern",
    "winner",
    "finalist",
    "runner-up",
    "speaker",
    "delegate",
    "representative",
    "co-founder",
    "chair",
    "president",
    "secretary",
    "treasurer",
)


def _clean_lines(lines: list[str]) -> list[str]:
    """Return non-empty activity lines with surrounding whitespace removed."""
    return [line.strip() for line in lines if line and line.strip()]


def _is_noise(line: str) -> bool:
    """Return True for lines that are not meaningful activity entries."""
    cleaned = line.strip()
    if not cleaned:
        return True
    if PAGE_NUMBER_PATTERN.fullmatch(cleaned):
        return True
    if URL_PATTERN.search(cleaned):
        return True
    if EMAIL_PATTERN.search(cleaned):
        return True
    if PHONE_PATTERN.search(cleaned):
        return True
    return False


def _normalize(line: str) -> str:
    """Normalize whitespace and remove simple bullet or numbering prefixes."""
    cleaned = line.strip()
    cleaned = BULLET_PATTERN.sub("", cleaned)
    cleaned = MULTISPACE_PATTERN.sub(" ", cleaned)
    return cleaned.strip()


def _is_continuation(previous: str, current: str) -> bool:
    """Return True when the current line likely continues the previous activity."""
    if not previous or not current:
        return False

    lowered = current.casefold()
    if lowered and lowered[0].islower():
        return True

    return any(lowered.startswith(prefix) for prefix in CONTINUATION_PREFIXES)


def extract_activities(lines: list[str]) -> list[str]:
    """Extract a clean ordered list of unique activities from the section lines."""
    cleaned_lines = _clean_lines(lines)
    filtered_lines = [line for line in cleaned_lines if not _is_noise(line)]

    merged: list[str] = []
    for line in filtered_lines:
        normalized_line = _normalize(line)
        if not normalized_line:
            continue

        if merged and _is_continuation(merged[-1], normalized_line):
            merged[-1] = f"{merged[-1]} {normalized_line}"
        else:
            merged.append(normalized_line)

    activities: list[str] = []
    seen: set[str] = set()

    for item in merged:
        normalized_key = item.casefold()
        if normalized_key in seen:
            continue
        seen.add(normalized_key)
        activities.append(item)

    return activities
