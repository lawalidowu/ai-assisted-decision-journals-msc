#!/usr/bin/env python3
"""Regenerate Appendix A with exact bounded excerpt texts.

Character offsets in configs/annotations/excerpts/*.json were measured against
clean_inquiry_text(processed_transcript). This script applies the same cleaning
before validating char_start:char_end, then emits the stored excerpt_text.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from decision_journal.extraction import clean_inquiry_text  # noqa: E402

HEARING_DATES = {
    "28-november-2023": "28 November 2023",
    "30-november-2023": "30 November 2023",
    "01-december-2023": "01 December 2023",
}


SHORT_HEARING = {
    "28-november-2023": "28 Nov 2023",
    "30-november-2023": "30 Nov 2023",
    "01-december-2023": "01 Dec 2023",
}


def hearing_from_slug(slug: str, *, short: bool = False) -> str:
    mapping = SHORT_HEARING if short else HEARING_DATES
    for key, value in mapping.items():
        if key in slug:
            return value
    return slug


def normalize_ws(text: str) -> str:
    """Collapse all whitespace runs to a single space and strip ends."""
    return " ".join((text or "").split())


def fold_alnum(text: str) -> str:
    """Lowercase alphanumeric fold for PDF-spacing-tolerant containment checks."""
    return re.sub(r"[^a-z0-9]+", "", (text or "").lower())


# PDF line furniture inserted into Module 2 transcripts (not part of spoken text).
_PAGE_LINE_NOISE = re.compile(
    r"1\s*2\s*3\s*4\s*5\s*6\s*7\s*8\s*910111213141516171819202122232425"
    r"(?:\s+\d{1,3})?"
)


def strip_page_line_noise(text: str) -> str:
    """Remove recurring inquiry page-number line artefacts before quote checks."""
    return _PAGE_LINE_NOISE.sub(" ", text or "")


def contains_normalized(haystack: str, needle: str) -> bool:
    """True if needle occurs in haystack under transcript-tolerant normalisation.

    Matching order:
    1. alphanumeric fold of both strings;
    2. same after stripping inquiry page-line digit furniture from haystack;
    3. long prefix (≥60 folded chars) for quotes truncated at the excerpt edge.
    """
    n = fold_alnum(needle)
    if not n:
        return False
    h = fold_alnum(haystack)
    if n in h:
        return True
    h2 = fold_alnum(strip_page_line_noise(haystack))
    if n in h2:
        return True
    if len(n) >= 60 and (n[:60] in h2 or n[:60] in h):
        return True
    return False


def load_excerpt(excerpt_id: str, *, root: Path = ROOT) -> dict:
    path = root / "configs" / "annotations" / "excerpts" / f"{excerpt_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def cleaned_transcript_slice(data: dict, *, root: Path = ROOT) -> str:
    """Return clean_inquiry_text(processed)[char_start:char_end]."""
    source = root / data["source_file"]
    raw = source.read_text(encoding="utf-8", errors="replace")
    cleaned = clean_inquiry_text(raw)
    return cleaned[data["char_start"] : data["char_end"]]


def assert_excerpt_matches_cleaned_slice(data: dict, *, root: Path = ROOT) -> str:
    """Validate stored excerpt_text against the cleaned coordinate slice.

    Returns the stored excerpt_text on success.
    """
    excerpt_id = data.get("excerpt_id", "?")
    stored = data.get("excerpt_text") or ""
    if not stored:
        raise ValueError(f"{excerpt_id}: missing excerpt_text in annotation JSON")

    sliced = cleaned_transcript_slice(data, root=root)
    if normalize_ws(sliced) != normalize_ws(stored):
        raise ValueError(
            f"{excerpt_id}: cleaned transcript slice "
            f"[{data['char_start']}:{data['char_end']}] does not match stored "
            f"excerpt_text after whitespace normalisation "
            f"(slice_chars={len(sliced)}, stored_chars={len(stored)}, "
            f"source={data.get('source_file')}). "
            "Offsets must be measured on clean_inquiry_text(processed_transcript)."
        )
    return stored


def main() -> None:
    lines: list[str] = [
        "# Appendix A: Manual excerpt evidence",
        "",
        "This appendix provides the six bounded Module 2 hearing excerpts used for "
        "manual triangulation in Chapter 4 Section 4.3. Each excerpt is the exact "
        "character-span text from the processed transcript. The project repository "
        "retains the machine-readable annotation files and complete extraction-run "
        "provenance.",
        "",
        "| ID | Hearing | Span | Manual | LLM IDs |",
        "|----|---------|------|-------:|---------|",
    ]

    blocks = []
    for i in range(1, 7):
        data = load_excerpt(f"excerpt_{i:03d}")
        stored = assert_excerpt_matches_cleaned_slice(data)
        # Emit stored annotation text (whitespace-collapsed for the blockquote).
        bounded = normalize_ws(stored)
        hearing = hearing_from_slug(data["transcript_slug"])
        hearing_short = hearing_from_slug(data["transcript_slug"], short=True)
        n_manual = len(data.get("manual_decisions") or [])
        ids = [str(it.get("llm_item_id")) for it in data.get("seed_llm_items") or []]
        if len(ids) > 3 and ids[0].isdigit() and ids[-1].isdigit():
            id_str_table = f"{ids[0]}–{ids[-1]}"
        else:
            id_str_table = ", ".join(ids) if ids else "—"
        id_str = ", ".join(ids) if ids else "—"
        lines.append(
            f"| excerpt_{i:03d} | {hearing_short} | {data['char_start']}–{data['char_end']} | "
            f"{n_manual} | {id_str_table} |"
        )

        if data.get("manual_decisions"):
            man_lines = [
                f"- `{m['manual_id']}`: {m['decision']}" for m in data["manual_decisions"]
            ]
        else:
            man_lines = ["- No manual decision"]

        comps = data.get("comparisons") or []
        if comps:
            status = f"{len(comps)} triangulation-workbook row(s)."
        elif n_manual == 0 and ids:
            status = "LLM-only silence rows; no manual decision in this span."
        else:
            status = "No comparison rows."

        blocks.append((i, data, hearing, bounded, man_lines, id_str, status))

    lines.append("")
    lines.append(
        "Table A.1 uses short column labels for readability: ID = excerpt identifier; "
        "Hearing = hearing date; Span = character span in the processed transcript; "
        "Manual = number of manual decisions; LLM IDs = linked extraction item identifiers."
    )
    lines.append("")
    for i, data, hearing, bounded, man_lines, id_str, status in blocks:
        lines.extend(
            [
                f"## excerpt_{i:03d}",
                "",
                f"- Hearing date: {hearing}",
                f"- Transcript: `{data['transcript_slug']}`",
                f"- Source span: characters {data['char_start']}–{data['char_end']}",
                f"- Linked LLM item IDs: {id_str}",
                "",
                "### Bounded transcript text",
                "",
                f"> {bounded}",
                "",
                "### Manual decisions",
                "",
            ]
        )
        lines.extend(man_lines)
        lines.extend(["", f"*Comparison status:* {status}", ""])

    lines.extend(
        [
            "## Closing note",
            "",
            "The six excerpts above are the complete bounded source texts used for "
            "Chapter 4 triangulation. Machine-readable annotations and extraction-run "
            "identifiers remain in the project repository.",
            "",
        ]
    )

    out = ROOT / "dissertation" / "APPENDIX_A_MANUAL_EXCERPTS.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
