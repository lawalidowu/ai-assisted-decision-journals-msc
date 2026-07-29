# Wave 2 — Final Integrity Fixes: Implementation Report

**Status:** Implementation, rebuild, and validation complete. **Not committed. Not pushed.** Awaiting approval before Wave 2 commit.

## Branch and baseline

| Item | Value |
| --- | --- |
| Branch | `distinction/final-integrity-fixes` |
| Starting / HEAD parent commit | `72e9fc4e7b8d4979fb3de9a63a9e8350056aed28` |
| Annotated tag (untouched) | `baseline-wave6c-corrected-2026-07-28` |
| Remote baseline | `origin/main` (not updated) |

## Changed files (working tree relative to protected baseline)

| Path | Change |
| --- | --- |
| `dissertation/CHAPTER_4_RESULTS.md` | I-01 prose fix only |
| `tests/test_phase2a_flag_counts_and_wordcount.py` | **Added** — flag counts + overlap=0 + prose guard + word-field vs markdown match |
| `dissertation/Lawal_MSc_Dissertation.docx` | Regenerated (working output; typically untracked) |
| `docs/revision_control/WAVE_6C_COMPLETION_RECORD.md` | Supersession banner only (historical) |
| `docs/revision_control/WAVE_6B3_COMPLETION_RECORD.md` | Supersession banner only (historical) |
| `docs/revision_control/WAVE_6B2_COMPLETION_RECORD.md` | Supersession banner only (historical) |
| `docs/revision_control/WAVE_2_FINAL_INTEGRITY_FIXES_IMPLEMENTATION_REPORT.md` | This report |
| `outputs/.../run_20260729_153931_wave2_final_integrity_fixes/*` | **New** candidate package |
| `outputs/.../run_20260728_141045_wave6c_.../WORDCOUNT_HISTORY_SUPERSEDED.md` | **New** note only; FINAL binaries untouched |
| `scripts/_wave2_package_and_export.py` | Temporary packaging helper (untracked) |

Protected baseline package FINAL DOCX/PDF **not** overwritten.

## I-01 — before / after wording

**Before:**

> Non-destructive review flags were applied using the rules defined in Chapter 3 Section 3.6. In the fixed reference dataset, 36/414 entries were flagged: 4 procedural and 32 possible duplicate, with some entries carrying both flags. No rows were deleted. Flag counts mark review need and are not performance scores. Procedural flags also illustrate why journal validity and evidence strength must be rated separately: a hearing adjournment can be quote-supported while still failing the journal definition.

**After:**

> Non-destructive review flags were applied using the rules defined in Chapter 3 Section 3.6. In the fixed reference dataset, 36/414 entries were flagged: 4 procedural and 32 possible duplicate. No rows were deleted. Flag counts mark review need and are not performance scores. Procedural flags also illustrate why journal validity and evidence strength must be rated separately: a hearing adjournment can be quote-supported while still failing the journal definition.

Verified analytical counts unchanged: flagged=36, procedural=4, possible_duplicate=32, both=0.

## I-02 — every 14,551 / 14,564 occurrence disposition

| Location | Value | Classification | Disposition |
| --- | --- | --- | --- |
| Pre-rebuild `Lawal_MSc_Dissertation.docx` / wave6c FINAL (field) | 14,564 | (a)/(c) then historical | Confirmed **before** Wave 2 edit; superseded after rebuild |
| Wave 2 rebuilt DOCX/PDF + Wave 2 package QA/manifest | **14,558** | (a) active current | Updated / authoritative |
| `run_..._wave6c_.../FINAL_SUBMISSION_MANIFEST.json`, `SUBMISSION_PACKAGE_README.md`, `APPENDIX_A_COORDINATE_FIX_REBUILD.json` | 14,564 | (b) historical audit | Left unchanged; package note marks superseded |
| `run_..._wave6c_.../FINAL_FIELD_AND_NAVIGATION_CHECK.md`, `FINAL_VISUAL_QA.md`, `FINAL_CONTENT_AND_FORMAT_LOCK_CHECK.md`, `WAVE6C_RUNTIME_SUMMARY.json`, `_write_wave6c_artefacts.py` | 14,551 | (b) historical / stale QA | Left unchanged; `WORDCOUNT_HISTORY_SUPERSEDED.md` + revision_control banners |
| `docs/revision_control/WAVE_6C/B3/B2_COMPLETION_RECORD.md` | 14,551 | (b) historical | Banner added; numbers retained |
| Embedding cache float values / site-packages | incidental numeric substring | (d) obsolete / unrelated | No action |
| `tests/test_phase2a_flag_counts_and_wordcount.py` | asserts reject 14,551 in DOCX field | active gate | Keep |

**Build gate:** Markdown `count_dissertation_words()` = **14,558**; DOCX displayed field = **14,558**; **no discrepancy**.

## Tests added / modified

- **Added** `tests/test_phase2a_flag_counts_and_wordcount.py`
  - flagged=36, procedural=4, possible_duplicate=32, both=0
  - Chapter 4 prose must not claim overlapping flags when overlap=0
  - DOCX displayed words must match markdown count and must not show 14,551
- **Retained** all 21 Appendix A coordinate regression tests

## Test results

```
24 passed (21 Appendix A + 3 Wave 2 integrity)
```

## Unchanged analytical hashes

| Asset | SHA-256 | Status |
| --- | --- | --- |
| `data/manifests/phase1_decision_journal.json` | `814cc7c47a9f75bfc0a6c7b693feec7073e59131398d89fab7c9111fbb2e5e06` | unchanged |
| `configs/annotations/excerpts/excerpt_001.json` … `excerpt_006.json` | baseline manifests | all 6 unchanged |
| Fixed journal n | 414 | unchanged |
| Baseline wave6c FINAL DOCX | `d41f5991…7e59` | unchanged on disk |
| Baseline wave6c FINAL PDF | `e672f578…0e14` | unchanged on disk |

## New candidate package

**Directory:** `outputs/dissertation_integration/run_20260729_153931_wave2_final_integrity_fixes/`

| Artefact | SHA-256 |
| --- | --- |
| `Lawal_Akeeb_Idowu_MSc_Dissertation_FINAL.docx` | `a829ff6d0b4a778f2a276f9fff45af05dbc47fa268f3a9b0b131a87099b0a2e2` |
| `Lawal_Akeeb_Idowu_MSc_Dissertation_FINAL.pdf` | `40c123b9743277d9083d3b66eb855e0fa7a57101017d08a7d8a2d94558a63519` |

| Metric | Value |
| --- | --- |
| Physical PDF pages | 77 |
| Displayed pages | 77 |
| Displayed / markdown body words | **14,558** (match) |
| PDF size | ~1.195 MB (≤ 20 MB) |

## Visual inspection

- Chapter 4 §4.4 corrected paragraph present in DOCX; “both flags” absent.
- Appendix A source still contains COVID-O / disability context for `excerpt_002`; coordinate tests PASS.

## Unresolved warnings

- `build_submission_docx.py` still prints `WARNING - verify in Word: Joint External Evaluation` (pre-existing leak-term scan against literature/reference corpus; not introduced by Wave 2).

## Next step (awaiting approval)

Create Wave 2 commit on `distinction/final-integrity-fixes` only after explicit approval. Do **not** push until requested.
