"""Rule-based job matching utilities for parsed resume data."""

from __future__ import annotations

import re
from typing import Any

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "our",
    "the",
    "this",
    "to",
    "with",
    "within",
    "your",
}

GENERIC_TERMS = {
    "backend",
    "fronted",
    "frontend",
    "full",
    "stack",
    "developer",
    "engineer",
    "experience",
    "experienced",
    "team",
    "working",
    "work",
    "build",
    "building",
    "strong",
    "good",
    "required",
    "seeking",
    "looking",
    "skills",
    "knowledge",
    "ability",
    "abilities",
    "role",
    "responsibilities",
    "candidate",
    "candidates",
    "background",
    "understanding",
    "related",
    "years",
    "year",
}

TECHNOLOGY_PATTERNS = [
    (re.compile(r"\b(?:rest\s+api|rest\s+apis|restful\s+api)\b"), "REST API"),
    (re.compile(r"\b(?:graphql)\b"), "GraphQL"),
    (re.compile(r"\b(?:mysql\s+database|mysql)\b"), "MySQL"),
    (re.compile(r"\b(?:postgresql|postgres)\b"), "PostgreSQL"),
    (re.compile(r"\b(?:sqlite)\b"), "SQLite"),
    (re.compile(r"\b(?:mongodb)\b"), "MongoDB"),
    (re.compile(r"\b(?:github\.com|github)\b"), "GitHub"),
    (re.compile(r"\b(?:javascript|js)\b"), "JavaScript"),
    (re.compile(r"\b(?:html5|html)\b"), "HTML"),
    (re.compile(r"\b(?:css3|css)\b"), "CSS"),
    (re.compile(r"\b(?:bootstrap)\b"), "Bootstrap"),
    (re.compile(r"\b(?:react(?:js)?|react\.js|react\s*js)\b"), "React"),
    (re.compile(r"\b(?:angular)\b"), "Angular"),
    (re.compile(r"\b(?:vue)\b"), "Vue"),
    (re.compile(r"\b(?:node(?:\.js)?|nodejs|node\s*js)\b"), "Node.js"),
    (re.compile(r"\b(?:express(?:\.js)?)\b"), "Express.js"),
    (re.compile(r"\b(?:django)\b"), "Django"),
    (re.compile(r"\b(?:flask)\b"), "Flask"),
    (re.compile(r"\b(?:python)\b"), "Python"),
    (re.compile(r"\b(?:java)\b"), "Java"),
    (re.compile(r"\b(?:c\+\+)\b"), "C++"),
    (re.compile(r"\b(?:c)\b"), "C"),
    (re.compile(r"\b(?:typescript|ts)\b"), "TypeScript"),
    (re.compile(r"\b(?:sql)\b"), "SQL"),
    (re.compile(r"\b(?:docker)\b"), "Docker"),
    (re.compile(r"\b(?:kubernetes|k8s)\b"), "Kubernetes"),
    (re.compile(r"\b(?:aws)\b"), "AWS"),
    (re.compile(r"\b(?:azure)\b"), "Azure"),
    (re.compile(r"\b(?:google\s+cloud)\b"), "Google Cloud"),
    (re.compile(r"\b(?:tensor\s*flow|tensorflow)\b"), "TensorFlow"),
    (re.compile(r"\b(?:keras)\b"), "Keras"),
    (re.compile(r"\b(?:scikit\s*learn|sklearn)\b"), "Scikit-learn"),
    (re.compile(r"\b(?:opencv)\b"), "OpenCV"),
    (re.compile(r"\b(?:numpy)\b"), "NumPy"),
    (re.compile(r"\b(?:pandas)\b"), "Pandas"),
    (re.compile(r"\b(?:matplotlib)\b"), "Matplotlib"),
    (re.compile(r"\b(?:machine\s+learning|machine-learning)\b"), "Machine Learning"),
    (re.compile(r"\b(?:deep\s+learning|deep-learning)\b"), "Deep Learning"),
    (re.compile(r"\b(?:artificial\s+intelligence|ai)\b"), "AI"),
    (re.compile(r"\b(?:data\s+science)\b"), "Data Science"),
    (re.compile(r"\b(?:efficientnetb0)\b"), "EfficientNetB0"),
    (re.compile(r"\b(?:git)\b"), "Git"),
    (re.compile(r"\b(?:linux)\b"), "Linux"),
    (re.compile(r"\b(?:vs\s+code|vscode)\b"), "VS Code"),
    (re.compile(r"\b(?:pycharm)\b"), "PyCharm"),
    (re.compile(r"\b(?:google\s+colab)\b"), "Google Colab"),
    (re.compile(r"\b(?:anaconda)\b"), "Anaconda"),
    (re.compile(r"\b(?:chart\.js|chartjs)\b"), "Chart.js"),
    (re.compile(r"\b(?:chrome\s+extensions\s+api)\b"), "Chrome Extensions API"),
]

TECHNOLOGY_CANONICALS = {canonical for _, canonical in TECHNOLOGY_PATTERNS}


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _normalize_skill(skill: str) -> str:
    normalized = _normalize(skill)
    if not normalized:
        return ""

    replacements = {
        "javascript": "JavaScript",
        "js": "JavaScript",
        "rest apis": "REST API",
        "rest api": "REST API",
        "restful api": "REST API",
        "github com": "GitHub",
        "github": "GitHub",
        "mysql database": "MySQL",
        "mysql": "MySQL",
        "html5": "HTML",
        "html": "HTML",
        "css3": "CSS",
        "css": "CSS",
        "postgresql": "PostgreSQL",
        "postgres": "PostgreSQL",
        "node": "Node.js",
        "nodejs": "Node.js",
        "node js": "Node.js",
        "reactjs": "React",
        "react js": "React",
        "react": "React",
        "tensorflow": "TensorFlow",
        "tensor flow": "TensorFlow",
        "machine learning": "Machine Learning",
        "deep learning": "Deep Learning",
        "artificial intelligence": "AI",
        "ai": "AI",
        "sql": "SQL",
        "python": "Python",
        "django": "Django",
        "flask": "Flask",
    }

    if normalized in replacements:
        return replacements[normalized]

    if " " in normalized:
        return " ".join(part.capitalize() for part in normalized.split())

    return normalized.capitalize()


def _add_detected_skills(text: str | None, seen: set[str], skills: list[str]) -> None:
    if text is None:
        return

    cleaned = str(text).strip()
    if not cleaned:
        return

    normalized_text = cleaned.lower()
    found_skills: list[str] = []
    for pattern, canonical in TECHNOLOGY_PATTERNS:
        if pattern.search(normalized_text):
            found_skills.append(canonical)

    if not found_skills:
        candidate = _normalize_skill(cleaned)
        if candidate in TECHNOLOGY_CANONICALS:
            found_skills.append(candidate)

    for canonical in found_skills:
        if canonical in seen:
            continue
        seen.add(canonical)
        skills.append(canonical)


def _extract_resume_skills(parsed_data: dict[str, Any]) -> list[str]:
    normalized_skills: list[str] = []
    seen: set[str] = set()

    skills = parsed_data.get("skills") or []
    if isinstance(skills, list):
        for skill in skills:
            _add_detected_skills(skill, seen, normalized_skills)

    projects = parsed_data.get("projects") or []
    if isinstance(projects, list):
        for project in projects:
            if not isinstance(project, dict):
                continue

            technologies = project.get("technologies") or []
            if isinstance(technologies, list):
                for technology in technologies:
                    _add_detected_skills(technology, seen, normalized_skills)

            for field in ("title", "description"):
                _add_detected_skills(project.get(field), seen, normalized_skills)

    experiences = parsed_data.get("experience") or []
    if isinstance(experiences, list):
        for experience in experiences:
            if isinstance(experience, dict):
                _add_detected_skills(experience.get("description"), seen, normalized_skills)
            else:
                _add_detected_skills(experience, seen, normalized_skills)

    certifications = parsed_data.get("certifications") or []
    if isinstance(certifications, list):
        for certification in certifications:
            if isinstance(certification, dict):
                for field in ("name", "description"):
                    _add_detected_skills(certification.get(field), seen, normalized_skills)
            else:
                _add_detected_skills(certification, seen, normalized_skills)

    activities = parsed_data.get("activities") or []
    if isinstance(activities, list):
        for activity in activities:
            if isinstance(activity, dict):
                for field in ("title", "name", "description"):
                    _add_detected_skills(activity.get(field), seen, normalized_skills)
            else:
                _add_detected_skills(activity, seen, normalized_skills)

    return normalized_skills


def _extract_job_skills(job_description: str) -> list[str]:
    if not job_description or not job_description.strip():
        return []

    text = job_description.lower()
    tokens = [token for token in re.split(r"[^a-z0-9]+", text) if token]
    detected_skills: list[str] = []
    seen: set[str] = set()

    for pattern, canonical in TECHNOLOGY_PATTERNS:
        for match in pattern.finditer(text):
            if canonical in seen:
                continue
            seen.add(canonical)
            detected_skills.append(canonical)

    for size in range(3, 0, -1):
        for index in range(len(tokens) - size + 1):
            phrase = " ".join(tokens[index:index + size])
            candidate = _normalize_skill(phrase)
            if candidate in {canonical for _, canonical in TECHNOLOGY_PATTERNS} and candidate not in seen:
                seen.add(candidate)
                detected_skills.append(candidate)

    return detected_skills


def calculate_job_match(parsed_data: dict[str, Any], job_description: str) -> dict[str, Any]:
    """Calculate a skill-based job match score from resume data and a job description."""
    if not job_description or not job_description.strip():
        return {
            "match_percentage": 0,
            "matched_skills": [],
            "missing_skills": [],
        }

    resume_skills = _extract_resume_skills(parsed_data)
    job_skills = _extract_job_skills(job_description)

    if not job_skills:
        return {
            "match_percentage": 0,
            "matched_skills": [],
            "missing_skills": [],
        }

    resume_skill_set = {skill.lower() for skill in resume_skills}
    matched_skills = [skill for skill in job_skills if skill.lower() in resume_skill_set]
    missing_skills = [skill for skill in job_skills if skill.lower() not in resume_skill_set]
    matched_skills = sorted(matched_skills)
    missing_skills = sorted(missing_skills)
    match_percentage = round((len(matched_skills) / len(job_skills)) * 100)

    return {
        "match_percentage": min(match_percentage, 100),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }
