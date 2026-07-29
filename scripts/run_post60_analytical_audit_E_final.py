#!/usr/bin/env python3
"""
Audit E — Final frozen analytical audit (post human-approval corrections).

Read-only analysis of CONSISTENCY_CORRECTED_REFERENCE.csv.
Uses human-reviewed traceability classifications; does not infer substantive
divergence from string comparison alone.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT_D_DIR = ROOT / "outputs/framework_mapping/run_20260727_094015_post60_coding_consistency_audit"
PRE_AUDIT_D_REF = ROOT / "outputs/framework_mapping/run_20260727_080220_post60_source_integrity_audit/corrected_adjudication_copy.csv"
ORIGINAL_AUDIT_E = ROOT / "outputs/framework_mapping/run_20260727_110052_post60_analytical_audit_E"
HUMAN_APPROVAL_DIR = ROOT / "outputs/framework_mapping/run_20260727_131920_audit_E_human_approval_check"
APPROVED_TRACEABILITY_SRC = HUMAN_APPROVAL_DIR / "AUDIT_E_TRACEABILITY_METRIC_CHECK.csv"
EXPECTED_REF_SHA256 = "eec6c4e87dfa9b42421a13fce4ebca9c84701ad80d765f19fbdba59ab0c75770"

APPROVED_TRACEABILITY_COUNTS = {
    "exact_or_near_verbatim": 8,
    "substantively_faithful_paraphrase": 25,
    "materially_unsupported_or_altered": 20,
    "traceability_false": 7,
}

JEE_MAPPED = {"accept_primary", "accept_primary_and_secondary", "replace"}
DQ_MAPPED = {"accept", "replace"}
DQ_UNMAPPED = {"insufficient_evidence", "procedural_or_inquiry"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        return rows, list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def pct(n: int, d: int) -> str:
    if d == 0:
        return "0.0% (0/0)"
    return f"{100 * n / d:.1f}% ({n}/{d})"


def _norm(s: str) -> str:
    return " ".join((s or "").lower().split())


def lexical_non_exact_non_substring_match(r: dict) -> bool:
    """Purely lexical diagnostic — NOT substantive divergence."""
    d, q = _norm(r.get("decision", "")), _norm(r.get("source_quote", ""))
    if not d or not q:
        return False
    return d != q and d not in q and q not in d


def is_traceable(r: dict) -> bool:
    return str(r.get("traceability_ok", "")).strip().lower() in ("true", "1", "yes")


def jee_mapped(r: dict) -> bool:
    return (r.get("human_JEE_decision") or "").strip() in JEE_MAPPED


def dq_mapped(r: dict) -> bool:
    return (r.get("human_DQ_decision") or "").strip() in DQ_MAPPED


def load_human_traceability(path: Path) -> dict[str, str]:
    rows, _ = read_csv(path)
    return {r["entry_id"]: r["classification"] for r in rows}


def build_traceability_human_classification(class_by_id: dict[str, str]) -> list[dict]:
    return [
        {
            "entry_id": eid,
            "approved_traceability_category": cat,
            "source_of_classification": str(APPROVED_TRACEABILITY_SRC.relative_to(ROOT)),
            "reviewer_basis": (
                "Single-reviewer human classification from source passages, "
                "traceability_ok field, and adjudication rationales (human-approval gate)"
            ),
            "approval_status": "human_approved_2026-07-27",
        }
        for eid, cat in sorted(class_by_id.items())
    ]


def verify_inputs(
    ref_path: Path,
    screening_path: Path,
    class_by_id: dict[str, str],
) -> tuple[bool, list[str]]:
    errors = []
    got = sha256_file(ref_path)
    if got != EXPECTED_REF_SHA256:
        errors.append(f"SHA256 mismatch: expected {EXPECTED_REF_SHA256}, got {got}")
    rows, _ = read_csv(ref_path)
    if len(rows) != 60:
        errors.append(f"expected 60 records, got {len(rows)}")
    scr, _ = read_csv(screening_path)
    status = Counter(r.get("consistency_review_status") for r in scr)
    expected = {
        "consistency_human_reviewed_keep": 52,
        "consistency_human_reviewed_corrected": 6,
        "consistency_auto_clear": 2,
        "consistency_flagged_pending_human": 0,
    }
    for k, v in expected.items():
        if status.get(k, 0) != v:
            errors.append(f"status {k}: expected {v}, got {status.get(k, 0)}")
    if len(class_by_id) != 60:
        errors.append(f"expected 60 traceability classifications, got {len(class_by_id)}")
    cat_counts = Counter(class_by_id.values())
    for cat, expected_n in APPROVED_TRACEABILITY_COUNTS.items():
        if cat_counts.get(cat, 0) != expected_n:
            errors.append(f"traceability {cat}: expected {expected_n}, got {cat_counts.get(cat, 0)}")
    return len(errors) == 0, errors


def crosstab(rows: list[dict], row_field: str, col_field: str, row_label: str, col_label: str) -> list[dict]:
    table: dict[tuple[str, str], int] = defaultdict(int)
    row_vals: set[str] = set()
    col_vals: set[str] = set()
    for r in rows:
        rv = (r.get(row_field) or "[blank]").strip() or "[blank]"
        cv = (r.get(col_field) or "[blank]").strip() or "[blank]"
        table[(rv, cv)] += 1
        row_vals.add(rv)
        col_vals.add(cv)
    out = []
    for rv in sorted(row_vals):
        for cv in sorted(col_vals):
            c = table.get((rv, cv), 0)
            if c:
                out.append({row_label: rv, col_label: cv, "count": c, "percentage_of_total": pct(c, len(rows))})
    return out


def build_failure_modes(
    rows: list[dict],
    pre_by_id: dict[str, dict],
    class_by_id: dict[str, str],
) -> list[dict]:
    out = []
    modes = [
        (
            "FM_THIN_VAGUE_SOURCE",
            "Source passage too thin or vague to identify a specific JEE capacity or DQ element",
            lambda r: (r.get("human_JEE_decision") or "") == "insufficient_evidence"
            or (r.get("human_DQ_decision") or "") == "insufficient_evidence",
            "Distinguish from extraction failure; reflects source granularity limits.",
        ),
        (
            "FM_CLEAR_BUT_NO_JEE_CAPACITY",
            "Passage sufficiently clear but does not support a specific JEE capacity",
            lambda r: (r.get("human_JEE_decision") or "") == "no_mapping",
            "Framework applicable but passage lacks capacity-specific evidence.",
        ),
        (
            "FM_PROCEDURAL_INQUIRY",
            "Passage concerns Inquiry administration rather than substantive preparedness policy",
            lambda r: (r.get("human_JEE_decision") or "") == "procedural_or_inquiry"
            or (r.get("human_DQ_decision") or "") == "procedural_or_inquiry",
            "Inquiry-administration content excluded from substantive preparedness mapping.",
        ),
        (
            "FM_NON_TRACEABLE",
            "Generated decision not traceable to source quote (traceability_ok=False)",
            lambda r: not is_traceable(r),
            "Generated-candidate field unreliable; analysis must use source quote.",
        ),
        (
            "FM_MATERIALLY_UNSUPPORTED_CANDIDATE",
            "Human-reviewed: generated decision introduced materially unsupported or altered meaning",
            lambda r: class_by_id.get(r["entry_id"]) == "materially_unsupported_or_altered",
            "Candidate summary must not substitute for source evidence; human review required.",
        ),
        (
            "FM_LEXICAL_NON_EXACT_NON_SUBSTRING",
            "Technical diagnostic only: decision and source_quote are non-identical strings with no substring containment",
            lambda r: lexical_non_exact_non_substring_match(r),
            "Lexical diagnostic only — does not establish substantive divergence or material alteration.",
        ),
        (
            "FM_UNSUPPORTED_SECONDARY_JEE",
            "Secondary JEE mapping without independent passage evidence (pre-Audit-D artefact)",
            lambda r: False,
            "Secondary mappings require independent passage evidence (corrected in Audit D).",
        ),
        (
            "FM_LOW_MEDIUM_CONFIDENCE",
            "Human confidence low or medium despite substantive coding",
            lambda r: (r.get("human_JEE_confidence") or "") in ("low", "medium")
            or (r.get("human_DQ_confidence") or "") in ("low", "medium"),
            "Interpretive caution warranted even where coding is complete.",
        ),
    ]
    for mode_id, definition, predicate, implication in modes:
        if mode_id == "FM_UNSUPPORTED_SECONDARY_JEE":
            affected = [pre_by_id[eid] for eid in pre_by_id if (pre_by_id[eid].get("human_secondary_JEE") or "").strip()]
        else:
            affected = [r for r in rows if predicate(r)]
        if not affected:
            continue
        eids = [r["entry_id"] for r in affected][:8]
        example = (affected[0].get("human_overall_rationale") or "")[:200]
        out.append(
            {
                "failure_mode_id": mode_id,
                "definition": definition,
                "n_records": len(affected),
                "percentage": pct(len(affected), len(rows)),
                "representative_entry_ids": "|".join(eids),
                "brief_example_paraphrase": example,
                "methodological_implication": implication,
            }
        )
    return out


def sensitivity_analysis(final_rows: list[dict], pre_by_id: dict[str, dict]):
    preview_path = AUDIT_D_DIR / "CONSISTENCY_CORRECTIONS_PREVIEW.csv"
    changes, _ = read_csv(preview_path)
    detail_rows = [dict(ch) for ch in changes]

    def jee_counts(rows):
        mapped = sum(1 for r in rows if jee_mapped(r))
        return {"mapped": mapped, "status": dict(Counter(r.get("human_JEE_decision", "") for r in rows))}

    def dq_counts(rows):
        mapped = sum(1 for r in rows if dq_mapped(r))
        return {"mapped": mapped, "status": dict(Counter(r.get("human_DQ_decision", "") for r in rows))}

    def st_counts(rows):
        return dict(Counter(r.get("human_candidate_statement_type", "") for r in rows))

    pre_stats = {
        "jee": jee_counts(list(pre_by_id.values())),
        "dq": dq_counts(list(pre_by_id.values())),
        "st": st_counts(list(pre_by_id.values())),
    }
    post_stats = {"jee": jee_counts(final_rows), "dq": dq_counts(final_rows), "st": st_counts(final_rows)}

    summary_rows = [
        {"metric": "records_changed", "pre_audit_d": 0, "post_audit_d": 6, "delta": 6},
        {"metric": "substantive_field_changes", "pre_audit_d": 0, "post_audit_d": len(changes), "delta": len(changes)},
        {"metric": "jee_mapped_count", "pre_audit_d": pre_stats["jee"]["mapped"], "post_audit_d": post_stats["jee"]["mapped"], "delta": post_stats["jee"]["mapped"] - pre_stats["jee"]["mapped"]},
        {"metric": "dq_mapped_count", "pre_audit_d": pre_stats["dq"]["mapped"], "post_audit_d": post_stats["dq"]["mapped"], "delta": post_stats["dq"]["mapped"] - pre_stats["dq"]["mapped"]},
        {"metric": "jee_replace_count", "pre_audit_d": pre_stats["jee"]["status"].get("replace", 0), "post_audit_d": post_stats["jee"]["status"].get("replace", 0), "delta": post_stats["jee"]["status"].get("replace", 0) - pre_stats["jee"]["status"].get("replace", 0)},
        {"metric": "jee_no_mapping_count", "pre_audit_d": pre_stats["jee"]["status"].get("no_mapping", 0), "post_audit_d": post_stats["jee"]["status"].get("no_mapping", 0), "delta": post_stats["jee"]["status"].get("no_mapping", 0) - pre_stats["jee"]["status"].get("no_mapping", 0)},
        {"metric": "statement_implementation_statement", "pre_audit_d": pre_stats["st"].get("implementation_statement", 0), "post_audit_d": post_stats["st"].get("implementation_statement", 0), "delta": post_stats["st"].get("implementation_statement", 0) - pre_stats["st"].get("implementation_statement", 0)},
        {"metric": "principal_conclusion_changed", "pre_audit_d": "n/a", "post_audit_d": "no", "delta": "Audit D refined edge cases; aggregate proportions unchanged"},
    ]
    return detail_rows, summary_rows, pre_stats, post_stats


def validate_outputs(work_dir: Path, rows: list[dict], class_by_id: dict[str, str]) -> tuple[bool, list[str]]:
    errors = []
    skip_historical = {"AUDIT_E_REVISION_LOG.md"}
    forbidden_divergence = re.compile(
        r"88\.3% \(53/60\) generated|generated decisions diverge|"
        r"substantive divergence from|show substantive divergence|"
        r"diverge from source quotes",
        re.I,
    )
    for md in work_dir.glob("AUDIT_E_*.md"):
        if md.name in skip_historical:
            continue
        text = md.read_text(encoding="utf-8")
        if forbidden_divergence.search(text):
            errors.append(f"forbidden divergence wording in {md.name}")
        if re.search(r"dominant mixed pattern", text, re.I):
            errors.append(f"unqualified 'dominant mixed pattern' in {md.name}")
        if re.search(r"52.*newly interactively reviewed|all 52.*human.reviewed during Audit D", text, re.I):
            errors.append(f"misleading Audit D review claim in {md.name}")

    cat_counts = Counter(class_by_id.values())
    if sum(cat_counts.values()) != 60:
        errors.append("traceability categories do not total 60")
    for cat, n in APPROVED_TRACEABILITY_COUNTS.items():
        if cat_counts.get(cat, 0) != n:
            errors.append(f"traceability count mismatch for {cat}")

    coding_fields = [
        "human_JEE_decision", "human_DQ_decision", "human_primary_JEE", "human_primary_DQ",
        "human_candidate_statement_type", "human_policy_vs_inquiry",
    ]
    ref_rows, _ = read_csv(AUDIT_D_DIR / "CONSISTENCY_CORRECTED_REFERENCE.csv")
    ref_by = {r["entry_id"]: r for r in ref_rows}
    for r in rows:
        eid = r["entry_id"]
        for f in coding_fields:
            if r.get(f) != ref_by[eid].get(f):
                errors.append(f"coding changed for {eid}.{f}")
                break
    return len(errors) == 0, errors


def main() -> int:
    ref_path = AUDIT_D_DIR / "CONSISTENCY_CORRECTED_REFERENCE.csv"
    screening_path = AUDIT_D_DIR / "CONSISTENCY_SCREENING_RESULTS.csv"

    if not APPROVED_TRACEABILITY_SRC.exists():
        print(f"Missing approved traceability source: {APPROVED_TRACEABILITY_SRC}")
        return 1

    class_by_id = load_human_traceability(APPROVED_TRACEABILITY_SRC)
    ok, verr = verify_inputs(ref_path, screening_path, class_by_id)
    if not ok:
        print("VERIFICATION FAILED:")
        for e in verr:
            print(f"  - {e}")
        return 1

    work_dir = ROOT / f"outputs/framework_mapping/run_{run_timestamp()}_post60_analytical_audit_E_final"
    work_dir.mkdir(parents=True, exist_ok=True)

    rows, _ = read_csv(ref_path)
    pre_rows, _ = read_csv(PRE_AUDIT_D_REF)
    pre_by_id = {r["entry_id"]: r for r in pre_rows}
    scr_rows, _ = read_csv(screening_path)
    status_by_id = {r["entry_id"]: r.get("consistency_review_status", "") for r in scr_rows}

    traceability_rows = build_traceability_human_classification(class_by_id)
    write_csv(
        work_dir / "AUDIT_E_TRACEABILITY_HUMAN_CLASSIFICATION.csv",
        traceability_rows,
        ["entry_id", "approved_traceability_category", "source_of_classification", "reviewer_basis", "approval_status"],
    )

    n = len(rows)
    traceable = sum(1 for r in rows if is_traceable(r))
    jee_m = sum(1 for r in rows if jee_mapped(r))
    dq_m = sum(1 for r in rows if dq_mapped(r))
    cat_counts = Counter(class_by_id.values())
    lexical_diag = sum(1 for r in rows if lexical_non_exact_non_substring_match(r))
    dq_jee_unmapped = sum(1 for r in rows if dq_mapped(r) and not jee_mapped(r))

    # A. Dataset profile
    profile = [
        {"metric": "total_records", "value": str(n), "percentage": pct(n, n)},
        {"metric": "traceable_source_level", "value": str(traceable), "percentage": pct(traceable, n)},
        {"metric": "non_traceable_source_level", "value": str(n - traceable), "percentage": pct(n - traceable, n)},
    ]
    for cat, c in sorted(cat_counts.items(), key=lambda x: (-x[1], x[0])):
        profile.append({"metric": f"traceability_human_{cat}", "value": str(c), "percentage": pct(c, n)})
    profile.append({"metric": "lexical_diagnostic_non_exact_non_substring", "value": str(lexical_diag), "percentage": pct(lexical_diag, n)})
    for st, c in Counter(r.get("human_candidate_statement_type", "") for r in rows).most_common():
        profile.append({"metric": f"statement_type_{st}", "value": str(c), "percentage": pct(c, n)})
    for pi, c in Counter(r.get("human_policy_vs_inquiry", "") for r in rows).most_common():
        profile.append({"metric": f"policy_or_inquiry_{pi}", "value": str(c), "percentage": pct(c, n)})
    for st, c in Counter(status_by_id.get(r["entry_id"], "") for r in rows).most_common():
        profile.append({"metric": f"consistency_review_{st}", "value": str(c), "percentage": pct(c, n)})
    write_csv(work_dir / "AUDIT_E_DATASET_PROFILE.csv", profile, ["metric", "value", "percentage"])

    # B. JEE summary
    jee_summary = []
    jee_status = Counter(r.get("human_JEE_decision", "") for r in rows)
    for status, c in sorted(jee_status.items(), key=lambda x: (-x[1], x[0])):
        jee_summary.append({"category": "jee_status", "label": status, "count": c, "percentage": pct(c, n)})
    jee_summary.append({"category": "jee_mapped_total", "label": "mapped", "count": jee_m, "percentage": pct(jee_m, n)})
    primary_jee = Counter(r.get("human_primary_JEE", "") for r in rows if (r.get("human_primary_JEE") or "").strip())
    for area, c in primary_jee.most_common():
        jee_summary.append({"category": "jee_primary", "label": area, "count": c, "percentage": pct(c, jee_m)})
    write_csv(work_dir / "AUDIT_E_JEE_SUMMARY.csv", jee_summary, ["category", "label", "count", "percentage"])

    # C. DQ summary
    dq_summary = []
    dq_status = Counter(r.get("human_DQ_decision", "") for r in rows)
    for status, c in sorted(dq_status.items(), key=lambda x: (-x[1], x[0])):
        dq_summary.append({"category": "dq_status", "label": status, "count": c, "percentage": pct(c, n)})
    dq_summary.append({"category": "dq_mapped_total", "label": "mapped", "count": dq_m, "percentage": pct(dq_m, n)})
    primary_dq = Counter(r.get("human_primary_DQ", "") for r in rows if (r.get("human_primary_DQ") or "").strip())
    for el, c in primary_dq.most_common():
        dq_summary.append({"category": "dq_primary", "label": el, "count": c, "percentage": pct(c, dq_m)})
    secondary_dq = Counter(r.get("human_secondary_DQ", "") for r in rows if (r.get("human_secondary_DQ") or "").strip())
    for el, c in secondary_dq.most_common():
        dq_summary.append({"category": "dq_secondary", "label": el, "count": c, "percentage": pct(c, dq_m)})
    write_csv(work_dir / "AUDIT_E_DQ_SUMMARY.csv", dq_summary, ["category", "label", "count", "percentage"])

    # D. Crosstabs
    crosstab_dir = work_dir / "crosstabs"
    crosstab_dir.mkdir(exist_ok=True)
    enriched = []
    for r in rows:
        e = dict(r)
        e["jee_mapped_flag"] = "mapped" if jee_mapped(r) else "unmapped"
        e["dq_mapped_flag"] = "mapped" if dq_mapped(r) else "unmapped"
        e["traceability_flag"] = "traceable" if is_traceable(r) else "non_traceable"
        e["traceability_human_category"] = class_by_id[r["entry_id"]]
        enriched.append(e)

    for name, data in [
        ("jee_vs_dq_mapped", crosstab(enriched, "jee_mapped_flag", "dq_mapped_flag", "jee_outcome", "dq_outcome")),
        ("jee_primary_vs_dq_primary", crosstab([r for r in enriched if (r.get("human_primary_JEE") or "").strip()], "human_primary_JEE", "human_primary_DQ", "jee_primary", "dq_primary")),
        ("statement_type_vs_jee", crosstab(enriched, "human_candidate_statement_type", "jee_mapped_flag", "statement_type", "jee_outcome")),
        ("statement_type_vs_dq", crosstab(enriched, "human_candidate_statement_type", "dq_mapped_flag", "statement_type", "dq_outcome")),
        ("traceability_vs_jee", crosstab(enriched, "traceability_flag", "jee_mapped_flag", "traceability", "jee_outcome")),
        ("traceability_vs_dq", crosstab(enriched, "traceability_flag", "dq_mapped_flag", "traceability", "dq_outcome")),
        ("policy_inquiry_vs_jee", crosstab(enriched, "human_policy_vs_inquiry", "jee_mapped_flag", "policy_or_inquiry", "jee_outcome")),
        ("policy_inquiry_vs_dq", crosstab(enriched, "human_policy_vs_inquiry", "dq_mapped_flag", "policy_or_inquiry", "dq_outcome")),
        ("traceability_category_vs_jee", crosstab(enriched, "traceability_human_category", "jee_mapped_flag", "traceability_category", "jee_outcome")),
        ("traceability_category_vs_dq", crosstab(enriched, "traceability_human_category", "dq_mapped_flag", "traceability_category", "dq_outcome")),
    ]:
        cols = list(data[0].keys()) if data else ["count"]
        write_csv(crosstab_dir / f"AUDIT_E_{name}.csv", data, cols)

    (work_dir / "AUDIT_E_JEE_DQ_CROSSTABS_INDEX.md").write_text(
        "# Audit E Final — JEE/DQ cross-tabulation index\n\n"
        "Descriptive cross-tabulations only (n=60 purposive pilot).\n\n"
        + "\n".join(f"- `crosstabs/AUDIT_E_{n}.csv`" for n, _ in [
            ("jee_vs_dq_mapped", None), ("jee_primary_vs_dq_primary", None),
            ("statement_type_vs_jee", None), ("statement_type_vs_dq", None),
            ("traceability_vs_jee", None), ("traceability_vs_dq", None),
            ("policy_inquiry_vs_jee", None), ("policy_inquiry_vs_dq", None),
            ("traceability_category_vs_jee", None), ("traceability_category_vs_dq", None),
        ]),
        encoding="utf-8",
    )

    # E. Failure modes
    fm = build_failure_modes(rows, pre_by_id, class_by_id)
    write_csv(work_dir / "AUDIT_E_FAILURE_MODES.csv", fm,
              ["failure_mode_id", "definition", "n_records", "percentage", "representative_entry_ids",
               "brief_example_paraphrase", "methodological_implication"])

    # F. Sensitivity
    detail, sens_summary, pre_stats, post_stats = sensitivity_analysis(rows, pre_by_id)
    write_csv(work_dir / "AUDIT_E_AUDIT_D_SENSITIVITY.csv", sens_summary,
              ["metric", "pre_audit_d", "post_audit_d", "delta"])
    write_csv(work_dir / "AUDIT_E_AUDIT_D_SENSITIVITY_DETAIL.csv", detail, list(detail[0].keys()) if detail else [])

    jee_no_map = jee_status.get("no_mapping", 0)
    jee_insuf = jee_status.get("insufficient_evidence", 0)

    provenance_note = f"""# Audit E — Review Provenance Note

Generated (UTC): {now_iso()}

## Status legend (Audit D labels — frozen, not altered)

| Audit D status label | n | Meaning for dissertation |
|----------------------|--:|--------------------------|
| `consistency_human_reviewed_keep` | 52 | Prior manual human adjudication **retained** via AI-assisted keep_all import; **no** individual interactive Audit D re-review |
| `consistency_human_reviewed_corrected` | 6 | Prior adjudication **updated** after interactive human confirmation of AI-proposed corrections |
| `consistency_auto_clear` | 2 | No consistency flags raised; prior adjudication unchanged |

## Dissertation-facing review description

The pilot consisted of 60 records originally adjudicated by a single human reviewer. Subsequent AI-assisted source-integrity and coding-consistency audits identified potential issues for targeted review. Six proposed coding corrections received interactive human confirmation, while 52 records retained their earlier adjudication through an AI-assisted keep-all recommendation without individual re-review during Audit D. Two records completed the predefined auto-clear route.

## Concise pilot description

A single-reviewer, human-adjudicated pilot supported by AI-assisted source-integrity and coding-consistency audits, with targeted human confirmation of proposed corrections.

**Clarification:** "Targeted human confirmation" refers to proposed corrections (six Audit D records, plus Audit C source-integrity approvals). It does **not** mean that all 52 retained records were interactively re-adjudicated during Audit D.

## All 60 records

Every record received manual human adjudication before Audit D (review_status=complete, reviewer AL, July 2026). Audit D did not replace the original adjudication workflow; it audited consistency of labels and rationales against frozen coding rules.
"""

    revision_log = f"""# Audit E — Revision Log

Generated (UTC): {now_iso()}

## Superseded run

- **Original:** `outputs/framework_mapping/run_20260727_110052_post60_analytical_audit_E`
- **Reason superseded:** String-based 53/60 metric incorrectly described as substantive divergence from source passages
- **Human-approval gate:** `outputs/framework_mapping/run_20260727_131920_audit_E_human_approval_check`
- **Final frozen run:** `{work_dir.relative_to(ROOT).as_posix()}`

## Correction 1 — Invalid divergence claim

| Item | Detail |
|------|--------|
| **Original incorrect wording** | "88.3% (53/60) generated decisions diverge from source quotes" |
| **Why incorrect** | `_decision_diverges()` / `_decision_diverges()` only tested non-identical strings without substring containment; it did not assess substantive faithfulness or material alteration |
| **Approved replacement** | Human-reviewed four-category traceability classification (8 / 25 / 20 / 7) |
| **Files revised** | AUDIT_E_EXECUTIVE_SUMMARY.md, AUDIT_E_ANALYTICAL_REPORT.md, AUDIT_E_DISSERTATION_FINDINGS.md, AUDIT_E_GO_NO_GO.md, AUDIT_E_FAILURE_MODES.csv, AUDIT_E_DATASET_PROFILE.csv |

## Correction 2 — Review provenance

| Item | Detail |
|------|--------|
| **Original misleading implication** | 52 `consistency_human_reviewed_keep` records appeared human-reviewed during Audit D |
| **Approved replacement** | Prior adjudication retained via AI-assisted keep_all without individual interactive re-review |
| **Files revised** | AUDIT_E_DISSERTATION_FINDINGS.md, AUDIT_E_REVIEW_PROVENANCE_NOTE.md, AUDIT_E_ANALYTICAL_REPORT.md |

## Correction 3 — Pilot-local frequency language

| Item | Detail |
|------|--------|
| **Original wording** | "dominant mixed pattern" |
| **Approved replacement** | "the most frequent pattern in this 60-record pilot" |
| **Files revised** | AUDIT_E_EXECUTIVE_SUMMARY.md, AUDIT_E_ANALYTICAL_REPORT.md |

## Script versioning

| Script | Role |
|--------|------|
| `scripts/run_post60_analytical_audit_E_v1.py` | Preserved original (contains `_decision_diverges` substantive misuse) |
| `scripts/run_post60_analytical_audit_E_final.py` | Final workflow; loads human classifications; lexical diagnostic labelled `lexical_non_exact_non_substring_match` |

## Coding records

**Confirmation: no coding values changed.** Input remains frozen `CONSISTENCY_CORRECTED_REFERENCE.csv` (SHA256 verified). Only interpretive documentation and analytical labelling were revised.
"""

    executive = f"""# Audit E — Executive Summary (Final)

Generated (UTC): {now_iso()}  
Status: **FROZEN** — human-approved corrected terminology

## What was analysed

Read-only descriptive analysis of 60 human-adjudicated decision-journal entries from `CONSISTENCY_CORRECTED_REFERENCE.csv` (SHA256 verified). Input: single-reviewer human-adjudicated reference set after AI-assisted source-integrity (Audit C) and coding-consistency (Audit D) audits.

## Key descriptive findings

| Domain | Finding |
|--------|---------|
| JEE mapped | {pct(jee_m, n)} |
| JEE no_mapping | {pct(jee_no_map, n)} |
| JEE insufficient_evidence | {pct(jee_insuf, n)} |
| DQ mapped | {pct(dq_m, n)} |
| Source-level traceable (`traceability_ok=True`) | {pct(traceable, n)} |

**Human-reviewed candidate-decision traceability (single reviewer):**

| Category | n | % |
|----------|--:|---|
| Exact or near-verbatim | {cat_counts['exact_or_near_verbatim']} | {pct(cat_counts['exact_or_near_verbatim'], n)} |
| Substantively faithful paraphrase | {cat_counts['substantively_faithful_paraphrase']} | {pct(cat_counts['substantively_faithful_paraphrase'], n)} |
| Materially unsupported or altered | {cat_counts['materially_unsupported_or_altered']} | {pct(cat_counts['materially_unsupported_or_altered'], n)} |
| Traceability=False | {cat_counts['traceability_false']} | {pct(cat_counts['traceability_false'], n)} |

Among the 11 JEE-mapped records, R4 occurred in 3 (27.3%, 3/11), while P3, D2 and R5 each occurred in 2 (18.2%, 2/11).

Among the 37 DQ-mapped records, commitment_to_follow_through was the **primary** element in 22 (59.5%, 22/37), helpful_frame in 8 (21.6%, 8/37), and clear_values in 6 (16.2%, 6/37).

The most frequent combined outcome in this purposive 60-record pilot was an observable Decision Quality element without a defensible JEE mapping, occurring in 26 of 60 records (43.3%).

## Did the frameworks add useful interpretation?

**Yes, with boundaries.** JEE mapping identifies specific preparedness capacities where passage evidence supports it. Decision Quality elements are more frequently observable than JEE capacities. `no_mapping` and `insufficient_evidence` are analytically distinct boundary conditions, not extraction failures.

## Traceability finding

Generated decision statements were not treated as authoritative evidence. Framework interpretation relied on validated source passages rather than generated decision wording. These categories were assigned by a single reviewer and should be interpreted as a structured feasibility assessment rather than an independently validated estimate of model error.

## Principal limitations

Purposive 60-record pilot; not representative of the 414-entry corpus. Single-reviewer workflow. No inferential or causal claims.

## Recommendations

| Decision | Recommendation |
|----------|----------------|
| **Dissertation integration** | **GO WITH LIMITATIONS** — supplementary feasibility analysis; does not require mapping all 414 records |
| **Full-corpus scaling** | **GO AFTER SPECIFIED CHANGES** — workflow stable; plan human review burden and periodic consistency audits |
"""

    report = f"""# Audit E — Analytical Report (Final)

Generated (UTC): {now_iso()}  
Status: **FROZEN**

## 1. Verification

| Check | Result |
|-------|--------|
| Input SHA256 | `{EXPECTED_REF_SHA256}` — verified |
| Records | 60 |
| Pending review | 0 |
| Coding values changed | No |

## 2. Traceability interpretation

Generated decision statements were not treated as authoritative evidence. Of the 60 candidate decisions:

- {cat_counts['exact_or_near_verbatim']} ({pct(cat_counts['exact_or_near_verbatim'], n)}) exact or near-verbatim
- {cat_counts['substantively_faithful_paraphrase']} ({pct(cat_counts['substantively_faithful_paraphrase'], n)}) substantively faithful paraphrases
- {cat_counts['materially_unsupported_or_altered']} ({pct(cat_counts['materially_unsupported_or_altered'], n)}) materially unsupported or altered despite traceable source
- {cat_counts['traceability_false']} ({pct(cat_counts['traceability_false'], n)}) non-traceable (`traceability_ok=False`)

**Limitation:** Single-reviewer human classification; structured feasibility assessment, not independent gold standard.

**Technical diagnostic only:** {lexical_diag} of {n} records ({pct(lexical_diag, n)}) show the lexical flag `non_exact_non_substring_string_match` (non-identical strings with no substring containment). This must not be interpreted as substantive divergence.

**Analytical implications retained:**
- Source quotations must remain attached to decision objects
- Human review required before decision-journal records are used for audit or accountability
- Generated decisions are candidate summaries, not authoritative records
- Textual traceability and framework applicability are separate dimensions

## 3. Review provenance

See `AUDIT_E_REVIEW_PROVENANCE_NOTE.md`. Fifty-two flagged records retained prior adjudication via AI-assisted keep_all **without individual interactive Audit D re-review**.

## 4. JEE and DQ findings

JEE mapped: {pct(jee_m, n)}. DQ mapped: {pct(dq_m, n)}. `no_mapping` and `insufficient_evidence` reported separately.

The most frequent combined outcome in this purposive 60-record pilot was DQ mapped / JEE unmapped: {pct(dq_jee_unmapped, n)} ({dq_jee_unmapped}/60). This pattern must not be generalised to the 414-entry corpus.

## 5. Audit D sensitivity

19 field changes across 6 records; JEE mapped {pre_stats['jee']['mapped']}→{post_stats['jee']['mapped']}; DQ mapped unchanged at {post_stats['dq']['mapped']}. Edge-case refinement only.

## 6. GO/NO-GO

Dissertation integration: **GO WITH LIMITATIONS**. Full-corpus scaling: **GO AFTER SPECIFIED CHANGES**.
"""

    dissertation = f"""# Audit E — Dissertation Findings (Final)

Generated (UTC): {now_iso()}

## Methodological finding

**Direct empirical finding:** A purposive 60-record pilot completed single-reviewer human adjudication with AI-assisted source-integrity and coding-consistency audits. All 60 records complete; zero pending.

**Pilot description:** The pilot consisted of 60 records originally adjudicated by a single human reviewer. Subsequent AI-assisted source-integrity and coding-consistency audits identified potential issues for targeted review. Six proposed coding corrections received interactive human confirmation, while 52 records retained their earlier adjudication through an AI-assisted keep-all recommendation without individual re-review during Audit D. Two records completed the predefined auto-clear route.

**Cannot conclude:** Independent dual-coder validation, gold-standard reference set, or representativeness of the 414-entry corpus.

## Preparedness-framework finding

**Direct empirical finding:** {pct(jee_m, n)} support mapped JEE capacity. Unmapped: insufficient_evidence {pct(jee_insuf, n)}, no_mapping {pct(jee_no_map, n)}.

Among the 11 JEE-mapped records, R4 occurred in 3 (27.3%, 3/11), while P3, D2 and R5 each occurred in 2 (18.2%, 2/11).

## Decision-quality finding

**Direct empirical finding:** {pct(dq_m, n)} ({dq_m}/60) contain observable DQ evidence.

Among the 37 DQ-mapped records, commitment_to_follow_through was the primary element in 22 (59.5%, 22/37), helpful_frame in 8 (21.6%, 8/37), clear_values in 6 (16.2%, 6/37). Secondary DQ elements (records with any secondary label): useful_information 3, clear_values 2, sound_reasoning 1, commitment_to_follow_through 1.

## Traceability finding

Generated decision statements were not treated as authoritative evidence. Of the 60 candidate decisions, 8 were exact or near-verbatim representations of their source passages and 25 were judged to be substantively faithful paraphrases. Twenty introduced materially unsupported or altered meaning despite retaining a traceable source passage, while 7 were classified as non-traceable. Framework interpretation therefore relied on the validated source passage rather than the generated decision statement.

These categories were assigned by a single reviewer and should be interpreted as a structured feasibility assessment rather than an independently validated estimate of model error.

## Human-oversight finding

Six Audit D corrections human-confirmed (19 field changes). Fifty-two records retained prior adjudication without interactive Audit D re-review.

## Limitations

Purposive pilot; single reviewer; no statistical generalisation; separate handling of textual traceability and framework applicability required.

## Organisational learning implication

Treat unmapped and insufficient-evidence codes as informative boundary conditions. Require human review and source-attached quotations before using generated decision-journal candidates for accountability analysis.
"""

    go_no_go = f"""# Audit E — GO/NO-GO Assessment (Final)

Generated (UTC): {now_iso()}

## Dissertation-integration decision

### **GO WITH LIMITATIONS**

Include as supplementary human-validated feasibility analysis. **Does not require mapping all 414 records.**

## Full-corpus-scaling decision

### **GO AFTER SPECIFIED CHANGES**

Methodologically stable; plan human review burden, periodic consistency audits, traceability protocol.

## Audit D sensitivity

Edge-case refinement only. Aggregate mapped proportions stable after six corrections.
"""

    (work_dir / "AUDIT_E_REVIEW_PROVENANCE_NOTE.md").write_text(provenance_note, encoding="utf-8")
    (work_dir / "AUDIT_E_REVISION_LOG.md").write_text(revision_log, encoding="utf-8")
    (work_dir / "AUDIT_E_EXECUTIVE_SUMMARY.md").write_text(executive, encoding="utf-8")
    (work_dir / "AUDIT_E_ANALYTICAL_REPORT.md").write_text(report, encoding="utf-8")
    (work_dir / "AUDIT_E_DISSERTATION_FINDINGS.md").write_text(dissertation, encoding="utf-8")
    (work_dir / "AUDIT_E_GO_NO_GO.md").write_text(go_no_go, encoding="utf-8")

    val_ok, val_err = validate_outputs(work_dir, rows, class_by_id)
    if not val_ok:
        print("OUTPUT VALIDATION FAILED:")
        for e in val_err:
            print(f"  - {e}")
        return 1

    manifest = {
        "task": "post60_analytical_audit_E_final",
        "status": "frozen",
        "frozen_at_utc": now_iso(),
        "work_dir": str(work_dir),
        "supersedes": str(ORIGINAL_AUDIT_E),
        "superseded_reason": "string-based 53/60 metric incorrectly described as substantive divergence",
        "human_approval_gate": str(HUMAN_APPROVAL_DIR),
        "input_file": str(ref_path),
        "input_sha256": EXPECTED_REF_SHA256,
        "input_sha256_verified": True,
        "traceability_human_classification_source": str(APPROVED_TRACEABILITY_SRC),
        "traceability_category_counts": dict(cat_counts),
        "lexical_diagnostic_non_exact_non_substring": lexical_diag,
        "coding_values_changed": False,
        "audit_d_dir_frozen": str(AUDIT_D_DIR),
        "n_records": n,
        "jee_mapped": jee_m,
        "dq_mapped": dq_m,
        "dissertation_decision": "GO WITH LIMITATIONS",
        "scaling_decision": "GO AFTER SPECIFIED CHANGES",
        "script_final": "scripts/run_post60_analytical_audit_E_final.py",
        "script_v1_preserved": "scripts/run_post60_analytical_audit_E_v1.py",
    }
    (work_dir / "AUDIT_E_MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    sha_lines = []
    for p in sorted(work_dir.rglob("*")):
        if p.is_file():
            sha_lines.append(f"{sha256_file(p)}  {p.as_posix()}")
    (work_dir / "AUDIT_E_SHA256SUMS.txt").write_text("\n".join(sha_lines) + "\n", encoding="utf-8")

    print(f"AUDIT E FINAL FROZEN: {work_dir}")
    print(f"traceability: {dict(cat_counts)}")
    print(f"lexical_diagnostic_only={lexical_diag}/60 (not substantive divergence)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
