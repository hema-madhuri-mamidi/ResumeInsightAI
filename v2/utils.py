"""Utility helpers for the Version 2 parser."""

from __future__ import annotations


def normalize_text(text: str) -> str:
    """
    Normalize whitespace in resume text.

    TODO: Implement shared text normalization in Version 2.
    """
    return text.strip()
