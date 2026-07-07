"""Name extraction for the Version 2 resume parser."""

from __future__ import annotations

import re

from .constants import SECTION_HEADINGS

# Heuristic constants used by the name parser.
MIN_NAME_WORDS = 2
MAX_NAME_WORDS = 5
NAME_WORD_SCORE = 20
NAME_LENGTH_SCORE = 40
UPPERCASE_NAME_SCORE = 20
EARLY_HEADER_SCORE = 15
REJECT_SCORE = -100
HEADING_SCORE_PENALTY = -50

EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}(?!\d)")
URL_PATTERN = re.compile(r"https?://[^\s]+|www\.[^\s]+")
LINKEDIN_PATTERN = re.compile(r"linkedin\.com", re.IGNORECASE)
GITHUB_PATTERN = re.compile(r"github\.com", re.IGNORECASE)
PORTFOLIO_PATTERN = re.compile(r"portfolio", re.IGNORECASE)

RESERVED_WORDS = {
    "resume",
    "curriculum vitae",
    "cv",
    "profile",
    "summary",
    "objective",
    "education",
    "skills",
    "experience",
    "projects",
    "certifications",
    "activities",
}

SECTION_LABELS = {
    heading.lower()
    for heading_variants in SECTION_HEADINGS.values()
    for heading in heading_variants
}


def _clean_lines(header_lines: list[str]) -> list[str]:
    """Return non-empty header lines for scanning."""
    return [line.strip() for line in header_lines if line and line.strip()]


def is_probable_name(line: str) -> bool:
    """Return True when a header line looks like a personal name."""
    cleaned = line.strip()
    if not cleaned:
        return False

    lowered = cleaned.lower()

    # Reject obvious non-name content.
    if EMAIL_PATTERN.search(cleaned):
        return False
    if PHONE_PATTERN.search(cleaned):
        return False
    if URL_PATTERN.search(cleaned):
        return False
    if LINKEDIN_PATTERN.search(cleaned) or GITHUB_PATTERN.search(cleaned):
        return False
    if PORTFOLIO_PATTERN.search(cleaned):
        return False

    # Reject known resume section labels and generic words.
    if lowered in RESERVED_WORDS:
        return False
    if any(token in lowered for token in RESERVED_WORDS):
        return False
    if lowered in SECTION_LABELS:
        return False

    # Reject headings and lines with too much punctuation or digits.
    if re.fullmatch(r"[^A-Za-z\s]+", cleaned):
        return False
    if any(char.isdigit() for char in cleaned):
        return False

    words = cleaned.split()
    if not (MIN_NAME_WORDS <= len(words) <= MAX_NAME_WORDS):
        return False

    if len(cleaned) < 2:
        return False

    # Avoid names with excessive punctuation such as repeated separators.
    if re.search(r"[\-_/]{2,}", cleaned):
        return False

    return True


def score_name(line: str) -> int:
    """Return a heuristic score for how likely a line is a person's name."""
    cleaned = line.strip()
    score = 0

    if EMAIL_PATTERN.search(cleaned):
        return REJECT_SCORE
    if PHONE_PATTERN.search(cleaned):
        return REJECT_SCORE
    if URL_PATTERN.search(cleaned):
        return REJECT_SCORE
    if any(char.isdigit() for char in cleaned):
        return REJECT_SCORE

    words = cleaned.split()
    if MIN_NAME_WORDS <= len(words) <= MAX_NAME_WORDS:
        score += NAME_LENGTH_SCORE

    if all(word[0].isupper() for word in words if word):
        score += NAME_WORD_SCORE * len(words)

    if cleaned.isupper():
        score += UPPERCASE_NAME_SCORE

    if cleaned.lower() in SECTION_LABELS:
        score += HEADING_SCORE_PENALTY

    return score


def extract_name(header_lines: list[str]) -> str | None:
    """Return the highest-scoring probable name from the header lines."""
    cleaned_lines = _clean_lines(header_lines)
    candidates: list[tuple[int, str]] = []

    for index, line in enumerate(cleaned_lines[:5]):
        if not is_probable_name(line):
            continue

        score = score_name(line)
        if index < 5:
            score += EARLY_HEADER_SCORE

        # Penalize obvious heading-like lines.
        if line.lower() in SECTION_LABELS:
            score += HEADING_SCORE_PENALTY

        candidates.append((score, line))

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]
