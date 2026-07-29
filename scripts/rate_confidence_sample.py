"""Interactive blind human rating for Phase 2b validation sample.

You are NOT rating model self-confidence. You rate how strongly the
audit package (decision + evidence + quote) supports the extraction.

Usage:
  python scripts/rate_confidence_sample.py
  python scripts/rate_confidence_sample.py --checklist   # Rubric A then 2-check → suggested H/M/L
  python scripts/rate_confidence_sample.py --export-csv
  python scripts/rate_confidence_sample.py --summary
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = ROOT / "configs/evaluation/confidence_validation_sample.json"
PROVISIONAL_PATH = ROOT / "configs/evaluation/confidence_validation_sample_provisional.json"
CSV_PATH = ROOT / "configs/evaluation/confidence_validation_sample.csv"

VALID_DECISION = {"y": "yes", "n": "no", "u": "unclear", "yes": "yes", "no": "no", "unclear": "unclear"}
VALID_CONFIDENCE = {"h": "high", "m": "medium", "l": "low", "high": "high", "medium": "medium", "low": "low"}
YN = {"y": True, "n": False, "yes": True, "no": False}


RUBRIC_INTRO = """
PHASE 2b — HUMAN GOLD STANDARD (not LLM confidence)
-------------------------------------------------
You judge TWO things from the AUDIT PACKAGE shown for each item:

  Rubric A — Valid decision journal entry?  (domain judgement — yes/no/unclear)
    Is this the kind of entry your decision journal is meant to capture?

  Rubric B — Strength of support  (evidence only — no domain expertise)
    How clearly do EVIDENCE + SOURCE QUOTE support the DECISION text?

Later, programmatic LLM/rule scores will be COMPARED to your Rubric B ratings.
"""


RUBRIC_A_GUIDE = """
RUBRIC A — Valid decision journal entry?
  yes     — COBR/COVID-O/Cabinet/PM agreed action; adopted measure; authoritative
            direction; commissioned task WHEN stated as decided (incl. recalled in
            testimony). Quote must plausibly support it.
  no      — Procedural (adjournment, resume hearing); witness opinion; advocacy
            ("we need to", "should have" with no agreement); pure narrative;
            future recommendation never adopted; scheduling/meta inquiry text.
  unclear — Borderline; genuinely unsure whether this belongs in the journal.
            Use freely — do not force yes/no. These cases are often the most
            interesting for the thesis (ambiguity in source or extraction).
"""


RUBRIC_B_GUIDE = """
RUBRIC B — Strength of support (evidence + quote → decision ONLY)
  No domain expertise required. Ignore whether this belongs in a policy journal.

  high    — Quote clearly supports the decision text (minimal inference).
  medium  — Partial/indirect support; some inference or bundling required.
  low     — Quote missing, unreadable, or does not support the decision.

  CHECKLIST (--checklist): [1] quote readable? + [2] quote supports decision?
    0/2 → low  |  1/2 → medium  |  2/2 → high

  Example: "Hearing adjourns at 10am" with matching quote → B=high, but A=no.
"""


CHECKLIST_GUIDE = """
RUBRIC B CHECKLIST — evidence strength only (no domain expertise)
  Answer y/n:
    [1] Quote present and readable?
    [2] Quote supports the decision text (not just the same topic)?

  Score → suggested support strength:
    0 points → low  |  1 point → medium  |  2 points → high

  Domain judgement (procedural vs policy?) belongs in Rubric A only — not here.
  Example: hearing adjournment → Rubric A=no, but Rubric B can still be high
  if the quote perfectly supports the extracted statement.
"""


def save(manifest: dict, path: Path) -> None:
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def prompt_choice(label: str, mapping: dict[str, str], allow_skip: bool = False) -> str | None:
    opts = " / ".join(sorted(set(mapping.values())))
    while True:
        raw = input(f"  {label} ({opts}){' [Enter=skip]' if allow_skip else ''}: ").strip().lower()
        if allow_skip and raw == "":
            return None
        if raw in mapping:
            return mapping[raw]
        print(f"    Invalid — use one of: {opts}")


def prompt_yn(label: str) -> bool | None:
    while True:
        raw = input(f"  {label} (y/n): ").strip().lower()
        if raw in YN:
            return YN[raw]
        if raw == "":
            return None
        print("    Invalid — use y or n")


def score_to_support(points: int) -> str:
    if points >= 2:
        return "high"
    if points == 1:
        return "medium"
    return "low"


def show_item(item: dict) -> None:
    trace = item.get("traceability_ok")
    trace_note = (
        "PASS — quote locatable in processed transcript text (mechanical check)"
        if trace
        else "FAIL — quote not matched in processed text (may still be semantically valid)"
        if trace is False
        else "N/A"
    )

    print("\n" + "=" * 72)
    print(f"Item {item['sample_index']}/50  |  {item.get('journal_id') or '(no journal id)'}")
    print(f"Stratum: {item['stratum']}  |  Hearing: {item.get('hearing_date', '—')}")
    if item.get("slug"):
        print(f"Source: {item['slug']}")
    if item.get("run_id"):
        print(f"Provenance: {item['run_id']}  item_index={item.get('item_index')}")
    flags = item.get("review_flags") or []
    if flags:
        print(f"Review flags (Phase 2a): {', '.join(flags)}")
    print(f"Traceability: {trace_note}")
    print("-" * 72)
    print("AUDIT PACKAGE — base your ratings ONLY on this:")
    print("\n  (1) DECISION — extracted claim:")
    print(f"      {item.get('decision', '')}")
    print("\n  (2) EVIDENCE — model's supporting explanation:")
    ev = item.get("evidence") or "(missing — run: python scripts/build_confidence_validation_sample.py)"
    print(f"      {ev}")
    print("\n  (3) SOURCE QUOTE — verbatim from transcript:")
    print(f"      {item.get('source_quote') or '(none)'}")
    loc = item.get("source_location")
    if loc:
        print(f"\n  (4) SOURCE LOCATION: {loc}  (within LLM chunk, not PDF page)")
    if not item.get("journal_id") and item.get("triangulation_notes"):
        print("\n  WORKBOOK CONTEXT (unmapped row):")
        print(f"      {item['triangulation_notes']}")
    print("-" * 72)
    print("Type '?' before rating for rubric help  |  'q' quit  |  's' skip")


def run_checklist() -> tuple[str, dict] | None:
    print(CHECKLIST_GUIDE)
    c1 = prompt_yn("[1] Quote present and readable?")
    if c1 is None:
        return None
    c2 = prompt_yn("[2] Quote supports the decision text?")
    if c2 is None:
        return None
    points = sum([c1, c2])
    suggested_b = score_to_support(points)
    checks = {"quote_usable": c1, "quote_supports": c2, "points": points}
    print(f"\n  Support checklist: {points}/2 → suggested Rubric B: {suggested_b}")
    return suggested_b, checks


def confirm_or_override(suggested: str, label: str, mapping: dict[str, str]) -> str | None:
    raw = input(f"  {label} [Enter={suggested}, or override]: ").strip().lower()
    if raw == "":
        return suggested
    if raw in mapping:
        return mapping[raw]
    print(f"    Invalid — using suggestion: {suggested}")
    return suggested


def export_csv(manifest: dict) -> None:
    items = manifest["items"]
    fields = [
        "sample_index",
        "journal_id",
        "stratum",
        "hearing_date",
        "traceability_ok",
        "review_flags",
        "decision",
        "evidence",
        "source_quote",
        "source_location",
        "slug",
        "human_valid_decision",
        "human_confidence",
        "human_notes",
        "human_checks",
    ]
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for item in items:
            row = dict(item)
            row["review_flags"] = ";".join(row.get("review_flags") or [])
            if row.get("human_checks"):
                row["human_checks"] = json.dumps(row["human_checks"])
            w.writerow(row)
    print(f"Exported {CSV_PATH}")


def summary(manifest: dict) -> None:
    items = manifest["items"]
    done = sum(1 for i in items if i.get("human_valid_decision") and i.get("human_confidence"))
    print(f"Rated: {done}/50")
    for i in items:
        if not i.get("human_valid_decision") or not i.get("human_confidence"):
            print(f"  pending: sample_index {i['sample_index']} ({i.get('journal_id')})")

    rated = [i for i in items if i.get("human_valid_decision") and i.get("human_confidence")]
    if not rated:
        return

    print("\nRubric A distribution:")
    for val in ("yes", "no", "unclear"):
        n = sum(1 for i in rated if i["human_valid_decision"] == val)
        if n:
            print(f"  {val}: {n}")

    print("\nRubric B distribution:")
    for val in ("high", "medium", "low"):
        n = sum(1 for i in rated if i["human_confidence"] == val)
        if n:
            print(f"  {val}: {n}")

    print("\nA × B cross-tab (rated items only):")
    cells = [
        ("yes", "high", "strong journal entries"),
        ("yes", "medium", "valid decision, partial/indirect quote support"),
        ("yes", "low", "decision-like, weak evidence"),
        ("no", "high", "correct extraction, wrong artefact type"),
        ("no", "medium", "not a journal entry; quote only partly supports text"),
        ("no", "low", "noise"),
        ("unclear", "high", "borderline inclusion; evidence supports extraction well"),
        ("unclear", "medium", "borderline inclusion; partial support"),
        ("unclear", "low", "borderline inclusion; weak support"),
    ]
    for a, b, label in cells:
        n = sum(
            1 for i in rated if i["human_valid_decision"] == a and i["human_confidence"] == b
        )
        if n:
            print(f"  A={a}, B={b}: {n}  ({label})")


def run_interactive(
    manifest: dict,
    manifest_path: Path,
    blind: bool = True,
    use_checklist: bool = False,
) -> None:
    items = manifest["items"]
    print(RUBRIC_INTRO)
    if manifest.get("rating_provenance") == "ai_provisional_dev":
        print("WARNING: Provisional dev manifest — NOT thesis human gold standard.\n")
    print(f"Writing to: {manifest_path}\n")
    print("Commands: Enter=rate  |  ?=rubric help  |  s=skip  |  q=save & quit")
    if use_checklist:
        print("Mode: CHECKLIST (Rubric A, then 2-check evidence rubric → suggested B)")
    else:
        print("Mode: DIRECT (h/m/l and y/n/u) — add --checklist for guided scoring")
    if blind:
        print("Blind: prior triangulation hidden (--show-triangulation to show)\n")
    else:
        print()

    for item in items:
        if item.get("human_valid_decision") and item.get("human_confidence"):
            continue

        show_item(item)
        if not blind and item.get("triangulation"):
            print(
                f"\n[Prior triangulation: {item.get('triangulation')} — "
                f"{item.get('triangulation_notes', '')[:120]}]"
            )

        cmd = input("\n  Press Enter to rate, ?=help, s=skip, q=quit: ").strip().lower()
        if cmd == "q":
            save(manifest, manifest_path)
            print("Saved. Progress kept.")
            return
        if cmd == "s":
            continue
        if cmd == "?":
            print(RUBRIC_A_GUIDE)
            print(RUBRIC_B_GUIDE)
            if use_checklist:
                print(CHECKLIST_GUIDE)
            input("\n  Press Enter to continue...")
            show_item(item)

        checks = None
        if use_checklist:
            print(RUBRIC_A_GUIDE)
            vd = prompt_choice("Rubric A — valid decision journal entry?", VALID_DECISION)
            if vd is None:
                continue
            result = run_checklist()
            if result is None:
                continue
            suggested_b, checks = result
            print(RUBRIC_B_GUIDE)
            hc = confirm_or_override(
                suggested_b,
                "Rubric B — strength of support",
                VALID_CONFIDENCE,
            )
        else:
            print(RUBRIC_A_GUIDE)
            vd = prompt_choice("Rubric A — valid decision?", VALID_DECISION)
            if vd is None:
                continue
            print(RUBRIC_B_GUIDE)
            hc = prompt_choice("Rubric B — strength of support", VALID_CONFIDENCE)
            if hc is None:
                continue

        notes = input("  Notes — optional one-line rationale: ").strip()

        item["human_valid_decision"] = vd
        item["human_confidence"] = hc
        item["human_notes"] = notes or None
        if checks:
            item["human_checks"] = checks
        save(manifest, manifest_path)
        print("  Saved.")

    save(manifest, manifest_path)
    print("\nAll 50 items rated. Run with --summary to verify.")


def import_csv(manifest: dict, manifest_path: Path) -> None:
    if not CSV_PATH.is_file():
        print(f"No CSV at {CSV_PATH}")
        return
    by_index = {int(row["sample_index"]): row for row in csv.DictReader(CSV_PATH.open(encoding="utf-8"))}
    for item in manifest["items"]:
        row = by_index.get(item["sample_index"])
        if not row:
            continue
        for key in ("human_valid_decision", "human_confidence", "human_notes"):
            val = (row.get(key) or "").strip()
            if val:
                item[key] = val
    save(manifest, manifest_path)
    print(f"Imported ratings from {CSV_PATH}")


PRISTINE_BACKUP = ROOT / "configs/evaluation/backups/confidence_validation_sample_pristine.json"


def reset_pristine_manifest() -> None:
    if not PRISTINE_BACKUP.is_file():
        print(f"Missing backup: {PRISTINE_BACKUP}")
        sys.exit(1)
    SAMPLE_PATH.write_bytes(PRISTINE_BACKUP.read_bytes())
    print(f"Restored pristine manifest from {PRISTINE_BACKUP}")
    print(f"  → {SAMPLE_PATH}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Rate Phase 2b validation sample")
    parser.add_argument("--export-csv", action="store_true", help="Export blank/filled CSV for Excel")
    parser.add_argument("--import-csv", action="store_true", help="Import human_* columns from CSV")
    parser.add_argument("--summary", action="store_true", help="Show progress only")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=SAMPLE_PATH,
        help="Manifest to read/write (default: pristine sample; use provisional path for dev)",
    )
    parser.add_argument(
        "--reset-pristine",
        action="store_true",
        help="Restore confidence_validation_sample.json from backups/ (no ratings)",
    )
    parser.add_argument(
        "--checklist",
        action="store_true",
        help="Use 2-check evidence rubric for Rubric B (after Rubric A); recommended",
    )
    parser.add_argument(
        "--show-triangulation",
        action="store_true",
        help="Show prior triangulation labels while rating (not blind)",
    )
    args = parser.parse_args()

    if args.reset_pristine:
        reset_pristine_manifest()
        return 0

    manifest_path = args.manifest.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if args.export_csv:
        export_csv(manifest)
        return 0
    if args.import_csv:
        import_csv(manifest, manifest_path)
        summary(manifest)
        return 0
    if args.summary:
        summary(manifest)
        return 0

    run_interactive(
        manifest,
        manifest_path,
        blind=not args.show_triangulation,
        use_checklist=args.checklist,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
