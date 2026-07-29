from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from post60_source_integrity_audit_lib import (  # noqa: E402
    AuditSession,
    build_queue,
    sha256_file,
    validate_corrected_evidence_excerpt,
    write_screening_outputs,
    read_csv_rows,
    default_audit_paths,
)


SOURCE_REVIEW_DIR = ROOT / "outputs/framework_mapping/run_20260726_045745_JEE_DQ_human_adjudication"
PROTOCOL_V2_DIR = ROOT / "outputs/framework_mapping/run_20260726_035733_JEE_DQ_protocol_v2"


DECISION_ONLY_IDS = {"phase1-003", "phase1-020", "phase1-166", "phase1-217", "phase1-281"}
TRACEABILITY_FALSE_IDS = {"phase1-007", "phase1-161", "phase1-314", "phase1-396", "phase1-382", "phase1-117", "phase1-274"}
QUESTION_LIKE_IDS = {"phase1-090", "phase1-396"}


def _run_screening(tmp_path: Path) -> Path:
    work_dir = tmp_path / "post60_source_integrity_audit"
    write_screening_outputs(
        source_dir=SOURCE_REVIEW_DIR,
        protocol_v2_dir=PROTOCOL_V2_DIR,
        work_dir=work_dir,
        reviewer_name="AL",
        batch_size=10,
    )
    return work_dir


def _load_audit_rows(work_dir: Path) -> list[dict[str, str]]:
    rows, _ = read_csv_rows(work_dir / "audit_working.csv")
    return rows


def _load_corrected_rows(work_dir: Path) -> list[dict[str, str]]:
    rows, _ = read_csv_rows(work_dir / "corrected_adjudication_copy.csv")
    return rows


def _risk_flags_set(r: dict[str, str]) -> set[str]:
    return {f for f in (r.get("automated_risk_flags") or "").split("|") if f}


def test_source_directory_hashes_unchanged(tmp_path: Path) -> None:
    protected = [
        SOURCE_REVIEW_DIR / "HUMAN_MAPPING_REVIEW_V2_WORKING.csv",
        SOURCE_REVIEW_DIR / "HUMAN_MAPPING_REVIEW_V2_AUDIT_LOG.jsonl",
        SOURCE_REVIEW_DIR / "REVIEW_SESSION_STATE.json",
        SOURCE_REVIEW_DIR / "REVIEW_PROGRESS.md",
        SOURCE_REVIEW_DIR / "IMPLEMENTATION_PROVENANCE.json",
    ]
    before = {p: sha256_file(p) for p in protected}
    _run_screening(tmp_path)
    after = {p: sha256_file(p) for p in protected}
    assert before == after


def test_decision_cannot_be_stored_as_corrected_evidence_source(tmp_path: Path) -> None:
    work_dir = _run_screening(tmp_path)
    # Load original rows for validator tests
    rows, _ = read_csv_rows(SOURCE_REVIEW_DIR / "HUMAN_MAPPING_REVIEW_V2_WORKING.csv")
    by_id = {r["entry_id"]: r for r in rows}

    # Decision-only excerpt (phase1-003 JEE evidence equals decision text and is decision-only)
    r003 = by_id["phase1-003"]
    decision_excerpt = r003["decision"]
    with pytest.raises(ValueError):
        validate_corrected_evidence_excerpt(excerpt=decision_excerpt, row=r003, evidence_field="human_JEE_evidence")

    # Exact match case: phase1-298 decision equals source_quote; validator should accept and attribute Source Quote.
    r298 = by_id["phase1-298"]
    src_field, _ = validate_corrected_evidence_excerpt(excerpt=r298["decision"], row=r298, evidence_field="human_JEE_evidence")
    assert "Source Quote" in src_field


def test_exact_substring_validation_accepts_source_quote_substring(tmp_path: Path) -> None:
    _run_screening(tmp_path)
    rows, _ = read_csv_rows(SOURCE_REVIEW_DIR / "HUMAN_MAPPING_REVIEW_V2_WORKING.csv")
    by_id = {r["entry_id"]: r for r in rows}
    r396 = by_id["phase1-396"]
    sq = r396["source_quote"]
    candidate = sq[:40]
    src_field, _ = validate_corrected_evidence_excerpt(excerpt=candidate, row=r396, evidence_field="human_JEE_evidence")
    assert src_field in ("Source Quote", "Evidence+Source Quote", "Evidence")


def test_question_like_and_traceability_flags_are_present(tmp_path: Path) -> None:
    work_dir = _run_screening(tmp_path)
    audit_rows = _load_audit_rows(work_dir)
    by_id = {r["entry_id"]: r for r in audit_rows}

    for eid in QUESTION_LIKE_IDS:
        rf = _risk_flags_set(by_id[eid])
        assert "quote_is_question" in rf

    for eid in TRACEABILITY_FALSE_IDS:
        rf = _risk_flags_set(by_id[eid])
        assert "traceability_false" in rf


def test_unsupported_added_detail_flag_is_stored(tmp_path: Path) -> None:
    work_dir = _run_screening(tmp_path)
    audit_rows = _load_audit_rows(work_dir)
    rf_any = [r for r in audit_rows if "unsupported_added_detail" in _risk_flags_set(r)]
    assert len(rf_any) >= 1


def test_critical_queue_includes_decision_only_ids_and_is_first(tmp_path: Path) -> None:
    work_dir = _run_screening(tmp_path)
    audit_rows = _load_audit_rows(work_dir)

    q_pending = build_queue(audit_rows, mode="pending", entry_ids=[])
    assert q_pending, "queue should not be empty"

    # Critical queue is presented before standard queue: until first non-critical, all should be critical.
    seen_standard = False
    for r in q_pending:
        if r.get("review_priority") != "critical":
            seen_standard = True
        if seen_standard:
            # after we see standard, no more critical should appear
            assert r.get("review_priority") != "critical"

    q_critical = build_queue(audit_rows, mode="critical", entry_ids=[])
    q_critical_ids = {r["entry_id"] for r in q_critical}
    assert DECISION_ONLY_IDS.issubset(q_critical_ids)


def test_blank_evidence_is_not_treated_as_auto_error(tmp_path: Path) -> None:
    work_dir = _run_screening(tmp_path)
    audit_rows = _load_audit_rows(work_dir)

    # Find a row where JEE decision is one of the "allowed to be blank" statuses and JEE evidence is blank.
    allowed = {"no_mapping", "insufficient_evidence", "procedural_or_inquiry"}
    picked = None
    for r in audit_rows:
        if (r.get("human_JEE_decision") in allowed) and not (r.get("human_JEE_evidence") or "").strip():
            picked = r
            break
    assert picked is not None, "expected at least one blank JEE evidence row under allowed status"

    # Screening should not set decision_used_as_evidence purely because evidence is blank.
    rf = _risk_flags_set(picked)
    assert "decision_used_as_evidence" not in rf


def test_inferred_evidence_provenance_fields_are_marked_inferred(tmp_path: Path) -> None:
    work_dir = _run_screening(tmp_path)
    screening_rows, cols = read_csv_rows(work_dir / "screening_results.csv")
    # Ensure explicit historical source labels are not introduced.
    forbidden_substrings = {"human_evidence_source", "explicit_evidence_source", "historical"}
    assert not any(any(s in c for s in forbidden_substrings) for c in cols)

    # Ensure inferred fields exist.
    for c in ["inferred_evidence_source", "inferred_evidence_source_basis", "inferred_evidence_source_confidence"]:
        assert c in cols


def test_keep_all_is_substantive_noop_and_writes_audit_events(tmp_path: Path) -> None:
    work_dir = _run_screening(tmp_path)
    # Load original corrected rows for comparison
    orig_rows, _ = read_csv_rows(SOURCE_REVIEW_DIR / "HUMAN_MAPPING_REVIEW_V2_WORKING.csv")
    orig_by_id = {r["entry_id"]: r for r in orig_rows}

    session_paths = default_audit_paths(work_dir)
    session = AuditSession(paths=session_paths)
    session.load()

    # Pick a pending entry
    pending = [r for r in session.audit_rows if r.get("audit_review_status") != "auto_clear"]
    assert pending
    eid = pending[0]["entry_id"]
    cand = "verbatim_supported"

    session.apply_keep_all(entry_id=eid, candidate_support=cand, reviewer="AL", audit_reason="unit_test_keep_all")

    # Corrected copy must remain human-field identical
    ci = next(i for i, r in enumerate(session.corrected_rows) if r.get("entry_id") == eid)
    corrected_row = session.corrected_rows[ci]
    # Compare substantive human fields
    human_fields = [
        "human_candidate_statement_type",
        "human_JEE_decision",
        "human_primary_JEE",
        "human_secondary_JEE",
        "human_JEE_evidence",
        "human_JEE_confidence",
        "human_JEE_rationale",
        "human_DQ_decision",
        "human_primary_DQ",
        "human_secondary_DQ",
        "human_DQ_evidence",
        "human_DQ_confidence",
        "human_DQ_rationale",
        "human_policy_vs_inquiry",
        "human_overall_rationale",
    ]
    for f in human_fields:
        assert corrected_row.get(f, "") == orig_by_id[eid].get(f, "")

    # Autosave: session state should persist reviewed_entry_ids
    state = json.loads((session_paths.session_state_json).read_text(encoding="utf-8"))
    assert eid in state.get("reviewed_entry_ids", [])

    # Resume: reloading should keep the updated audit_working labels
    session_reload = AuditSession(paths=session_paths)
    session_reload.load()
    row_reload = next(r for r in session_reload.audit_rows if r.get("entry_id") == eid)
    assert row_reload.get("audit_review_status") == "human_reviewed_keep"
    assert row_reload.get("candidate_support") == cand

    # Audit log must contain events for changed audit fields
    audit_log_path = session_paths.audit_log_jsonl
    lines = [json.loads(l) for l in audit_log_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert lines, "audit log should not be empty after keep_all"
    changed_fields = {evt["field"] for evt in lines if evt["entry_id"] == eid}
    assert "candidate_support" in changed_fields
    assert "audit_review_status" in changed_fields


def test_deferred_entries_remain_pending_and_queue_supports_deferred_mode(tmp_path: Path) -> None:
    work_dir = _run_screening(tmp_path)
    session_paths = default_audit_paths(work_dir)
    session = AuditSession(paths=session_paths)
    session.load()
    pending = [r for r in session.audit_rows if r.get("audit_review_status") != "auto_clear"]
    eid = pending[-1]["entry_id"]
    session.apply_defer(entry_id=eid, reviewer="AL", audit_reason="unit_test_defer")

    # Reload for queue check
    session2 = AuditSession(paths=session_paths)
    session2.load()
    q_deferred = build_queue(session2.audit_rows, mode="deferred", entry_ids=[])
    assert any(r["entry_id"] == eid for r in q_deferred)


def test_targeted_queue_filters_entry_ids(tmp_path: Path) -> None:
    work_dir = _run_screening(tmp_path)
    audit_rows = _load_audit_rows(work_dir)
    q = build_queue(audit_rows, mode="targeted", entry_ids=["phase1-003", "phase1-020"])
    ids = {r["entry_id"] for r in q}
    assert ids == {"phase1-003", "phase1-020"}


def test_corrected_copy_contains_all_60_entries(tmp_path: Path) -> None:
    work_dir = _run_screening(tmp_path)
    corrected = _load_corrected_rows(work_dir)
    assert len(corrected) == 60
    assert len({r["entry_id"] for r in corrected}) == 60

