"""Contact extraction for the Version 2 resume parser."""

from __future__ import annotations

import re

# Compiled regex patterns used across the contact parser.
EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}(?!\d)")
LINKEDIN_PATTERN = re.compile(r"https?://(?:www\.)?linkedin\.com/[^\s]+|(?:www\.)?linkedin\.com/[^\s]+")
GITHUB_PATTERN = re.compile(r"https?://(?:www\.)?github\.com/[^\s]+|(?:www\.)?github\.com/[^\s]+")
PORTFOLIO_PATTERN = re.compile(r"https?://[^\s]+")


def _clean_lines(header_lines: list[str]) -> list[str]:
    """Return non-empty header lines for scanning."""
    return [line.strip() for line in header_lines if line and line.strip()]


def extract_email(header_lines: list[str]) -> str | None:
    """Return the first valid email present in the header lines."""
    for line in _clean_lines(header_lines):
        match = EMAIL_PATTERN.search(line)
        if match:
            return match.group(0)
    return None


def extract_phone(header_lines: list[str]) -> str | None:
    """Return the first valid phone number present in the header lines."""
    for line in _clean_lines(header_lines):
        match = PHONE_PATTERN.search(line)
        if match:
            phone_value = match.group(0)
            digits_only = re.sub(r"[^0-9]", "", phone_value)
            if 10 <= len(digits_only) <= 12:
                return phone_value
    return None


def extract_linkedin(header_lines: list[str]) -> str | None:
    """Return the first LinkedIn URL present in the header lines."""
    for line in _clean_lines(header_lines):
        match = LINKEDIN_PATTERN.search(line)
        if match:
            return match.group(0)
    return None


def extract_github(header_lines: list[str]) -> str | None:
    """Return the first GitHub URL present in the header lines."""
    for line in _clean_lines(header_lines):
        match = GITHUB_PATTERN.search(line)
        if match:
            return match.group(0)
    return None


def extract_portfolio(header_lines: list[str]) -> str | None:
    """Return a portfolio URL if one is present and it is not LinkedIn or GitHub."""
    for line in _clean_lines(header_lines):
        match = PORTFOLIO_PATTERN.search(line)
        if not match:
            continue

        url = match.group(0)
        lowered = url.lower()
        if "linkedin.com" in lowered or "github.com" in lowered:
            continue

        return url
    return None


def extract_contact_info(header_lines: list[str]) -> dict[str, str | None]:
    """Extract a structured contact dictionary from the resume header."""
    return {
        "email": extract_email(header_lines),
        "phone": extract_phone(header_lines),
        "linkedin": extract_linkedin(header_lines),
        "github": extract_github(header_lines),
        "portfolio": extract_portfolio(header_lines),
    }
