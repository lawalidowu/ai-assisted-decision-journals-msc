"""Build stratified Phase 2b validation sample (human rating before model confidence)."""

from __future__ import annotations

import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from decision_journal.journal import load_phase1_journal  # noqa: E402

JOURNAL_PATH = ROOT / "data/manifests/phase1_decision_journal.json"
WORKBOOK_PATH = ROOT / "configs/annotations/manual_phase1.json"
OUTPUT_PATH = ROOT / "configs/evaluation/confidence_validation_sample.json"

RNG = random.Random(42)

# Workbook llm_item_id drift vs canonical run (Dec 01 excerpt_006)
TRIANGULATION_OVERRIDES: dict[tuple[str, int], str] = {
    ("run_20260609_014914_module2_2023-12-01", 40): "phase1-090",
}

STRATA = {
    "flagged": 10,
    "traceability_fail": 10,
    "triangulation": 15,
    "random_unflagged_traceable": 15,
}


def index_journal(entries: list[dict]) -> dict[tuple[str, int], dict]:
    return {(e["run_id"], e["item_index"]): e for e in entries}


def entry_record(entry: dict, stratum: str, extra: dict | None = None) -> dict:
    rec = {
        "journal_id": entry["id"],
        "stratum": stratum,
        "run_id": entry["run_id"],
        "item_index": entry["item_index"],
        "hearing_date": entry["hearing_date"],
        "slug": entry.get("slug"),
        "source_document_type": entry.get("source_document_type"),
        "traceability_ok": entry["traceability_ok"],
        "review_flags": list(entry.get("phase2", {}).get("review_flags") or []),
        "decision": entry["decision"],
        "evidence": entry.get("evidence", ""),
        "source_quote": entry["source_quote"],
        "source_location": entry.get("source_location", ""),
        "human_valid_decision": None,
        "human_confidence": None,
        "human_notes": None,
    }
    if extra:
        rec.update(extra)
    return rec


def norm(text: str) -> str:
    import re

    return re.sub(r"\s+", " ", (text or "").strip().lower())


def find_entry(
    run_id: str,
    llm_item_id: int | None,
    source_quote: str | None,
    decision: str | None,
    by_key: dict[tuple[str, int], dict],
    by_run_quote: dict[tuple[str, str], dict],
    entries: list[dict],
    by_id: dict[str, dict],
) -> dict | None:
    if llm_item_id is not None:
        override_id = TRIANGULATION_OVERRIDES.get((run_id, int(llm_item_id)))
        if override_id and override_id in by_id:
            return by_id[override_id]
        hit = by_key.get((run_id, int(llm_item_id)))
        if hit:
            return hit
    quote_key = norm(source_quote or "")
    if quote_key:
        hit = by_run_quote.get((run_id, quote_key))
        if hit:
            return hit
        prefix = quote_key[:60]
        for e in entries:
            if e["run_id"] != run_id:
                continue
            q = norm(e.get("source_quote", ""))
            if prefix and (prefix in q or q in quote_key):
                return e
    decision_key = norm(decision or "")
    if decision_key:
        for e in entries:
            if e["run_id"] != run_id:
                continue
            if norm(e.get("decision", "")) == decision_key:
                return e
    return None


def triangulation_rows(
    workbook: dict,
    by_key: dict[tuple[str, int], dict],
    by_run_quote: dict[tuple[str, str], dict],
    entries: list[dict],
    by_id: dict[str, dict],
) -> list[dict]:
    rows: list[dict] = []
    for excerpt in workbook.get("excerpts", []):
        excerpt_id = excerpt.get("excerpt_id")
        run_id = Path(excerpt.get("llm_run", "")).name
        seeds = {s["llm_item_id"]: s for s in excerpt.get("seed_llm_items", [])}
        for comp in excerpt.get("comparisons", []):
            llm_item_id = comp.get("llm_item_id")
            seed = seeds.get(llm_item_id) if llm_item_id is not None else None
            source_quote = (seed or {}).get("source_quote")
            seed_decision = (seed or {}).get("decision")
            extra = {
                "excerpt_id": excerpt_id,
                "triangulation": comp.get("triangulation"),
                "triangulation_notes": comp.get("triangulation_notes"),
                "manual_id": comp.get("manual_id"),
                "llm_item_id": llm_item_id,
                "semantic_grounding": comp.get("semantic_grounding"),
            }
            if llm_item_id is not None:
                entry = find_entry(
                    run_id,
                    llm_item_id,
                    source_quote,
                    seed_decision,
                    by_key,
                    by_run_quote,
                    entries,
                    by_id,
                )
                if entry is None:
                    extra["mapping_note"] = (
                        f"Workbook llm_item_id {llm_item_id} not in canonical run; "
                        "could not match by quote"
                    )
                    rows.append(
                        {
                            "journal_id": None,
                            "stratum": "triangulation",
                            "run_id": run_id,
                            "item_index": llm_item_id,
                            "hearing_date": None,
                            "traceability_ok": (seed or {}).get("traceability_ok"),
                            "review_flags": [],
                            "decision": (seed or {}).get("decision") or comp.get("llm_decision_summary"),
                            "source_quote": source_quote,
                            **extra,
                            "human_valid_decision": None,
                            "human_confidence": None,
                            "human_notes": None,
                        }
                    )
                    continue
                rows.append(entry_record(entry, "triangulation", extra))
            else:
                rows.append(
                    {
                        "journal_id": None,
                        "stratum": "triangulation",
                        "run_id": run_id,
                        "item_index": None,
                        "hearing_date": None,
                        "traceability_ok": None,
                        "review_flags": [],
                        "decision": comp.get("triangulation_notes", "")[:200],
                        "source_quote": None,
                        "excerpt_id": excerpt_id,
                        "triangulation": comp.get("triangulation"),
                        "triangulation_notes": comp.get("triangulation_notes"),
                        "manual_id": comp.get("manual_id"),
                        "llm_item_id": None,
                        "semantic_grounding": comp.get("semantic_grounding"),
                        "human_valid_decision": None,
                        "human_confidence": None,
                        "human_notes": None,
                        "note": "Manual-only comparison row — no LLM journal entry in excerpt region",
                    }
                )
    return rows


def pick_flagged(entries: list[dict], n: int, exclude: set[str]) -> list[dict]:
    procedural = [
        e for e in entries if "procedural" in (e.get("phase2", {}).get("review_flags") or [])
    ]
    dupe_only = [
        e
        for e in entries
        if "possible_duplicate" in (e.get("phase2", {}).get("review_flags") or [])
        and "procedural" not in (e.get("phase2", {}).get("review_flags") or [])
    ]
    chosen: list[dict] = []
    for e in procedural:
        if e["id"] not in exclude and len(chosen) < n:
            chosen.append(entry_record(e, "flagged"))
            exclude.add(e["id"])
    pool = dupe_only[:]
    RNG.shuffle(pool)
    for e in pool:
        if len(chosen) >= n:
            break
        if e["id"] not in exclude:
            chosen.append(entry_record(e, "flagged"))
            exclude.add(e["id"])
    if len(chosen) < n:
        rest = [
            e
            for e in entries
            if e.get("phase2", {}).get("review_flags") and e["id"] not in exclude
        ]
        RNG.shuffle(rest)
        for e in rest:
            if len(chosen) >= n:
                break
            chosen.append(entry_record(e, "flagged"))
            exclude.add(e["id"])
    return chosen


def main() -> int:
    journal = load_phase1_journal(JOURNAL_PATH)
    entries = journal["entries"]
    by_key = index_journal(entries)
    by_id = {e["id"]: e for e in entries}
    by_run_quote = {(e["run_id"], norm(e.get("source_quote", ""))): e for e in entries if e.get("source_quote")}
    workbook = json.loads(WORKBOOK_PATH.read_text(encoding="utf-8"))

    selected: list[dict] = []
    used_ids: set[str] = set()

    tri_rows = triangulation_rows(workbook, by_key, by_run_quote, entries, by_id)
    if len(tri_rows) != STRATA["triangulation"]:
        print(f"WARN: expected {STRATA['triangulation']} triangulation rows, got {len(tri_rows)}")
    selected.extend(tri_rows)
    used_ids.update(r["journal_id"] for r in tri_rows if r.get("journal_id"))

    flagged = pick_flagged(entries, STRATA["flagged"], used_ids)
    selected.extend(flagged)
    used_ids.update(r["journal_id"] for r in flagged)

    trace_fail_pool = [e for e in entries if not e["traceability_ok"] and e["id"] not in used_ids]
    RNG.shuffle(trace_fail_pool)
    for e in trace_fail_pool[: STRATA["traceability_fail"]]:
        selected.append(entry_record(e, "traceability_fail"))
        used_ids.add(e["id"])

    random_pool = [
        e
        for e in entries
        if e["traceability_ok"]
        and not (e.get("phase2", {}).get("review_flags"))
        and e["id"] not in used_ids
    ]
    RNG.shuffle(random_pool)
    for e in random_pool[: STRATA["random_unflagged_traceable"]]:
        selected.append(entry_record(e, "random_unflagged_traceable"))
        used_ids.add(e["id"])

    strata_counts: dict[str, int] = {}
    for row in selected:
        strata_counts[row["stratum"]] = strata_counts.get(row["stratum"], 0) + 1

    manifest = {
        "description": "Phase 2b blind human validation sample — rate before any model confidence labels",
        "rubric_ref": "docs/MEETING_4_ISSUES_AND_TODOS.md §B.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "random_seed": 42,
        "target_strata": STRATA,
        "actual_strata": strata_counts,
        "total": len(selected),
        "instructions": (
            "Rate using the full audit package: decision + evidence + source_quote + source_location. "
            "Rubric A: valid journal entry? Rubric B: how strongly does the quoted evidence support "
            "the decision text? (Not model self-confidence — you are the judge.)"
        ),
        "items": [{**row, "sample_index": i} for i, row in enumerate(selected, start=1)],
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Wrote {OUTPUT_PATH}")
    print(f"  total: {len(selected)}")
    for k in sorted(strata_counts):
        print(f"  {k}: {strata_counts[k]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
