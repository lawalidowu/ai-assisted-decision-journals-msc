# Audit E — Revision Log

Generated (UTC): 2026-07-27T13:38:38.779881+00:00

## Superseded run

- **Original:** `outputs/framework_mapping/run_20260727_110052_post60_analytical_audit_E`
- **Reason superseded:** String-based 53/60 metric incorrectly described as substantive divergence from source passages
- **Human-approval gate:** `outputs/framework_mapping/run_20260727_131920_audit_E_human_approval_check`
- **Final frozen run:** `outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final`

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
