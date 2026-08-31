# Final MSc pre-commit verification

**Date:** 2026-08-31  
**Branch:** `main` (HEAD `a42d935` — same as tag `final-submission-candidate-september-2026`)  
**Basis:** `README.md`, `docs/REPRODUCIBILITY_GUIDE.md`, `docs/repository_release/DUAL_RELEASE_AUDIT.md` Manifest A  
**Method:** Read-only filesystem and git inspection; offline pytest; no API calls; no experiments re-run; nothing staged or committed.

---

## Verdict

## **BLOCKED**

---

## Executive summary

All **required release artefacts are present on disk**, offline integrity tests **pass (48/48)**, the **frozen 414-entry journal is unchanged** (SHA-256 `814cc7c47a9f75bfc0a6c7b693feec7073e59131398d89fab7c9111fbb2e5e06`), and **gpt-5.6-sol full-hearing failure is correctly documented** as execution failure (not performance evidence).

However, the repository is **not ready to commit** as an MSc reproducibility release:

- **Nothing is staged** (`git diff --cached` empty).
- **114 of 130 Manifest A paths are not tracked**; **41 of those are blocked by `.gitignore`** (`data/processed/**`, bulk `outputs/**`).
- **Human-facing docs** (`docs/REPRODUCIBILITY_GUIDE.md`, `docs/ARCHITECTURE.md`, evaluation summaries) exist locally but are **not in git**.
- **`BASELINE_SHA256_MANIFEST.json` has not been updated** for new artefacts.
- **`.gitignore` must be amended** before processed transcripts, report-genre pilot, and full Audit E / gate directories can be tracked.

**No secrets, venvs, or private material are currently staged.** A blind `git add .` would be unsafe because ~176 untracked private/duplicate paths remain in the working tree.

---

## 1. Frozen 414-entry dataset

| Check | Result |
|-------|--------|
| File exists | Yes — `data/manifests/phase1_decision_journal.json` |
| Git modified? | No (`git status` clean for this path) |
| SHA-256 (working tree) | `814cc7c47a9f75bfc0a6c7b693feec7073e59131398d89fab7c9111fbb2e5e06` |
| SHA-256 in `BASELINE_SHA256_MANIFEST.json` | Matches (`426510` bytes) |
| Index blob == HEAD blob | Yes (`0a9b7f8963085a559b5326cbd801885427d5e574`) |
| Live counts (414 / 351 / 36 flags) | Confirmed via prior audit; integrity tests pass |

**Pass** — dataset unchanged and authoritative.

---

## 2. Aug 2026 sensitivity experiments (minimum evidence sets)

### 2.1 Chunk/overlap (`experiments/chunk_overlap_sensitivity_2026-08-30/`)

| Check | Result |
|-------|--------|
| Minimum protocol/reports/CSVs (17 files) | **Present** |
| `runs/stage1_w*.json` | **12/12 present** |
| `PROTOCOL_DEVIATIONS.md` | Present |
| Gitignored? | **No** (addable once `git add`) |
| Tracked? | **No** (0 files in git) |

### 2.2 Model sensitivity (`experiments/model_sensitivity_2026-08-31/`)

| Check | Result |
|-------|--------|
| Minimum reports/CSVs/scripts (27 paths) | **Present** |
| Terra full-hearing raw JSON | Present |
| Sol invalidated + incomplete JSON | Present (transparency artefacts) |
| Gitignored? | **No** |
| Tracked? | **No** |

**Pass on disk / Fail on trackability** — evidence exists but is not version-controlled.

---

## 3. Processed transcripts, Audit E, report-genre pilot

| Requirement | On disk | Tracked | Blocked by `.gitignore` |
|-------------|---------|---------|-------------------------|
| 8 hearing `.txt` under `data/processed/inquiry/document/` | Yes (8) | No | **Yes** (`data/processed/**`) |
| Report text `data/processed/inquiry/report/module-2-in-brief.txt` | Yes | No | **Yes** |
| Report-genre run `outputs/run_20260609_081454_module2_in_brief_report/` (3 JSON files) | Yes | No | **Yes** (`outputs/**`) |
| Audit E final (26 files) | Yes | **6/26** | **20/26 yes** |
| Audit E human-approval gate (8 files) | Yes | **0/8** | **8/8 yes** |
| `CONSISTENCY_CORRECTED_REFERENCE.csv` | Yes | Yes | No |

**Pass on disk / Fail on trackability** — `.gitignore` exceptions required per DUAL_RELEASE_AUDIT Manifest A items 5–8.

---

## 4. Dissertation results ↔ committed evidence

| Result (from reproducibility guide) | Artefact | On disk | Tracked |
|-------------------------------------|----------|---------|---------|
| 414 / 351 traceability | `phase1_decision_journal.json` | Yes | **Yes** |
| 36 review flags | embedded in journal | Yes | **Yes** |
| Six excerpts | `configs/annotations/*` | Yes | **Yes** |
| n=50 Rubric A/B | `confidence_validation_sample.json` | Yes | **Yes** |
| Confidence κ | `confidence_comparison_results.json` | Yes | **Yes** |
| Clustering (20) | `phase1_clustering_report.json` | Yes | **Yes** |
| Structural 49/50 | `structural_reliability_results.json` | Yes | **Yes** |
| GRACE / taxonomy | `grace_expansion.json`, `error_taxonomy_sample.json` | Yes | **Yes** |
| Triangulation / baseline / GRACE / error / report docs | `docs/*_SUMMARY.md`, `REPORT_PILOT.md` | Yes | **No** |
| n=60 JEE/DQ/faithfulness summaries | Audit E CSVs (partial) | Yes | **Partial** (3 summaries tracked; 20+ supporting files not) |
| Report-genre pilot run JSON | `outputs/run_20260609_081454_*` | Yes | **No** (ignored) |
| Chunk sensitivity | `experiments/chunk_overlap_sensitivity_2026-08-30/` | Yes | **No** |
| Model sensitivity + full-hearing | `experiments/model_sensitivity_2026-08-31/` | Yes | **No** |
| Final dissertation DOCX/PDF | `dissertation/Submission/final submission/` | Yes | **No** |
| Reproducibility / release docs | `docs/REPRODUCIBILITY_GUIDE.md`, `docs/repository_release/` | Yes | **No** |

**Fail** — supplementary and documentation artefacts cited in the dissertation are not yet committed.

---

## 5. gpt-5.6-sol full-hearing representation

| Check | Result |
|-------|--------|
| `17_FULL_HEARING_CONFIRMATION_REPORT.md` labels Sol as **INCOMPLETE — execution failure** | **Pass** |
| `18_FINAL_MODEL_SENSITIVITY_INTEGRATION_RECOMMENDATION.md` — **NOT INTERPRETABLE DUE TO EXECUTION FAILURE** | **Pass** |
| `POST_FULL_HEARING_SAFETY_CHECK.md` — invalid Sol excluded from recovery CSV | **Pass** |
| `15_FULL_HEARING_RUN_RESULTS.csv` contains **Terra row only** (no Sol performance row) | **Pass** |
| Invalid/incomplete Sol JSON preserved with explicit filenames | **Pass** |
| `docs/REPRODUCIBILITY_GUIDE.md` states Sol must not be cited as performance evidence | **Pass** |

**Pass** — scientific distinction is correctly represented.

---

## 6. Security / privacy / staging safety

| Item | Staged? | Gitignored? | Notes |
|------|---------|-------------|-------|
| `.env` | No | Yes | Present locally (150 B); must never be added |
| `.venv/` | No | Yes | Present locally |
| Meeting transcripts (`dissertation/Meeing 4.txt`, etc.) | No | No | Untracked — **exclude from `git add`** |
| Other students' work (`Jesutomiwa_Salam_*`, `Lohit_*`) | No | No | Untracked — **exclude** |
| `dissertation_Backup_270726_1828/` | No | Partial | Large venv pollution — **exclude** |
| Virtualenv under `dissertation/Lib/` | No | Yes | |

**Pass for current staging state** — nothing sensitive is staged. **Risk remains** if staging is done with `git add .` without path filters.

---

## 7. Human-facing documentation

| Check | Result |
|-------|--------|
| `README.md` uses plain-language navigation (no “wave” dependency) | **Pass** |
| `docs/REPRODUCIBILITY_GUIDE.md` — one incidental mention of `build_wave7a_final_freeze.py` as a script to **ignore** | Acceptable |
| Linked paths in README exist on disk | **Pass** (`docs/ARCHITECTURE.md`, `docs/REPRODUCIBILITY_GUIDE.md`, `docs/repository_release/DUAL_RELEASE_AUDIT.md`, `data/raw/README.md`, `docs/ANNOTATION_RUBRIC.md`) |
| Linked evaluation summaries exist on disk | **Pass** |
| Same linked docs **tracked in git** | **Fail** — `docs/ARCHITECTURE.md`, `docs/TRIANGULATION_SUMMARY.md`, `docs/BASELINE_KEYWORD.md`, `docs/GRACE_SUMMARY.md`, `docs/ERROR_TAXONOMY.md`, `docs/REPORT_PILOT.md`, `docs/INQUIRY_EXTRACTION_SUMMARY.md`, `docs/REPRODUCIBILITY_GUIDE.md` are **not** in git |
| Command examples reference real scripts | **Pass** (`scripts/run_extraction.py`, `build_phase1_journal.py`, `run_post60_analytical_audit_E_final.py`, experiment runners verified by AST parse) |

---

## 8. Automated checks (no API)

| Check | Result |
|-------|--------|
| `pytest tests/test_appendix_a_excerpt_coordinates.py tests/test_phase2a_flag_counts_and_wordcount.py tests/test_leak_term_scan.py tests/test_examiner_evidence_package.py` | **48 passed** |
| `import decision_journal.{extraction,journal,review_flags,clustering}` (with `PYTHONPATH=src`) | **Pass** |
| AST parse of key scripts | **Pass** |

---

## 9. Concrete blockers (only)

1. **No release files staged** — `git diff --cached` is empty; Manifest A has not been added.
2. **`.gitignore` blocks 41 required paths** — `data/processed/**` (9 transcripts), report-genre pilot (3 files), Audit E final (20 files), Audit E human-approval gate (8 files). Exceptions must be added before `git add -f` or policy update.
3. **73 addable but untracked release paths** — including both experiment minimum sets (39 + runs), final dissertation DOCX/PDF, human-facing docs, and release audit markdown.
4. **`BASELINE_SHA256_MANIFEST.json` not updated** for new tracked artefacts (required by audit Manifest A item 10).
5. **Evaluation summary markdown never committed** — `docs/ARCHITECTURE.md` and five `docs/*_SUMMARY.md` / pilot docs exist locally but are absent from git; README links to them.
6. **Modified dissertation chapters and README not staged** — 11 modified tracked files (including Aug sensitivity prose in Ch. 3–4) remain unstaged.

---

## 10. Exact files to commit (recommended staging set)

### 10.1 Modified tracked files (11)

```
README.md
dissertation/ABSTRACT.md
dissertation/CHAPTER_1_INTRODUCTION.md
dissertation/CHAPTER_2_LITERATURE.md
dissertation/CHAPTER_3_METHODS.md
dissertation/CHAPTER_4_RESULTS.md
dissertation/CHAPTER_5_DISCUSSION.md
docs/examiner_evidence/README.md
docs/examiner_evidence/REPRODUCTION_RUNBOOK.md
scripts/build_dissertation_docx.py
scripts/build_submission_docx.py
```

### 10.2 New documentation and release audit (16)

```
docs/REPRODUCIBILITY_GUIDE.md
docs/repository_release/DUAL_RELEASE_AUDIT.md
docs/repository_release/REPOSITORY_DEVELOPMENT_INVENTORY.md
docs/repository_release/FINAL_MSC_PRECOMMIT_VERIFICATION.md
docs/ARCHITECTURE.md
docs/TRIANGULATION_SUMMARY.md
docs/BASELINE_KEYWORD.md
docs/GRACE_SUMMARY.md
docs/ERROR_TAXONOMY.md
docs/REPORT_PILOT.md
docs/INQUIRY_EXTRACTION_SUMMARY.md
data/raw/README.md
docs/revision_control/CHUNK_SENSITIVITY_DOCX_INTEGRATION_2026-08-30.md
docs/revision_control/CHUNK_SENSITIVITY_DOCX_REPAIR_REPORT_2026-08-30.md
docs/revision_control/CHUNK_SENSITIVITY_INTEGRATION_FINAL_REPORT_2026-08-30.md
dissertation/Submission/final submission/Lawal_MSc_Dissertation_handbook_compliant.docx
dissertation/Submission/final submission/Lawal_MSc_Dissertation_handbook_compliant.pdf
```

### 10.3 Chunk sensitivity minimum set (29)

```
experiments/chunk_overlap_sensitivity_2026-08-30/00_PROTOCOL_PRE_REGISTERED.md
experiments/chunk_overlap_sensitivity_2026-08-30/01_STAGE1_CONFIGURATION_RESULTS.csv
experiments/chunk_overlap_sensitivity_2026-08-30/01_STAGE1_CONFIGURATION_RESULTS.md
experiments/chunk_overlap_sensitivity_2026-08-30/02_STABILITY_RESULTS.csv
experiments/chunk_overlap_sensitivity_2026-08-30/02_STABILITY_RESULTS.md
experiments/chunk_overlap_sensitivity_2026-08-30/03_CONFIRMATORY_RESULTS.csv
experiments/chunk_overlap_sensitivity_2026-08-30/03_CONFIRMATORY_RESULTS.md
experiments/chunk_overlap_sensitivity_2026-08-30/API_RUN_MANIFEST.csv
experiments/chunk_overlap_sensitivity_2026-08-30/BASELINE_MANIFEST.md
experiments/chunk_overlap_sensitivity_2026-08-30/BASELINE_SHA256_SNAPSHOT.txt
experiments/chunk_overlap_sensitivity_2026-08-30/FINAL_CHUNK_SENSITIVITY_REPORT.md
experiments/chunk_overlap_sensitivity_2026-08-30/GOLD_DECISION_ALIGNMENT.csv
experiments/chunk_overlap_sensitivity_2026-08-30/POST_EXPERIMENT_SAFETY_CHECK.md
experiments/chunk_overlap_sensitivity_2026-08-30/PROTOCOL_DEVIATIONS.md
experiments/chunk_overlap_sensitivity_2026-08-30/STAGE2_CONFIG_SELECTION.json
experiments/chunk_overlap_sensitivity_2026-08-30/finalize_experiment.py
experiments/chunk_overlap_sensitivity_2026-08-30/generate_reports.py
experiments/chunk_overlap_sensitivity_2026-08-30/run_experiment.py
experiments/chunk_overlap_sensitivity_2026-08-30/runs/stage1_w5_o1.json
experiments/chunk_overlap_sensitivity_2026-08-30/runs/stage1_w5_o2.json
experiments/chunk_overlap_sensitivity_2026-08-30/runs/stage1_w5_o3.json
experiments/chunk_overlap_sensitivity_2026-08-30/runs/stage1_w7_o1.json
experiments/chunk_overlap_sensitivity_2026-08-30/runs/stage1_w7_o2.json
experiments/chunk_overlap_sensitivity_2026-08-30/runs/stage1_w7_o3.json
experiments/chunk_overlap_sensitivity_2026-08-30/runs/stage1_w9_o1.json
experiments/chunk_overlap_sensitivity_2026-08-30/runs/stage1_w9_o2.json
experiments/chunk_overlap_sensitivity_2026-08-30/runs/stage1_w9_o3.json
experiments/chunk_overlap_sensitivity_2026-08-30/runs/stage1_w11_o1.json
experiments/chunk_overlap_sensitivity_2026-08-30/runs/stage1_w11_o2.json
experiments/chunk_overlap_sensitivity_2026-08-30/runs/stage1_w11_o3.json
```

### 10.4 Model sensitivity minimum set (27)

```
experiments/model_sensitivity_2026-08-31/00_PROTOCOL.md
experiments/model_sensitivity_2026-08-31/02_RUN_RESULTS.csv
experiments/model_sensitivity_2026-08-31/03_MODEL_SUMMARY.csv
experiments/model_sensitivity_2026-08-31/04_RAW_OUTPUT_MANIFEST.csv
experiments/model_sensitivity_2026-08-31/05_FINAL_MODEL_SENSITIVITY_REPORT.md
experiments/model_sensitivity_2026-08-31/07_PROTOCOL_AMENDMENT_CURRENT_MODELS.md
experiments/model_sensitivity_2026-08-31/08_CURRENT_MODEL_AVAILABILITY_PARITY.md
experiments/model_sensitivity_2026-08-31/09_EXTENDED_RUN_RESULTS.csv
experiments/model_sensitivity_2026-08-31/10_EXTENDED_MODEL_SUMMARY.csv
experiments/model_sensitivity_2026-08-31/11_EXTENDED_RAW_OUTPUT_MANIFEST.csv
experiments/model_sensitivity_2026-08-31/12_EXTENDED_MODEL_SENSITIVITY_REPORT.md
experiments/model_sensitivity_2026-08-31/14_FULL_HEARING_CONFIRMATION_PROTOCOL.md
experiments/model_sensitivity_2026-08-31/15_FULL_HEARING_RUN_RESULTS.csv
experiments/model_sensitivity_2026-08-31/16_FULL_HEARING_ALIGNMENT.csv
experiments/model_sensitivity_2026-08-31/17_FULL_HEARING_CONFIRMATION_REPORT.md
experiments/model_sensitivity_2026-08-31/18_FINAL_MODEL_SENSITIVITY_INTEGRATION_RECOMMENDATION.md
experiments/model_sensitivity_2026-08-31/POST_EXPERIMENT_SAFETY_CHECK.md
experiments/model_sensitivity_2026-08-31/POST_EXTENSION_SAFETY_CHECK.md
experiments/model_sensitivity_2026-08-31/POST_FULL_HEARING_SAFETY_CHECK.md
experiments/model_sensitivity_2026-08-31/run_experiment.py
experiments/model_sensitivity_2026-08-31/run_extension.py
experiments/model_sensitivity_2026-08-31/run_full_hearing_confirmation.py
experiments/model_sensitivity_2026-08-31/logs/extended_run_log.json
experiments/model_sensitivity_2026-08-31/logs/full_hearing_comparison.json
experiments/model_sensitivity_2026-08-31/raw_responses_full_hearing/gpt-5.6-terra/full_hearing_confirmation.json
experiments/model_sensitivity_2026-08-31/raw_responses_full_hearing/gpt-5.6-sol/full_hearing_confirmation_invalidated_run1.json
experiments/model_sensitivity_2026-08-31/raw_responses_full_hearing/gpt-5.6-sol/full_hearing_confirmation_retry1_INCOMPLETE.json
```

### 10.5 Requires `.gitignore` exceptions first (41)

```
data/processed/inquiry/document/transcript-of-module-2-public-hearing-on-28-november-2023.txt
data/processed/inquiry/document/transcript-of-module-2-public-hearing-on-30-november-2023.txt
data/processed/inquiry/document/transcript-of-module-2-public-hearing-on-01-december-2023.txt
data/processed/inquiry/document/transcript-of-module-2-public-hearing-on-07-december-2023.txt
data/processed/inquiry/document/transcript-of-module-2-public-hearing-on-11-december-2023.txt
data/processed/inquiry/document/transcript-of-module-2-public-hearing-on-13-december-2023.txt
data/processed/inquiry/document/transcript-of-module-2-public-hearing-on-14-december-2023.txt
data/processed/inquiry/document/transcript-of-module-2-public-hearing-on-23-may-2024.txt
data/processed/inquiry/report/module-2-in-brief.txt
outputs/run_20260609_081454_module2_in_brief_report/decisions.json
outputs/run_20260609_081454_module2_in_brief_report/manifest.json
outputs/run_20260609_081454_module2_in_brief_report/raw_llm_outputs.json
outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/AUDIT_E_ANALYTICAL_REPORT.md
outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/AUDIT_E_AUDIT_D_SENSITIVITY.csv
outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/AUDIT_E_AUDIT_D_SENSITIVITY_DETAIL.csv
outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/AUDIT_E_DATASET_PROFILE.csv
outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/AUDIT_E_DISSERTATION_FINDINGS.md
outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/AUDIT_E_FAILURE_MODES.csv
outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/AUDIT_E_GO_NO_GO.md
outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/AUDIT_E_JEE_DQ_CROSSTABS_INDEX.md
outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/AUDIT_E_REVIEW_PROVENANCE_NOTE.md
outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/AUDIT_E_REVISION_LOG.md
outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/AUDIT_E_SHA256SUMS.txt
outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/crosstabs/AUDIT_E_jee_primary_vs_dq_primary.csv
outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/crosstabs/AUDIT_E_policy_inquiry_vs_dq.csv
outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/crosstabs/AUDIT_E_policy_inquiry_vs_jee.csv
outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/crosstabs/AUDIT_E_statement_type_vs_dq.csv
outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/crosstabs/AUDIT_E_statement_type_vs_jee.csv
outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/crosstabs/AUDIT_E_traceability_category_vs_dq.csv
outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/crosstabs/AUDIT_E_traceability_category_vs_jee.csv
outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/crosstabs/AUDIT_E_traceability_vs_dq.csv
outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/crosstabs/AUDIT_E_traceability_vs_jee.csv
outputs/framework_mapping/run_20260727_131920_audit_E_human_approval_check/AUDIT_E_APPROVED_DISSERTATION_WORDING.md
outputs/framework_mapping/run_20260727_131920_audit_E_human_approval_check/AUDIT_E_DENOMINATOR_CHECK.csv
outputs/framework_mapping/run_20260727_131920_audit_E_human_approval_check/AUDIT_E_HUMAN_APPROVAL_CHECK.md
outputs/framework_mapping/run_20260727_131920_audit_E_human_approval_check/AUDIT_E_HUMAN_APPROVAL_MANIFEST.json
outputs/framework_mapping/run_20260727_131920_audit_E_human_approval_check/AUDIT_E_HUMAN_APPROVAL_SHA256SUMS.txt
outputs/framework_mapping/run_20260727_131920_audit_E_human_approval_check/AUDIT_E_REVIEW_PROVENANCE_CHECK.csv
outputs/framework_mapping/run_20260727_131920_audit_E_human_approval_check/AUDIT_E_REVIEW_PROVENANCE_SUMMARY.csv
outputs/framework_mapping/run_20260727_131920_audit_E_human_approval_check/AUDIT_E_TRACEABILITY_METRIC_CHECK.csv
```

### 10.6 Manifest update (1)

```
BASELINE_SHA256_MANIFEST.json   # regenerate after all paths above are staged
```

**Total intended new/modified paths:** ~131 (plus `.gitignore` amendment).

---

## 11. Exact files intentionally excluded

Do **not** stage:

```
.env
.venv/
venv/
dissertation/Lib/
dissertation/Include/
dissertation/Scripts/
dissertation/pyvenv.cfg
dissertation_Backup_270726_1828/
dissertation/Meeing 4.txt
dissertation/Meeting 3.md
dissertation/Meeting 4.md
Jesutomiwa_Salam_Msc_Dissertation.*
Lohit_Dissertation_Report.pdf
Official dissertation resources/
NLP Lectures/
historical docs/
docs/my writtings/
docs/review/ai and sustainability/
~$*.docx
*Copy.docx
Methodology_Results_v*.docx
outputs/language_edit/
outputs/distinction_strategy/   # optional July examiner bundles
experiments/**/raw_responses_extended/   # large API archives; CSV manifests suffice
experiments/**/repair_*.docx
experiments/**/integrate_dissertation_docx.py
data/manifests/phase1_embedding_cache.json   # hash-only policy
data/raw/inquiry/**   # optional; public PDFs recoverable via manifest URLs
```

---

## 12. Recommended commit message

```
Add MSc reproducibility release evidence, human-facing docs, and supplementary experiments.

Track handbook-compliant dissertation, Aug 2026 sensitivity minimum sets,
processed inquiry transcripts, full Audit E workspace, report-genre pilot run,
and reproducibility guide. Update .gitignore exceptions and baseline SHA manifest.
Frozen 414-entry journal unchanged (814cc7c4).
```

---

## 13. Recommended final tag name

```
msc-dissertation-reproducibility-2026-08-31
```

Apply **only after** staging §10 paths, updating `BASELINE_SHA256_MANIFEST.json`, and re-running offline pytest. Do **not** reuse `final-submission-candidate-september-2026` (July 77-page artefact without Aug supplementary evidence).

---

## 14. Pre-commit checklist (operator)

1. Amend `.gitignore` with Manifest A exceptions for `data/processed/inquiry/`, report-genre run, Audit E final + gate.
2. Stage paths in §10 using explicit path lists — **never** `git add .`.
3. Regenerate `BASELINE_SHA256_MANIFEST.json`.
4. Re-run: `python -m pytest tests/test_appendix_a_excerpt_coordinates.py tests/test_phase2a_flag_counts_and_wordcount.py tests/test_leak_term_scan.py tests/test_examiner_evidence_package.py -q`
5. Verify `git diff --cached` contains no `.env`, meeting transcripts, or other-student files.
6. Commit, then tag `msc-dissertation-reproducibility-2026-08-31`.

---

*End of verification report.*

**Report path:** `docs/repository_release/FINAL_MSC_PRECOMMIT_VERIFICATION.md`
