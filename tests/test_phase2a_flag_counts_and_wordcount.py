"""Regression: Phase 2a review-flag counts and active Chapter 4 prose consistency."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from docx import Document

ROOT = Path(__file__).resolve().parents[1]
JOURNAL = ROOT / "data/manifests/phase1_decision_journal.json"
CHAPTER4 = ROOT / "dissertation/CHAPTER_4_RESULTS.md"
SUBMISSION_DOCX = ROOT / "dissertation/Lawal_MSc_Dissertation.docx"


def _flag_counts() -> dict[str, int]:
    data = json.loads(JOURNAL.read_text(encoding="utf-8"))
    procedural = 0
    possible_duplicate = 0
    flagged = 0
    both = 0
    for entry in data["entries"]:
        flags = (entry.get("phase2") or {}).get("review_flags") or []
        has_p = "procedural" in flags
        has_d = any("duplicate" in str(x) for x in flags)
        if flags:
            flagged += 1
        if has_p:
            procedural += 1
        if has_d:
            possible_duplicate += 1
        if has_p and has_d:
            both += 1
    return {
        "flagged": flagged,
        "procedural": procedural,
        "possible_duplicate": possible_duplicate,
        "both": both,
        "n_entries": len(data["entries"]),
    }


def test_phase2a_review_flag_counts() -> None:
    counts = _flag_counts()
    assert counts["n_entries"] == 414
    assert counts["flagged"] == 36
    assert counts["procedural"] == 4
    assert counts["possible_duplicate"] == 32
    assert counts["both"] == 0


def test_chapter4_flag_prose_rejects_false_overlap_claim() -> None:
    text = CHAPTER4.read_text(encoding="utf-8")
    counts = _flag_counts()
    assert counts["both"] == 0
    # Active §4.4 must retain verified counts without claiming dual flags.
    assert "36/414 entries were flagged: 4 procedural and 32 possible duplicate." in text
    assert "No rows were deleted." in text
    # Guard against the verified-false overlap phrasing in active Chapter 4.
    bad = re.compile(
        r"36/414[^\n]{0,120}(both flags|carry(?:ing)? both)",
        re.IGNORECASE,
    )
    assert bad.search(text) is None, (
        "Active Chapter 4 still claims overlapping flags while journal overlap=0"
    )


def test_submission_docx_displayed_words_match_markdown_and_reject_stale_14551() -> None:
    """I-02: active DOCX word field must match markdown body count, not stale 14,551."""
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from build_submission_docx import count_dissertation_words  # noqa: E402

    if not SUBMISSION_DOCX.exists():
        pytest.skip("submission DOCX not present")

    expected = count_dissertation_words()
    words_line = None
    for para in Document(str(SUBMISSION_DOCX)).paragraphs:
        t = para.text.strip()
        if t.startswith("Number of Words"):
            words_line = t
            break
    assert words_line is not None, "Number of Words field missing from submission DOCX"
    assert "14,551" not in words_line, "stale pre-Appendix-A word count still displayed"
    digits = re.sub(r"[^0-9]", "", words_line)
    assert digits == str(expected), (
        f"displayed word field {words_line!r} != markdown body count {expected}"
    )
