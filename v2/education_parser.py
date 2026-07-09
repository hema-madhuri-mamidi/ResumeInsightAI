"""Education extraction for the Version 2 resume parser."""

from __future__ import annotations

import re

# Compiled regex patterns used across the education parser.
DEGREE_PATTERN = re.compile(
    r"\b(?:"
    r"B\.Tech|Bachelor of Technology|Bachelor of Engineering|B\.E\.|B\.Sc|BCA|"
    r"M\.Tech|MCA|MBA|Diploma|Intermediate|SSC"
    r")\b",
    re.IGNORECASE,
)

BRANCH_PATTERN = re.compile(
    r"\b(?:"
    r"Artificial Intelligence and Data Science|Computer Science and Engineering|"
    r"Electronics and Communication Engineering|Mechanical Engineering|"
    r"Information Technology|Electrical Engineering|Civil Engineering|"
    r"Computer Science|Electronics and Communication|Mechanical|"
    r"Electrical|Civil|AI and DS|CSE|ECE|IT|EEE|ME|CE"
    r")\b",
    re.IGNORECASE,
)

COLLEGE_PATTERN = re.compile(
    r"\b(?:"
    r"Vignan['’]s Institute of Information Technology|Vignan['’] s Institute of Information Technology|"
    r"IIT Madras|NIT Warangal|Anna University|University of Hyderabad|"
    r"Institute of Technology|University|College|Engineering College"
    r")\b",
    re.IGNORECASE,
)

CGPA_PATTERN = re.compile(r"(?:CGPA\s*[:=]?\s*)(\d+(?:\.\d+)?)", re.IGNORECASE)
CGPA_ALT_PATTERN = re.compile(r"\b(\d+(?:\.\d+)?)\s*/\s*10\b")
SIMPLE_CGPA_PATTERN = re.compile(r"\b(\d+(?:\.\d+)?)\b")

GRAD_YEAR_PATTERN = re.compile(r"\b(20\d{2})\b")
YEAR_RANGE_PATTERN = re.compile(r"\b(20\d{2})\s*[-–]\s*(20\d{2})\b")
EXPECTED_GRAD_PATTERN = re.compile(r"expected graduation\s*[:=]?\s*(20\d{2})", re.IGNORECASE)


def _clean_lines(lines: list[str]) -> list[str]:
    """Return non-empty education lines for processing."""
    return [line.strip() for line in lines if line and line.strip()]


def _is_ignored_line(line: str) -> bool:
    """Return True for lines that should not be treated as college names."""
    lowered = line.lower()
    if not lowered:
        return True

    if "percentage" in lowered or "%" in lowered:
        return True
    if re.fullmatch(r"\d{4}", lowered):
        return True
    if re.fullmatch(r"\d{4}\s*[-–]\s*\d{4}", lowered):
        return True
    if re.fullmatch(r"(?:cgpa|gpa)\s*[:=]?\s*\d+(?:\.\d+)?(?:\s*/\s*10)?", lowered):
        return True

    return False


def extract_degree(lines: list[str]) -> str | None:
    """Return the first recognized degree from the education section."""
    for line in _clean_lines(lines):
        match = DEGREE_PATTERN.search(line)
        if match:
            return match.group(0).strip()
    return None


def extract_branch(lines: list[str]) -> str | None:
    """Return the first recognized branch or specialization from the education section."""
    for line in _clean_lines(lines):
        match = BRANCH_PATTERN.search(line)
        if match:
            return match.group(0).strip()
    return None


def extract_college(lines: list[str]) -> str | None:
    """Return the most likely college or university name from the education section."""
    for line in _clean_lines(lines):
        cleaned_line = line
        cleaned_line = re.sub(
            r"\s*(?:cgpa|gpa)\s*[:=]?\s*\d+(?:\.\d+)?(?:\s*/\s*10)?$",
            "",
            cleaned_line,
            flags=re.IGNORECASE,
        ).strip()
        cleaned_line = re.sub(r"\s*\([^)]*\)\s*$", "", cleaned_line).strip()
        if _is_ignored_line(cleaned_line):
            continue

        match = COLLEGE_PATTERN.search(cleaned_line)
        if match:
            return match.group(0).strip()
        if DEGREE_PATTERN.search(cleaned_line):
            continue
        if BRANCH_PATTERN.search(cleaned_line):
            continue

    return None


def extract_cgpa(lines: list[str]) -> str | None:
    """Return the numeric CGPA or GPA value from the education section."""
    for line in _clean_lines(lines):
        match = CGPA_PATTERN.search(line)
        if match:
            return match.group(1)

    for line in _clean_lines(lines):
        match = CGPA_ALT_PATTERN.search(line)
        if match:
            return match.group(1)

    # Fallback for standalone numeric values that look like CGPA.
    for line in _clean_lines(lines):
        lowered = line.lower()
        if "cgpa" not in lowered and "gpa" not in lowered:
            continue
        match = SIMPLE_CGPA_PATTERN.search(line)
        if match:
            return match.group(1)

    return None


def extract_graduation_year(lines: list[str]) -> str | None:
    """Return the latest graduation year found in the education section."""
    years: list[int] = []

    for line in _clean_lines(lines):
        range_match = YEAR_RANGE_PATTERN.search(line)
        if range_match:
            years.append(int(range_match.group(2)))
            continue

        expected_match = EXPECTED_GRAD_PATTERN.search(line)
        if expected_match:
            years.append(int(expected_match.group(1)))
            continue

        year_match = GRAD_YEAR_PATTERN.search(line)
        if year_match:
            years.append(int(year_match.group(1)))

    if not years:
        return None

    return str(max(years))


def extract_education(lines: list[str]) -> dict[str, str | None]:
    """Extract a structured education summary from the education section."""
    return {
        "degree": extract_degree(lines),
        "branch": extract_branch(lines),
        "college": extract_college(lines),
        "cgpa": extract_cgpa(lines),
        "graduation_year": extract_graduation_year(lines),
    }
