"""Utility helpers for classifying project-section lines in Version 2."""

from __future__ import annotations

import re
from typing import Final

_BULLET_PREFIXES: Final[tuple[str, ...]] = ("•", "-", "*")
_URL_PATTERN: Final[re.Pattern[str]] = re.compile(r"https?://", re.IGNORECASE)
_EMAIL_PATTERN: Final[re.Pattern[str]] = re.compile(r"@")
_PHONE_PATTERN: Final[re.Pattern[str]] = re.compile(r"\b\d{10}\b")
_TECH_SEPARATOR_PATTERN: Final[re.Pattern[str]] = re.compile(r"[,;|/•]")
ACTION_VERBS: Final[tuple[str, ...]] = (
    "built",
    "developed",
    "created",
    "designed",
    "implemented",
    "engineered",
    "led",
    "worked",
    "used",
    "responsible",
    "architected",
    "leading",
)
_LINK_METADATA_TOKENS: Final[tuple[str, ...]] = (
    "live demo",
    "github",
    "render",
    "vercel",
    "netlify",
    "railway",
    "team lead",
    "deployed",
    "ongoing",
    "demo",
)
COMMON_TECHNOLOGIES: Final[frozenset[str]] = frozenset(
    {
        "python",
        "django",
        "react",
        "sql",
        "flask",
        "tensorflow",
        "pytorch",
        "java",
        "javascript",
        "typescript",
        "c++",
        "c",
        "html",
        "css",
        "node",
        "express",
        "fastapi",
        "pandas",
        "numpy",
        "opencv",
        "spark",
        "aws",
        "azure",
        "docker",
        "kubernetes",
        "linux",
        "git",
        "github",
        "mongodb",
        "postgresql",
        "mysql",
        "redis",
        "rest",
        "api",
        "keras",
        "matplotlib",
        "seaborn",
        "scikit-learn",
        "bootstrap",
        "tailwind",
        "nextjs",
        "vue",
        "angular",
        "pytest",
    }
)


def clean_project_line(line: str) -> str:
    """Return a trimmed line with collapsed internal whitespace."""
    if not line:
        return ""

    normalized = re.sub(r"\s+", " ", line.strip())
    return normalized


def is_empty_line(line: str) -> bool:
    """Return True when the line contains no meaningful content."""
    return not clean_project_line(line)


def looks_like_new_section(line: str) -> bool:
    """Return True when a line looks like a section heading that should end the Projects section."""
    cleaned = clean_project_line(line)
    if not cleaned:
        return False

    normalized = re.sub(r"[^a-z0-9]+", " ", cleaned.lower()).strip()
    if not normalized:
        return False

    headings = {
        "experience",
        "work experience",
        "professional experience",
        "skills",
        "technical skills",
        "education",
        "certifications",
        "certificates",
        "activities",
        "extracurricular activities",
        "achievements",
        "awards",
        "publications",
        "research",
        "leadership",
        "volunteer experience",
        "positions of responsibility",
        "interests",
        "hobbies",
        "languages",
        "additional learning",
        "trainings",
        "workshops",
        "participations",
    }

    return normalized in headings


def _starts_with_action_verb(line: str) -> bool:
    """Return True when the line begins with a common action verb."""
    cleaned = clean_project_line(line)
    if not cleaned:
        return False

    first_word = cleaned.split()[0].lower()
    return first_word in ACTION_VERBS


def _contains_multiple_sentences(line: str) -> bool:
    """Return True when the line appears to contain more than one sentence."""
    cleaned = clean_project_line(line)
    if not cleaned:
        return False

    sentence_count = len(re.split(r"(?<=[.!?])\s+", cleaned))
    return sentence_count > 1


def _tokenize_technology_candidates(line: str) -> list[str]:
    """Split a line into candidate technology tokens."""
    cleaned = clean_project_line(line)
    if not cleaned:
        return []

    return [token for token in re.split(r"[\s,|/•]+", cleaned) if token]


def _strip_classification_metadata(line: str) -> str:
    """Remove obvious link/deployment metadata before classifying a line."""
    cleaned = clean_project_line(line)
    if not cleaned:
        return ""

    if "|" in cleaned:
        parts = [part.strip() for part in re.split(r"\|", cleaned) if part.strip()]
        if len(parts) > 1:
            cleaned = parts[0]

    for token in _LINK_METADATA_TOKENS:
        if token in cleaned.lower():
            cleaned = re.sub(rf"(?<!\w){re.escape(token)}(?!\w)", "", cleaned, flags=re.IGNORECASE).strip()

    cleaned = re.sub(r"\s*\((?:deployed|live demo|demo|ongoing)\s*\)", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*\[(.*?)\]", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" -–—")
    return cleaned


def _looks_like_technology_heavy_line(line: str) -> bool:
    """Return True when a line is a short, structured technology list rather than a sentence."""
    cleaned = clean_project_line(line)
    if not cleaned:
        return False

    if cleaned.startswith(_BULLET_PREFIXES):
        return False

    if looks_like_new_section(cleaned):
        return False

    if _starts_with_action_verb(cleaned):
        return False

    if cleaned.endswith((".", "!", "?")):
        return False

    candidate = _strip_classification_metadata(cleaned)
    if not candidate:
        return False

    tokens = _tokenize_technology_candidates(candidate)
    if not tokens:
        return False

    if len(tokens) > 6:
        return False

    stop_words = {"such", "as", "using", "used", "with", "for", "and", "or", "the", "a", "an", "this", "that", "these", "those"}
    if any(token.lower() in stop_words for token in tokens):
        return False

    technology_hits = sum(1 for token in tokens if token.lower() in COMMON_TECHNOLOGIES)
    if technology_hits >= 2:
        return True

    if _TECH_SEPARATOR_PATTERN.search(candidate) and len(tokens) >= 2:
        return True

    return False


def _strip_link_metadata(title: str) -> str:
    """Remove common link and deployment metadata from a project title."""
    cleaned = clean_project_line(title)
    if not cleaned:
        return ""

    parts = [part.strip() for part in re.split(r"\|", cleaned) if part.strip()]
    if len(parts) > 1:
        cleaned = parts[0]

    if "(" in cleaned and ")" in cleaned:
        prefix, suffix = cleaned.split("(", 1)
        parenthetical = suffix.rsplit(")", 1)[0]
        if prefix.strip() and _looks_like_technology_heavy_line(parenthetical):
            cleaned = prefix.strip()
        elif prefix.strip() and parenthetical.lower() in {"deployed", "live demo", "demo", "ongoing"}:
            cleaned = prefix.strip()

    for token in _LINK_METADATA_TOKENS:
        if token in cleaned.lower():
            cleaned = re.sub(rf"\b{re.escape(token)}\b", "", cleaned, flags=re.IGNORECASE).strip()

    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"\s*\((?:deployed|live demo|demo)\s*\)", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*\[(.*?)\]", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" -–—")
    return cleaned


def looks_like_project_title(line: str) -> bool:
    """Return True when a line looks like a standalone project title."""
    cleaned = clean_project_line(line)
    if not cleaned:
        return False

    if looks_like_new_section(cleaned):
        return False

    if cleaned.startswith(_BULLET_PREFIXES):
        return False

    if "(" in cleaned and ")" in cleaned:
        prefix, suffix = cleaned.split("(", 1)
        parenthetical = suffix.rsplit(")", 1)[0]
        if prefix.strip() and _looks_like_technology_heavy_line(parenthetical):
            return True

        if prefix.strip() and len(prefix.split()) <= 8 and not _starts_with_action_verb(prefix):
            return True

    if _looks_like_technology_heavy_line(cleaned):
        return False

    candidate = _strip_classification_metadata(cleaned)
    if candidate and _TECH_SEPARATOR_PATTERN.search(candidate):
        tokens = _tokenize_technology_candidates(candidate)
        if len(tokens) >= 2 and sum(1 for token in tokens if token.lower() in COMMON_TECHNOLOGIES) >= 2:
            return False

    candidate = _strip_classification_metadata(cleaned)
    if candidate and len(candidate.split()) > 12:
        return False
    if len(cleaned.split()) > 12 and not candidate:
        return False

    if _URL_PATTERN.search(cleaned):
        return False

    if _EMAIL_PATTERN.search(cleaned):
        return False

    if _PHONE_PATTERN.search(cleaned):
        return False

    if _starts_with_action_verb(cleaned):
        return False

    if cleaned.endswith((".", "!", "?")):
        return False

    if _contains_multiple_sentences(cleaned):
        return False

    if candidate and re.fullmatch(r"[A-Za-z0-9.+/#-]+", candidate):
        return False

    return True


def looks_like_description(line: str) -> bool:
    """Return True when a line looks like a project description bullet or sentence."""
    cleaned = clean_project_line(line)
    if not cleaned:
        return False

    if cleaned.startswith(_BULLET_PREFIXES):
        return True

    if _looks_like_technology_heavy_line(cleaned):
        return False

    if _starts_with_action_verb(cleaned):
        return True

    if cleaned.endswith((".", "!", "?")):
        return True

    if len(cleaned.split()) >= 8 and not looks_like_project_title(cleaned):
        return True

    if looks_like_project_title(cleaned):
        return False

    return True


def looks_like_technology_line(line: str) -> bool:
    """Return True when a line looks like a technology list."""
    cleaned = clean_project_line(line)
    if not cleaned:
        return False

    if cleaned.startswith(_BULLET_PREFIXES):
        return False

    if looks_like_project_title(cleaned):
        return False

    if _starts_with_action_verb(cleaned):
        return False

    return _looks_like_technology_heavy_line(cleaned)
