from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Any

from flask import Blueprint, current_app, jsonify, request

from .ats_score import calculate_ats_score
from .job_match import calculate_job_match
from .parser import parse_resume as parse_resume_v2
from .skill_gap import analyze_skill_gap
from .suggestions import generate_suggestions
from database import save_resume_analysis

bp = Blueprint("main", __name__, url_prefix="/api")


def _safe_filename(original_name: str) -> str:
    stem = Path(original_name).stem or "resume"
    suffix = Path(original_name).suffix.lower() or ".pdf"
    return f"{uuid.uuid4().hex}-{Path(stem).name}{suffix}"


def extract_pdf_text(pdf_path: str | os.PathLike[str]) -> str:
    from parser import extract_text

    return extract_text(str(pdf_path))


@bp.get("/health")
def health() -> Any:
    return jsonify({"status": "ok"})


@bp.post("/parse")
def parse_resume() -> Any:
    if "resume" not in request.files:
        return jsonify({"success": False, "message": "No file uploaded"}), 400

    uploaded_file = request.files["resume"]
    if uploaded_file.filename == "":
        return jsonify({"success": False, "message": "No file uploaded"}), 400

    if not uploaded_file.filename.lower().endswith(".pdf"):
        return jsonify({"success": False, "message": "Only PDF files are allowed"}), 400

    upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
    upload_folder.mkdir(parents=True, exist_ok=True)

    filename = _safe_filename(uploaded_file.filename)
    temp_path = upload_folder / filename
    uploaded_file.save(temp_path)

    try:
        text = extract_pdf_text(temp_path)
        data = parse_resume_v2(text)
    finally:
        if temp_path.exists():
            temp_path.unlink()

    job_description = request.form.get("job_description", "").strip()
    ats_score = calculate_ats_score(data)
    suggestions = generate_suggestions(data, ats_score)
    job_match = calculate_job_match(data, job_description)
    skill_gap = analyze_skill_gap(data, job_description)
    data["ats_score"] = ats_score
    data["suggestions"] = suggestions
    data["job_match"] = job_match
    data["skill_gap"] = skill_gap

    save_resume_analysis(data)

    return jsonify({"success": True, "data": data})
# text=extract_pdf_text(temp_path)
# print(text)