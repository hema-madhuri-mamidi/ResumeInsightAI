from __future__ import annotations

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = str(BASE_DIR / "uploads")
MAX_CONTENT_LENGTH = 16 * 1024 * 1024


class Config:
    UPLOAD_FOLDER = UPLOAD_FOLDER
    MAX_CONTENT_LENGTH = MAX_CONTENT_LENGTH
