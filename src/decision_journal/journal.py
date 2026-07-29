"""Load and iterate the canonical Phase 1 decision journal."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_JOURNAL_PATH = Path("data/manifests/phase1_decision_journal.json")


def load_phase1_journal(path: Path | str | None = None) -> dict[str, Any]:
    """Load the canonical Phase 1 decision journal envelope."""
    journal_path = Path(path) if path else DEFAULT_JOURNAL_PATH
    data = json.loads(journal_path.read_text(encoding="utf-8"))
    if data.get("artifact_type") != "canonical_decision_journal":
        raise ValueError(f"Unexpected artifact_type in {journal_path}")
    return data


def iter_entries(journal: dict[str, Any]) -> list[dict[str, Any]]:
    """Return journal entries list."""
    entries = journal.get("entries")
    if not isinstance(entries, list):
        raise ValueError("Journal missing 'entries' list")
    return entries
