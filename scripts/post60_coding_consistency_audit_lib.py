#!/usr/bin/env python3
"""
Post-60 coding-consistency audit library (Audit D — Phase 0).

Read-only screening against corrected_adjudication_copy.csv.
Does not modify the frozen source-integrity audit or original adjudication.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from post60_source_integrity_audit_lib import normalize_ws, read_csv_rows, sha256_file


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def load_hr_module(scripts_dir: Path):
    hr_path = scripts_dir / "run_jee_dq_human_review.py"
    spec = importlib.util.spec_from_file_location("_hr", hr_path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MAPPED_JEE_DECISIONS = {"accept_primary", "accept_primary_and_secondary", "replace"}
UNMAPPED_JEE_DECISIONS = {"no_mapping", "insufficient_evidence", "procedural_or_inquiry"}
MAPPED_DQ_DECISIONS = {"accept", "replace"}
UNMAPPED_DQ_DECISIONS = {"insufficient_evidence", "procedural_or_inquiry"}

JEE_AREA_KEYWORDS: dict[str, list[str]] = {
    "P1": ["legal", "regulatory", "legislation", "statute", "law", "regulation"],
    "P2": ["financ", "fund", "budget", "payment", "treasury", "resource"],
    "P3": ["coordination", "multisectoral", "focal point", "i hr", "cabinet office", "civil contingencies"],
    "D2": ["surveillance", "monitoring", "data system", "epidemiological"],
    "R1": ["emergency management", "emergency operation", "resilience", "civil contingencies", "taskforce"],
    "R4": ["infection prevention", "infection control", "ipc", "ppe", "stockpile"],
    "R5": ["public communication", "risk communication", "engage the public", "media", "messaging"],
}

GENERIC_VALUE_WORDS = {"important", "better", "good", "bad", "significant", "appropriate"}
GENERIC_INFO_PHRASES = [
    "advice was received",
    "received advice",
    "scientific advice",
    "the evidence",
    "a report",
    "modelling",
    "sage advised",
    "advice from",
]
INQUIRY_PROCEDURE_PHRASES = [
    "hearing",
    "schedule",
    "disclosure",
    "publication",
    "module",
    "inquiry report",
    "witness statement",
    "core participant",
    "rule 9",
]
POLICY_CONTENT_PHRASES = [
    "policy",
    "preparedness",
    "implementation",
    "restrict",
    "lockdown",
    "vaccin",
    "pandemic",
    "covid",
    "care home",
    "domestic abuse",
]

COMPARABLE_GROUPS: list[dict[str, Any]] = [
    {
        "group_id": "CG_INQUIRY_SCHEDULING_REPORTING",
        "group_name": "Inquiry scheduling and reporting records",
        "entry_ids": [
            "phase1-048", "phase1-082", "phase1-113", "phase1-114",
            "phase1-204", "phase1-207", "phase1-209", "phase1-217", "phase1-366",
        ],
        "compare_fields": ["human_JEE_decision", "human_DQ_decision", "human_candidate_statement_type", "human_policy_vs_inquiry"],
        "note": "Comparable Inquiry-administration passages; procedural_or_inquiry expected on at least one axis.",
    },
    {
        "group_id": "CG_RECOMMENDATION_UNSPECIFIED",
        "group_name": "Recommendations with unspecified content",
        "entry_ids": ["phase1-106", "phase1-124", "phase1-252", "phase1-321"],
        "compare_fields": ["human_candidate_statement_type", "human_DQ_decision", "human_primary_DQ"],
        "note": "Recommendation-type passages where the recommended action is vague or unspecified.",
    },
    {
        "group_id": "CG_IMPLEMENTATION_NO_SUBJECT",
        "group_name": "Implementation statements with no stated subject",
        "entry_ids": ["phase1-050", "phase1-111", "phase1-382", "phase1-405"],
        "compare_fields": ["human_candidate_statement_type", "human_DQ_decision", "human_primary_DQ", "human_JEE_decision"],
        "note": "Implementation or operational statements where the implemented measure is thinly specified.",
    },
    {
        "group_id": "CG_DOMESTIC_ABUSE_POLICY",
        "group_name": "Domestic-abuse policy recommendations",
        "entry_ids": ["phase1-142", "phase1-285"],
        "compare_fields": ["human_JEE_decision", "human_DQ_decision", "human_candidate_statement_type", "human_policy_vs_inquiry"],
        "note": "Comparable domestic-abuse policy content.",
    },
    {
        "group_id": "CG_CARE_HOME_STAFF_MOVEMENT",
        "group_name": "Care-home staff-movement restrictions",
        "entry_ids": ["phase1-079", "phase1-182"],
        "compare_fields": ["human_JEE_decision", "human_primary_JEE", "human_DQ_decision", "human_primary_DQ"],
        "note": "Comparable care-home staffing restriction passages.",
    },
    {
        "group_id": "CG_POLICING_FOUR_ES",
        "group_name": "Policing and four-Es records",
        "entry_ids": ["phase1-117", "phase1-310", "phase1-311", "phase1-312"],
        "compare_fields": ["human_JEE_decision", "human_primary_JEE", "human_DQ_decision", "human_candidate_statement_type"],
        "note": "Policing enforcement / four-Es framing records.",
    },
    {
        "group_id": "CG_NATIONAL_COORDINATION",
        "group_name": "National coordination or governance structures",
        "entry_ids": ["phase1-003", "phase1-246", "phase1-382", "phase1-405"],
        "compare_fields": ["human_JEE_decision", "human_primary_JEE", "human_secondary_JEE", "human_DQ_decision"],
        "note": "National coordination, governance or Situation Centre/Taskforce records.",
    },
    {
        "group_id": "CG_RETROSPECTIVE_PREPAREDNESS",
        "group_name": "Retrospective pandemic-preparedness judgements",
        "entry_ids": ["phase1-018", "phase1-106", "phase1-217", "phase1-314"],
        "compare_fields": ["human_candidate_statement_type", "human_JEE_decision", "human_DQ_decision", "human_policy_vs_inquiry"],
        "note": "Retrospective judgements about preparedness or lessons learned.",
    },
    {
        "group_id": "CG_ADVICE_WITHOUT_CONTENT",
        "group_name": "Statements mentioning advice without exposing its content",
        "entry_ids": ["phase1-117", "phase1-161", "phase1-311"],
        "compare_fields": ["human_primary_DQ", "human_DQ_decision", "human_candidate_statement_type"],
        "note": "Advice/report referenced but substantive content not presented in excerpt.",
    },
    {
        "group_id": "CG_QUESTION_SOURCE_QUOTES",
        "group_name": "Question-only or question-like Source Quotes",
        "entry_ids": ["phase1-007", "phase1-090", "phase1-117", "phase1-161", "phase1-274", "phase1-314", "phase1-382", "phase1-396"],
        "compare_fields": ["human_JEE_decision", "human_DQ_decision", "human_JEE_confidence", "human_DQ_confidence"],
        "note": "Traceability-failed or question-like quotes requiring cautious coding.",
    },
    {
        "group_id": "CG_JEE_NO_MAPPING_VS_INSUFFICIENT",
        "group_name": "no_mapping versus insufficient_evidence JEE cases",
        "entry_ids": [],  # filled dynamically
        "compare_fields": ["human_JEE_decision", "human_JEE_rationale", "human_JEE_confidence"],
        "note": "Thin or vague passages where JEE unmapped-status choice may differ by source wording.",
    },
]


@dataclass
class ConsistencyFlag:
    flag: str
    reason: str


@dataclass
class ScreeningResult:
    entry_id: str
    flags: list[ConsistencyFlag] = field(default_factory=list)
    comparable_groups: list[str] = field(default_factory=list)
    review_priority: str = "standard"
    consistency_review_status: str = "consistency_auto_clear"
    validate_errors: list[str] = field(default_factory=list)


def _text_blob(row: dict[str, str]) -> str:
    parts = [
        row.get("decision", ""),
        row.get("evidence", ""),
        row.get("source_quote", ""),
        row.get("human_JEE_evidence", ""),
        row.get("human_DQ_evidence", ""),
        row.get("human_JEE_rationale", ""),
        row.get("human_DQ_rationale", ""),
        row.get("human_overall_rationale", ""),
    ]
    return normalize_ws(" ".join(parts))


def _has_phrase(blob: str, phrases: list[str]) -> bool:
    return any(p in blob for p in phrases)


def _keyword_hits(blob: str, keywords: list[str]) -> list[str]:
    return [k for k in keywords if k in blob]


def _quote_is_question(row: dict[str, str]) -> bool:
    sq = (row.get("source_quote") or "").strip()
    return bool(sq) and "?" in sq


def _traceability_false(row: dict[str, str]) -> bool:
    return str(row.get("traceability_ok", "")).strip().lower() not in ("true", "1", "yes")


def screen_record(
    row: dict[str, str],
    *,
    jee_areas: set[str],
    dq_elements: set[str],
    hr_mod,
    all_rows_by_id: dict[str, dict[str, str]],
    group_membership: dict[str, list[str]],
    by_group: dict[str, list[str]],
) -> ScreeningResult:
    eid = row["entry_id"]
    result = ScreeningResult(entry_id=eid)
    blob = _text_blob(row)

    jd = (row.get("human_JEE_decision") or "").strip()
    jp = (row.get("human_primary_JEE") or "").strip()
    js = (row.get("human_secondary_JEE") or "").strip()
    dd = (row.get("human_DQ_decision") or "").strip()
    dp = (row.get("human_primary_DQ") or "").strip()
    ds = (row.get("human_secondary_DQ") or "").strip()
    st = (row.get("human_candidate_statement_type") or "").strip()
    pv = (row.get("human_policy_vs_inquiry") or "").strip()
    jconf = (row.get("human_JEE_confidence") or "").strip()
    dconf = (row.get("human_DQ_confidence") or "").strip()
    jee_ev = (row.get("human_JEE_evidence") or "").strip()
    dq_ev = (row.get("human_DQ_evidence") or "").strip()

    def add(flag: str, reason: str) -> None:
        result.flags.append(ConsistencyFlag(flag=flag, reason=reason))

    # Schema validation via existing helper
    val_errs = hr_mod.validate_row(row, jee_areas, dq_elements, require_complete=True)
    result.validate_errors = val_errs
    for msg in val_errs:
        if "must not carry" in msg or "requires" in msg or "must not be identical" in msg:
            if "primary" in msg and "secondary" in msg and "identical" in msg:
                add("primary_secondary_duplicate", msg)
            elif "secondary" in msg:
                add("invalid_secondary_mapping", msg)
            elif "requires" in msg and "primary" in msg:
                add("mapped_status_without_primary", msg)
            elif "must not carry" in msg:
                add("unmapped_status_with_primary", msg)
        else:
            add("other", msg)

    # no_mapping vs insufficient_evidence tension
    if jd in ("no_mapping", "insufficient_evidence"):
        thin_markers = ["thin", "vague", "incomplete", "unspecified", "does not identify", "too brief", "not enough"]
        clear_markers = ["does not support", "no specific", "not map", "sufficiently clear", "clearly"]
        rat = normalize_ws((row.get("human_JEE_rationale") or "") + " " + (row.get("human_overall_rationale") or ""))
        has_thin = any(m in rat for m in thin_markers)
        has_clear = any(m in rat for m in clear_markers)
        if jd == "no_mapping" and has_thin and not has_clear:
            add(
                "no_mapping_vs_insufficient_conflict",
                "JEE status is no_mapping but rationale language suggests insufficient_evidence (thin/vague source).",
            )
        if jd == "insufficient_evidence" and has_clear and not has_thin:
            add(
                "no_mapping_vs_insufficient_conflict",
                "JEE status is insufficient_evidence but rationale language suggests passage clarity sufficient for no_mapping.",
            )

    # JEE over/under mapping heuristics
    if jd in MAPPED_JEE_DECISIONS and jp:
        area_keywords = JEE_AREA_KEYWORDS.get(jp, [])
        if area_keywords:
            hits = _keyword_hits(blob, area_keywords)
            if len(hits) < 1:
                add(
                    "possible_JEE_overmapping",
                    f"JEE primary {jp} mapped but passage lacks area-specific capacity cues ({', '.join(area_keywords[:4])}...).",
                )
        if jp == "P2" and any(w in blob for w in ["payment", "paid", "fund"]) and "preparedness" not in blob and "response capacity" not in blob:
            add("generic_keyword_JEE_mapping", "P2 mapped on generic funding/payment reference without preparedness financing capacity.")
        if jp == "P3" and "coordination" not in blob and "cabinet office" not in blob and "civil contingencies" not in blob and "focal point" not in blob:
            add("generic_keyword_JEE_mapping", "P3 mapped without identifiable multisectoral/national coordination mechanism language.")
        if jp == "D2" and "surveillance" not in blob and "monitoring" not in blob and "data system" not in blob:
            add("generic_keyword_JEE_mapping", "D2 mapped without surveillance/monitoring capacity language.")
        if jp == "R5" and "public" not in blob and "communication" not in blob and "media" not in blob:
            add("generic_keyword_JEE_mapping", "R5 mapped without public/risk-communication capacity language.")
        if jp == "R1" and "emergency" not in blob and "taskforce" not in blob and "resilience" not in blob:
            add("generic_keyword_JEE_mapping", "R1 mapped without emergency-management operation/capacity language.")

    machine_jee = (row.get("JEE_mapping_status") or "").strip()
    if jd in UNMAPPED_JEE_DECISIONS and machine_jee in ("mapped_substantive", "ambiguous_substantive"):
        if (row.get("proposed_primary_JEE_area") or "").strip():
            add(
                "possible_JEE_undermapping",
                f"Human JEE unmapped ({jd}) but machine proposal suggested substantive mapping ({row.get('proposed_primary_JEE_area')}).",
            )

    # Secondary JEE evidence independence
    if js and jd == "accept_primary_and_secondary":
        if jee_ev and not js:
            pass
        elif not jee_ev:
            add("invalid_secondary_mapping", "Secondary JEE present but no JEE evidence excerpt recorded to support independent second capacity.")
    elif js and jd == "replace":
        add("invalid_secondary_mapping", "Secondary JEE present under replace decision; expected only under accept_primary_and_secondary.")

    if jp and js and jp == js:
        add("primary_secondary_duplicate", "JEE primary and secondary are identical.")

    if dp and ds and dp == ds:
        add("primary_secondary_duplicate", "DQ primary and secondary are identical.")

    # DQ false positives
    if dp == "useful_information":
        if _has_phrase(blob, GENERIC_INFO_PHRASES) and not any(
            w in blob for w in ["data show", "analysis", "model", "figure", "rate", "number", "percent", "evidence that"]
        ):
            add("generic_information_reference", "useful_information coded but passage only references advice/report existence without presenting content.")
            add("possible_DQ_false_positive", "Possible useful_information false positive: advice/report mentioned without observable information content.")

    if dp == "clear_values":
        tokens = set(re.findall(r"[a-z']+", blob))
        if tokens & GENERIC_VALUE_WORDS and not any(w in blob for w in ["priority", "trade-off", "objective", "balance", "value"]):
            add("generic_value_reference", "clear_values coded but only generic evaluative words (e.g. important/better) appear without identifiable objective or trade-off.")

    if dp == "commitment_to_follow_through":
        weak = ["should", "recommend", "propose", "ought", "need to", "must consider"]
        strong = ["authorised", "authorized", "implemented", "ordered", "agreed to", "will reopen", "was to", "timetable", "completed"]
        if any(w in blob for w in weak) and not any(w in blob for w in strong):
            if st in ("recommendation", "proposed_decision"):
                add("recommendation_as_commitment", "commitment_to_follow_through coded but statement type and wording suggest recommendation/proposal only.")
        if st == "recommendation" and dp == "commitment_to_follow_through":
            add("recommendation_as_commitment", "DQ commitment_to_follow_through conflicts with recommendation statement type.")

    if dp == "helpful_frame":
        if not any(w in blob for w in ["scope", "objective", "frame", "boundary", "dimension", "remit", "criteria"]):
            add("possible_DQ_false_positive", "helpful_frame coded without clear decision-scope or objective framing language.")

    # DQ false negative heuristic
    if dd in UNMAPPED_DQ_DECISIONS and (row.get("DQ_mapping_status") or "").strip() == "observable":
        prop = (row.get("proposed_primary_DQ_element") or "").strip()
        if prop:
            add("possible_DQ_false_negative", f"Human DQ unmapped ({dd}) but machine observable indicator suggested {prop}.")

    # Statement type conflicts
    if st == "implementation_statement" and any(w in blob for w in ["propose", "recommended", "should"]):
        if not any(w in blob for w in ["implemented", "authorised", "authorized", "carried out", "was to", "ordered"]):
            add("proposal_as_implementation", "implementation_statement coded but wording suggests proposal/recommendation.")
    if st == "enacted_or_authorised_decision" and any(w in blob for w in ["propose", "recommended", "should"]) and "authorised" not in blob and "authorized" not in blob and "ordered" not in blob:
        add("implementation_as_authorised_decision", "enacted_or_authorised_decision coded but passage may be proposal/recommendation language.")
    if st == "recommendation" and "retrospective" in blob:
        add("retrospective_as_recommendation", "recommendation statement type on retrospective judgement passage.")
    if st == "retrospective_judgement" and any(w in blob for w in ["recommend", "should", "propose"]):
        add("retrospective_as_recommendation", "retrospective_judgement statement type but recommendation language present (may be justified if dual content).")

    # Policy vs inquiry
    has_inquiry = _has_phrase(blob, INQUIRY_PROCEDURE_PHRASES)
    has_policy = _has_phrase(blob, POLICY_CONTENT_PHRASES)
    if pv == "inquiry_procedure" and has_policy and not has_inquiry:
        add("inquiry_policy_misclassification", "Coded inquiry_procedure but passage contains substantive policy content markers.")
    if pv == "policy_content" and has_inquiry and not has_policy and jd == "procedural_or_inquiry":
        add("inquiry_policy_misclassification", "Coded policy_content but passage appears Inquiry-administration focused.")
    if pv == "mixed" and not (has_inquiry and has_policy):
        add("mixed_without_dual_content", "mixed policy/inquiry coded without both inquiry-procedure and policy-content markers in passage text.")

    # Evidence / status conflicts
    if jd in UNMAPPED_JEE_DECISIONS and jee_ev:
        add("evidence_status_conflict", f"JEE decision {jd} carries a non-empty JEE evidence excerpt.")
    if jd in MAPPED_JEE_DECISIONS and not jee_ev:
        add("evidence_status_conflict", f"JEE decision {jd} mapped but JEE evidence excerpt is blank.")
    if dd in UNMAPPED_DQ_DECISIONS and dq_ev:
        add("evidence_status_conflict", f"DQ decision {dd} carries a non-empty DQ evidence excerpt.")
    if dd in MAPPED_DQ_DECISIONS and not dq_ev:
        add("evidence_status_conflict", f"DQ decision {dd} mapped but DQ evidence excerpt is blank.")

    # Rationale vs label
    if jd == "procedural_or_inquiry" and "policy" in rat if (rat := normalize_ws(row.get("human_JEE_rationale", ""))) else False:
        add("rationale_label_conflict", "JEE procedural_or_inquiry but JEE rationale references policy mapping.")
    if dd == "procedural_or_inquiry" and st == "enacted_or_authorised_decision":
        add("rationale_label_conflict", "DQ procedural_or_inquiry conflicts with enacted_or_authorised_decision statement type.")

    # Confidence conflicts
    if jconf == "high" and jd == "insufficient_evidence":
        add("confidence_support_conflict", "JEE confidence high despite insufficient_evidence status.")
    if dconf == "high" and dd == "insufficient_evidence":
        add("confidence_support_conflict", "DQ confidence high despite insufficient_evidence status.")
    if jconf == "low" and jd in MAPPED_JEE_DECISIONS and jee_ev:
        add("confidence_support_conflict", "JEE confidence low despite substantive mapped coding with evidence excerpt.")
    if _traceability_false(row) and jconf == "high" and jd in MAPPED_JEE_DECISIONS:
        add("confidence_support_conflict", "JEE confidence high on traceability-failed source with substantive mapping.")

    # Comparable group membership
    result.comparable_groups = group_membership.get(eid, [])

    # Cross-record inconsistency within groups
    for gid in result.comparable_groups:
        peers = [all_rows_by_id[x] for x in by_group.get(gid, []) if x != eid and x in all_rows_by_id]
        if not peers:
            continue
        group_def = next((g for g in COMPARABLE_GROUPS if g["group_id"] == gid), None)
        if not group_def:
            continue
        compare_fields = group_def.get("compare_fields", [])
        diffs = []
        for cf in compare_fields:
            vals = {(row.get(cf) or "").strip()} | {(p.get(cf) or "").strip() for p in peers}
            vals.discard("")
            if len(vals) > 1:
                peer_summary = ", ".join(f"{p['entry_id']}={p.get(cf,'')}" for p in peers[:4])
                diffs.append(f"{cf}: this={row.get(cf,'')!r}; peers include {peer_summary}")
        if diffs:
            add(
                "duplicate_or_comparable_record_inconsistency",
                f"Group {gid}: " + "; ".join(diffs[:3]),
            )

    # Priority
    critical_flags = {
        "mapped_status_without_primary",
        "unmapped_status_with_primary",
        "invalid_secondary_mapping",
        "primary_secondary_duplicate",
        "evidence_status_conflict",
        "duplicate_or_comparable_record_inconsistency",
    }
    if result.validate_errors or any(f.flag in critical_flags for f in result.flags):
        result.review_priority = "critical"
    elif len(result.flags) >= 2:
        result.review_priority = "critical"
    else:
        result.review_priority = "standard"

    if result.flags:
        result.consistency_review_status = "consistency_flagged_pending_human"
    else:
        result.consistency_review_status = "consistency_auto_clear"

    return result


def build_group_membership(rows: list[dict[str, str]]) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    by_id = {r["entry_id"]: r for r in rows}
    membership: dict[str, list[str]] = defaultdict(list)
    by_group: dict[str, list[str]] = {}

    groups = [dict(g) for g in COMPARABLE_GROUPS]
    # Dynamic JEE no_mapping vs insufficient group
    dynamic_ids = sorted(
        eid for eid, r in by_id.items()
        if (r.get("human_JEE_decision") or "").strip() in ("no_mapping", "insufficient_evidence")
    )
    for g in groups:
        if g["group_id"] == "CG_JEE_NO_MAPPING_VS_INSUFFICIENT":
            g["entry_ids"] = dynamic_ids

    for g in groups:
        gid = g["group_id"]
        ids = [eid for eid in g.get("entry_ids", []) if eid in by_id]
        by_group[gid] = ids
        for eid in ids:
            membership[eid].append(gid)

    return membership, by_group


def screening_row_to_csv(
    row: dict[str, str],
    screening: ScreeningResult,
    candidate_support: str,
) -> dict[str, str]:
    flags = "|".join(f.flag for f in screening.flags)
    reasons = "|".join(f"{f.flag}:{f.reason}" for f in screening.flags)
    return {
        "entry_id": row["entry_id"],
        "current_JEE_status": row.get("human_JEE_decision", ""),
        "current_JEE_primary": row.get("human_primary_JEE", ""),
        "current_JEE_secondary": row.get("human_secondary_JEE", ""),
        "current_JEE_confidence": row.get("human_JEE_confidence", ""),
        "current_DQ_status": row.get("human_DQ_decision", ""),
        "current_DQ_primary": row.get("human_primary_DQ", ""),
        "current_DQ_secondary": row.get("human_secondary_DQ", ""),
        "current_DQ_confidence": row.get("human_DQ_confidence", ""),
        "current_policy_or_inquiry": row.get("human_policy_vs_inquiry", ""),
        "current_statement_type": row.get("human_candidate_statement_type", ""),
        "current_overall_rationale": row.get("human_overall_rationale", ""),
        "consistency_flags": flags,
        "flag_reasons": reasons,
        "comparable_group": "|".join(screening.comparable_groups),
        "review_priority": screening.review_priority,
        "consistency_review_status": screening.consistency_review_status,
        "candidate_support": candidate_support,
        "validate_errors": "|".join(screening.validate_errors),
    }


def comparable_groups_rows(
    rows_by_id: dict[str, dict[str, str]],
    by_group: dict[str, list[str]],
) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for g in COMPARABLE_GROUPS:
        gid = g["group_id"]
        ids = by_group.get(gid, [])
        if not ids:
            continue
        label_parts = []
        for eid in ids:
            r = rows_by_id[eid]
            label_parts.append(
                f"{eid}[JEE={r.get('human_JEE_decision','')}/{r.get('human_primary_JEE','')};"
                f"DQ={r.get('human_DQ_decision','')}/{r.get('human_primary_DQ','')};"
                f"ST={r.get('human_candidate_statement_type','')};PI={r.get('human_policy_vs_inquiry','')}]"
            )
        compare_fields = g.get("compare_fields", [])
        inconsistencies = []
        for cf in compare_fields:
            vals = {(rows_by_id[eid].get(cf) or "").strip() for eid in ids}
            vals.discard("")
            if len(vals) > 1:
                inconsistencies.append(f"{cf} varies across group: {sorted(vals)}")
        out.append({
            "group_id": gid,
            "group_name": g["group_name"],
            "entry_ids": "|".join(ids),
            "n_entries": str(len(ids)),
            "current_labels": " || ".join(label_parts),
            "apparent_inconsistency": "; ".join(inconsistencies) if inconsistencies else "none detected by field comparison",
            "justification_note": g.get("note", ""),
        })
    return out


def atomic_write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    tmp.replace(path)


def write_discovery_report(
    path: Path,
    *,
    source_integrity_dir: Path,
    work_dir: Path,
    n_records: int,
    auto_clear: int,
    flagged: int,
    flag_counts: Counter,
    n_groups: int,
    frozen_ok: bool,
    protected_ok: bool,
) -> None:
    lines = [
        "# POST-60 Coding-Consistency Audit — Discovery Report (Audit D Phase 0)",
        "",
        f"- Generated (UTC): {now_iso()}",
        f"- Audit D work directory: `{work_dir.as_posix()}`",
        f"- Source-integrity audit (frozen, read-only): `{source_integrity_dir.as_posix()}`",
        f"- Input reference copy: `corrected_adjudication_copy.csv`",
        f"- Methodology: AI-assisted human reference set (not independent gold standard)",
        "",
        "## Phase 0 confirmation",
        "",
        f"- All {n_records} corrected records present: **yes**",
        f"- Source-integrity audit frozen (no pending/deferred): **{frozen_ok}**",
        f"- Original adjudication directory protected: **{protected_ok}**",
        f"- Audit E metrics produced: **no**",
        f"- Human labels modified: **no**",
        "",
        "## Screening summary",
        "",
        f"- Auto-cleared: {auto_clear}",
        f"- Flagged for human consistency review: {flagged}",
        f"- Comparable groups defined: {n_groups}",
        "",
        "## Flag counts (automated review aids)",
        "",
    ]
    for fl, cnt in flag_counts.most_common():
        lines.append(f"- {fl}: {cnt}")
    lines += [
        "",
        "## Scope",
        "",
        "Audit D tests internal coding consistency after source-integrity corrections.",
        "Automated flags are review aids only; no label was changed automatically.",
        "",
        "## Next step",
        "",
        "Human consistency review via structured batch files in `review_packets/`.",
        "Do not begin Audit E or automated-versus-human performance metrics.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


RESPONSE_TEMPLATE_FIELDS = [
    "entry_id",
    "review_priority",
    "comparable_group",
    "selected_consistency_action",
    "corrected_JEE_status",
    "corrected_JEE_primary",
    "corrected_JEE_secondary",
    "corrected_JEE_confidence",
    "corrected_JEE_evidence_excerpt",
    "corrected_JEE_rationale",
    "corrected_DQ_status",
    "corrected_DQ_primary",
    "corrected_DQ_secondary",
    "corrected_DQ_confidence",
    "corrected_DQ_evidence_excerpt",
    "corrected_DQ_rationale",
    "corrected_policy_or_inquiry",
    "corrected_statement_type",
    "corrected_overall_rationale",
    "consistency_reason",
    "reviewer_notes",
]
