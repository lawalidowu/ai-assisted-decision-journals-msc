"""Phase 2a — rule-based review flags on canonical journal entries."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

PROCEDURAL_PATTERNS = [
    re.compile(p, re.I)
    for p in [
        r"\badjourn",
        r"\bhearing will resume\b",
        r"\bhearing is adjourned\b",
        r"\bhearing adjourned\b",
        r"\bwill resume at\b",
        r"\breconvene",
        r"\bnext substantive hearing",
        r"\bsit again at\b",
        r"\bwe will now adjourn\b",
        r"\bbreak for lunch\b",
        r"\blunch adjournment\b",
    ]
]

MIN_QUOTE_DUPE_LEN = 50


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def is_procedural(entry: dict[str, Any]) -> bool:
    blob = f"{entry.get('decision', '')} {entry.get('source_quote', '')}"
    return any(p.search(blob) for p in PROCEDURAL_PATTERNS)


def apply_review_flags(entries: list[dict[str, Any]]) -> dict[str, int]:
    """Set phase2.review_flags on each entry. Returns flag counts."""
    decision_groups: dict[str, list[str]] = defaultdict(list)
    quote_groups: dict[str, list[str]] = defaultdict(list)

    for entry in entries:
        entry.setdefault("phase2", {})
        entry["phase2"]["review_flags"] = []

        decision_key = norm(entry.get("decision", ""))
        if decision_key:
            decision_groups[decision_key].append(entry["id"])

        quote_key = norm(entry.get("source_quote", ""))
        if len(quote_key) >= MIN_QUOTE_DUPE_LEN:
            quote_groups[quote_key].append(entry["id"])

    dupe_ids: set[str] = set()
    for ids in decision_groups.values():
        if len(ids) > 1:
            dupe_ids.update(ids)
    for ids in quote_groups.values():
        if len(ids) > 1:
            dupe_ids.update(ids)

    counts: dict[str, int] = defaultdict(int)
    for entry in entries:
        flags: list[str] = []
        if is_procedural(entry):
            flags.append("procedural")
        if entry["id"] in dupe_ids:
            flags.append("possible_duplicate")
        entry["phase2"]["review_flags"] = sorted(set(flags))
        for flag in entry["phase2"]["review_flags"]:
            counts[flag] += 1
        if not entry["phase2"]["review_flags"]:
            counts["unflagged"] += 1

    return dict(counts)
