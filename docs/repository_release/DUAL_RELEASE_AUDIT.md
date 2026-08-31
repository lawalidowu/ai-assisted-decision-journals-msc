# Dual-Release Audit

**Project:** AI-assisted decision journaling (UK COVID-19 Inquiry MSc) + future Rapid Research / Ebola follow-on  
**Audit date:** 2026-08-31  
**Basis:** `docs/repository_release/REPOSITORY_DEVELOPMENT_INVENTORY.md` + read-only repository inspection  
**Constraint:** No repository files were modified during this audit (except creation of this report).

---

## Executive summary

| Release | Readiness | Primary blockers |
|---------|-----------|------------------|
| **A. MSc dissertation reproducibility** | **NOT_READY_FOR_RELEASE** | Aug 2026 sensitivity experiments untracked; final handbook-compliant dissertation not in git; source transcripts/PDFs and most extraction runs gitignored; `main` has unstaged chapter edits post-tag |
| **B. Ebola reusable code** | **Not applicable yet** | No separate codebase; generic pipeline modules identifiable for future fork |

The tag `final-submission-candidate-september-2026` (commit `a42d935`, 2026-07-30) does **not** contain the dissertation text now described in the handbook-compliant submission (67 pages / ~10,724 words with chunk+model sensitivity sections). It freezes a **77-page / 14,558-word** Wave 7A candidate **without** the Aug 2026 supplementary experiments.

---

# Part 1 — File/folder classification

Classification key: **MSC** = dissertation reproducibility release; **EBOLA** = future reusable-code release.

## 1.1 Core pipeline and library

| Path | Class | Purpose | Track | Supports claim | Reproducible | Ebola reuse | Public-safe | MSC action | Ebola action |
|------|-------|---------|-------|----------------|--------------|-------------|-------------|------------|--------------|
| `src/decision_journal/extraction.py` | **BOTH** | LLM chunk extraction, schema, traceability | Tracked | Yes | Yes (with API key) | Yes — core | Yes | Include | **COPY/ADAPT** |
| `src/decision_journal/pdf_text.py` | **EBOLA_REUSABLE_CORE** | PDF→text preprocessing | Tracked | Yes | Yes | Yes | Yes | Include | **COPY/ADAPT** |
| `src/decision_journal/inquiry_harvest.py` | **COVID_SPECIFIC_ONLY** | UK Inquiry API harvest | Tracked | Yes | Yes | No (domain-specific) | Yes | Include | Exclude |
| `src/decision_journal/inquiry_download.py` | **COVID_SPECIFIC_ONLY** | Inquiry PDF download | Tracked | Yes | Yes | Pattern only | Yes | Include | Replace with generic fetch |
| `src/decision_journal/inquiry_client.py` | **COVID_SPECIFIC_ONLY** | Inquiry API client | Tracked | Yes | Yes | No | Yes | Include | Exclude |
| `src/decision_journal/inquiry_batch_text.py` | **BOTH** | Batch text processing | Tracked | Yes | Yes | Yes | Yes | Include | **COPY/ADAPT** |
| `src/decision_journal/journal.py` | **BOTH** | Merge runs → canonical journal | Tracked | Yes | Yes | Yes | Yes | Include | **COPY/ADAPT** |
| `src/decision_journal/review_flags.py` | **BOTH** | Non-destructive review flags | Tracked | Yes | Yes | Yes | Yes | Include | **COPY/ADAPT** |
| `src/decision_journal/confidence_signals.py` | **BOTH** | Automated confidence heuristics | Tracked | Yes | Yes | Yes | Yes | Include | Optional adapt |
| `src/decision_journal/clustering.py` | **MSC_SUPPORTING_EVIDENCE** | Embedding + agglomerative clustering | Tracked | Yes | Yes (needs cache or re-embed) | Optional | Yes | Include | Defer |
| `src/decision_journal/structural_reliability.py` | **MSC_SUPPORTING_EVIDENCE** | Schema stress-test | Tracked | Yes | Yes | Optional | Yes | Include | Defer |
| `src/decision_journal/language_edit/*` | **COVID_SPECIFIC_ONLY** | Dissertation prose LLM editing | Tracked | No (writing) | N/A | No | Yes | Exclude from code release | Exclude |

## 1.2 Scripts — pipeline and evaluation

| Path | Class | Purpose | Track | MSC | Ebola |
|------|-------|---------|-------|-----|-------|
| `scripts/run_pipeline.py` | **COVID_SPECIFIC_ONLY** | Harvest/download/text | Tracked | Include | Replace ingestion |
| `scripts/run_extraction.py` | **BOTH** | Per-document extraction CLI | Tracked | Include | **COPY/ADAPT** |
| `scripts/build_phase1_journal.py` | **BOTH** | Build 414-entry journal | Tracked | Include | **COPY/ADAPT** |
| `scripts/verify_phase1_data.py` | **MSC_CORE_REQUIRED** | Journal integrity checks | Tracked | Include | Exclude |
| `scripts/apply_review_flags.py` | **BOTH** | Phase 2a flags | Tracked | Include | **COPY/ADAPT** |
| `scripts/build_confidence_validation_sample.py` | **MSC_CORE_REQUIRED** | n=50 sample construction | Tracked | Include | Exclude |
| `scripts/rate_confidence_sample.py` | **MSC_CORE_REQUIRED** | Human Rubric A/B rating | Tracked | Include | Exclude |
| `scripts/compare_confidence_signals.py` | **MSC_SUPPORTING_EVIDENCE** | κ vs Rubric B | Tracked | Include | Exclude |
| `scripts/classify_discourse.py` | **MSC_SUPPORTING_EVIDENCE** | Exploratory discourse tags | Tracked | Include | Exclude |
| `scripts/run_clustering.py` | **MSC_SUPPORTING_EVIDENCE** | 414-entry clustering | Tracked | Include | Exclude |
| `scripts/visualize_clustering.py` | **MSC_SUPPORTING_EVIDENCE** | Thesis figures | Tracked | Include | Exclude |
| `scripts/keyword_baseline.py` | **MSC_SUPPORTING_EVIDENCE** | Keyword baseline | Tracked | Include | Optional pattern |
| `scripts/build_error_taxonomy.py` | **MSC_SUPPORTING_EVIDENCE** | n=42 error taxonomy | Tracked | Include | Exclude |
| `scripts/summarize_grace.py` | **MSC_SUPPORTING_EVIDENCE** | GRACE scores | Tracked | Include | Exclude |
| `scripts/summarize_triangulation.py` | **MSC_SUPPORTING_EVIDENCE** | MATA triangulation | Tracked | Include | Exclude |
| `scripts/run_structural_reliability.py` | **MSC_SUPPORTING_EVIDENCE** | 49/50 structural test | Tracked | Include | Exclude |
| `scripts/build_annotation_excerpts.py` | **MSC_CORE_REQUIRED** | Six excerpt workbooks | Tracked | Include | Exclude |
| `scripts/run_jee_dq_human_review.py` | **MSC_SUPPORTING_EVIDENCE** | n=60 interactive review | Untracked | Track minimum | Exclude |
| `scripts/run_post60_analytical_audit_E_final.py` | **MSC_SUPPORTING_EVIDENCE** | Audit E aggregation | Tracked | Include + full outputs | Exclude |
| `scripts/build_dissertation_docx.py` | **GENERATED_OPTIONAL** | Word build | Modified | Include if used for final | Exclude |
| `scripts/build_wave7a_final_freeze.py` | **GENERATED_OPTIONAL** | July freeze packaging | Tracked | Historical only | Exclude |
| `scripts/_lot_fix_handbook_compliant.py` | **GENERATED_OPTIONAL** | LoT repair Aug 2026 | Untracked | Document | Exclude |

## 1.3 Configuration and frozen data

| Path | Class | Purpose | Track | MSC | Ebola |
|------|-------|---------|-------|-----|-------|
| `data/manifests/phase1_decision_journal.json` | **MSC_CORE_REQUIRED** | Frozen 414 candidates (351 traceable; 36 flagged in `phase2.review_flags`) | Tracked | **Must include** | **Exclude** |
| `data/manifests/phase1_clustering_report.json` | **MSC_SUPPORTING_EVIDENCE** | 20 clusters | Tracked | Include | Exclude |
| `data/manifests/inquiry_module2_phase1.csv` | **COVID_SPECIFIC_ONLY** | Corpus metadata (contains `C:/SURREY/...` paths) | Tracked | Include + sanitise note | Exclude |
| `configs/annotations/manual_phase1.json` | **MSC_CORE_REQUIRED** | Six-excerpt triangulation | Tracked | Include | Exclude |
| `configs/annotations/excerpts/excerpt_001–006.json` | **MSC_CORE_REQUIRED** | Bounded spans | Tracked | Include | Exclude |
| `configs/evaluation/confidence_validation_sample.json` | **MSC_CORE_REQUIRED** | n=50 Rubric A/B | Tracked | Include | Exclude |
| `configs/evaluation/confidence_comparison_results.json` | **MSC_SUPPORTING_EVIDENCE** | κ results | Tracked | Include | Exclude |
| `configs/evaluation/confidence_llm_cache.json` | **MSC_SUPPORTING_EVIDENCE** | LLM second-pass cache | Tracked | Include (API outputs) | Exclude |
| `configs/evaluation/error_taxonomy_sample.json` | **MSC_SUPPORTING_EVIDENCE** | n=42 taxonomy | Tracked | Include | Exclude |
| `configs/evaluation/grace_expansion.json` | **MSC_SUPPORTING_EVIDENCE** | GRACE item scores | Tracked | Include | Exclude |
| `configs/evaluation/structural_reliability_*.json` | **MSC_SUPPORTING_EVIDENCE** | Stress test | Tracked | Include | Exclude |
| `configs/phase1_journal_runs.json` | **MSC_CORE_REQUIRED** | Maps 8 runs → journal | Tracked | Include | Exclude |
| `configs/default.json`, `inquiry_corpus.json`, `inquiry_phase1_seeds.json` | **COVID_SPECIFIC_ONLY** | Inquiry seeds/settings | Tracked | Include | Exclude |
| `data/raw/inquiry/**` | **COVID_SPECIFIC_ONLY** | Source PDFs | Ignored | Track or manifest+URL | Exclude |
| `data/processed/inquiry/**` | **COVID_SPECIFIC_ONLY** | Extracted `.txt` | Ignored | Track or regenerate | Exclude |
| `data/manifests/phase1_embedding_cache.json` | **GENERATED_BUT_REQUIRED** | 16.5 MB embeddings | Ignored | Manifest hash only (per baseline) | Exclude |

## 1.4 Outputs and experiments

| Path | Class | Purpose | Track | MSC | Ebola |
|------|-------|---------|-------|-----|-------|
| `outputs/run_20260608_*`, `run_20260609_*` | **GENERATED_BUT_REQUIRED** | 11 Phase 1 extraction runs | Ignored | Track or document as optional if journal sufficient | Exclude |
| `outputs/run_20260609_081454_module2_in_brief_report` | **MSC_SUPPORTING_EVIDENCE** | Report-genre pilot (53 candidates) | Ignored | Track summary + run JSON | Exclude |
| `outputs/figures/*.png` | **MSC_SUPPORTING_EVIDENCE** | Thesis figures | Partial | Include | Exclude |
| `outputs/framework_mapping/run_20260727_133838_*` | **MSC_SUPPORTING_EVIDENCE** | Frozen Audit E (n=60) | Partial (6 files) | Track full directory | Exclude |
| `outputs/framework_mapping/run_20260727_094015_*` | **MSC_SUPPORTING_EVIDENCE** | Audit D corrected CSV | Partial | Track | Exclude |
| `outputs/dissertation_integration/run_20260730_*` | **GENERATED_OPTIONAL** | July Wave 7A DOCX/PDF | Partial | Superseded by handbook-compliant | Exclude |
| `dissertation/Submission/final submission/Lawal_MSc_Dissertation_handbook_compliant.docx` | **MSC_CORE_REQUIRED** | Final submitted dissertation | Untracked | **Must track or archive** | Exclude |
| `experiments/chunk_overlap_sensitivity_2026-08-30/` | **MSC_SUPPORTING_EVIDENCE** | Chunk sensitivity (Aug 2026) | Ignored | Track minimum audit set (Part 3) | Exclude |
| `experiments/model_sensitivity_2026-08-31/` | **MSC_SUPPORTING_EVIDENCE** | Model sensitivity (Aug 2026) | Ignored | Track minimum audit set (Part 3) | Exclude |
| `outputs/distinction_strategy/07_final_submission_freeze/` | **GENERATED_OPTIONAL** | July examiner bundle | Tracked | Optional reference | Exclude |

## 1.5 Exclusions and hazards

| Path | Class | Purpose | Track | MSC | Ebola |
|------|-------|---------|-------|-----|-------|
| `.env` | **SECRET_RISK** | API key (150 bytes, present) | Ignored | Never commit | Never commit |
| `.env.example` | **BOTH** | Placeholder | Tracked | Include | Include |
| `.venv/`, `dissertation/Lib/`, `dissertation_Backup_*/Lib/` | **LOCAL_ENVIRONMENT_ONLY** | Virtualenvs (~700 MB) | Ignored | Exclude | Exclude |
| `dissertation/Meeing 4.txt`, `Meeting 3.md`, `docs/SUPERVISOR_*` | **PRIVATE_OR_SENSITIVE** | Supervisor meetings | Untracked | Exclude | Exclude |
| `Jesutomiwa_Salam_*`, `Lohit_*`, `docs/review/ai and sustainability/` | **PRIVATE_OR_SENSITIVE** | Other students' work | Untracked | Exclude | Exclude |
| `dissertation_Backup_270726_1828/` | **OBSOLETE_OR_DUPLICATE** | July snapshot + venv | Untracked | Exclude | Exclude |
| `Official dissertation resources/Supervisor allocations/` | **PRIVATE_OR_SENSITIVE** | Staff names | Untracked | Exclude | Exclude |
| `Transcript0.txt`, `outputs/distinction_strategy/Final meeting_transcript.txt` | **PRIVATE_OR_SENSITIVE** | Planning / Ebola discussion | Untracked | Exclude | Exclude (requirements only) |
| `~$*.docx` | **OBSOLETE_OR_DUPLICATE** | Office lock files | Untracked | Delete locally | Exclude |
| `historical docs/`, `NLP Lectures/` | **OBSOLETE_OR_DUPLICATE** | Pre-project / coursework | Untracked | Exclude | Exclude |

---

# Part 2 — Trace dissertation claims to code and artefacts

Verified counts from live `phase1_decision_journal.json` (2026-08-31): **414 entries**, **351** `traceability_ok`, **36** with `phase2.review_flags` (4 procedural, 32 possible_duplicate).

| Dissertation result | Producing script(s) | Input data | Output artefact(s) | Manual / eval files | Committed? | Reproducible from proposed release? |
|---------------------|----------------------|------------|----------------------|---------------------|------------|-------------------------------------|
| **414 fixed candidates** | `build_phase1_journal.py` ← `run_extraction.py` × 8 | `configs/phase1_journal_runs.json`, processed transcripts | `data/manifests/phase1_decision_journal.json` | — | Journal yes; runs no | **Partial** — journal yes; rebuild needs runs + processed text |
| **351/414 traceability** | `run_extraction.py` (traceability in `extraction.py`) | Same | Field in journal | — | Journal yes | **Yes** from frozen journal; **partial** to recompute |
| **36 review flags** | `apply_review_flags.py` | Journal entries | `phase2.review_flags` in journal | — | Yes (embedded) | **Yes** — re-run script on journal |
| **Six excerpts / six manual decisions** | `build_annotation_excerpts.py` | Processed transcripts | `configs/annotations/manual_phase1.json`, `excerpt_*.json` | Author labels | Yes | **Yes** |
| **Triangulation 5/10/0** | `summarize_triangulation.py` | manual_phase1 + LLM outputs | `docs/TRIANGULATION_SUMMARY.md` | manual_phase1 | Summary doc not all tracked | **Yes** with scripts + annotations |
| **n=50 Rubric A/B (e.g. 21/50 no×high)** | `build_confidence_validation_sample.py`, `rate_confidence_sample.py` | Journal | `configs/evaluation/confidence_validation_sample.json` | Author ratings | Yes | **Yes** |
| **Automated confidence (κ 0.48 / 0.39)** | `compare_confidence_signals.py` | n=50 sample | `configs/evaluation/confidence_comparison_results.json`, `confidence_llm_cache.json` | Rubric B | Yes | **Yes** (re-run needs API for LLM pass) |
| **Clustering 20 groups / n=414** | `run_clustering.py`, `visualize_clustering.py` | Journal + embeddings | `data/manifests/phase1_clustering_report.json`, `outputs/figures/` | — | Report yes; cache no | **Partial** — without 16 MB cache, re-embed via API |
| **n=60 JEE/DQ (11/60 JEE; 37/60 DQ)** | `run_jee_dq_human_review.py` → audit chain | Purposive 60 from journal | `outputs/framework_mapping/run_20260727_133838_*/AUDIT_E_JEE_SUMMARY.csv`, `AUDIT_E_DQ_SUMMARY.csv` | Single reviewer | **Partial** (6 CSV/MD tracked) | **No** — full adjudication workspace gitignored |
| **Faithfulness (8/25/20/7 of 60)** | Audit E + human gate | Source passages | `AUDIT_E_TRACEABILITY_HUMAN_CLASSIFICATION.csv` | Author | Partial | **Partial** — summary CSV tracked; gate run not |
| **Keyword baseline 1/6 vs LLM 5/6** | `keyword_baseline.py` | Six excerpts | `docs/BASELINE_KEYWORD.md` | manual_phase1 | Doc tracked | **Yes** with scripts |
| **GRACE-adapted (n=16)** | `summarize_grace.py` | Triangulation items | `configs/evaluation/grace_expansion.json`, `docs/GRACE_SUMMARY.md` | Author scoring | Yes | **Yes** |
| **Structural stress 49/50** | `run_structural_reliability.py` | `structural_reliability_chunks.json` | `configs/evaluation/structural_reliability_results.json` | — | Yes | **Yes** (re-run needs API) |
| **Report-genre pilot 53 candidates, 50/53 traceable** | `run_extraction.py` (no `--inquiry`) | `module-2-in-brief` text | `outputs/run_20260609_081454_*`, `docs/REPORT_PILOT.md` | None | **No** (run ignored) | **No** — run JSON not committed |
| **Chunk/overlap sensitivity** | `experiments/chunk_overlap_sensitivity_2026-08-30/run_experiment.py` | Six excerpts | `FINAL_CHUNK_SENSITIVITY_REPORT.md`, CSVs | Gold alignment CSV | **No** | **No** — entire tree gitignored |
| **Model sensitivity (excerpt panel)** | `experiments/model_sensitivity_2026-08-31/run_experiment.py` | Six excerpts | `05_FINAL_MODEL_SENSITIVITY_REPORT.md`, `02–04` CSVs | Same | **No** | **No** |
| **Model sensitivity (GPT-5.6 extended)** | `run_extension.py` | Six excerpts | `12_EXTENDED_MODEL_SENSITIVITY_REPORT.md`, `09–11` CSVs | Same | **No** | **No** |
| **Full-hearing confirmation Terra 2/6** | `run_full_hearing_confirmation.py` | 3 full hearing `.txt` | `17_FULL_HEARING_CONFIRMATION_REPORT.md`, `15–16` CSVs, Terra raw JSON | Six decisions | **No** | **No** |
| **Full-hearing Sol** | Same (failed/incomplete) | Same | `*_invalidated_*`, `*_INCOMPLETE.json` | — | **No** | **Must not be used as evidence** |

### Claims with evidence gaps (flags)

1. **Report-genre pilot** — documented in `docs/REPORT_PILOT.md` but extraction run directory not committed.  
2. **n=60 JEE/DQ/faithfulness** — published summaries partially tracked; interactive review session and audit gate directories are not.  
3. **Aug 2026 sensitivity experiments** — cited in final handbook-compliant dissertation but **zero files** in git.  
4. **Final dissertation PDF/DOCX** — `Submission/final submission/Lawal_MSc_Dissertation_handbook_compliant.docx` is **untracked**; tag points to different July artefact.

---

# Part 3 — Audit of untracked sensitivity experiments

## 3.1 `experiments/chunk_overlap_sensitivity_2026-08-30/`

### Scientific status

| Category | Files |
|----------|-------|
| **Valid results** | `00_PROTOCOL_PRE_REGISTERED.md`, `01_STAGE1_CONFIGURATION_RESULTS.csv/.md`, `02_STABILITY_RESULTS.csv/.md`, `03_CONFIRMATORY_RESULTS.csv/.md`, `FINAL_CHUNK_SENSITIVITY_REPORT.md`, `GOLD_DECISION_ALIGNMENT.csv`, `STAGE2_CONFIG_SELECTION.json`, `API_RUN_MANIFEST.csv`, `BASELINE_MANIFEST.md`, `BASELINE_SHA256_SNAPSHOT.txt`, `POST_EXPERIMENT_SAFETY_CHECK.md`, `PROTOCOL_DEVIATIONS.md` (if any), `run_experiment.py`, `generate_reports.py`, `finalize_experiment.py` |
| **Supporting run JSON** | `runs/stage1_w{5,7,9,11}_o{1,2,3}.json` (12 files) — needed for audit trail |
| **Debug / integration artefacts (exclude from MSc minimum)** | `_chunk_repair_*.docx`, `_chunk_sensitivity_integration_work*.docx/pdf`, `integrate_dissertation_docx.py`, `repair_dissertation_docx*.py`, `_test_repair.docx`, `_results_bundle.json` (optional if reports sufficient) |
| **Invalidated / N/A** | None identified |

### Minimum audit-safe MSc set (chunk)

```
experiments/chunk_overlap_sensitivity_2026-08-30/
  00_PROTOCOL_PRE_REGISTERED.md
  01_STAGE1_CONFIGURATION_RESULTS.csv
  01_STAGE1_CONFIGURATION_RESULTS.md
  02_STABILITY_RESULTS.csv
  02_STABILITY_RESULTS.md
  03_CONFIRMATORY_RESULTS.csv
  03_CONFIRMATORY_RESULTS.md
  FINAL_CHUNK_SENSITIVITY_REPORT.md
  GOLD_DECISION_ALIGNMENT.csv
  STAGE2_CONFIG_SELECTION.json
  API_RUN_MANIFEST.csv
  BASELINE_MANIFEST.md
  BASELINE_SHA256_SNAPSHOT.txt
  POST_EXPERIMENT_SAFETY_CHECK.md
  PROTOCOL_DEVIATIONS.md
  run_experiment.py
  generate_reports.py
  finalize_experiment.py
  runs/stage1_w*.json
```

**Ebola release:** exclude entire directory.

---

## 3.2 `experiments/model_sensitivity_2026-08-31/`

### Scientific status

| Category | Files |
|----------|-------|
| **Valid excerpt-level results** | `00_PROTOCOL.md`, `02_RUN_RESULTS.csv`, `03_MODEL_SUMMARY.csv`, `04_RAW_OUTPUT_MANIFEST.csv`, `05_FINAL_MODEL_SENSITIVITY_REPORT.md`, `09_EXTENDED_RUN_RESULTS.csv`, `10_EXTENDED_MODEL_SUMMARY.csv`, `11_EXTENDED_RAW_OUTPUT_MANIFEST.csv`, `12_EXTENDED_MODEL_SENSITIVITY_REPORT.md`, `POST_EXPERIMENT_SAFETY_CHECK.md`, `POST_EXTENSION_SAFETY_CHECK.md`, `07_PROTOCOL_AMENDMENT_CURRENT_MODELS.md`, `08_CURRENT_MODEL_AVAILABILITY_PARITY.md` |
| **Valid full-hearing (Terra only)** | `14_FULL_HEARING_CONFIRMATION_PROTOCOL.md`, `15_FULL_HEARING_RUN_RESULTS.csv` (Terra rows only), `16_FULL_HEARING_ALIGNMENT.csv`, `17_FULL_HEARING_CONFIRMATION_REPORT.md`, `raw_responses_full_hearing/gpt-5.6-terra/full_hearing_confirmation.json`, `logs/full_hearing_comparison.json` |
| **INVALID — not performance evidence** | `raw_responses_full_hearing/gpt-5.6-sol/full_hearing_confirmation_invalidated_run1.json` |
| **INCOMPLETE — not performance evidence** | `raw_responses_full_hearing/gpt-5.6-sol/full_hearing_confirmation_retry1_INCOMPLETE.json`, `full_hearing_confirmation_retry1.json` (if partial) |
| **Raw API archives (optional for MSc)** | `raw_responses/` (gpt-4o-mini, gpt-4o), `raw_responses_extended/` (all models × 3 reps × 6 excerpts) — large; manifest CSVs may suffice |
| **Advisory only** | `06/13/18_*_INTEGRATION_RECOMMENDATION.md` |
| **Scripts** | `run_experiment.py`, `run_extension.py`, `run_full_hearing_confirmation.py` |

### Minimum audit-safe MSc set (model)

```
experiments/model_sensitivity_2026-08-31/
  00_PROTOCOL.md
  02_RUN_RESULTS.csv
  03_MODEL_SUMMARY.csv
  04_RAW_OUTPUT_MANIFEST.csv
  05_FINAL_MODEL_SENSITIVITY_REPORT.md
  07_PROTOCOL_AMENDMENT_CURRENT_MODELS.md
  08_CURRENT_MODEL_AVAILABILITY_PARITY.md
  09_EXTENDED_RUN_RESULTS.csv
  10_EXTENDED_MODEL_SUMMARY.csv
  11_EXTENDED_RAW_OUTPUT_MANIFEST.csv
  12_EXTENDED_MODEL_SENSITIVITY_REPORT.md
  14_FULL_HEARING_CONFIRMATION_PROTOCOL.md
  15_FULL_HEARING_RUN_RESULTS.csv
  16_FULL_HEARING_ALIGNMENT.csv
  17_FULL_HEARING_CONFIRMATION_REPORT.md
  18_FINAL_MODEL_SENSITIVITY_INTEGRATION_RECOMMENDATION.md
  POST_EXPERIMENT_SAFETY_CHECK.md
  POST_EXTENSION_SAFETY_CHECK.md
  POST_FULL_HEARING_SAFETY_CHECK.md
  run_experiment.py
  run_extension.py
  run_full_hearing_confirmation.py
  raw_responses_full_hearing/gpt-5.6-terra/full_hearing_confirmation.json
  logs/full_hearing_comparison.json
  logs/extended_run_log.json
```

**Include with clear INVALID/INCOMPLETE labels (transparency, not evidence):**

- `raw_responses_full_hearing/gpt-5.6-sol/full_hearing_confirmation_invalidated_run1.json`
- `raw_responses_full_hearing/gpt-5.6-sol/full_hearing_confirmation_retry1_INCOMPLETE.json`

**Exclude from MSc minimum:** full `raw_responses_extended/` tree unless examiner requests full API audit (use manifest CSV instead).

**Critical rule:** Dissertation text must cite **Terra 2/6** full-hearing result only; **never** Sol full-hearing recovery. Sol excerpt-level 4/6 remains bounded-excerpt evidence only.

---

# Part 4 — Security / privacy / shareability audit

| Item | Class | MSC handling | Ebola handling |
|------|-------|--------------|----------------|
| `.env` (OPENAI_API_KEY) | **SECRET_RISK** | `.gitignore`; release with `.env.example` only | Same |
| `.env.example` | Safe template | Include | Include |
| `configs/evaluation/confidence_llm_cache.json` | API output | Include (no secrets); document re-run | Exclude |
| `experiments/*/raw_responses*` | API archives | Minimum set or manifest only | Exclude |
| Hard-coded `C:\SURREY\...` in manifests | **PRIVATE_OR_SENSITIVE** | Sanitise in release docs; optional path-neutral re-export | Fix in Ebola fork |
| `data/manifests/inquiry_module2_phase1.csv` local paths | Portability risk | Document regeneration via `run_pipeline.py` | Exclude |
| Meeting transcripts (`dissertation/Meeing 4.txt`, etc.) | **PRIVATE_OR_SENSITIVE** | Exclude; keep `.gitignore` | Exclude |
| `docs/revision_control/Consolidated_Supervisor_Feedback_Register_Reconciled.xlsx` | **PRIVATE_OR_SENSITIVE** | Exclude from public repo | Exclude |
| Other students' dissertations (root + `docs/review/`) | **PRIVATE_OR_SENSITIVE** | Exclude; add `.gitignore` rule | Exclude |
| `Official dissertation resources/Supervisor allocations/` | Staff PII | Exclude | Exclude |
| `docs/my writtings/` | Personal | Exclude | Exclude |
| `dissertation/Lib/`, `.venv/` | **LOCAL_ENVIRONMENT_ONLY** | Exclude | Exclude |
| `~$*.docx` | Temp | Delete locally; ignore | Exclude |
| Viva mock scripts / rehearsal logs | Low sensitivity | Optional private retention | Exclude |
| `outputs/language_edit/run_*/llm/` | LLM prose edits | Exclude | Exclude |

**No secret values are recorded in this audit.** `.env` exists locally (150 bytes — consistent with `.env.example` size); treat as **present until verified absent from any tracked file** (secret-scan tests in `tests/test_*.py` support this).

---

# Part 5 — Path and portability audit

| Issue | Location | Classification | Action |
|-------|----------|----------------|--------|
| Absolute `C:\SURREY\MODULES\...` | `data/manifests/inquiry_module2_phase1.csv` | Document only (MSc); fix in Ebola | Regenerate manifest on clone |
| Absolute paths | `outputs/framework_mapping/*/AUDIT_E_MANIFEST.json`, `CONSISTENCY_*.json` | Document only | Paths are metadata; CSVs use relative refs |
| README setup example Windows path | `README.md` | Document only | Add POSIX example in release README |
| Implicit `ROOT = Path(__file__).parents[1]` | Most `scripts/` | No action | Standard pattern |
| Default model `gpt-4o-mini` | `extraction.py`, env | Document only | Moving API alias documented in dissertation |
| `gpt-5.6-terra/sol/luna` experiment IDs | Aug 2026 experiments | Document only | Ephemeral; report returned snapshot IDs |
| Missing `data/processed/` on clone | Rebuild chain | **Must fix before MSc release** | Track processed text OR document download+`run_pipeline.py` |
| Missing `outputs/run_*` on clone | Journal rebuild | Document only if journal frozen | Journal alone sufficient for Phase 2 claims |
| `phase1_embedding_cache.json` gitignored | Clustering re-run | Document only | Hash in `BASELINE_SHA256_MANIFEST.json`; re-embed documented |
| Audit E paths reference gitignored gate run | `AUDIT_E_TRACEABILITY_HUMAN_CLASSIFICATION.csv` | Document only | Gate CSV not committed |

---

# Part 6 — Proposed MSc release manifest

Frozen snapshot representing **what the final handbook-compliant dissertation actually used**, not a cleaned rewrite.

## 6.1 Core code

```
src/decision_journal/
  extraction.py, pdf_text.py, journal.py, review_flags.py,
  confidence_signals.py, clustering.py, structural_reliability.py,
  inquiry_harvest.py, inquiry_download.py, inquiry_client.py, inquiry_batch_text.py
scripts/
  run_pipeline.py, run_extraction.py, build_phase1_journal.py, verify_phase1_data.py,
  apply_review_flags.py, build_annotation_excerpts.py, summarize_triangulation.py,
  keyword_baseline.py, build_error_taxonomy.py, summarize_grace.py,
  build_confidence_validation_sample.py, rate_confidence_sample.py,
  compare_confidence_signals.py, classify_discourse.py,
  run_clustering.py, visualize_clustering.py, run_structural_reliability.py,
  build_figure33_pipeline.py, build_figure43_error_taxonomy.py, build_figure49_crosstab.py,
  build_conceptual_framework_figure.py, rebuild_appendix_a_excerpts.py
tests/
  test_phase2a_flag_counts_and_wordcount.py, test_appendix_a_excerpt_coordinates.py,
  (+ other evaluation integrity tests as applicable)
requirements.txt, .env.example, README.md
```

## 6.2 Configuration / prompts

```
configs/default.json, inquiry_corpus.json, inquiry_phase1_seeds.json, phase1_journal_runs.json
configs/annotations/** (manual_phase1 + six excerpts)
configs/evaluation/** (all frozen evaluation JSON except pristine backups optional)
```

## 6.3 Required derived data

```
data/manifests/phase1_decision_journal.json          # canonical 414
data/manifests/phase1_clustering_report.json
data/manifests/inquiry_module2_phase1.csv
data/processed/inquiry/document/*.txt                 # 8 hearings — TRACK or SHA256 manifest + public URLs
data/processed/inquiry/report/module-2-in-brief.txt   # report-genre pilot
```

Optional: `data/raw/inquiry/**/*.pdf` (public UK Inquiry documents — redistribution acceptable with URLs).

## 6.4 Manual annotations / evaluation

```
configs/annotations/manual_phase1.json
configs/annotations/excerpts/excerpt_001–006.json
configs/evaluation/confidence_validation_sample.json
outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/  # FULL directory
outputs/framework_mapping/run_20260727_094015_post60_coding_consistency_audit/CONSISTENCY_CORRECTED_REFERENCE.csv
```

## 6.5 Key result artefacts

```
configs/evaluation/confidence_comparison_results.json
configs/evaluation/structural_reliability_results.json
configs/evaluation/grace_expansion.json
configs/evaluation/error_taxonomy_sample.json
outputs/figures/conceptual_framework.png, phase1_cluster_sizes.png, phase1_cluster_composition.png
docs/TRIANGULATION_SUMMARY.md, BASELINE_KEYWORD.md, GRACE_SUMMARY.md, ERROR_TAXONOMY.md, REPORT_PILOT.md
outputs/run_20260609_081454_module2_in_brief_report/   # report-genre pilot JSON
```

## 6.6 Supplementary experiments (Aug 2026)

Minimum sets from **Part 3** for both experiment directories.

## 6.7 Documentation

```
docs/ARCHITECTURE.md, docs/LITERATURE_AND_SAMPLES_INDEX.md
docs/examiner_evidence/REPRODUCTION_RUNBOOK.md, REPRODUCIBILITY_LIMITS.md, SECURITY_AND_PRIVACY_NOTE.md
docs/revision_control/CHUNK_SENSITIVITY_*_2026-08-30.md (integration reports)
dissertation/CHAPTER_1–5.md, ABSTRACT.md, APPENDIX_A–C.md, REFERENCES.md  # post-Aug edits committed
dissertation/Submission/final submission/Lawal_MSc_Dissertation_handbook_compliant.docx
dissertation/Submission/final submission/Lawal_MSc_Dissertation_handbook_compliant.pdf  # if generated
BASELINE_SHA256_MANIFEST.json  # update to include new tracked files
docs/repository_release/REPOSITORY_DEVELOPMENT_INVENTORY.md
docs/repository_release/DUAL_RELEASE_AUDIT.md
```

## 6.8 Files to exclude from MSc release

```
.env, .venv/, dissertation/Lib/, dissertation_Backup_*/
~$*.docx, *Copy.docx, Methodology_Results_v*.docx
Official dissertation resources/, NLP Lectures/, historical docs/
Jesutomiwa_Salam_*, Lohit_*, docs/review/ai and sustainability/
docs/my writtings/, meeting transcripts, supervisor xlsx/csv
outputs/language_edit/, outputs/dissertation_integration/ (except pointer README)
outputs/distinction_strategy/ (optional; July bundle superseded)
src/decision_journal/language_edit/ (dissertation prose tooling)
scripts/build_wave7a_*, generate_viva_*, presentation_*, covid_deck_*
```

---

# Part 7 — Proposed Ebola reusable-code manifest

Smallest foundation for a **new repository** (not a copy of this repo).

## 7.1 COPY/ADAPT

| Module | Rationale |
|--------|-----------|
| `src/decision_journal/pdf_text.py` | Generic document text extraction |
| `src/decision_journal/extraction.py` | Chunked LLM extraction + schema + traceability (parameterise prompts) |
| `src/decision_journal/journal.py` | Stable-ID journal merge/dedup |
| `src/decision_journal/review_flags.py` | Deterministic review flags |
| `src/decision_journal/confidence_signals.py` | Optional review aids |
| `src/decision_journal/inquiry_batch_text.py` | Batch processing patterns |
| Thin CLI wrappers patterned on `run_extraction.py`, `apply_review_flags.py` | |
| `requirements.txt`, `.env.example` pattern | |
| Generic config schema (new `configs/default.json` without inquiry seeds) | |

## 7.2 Do not carry over by default

| Item | Reason |
|------|--------|
| `data/manifests/phase1_decision_journal.json` | COVID Inquiry frozen research output |
| All `configs/inquiry_*`, `configs/annotations/*`, `configs/evaluation/*` | Dissertation-specific labels and n=50/n=60 |
| `outputs/**`, `experiments/**` | COVID evidence |
| `dissertation/**`, `docs/viva/**`, `docs/revision_control/**` | Dissertation prose and governance |
| JEE/DQ mapping scripts and Audit A–E chain | Framework pilot specific to MSc |
| `clustering.py` + COVID thematic labels | Navigation aid tied to 414 COVID candidates |
| Meeting transcripts / Ebola planning notes | Requirements input only, not code |
| Sensitivity experiment results | MSc supplementary only |

## 7.3 Ebola repo bootstrap (future)

1. New corpus ingestion interface (outbreak transcripts / sitreps — format TBD).  
2. New prompt/schema config (no COVID Inquiry wording).  
3. New evaluation harness (not JEE/DQ).  
4. Read `docs/revision_control/DEFERRED_LIMITATIONS_FUTURE_WORK_REVISIONS.md` for genre-transfer notes only.

---

# Part 8 — Git state recommendation

| Question | Finding |
|----------|---------|
| Does `final-submission-candidate-september-2026` contain all evidence in the **final** dissertation? | **No.** Tag is commit `a42d935` (2026-07-30): 77-page Wave 7A DOCX/PDF. Final handbook-compliant version (67 pp, chunk+model sensitivity in Ch. 3–4) is **untracked** and post-dates tag. |
| What must become tracked for a true final MSc snapshot? | See **Manifest A** below + unstaged `CHAPTER_3/4` edits + both `experiments/` minimum sets + `dissertation/Submission/final submission/*` + `data/processed/**` (or manifest) + full Audit E directory + report-genre run |
| Is `main` the right base? | **Yes**, after committing missing evidence. Do not tag current dirty tree without reconciling chapter markdown ↔ DOCX. |
| New final tag? | **Yes — only after** Manifest A items tracked and `BASELINE_SHA256_MANIFEST.json` updated. Suggested name pattern: `msc-dissertation-reproducibility-2026-08-31` (do not reuse July tag). |
| Large files via manifest vs commit? | `phase1_embedding_cache.json` (16.5 MB): **manifest/hash only** (existing policy). Processed transcripts (~3.3 MB total): **commit** (public text). PDFs: commit or URL manifest. Raw API archives: **exclude**; use CSV manifests. |

**Current `main` vs tag:** No commits after `a42d935`; however **working tree** has unstaged chapter/build-script edits and ~176 untracked paths — so **HEAD equals tag in git history but not in workspace completeness**.

---

# Part 9 — Final release decision table

| Item | MSc release | Ebola release | Public-safe? | Required action |
|------|-------------|---------------|--------------|-----------------|
| `phase1_decision_journal.json` | **Include** | Exclude | Yes | Keep tracked |
| Processed inquiry `.txt` (8) | **Include** | Exclude | Yes | Add to git or release archive |
| Aug 2026 experiments (minimum sets) | **Include** | Exclude | Yes | Track; remove `.gitignore` blanket on `experiments/` |
| Handbook-compliant DOCX/PDF | **Include** | Exclude | Yes | Track in `dissertation/Submission/final submission/` |
| n=60 Audit E full directory | **Include** | Exclude | Yes | Track all `run_20260727_133838_*` files |
| Report-genre extraction run | **Include** | Exclude | Yes | Track `outputs/run_20260609_081454_*` |
| `confidence_llm_cache.json` | Include | Exclude | Yes | Already tracked |
| Sol invalidated full-hearing JSON | Include (labelled invalid) | Exclude | Yes | Not evidence; transparency only |
| `raw_responses_extended/` | Optional | Exclude | Yes | Prefer manifest CSV only |
| `.env` | **Exclude** | Exclude | No | Keep gitignored |
| Meeting / supervisor material | **Exclude** | Exclude | No | `.gitignore` + never publish |
| Other students' PDFs | **Exclude** | Exclude | No | Delete from shared clones |
| `dissertation/Lib/`, backups | **Exclude** | Exclude | N/A | Delete locally |
| Core `src/decision_journal` extraction stack | Include | **COPY/ADAPT** | Yes | Fork without COVID configs |
| July Wave 7A 77-page DOCX in tag | Superseded | Exclude | Yes | Retain as historical tag only |
| `language_edit` module | Exclude | Exclude | Yes | Dissertation-only |
| Viva/distinction packages | Optional | Exclude | Yes | Not needed for reproducibility |

---

## Manifest A — ADD/TRACK for final MSc snapshot

1. `dissertation/Submission/final submission/Lawal_MSc_Dissertation_handbook_compliant.docx` (+ PDF if exists)  
2. `dissertation/CHAPTER_3_METHODS.md`, `CHAPTER_4_RESULTS.md`, `ABSTRACT.md` (unstaged Aug edits)  
3. `experiments/chunk_overlap_sensitivity_2026-08-30/` — minimum set (Part 3.1)  
4. `experiments/model_sensitivity_2026-08-31/` — minimum set (Part 3.2)  
5. `data/processed/inquiry/document/*.txt` (8 hearings) + report text  
6. `outputs/run_20260609_081454_module2_in_brief_report/`  
7. `outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/**` (complete)  
8. `outputs/framework_mapping/run_20260727_131920_audit_E_human_approval_check/` (referenced by faithfulness CSV)  
9. `docs/revision_control/CHUNK_SENSITIVITY_*_2026-08-30.md`  
10. Update `BASELINE_SHA256_MANIFEST.json` for all new tracked artefacts  
11. `docs/repository_release/*.md`  
12. Optional: `outputs/run_2026060*` (11 hearing runs) if full journal rebuild required  

---

## Manifest B — EXCLUDE/SANITISE from all shared releases

1. `.env`, `.venv/`, `dissertation/Lib/`, `dissertation_Backup_270726_1828/`  
2. All meeting transcripts and supervisor registers (`Meeing 4.txt`, `SUPERVISOR_*`, xlsx)  
3. Other students' work (`Jesutomiwa_Salam_*`, `Lohit_*`, `EEEM073_Submission/`)  
4. `docs/my writtings/`, `Official dissertation resources/Supervisor allocations/`  
5. `~$*.docx`, duplicate Word builds, `Methodology_Results_v*.docx`  
6. `outputs/language_edit/`  
7. `outputs/distinction_strategy/Final meeting_transcript.txt`  
8. Chunk experiment `repair_*.docx`, `integrate_dissertation_docx.py` (integration debris)  
9. Full `raw_responses_extended/` unless explicitly requested  
10. `NLP Lectures/`, `historical docs/`, coursework PDFs at repo root  

---

## Manifest C — COPY/ADAPT as basis of future Ebola repository

1. `src/decision_journal/pdf_text.py`  
2. `src/decision_journal/extraction.py` (generalise prompts/schema)  
3. `src/decision_journal/journal.py`  
4. `src/decision_journal/review_flags.py`  
5. `src/decision_journal/confidence_signals.py` (optional)  
6. `src/decision_journal/inquiry_batch_text.py` (rename/generalise)  
7. CLI patterns from `scripts/run_extraction.py`, `apply_review_flags.py`  
8. `requirements.txt`, `.env.example`, generic `README.md`  
9. Design notes only from `docs/revision_control/DEFERRED_LIMITATIONS_FUTURE_WORK_REVISIONS.md`  

**Do not copy:** any `data/manifests/phase1_*`, `configs/annotations`, `configs/evaluation`, `experiments/`, `dissertation/`, COVID inquiry harvest/download modules without replacement.

---

## Final readiness verdict

### **NOT_READY_FOR_RELEASE**

**Blockers (must resolve before MSc reproducibility release):**

1. **Aug 2026 supplementary experiments entirely gitignored** — dissertation reports chunk/overlap and model sensitivity including full-hearing Terra confirmation; evidence not in version control.  
2. **Final handbook-compliant dissertation not tracked** — tag freezes superseded July 77-page artefact.  
3. **`data/processed/` transcripts not committed** — rebuild and traceability re-verification impossible without them.  
4. **n=60 audit chain incomplete in git** — only six Audit E files tracked; faithfulness CSV references gitignored human-approval gate.  
5. **Report-genre pilot run not committed** — claim documented but run JSON absent.  
6. **Unstaged chapter markdown** post-dates tag — source/prose drift risk vs submitted DOCX.  
7. **Repository pollution** (~700 MB stray venvs, backups) — must not ship in any archive.

**After blockers 1–6 are addressed:** status becomes **READY_AFTER_MINOR_CLEANUP** (venv deletion, path documentation, optional embedding-cache hash-only policy).

**Ebola reusable release:** not started; no action until separate repository is created from Manifest C.

---

*End of dual-release audit.*

**Report path:** `docs/repository_release/DUAL_RELEASE_AUDIT.md`
