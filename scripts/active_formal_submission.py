#!/usr/bin/env python3
"""Resolve the active formal dissertation package (Wave 7A+)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POINTER = ROOT / "outputs" / "dissertation_integration" / "ACTIVE_FORMAL_SUBMISSION_POINTER.json"


def load_active_formal() -> dict:
    data = json.loads(POINTER.read_text(encoding="utf-8"))
    for key in ("docx", "pdf", "active_package"):
        path = ROOT / data[key]
        if not path.exists():
            raise FileNotFoundError(path)
    return data


def active_docx() -> Path:
    return ROOT / load_active_formal()["docx"]


def active_pdf() -> Path:
    return ROOT / load_active_formal()["pdf"]


def active_docx_sha256() -> str:
    return load_active_formal()["docx_sha256"]


def active_pdf_sha256() -> str:
    return load_active_formal()["pdf_sha256"]
