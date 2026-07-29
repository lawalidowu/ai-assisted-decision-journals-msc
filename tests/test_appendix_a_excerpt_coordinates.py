"""Regression: Appendix A excerpt offsets use clean_inquiry_text coordinates."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from rebuild_appendix_a_excerpts import (  # noqa: E402
    assert_excerpt_matches_cleaned_slice,
    cleaned_transcript_slice,
    contains_normalized,
    fold_alnum,
    load_excerpt,
    normalize_ws,
)

EXCERPT_IDS = [f"excerpt_{i:03d}" for i in range(1, 7)]
CHAPTER4 = ROOT / "dissertation" / "CHAPTER_4_RESULTS.md"


@pytest.fixture(params=EXCERPT_IDS)
def excerpt(request) -> dict:
    return load_excerpt(request.param)


def test_stored_excerpt_text_matches_cleaned_transcript_slice(excerpt: dict) -> None:
    stored = assert_excerpt_matches_cleaned_slice(excerpt)
    sliced = cleaned_transcript_slice(excerpt)
    assert normalize_ws(sliced) == normalize_ws(stored)
    assert stored == excerpt["excerpt_text"]


def test_manual_source_quotes_contained_in_cleaned_excerpt(excerpt: dict) -> None:
    stored = assert_excerpt_matches_cleaned_slice(excerpt)
    for manual in excerpt.get("manual_decisions") or []:
        quote = (manual.get("source_quote") or "").strip()
        if not quote:
            continue
        assert contains_normalized(stored, quote), (
            f"{excerpt['excerpt_id']} {manual.get('manual_id')}: "
            f"source_quote not in cleaned/stored excerpt"
        )


def test_seed_llm_source_quotes_contained_in_cleaned_excerpt(excerpt: dict) -> None:
    """seed_llm_items were linked because their anchors fell inside the span."""
    stored = assert_excerpt_matches_cleaned_slice(excerpt)
    for item in excerpt.get("seed_llm_items") or []:
        quote = (item.get("source_quote") or "").strip()
        if not quote:
            continue
        assert contains_normalized(stored, quote), (
            f"{excerpt['excerpt_id']} llm_item_id={item.get('llm_item_id')}: "
            f"source_quote not in cleaned/stored excerpt"
        )


def test_excerpt_002_contains_covid_o_and_disability_passages() -> None:
    data = load_excerpt("excerpt_002")
    stored = assert_excerpt_matches_cleaned_slice(data)
    folded = fold_alnum(stored)
    assert fold_alnum("29 October meeting of COVID-O") in folded
    assert fold_alnum("people withdisabilities") in folded


def _triangulation_totals_from_annotations() -> dict[str, int]:
    totals = {"agreement": 0, "silence": 0, "dissonance": 0, "manual_decisions": 0}
    for excerpt_id in EXCERPT_IDS:
        data = load_excerpt(excerpt_id)
        totals["manual_decisions"] += len(data.get("manual_decisions") or [])
        for row in data.get("comparisons") or []:
            label = row.get("triangulation")
            if label not in ("agreement", "silence", "dissonance"):
                raise AssertionError(
                    f"{excerpt_id}: unexpected triangulation label {label!r}"
                )
            totals[label] += 1
    return totals


def test_chapter4_triangulation_totals_unchanged() -> None:
    totals = _triangulation_totals_from_annotations()
    assert totals == {
        "agreement": 5,
        "silence": 10,
        "dissonance": 0,
        "manual_decisions": 6,
    }

    text = CHAPTER4.read_text(encoding="utf-8")
    # Table 4.2 count cells must still match the annotation workbook.
    assert re.search(
        r"\|\s*Agreement\s*\|[^|]*\|\s*5\s*\|", text
    ), "Chapter 4 Table 4.2 Agreement count drifted"
    assert re.search(
        r"\|\s*Silence\s*\|[^|]*\|\s*10\s*\|", text
    ), "Chapter 4 Table 4.2 Silence count drifted"
    assert re.search(
        r"\|\s*Dissonance\s*\|[^|]*\|\s*0\s*\|", text
    ), "Chapter 4 Table 4.2 Dissonance count drifted"
    assert "six manual decisions" in text


def test_excerpt_identifiers_and_spans_preserved() -> None:
    """Guardrail: correction must not rewrite annotation span metadata."""
    expected_spans = {
        "excerpt_001": (83955, 86750),
        "excerpt_002": (229233, 232162),
        "excerpt_003": (0, 1382),
        "excerpt_004": (21739, 24495),
        "excerpt_005": (0, 1508),
        "excerpt_006": (26169, 28883),
    }
    for excerpt_id, (start, end) in expected_spans.items():
        data = load_excerpt(excerpt_id)
        assert data["excerpt_id"] == excerpt_id
        assert data["char_start"] == start
        assert data["char_end"] == end
