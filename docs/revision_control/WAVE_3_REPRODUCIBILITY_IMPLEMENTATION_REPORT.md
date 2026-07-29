# Wave 3 — Reproducibility Implementation Report

**Branch:** `distinction/final-integrity-fixes`  
**HEAD at implementation:** `ee02346b3f1e60704c59d08e891c2a4735fa1307` (Wave 2; no Wave 3 commit yet)  
**Status:** Implementation + validation complete. **Not committed. Not pushed.**

## Files created or changed

### Created — `docs/examiner_evidence/`

| File | Role |
| --- | --- |
| `README.md` | Five-minute examiner path |
| `ARTEFACT_MANIFEST.csv` | Master inventory |
| `DATA_LINEAGE.md` | Source→findings lineage |
| `REPRODUCTION_RUNBOOK.md` | Offline / download / API commands |
| `REPRODUCIBILITY_LIMITS.md` | Explicit non-claims |
| `EXAMINER_EVIDENCE_MAP.md` | Mandatory claim map |
| `COMMAND_REFERENCE.md` | Compact CLI list |
| `DEMO_CASE_SELECTION.md` | Four validated demos + rejects |
| `AUDIT_E_CANONICAL_LOCATOR.md` | Single authoritative path per n=60 claim |
| `SECURITY_AND_PRIVACY_NOTE.md` | Secrets / redaction |
| `SHA256SUMS` | Hash lock (generated) |

### Created — package + tooling

| Path | Role |
| --- | --- |
| `outputs/distinction_strategy/03_reproducibility_package/` | Generated package |
| `…/demos/phase1-{016,082,090,246}.json` | Minimal demo snapshots (no reviewer fields) |
| `…/demos/DEMO_CASE_INDEX.json` | Index |
| `…/validation/PACKAGE_VALIDATION_LOG.json` | Claim-check log |
| `…/PACKAGE_MANIFEST.json` | Package meta |
| `…/SHA256SUMS` | Same hash lock |
| `…/docs_copy/` | Mirror of examiner docs |
| `scripts/build_examiner_evidence_package.py` | Offline builder |
| `tests/test_examiner_evidence_package.py` | Package validation tests |
| `.gitignore` | Allow-list Wave 3 package + Audit E faithfulness/crosstab |

### Unchanged (verified)

- Dissertation markdown prose
- Frozen journal `814cc7c4…`
- Wave 2 DOCX `a829ff6d…` / PDF `40c123b9…`
- Annotation JSON; analytical eval JSON contents

## Audit E canonical-path resolution

| Claim | Authoritative path |
| --- | --- |
| JEE 11/60 | `AUDIT_E_JEE_SUMMARY.csv` (`mapped` = 11) |
| DQ 37/60 | `AUDIT_E_DQ_SUMMARY.csv` (count 37) |
| Combined 26/60 | `crosstabs/AUDIT_E_jee_vs_dq_mapped.csv` (unmapped×mapped=26) |
| Faithfulness 8/25/20/7 | `AUDIT_E_MANIFEST.json` → `traceability_category_counts` |

Precedence documented in `AUDIT_E_CANONICAL_LOCATOR.md`. Earlier Audit runs are aliases only.

## Untracked runs / PDFs

- Entire `outputs/run_*` and `data/raw|processed` trees **not** added to Git.
- Demo JSON records: public `pdf_url`, run_id, slug, hearing date, journal quote/decision, optional local run SHA if file present.
- Historical provenance only — claim verification uses frozen journal.

## Selected four demo cases

| Role | ID | Notes |
| --- | --- | --- |
| Yes × High | `phase1-016` | Confirmed |
| No × High wrong-artefact | `phase1-082` | Procedural adjournment |
| Materially unsupported | `phase1-090` | Preferred over `018` (counsel question vs asserted commission) |
| JEE/DQ | `phase1-246` | Preferred over `182` (clear P3 + commitment; exact/near-verbatim) |

Rejected with rationale: `018`, `182`, `124`, `252` — see `DEMO_CASE_SELECTION.md`.

## Test results

```
48 passed
```

- Prior 36 (Appendix A + flag/word + leak-term)
- +12 examiner package checks (paths, hashes, Audit E authority, demos, secrets, limits)

## Package path and SHA-256

**Directory:** `outputs/distinction_strategy/03_reproducibility_package/`

| File | SHA-256 |
| --- | --- |
| `SHA256SUMS` | `da8b9a5d838bfab26ddca55c9548fc8db80adb5b23c318eb1cfef2b80cf13cd8` |
| `PACKAGE_MANIFEST.json` | `5ed897cd2c9510dbe311f2c6ef73da919cfb6d44354e6fd178b169e68a58d7e0` |

Referenced journal / Wave 2 / Audit E hashes recorded inside `SHA256SUMS`.

## Security / privacy

- No `.env` / API key material in examiner docs or package (scan passed).
- Demo JSON omits `reviewer_name`.
- No private UKHSA tree references.
- No full raw/processed transcripts embedded.

## Unresolved gaps

| Severity | Gap |
| --- | --- |
| High | Phase 1 `outputs/run_*` remain untracked; examiners clone without local run trees (mitigated by frozen journal + local SHA notes) |
| Medium | Report-pilot authoritative numbers remain narrative (`docs/REPORT_PILOT.md`) unless local run is present |
| Medium | Embedding cache still untracked (expected) |
| Low | `requirements.txt` loose pins |
| Critical | **None** for offline inspection of mandatory dissertation counts |

## Confirmations

| Item | Status |
| --- | --- |
| Dissertation prose unchanged | Yes |
| DOCX/PDF unchanged | Yes |
| Analytical JSON/CSV/annotations/journal unchanged | Yes |
| External LLM API called | No |
| Commit / push | **No — awaiting approval** |
