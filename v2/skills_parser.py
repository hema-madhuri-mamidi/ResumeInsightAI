"""Skills extraction for the Version 2 resume parser."""

from __future__ import annotations

import re

from .section_detector import is_section_boundary

# Category labels that should be removed before skill extraction.
IGNORED_CATEGORY_LABELS = {
    "languages",
    "programming languages",
    "frameworks",
    "libraries",
    "tools",
    "databases",
    "platforms",
    "technologies",
    "technical skills",
    "core skills",
}

# Compiled regex helpers used throughout the parser.
TEMPLATE_PREFIX_PATTERN = re.compile(
    r"^(?:\(tip:|tip:|example:|e\.g\.|for example)",
    re.IGNORECASE,
)
CATEGORY_PREFIX_PATTERN = re.compile(
    rf"^(?:{'|'.join(re.escape(label) for label in IGNORED_CATEGORY_LABELS)})\s*[:\-]\s*",
    re.IGNORECASE,
)
SEPARATOR_PATTERN = re.compile(r"[,;|/•]")
MULTISPACE_PATTERN = re.compile(r"\s{2,}")
WHITESPACE_PATTERN = re.compile(r"\s+")


def _clean_lines(lines: list[str]) -> list[str]:
    """Return non-empty lines from the skills section."""
    return [line.strip() for line in lines if line and line.strip()]


def _is_template_instruction(line: str) -> bool:
    """Return True for template/help text that should never appear in parsed skills."""
    cleaned = line.strip()
    if not cleaned:
        return False

    lowered = cleaned.lower()
    if TEMPLATE_PREFIX_PATTERN.match(cleaned):
        return True

    if lowered.startswith("for example"):
        return True

    if lowered.startswith("e.g."):
        return True

    if lowered.startswith("example"):
        return True

    if "include" in lowered:
        return True

    if "when applying" in lowered or "advertised roles" in lowered:
        return True

    if "where and how" in lowered:
        return True

    if lowered.startswith("add your skills"):
        return True

    if lowered.startswith("list your skills"):
        return True

    if "resume template" in lowered:
        return True

    if "template" in lowered and "skills" in lowered:
        return True

    return False


def _strip_category_prefix(line: str) -> str:
    """Remove a leading category prefix such as 'Programming Languages:' from a line."""
    cleaned = line.strip()
    if not cleaned:
        return ""

    prefix_match = CATEGORY_PREFIX_PATTERN.match(cleaned)
    if prefix_match:
        return cleaned[prefix_match.end():].strip()

    return cleaned


def _split_skill_tokens(line: str) -> list[str]:
    """Split a line into skill candidates using the allowed separators only."""
    cleaned = _strip_category_prefix(line)
    if not cleaned:
        return []

    if SEPARATOR_PATTERN.search(cleaned):
        parts = SEPARATOR_PATTERN.split(cleaned)
        tokens = [WHITESPACE_PATTERN.sub(" ", part).strip() for part in parts]
        return [token for token in tokens if token]

    if MULTISPACE_PATTERN.search(cleaned):
        return [token for token in MULTISPACE_PATTERN.split(cleaned) if token]

    # Intentionally do not split on single spaces here.
    # Future versions may use a known-skills dictionary to safely split lines such as
    # "Python Java C" without breaking multi-word skills like "Machine Learning".
    return [cleaned]


def _is_category_label(token: str) -> bool:
    """Return True for labels that describe a skill group rather than a skill."""
    normalized = WHITESPACE_PATTERN.sub(" ", token).strip().lower()
    return normalized in IGNORED_CATEGORY_LABELS


def extract_skills(lines: list[str]) -> list[str]:
    """Extract a clean ordered list of unique skills from the Skills section."""
    skills: list[str] = []
    seen: set[str] = set()

    for line in _clean_lines(lines):
        if _is_template_instruction(line):
            continue

        if is_section_boundary(line):
            break

        for token in _split_skill_tokens(line):
            if _is_category_label(token):
                continue

            normalized = WHITESPACE_PATTERN.sub(" ", token).strip()
            if not normalized:
                continue

            normalized_key = normalized.casefold()
            if normalized_key in seen:
                continue

            seen.add(normalized_key)
            skills.append(normalized)

    return skills
