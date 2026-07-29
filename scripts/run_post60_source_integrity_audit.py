#!/usr/bin/env python3
"""
Post-60 Source-Integrity audit CLI.

Phase 0 behaviour:
- Always runs automated screening and writes:
  screening_results.csv, flagged_entries.csv, audit_working.csv,
  corrected_adjudication_copy.csv, corrections_preview.csv, audit_log.jsonl,
  SOURCE_INTEGRITY_AUDIT_REPORT.md, manifest.json, SHA256SUMS.txt
- Interactive human review is optional and should be invoked explicitly:
  - Use --screen-only to skip interactive review.

Never modify completed adjudication data in-place.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from typing import Any

from post60_source_integrity_audit_lib import (
    AuditSession,
    default_audit_paths,
    validate_corrected_evidence_excerpt,
    write_screening_outputs,
    build_queue,
    now_iso,
)


def _load_hr_module() -> Any:
    """Import the existing interactive JEE/DQ adjudication CLI as a helper library."""
    scripts_dir = Path(__file__).resolve().parent
    hr_path = scripts_dir / "run_jee_dq_human_review.py"
    spec = importlib.util.spec_from_file_location("_hr", hr_path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work-dir", required=True, type=Path)
    ap.add_argument("--source-review-dir", required=True, type=Path)
    ap.add_argument("--protocol-v2-dir", required=True, type=Path)
    ap.add_argument("--mode", default="critical", choices=["critical", "standard", "pending", "deferred", "all", "targeted"])
    ap.add_argument("--batch-size", default=10, type=int)
    ap.add_argument("--reviewer-name", default="AL", type=str)
    ap.add_argument("--entry-ids", default="", type=str)
    ap.add_argument("--screen-only", action="store_true")
    ap.add_argument("--resume", action="store_true")
    return ap.parse_args()


def _prompt(msg: str) -> str:
    return input(msg).strip()


def _print_entry_panels(hr: Any, audit_row: dict[str, str]) -> None:
    print("\n" + "=" * 84)
    print(f"ENTRY {audit_row.get('entry_id')} | review_priority={audit_row.get('review_priority')} | status={audit_row.get('audit_review_status')}")
    print("=" * 84)

    # A) Original source fields
    print("\nA. ORIGINAL SOURCE FIELDS (generated candidate + frozen extracts)")
    print(f"  Generated Decision: {audit_row.get('decision','')}")
    print(f"  Evidence          : {audit_row.get('evidence','')}")
    print(f"  Source Quote      : {audit_row.get('source_quote','')}")
    print(f"  traceability_ok   : {audit_row.get('traceability_ok','')}")
    print(f"  original review_flags: {audit_row.get('review_flags','')}")

    # B) Existing human coding
    print("\nB. EXISTING HUMAN CODING")
    print("  JEE:")
    print(f"    human_JEE_decision      : {audit_row.get('human_JEE_decision','')}")
    print(f"    human_primary_JEE       : {audit_row.get('human_primary_JEE','')}")
    print(f"    human_secondary_JEE     : {audit_row.get('human_secondary_JEE','')}")
    print(f"    human_JEE_confidence    : {audit_row.get('human_JEE_confidence','')}")
    print(f"    human_JEE_rationale     : {audit_row.get('human_JEE_rationale','')}")
    print(f"    human_JEE_evidence      : {audit_row.get('human_JEE_evidence','')}")

    print("  DQ:")
    print(f"    human_DQ_decision       : {audit_row.get('human_DQ_decision','')}")
    print(f"    human_primary_DQ        : {audit_row.get('human_primary_DQ','')}")
    print(f"    human_secondary_DQ      : {audit_row.get('human_secondary_DQ','')}")
    print(f"    human_DQ_confidence     : {audit_row.get('human_DQ_confidence','')}")
    print(f"    human_DQ_rationale      : {audit_row.get('human_DQ_rationale','')}")
    print(f"    human_DQ_evidence      : {audit_row.get('human_DQ_evidence','')}")

    print("  Policy / inquiry:")
    print(f"    human_policy_vs_inquiry : {audit_row.get('human_policy_vs_inquiry','')}")
    print(f"    human_overall_rationale : {audit_row.get('human_overall_rationale','')}")

    print("  Statement type:")
    print(f"    human_candidate_statement_type : {audit_row.get('human_candidate_statement_type','')}")

    print("\n  Evidence provenance (explicitly labelled INFERRED):")
    print(f"    inferred_evidence_source           : {audit_row.get('inferred_evidence_source','')}")
    print(f"    inferred_evidence_source_confidence: {audit_row.get('inferred_evidence_source_confidence','')}")
    print(f"    inferred_evidence_source_basis    : {audit_row.get('inferred_evidence_source_basis','')}")

    # C) Automated flags
    print("\nC. AUDIT FLAGS (automated screening)")
    rf = audit_row.get("automated_risk_flags", "") or ""
    fr = audit_row.get("automated_flag_reasons", "") or ""
    print(f"  automated_risk_flags : {rf}")
    if fr:
        print(f"  automated_flag_reasons: {fr}")


def interactive_review(args: argparse.Namespace) -> None:
    paths = default_audit_paths(args.work_dir)
    audit = AuditSession(paths=paths)
    audit.load()

    hr = _load_hr_module()

    entry_ids = [x.strip() for x in args.entry_ids.split(",") if x.strip()]
    queue = build_queue(audit.audit_rows, mode=args.mode, entry_ids=entry_ids)

    session_state = audit.load_session_state()
    reviewed = set(session_state.get("reviewed_entry_ids", []))

    print(f"Audit session: session_id={session_state.get('session_id')} reviewer={args.reviewer_name}")
    print(f"Mode={args.mode} queue_size={len(queue)} batch_size={args.batch_size} resume={args.resume}")

    # Skip reviewed if resume
    if args.resume:
        queue = [r for r in queue if r.get("entry_id") not in reviewed]

    # Batch loop
    processed = 0
    for audit_row in queue:
        if processed >= args.batch_size:
            break
        eid = audit_row.get("entry_id")
        if not eid:
            continue

        _print_entry_panels(hr, audit_row)

        # Candidate support step 1 (one-key)
        print("\nStep 1 — Candidate support")
        print("  1 verbatim_supported")
        print("  2 paraphrase_supported")
        print("  3 partially_supported")
        print("  4 unsupported")
        print("  5 contradicted")
        print("  6 defer")
        raw = _prompt("Select (1-6): ")
        cand_map = {
            "1": "verbatim_supported",
            "2": "paraphrase_supported",
            "3": "partially_supported",
            "4": "unsupported",
            "5": "contradicted",
            "6": "defer",
        }
        if raw not in cand_map:
            print("Invalid selection; skipping entry.")
            continue
        candidate_support = cand_map[raw]

        # Correction step 2 (keep_all extremely quick)
        print("\nStep 2 — Existing human coding action")
        print("  1 keep_all")
        print("  2 edit_evidence_only")
        print("  3 edit_statement_type")
        print("  4 edit_JEE")
        print("  5 edit_DQ")
        print("  6 edit_policy_inquiry")
        print("  7 edit_rationale")
        print("  8 edit_multiple_fields")
        print("  9 defer")
        raw2 = _prompt("Select (1-9): ")

        action_map = {
            "1": "keep_all",
            "2": "edit_evidence_only",
            "3": "edit_statement_type",
            "4": "edit_JEE",
            "5": "edit_DQ",
            "6": "edit_policy_inquiry",
            "7": "edit_rationale",
            "8": "edit_multiple_fields",
            "9": "defer",
        }
        if raw2 not in action_map:
            print("Invalid selection; skipping entry.")
            continue
        action = action_map[raw2]

        # For Phase 0, implement keep_all/defer now; evidence editing scaffold with strict validators.
        if action == "keep_all":
            audit.apply_keep_all(entry_id=eid, candidate_support=candidate_support, reviewer=args.reviewer_name)
            processed += 1
            continue
        if action == "defer":
            audit.apply_defer(entry_id=eid, reviewer=args.reviewer_name)
            processed += 1
            continue

        if action != "edit_evidence_only":
            print("Only keep_all/defer/edit_evidence_only are implemented in this Phase 0 build. Using defer.")
            audit.apply_defer(entry_id=eid, reviewer=args.reviewer_name, audit_reason=f"unimplemented_action:{action}")
            processed += 1
            continue

        # edit_evidence_only
        # Choose which evidence field to edit
        print("Editing evidence excerpts. Evidence may only be selected from Evidence or Source Quote (or exact substrings).")
        which = _prompt("Edit which? (1 human_JEE_evidence, 2 human_DQ_evidence, 3 both): ")
        # reload current row from audit list
        row_idx = next(i for i, r in enumerate(audit.audit_rows) if r.get("entry_id") == eid)
        before_row = dict(audit.audit_rows[row_idx])
        after_row = dict(audit.audit_rows[row_idx])

        source_fields_updated: list[str] = []
        source_excerpts_used: dict[str, str] = {}
        try:
            if which in ("1", "3"):
                new_ex = _prompt(f"New human_JEE_evidence excerpt (blank allowed): ")
                if new_ex.strip():
                    src_field, _ = validate_corrected_evidence_excerpt(excerpt=new_ex, row=before_row, evidence_field="human_JEE_evidence")
                    source_fields_updated.append(src_field)
                    source_excerpts_used["human_JEE_evidence"] = new_ex
                after_row["human_JEE_evidence"] = new_ex
            if which in ("2", "3"):
                new_ex = _prompt(f"New human_DQ_evidence excerpt (blank allowed): ")
                if new_ex.strip():
                    src_field, _ = validate_corrected_evidence_excerpt(excerpt=new_ex, row=before_row, evidence_field="human_DQ_evidence")
                    source_fields_updated.append(src_field)
                    source_excerpts_used["human_DQ_evidence"] = new_ex
                after_row["human_DQ_evidence"] = new_ex

            # Update audit fields first
            after_row["candidate_support"] = candidate_support
            after_row["audit_review_status"] = "human_reviewed_corrected"

            audit.audit_rows[row_idx] = after_row

            # Persist via direct event logging for changed audit fields and edited evidence fields
            session_state2 = audit.load_session_state()
            session_id = session_state2.get("session_id")
            risk_flags = [f for f in (after_row.get("automated_risk_flags") or "").split("|") if f]
            # Events for any changed fields in audit_working + edited evidence excerpts
            changed_fields = [f for f in ("human_JEE_evidence", "human_DQ_evidence", "candidate_support", "audit_review_status") if before_row.get(f, "") != after_row.get(f, "")]
            for f in changed_fields:
                from post60_source_integrity_audit_lib import record_audit_event  # local import to avoid cycles

                record_audit_event(
                    audit_log_jsonl=paths.audit_log_jsonl,
                    entry_row_before=before_row,
                    entry_row_after=after_row,
                    field=f,
                    action="human_correction",
                    session_id=session_id,
                    reviewer=args.reviewer_name,
                    candidate_support=candidate_support,
                    risk_flags=risk_flags,
                    audit_reason=f"edit_evidence_only:{eid}",
                    source_field=";".join(sorted(set(source_fields_updated))) if source_fields_updated else "",
                    source_excerpt=source_excerpts_used.get(f, ""),
                    provenance="human_edit_evidence",
                )

            # Update reviewed_entry_ids in session state
            session_state2.setdefault("reviewed_entry_ids", [])
            if eid not in session_state2["reviewed_entry_ids"]:
                session_state2["reviewed_entry_ids"].append(eid)
            session_state2["updated_at_utc"] = now_iso()
            # Also update the corrected adjudication copy so the audited evidence edit is preserved.
            if audit.corrected_rows:
                ci = next(i for i, r in enumerate(audit.corrected_rows) if r.get("entry_id") == eid)
                corrected_after = dict(audit.corrected_rows[ci])
                if "human_JEE_evidence" in after_row:
                    corrected_after["human_JEE_evidence"] = after_row["human_JEE_evidence"]
                if "human_DQ_evidence" in after_row:
                    corrected_after["human_DQ_evidence"] = after_row["human_DQ_evidence"]
                audit.corrected_rows[ci] = corrected_after
            audit.save_session_state(session_state2)
            audit.save_all()

            processed += 1
        except Exception as e:
            print(f"Evidence edit rejected: {e}")
            # leave unchanged; do not modify audit/corrected rows


def main() -> int:
    args = parse_args()
    args.work_dir.mkdir(parents=True, exist_ok=True)

    paths = default_audit_paths(args.work_dir)

    # Screening output generation if missing or forced
    if not paths.audit_working_csv.is_file() or args.screen_only:
        # Always run screening-only to produce deterministic outputs unless interactive already exists.
        write_screening_outputs(
            source_dir=args.source_review_dir,
            protocol_v2_dir=args.protocol_v2_dir,
            work_dir=args.work_dir,
            reviewer_name=args.reviewer_name,
            batch_size=args.batch_size,
        )

    if args.screen_only:
        print(f"Screening complete. Outputs written to: {args.work_dir}")
        return 0

    # Interactive review
    interactive_review(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

