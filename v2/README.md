# Version 2 Resume Parser

This folder contains a new, modular architecture for resume parsing that is intentionally separate from the existing Version 1 implementation.

## Goals

- Preserve the current Version 1 parser without modification.
- Build a cleaner, more maintainable architecture for Version 2.
- Keep each parsing responsibility isolated in its own module.
- Add placeholder implementations first, then evolve the logic incrementally.

## Structure

- parser.py: main orchestrator entry point.
- section_detector.py: detects and extracts section content.
- name_parser.py: extracts candidate names.
- contact_parser.py: extracts contact details.
- education_parser.py: extracts education data.
- project_parser.py: extracts project data.
- experience_parser.py: extracts experience data.
- skills_parser.py: extracts skills.
- certification_parser.py: extracts certifications.
- activity_parser.py: extracts activities and achievements.
- utils.py: shared text and parsing helpers.
- constants.py: headings, regex patterns, and keywords.
- models.py: dataclasses for structured output.

## Current Status

The Version 2 scaffold is in place with placeholder functions and TODO comments. No parsing logic has been implemented yet.
