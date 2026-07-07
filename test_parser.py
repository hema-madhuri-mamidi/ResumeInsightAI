"""Standalone evaluation script for the resume parser."""

from __future__ import annotations

import importlib.util
import inspect
import io
import json
import os
import sys
import time
import traceback
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Callable

PROJECT_ROOT = Path(__file__).resolve().parent
UPLOADS_DIR = PROJECT_ROOT / "uploads"


def _load_legacy_parser_module() -> Any:
    """Load the legacy parser module without executing its demo loop."""
    spec = importlib.util.spec_from_file_location("legacy_parser", PROJECT_ROOT / "parser.py")
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load the legacy parser module")

    module = importlib.util.module_from_spec(spec)
    original_listdir = os.listdir

    def _quiet_listdir(path: str | os.PathLike[str]) -> list[str]:
        if Path(path).name == "uploads":
            return []
        return list(original_listdir(path))

    os.listdir = _quiet_listdir  # type: ignore[assignment]
    try:
        spec.loader.exec_module(module)
    finally:
        os.listdir = original_listdir  # type: ignore[assignment]

    return module


def _load_parser_entrypoint() -> Callable[[Path], dict[str, Any]]:
    """Load the parser callable and choose the correct input format."""
    from v2.parser import parse_resume as parse_resume_v2

    legacy_parser = _load_legacy_parser_module()
    signature = inspect.signature(parse_resume_v2)

    if any(name in signature.parameters for name in {"text", "resume_text", "content"}):
        def _invoke_parser(pdf_path: Path) -> dict[str, Any]:
            text = legacy_parser.extract_text(str(pdf_path))
            return parse_resume_v2(text)

        return _invoke_parser

    def _invoke_parser(pdf_path: Path) -> dict[str, Any]:
        return parse_resume_v2(str(pdf_path))

    return _invoke_parser


def _iter_pdf_files(uploads_dir: Path) -> list[Path]:
    """Return all PDF files under the uploads directory."""
    if not uploads_dir.exists():
        return []
    return sorted(path for path in uploads_dir.rglob("*.pdf") if path.is_file())


def _has_value(value: Any) -> bool:
    """Return True when the value contains something meaningful."""
    if value is None:
        return False

    if isinstance(value, str):
        return bool(value.strip())

    if isinstance(value, (int, float, bool)):
        return bool(value)

    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)

    return bool(value)


def _summarize_completeness(data: dict[str, Any]) -> list[tuple[bool, str]]:
    """Create simple completeness indicators for the parsed output."""
    name_present = _has_value(data.get("name"))

    contact_data = data.get("contact")
    if isinstance(contact_data, dict):
        contact_present = any(_has_value(value) for value in contact_data.values())
    else:
        contact_present = _has_value(data.get("email")) or _has_value(data.get("phone"))

    education_data = data.get("education")
    education_present = isinstance(education_data, dict) and any(
        _has_value(value) for value in education_data.values()
    )

    experience_present = bool(data.get("experience"))
    projects_present = bool(data.get("projects"))
    skills_present = bool(data.get("skills"))
    certifications_present = bool(data.get("certifications"))
    activities_present = bool(data.get("activities"))

    return [
        (name_present, "Name"),
        (contact_present, "Contact"),
        (education_present, "Education"),
        (experience_present, "Experience"),
        (projects_present, "Projects"),
        (skills_present, "Skills"),
        (certifications_present, "Certifications"),
        (activities_present, "Activities"),
    ]


def _marker(present: bool) -> str:
    """Return a marker that works even when stdout cannot encode Unicode."""
    marker = "✓" if present else "✗"
    try:
        marker.encode(sys.stdout.encoding or "utf-8", errors="strict")
    except (LookupError, UnicodeEncodeError):
        marker = "Y" if present else "N"
    return marker


def _format_completeness(indicators: list[tuple[bool, str]]) -> str:
    """Render completeness indicators in a compact, multi-line format."""
    return "\n".join(f"{_marker(present)} {label}" for present, label in indicators)


def _render_resume_result(pdf_path: Path, parse_resume: Callable[[Path], dict[str, Any]]) -> tuple[dict[str, Any], str, list[tuple[bool, str]], float]:
    """Parse one resume and return the parsed data, summary, and elapsed time."""
    start_time = time.perf_counter()
    with redirect_stdout(io.StringIO()):
        data = parse_resume(pdf_path)
    elapsed = time.perf_counter() - start_time

    indicators = _summarize_completeness(data)
    summary = _format_completeness(indicators)
    return data, summary, indicators, elapsed


def main() -> None:
    """Scan uploads, parse every resume, and print a readable evaluation report."""
    parse_resume = _load_parser_entrypoint()
    pdf_files = _iter_pdf_files(UPLOADS_DIR)
    if not pdf_files:
        print(f"No PDF resumes found in: {UPLOADS_DIR}")
        return

    successful = 0
    failed = 0
    parse_times: list[float] = []

    for pdf_path in pdf_files:
        print("=" * 80)
        print(f"Resume: {pdf_path.name}")
        print("=" * 80)
        try:
            data, completeness, indicators, elapsed = _render_resume_result(pdf_path, parse_resume)
            successful += 1
            parse_times.append(elapsed)

            # header = f"{'=' * 20}Resume: {pdf_path.name}{'=' * 20}"
            # print(header)
            print(f"Parse Time: {elapsed:.2f} seconds")
            print("Completeness")
            print("------------")
            print(completeness)
            print("\nParsed JSON")
            print("-----------")
            print(json.dumps(data, indent=4, ensure_ascii=False))
        except Exception:
            failed += 1
            print("-> FAILED")
            print(traceback.format_exc())

    print("\n" + "=" * 80)
    print("Evaluation Summary")
    print("=" * 80)
    print(f"Processed      : {len(pdf_files)}")
    print(f"Successful     : {successful}")
    print(f"Failed         : {failed}")

    if pdf_files:
        success_rate = (successful / len(pdf_files)) * 100
        average_time = sum(parse_times) / len(parse_times) if parse_times else 0.0
        print(f"Success Rate   : {success_rate:.1f}%")
        print(f"Average Time   : {average_time:.2f} sec")


if __name__ == "__main__":
    main()
