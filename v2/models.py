"""Data models for structured resume parsing output."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ContactInfo:
    """Structured contact information."""

    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None


@dataclass
class EducationEntry:
    """Structured education entry."""

    institution: str | None = None
    degree: str | None = None
    field: str | None = None
    years: str | None = None
    details: list[str] = field(default_factory=list)


@dataclass
class ProjectEntry:
    """Structured project entry."""

    title: str | None = None
    technologies: list[str] = field(default_factory=list)
    description: list[str] = field(default_factory=list)


@dataclass
class ExperienceEntry:
    """Structured experience entry."""

    title: str | None = None
    organization: str | None = None
    duration: str | None = None
    description: list[str] = field(default_factory=list)


@dataclass
class CertificationEntry:
    """Structured certification entry."""

    name: str | None = None
    issuer: str | None = None
    year: str | None = None
