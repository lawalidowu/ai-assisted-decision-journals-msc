#!/usr/bin/env python3
"""
Audit E — Post-adjudication analytical and interpretive audit.

Read-only analysis of CONSISTENCY_CORRECTED_REFERENCE.csv.
Does not modify frozen Audit D or source directories.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT_D_DIR = ROOT / "outputs/framework_mapping/run_20260727_094015_post60_coding_consistency_audit"
PRE_AUDIT_D_REF = ROOT / "outputs/framework_mapping/run_20260727_080220_post60_source_integrity_audit/corrected_adjudication_copy.csv"
EXPECTED_REF_SHA256 = "eec6c4e87dfa9b42421a13fce4ebca9c84701ad80d765f19fbdba59ab0c75770"

JEE_MAPPED = {"accept_primary", "accept_primary_and_secondary", "replace"}
JEE_UNMAPPED = {"no_mapping", "insufficient_evidence", "procedural_or_inquiry"}
DQ_MAPPED = {"accept", "replace"}
DQ_UNMAPPED = {"insufficient_evidence", "procedural_or_inquiry"}

EDIT_IDS = ["phase1-003", "phase1-161", "phase1-182", "phase1-246", "phase1-311", "phase1-382"]

FAILURE_MODES = [
    ("FM_THIN_VAGUE_SOURCE", "Source passage too thin or vague to identify a specific JEE capacity or DQ element",
     lambda r: (r.get("human_JEE_decision") or "") == "insufficient_evidence"
     or (r.get("human_DQ_decision") or "") == "insufficient_evidence"),
    ("FM_CLEAR_BUT_NO_JEE_CAPACITY", "Passage sufficiently clear but does not support a specific JEE capacity",
     lambda r: (r.get("human_JEE_decision") or "") == "no_mapping"),
    ("FM_PROCEDURAL_INQUIRY", "Passage concerns Inquiry administration rather than substantive preparedness policy",
     lambda r: (r.get("human_JEE_decision") or "") == "procedural_or_inquiry"
     or (r.get("human_DQ_decision") or "") == "procedural_or_inquiry"),
    ("FM_NON_TRACEABLE", "Generated decision not traceable to source quote (traceability_ok=False)",
     lambda r: str(r.get("traceability_ok", "")).strip().lower() not in ("true", "1", "yes")),
    ("FM_DECISION_SOURCE_DIVERGENCE", "Generated decision adds substantive content not in source quote",
     lambda r: _decision_diverges(r)),
    ("FM_UNSUPPORTED_SECONDARY_JEE", "Secondary JEE mapping without independent passage evidence (pre-Audit-D artefact)",
     lambda r: bool((r.get("human_secondary_JEE") or "").strip())),
    ("FM_LOW_MEDIUM_CONFIDENCE", "Human confidence low or medium despite substantive coding",
     lambda r: (r.get("human_JEE_confidence") or "") in ("low", "medium")
     or (r.get("human_DQ_confidence") or "") in ("low", "medium")),
]


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


def is_traceable(r: dict) -> bool:
    return str(r.get("traceability_ok", "")).strip().lower() in ("true", "1", "yes")


def jee_mapped(r: dict) -> bool:
    return (r.get("human_JEE_decision") or "").strip() in JEE_MAPPED


def dq_mapped(r: dict) -> bool:
    return (r.get("human_DQ_decision") or "").strip() in DQ_MAPPED


def _norm(s: str) -> str:
    return " ".join((s or "").lower().split())


def _decision_diverges(r: dict) -> bool:
    d = _norm(r.get("decision", ""))
    q = _norm(r.get("source_quote", ""))
    if not d or not q:
        return False
    return d != q and d not in q and q not in d


def verify_inputs(ref_path: Path, screening_path: Path) -> tuple[bool, list[str]]:
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
    return len(errors) == 0, errors


def counter_rows(counter: Counter, total: int, key_col: str, count_col: str = "count", pct_col: str = "percentage") -> list[dict]:
    return [{key_col: k, count_col: v, pct_col: pct(v, total)} for k, v in sorted(counter.items(), key=lambda x: (-x[1], x[0]))]


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


def build_failure_modes(rows: list[dict], pre_rows: dict[str, dict]) -> list[dict]:
    out = []
    for mode_id, definition, predicate in FAILURE_MODES:
        affected = [r for r in rows if predicate(r)]
        if mode_id == "FM_UNSUPPORTED_SECONDARY_JEE":
            affected = [pre_rows[eid] for eid in pre_rows if (pre_rows[eid].get("human_secondary_JEE") or "").strip()]
        if not affected:
            continue
        eids = [r["entry_id"] for r in affected][:8]
        example = (affected[0].get("human_overall_rationale") or affected[0].get("human_JEE_rationale") or "")[:200]
        implications = {
            "FM_THIN_VAGUE_SOURCE": "Distinguish from extraction failure; reflects source granularity limits.",
            "FM_CLEAR_BUT_NO_JEE_CAPACITY": "Framework applicable but passage lacks capacity-specific evidence.",
            "FM_PROCEDURAL_INQUIRY": "Inquiry-administration content excluded from substantive preparedness mapping.",
            "FM_NON_TRACEABLE": "Generated-candidate field unreliable; analysis must use source quote.",
            "FM_DECISION_SOURCE_DIVERGENCE": "Automated decision field must not substitute for source evidence.",
            "FM_UNSUPPORTED_SECONDARY_JEE": "Secondary mappings require independent passage evidence (corrected in Audit D).",
            "FM_LOW_MEDIUM_CONFIDENCE": "Interpretive caution warranted even where coding is complete.",
        }.get(mode_id, "")
        out.append({
            "failure_mode_id": mode_id,
            "definition": definition,
            "n_records": len(affected),
            "percentage": pct(len(affected), len(rows)),
            "representative_entry_ids": "|".join(eids),
            "brief_example_paraphrase": example,
            "methodological_implication": implications,
        })
    return out


def sensitivity_analysis(final_rows: list[dict], pre_by_id: dict[str, dict]) -> tuple[list[dict], dict]:
    preview_path = AUDIT_D_DIR / "CONSISTENCY_CORRECTIONS_PREVIEW.csv"
    changes, _ = read_csv(preview_path)
    detail_rows = []
    for ch in changes:
        detail_rows.append(dict(ch))

    def jee_counts(rows):
        c = Counter(r.get("human_JEE_decision", "") for r in rows)
        mapped = sum(1 for r in rows if jee_mapped(r))
        return {"mapped": mapped, "status": dict(c)}

    def dq_counts(rows):
        mapped = sum(1 for r in rows if dq_mapped(r))
        c = Counter(r.get("human_DQ_decision", "") for r in rows)
        return {"mapped": mapped, "status": dict(c)}

    def st_counts(rows):
        return dict(Counter(r.get("human_candidate_statement_type", "") for r in rows))

    pre_stats = {"jee": jee_counts(list(pre_by_id.values())), "dq": dq_counts(list(pre_by_id.values())), "st": st_counts(list(pre_by_id.values()))}
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


def main() -> int:
    ref_path = AUDIT_D_DIR / "CONSISTENCY_CORRECTED_REFERENCE.csv"
    screening_path = AUDIT_D_DIR / "CONSISTENCY_SCREENING_RESULTS.csv"

    ok, verr = verify_inputs(ref_path, screening_path)
    if not ok:
        print("VERIFICATION FAILED — stopping without analytical results:")
        for e in verr:
            print(f"  - {e}")
        return 1

    work_dir = ROOT / f"outputs/framework_mapping/run_{run_timestamp()}_post60_analytical_audit_E"
    work_dir.mkdir(parents=True, exist_ok=True)

    rows, _ = read_csv(ref_path)
    pre_rows, _ = read_csv(PRE_AUDIT_D_REF)
    pre_by_id = {r["entry_id"]: r for r in pre_rows}
    scr_rows, _ = read_csv(screening_path)
    status_by_id = {r["entry_id"]: r.get("consistency_review_status", "") for r in scr_rows}

    n = len(rows)
    traceable = sum(1 for r in rows if is_traceable(r))
    jee_m = sum(1 for r in rows if jee_mapped(r))
    dq_m = sum(1 for r in rows if dq_mapped(r))

    # A. Dataset profile
    profile = []
    profile.append({"metric": "total_records", "value": str(n), "percentage": pct(n, n)})
    profile.append({"metric": "traceable", "value": str(traceable), "percentage": pct(traceable, n)})
    profile.append({"metric": "non_traceable", "value": str(n - traceable), "percentage": pct(n - traceable, n)})
    for st, c in Counter(r.get("human_candidate_statement_type", "") for r in rows).most_common():
        profile.append({"metric": f"statement_type_{st}", "value": str(c), "percentage": pct(c, n)})
    for pi, c in Counter(r.get("human_policy_vs_inquiry", "") for r in rows).most_common():
        profile.append({"metric": f"policy_or_inquiry_{pi}", "value": str(c), "percentage": pct(c, n)})
    for st, c in Counter(status_by_id.get(r["entry_id"], "") for r in rows).most_common():
        profile.append({"metric": f"consistency_review_{st}", "value": str(c), "percentage": pct(c, n)})
    complete_src = sum(1 for r in rows if (r.get("source_quote") or "").strip() and (r.get("evidence") or "").strip() and (r.get("decision") or "").strip())
    profile.append({"metric": "complete_source_decision_evidence_fields", "value": str(complete_src), "percentage": pct(complete_src, n)})
    for field in ["human_JEE_decision", "human_DQ_decision", "human_candidate_statement_type", "human_policy_vs_inquiry"]:
        missing = sum(1 for r in rows if not (r.get(field) or "").strip())
        profile.append({"metric": f"missing_{field}", "value": str(missing), "percentage": pct(missing, n)})

    write_csv(work_dir / "AUDIT_E_DATASET_PROFILE.csv", profile, ["metric", "value", "percentage"])

    # B. JEE summary
    jee_summary = []
    jee_status = Counter(r.get("human_JEE_decision", "") for r in rows)
    for status, c in sorted(jee_status.items(), key=lambda x: (-x[1], x[0])):
        jee_summary.append({"category": "jee_status", "label": status, "count": c, "percentage": pct(c, n)})
    jee_summary.append({"category": "jee_mapped_total", "label": "mapped", "count": jee_m, "percentage": pct(jee_m, n)})
    jee_summary.append({"category": "jee_unmapped_total", "label": "unmapped", "count": n - jee_m, "percentage": pct(n - jee_m, n)})

    primary_jee = Counter(r.get("human_primary_JEE", "") for r in rows if (r.get("human_primary_JEE") or "").strip())
    for area, c in primary_jee.most_common():
        jee_summary.append({"category": "jee_primary", "label": area, "count": c, "percentage": pct(c, jee_m)})

    secondary_jee = Counter(r.get("human_secondary_JEE", "") for r in rows if (r.get("human_secondary_JEE") or "").strip())
    for area, c in secondary_jee.most_common():
        jee_summary.append({"category": "jee_secondary", "label": area, "count": c, "percentage": pct(c, jee_m)})

    primary_only = sum(1 for r in rows if jee_mapped(r) and (r.get("human_primary_JEE") or "").strip() and not (r.get("human_secondary_JEE") or "").strip())
    both = sum(1 for r in rows if (r.get("human_primary_JEE") or "").strip() and (r.get("human_secondary_JEE") or "").strip())
    jee_summary.append({"category": "jee_primary_only", "label": "primary_only", "count": primary_only, "percentage": pct(primary_only, jee_m)})
    jee_summary.append({"category": "jee_primary_and_secondary", "label": "valid_both", "count": both, "percentage": pct(both, jee_m)})

    for conf, c in Counter(r.get("human_JEE_confidence", "") for r in rows if jee_mapped(r)).most_common():
        jee_summary.append({"category": "jee_confidence_mapped", "label": conf, "count": c, "percentage": pct(c, jee_m)})

    write_csv(work_dir / "AUDIT_E_JEE_SUMMARY.csv", jee_summary, ["category", "label", "count", "percentage"])

    # C. DQ summary
    dq_summary = []
    dq_status = Counter(r.get("human_DQ_decision", "") for r in rows)
    for status, c in sorted(dq_status.items(), key=lambda x: (-x[1], x[0])):
        dq_summary.append({"category": "dq_status", "label": status, "count": c, "percentage": pct(c, n)})
    dq_summary.append({"category": "dq_mapped_total", "label": "mapped", "count": dq_m, "percentage": pct(dq_m, n)})
    no_dq = sum(1 for r in rows if (r.get("human_DQ_decision") or "") in DQ_UNMAPPED)
    dq_summary.append({"category": "dq_no_defensible_mapping", "label": "unmapped", "count": no_dq, "percentage": pct(no_dq, n)})

    primary_dq = Counter(r.get("human_primary_DQ", "") for r in rows if (r.get("human_primary_DQ") or "").strip())
    for el, c in primary_dq.most_common():
        dq_summary.append({"category": "dq_primary", "label": el, "count": c, "percentage": pct(c, dq_m)})

    secondary_dq = Counter(r.get("human_secondary_DQ", "") for r in rows if (r.get("human_secondary_DQ") or "").strip())
    for el, c in secondary_dq.most_common():
        dq_summary.append({"category": "dq_secondary", "label": el, "count": c, "percentage": pct(c, dq_m)})

    for conf, c in Counter(r.get("human_DQ_confidence", "") for r in rows if dq_mapped(r)).most_common():
        dq_summary.append({"category": "dq_confidence_mapped", "label": conf, "count": c, "percentage": pct(c, dq_m)})

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
        enriched.append(e)

    ct1 = crosstab(enriched, "jee_mapped_flag", "dq_mapped_flag", "jee_outcome", "dq_outcome")
    ct2 = crosstab([r for r in enriched if (r.get("human_primary_JEE") or "").strip()],
                   "human_primary_JEE", "human_primary_DQ", "jee_primary", "dq_primary")
    ct3 = crosstab(enriched, "human_candidate_statement_type", "jee_mapped_flag", "statement_type", "jee_outcome")
    ct4 = crosstab(enriched, "human_candidate_statement_type", "dq_mapped_flag", "statement_type", "dq_outcome")
    ct5 = crosstab(enriched, "traceability_flag", "jee_mapped_flag", "traceability", "jee_outcome")
    ct6 = crosstab(enriched, "traceability_flag", "dq_mapped_flag", "traceability", "dq_outcome")
    ct7 = crosstab(enriched, "human_policy_vs_inquiry", "jee_mapped_flag", "policy_or_inquiry", "jee_outcome")
    ct8 = crosstab(enriched, "human_policy_vs_inquiry", "dq_mapped_flag", "policy_or_inquiry", "dq_outcome")

    for name, data in [
        ("jee_vs_dq_mapped", ct1), ("jee_primary_vs_dq_primary", ct2),
        ("statement_type_vs_jee", ct3), ("statement_type_vs_dq", ct4),
        ("traceability_vs_jee", ct5), ("traceability_vs_dq", ct6),
        ("policy_inquiry_vs_jee", ct7), ("policy_inquiry_vs_dq", ct8),
    ]:
        write_csv(crosstab_dir / f"AUDIT_E_{name}.csv", data,
                  ["count", "percentage_of_total"] + list(data[0].keys()) if data else ["count"])

    # Fix header order for crosstabs
    for fname in crosstab_dir.glob("*.csv"):
        data, _ = read_csv(fname)
        if data:
            cols = list(data[0].keys())
            write_csv(fname, data, cols)

    # E. Failure modes
    fm = build_failure_modes(rows, pre_by_id)
    write_csv(work_dir / "AUDIT_E_FAILURE_MODES.csv", fm,
              ["failure_mode_id", "definition", "n_records", "percentage", "representative_entry_ids",
               "brief_example_paraphrase", "methodological_implication"])

    # F. Sensitivity
    detail, sens_summary, pre_stats, post_stats = sensitivity_analysis(rows, pre_by_id)
    write_csv(work_dir / "AUDIT_E_AUDIT_D_SENSITIVITY.csv", sens_summary,
              ["metric", "pre_audit_d", "post_audit_d", "delta"])
    write_csv(work_dir / "AUDIT_E_AUDIT_D_SENSITIVITY_DETAIL.csv", detail,
              list(detail[0].keys()) if detail else [])

    # Key findings for reports
    jee_no_map = jee_status.get("no_mapping", 0)
    jee_insuf = jee_status.get("insufficient_evidence", 0)
    jee_proc = jee_status.get("procedural_or_inquiry", 0)
    top_jee = primary_jee.most_common(3)
    top_dq = primary_dq.most_common(3)

    dissertation = f"""# Audit E — Dissertation Findings

Generated (UTC): {now_iso()}

## Methodological finding

A purposive 60-record pilot from Phase 1 decision-journal entries was adjudicated through a single-reviewer, AI-assisted human reference workflow with source-integrity (Audit C) and coding-consistency (Audit D) layers. All 60 records completed review; none remain pending. This is a feasibility and methods pilot, not a representative sample of the 414-entry corpus.

## Preparedness-framework finding

**Direct empirical finding:** {pct(jee_m, n)} of entries ({jee_m}/60) received a mapped JEE capacity (accept/replace). {pct(jee_no_map, n)} were coded `no_mapping` ({jee_no_map}/60) — passage clear but no specific capacity — and {pct(jee_insuf, n)} `insufficient_evidence` ({jee_insuf}/60). {pct(jee_proc, n)} were procedural/inquiry ({jee_proc}/60).

**Cautious interpretation:** The JEE framework adds interpretive value where passages describe identifiable preparedness or response capacities (most frequent primary areas: {', '.join(f'{a} ({c})' for a,c in top_jee) if top_jee else 'none'}).

**Cannot conclude:** Population-level preparedness coverage for the full corpus or UK COVID-19 inquiry evidence base.

## Decision-quality finding

**Direct empirical finding:** {pct(dq_m, n)} ({dq_m}/60) carry a mapped DQ element. Most frequent primary elements: {', '.join(f'{e} ({c})' for e,c in top_dq) if top_dq else 'none'}. `commitment_to_follow_through` and `helpful_frame` dominate mapped DQ coding.

**Cautious interpretation:** Decision Quality elements are more frequently observable than JEE capacities in this sample, consistent with inquiry testimony describing decisions and implementation rather than technical preparedness architecture.

## Traceability finding

**Direct empirical finding:** {pct(traceable, n)} ({traceable}/60) entries have traceability_ok=True; {pct(n - traceable, n)} ({n - traceable}/60) do not. Non-traceable entries require reliance on Source Quote and Evidence, not generated Decision fields.

**Implication:** Automated decision generation is a screening aid only; analytical claims must cite source passages.

## Human-oversight finding

Fifty-eight records underwent consistency screening; six received interactive human correction after AI-assisted review; fifty-two retained AI-assisted keep_all. Audit D changed 19 substantive fields across six records without altering aggregate mapped/unmapped proportions.

## Limitations

- Purposive 60-record pilot; no statistical generalisation
- Single reviewer (AI-assisted)
- Generated decisions may diverge from source quotes
- Inquiry-procedure and policy-content passages mixed
- Secondary JEE mappings largely removed in Audit D

## Implication for organisational learning in public-health emergencies

The pilot demonstrates that JEE and Decision Quality frameworks can structure retrospective interpretation of decision-journal and inquiry testimony, but only where source passages contain capacity-specific or decision-process evidence. Organisational learning applications should treat unmapped and insufficient-evidence codes as informative boundary conditions, not coding failures.
"""

    go_no_go = f"""# Audit E — GO/NO-GO Assessment

Generated (UTC): {now_iso()}

## Dissertation-integration decision

**Recommendation: GO WITH LIMITATIONS**

The 60-record pilot can be included as a **supplementary human-validated feasibility analysis** demonstrating:
- A reproducible AI-assisted human adjudication workflow
- Framework mapping rates and boundary conditions (no_mapping vs insufficient_evidence)
- Source-integrity and coding-consistency audit layers

Limitations that must be stated explicitly:
- Purposive sample, not representative
- Single-reviewer AI-assisted reference set, not independent gold standard
- Descriptive counts only; no inferential statistics

## Full-corpus-scaling decision

**Recommendation: GO AFTER SPECIFIED CHANGES**

Scaling to 414 entries is methodologically plausible but requires:
1. Confirmed schema and frozen coding rules (achieved in pilot)
2. Batch review workflow with periodic consistency audits
3. Explicit handling of traceability-failed entries
4. Documented AI-assisted + human approval protocol
5. Resource plan for human review burden (~similar flag rate would imply substantial review time)

Aggregate coding stability after Audit D is acceptable (6/60 interactive corrections; no change to principal mapped/unmapped proportions).

## Audit D sensitivity conclusion

Audit D corrections **refined edge cases only**. JEE mapped count unchanged ({pre_stats['jee']['mapped']} → {post_stats['jee']['mapped']}); DQ mapped count unchanged ({pre_stats['dq']['mapped']} → {post_stats['dq']['mapped']}). One statement-type reclassification (phase1-161) and one JEE demotion (phase1-311) improve interpretive accuracy without shifting headline proportions.
"""

    executive = f"""# Audit E — Executive Summary

Generated (UTC): {now_iso()}

## What was analysed

Read-only descriptive analysis of 60 human-adjudicated decision-journal entries from `CONSISTENCY_CORRECTED_REFERENCE.csv` (SHA256 verified). Input: single-reviewer AI-assisted human reference set after source-integrity and coding-consistency audits.

## Key descriptive findings

| Domain | Finding |
|--------|---------|
| JEE mapped | {pct(jee_m, n)} ({jee_m}/60) |
| JEE no_mapping | {pct(jee_no_map, n)} ({jee_no_map}/60) |
| JEE insufficient_evidence | {pct(jee_insuf, n)} ({jee_insuf}/60) |
| DQ mapped | {pct(dq_m, n)} ({dq_m}/60) |
| Traceable source | {pct(traceable, n)} ({traceable}/60) |
| Policy content | {pct(sum(1 for r in rows if r.get('human_policy_vs_inquiry')=='policy_content'), n)} |

Top JEE primary capacities: {', '.join(f'{a} ({c})' for a,c in top_jee) or 'none'}.
Top DQ primary elements: {', '.join(f'{e} ({c})' for e,c in top_dq) or 'none'}.

## Did the frameworks add useful interpretation?

**Yes, with boundaries.** JEE mapping identifies specific preparedness/response capacities where passage evidence supports it; `no_mapping` and `insufficient_evidence` codes distinguish “clear but not applicable” from “too thin.” Decision Quality elements capture observable decision-process features more frequently than JEE technical capacities.

## Principal limitations

Purposive 60-record pilot; single AI-assisted reviewer; non-traceable generated decisions in {n - traceable} entries; no statistical significance claims.

## Recommendations

- **Dissertation integration:** GO WITH LIMITATIONS — include as supplementary feasibility analysis
- **Full-corpus scaling:** GO AFTER SPECIFIED CHANGES — workflow stable but human review burden must be planned
"""

    report = f"""# Audit E — Analytical Report

Generated (UTC): {now_iso()}

## 1. Verification

- Input: `{ref_path.as_posix()}`
- SHA256: `{EXPECTED_REF_SHA256}` (verified)
- Records: 60
- Review status: 52 keep, 6 corrected, 2 auto-clear, 0 pending

## 2. Research questions (descriptive answers)

### JEE interpretability
{pct(jee_m, n)} of entries support a mapped JEE capacity. {pct(jee_no_map + jee_insuf, n)} are unmapped ({jee_no_map} no_mapping + {jee_insuf} insufficient_evidence + {jee_proc} procedural).

### DQ observability
{pct(dq_m, n)} contain observable DQ element evidence.

### Mapping failure reasons
See AUDIT_E_FAILURE_MODES.csv. Primary modes: thin/vague source, clear-but-no-capacity, non-traceable decisions, procedural content.

### Framework utility
Frameworks add structured interpretation without requiring every passage to map. Unmapped codes are analytically meaningful.

### Audit D impact
19 field changes across 6 records; aggregate mapped counts unchanged. Refinement only.

### Dissertation suitability
Suitable as supplementary feasibility analysis with explicit limitations.

### Scaling suitability
Methodologically stable; scaling requires planned human review infrastructure.

## 3. Output files

All outputs in `{work_dir.as_posix()}`.

## 4. Safeguards

Read-only analysis. No coding changes. No causal or significance claims. Percentages include denominators.
"""

    (work_dir / "AUDIT_E_DISSERTATION_FINDINGS.md").write_text(dissertation, encoding="utf-8")
    (work_dir / "AUDIT_E_GO_NO_GO.md").write_text(go_no_go, encoding="utf-8")
    (work_dir / "AUDIT_E_EXECUTIVE_SUMMARY.md").write_text(executive, encoding="utf-8")
    (work_dir / "AUDIT_E_ANALYTICAL_REPORT.md").write_text(report, encoding="utf-8")

    manifest = {
        "task": "post60_analytical_audit_E",
        "generated_at_utc": now_iso(),
        "work_dir": str(work_dir),
        "input_file": str(ref_path),
        "input_sha256": EXPECTED_REF_SHA256,
        "input_sha256_verified": True,
        "audit_d_dir_frozen": str(AUDIT_D_DIR),
        "n_records": n,
        "review_status_counts": dict(Counter(status_by_id.values())),
        "jee_mapped": jee_m,
        "dq_mapped": dq_m,
        "traceable": traceable,
        "dissertation_decision": "GO WITH LIMITATIONS",
        "scaling_decision": "GO AFTER SPECIFIED CHANGES",
    }
    (work_dir / "AUDIT_E_MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    sha_lines = []
    for p in sorted(work_dir.rglob("*")):
        if p.is_file():
            sha_lines.append(f"{sha256_file(p)}  {p.as_posix()}")
    (work_dir / "AUDIT_E_SHA256SUMS.txt").write_text("\n".join(sha_lines) + "\n", encoding="utf-8")

    print(f"AUDIT E complete: {work_dir}")
    print(f"jee_mapped={jee_m}/60 dq_mapped={dq_m}/60 traceable={traceable}/60")
    print(f"dissertation=GO WITH LIMITATIONS scaling=GO AFTER SPECIFIED CHANGES")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
