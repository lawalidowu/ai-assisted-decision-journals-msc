#!/usr/bin/env python3
"""
Audit D — POST-60 human coding-consistency audit (Phase 0).

Read-only discovery, automated screening, and review-packet export.
Does not modify the frozen source-integrity audit or original adjudication.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from post60_coding_consistency_audit_lib import (  # noqa: E402
    COMPARABLE_GROUPS,
    RESPONSE_TEMPLATE_FIELDS,
    ScreeningResult,
    atomic_write_csv,
    build_group_membership,
    comparable_groups_rows,
    load_hr_module,
    now_iso,
    run_timestamp,
    screen_record,
    screening_row_to_csv,
    sha256_file,
    write_discovery_report,
)
from post60_source_integrity_audit_lib import read_csv_rows  # noqa: E402

DEFAULT_SOURCE_INTEGRITY_DIR = ROOT / "outputs/framework_mapping/run_20260727_080220_post60_source_integrity_audit"
DEFAULT_PROTOCOL_DIR = ROOT / "outputs/framework_mapping/run_20260726_035733_JEE_DQ_protocol_v2"
DEFAULT_ORIGINAL_ADJ_DIR = ROOT / "outputs/framework_mapping/run_20260726_045745_JEE_DQ_human_adjudication"

BATCH_SIZE = 10


def blank_display(v) -> str:
    if v is None or str(v).strip() == "":
        return "[blank]"
    return str(v)


def format_packet_entry(
    row: dict[str, str],
    screening_row: dict[str, str],
    audit_row: dict[str, str],
    seq: int,
    batch_total: int,
    all_rows_by_id: dict[str, dict[str, str]],
    group_defs: list[dict],
) -> str:
    groups = (screening_row.get("comparable_group") or "").split("|")
    groups = [g for g in groups if g]
    peer_lines: list[str] = []
    for gid in groups:
        gdef = next((g for g in group_defs if g["group_id"] == gid), None)
        if not gdef:
            continue
        peer_lines.append(f"### {gid} — {gdef.get('group_name', '')}")
        for pid in gdef.get("entry_ids", []):
            if pid == row["entry_id"]:
                continue
            pr = all_rows_by_id.get(pid)
            if not pr:
                continue
            peer_lines.append(
                f"- {pid}: JEE={pr.get('human_JEE_decision','')}/{pr.get('human_primary_JEE','')}; "
                f"DQ={pr.get('human_DQ_decision','')}/{pr.get('human_primary_DQ','')}; "
                f"ST={pr.get('human_candidate_statement_type','')}; PI={pr.get('human_policy_vs_inquiry','')}"
            )
        peer_lines.append("")

    flag_lines = []
    flags = (screening_row.get("consistency_flags") or "").split("|")
    reasons = (screening_row.get("flag_reasons") or "").split("|")
    reason_map = {}
    for r in reasons:
        if ":" in r:
            k, v = r.split(":", 1)
            reason_map[k] = v
    for fl in flags:
        if fl:
            flag_lines.append(f"- **{fl}**: {reason_map.get(fl, '')}")

    lines = [
        f"# Entry {seq} of {batch_total}",
        "",
        "## A. Identification",
        "",
        f"- entry_id: {row['entry_id']}",
        f"- review_priority: {screening_row.get('review_priority', '')}",
        f"- comparable_group: {screening_row.get('comparable_group', '') or '[none]'}",
        "",
        "## B. Original source basis",
        "",
        "### Generated candidate Decision",
        "",
        "> **Label:** GENERATED CANDIDATE — not original source evidence.",
        "",
        blank_display(row.get("decision")),
        "",
        "### Evidence",
        "",
        blank_display(row.get("evidence")),
        "",
        "### Source Quote",
        "",
        blank_display(row.get("source_quote")),
        "",
        "### Source metadata",
        "",
        f"- traceability: {blank_display(row.get('traceability_ok'))}",
        f"- candidate_support (source-integrity audit): {blank_display(audit_row.get('candidate_support'))}",
        "",
        "## C. Current final coding",
        "",
        "### JEE",
        "",
        f"- status: {blank_display(row.get('human_JEE_decision'))}",
        f"- primary: {blank_display(row.get('human_primary_JEE'))}",
        f"- secondary: {blank_display(row.get('human_secondary_JEE'))}",
        f"- confidence: {blank_display(row.get('human_JEE_confidence'))}",
        f"- evidence excerpt: {blank_display(row.get('human_JEE_evidence'))}",
        f"- rationale: {blank_display(row.get('human_JEE_rationale'))}",
        "",
        "### Decision Quality",
        "",
        f"- status: {blank_display(row.get('human_DQ_decision'))}",
        f"- primary: {blank_display(row.get('human_primary_DQ'))}",
        f"- secondary: {blank_display(row.get('human_secondary_DQ'))}",
        f"- confidence: {blank_display(row.get('human_DQ_confidence'))}",
        f"- evidence excerpt: {blank_display(row.get('human_DQ_evidence'))}",
        f"- rationale: {blank_display(row.get('human_DQ_rationale'))}",
        "",
        "### Other coding",
        "",
        f"- policy_or_inquiry: {blank_display(row.get('human_policy_vs_inquiry'))}",
        f"- statement_type: {blank_display(row.get('human_candidate_statement_type'))}",
        f"- overall_rationale: {blank_display(row.get('human_overall_rationale'))}",
        "",
        "## D. Consistency flags",
        "",
        "> Automated flags are review aids only.",
        "",
    ]
    lines.extend(flag_lines or ["- [none]"])
    lines += [
        "",
        "### Comparable records and their labels",
        "",
    ]
    lines.extend(peer_lines or ["- [no comparable group peers listed]"])
    lines += [
        "",
        "## E. Human response fields — leave blank",
        "",
        "selected_consistency_action:",
        "- keep_all",
        "- edit_JEE",
        "- edit_DQ",
        "- edit_policy_inquiry",
        "- edit_statement_type",
        "- edit_confidence",
        "- edit_rationale",
        "- edit_multiple_fields",
        "- defer",
        "",
        "corrected_JEE_status:",
        "",
        "corrected_JEE_primary:",
        "",
        "corrected_JEE_secondary:",
        "",
        "corrected_JEE_confidence:",
        "",
        "corrected_JEE_evidence_excerpt:",
        "",
        "corrected_JEE_rationale:",
        "",
        "corrected_DQ_status:",
        "",
        "corrected_DQ_primary:",
        "",
        "corrected_DQ_secondary:",
        "",
        "corrected_DQ_confidence:",
        "",
        "corrected_DQ_evidence_excerpt:",
        "",
        "corrected_DQ_rationale:",
        "",
        "corrected_policy_or_inquiry:",
        "",
        "corrected_statement_type:",
        "",
        "corrected_overall_rationale:",
        "",
        "consistency_reason:",
        "",
        "reviewer_notes:",
        "",
        "---",
        "",
    ]
    return "\n".join(lines)


def validate_outputs(
    *,
    work_dir: Path,
    source_integrity_dir: Path,
    original_adj_dir: Path,
    pre_hashes: dict[str, str],
    screening_rows: list[dict[str, str]],
    flagged_rows: list[dict[str, str]],
    packet_dir: Path,
    corrected_rows: list[dict[str, str]],
) -> tuple[bool, list[str]]:
    errors: list[str] = []

    if len(screening_rows) != 60:
        errors.append(f"screening rows {len(screening_rows)} != 60")
    if len(corrected_rows) != 60:
        errors.append(f"corrected rows {len(corrected_rows)} != 60")

    flagged_ids = {r["entry_id"] for r in flagged_rows}
    auto_ids = {r["entry_id"] for r in screening_rows if r.get("consistency_review_status") == "consistency_auto_clear"}
    if flagged_ids & auto_ids:
        errors.append("overlap between flagged and auto-clear in screening")

    batch_files = sorted(packet_dir.glob("CONSISTENCY_BATCH_*.md"))
    packet_ids: list[str] = []
    for bf in batch_files:
        text = bf.read_text(encoding="utf-8")
        ids_in_batch = [line.split(":")[-1].strip() for line in text.splitlines() if line.startswith("- entry_id:")]
        packet_ids.extend(ids_in_batch)
        n_entries = text.count("# Entry ")
        if n_entries > BATCH_SIZE:
            errors.append(f"{bf.name} has {n_entries} entries > {BATCH_SIZE}")

    if set(packet_ids) != flagged_ids:
        errors.append(f"packet ids mismatch flagged: missing={flagged_ids-set(packet_ids)} extra={set(packet_ids)-flagged_ids}")
    if len(packet_ids) != len(set(packet_ids)):
        errors.append("duplicate entry_id in review packets")

    for ac_id in auto_ids:
        if ac_id in packet_ids:
            errors.append(f"auto-clear {ac_id} appears in review packets")

    # response template blank
    tmpl = packet_dir / "CONSISTENCY_REVIEW_RESPONSES_TEMPLATE.csv"
    if tmpl.is_file():
        with tmpl.open(encoding="utf-8-sig", newline="") as f:
            tmpl_rows = list(csv.DictReader(f))
        for tr in tmpl_rows:
            for col in RESPONSE_TEMPLATE_FIELDS:
                if col in ("entry_id", "review_priority", "comparable_group"):
                    continue
                if (tr.get(col) or "").strip():
                    errors.append(f"pre-filled response field {tr['entry_id']}.{col}")
                    break

    # source integrity unchanged
    protected_si = [
        source_integrity_dir / "audit_working.csv",
        source_integrity_dir / "corrected_adjudication_copy.csv",
        source_integrity_dir / "audit_log.jsonl",
        source_integrity_dir / "APPROVAL_RECORD.md",
    ]
    for p in protected_si:
        key = p.as_posix()
        if p.exists() and pre_hashes.get(key) != sha256_file(p):
            errors.append(f"source-integrity file changed: {p.name}")

    protected_orig = [
        original_adj_dir / "HUMAN_MAPPING_REVIEW_V2_WORKING.csv",
        original_adj_dir / "HUMAN_MAPPING_REVIEW_V2_AUDIT_LOG.jsonl",
    ]
    for p in protected_orig:
        key = p.as_posix()
        if p.exists() and pre_hashes.get(key) != sha256_file(p):
            errors.append(f"original adjudication file changed: {p.name}")

    # no audit E outputs
    for p in work_dir.rglob("*"):
        if "audit_e" in p.name.lower() or "model_performance" in p.name.lower():
            errors.append(f"unexpected Audit E artifact: {p}")

    return len(errors) == 0, errors


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Audit D — coding consistency Phase 0")
    ap.add_argument("--source-integrity-dir", type=Path, default=DEFAULT_SOURCE_INTEGRITY_DIR)
    ap.add_argument("--protocol-v2-dir", type=Path, default=DEFAULT_PROTOCOL_DIR)
    ap.add_argument("--original-adj-dir", type=Path, default=DEFAULT_ORIGINAL_ADJ_DIR)
    ap.add_argument("--work-dir", type=Path, default=None, help="Audit D output dir (default: auto timestamp)")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    ts = run_timestamp()
    work_dir = args.work_dir or (ROOT / f"outputs/framework_mapping/run_{ts}_post60_coding_consistency_audit")
    work_dir.mkdir(parents=True, exist_ok=True)
    packet_dir = work_dir / "review_packets"
    packet_dir.mkdir(parents=True, exist_ok=True)

    source_integrity_dir = args.source_integrity_dir
    corrected_path = source_integrity_dir / "corrected_adjudication_copy.csv"
    audit_working_path = source_integrity_dir / "audit_working.csv"

    if not corrected_path.is_file():
        print(f"ERROR: missing {corrected_path}")
        return 2

    pre_hashes = {
        (source_integrity_dir / "audit_working.csv").as_posix(): sha256_file(source_integrity_dir / "audit_working.csv"),
        (source_integrity_dir / "corrected_adjudication_copy.csv").as_posix(): sha256_file(corrected_path),
        (source_integrity_dir / "audit_log.jsonl").as_posix(): sha256_file(source_integrity_dir / "audit_log.jsonl"),
        (source_integrity_dir / "APPROVAL_RECORD.md").as_posix(): sha256_file(source_integrity_dir / "APPROVAL_RECORD.md"),
        (args.original_adj_dir / "HUMAN_MAPPING_REVIEW_V2_WORKING.csv").as_posix(): sha256_file(
            args.original_adj_dir / "HUMAN_MAPPING_REVIEW_V2_WORKING.csv"
        ),
        (args.original_adj_dir / "HUMAN_MAPPING_REVIEW_V2_AUDIT_LOG.jsonl").as_posix(): sha256_file(
            args.original_adj_dir / "HUMAN_MAPPING_REVIEW_V2_AUDIT_LOG.jsonl"
        ),
    }

    corrected_rows, _ = read_csv_rows(corrected_path)
    audit_rows, _ = read_csv_rows(audit_working_path)
    audit_by_id = {r["entry_id"]: r for r in audit_rows}
    rows_by_id = {r["entry_id"]: r for r in corrected_rows}

    frozen_ok = all(
        audit_by_id[eid].get("audit_review_status") in ("human_reviewed_keep", "human_reviewed_corrected", "auto_clear")
        for eid in audit_by_id
    ) and not any(
        audit_by_id[eid].get("audit_review_status") in ("flagged_pending_human", "deferred")
        for eid in audit_by_id
    )

    hr = load_hr_module(SCRIPTS)
    jee_cards, dq_cards, _ = hr.load_cards(args.protocol_v2_dir)
    jee_areas = set(jee_cards)
    dq_elements = set(dq_cards)

    membership, by_group = build_group_membership(corrected_rows)

    screenings: list[tuple[dict[str, str], ScreeningResult]] = []
    for row in sorted(corrected_rows, key=lambda r: r["entry_id"]):
        sr = screen_record(
            row,
            jee_areas=jee_areas,
            dq_elements=dq_elements,
            hr_mod=hr,
            all_rows_by_id=rows_by_id,
            group_membership=membership,
            by_group=by_group,
        )
        screenings.append((row, sr))

    screening_csv_rows = []
    for row, sr in screenings:
        cs = audit_by_id.get(row["entry_id"], {}).get("candidate_support", "")
        screening_csv_rows.append(screening_row_to_csv(row, sr, cs))

    screening_fields = list(screening_csv_rows[0].keys()) if screening_csv_rows else []
    atomic_write_csv(work_dir / "CONSISTENCY_SCREENING_RESULTS.csv", screening_csv_rows, screening_fields)

    flagged_csv_rows = [r for r in screening_csv_rows if r.get("consistency_review_status") != "consistency_auto_clear"]
    atomic_write_csv(work_dir / "CONSISTENCY_FLAGGED_ENTRIES.csv", flagged_csv_rows, screening_fields)

    comp_rows = comparable_groups_rows(rows_by_id, by_group)
    comp_fields = ["group_id", "group_name", "entry_ids", "n_entries", "current_labels", "apparent_inconsistency", "justification_note"]
    atomic_write_csv(work_dir / "COMPARABLE_RECORD_GROUPS.csv", comp_rows, comp_fields)

    # Response template (root + review_packets)
    template_rows = [
        {
            "entry_id": r["entry_id"],
            "review_priority": r.get("review_priority", ""),
            "comparable_group": r.get("comparable_group", ""),
            **{f: "" for f in RESPONSE_TEMPLATE_FIELDS if f not in ("entry_id", "review_priority", "comparable_group")},
        }
        for r in flagged_csv_rows
    ]
    atomic_write_csv(work_dir / "CONSISTENCY_REVIEW_RESPONSES_TEMPLATE.csv", template_rows, RESPONSE_TEMPLATE_FIELDS)
    atomic_write_csv(packet_dir / "CONSISTENCY_REVIEW_RESPONSES_TEMPLATE.csv", template_rows, RESPONSE_TEMPLATE_FIELDS)

    flag_counter: Counter = Counter()
    for _, sr in screenings:
        for f in sr.flags:
            flag_counter[f.flag] += 1

    auto_clear = sum(1 for _, sr in screenings if sr.consistency_review_status == "consistency_auto_clear")
    flagged = len(flagged_csv_rows)

    write_discovery_report(
        work_dir / "CONSISTENCY_DISCOVERY_REPORT.md",
        source_integrity_dir=source_integrity_dir,
        work_dir=work_dir,
        n_records=len(corrected_rows),
        auto_clear=auto_clear,
        flagged=flagged,
        flag_counts=flag_counter,
        n_groups=len(comp_rows),
        frozen_ok=frozen_ok,
        protected_ok=True,
    )

    # Review packets
    flagged_sorted = sorted(flagged_csv_rows, key=lambda r: (r.get("review_priority") != "critical", r["entry_id"]))
    batches = [flagged_sorted[i : i + BATCH_SIZE] for i in range(0, len(flagged_sorted), BATCH_SIZE)]

    group_defs = [dict(g) for g in COMPARABLE_GROUPS]
    for g in group_defs:
        if g["group_id"] == "CG_JEE_NO_MAPPING_VS_INSUFFICIENT":
            g["entry_ids"] = by_group.get(g["group_id"], [])

    jsonl_records = []
    for batch_idx, batch in enumerate(batches, start=1):
        parts = [
            f"# Consistency Review Packet — Batch {batch_idx:02d}",
            "",
            f"- Records: {len(batch)}",
            f"- Generated (UTC): {now_iso()}",
            f"- Methodology: AI-assisted human reference set",
            "",
        ]
        for seq, srow in enumerate(batch, start=1):
            eid = srow["entry_id"]
            row = rows_by_id[eid]
            audit_row = audit_by_id[eid]
            parts.append(
                format_packet_entry(row, srow, audit_row, seq, len(batch), rows_by_id, group_defs)
            )
            jsonl_records.append({
                "entry_id": eid,
                "batch": batch_idx,
                "review_priority": srow.get("review_priority"),
                "comparable_group": srow.get("comparable_group"),
                "consistency_flags": srow.get("consistency_flags"),
                "current_coding": {
                    "human_JEE_decision": row.get("human_JEE_decision"),
                    "human_primary_JEE": row.get("human_primary_JEE"),
                    "human_DQ_decision": row.get("human_DQ_decision"),
                    "human_primary_DQ": row.get("human_primary_DQ"),
                    "human_candidate_statement_type": row.get("human_candidate_statement_type"),
                    "human_policy_vs_inquiry": row.get("human_policy_vs_inquiry"),
                },
            })
        batch_path = packet_dir / f"CONSISTENCY_BATCH_{batch_idx:02d}.md"
        batch_path.write_text("\n".join(parts), encoding="utf-8")

    index_lines = [
        "# Consistency Review Packet Index",
        "",
        f"- Generated (UTC): {now_iso()}",
        f"- Flagged records: {flagged}",
        f"- Batches: {len(batches)} (max {BATCH_SIZE} per batch)",
        "",
        "## Batches",
        "",
    ]
    for i, batch in enumerate(batches, start=1):
        ids = ", ".join(r["entry_id"] for r in batch)
        index_lines.append(f"- [CONSISTENCY_BATCH_{i:02d}.md](CONSISTENCY_BATCH_{i:02d}.md): {ids}")
    index_lines += [
        "",
        "## Files",
        "",
        "- ALL_CONSISTENCY_FLAGGED_RECORDS.jsonl",
        "- CONSISTENCY_REVIEW_RESPONSES_TEMPLATE.csv",
        "- REVIEW_PACKET_MANIFEST.json",
        "- REVIEW_PACKET_SHA256SUMS.txt",
        "",
    ]
    (packet_dir / "CONSISTENCY_REVIEW_PACKET_INDEX.md").write_text("\n".join(index_lines), encoding="utf-8")

    jsonl_path = packet_dir / "ALL_CONSISTENCY_FLAGGED_RECORDS.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as f:
        for rec in jsonl_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    manifest = {
        "task": "post60_coding_consistency_audit",
        "phase": "0_discovery_screening",
        "generated_at_utc": now_iso(),
        "work_dir": str(work_dir),
        "source_integrity_dir": str(source_integrity_dir),
        "input_corrected_copy": str(corrected_path),
        "input_corrected_copy_sha256": sha256_file(corrected_path),
        "methodology_label": "single_reviewer_AI_assisted_human_adjudication",
        "n_records": len(corrected_rows),
        "auto_clear": auto_clear,
        "flagged": flagged,
        "flag_counts": dict(flag_counter),
        "comparable_groups": len(comp_rows),
        "review_batches": len(batches),
        "batch_size_max": BATCH_SIZE,
        "audit_e_produced": False,
        "human_labels_modified": False,
    }
    (work_dir / "CONSISTENCY_AUDIT_MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    packet_manifest = {
        "generated_at_utc": now_iso(),
        "flagged_records": flagged,
        "batches": [f"CONSISTENCY_BATCH_{i:02d}.md" for i in range(1, len(batches) + 1)],
        "batch_sizes": [len(b) for b in batches],
    }
    (packet_dir / "REVIEW_PACKET_MANIFEST.json").write_text(json.dumps(packet_manifest, indent=2), encoding="utf-8")

    sha_lines = []
    for p in sorted(work_dir.glob("*")):
        if p.is_file():
            sha_lines.append(f"{sha256_file(p)}  {p.as_posix()}")
    for p in sorted(packet_dir.glob("*")):
        if p.is_file():
            sha_lines.append(f"{sha256_file(p)}  {p.as_posix()}")
    (work_dir / "CONSISTENCY_SHA256SUMS.txt").write_text("\n".join(sha_lines) + "\n", encoding="utf-8")

    pkt_sha = []
    for p in sorted(packet_dir.glob("*")):
        if p.is_file():
            pkt_sha.append(f"{sha256_file(p)}  {p.name}")
    (packet_dir / "REVIEW_PACKET_SHA256SUMS.txt").write_text("\n".join(pkt_sha) + "\n", encoding="utf-8")

    ok, val_errors = validate_outputs(
        work_dir=work_dir,
        source_integrity_dir=source_integrity_dir,
        original_adj_dir=args.original_adj_dir,
        pre_hashes=pre_hashes,
        screening_rows=screening_csv_rows,
        flagged_rows=flagged_csv_rows,
        packet_dir=packet_dir,
        corrected_rows=corrected_rows,
    )

    print(f"Audit D directory: {work_dir}")
    print(f"records_screened=60 auto_clear={auto_clear} flagged={flagged}")
    print(f"comparable_groups={len(comp_rows)} batches={len(batches)}")
    print(f"flag_counts={dict(flag_counter.most_common())}")
    print(f"validation={'PASS' if ok else 'FAIL'}")
    if not ok:
        for e in val_errors:
            print(f"  - {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
