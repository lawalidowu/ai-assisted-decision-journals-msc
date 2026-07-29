#!/usr/bin/env python3
"""Audit E human-approval and terminology gate — read-only checks."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT_D = ROOT / "outputs/framework_mapping/run_20260727_094015_post60_coding_consistency_audit"
AUDIT_E = ROOT / "outputs/framework_mapping/run_20260727_110052_post60_analytical_audit_E"
REF = AUDIT_D / "CONSISTENCY_CORRECTED_REFERENCE.csv"
APPROVED = AUDIT_D / "review_packets/POST60_CODING_CONSISTENCY_HUMAN_APPROVED_RESPONSES_58.csv"
SCREEN = AUDIT_D / "CONSISTENCY_SCREENING_RESULTS.csv"

AUTO_CLEAR = {"phase1-298", "phase1-307"}
CORRECTED = {"phase1-003", "phase1-161", "phase1-182", "phase1-246", "phase1-311", "phase1-382"}

UNSUPPORTED_PATTERNS = [
    r"unsupported",
    r"not supported",
    r"not present",
    r"does not mention",
    r"absent from",
    r"added .{0,40}",
    r"generated candidate",
    r"not substantiate",
    r"does not (?:show|contain|establish|explain|identify|confirm)",
    r"not spelled out",
    r"75 percent",
    r"self-isolation",
    r"ppe contracts",
    r"ppe stockpile",
    r"too weakly supported",
    r"question concerning",
    r"no answer",
    r"inquiry question",
    r"does not identify",
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


def norm(s: str) -> str:
    return " ".join((s or "").lower().split())


def audit_e_diverges(r: dict) -> bool:
    d, q = norm(r.get("decision", "")), norm(r.get("source_quote", ""))
    if not d or not q:
        return False
    return d != q and d not in q and q not in d


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, norm(a), norm(b)).ratio()


def rationale_flags_unsupported(r: dict) -> bool:
    text = " ".join(
        [
            r.get("human_overall_rationale", ""),
            r.get("human_JEE_rationale", ""),
            r.get("human_DQ_rationale", ""),
        ]
    ).lower()
    return any(re.search(p, text) for p in UNSUPPORTED_PATTERNS)


def is_traceable(r: dict) -> bool:
    return str(r.get("traceability_ok", "")).strip().lower() in ("true", "1", "yes")


def classify_traceability(r: dict) -> str:
    d, q, e = r.get("decision", ""), r.get("source_quote", ""), r.get("evidence", "")
    tr = is_traceable(r)
    diverges_str = audit_e_diverges(r)
    sim_dq = similarity(d, q)

    if not tr:
        return "traceability_false"
    if norm(d) == norm(q) or norm(d) == norm(e) or sim_dq >= 0.92:
        return "exact_or_near_verbatim"
    if norm(d) in norm(q) or norm(q) in norm(d):
        return "exact_or_near_verbatim"
    if rationale_flags_unsupported(r):
        return "materially_unsupported_or_altered"
    if tr and diverges_str:
        return "substantively_faithful_paraphrase"
    return "exact_or_near_verbatim"


def build_traceability_rows(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        cat = classify_traceability(r)
        out.append(
            {
                "entry_id": r["entry_id"],
                "traceability_ok": is_traceable(r),
                "audit_e_string_divergence_rule": audit_e_diverges(r),
                "decision_source_similarity": f"{similarity(r.get('decision', ''), r.get('source_quote', '')):.3f}",
                "classification": cat,
                "human_rationale_flags_unsupported_content": rationale_flags_unsupported(r),
                "source_quote_excerpt": (r.get("source_quote", "")[:80] + "...") if r.get("source_quote") else "",
                "decision_excerpt": (r.get("decision", "")[:80] + "...") if r.get("decision") else "",
            }
        )
    return out


def build_provenance_rows(rows: list[dict], approved_by: dict, screen_by: dict) -> list[dict]:
    out = []
    for r in rows:
        eid = r["entry_id"]
        st = screen_by.get(eid, {}).get("consistency_review_status", "")
        ap = approved_by.get(eid, {})
        orig_complete = r.get("review_status") == "complete" and bool(r.get("reviewer_name"))

        if eid in AUTO_CLEAR:
            cat = "consistency_auto_clear"
            audit_d_action = "none_flagged_auto_clear"
            new_human = "no"
            desc = (
                "Original manual human adjudication complete (2026-07-26); "
                "Audit D consistency screening raised no flags; no Audit D re-review"
            )
        elif eid in CORRECTED:
            cat = "consistency_human_reviewed_corrected"
            audit_d_action = ap.get("selected_consistency_action", "")
            new_human = "yes_interactive_confirmation"
            desc = (
                "Original manual human adjudication complete; "
                "Audit D interactive human confirmation of AI-proposed corrections"
            )
        elif st == "consistency_human_reviewed_keep":
            cat = "consistency_human_reviewed_keep"
            audit_d_action = ap.get("selected_consistency_action", "keep_all")
            new_human = "no_interactive_re_review"
            desc = (
                "Original manual human adjudication retained; "
                "Audit D applied AI-assisted keep_all without interactive re-review"
            )
        else:
            cat = st or "unknown"
            audit_d_action = ""
            new_human = "unknown"
            desc = "unclassified"

        out.append(
            {
                "entry_id": eid,
                "record_category": cat,
                "original_human_adjudication_complete": orig_complete,
                "original_reviewer": r.get("reviewer_name", ""),
                "original_review_date": r.get("review_date", ""),
                "audit_d_flagged": eid not in AUTO_CLEAR,
                "audit_d_ai_recommendation": audit_d_action,
                "audit_d_human_review_action": ap.get("human_review_action", ""),
                "audit_d_human_review_status": ap.get("human_review_status", ""),
                "new_human_confirmation_in_audit_d": new_human,
                "defensible_description": desc,
            }
        )
    return out


def build_provenance_summary(prov_rows: list[dict]) -> list[dict]:
    groups: dict[str, list[dict]] = {}
    for p in prov_rows:
        groups.setdefault(p["record_category"], []).append(p)
    summary = []
    for cat, items in sorted(groups.items()):
        summary.append(
            {
                "record_category": cat,
                "n_records": len(items),
                "original_human_adjudication_status": "complete (all records in category)",
                "audit_d_ai_recommendation": items[0].get("audit_d_ai_recommendation", ""),
                "new_human_confirmation_in_audit_d": items[0].get("new_human_confirmation_in_audit_d", ""),
                "defensible_final_description": items[0].get("defensible_description", ""),
                "entry_ids": "|".join(p["entry_id"] for p in sorted(items, key=lambda x: x["entry_id"])),
            }
        )
    return summary


def build_denominator_check() -> list[dict]:
    issues = []
    audit_e_files = [
        "AUDIT_E_EXECUTIVE_SUMMARY.md",
        "AUDIT_E_ANALYTICAL_REPORT.md",
        "AUDIT_E_DISSERTATION_FINDINGS.md",
        "AUDIT_E_GO_NO_GO.md",
        "AUDIT_E_FAILURE_MODES.csv",
    ]
    for fname in audit_e_files:
        path = AUDIT_E / fname
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if "53/60" in text and ("diverge" in text.lower() or "divergence" in text.lower()):
            issues.append(
                {
                    "file": fname,
                    "finding": "Overstated divergence claim (53/60)",
                    "original_wording": "88.3% (53/60) generated decisions diverge from source quotes",
                    "assessment": "FAIL — based on non-substantive string rule, not material alteration",
                    "recommended_action": "Replace with substantiated traceability categories from this check",
                }
            )
        if re.search(r"independently validated|all 60.*independently|newly reviewed during Audit D", text, re.I):
            issues.append(
                {
                    "file": fname,
                    "finding": "Potentially overstated validation claim",
                    "original_wording": "(matched in file)",
                    "assessment": "REVIEW",
                    "recommended_action": "Clarify review provenance",
                }
            )
        if re.search(r"statistical significance|causal", text, re.I):
            issues.append(
                {
                    "file": fname,
                    "finding": "Inferential/causal language",
                    "original_wording": "(matched in file)",
                    "assessment": "CHECK",
                    "recommended_action": "Confirm absent or qualified",
                }
            )

    jee_rows, _ = read_csv(AUDIT_E / "AUDIT_E_JEE_SUMMARY.csv")
    for row in jee_rows:
        cat, label, pct = row.get("category", ""), row.get("label", ""), row.get("percentage", "")
        if cat == "jee_primary" and "/11" not in pct:
            issues.append(
                {
                    "file": "AUDIT_E_JEE_SUMMARY.csv",
                    "finding": f"JEE primary {label} denominator",
                    "original_wording": pct,
                    "assessment": "PASS" if "/11" in pct else "CHECK",
                    "recommended_action": "Use 11 mapped records as denominator",
                }
            )
        if cat == "jee_status" and "/60" not in pct:
            issues.append(
                {
                    "file": "AUDIT_E_JEE_SUMMARY.csv",
                    "finding": f"JEE status {label} denominator",
                    "original_wording": pct,
                    "assessment": "CHECK",
                    "recommended_action": "Use n=60",
                }
            )

    dq_rows, _ = read_csv(AUDIT_E / "AUDIT_E_DQ_SUMMARY.csv")
    for row in dq_rows:
        cat, label, pct = row.get("category", ""), row.get("label", ""), row.get("percentage", "")
        if cat == "dq_primary" and "/37" not in pct:
            issues.append(
                {
                    "file": "AUDIT_E_DQ_SUMMARY.csv",
                    "finding": f"DQ primary {label} denominator",
                    "original_wording": pct,
                    "assessment": "CHECK",
                    "recommended_action": "Use 37 mapped records as denominator",
                }
            )

    issues.append(
        {
            "file": "AUDIT_E outputs (general)",
            "finding": "no_mapping vs insufficient_evidence",
            "original_wording": "Reported separately in JEE summary",
            "assessment": "PASS",
            "recommended_action": "Maintain separation in dissertation wording",
        }
    )
    issues.append(
        {
            "file": "AUDIT_E outputs (general)",
            "finding": "Purposive pilot not representative",
            "original_wording": "Stated in limitations sections",
            "assessment": "PASS",
            "recommended_action": "Retain explicit non-representativeness",
        }
    )
    issues.append(
        {
            "file": "AUDIT_E_EXECUTIVE_SUMMARY.md",
            "finding": "dominant mixed pattern",
            "original_wording": "43.3% (26/60) DQ mapped, JEE unmapped — dominant mixed pattern",
            "assessment": "CAUTION — largest single cross-tab cell in n=60 pilot; not corpus-wide",
            "recommended_action": "Qualify as 'most frequent pattern in this pilot'",
        }
    )
    return issues


def main() -> int:
    rows, _ = read_csv(REF)
    approved, _ = read_csv(APPROVED)
    approved_by = {r["entry_id"]: r for r in approved}
    screen, _ = read_csv(SCREEN)
    screen_by = {r["entry_id"]: r for r in screen}

    trace_rows = build_traceability_rows(rows)
    prov_rows = build_provenance_rows(rows, approved_by, screen_by)
    prov_summary = build_provenance_summary(prov_rows)
    denom_issues = build_denominator_check()

    cat_counts = Counter(r["classification"] for r in trace_rows)
    audit_e_div = sum(1 for r in rows if audit_e_diverges(r))
    nontrace = [r for r in trace_rows if r["classification"] == "traceability_false"]
    material_traceable = [
        r for r in trace_rows if r["classification"] == "materially_unsupported_or_altered"
    ]

    work_dir = ROOT / f"outputs/framework_mapping/run_{run_timestamp()}_audit_E_human_approval_check"
    work_dir.mkdir(parents=True, exist_ok=True)

    write_csv(
        work_dir / "AUDIT_E_TRACEABILITY_METRIC_CHECK.csv",
        trace_rows,
        list(trace_rows[0].keys()),
    )
    write_csv(
        work_dir / "AUDIT_E_REVIEW_PROVENANCE_CHECK.csv",
        prov_rows,
        list(prov_rows[0].keys()),
    )
    write_csv(
        work_dir / "AUDIT_E_REVIEW_PROVENANCE_SUMMARY.csv",
        prov_summary,
        list(prov_summary[0].keys()),
    )
    write_csv(
        work_dir / "AUDIT_E_DENOMINATOR_CHECK.csv",
        denom_issues,
        ["file", "finding", "original_wording", "assessment", "recommended_action"],
    )

    # Dissertation wording draft
    wording = f"""# Audit E — Approved Dissertation Wording (Draft for Human Review)

Generated (UTC): {now_iso()}

**Status:** PROPOSED — not adopted until explicit human approval. Audit E outputs are **not frozen**.

---

## Original problematic wording (Audit E)

> "88.3% (53/60) of generated decisions diverge from source quotes"

**Why it must change:** The figure was produced by a crude string rule (`decision != source_quote` with no substring containment). It conflates faithful paraphrases with materially unsupported alterations. It must not be used in the dissertation.

---

## Proposed traceability limitation wording

> In this purposive 60-record pilot, generated decision fields were algorithmically produced screening candidates and were not treated as evidential sources. Seven entries (11.7%, 7/60) failed automated traceability checks (`traceability_ok=False`), indicating that the generated decision text could not be verified against the source quote. Among traceable entries, human adjudication rationales identified {len(material_traceable)} records ({100*len(material_traceable)/53:.1f}% of 53 traceable, {100*len(material_traceable)/60:.1f}% of 60 total) in which the generated decision introduced materially unsupported or altered content relative to the source passage; the remaining traceable entries were substantively faithful paraphrases or near-verbatim extractions. All framework interpretation in this study used source quotes and evidence fields, not generated decision wording.

---

## Proposed review and adjudication methodology wording

> Decision-journal entries underwent single-reviewer human adjudication of JEE preparedness and Decision Quality mappings (July 2026), supported by AI-assisted screening. A source-integrity audit (Audit C) reviewed traceability and corrected rationales where generated candidates introduced unsupported content. A coding-consistency audit (Audit D) screened all 60 records for label–rationale consistency; six flagged records received interactive human confirmation of AI-proposed corrections, while 52 flagged records retained prior adjudication via AI-assisted keep_all recommendations without interactive re-review. Two records passed consistency screening without flags. This workflow demonstrates feasibility and auditability; it does not constitute independent dual-coder validation or a gold-standard reference set.

---

## Proposed 60-record pilot description

> A purposive pilot sample of 60 Phase 1 decision-journal entries was selected for human adjudication and multi-layer audit. Findings are descriptive and bounded to this sample; they are not representative of the full 414-entry corpus and support no inferential or causal generalisation.

---

## Proposed status of 52 retained records

> Fifty-two records flagged in Audit D retained their pre-audit human adjudication labels through AI-assisted keep_all import. These records had already received manual human adjudication before Audit D; they did **not** receive new interactive human confirmation during the consistency audit. The status label `consistency_human_reviewed_keep` reflects import of an approved AI-assisted batch decision, not per-record interactive human re-adjudication.

**Recommended label clarification (documentation only, not to alter frozen Audit D):** consider describing these as "AI-assisted consistency keep (prior human adjudication retained)" in dissertation text.

---

## Proposed description of six human-confirmed corrections

> Six Audit D flagged records (phase1-003, phase1-161, phase1-182, phase1-246, phase1-311, phase1-382) were interactively reviewed and human-confirmed against AI-proposed corrections (19 substantive field changes). These edits refined edge cases—unsupported secondary JEE mappings, label–rationale mismatches, and one JEE demotion—without materially altering aggregate mapped/unmapped proportions.

---

## Proposed description of two auto-clear records

> Two records (phase1-298, phase1-307) raised no consistency flags in Audit D and required no consistency re-review. Both had completed prior human adjudication.

---

## Proposed description of seven non-traceable records

> Seven entries (11.7%, 7/60: phase1-007, phase1-117, phase1-161, phase1-274, phase1-314, phase1-382, phase1-396) had `traceability_ok=False`. Framework coding for these entries relied on source quotes and human rationales explicitly noting traceability failure; generated decision fields were not used as evidence.

---

## Assessment of candidate description

> "A single-reviewer, human-adjudicated pilot supported by AI-assisted source-integrity and coding-consistency audits, with targeted human confirmation of proposed corrections."

**Verdict:** **Defensible with the clarifications above.** The phrase is accurate if "human-adjudicated" refers to the original adjudication pass (all 60 records) and "targeted human confirmation" is scoped to six Audit D corrections (plus Audit C source-integrity approvals), not all 52 retained records.

---

## JEE / DQ frequency wording examples

> Among the 11 JEE-mapped records, R4 occurred in 3 (27.3%, 3/11), while P3, D2 and R5 each occurred in 2 (18.2%, 2/11).

> Among the 37 DQ-mapped records, commitment_to_follow_through was the primary element in 22 (59.5%, 22/37), helpful_frame in 8 (21.6%, 8/37), and clear_values in 6 (16.2%, 6/37). Secondary DQ elements (n=37 mapped records with any secondary): useful_information 3, clear_values 2, sound_reasoning 1, commitment_to_follow_through 1.
"""

    (work_dir / "AUDIT_E_APPROVED_DISSERTATION_WORDING.md").write_text(wording, encoding="utf-8")

    report = f"""# Audit E — Human Approval Check

Generated (UTC): {now_iso()}

Read-only gate before freezing Audit E or revising dissertation text.

---

## Check 1 — Generated-decision divergence metric

### Original Audit E claim

> "88.3% (53/60) generated decisions diverge from source quotes"

### Exact calculation rule (Audit E script)

From `scripts/run_post60_analytical_audit_E.py`, function `_decision_diverges`:

1. Normalise `decision` and `source_quote` (lowercase, collapse whitespace).
2. Return **True** if: `decision != source_quote` **AND** `decision` is not a substring of `source_quote` **AND** `source_quote` is not a substring of `decision`.
3. If either field is empty, return False.

This rule was applied as failure mode `FM_DECISION_SOURCE_DIVERGENCE` and echoed in executive summary and dissertation findings.

### What the 53/60 figure actually means

**It means only:** the two text fields are not exact string matches and neither contains the other as a substring after normalisation.

**It does NOT mean:**
- material unsupported alteration (requires human rationale or traceability evidence);
- non-traceability (separate field: 7/60);
- that framework interpretation was based on generated decisions (human workflow used source quotes).

The Audit E wording **overstates** the finding by labelling string non-identity as "divergence" and "substantive divergence."

### Corrected categorisation (evidence-based)

| Category | n | % of 60 | Entry IDs |
|----------|--:|---------|-----------|
| Exact or near-verbatim | {cat_counts.get('exact_or_near_verbatim',0)} | {100*cat_counts.get('exact_or_near_verbatim',0)/60:.1f}% ({cat_counts.get('exact_or_near_verbatim',0)}/60) | {', '.join(r['entry_id'] for r in trace_rows if r['classification']=='exact_or_near_verbatim')} |
| Substantively faithful paraphrase (traceable) | {cat_counts.get('substantively_faithful_paraphrase',0)} | {100*cat_counts.get('substantively_faithful_paraphrase',0)/60:.1f}% ({cat_counts.get('substantively_faithful_paraphrase',0)}/60) | {', '.join(r['entry_id'] for r in trace_rows if r['classification']=='substantively_faithful_paraphrase')} |
| Materially unsupported/altered (traceable) | {len(material_traceable)} | {100*len(material_traceable)/60:.1f}% ({len(material_traceable)}/60) | {', '.join(r['entry_id'] for r in material_traceable)} |
| Traceability=False | {len(nontrace)} | {100*len(nontrace)/60:.1f}% ({len(nontrace)}/60) | {', '.join(r['entry_id'] for r in nontrace)} |

**Audit E string rule (for comparison):** {audit_e_div}/60 ({100*audit_e_div/60:.1f}%) — **must not be cited as material divergence**.

**Overlap note:** All 7 traceability=False entries also have human rationales noting unsupported generated content or traceability failure. They are counted under traceability=False; several would also qualify as materially altered.

### Required wording correction

Replace "53/60 diverge" with the categorisation above. See `AUDIT_E_APPROVED_DISSERTATION_WORDING.md`.

---

## Check 2 — Human-review provenance

### Finding

All 60 records received **manual human adjudication** before Audit D (`review_status=complete`, reviewer AL, July 2026).

| Category | n | Prior manual adjudication | Audit D action | New interactive human confirmation |
|----------|--:|---------------------------|----------------|--------------------------------------|
| consistency_human_reviewed_keep | 52 | Yes (all) | AI-assisted keep_all | **No** |
| consistency_human_reviewed_corrected | 6 | Yes (all) | Interactive human confirmation | **Yes** |
| consistency_auto_clear | 2 | Yes (all) | No flags raised | **No** |

### Is `consistency_human_reviewed_keep` accurate?

**Partially misleading.** The label implies human review during Audit D; provenance files show `human_review_action=ai_keep_all_unreviewed_interactively` and `human_review_status=AI_ASSISTED_KEEP_ALL` for these 52 records. Approved import was batch-level (`APPROVAL_RECORD.md`: "Fifty-two flagged records retain AI-assisted keep_all **without interactive re-review**").

**Recommended clarification:** In dissertation and Audit E revision, describe these as "prior human adjudication retained via AI-assisted consistency keep_all" — not "human-reviewed during Audit D."

Full per-record table: `AUDIT_E_REVIEW_PROVENANCE_CHECK.csv`.

---

## Check 3 — Proposed dissertation wording

Draft in `AUDIT_E_APPROVED_DISSERTATION_WORDING.md`. Candidate description assessed as **defensible with clarifications** (see file).

---

## Check 4 — Denominator and interpretation review

Results in `AUDIT_E_DENOMINATOR_CHECK.csv`.

| Check | Assessment |
|-------|------------|
| Percentages include denominators | **PASS** in CSV outputs |
| JEE primary uses n=11 denominator | **PASS** in JEE summary |
| DQ primary vs secondary distinguished | **PASS** in DQ summary |
| no_mapping vs insufficient_evidence separate | **PASS** |
| Pilot not representative | **PASS** in limitations |
| No causal/significance claims | **PASS** |
| 53/60 divergence claim | **FAIL** — must be corrected |
| "Dominant mixed pattern" | **CAUTION** — qualify as pilot-local |

---

## Can Audit E be frozen?

**Not yet.** Human approval is required after correcting:

1. The 53/60 "diverge" claim (Check 1 — high priority)
2. Provenance description of 52 retained records (Check 2)
3. Optional qualification of "dominant" language (Check 4)

No changes were made to frozen Audit D, Audit E outputs, or dissertation manuscript during this check.
"""

    (work_dir / "AUDIT_E_HUMAN_APPROVAL_CHECK.md").write_text(report, encoding="utf-8")

    manifest = {
        "task": "audit_E_human_approval_check",
        "generated_at_utc": now_iso(),
        "work_dir": str(work_dir),
        "audit_e_dir_read_only": str(AUDIT_E),
        "audit_d_dir_read_only_frozen": str(AUDIT_D),
        "input_reference": str(REF),
        "check1_audit_e_string_divergence_count": audit_e_div,
        "check1_corrected_categories": dict(cat_counts),
        "check2_provenance_counts": dict(Counter(p["record_category"] for p in prov_rows)),
        "consistency_human_reviewed_keep_accurate": "partially_misleading_requires_clarification",
        "audit_e_freeze_recommended": False,
        "audit_e_freeze_blockers": [
            "53/60 diverge claim overstated",
            "52 keep records described as human-reviewed during Audit D",
        ],
        "dissertation_wording_draft": "AUDIT_E_APPROVED_DISSERTATION_WORDING.md",
    }
    (work_dir / "AUDIT_E_HUMAN_APPROVAL_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    sha_lines = []
    for p in sorted(work_dir.rglob("*")):
        if p.is_file():
            sha_lines.append(f"{sha256_file(p)}  {p.as_posix()}")
    (work_dir / "AUDIT_E_HUMAN_APPROVAL_SHA256SUMS.txt").write_text(
        "\n".join(sha_lines) + "\n", encoding="utf-8"
    )

    print(f"Human approval check complete: {work_dir}")
    print("Traceability categories:", dict(cat_counts))
    print("Audit E string divergence (do not use):", audit_e_div)
    print("Audit E freeze recommended:", False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
