#!/usr/bin/env python3
"""
Post-60 Source-Integrity audit library (Phase 1 implementation support).

This module is intentionally written to support:
1) Automated screening (non-interactive)
2) An interactive review loop (optional in the CLI)
3) Deterministic, unit-testable validation and queue construction

Constraints enforced here:
- Corrected evidence may only come from Evidence or Source Quote (or exact substrings thereof).
- The generated Decision text must never be stored as corrected evidence source unless the chosen
  excerpt is also independently present verbatim in Evidence or Source Quote (then attribution
  is Evidence/Source Quote, not Decision).
- Inferred evidence provenance must be explicitly marked as inferred and never treated as an
  historical fact.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_ws(text: str) -> str:
    """Lowercase whitespace-normalised form; ellipsis variants collapsed out."""
    t = (text or "").replace("\u2026", " ").replace("...", " ")
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "of",
    "to",
    "in",
    "for",
    "on",
    "at",
    "by",
    "with",
    "from",
    "as",
    "that",
    "this",
    "was",
    "were",
    "is",
    "are",
    "be",
    "been",
    "being",
    "it",
    "its",
    "we",
    "they",
    "you",
    "i",
    "he",
    "she",
    "their",
    "our",
    "had",
    "have",
    "has",
    "not",
    "but",
    "which",
    "who",
}


def tokenize_content_words(text: str) -> list[str]:
    """Tokenise text for novelty heuristics (screening aid only)."""
    t = normalize_ws(text)
    return [
        tok
        for tok in re.findall(r"[a-z0-9']+", t)
        if tok not in STOPWORDS and len(tok) > 2
    ]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        return rows, list(reader.fieldnames or [])


def atomic_write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})
    tmp.replace(path)


def append_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Evidence provenance inference (from substring membership)
# ---------------------------------------------------------------------------


def _excerpt_hits_sources(excerpt_norm: str, row: dict[str, str]) -> set[str]:
    """Return which of {Decision,Evidence,Source Quote} contain the excerpt (normalised substring)."""
    hits: set[str] = set()
    if not excerpt_norm:
        return hits
    if excerpt_norm in normalize_ws(row.get("decision", "")):
        hits.add("Decision")
    if excerpt_norm in normalize_ws(row.get("evidence", "")):
        hits.add("Evidence")
    if excerpt_norm in normalize_ws(row.get("source_quote", "")):
        hits.add("Source Quote")
    return hits


def _excerpt_exact_hits_sources(excerpt_norm: str, row: dict[str, str]) -> set[str]:
    """Return which of {Decision,Evidence,Source Quote} equal excerpt (normalised exact match)."""
    hits: set[str] = set()
    if not excerpt_norm:
        return hits
    if excerpt_norm == normalize_ws(row.get("decision", "")):
        hits.add("Decision")
    if excerpt_norm == normalize_ws(row.get("evidence", "")):
        hits.add("Evidence")
    if excerpt_norm == normalize_ws(row.get("source_quote", "")):
        hits.add("Source Quote")
    return hits


def infer_evidence_source_for_entry(row: dict[str, str]) -> tuple[str, str, str]:
    """
    Infer the evidence source label for evidence excerpts (JEE and DQ) via substring membership.

    IMPORTANT: this is inferred provenance, not a historical fact. We always mark it with
    `inferred_evidence_source_*` fields and an explicit confidence.
    """
    jee = row.get("human_JEE_evidence") or ""
    dq = row.get("human_DQ_evidence") or ""
    has_any = bool(jee.strip() or dq.strip())
    if not has_any:
        return "blank", "no evidence excerpt provided", "unresolved"

    sources_sub: set[str] = set()
    sources_exact: set[str] = set()
    for excerpt in (jee, dq):
        ex_norm = normalize_ws(excerpt)
        sources_sub |= _excerpt_hits_sources(ex_norm, row)
        sources_exact |= _excerpt_exact_hits_sources(ex_norm, row)

    if not sources_sub:
        return "unresolved", "no normalised substring matches", "unresolved"

    if len(sources_exact) == 1:
        conf = "exact_unique_match"
        inferred = next(iter(sources_exact))
    elif len(sources_exact) > 1:
        conf = "exact_multiple_match"
        inferred = "+".join(sorted(sources_exact))
    elif len(sources_sub) == 1:
        conf = "normalised_unique_match"
        inferred = next(iter(sources_sub))
    else:
        conf = "ambiguous"
        inferred = "+".join(sorted(sources_sub))

    basis = f"substring_hits={'+'.join(sorted(sources_sub))}; exact_hits={'+'.join(sorted(sources_exact))}"
    return inferred, basis, conf


def infer_decision_only_evidence(entry_row: dict[str, str]) -> bool:
    """
    Return True if at least one non-empty evidence excerpt appears in Decision but not in Evidence
    nor Source Quote (for that excerpt).
    """
    for excerpt_field in ("human_JEE_evidence", "human_DQ_evidence"):
        excerpt = (entry_row.get(excerpt_field) or "").strip()
        if not excerpt:
            continue
        ex_norm = normalize_ws(excerpt)
        if ex_norm and ex_norm in normalize_ws(entry_row.get("decision", "")):
            in_evidence = ex_norm in normalize_ws(entry_row.get("evidence", ""))
            in_quote = ex_norm in normalize_ws(entry_row.get("source_quote", ""))  # noqa: E501
            if not in_evidence and not in_quote:
                return True
    return False


# ---------------------------------------------------------------------------
# Automated screening
# ---------------------------------------------------------------------------


def quote_is_question(source_quote: str) -> bool:
    sq = (source_quote or "").strip()
    if not sq:
        return False
    return "?" in sq


def evidence_quote_mismatch(evidence: str, source_quote: str) -> bool:
    e = normalize_ws(evidence)
    q = normalize_ws(source_quote)
    if not e or not q:
        return False
    return not (e in q or q in e)


def source_too_thin(evidence: str, source_quote: str, *, min_chars: int = 60) -> bool:
    e = normalize_ws(evidence)
    q = normalize_ws(source_quote)
    if not e and not q:
        return True
    return (len(e) + len(q)) < min_chars


def unsupported_added_detail_flag(decision: str, evidence: str, source_quote: str) -> tuple[bool, str]:
    """
    Screening-only heuristic: tokens in Decision absent from Evidence+SourceQuote.

    This cannot be treated as proof. We store missing tokens for review UI.
    """
    dec_tokens = set(tokenize_content_words(decision))
    corpus_tokens = set(tokenize_content_words((evidence or "") + " " + (source_quote or "")))
    missing = sorted([t for t in dec_tokens if t not in corpus_tokens])
    if len(missing) >= 3:
        return True, f"decision_novel_tokens={missing[:20]}"
    return False, ""


def detect_procedural_contamination(row: dict[str, str]) -> bool:
    rf = (row.get("review_flags") or "").lower()
    st = (row.get("human_candidate_statement_type") or "").strip()
    if "procedural" not in rf:
        return False
    return st != "procedural_or_inquiry"


def detect_statement_type_depends_on_generated_wording(row: dict[str, str]) -> bool:
    # Minimal heuristic: if statement type is procedural and evidence looks decision-only,
    # reviewers should treat this as potentially generated-wording dependent.
    st = (row.get("human_candidate_statement_type") or "").strip()
    return st == "procedural_or_inquiry" and infer_decision_only_evidence(row)


def infer_possible_context_omission(row: dict[str, str], *, unsupported_added_detail: bool, mismatch: bool) -> bool:
    # Minimal heuristic: novelty + mismatch suggests that added detail may be context-dependent.
    return unsupported_added_detail and mismatch


def strict_normalised_exact_decision_match(decision: str, evidence: str, source_quote: str) -> bool:
    d = normalize_ws(decision)
    if not d:
        return False
    return d == normalize_ws(evidence) or d == normalize_ws(source_quote)


def strict_auto_clear_gate(row: dict[str, str], *, risk_flags: set[str], traceability_false: bool) -> bool:
    """
    Only strict auto-clear:
    - Decision normalised exact match of Evidence or Source Quote
    - decision_used_as_evidence is false
    - traceability_ok is True
    - Source Quote is not a question
    - no unsupported_added_detail
    - no evidence_quote_mismatch
    """
    if traceability_false:
        return False
    if quote_is_question(row.get("source_quote", "")):
        return False
    if strict_normalised_exact_decision_match(row.get("decision", ""), row.get("evidence", ""), row.get("source_quote", "")) is False:
        return False
    if infer_decision_only_evidence(row):
        return False
    if "unsupported_added_detail" in risk_flags:
        return False
    if "evidence_quote_mismatch" in risk_flags:
        return False
    return True


def automated_candidate_support_suggestion(row: dict[str, str], *, risk_flags: set[str]) -> str:
    """
    Produce a suggestion only.

    We avoid setting unsupported/contradicted by automation to prevent silent judgement.
    """
    d = normalize_ws(row.get("decision", ""))
    e = normalize_ws(row.get("evidence", ""))
    q = normalize_ws(row.get("source_quote", ""))
    if not d:
        return "defer"
    if d == e or d == q:
        return "verbatim_supported"
    if e and (d in e or e in d):
        return "paraphrase_supported"
    if q and (d in q or q in d):
        return "paraphrase_supported"
    # If mismatch is present, suggest partially supported rather than unsupported.
    return "partially_supported" if risk_flags else "partially_supported"


def build_critical_queue_ids(audit_rows: list[dict[str, str]], *, decision_only_ids: set[str]) -> set[str]:
    critical_ids: set[str] = set(decision_only_ids)
    # traceability false / quote question
    for r in audit_rows:
        eid = r["entry_id"]
        if str(r.get("traceability_ok", "")).strip().lower() not in ("true", "1", "yes"):
            critical_ids.add(eid)
        if quote_is_question(r.get("source_quote", "")):
            critical_ids.add(eid)
        # Any risk-triggered critical criteria
        rf = set((r.get("automated_risk_flags") or "").split("|")) if r.get("automated_risk_flags") else set()
        if any(
            flag in rf
            for flag in (
                "unsupported_added_detail",
                "evidence_quote_mismatch",
                "statement_type_depends_on_generated_wording",
                "source_too_thin",
                "possible_context_omission",
            )
        ):
            critical_ids.add(eid)
    return critical_ids


# ---------------------------------------------------------------------------
# Output generation / audit session persistence
# ---------------------------------------------------------------------------


AUDIT_ACTION_AUTO = {
    "auto_clear",
}


REVIEW_STATUS_VALUES = [
    "auto_clear",
    "flagged_pending_human",
    "human_reviewed_keep",
    "human_reviewed_corrected",
    "deferred",
]


@dataclass
class AuditPaths:
    work_dir: Path
    screening_results_csv: Path
    flagged_entries_csv: Path
    audit_working_csv: Path
    corrected_copy_csv: Path
    corrections_preview_csv: Path
    audit_log_jsonl: Path
    manifest_json: Path
    sha256_sums_txt: Path
    report_md: Path
    session_state_json: Path


def default_audit_paths(work_dir: Path) -> AuditPaths:
    return AuditPaths(
        work_dir=work_dir,
        screening_results_csv=work_dir / "screening_results.csv",
        flagged_entries_csv=work_dir / "flagged_entries.csv",
        audit_working_csv=work_dir / "audit_working.csv",
        corrected_copy_csv=work_dir / "corrected_adjudication_copy.csv",
        corrections_preview_csv=work_dir / "corrections_preview.csv",
        audit_log_jsonl=work_dir / "audit_log.jsonl",
        manifest_json=work_dir / "manifest.json",
        sha256_sums_txt=work_dir / "SHA256SUMS.txt",
        report_md=work_dir / "SOURCE_INTEGRITY_AUDIT_REPORT.md",
        session_state_json=work_dir / "AUDIT_SESSION_STATE.json",
    )


def build_auto_flags_and_support(row: dict[str, str]) -> dict[str, Any]:
    """
    Compute:
    - automated_candidate_support_suggestion
    - automated_risk_flags (set + pipe string)
    - automated_flag_reasons
    - traceability_false, quote_is_question
    - strict auto-clear gate
    """
    traceability_false = str(row.get("traceability_ok", "")).strip().lower() not in ("true", "1", "yes")
    qflag = quote_is_question(row.get("source_quote", ""))

    mismatch = evidence_quote_mismatch(row.get("evidence", ""), row.get("source_quote", ""))
    thin = source_too_thin(row.get("evidence", ""), row.get("source_quote", ""))
    unsupported, unsupported_notes = unsupported_added_detail_flag(row.get("decision", ""), row.get("evidence", ""), row.get("source_quote", ""))

    decision_used_as_evidence = infer_decision_only_evidence(row)
    procedural_contamination = detect_procedural_contamination(row)
    statement_type_depends = detect_statement_type_depends_on_generated_wording(row)
    possible_context_omission = infer_possible_context_omission(row, unsupported_added_detail=unsupported, mismatch=mismatch)

    risk_flags: set[str] = set()
    reasons: dict[str, str] = {}

    def add(flag: str, reason: str) -> None:
        risk_flags.add(flag)
        reasons[flag] = reason

    if decision_used_as_evidence:
        add("decision_used_as_evidence", "human_evidence_excerpt_matches_decision_not_evidence_or_quote")
    if qflag:
        add("quote_is_question", "source_quote_contains_question_mark")
    if traceability_false:
        add("traceability_false", "traceability_ok=False")
    if unsupported:
        add("unsupported_added_detail", unsupported_notes or "decision_novel_tokens_detected")
    if mismatch:
        add("evidence_quote_mismatch", "evidence_and_source_quote_neither_contains_other")
    if thin:
        add("source_too_thin", "evidence+source_quote_text_too_short")
    if procedural_contamination:
        add("procedural_contamination", "review_flags_contains_procedural_but_statement_type_is_not_procedural_or_inquiry")
    if statement_type_depends:
        add("statement_type_depends_on_generated_wording", "procedural_statement_type_with_decision_only_evidence")
    if possible_context_omission:
        add("possible_context_omission", "unsupported_added_detail_and_evidence_quote_mismatch")
    # risk_flags can be empty

    candidate_support = automated_candidate_support_suggestion(row, risk_flags=risk_flags)

    auto_clear = strict_auto_clear_gate(row, risk_flags=risk_flags, traceability_false=traceability_false)
    audit_review_status = "auto_clear" if auto_clear else "flagged_pending_human"

    return {
        "traceability_false": traceability_false,
        "quote_is_question": qflag,
        "decision_used_as_evidence": decision_used_as_evidence,
        "automated_risk_flags": "|".join(sorted(risk_flags)) if risk_flags else "",
        "automated_flag_reasons": "|".join(f"{k}={reasons.get(k,'')}" for k in sorted(reasons.keys())),
        "automated_candidate_support_suggestion": candidate_support,
        "audit_review_status": audit_review_status,
        "auto_clear": auto_clear,
        "risk_flags_set": risk_flags,
        "unsupported_added_detail_notes": unsupported_notes,
    }


def build_audit_rows_for_screening(source_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """
    Return audit_working rows with screening outputs attached.
    """
    enriched: list[dict[str, str]] = []
    decision_only_ids: set[str] = set()

    # First pass: compute flags/support + inferred evidence source (explicitly inferred)
    for r in source_rows:
        inferred_source, inferred_basis, inferred_conf = infer_evidence_source_for_entry(r)
        auto = build_auto_flags_and_support(r)
        row = dict(r)
        row["original_review_flags"] = r.get("review_flags", "")
        row["traceability"] = r.get("traceability_ok", "")

        # Inferred provenance: never represent as explicit/historical
        row["inferred_evidence_source"] = inferred_source
        row["inferred_evidence_source_basis"] = inferred_basis
        row["inferred_evidence_source_confidence"] = inferred_conf

        row["automated_candidate_support_suggestion"] = auto["automated_candidate_support_suggestion"]
        row["automated_risk_flags"] = auto["automated_risk_flags"]
        row["automated_flag_reasons"] = auto["automated_flag_reasons"]
        row["review_priority"] = "standard"  # placeholder; set after critical queue
        row["audit_review_status"] = auto["audit_review_status"]
        # candidate_support is a human-audit field; populate only for strict auto-clear.
        row["candidate_support"] = (
            "verbatim_supported" if auto["auto_clear"] else ""
        )

        if auto["decision_used_as_evidence"]:
            decision_only_ids.add(r["entry_id"])

        enriched.append(row)

    # Second pass: critical queue IDs
    critical_ids = build_critical_queue_ids(enriched, decision_only_ids=decision_only_ids)
    for r in enriched:
        r["review_priority"] = "critical" if r["entry_id"] in critical_ids else "standard"
    return enriched


def write_screening_outputs(source_dir: Path, protocol_v2_dir: Path, work_dir: Path, *, reviewer_name: str, batch_size: int | None) -> dict[str, Any]:
    """
    Create screening_results.csv, flagged_entries.csv, audit_working.csv,
    corrected_adjudication_copy.csv, corrections_preview.csv, audit_log.jsonl (empty),
    and report/manifest/SHA256.

    This function performs screening only; it does not start interactive review.
    """
    paths = default_audit_paths(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    # Locate completed working CSV
    completed_working_csv = source_dir / "HUMAN_MAPPING_REVIEW_V2_WORKING.csv"
    if not completed_working_csv.is_file():
        raise FileNotFoundError(f"Missing completed results file: {completed_working_csv}")

    rows, fieldnames = read_csv_rows(completed_working_csv)

    # Clone corrected copy base (all 60 original rows must exist)
    corrected_rows = [dict(r) for r in rows]
    corrected_fieldnames = list(fieldnames)
    atomic_write_csv(paths.corrected_copy_csv, corrected_rows, corrected_fieldnames)

    # Ensure audit_log exists empty
    paths.audit_log_jsonl.write_text("", encoding="utf-8")

    # Screening outputs
    audit_rows = build_audit_rows_for_screening(rows)

    # Standardised CSV outputs
    screening_fieldnames = [
        # required original fields
        "entry_id",
        "decision",
        "evidence",
        "source_quote",
        "traceability",
        "original_review_flags",
        # existing human JEE/DQ fields + evidence excerpts
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
        "human_candidate_statement_type",
        "human_overall_rationale",
        # inferred provenance (must be marked inferred, not historical)
        "inferred_evidence_source",
        "inferred_evidence_source_basis",
        "inferred_evidence_source_confidence",
        # automated results
        "automated_candidate_support_suggestion",
        "automated_risk_flags",
        "automated_flag_reasons",
        "review_priority",
        "candidate_support",
        "audit_review_status",
        # include original backing fields for traceability
        "traceability_ok",
        "review_flags",
    ]
    # De-duplicate while preserving order
    seen: set[str] = set()
    screening_fieldnames_dedup: list[str] = []
    for f in screening_fieldnames:
        if f not in seen:
            screening_fieldnames_dedup.append(f)
            seen.add(f)
    screening_fieldnames = screening_fieldnames_dedup

    # audit_working includes all original columns + audit columns
    audit_fieldnames = list(fieldnames) + [
        "original_review_flags",
        "traceability",
        "inferred_evidence_source",
        "inferred_evidence_source_basis",
        "inferred_evidence_source_confidence",
        "automated_candidate_support_suggestion",
        "automated_risk_flags",
        "automated_flag_reasons",
        "review_priority",
        "candidate_support",
        "audit_review_status",
    ]
    # De-duplicate
    audit_seen: set[str] = set()
    audit_fieldnames_dedup: list[str] = []
    for f in audit_fieldnames:
        if f not in audit_seen:
            audit_fieldnames_dedup.append(f)
            audit_seen.add(f)
    audit_fieldnames = audit_fieldnames_dedup

    # Write screening_results.csv (all rows)
    atomic_write_csv(
        paths.screening_results_csv,
        audit_rows,
        fieldnames=screening_fieldnames,
    )

    # flagged_entries.csv (subset)
    flagged = [r for r in audit_rows if r.get("audit_review_status") != "auto_clear"]
    atomic_write_csv(
        paths.flagged_entries_csv,
        flagged,
        fieldnames=screening_fieldnames,
    )

    # audit_working.csv (full 60)
    atomic_write_csv(paths.audit_working_csv, audit_rows, audit_fieldnames)

    # corrections_preview.csv initially: no corrections yet
    atomic_write_csv(
        paths.corrections_preview_csv,
        audit_rows,
        fieldnames=["entry_id", "audit_review_status", "review_priority", "automated_risk_flags"],
    )

    # manifest + hashes + report
    protected_files = [
        completed_working_csv,
        source_dir / "HUMAN_MAPPING_REVIEW_V2_AUDIT_LOG.jsonl",
        source_dir / "REVIEW_PROGRESS.md",
        source_dir / "REVIEW_SESSION_STATE.json",
        source_dir / "IMPLEMENTATION_PROVENANCE.json",
    ]
    manifest = {
        "task": "post60_source_integrity_audit",
        "generated_at_utc": now_iso(),
        "source_review_dir": str(source_dir),
        "protocol_v2_dir": str(protocol_v2_dir),
        "work_dir": str(work_dir),
        "completed_working_csv": str(completed_working_csv),
        "input_files": {str(p): sha256_file(p) for p in protected_files if p.exists()},
        "script_version": "1",
        "reviewer_name": reviewer_name,
        "batch_size": batch_size,
    }
    paths.manifest_json.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # SHA256SUMS.txt: include protected inputs and outputs from this audit run
    out_files = [
        paths.screening_results_csv,
        paths.flagged_entries_csv,
        paths.audit_working_csv,
        paths.corrected_copy_csv,
        paths.corrections_preview_csv,
        paths.audit_log_jsonl,
        paths.manifest_json,
        paths.report_md,  # may not exist yet
    ]
    sha_lines: list[str] = []
    for p in sorted(protected_files):
        if p.exists():
            sha_lines.append(f"{sha256_file(p)}  {p.as_posix()}")
    # Outputs
    for p in [
        paths.screening_results_csv,
        paths.flagged_entries_csv,
        paths.audit_working_csv,
        paths.corrected_copy_csv,
        paths.corrections_preview_csv,
        paths.audit_log_jsonl,
        paths.manifest_json,
    ]:
        sha_lines.append(f"{sha256_file(p)}  {p.as_posix()}")
    paths.sha256_sums_txt.write_text("\n".join(sha_lines) + "\n", encoding="utf-8")

    # Report (screening-only)
    critical_count = len([r for r in audit_rows if r.get("review_priority") == "critical" and r.get("audit_review_status") != "auto_clear"])
    standard_count = len([r for r in audit_rows if r.get("review_priority") == "standard" and r.get("audit_review_status") != "auto_clear"])
    auto_clear_count = len([r for r in audit_rows if r.get("audit_review_status") == "auto_clear"])
    deferred_count = 0
    human_reviewed_keep = 0
    human_reviewed_corrected = 0

    report_lines = [
        "# SOURCE INTEGRITY AUDIT REPORT (Phase 0 screening only)",
        "",
        f"- Total records: {len(audit_rows)}",
        f"- Auto-cleared: {auto_clear_count}",
        f"- Critical pending: {critical_count}",
        f"- Standard pending: {standard_count}",
        f"- Human-reviewed (keep): {human_reviewed_keep}",
        f"- Human-reviewed (corrected): {human_reviewed_corrected}",
        f"- Deferred: {deferred_count}",
        "",
        "## Support / evidence source discovery",
        "- Evidence provenance is reconstructed via substring membership and recorded as *inferred* fields:",
        "  `inferred_evidence_source`, `inferred_evidence_source_basis`, `inferred_evidence_source_confidence`.",
        "",
        "## Automated support-category counts",
        "This screening stage does not compute final unsupported/contradicted judgements. It stores suggestions only.",
        "",
        "## Flag counts (risk flags)",
    ]
    # Count risk flags
    risk_counter: dict[str, int] = {}
    for r in audit_rows:
        flags = [f for f in (r.get("automated_risk_flags") or "").split("|") if f]
        for fl in flags:
            risk_counter[fl] = risk_counter.get(fl, 0) + 1
    for fl in sorted(risk_counter):
        report_lines.append(f"- {fl}: {risk_counter[fl]}")
    report_lines += [
        "",
        "## Queue composition invariants",
        f"- Critical queue includes: decision-only evidence entries, traceability_false entries, question-like quotes, and any entries with: unsupported_added_detail/evidence_quote_mismatch/statement_type_depends_on_generated_wording/source_too_thin/possible_context_omission.",
        "",
        "## Source-file integrity confirmation",
        "- Completed source files are not modified by this screening-only run. SHA256SUMS.txt records baseline hashes.",
        "",
    ]
    paths.report_md.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    # Session state for resume (screening-only run -> no entries reviewed)
    session_state = {
        "session_id": uuid.uuid4().hex[:12],
        "reviewer_name": reviewer_name,
        "created_at_utc": now_iso(),
        "mode": "screening_only",
        "batch_size": batch_size,
        "reviewed_entry_ids": [],
    }
    paths.session_state_json.write_text(json.dumps(session_state, indent=2), encoding="utf-8")

    # Return counts for CLI display / tests
    return {
        "n_rows": len(audit_rows),
        "auto_clear_count": auto_clear_count,
        "critical_pending": critical_count,
        "standard_pending": standard_count,
        "flagged_pending_count": len(flagged),
        "session_id": session_state["session_id"],
    }


# ---------------------------------------------------------------------------
# Evidence validation for corrected copy edits
# ---------------------------------------------------------------------------


def validate_corrected_evidence_excerpt(
    *,
    excerpt: str,
    row: dict[str, str],
    evidence_field: str,
) -> tuple[str, str]:
    """
    Validate that the excerpt is a normalised substring of Evidence or Source Quote.

    Returns:
      (source_field, normalized_excerpt) where source_field is either:
       - "Source Quote"
       - "Evidence"
       - "Evidence+Source Quote" (if it matches both)

    Raises:
      ValueError if excerpt is not allowed.
    """
    ex = (excerpt or "").strip()
    if not ex:
        # blank is allowed; the caller decides based on decision status
        return "", ""

    ex_norm = normalize_ws(ex)
    ev_norm = normalize_ws(row.get("evidence", ""))
    q_norm = normalize_ws(row.get("source_quote", ""))

    in_ev = ex_norm and (ex_norm in ev_norm)
    in_q = ex_norm and (ex_norm in q_norm)

    if not in_ev and not in_q:
        raise ValueError(
            f"{evidence_field}: corrected evidence excerpt must be a normalised substring of "
            "Evidence or Source Quote (not Decision-only)."
        )

    if in_ev and in_q:
        return "Evidence+Source Quote", ex_norm
    if in_q:
        return "Source Quote", ex_norm
    return "Evidence", ex_norm


# ---------------------------------------------------------------------------
# Audit session update primitives (for tests and interactive CLI)
# ---------------------------------------------------------------------------


REVIEW_ACTION_VALUES = [
    "keep_all",
    "edit_evidence_only",
    "edit_statement_type",
    "edit_JEE",
    "edit_DQ",
    "edit_policy_inquiry",
    "edit_rationale",
    "edit_multiple_fields",
    "defer",
]


def record_audit_event(
    *,
    audit_log_jsonl: Path,
    entry_row_before: dict[str, str],
    entry_row_after: dict[str, str],
    field: str,
    action: str,
    session_id: str,
    reviewer: str,
    candidate_support: str,
    risk_flags: list[str],
    audit_reason: str,
    source_field: str,
    source_excerpt: str,
    provenance: str,
) -> None:
    evt = {
        "timestamp": now_iso(),
        "entry_id": entry_row_after.get("entry_id") or entry_row_before.get("entry_id"),
        "field": field,
        "old_value": entry_row_before.get(field, ""),
        "new_value": entry_row_after.get(field, ""),
        "action": action,
        "session_id": session_id,
        "reviewer": reviewer,
        "candidate_support": candidate_support,
        "source_field": source_field,
        "source_excerpt": source_excerpt,
        "risk_flags": risk_flags,
        "audit_reason": audit_reason,
        "provenance": provenance,
    }
    append_jsonl(audit_log_jsonl, [evt])


def apply_keep_all_to_audit_row(
    *,
    audit_row: dict[str, str],
    candidate_support: str,
) -> dict[str, str]:
    # keep_all is fast: only update audit labels
    out = dict(audit_row)
    out["candidate_support"] = candidate_support
    out["audit_review_status"] = "human_reviewed_keep"
    return out


def apply_defer_to_audit_row(*, audit_row: dict[str, str]) -> dict[str, str]:
    out = dict(audit_row)
    out["audit_review_status"] = "deferred"
    return out


def build_queue(
    audit_rows: list[dict[str, str]],
    *,
    mode: str,
    entry_ids: list[str] | None,
) -> list[dict[str, str]]:
    """
    Build review queue with critical-first ordering.

    mode semantics:
    - critical: only critical pending (audit_review_status != auto_clear)
    - standard: only standard pending
    - pending: critical pending first, then standard pending
    - deferred: audit_review_status==deferred
    - all: all non-auto-cleared rows
    - targeted: entry_ids only
    """
    if entry_ids is None:
        entry_ids = []
    idset = set(entry_ids)

    pending = [r for r in audit_rows if r.get("audit_review_status") != "auto_clear"]
    critical = [r for r in pending if r.get("review_priority") == "critical"]
    standard = [r for r in pending if r.get("review_priority") != "critical"]

    if mode == "critical":
        return sorted(critical, key=lambda x: x["entry_id"])
    if mode == "standard":
        return sorted(standard, key=lambda x: x["entry_id"])
    if mode == "pending":
        return sorted(critical, key=lambda x: x["entry_id"]) + sorted(standard, key=lambda x: x["entry_id"])
    if mode == "deferred":
        deferred = [r for r in audit_rows if r.get("audit_review_status") == "deferred"]
        return sorted(deferred, key=lambda x: x["entry_id"])
    if mode == "all":
        return sorted(pending, key=lambda x: x["entry_id"])
    if mode == "targeted":
        filtered = [r for r in audit_rows if r.get("entry_id") in idset]
        # preserve critical-first ordering within targeted
        c = [r for r in filtered if r.get("review_priority") == "critical"]
        s = [r for r in filtered if r.get("review_priority") != "critical"]
        return sorted(c, key=lambda x: x["entry_id"]) + sorted(s, key=lambda x: x["entry_id"])
    raise ValueError(f"unknown mode: {mode}")


def enforce_keep_all_does_not_change_human_fields(
    *,
    original_row: dict[str, str],
    corrected_row: dict[str, str],
) -> None:
    """
    Sanity helper for tests: keep_all must not modify any substantive human fields.
    """
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
    diffs = [(f, original_row.get(f, ""), corrected_row.get(f, "")) for f in human_fields if original_row.get(f, "") != corrected_row.get(f, "")]
    if diffs:
        raise AssertionError(f"keep_all changed substantive human fields: {diffs[:5]}")


# ---------------------------------------------------------------------------
# Audit session persistence (used by tests + interactive CLI)
# ---------------------------------------------------------------------------


class AuditSession:
    """
    Minimal persistence layer for screening + review.

    It supports:
    - loading audit_working.csv + corrected_adjudication_copy.csv
    - applying review actions without interactive prompts
    - autosave after each applied action
    """

    def __init__(self, *, paths: AuditPaths, load_corrected_copy: bool = True):
        self.paths = paths
        self.audit_rows: list[dict[str, str]] = []
        self.corrected_rows: list[dict[str, str]] = []
        self.audit_fieldnames: list[str] = []
        self.corrected_fieldnames: list[str] = []

    def load(self) -> None:
        self.audit_rows, self.audit_fieldnames = read_csv_rows(self.paths.audit_working_csv)
        if self.paths.corrected_copy_csv.is_file():
            self.corrected_rows, self.corrected_fieldnames = read_csv_rows(self.paths.corrected_copy_csv)

    def save_all(self) -> None:
        atomic_write_csv(self.paths.audit_working_csv, self.audit_rows, self.audit_fieldnames)
        if self.corrected_rows and self.corrected_fieldnames:
            atomic_write_csv(self.paths.corrected_copy_csv, self.corrected_rows, self.corrected_fieldnames)

    def load_session_state(self) -> dict[str, Any]:
        if not self.paths.session_state_json.is_file():
            return {}
        return json.loads(self.paths.session_state_json.read_text(encoding="utf-8"))

    def save_session_state(self, state: dict[str, Any]) -> None:
        self.paths.session_state_json.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def _get_index(self, entry_id: str) -> int:
        for i, r in enumerate(self.audit_rows):
            if r.get("entry_id") == entry_id:
                return i
        raise KeyError(f"entry_id not found in audit_working: {entry_id}")

    def _get_corrected_index(self, entry_id: str) -> int:
        for i, r in enumerate(self.corrected_rows):
            if r.get("entry_id") == entry_id:
                return i
        raise KeyError(f"entry_id not found in corrected copy: {entry_id}")

    def apply_keep_all(
        self,
        *,
        entry_id: str,
        candidate_support: str,
        reviewer: str,
        audit_reason: str = "keep_all",
    ) -> None:
        session = self.load_session_state()
        session_id = session.get("session_id") or uuid.uuid4().hex[:12]
        session.setdefault("reviewed_entry_ids", [])

        i = self._get_index(entry_id)
        before = dict(self.audit_rows[i])
        after = apply_keep_all_to_audit_row(audit_row=self.audit_rows[i], candidate_support=candidate_support)
        self.audit_rows[i] = after

        # Ensure keep_all doesn't change corrected copy human fields
        if self.corrected_rows:
            ci = self._get_corrected_index(entry_id)
            corrected_before = dict(self.corrected_rows[ci])
            corrected_after = dict(self.corrected_rows[ci])
            enforce_keep_all_does_not_change_human_fields(original_row=corrected_before, corrected_row=corrected_after)

        # Audit events for each changed audit field
        changed_fields = []
        for f in ("candidate_support", "audit_review_status"):
            if before.get(f, "") != after.get(f, ""):
                changed_fields.append(f)

        risk_flags = [f for f in (after.get("automated_risk_flags") or "").split("|") if f]
        for f in changed_fields:
            record_audit_event(
                audit_log_jsonl=self.paths.audit_log_jsonl,
                entry_row_before=before,
                entry_row_after=after,
                field=f,
                action="human_reviewed_keep",
                session_id=session_id,
                reviewer=reviewer,
                candidate_support=candidate_support,
                risk_flags=risk_flags,
                audit_reason=audit_reason,
                source_field="",
                source_excerpt="",
                provenance="human_keep_all",
            )

        if entry_id not in session["reviewed_entry_ids"]:
            session["reviewed_entry_ids"].append(entry_id)
        session["updated_at_utc"] = now_iso()
        self.save_session_state(session)
        self.save_all()

    def apply_defer(
        self,
        *,
        entry_id: str,
        reviewer: str,
        audit_reason: str = "defer",
    ) -> None:
        session = self.load_session_state()
        session_id = session.get("session_id") or uuid.uuid4().hex[:12]
        session.setdefault("reviewed_entry_ids", [])

        i = self._get_index(entry_id)
        before = dict(self.audit_rows[i])
        after = apply_defer_to_audit_row(audit_row=self.audit_rows[i])
        self.audit_rows[i] = after

        changed_fields = []
        for f in ("audit_review_status",):
            if before.get(f, "") != after.get(f, ""):
                changed_fields.append(f)

        risk_flags = [f for f in (after.get("automated_risk_flags") or "").split("|") if f]
        for f in changed_fields:
            record_audit_event(
                audit_log_jsonl=self.paths.audit_log_jsonl,
                entry_row_before=before,
                entry_row_after=after,
                field=f,
                action="deferred",
                session_id=session_id,
                reviewer=reviewer,
                candidate_support=after.get("candidate_support", ""),
                risk_flags=risk_flags,
                audit_reason=audit_reason,
                source_field="",
                source_excerpt="",
                provenance="human_defer",
            )

        if entry_id not in session["reviewed_entry_ids"]:
            session["reviewed_entry_ids"].append(entry_id)
        session["updated_at_utc"] = now_iso()
        self.save_session_state(session)
        self.save_all()

