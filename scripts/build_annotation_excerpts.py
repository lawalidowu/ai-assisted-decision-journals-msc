"""Build pre-filled annotation excerpt shells for manual labelling.

Excerpt text is copied from processed inquiry transcripts. LLM items are
linked where a matching extraction run exists (--inquiry mode recommended).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from decision_journal.extraction import clean_inquiry_text, quote_found_in_text

DEFAULT_RUNS = {
    "transcript-of-module-2-public-hearing-on-28-november-2023": (
        "outputs/run_20260608_005512_module2_2023-11-28"
    ),
    "transcript-of-module-2-public-hearing-on-30-november-2023": (
        "outputs/run_20260609_014425_module2_2023-11-30"
    ),
    "transcript-of-module-2-public-hearing-on-01-december-2023": (
        "outputs/run_20260609_014914_module2_2023-12-01"
    ),
}

# LLM decision indices (1-based) to anchor excerpts — mix pass/fail/debatable
ANCHOR_INDICES_28NOV = [7, 12, 15, 31, 32]  # items 7,12,31 failed traceability

# Fallback search phrases when no reliable LLM anchor (non-inquiry runs)
FALLBACK_ANCHORS = [
    r"COBR decided",
    r"THE CHAIR said",
    r"LADY HALLETT:",
    r"ministerial implementation groups",
    r"Covid-19 Taskforce",
]


def slug_to_txt(slug: str) -> Path:
    return ROOT / "data/processed/inquiry/document" / f"{slug}.txt"


def load_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace")
    return clean_inquiry_text(raw)


def find_anchor_pos(text: str, quote: str, decision: str) -> int | None:
    if quote and quote_found_in_text(quote, text):
        norm_q = re.sub(r"\s+", " ", quote.strip())
        if norm_q in text:
            return text.index(norm_q)
        # fuzzy: scan sliding window on alphanumeric fold
        from decision_journal.extraction import normalize_for_quote_match

        nq = normalize_for_quote_match(quote)
        ns = normalize_for_quote_match(text)
        idx = ns.find(nq)
        if idx >= 0:
            # map back approximately by counting alnum chars in original
            alnum_seen = 0
            for i, ch in enumerate(text):
                if ch.isalnum():
                    alnum_seen += 1
                if alnum_seen >= idx:
                    return max(0, i - 40)
    snippet = (decision or "")[:60]
    if snippet and snippet.lower() in text.lower():
        return text.lower().index(snippet.lower())
    return None


def find_fallback_anchors(text: str, count: int, used: set[int]) -> list[int]:
    positions: list[int] = []
    for pattern in FALLBACK_ANCHORS:
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            pos = m.start()
            if any(abs(pos - u) < 1500 for u in used):
                continue
            positions.append(pos)
            used.add(pos)
            if len(positions) >= count:
                return sorted(positions)
    return sorted(positions)


def extract_window(text: str, center: int, target_words: int = 450) -> tuple[int, int, str]:
    """Return char_start, char_end, excerpt_text (~target_words)."""
    words_before = target_words // 2
    words_after = target_words - words_before

    # expand to word boundaries
    start = center
    for _ in range(words_before):
        ws = text.rfind(" ", 0, start)
        if ws <= 0:
            start = 0
            break
        start = ws

    end = center
    for _ in range(words_after):
        we = text.find(" ", end + 1)
        if we < 0:
            end = len(text)
            break
        end = we

    excerpt = text[start:end].strip()
    word_count = len(excerpt.split())
    if word_count < 200 and end < len(text):
        extra = text[end : min(len(text), end + 8000)]
        end = min(len(text), end + len(extra))
        excerpt = text[start:end].strip()

    return start, end, excerpt


def load_decisions(run_dir: Path) -> list[dict]:
    path = run_dir / "decisions.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def llm_items_in_range(
    decisions: list[dict], char_start: int, char_end: int, text: str
) -> list[dict]:
    """Return LLM decisions whose quote anchor falls inside excerpt range."""
    items = []
    for i, d in enumerate(decisions, start=1):
        pos = find_anchor_pos(text, d.get("source_quote", ""), d.get("decision", ""))
        if pos is not None and char_start <= pos <= char_end:
            items.append(
                {
                    "llm_item_id": i,
                    "decision": d.get("decision"),
                    "source_quote": d.get("source_quote"),
                    "traceability_ok": d.get("traceability_ok"),
                }
            )
    return items


def build_excerpt(
    excerpt_id: str,
    slug: str,
    text: str,
    center: int,
    rationale: str,
    run_dir: Path | None,
    decisions: list[dict],
) -> dict:
    char_start, char_end, excerpt_text = extract_window(text, center)
    seed_llm = llm_items_in_range(decisions, char_start, char_end, text) if decisions else []

    return {
        "excerpt_id": excerpt_id,
        "transcript_slug": slug,
        "source_file": f"data/processed/inquiry/document/{slug}.txt",
        "char_start": char_start,
        "char_end": char_end,
        "word_count": len(excerpt_text.split()),
        "excerpt_text": excerpt_text,
        "selection_rationale": rationale,
        "llm_run": str(run_dir.relative_to(ROOT)).replace("\\", "/") if run_dir else None,
        "seed_llm_items": seed_llm,
        "manual_decisions": [],
        "comparisons": [],
        "_instructions": "Label manual_decisions before filling comparisons. See docs/ANNOTATION_RUBRIC.md.",
    }


def build_for_transcript(
    slug: str,
    run_rel: str,
    anchor_indices: list[int] | None,
    excerpt_prefix: str,
    start_counter: int,
) -> tuple[list[dict], int]:
    txt_path = slug_to_txt(slug)
    if not txt_path.exists():
        raise FileNotFoundError(f"Missing transcript text: {txt_path}")

    text = load_text(txt_path)
    run_dir = ROOT / run_rel if run_rel else None
    decisions = load_decisions(run_dir) if run_dir else []
    excerpts: list[dict] = []
    used_centers: set[int] = set()
    counter = start_counter

    if anchor_indices and decisions:
        for idx in anchor_indices:
            if idx < 1 or idx > len(decisions):
                continue
            d = decisions[idx - 1]
            pos = find_anchor_pos(text, d.get("source_quote", ""), d.get("decision", ""))
            if pos is None:
                continue
            if any(abs(pos - u) < 2000 for u in used_centers):
                continue
            used_centers.add(pos)
            trace = d.get("traceability_ok")
            rationale = (
                f"Anchored on LLM item {idx} "
                f"(traceability_ok={trace}). "
                "Review whether this is a formal decision vs testimony."
            )
            excerpts.append(
                build_excerpt(
                    f"excerpt_{counter:03d}",
                    slug,
                    text,
                    pos,
                    rationale,
                    run_dir,
                    decisions,
                )
            )
            counter += 1

    # Ensure at least 2 excerpts per transcript via fallbacks if needed
    while len(excerpts) < 2:
        fallbacks = find_fallback_anchors(text, 2 - len(excerpts), used_centers)
        if not fallbacks:
            break
        for pos in fallbacks:
            used_centers.add(pos)
            excerpts.append(
                build_excerpt(
                    f"excerpt_{counter:03d}",
                    slug,
                    text,
                    pos,
                    "Procedural / decision-language segment (fallback anchor).",
                    run_dir,
                    decisions,
                )
            )
            counter += 1
            if len(excerpts) >= 2:
                break

    return excerpts, counter


def main() -> None:
    parser = argparse.ArgumentParser(description="Build annotation excerpt shells")
    parser.add_argument(
        "--output",
        default="configs/annotations/manual_phase1.json",
        help="Output workbook JSON path",
    )
    parser.add_argument(
        "--excerpt-dir",
        default="configs/annotations/excerpts",
        help="Directory for individual excerpt JSON files",
    )
    args = parser.parse_args()

    all_excerpts: list[dict] = []
    counter = 1

    # 28 Nov: inquiry run with curated LLM anchors
    ex, counter = build_for_transcript(
        "transcript-of-module-2-public-hearing-on-28-november-2023",
        DEFAULT_RUNS["transcript-of-module-2-public-hearing-on-28-november-2023"],
        ANCHOR_INDICES_28NOV,
        "28nov",
        counter,
    )
    all_excerpts.extend(ex)

    # 30 Nov & 01 Dec: fallback anchors (re-run with --inquiry recommended)
    for slug in [
        "transcript-of-module-2-public-hearing-on-30-november-2023",
        "transcript-of-module-2-public-hearing-on-01-december-2023",
    ]:
        ex, counter = build_for_transcript(
            slug,
            DEFAULT_RUNS[slug],
            None,
            slug.split("-on-")[-1][:7],
            counter,
        )
        all_excerpts.extend(ex)

    llm_runs = []
    seen = set()
    for slug, run_rel in DEFAULT_RUNS.items():
        if run_rel not in seen:
            seen.add(run_rel)
            llm_runs.append(
                {
                    "run_id": Path(run_rel).name,
                    "transcript_slug": slug,
                    "path": run_rel,
                    "note": "inquiry_mode=true",
                }
            )

    workbook = {
        "annotator": "",
        "created_at": str(date.today()),
        "generated_by": "scripts/build_annotation_excerpts.py",
        "llm_runs": llm_runs,
        "excerpts": all_excerpts,
    }

    out_path = ROOT / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(workbook, indent=2, ensure_ascii=False), encoding="utf-8")

    excerpt_dir = ROOT / args.excerpt_dir
    excerpt_dir.mkdir(parents=True, exist_ok=True)
    for ex in all_excerpts:
        single = excerpt_dir / f"{ex['excerpt_id']}.json"
        single.write_text(json.dumps(ex, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote {len(all_excerpts)} excerpts to {out_path}")
    print(f"Individual files in {excerpt_dir}")
    for ex in all_excerpts:
        seeds = len(ex.get("seed_llm_items", []))
        print(
            f"  {ex['excerpt_id']}: {ex['transcript_slug'][-10:]} "
            f"words={ex['word_count']} seed_llm_items={seeds}"
        )


if __name__ == "__main__":
    main()
