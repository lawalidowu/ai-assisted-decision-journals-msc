# Audit E — Human Approval Check

Generated (UTC): 2026-07-27T13:19:20.288213+00:00

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
| Exact or near-verbatim | 8 | 13.3% (8/60) | phase1-246, phase1-252, phase1-326, phase1-380, phase1-298, phase1-316, phase1-114, phase1-407 |
| Substantively faithful paraphrase (traceable) | 25 | 41.7% (25/60) | phase1-124, phase1-111, phase1-217, phase1-276, phase1-003, phase1-375, phase1-048, phase1-204, phase1-209, phase1-366, phase1-079, phase1-182, phase1-142, phase1-281, phase1-285, phase1-362, phase1-405, phase1-295, phase1-082, phase1-112, phase1-113, phase1-310, phase1-116, phase1-128, phase1-307 |
| Materially unsupported/altered (traceable) | 20 | 33.3% (20/60) | phase1-018, phase1-050, phase1-057, phase1-321, phase1-020, phase1-053, phase1-378, phase1-166, phase1-198, phase1-207, phase1-106, phase1-090, phase1-311, phase1-312, phase1-185, phase1-059, phase1-169, phase1-033, phase1-042, phase1-084 |
| Traceability=False | 7 | 11.7% (7/60) | phase1-007, phase1-161, phase1-314, phase1-396, phase1-382, phase1-117, phase1-274 |

**Audit E string rule (for comparison):** 53/60 (88.3%) — **must not be cited as material divergence**.

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
