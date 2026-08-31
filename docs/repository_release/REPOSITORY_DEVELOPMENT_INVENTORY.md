# Repository Development Inventory

**Project:** AI-assisted decision journaling from UK COVID-19 Inquiry transcripts  
**Author:** Akeeb Idowu Lawal (MSc Artificial Intelligence, EEEM004)  
**Inventory date:** 2026-08-31  
**Scope:** Read-only reconstruction of workspace structure and development history for a future release/reproducibility audit.  
**Method:** Recursive directory inspection, `git` metadata, manifest/README files, and representative file sampling. No repository files were modified during this inventory.

---

## 1. Executive summary

This workspace is a **hybrid research repository**: a Python CLI pipeline (`src/decision_journal/`, `scripts/`) for LLM-based extraction and evaluation from UK COVID-19 Inquiry Module 2 transcripts, plus extensive **dissertation authoring**, **revision-control wave documentation**, **examiner/viva packages**, and **late-stage sensitivity experiments** (Aug 2026) that are **gitignored**.

| Metric | Value |
|--------|-------|
| Current branch | `main` |
| Tracked files | 374 |
| Untracked items (approx.) | 176 |
| Top-level folders | 17 (+ `.venv`, `.pytest_cache`) |
| Largest folders | `dissertation/` (~363 MB), `dissertation_Backup_270726_1828/` (~347 MB), `.venv/` (~228 MB), `outputs/` (~188 MB) |
| Case study | UK COVID-19 Inquiry Module 2 (8 hearing transcripts → 414 candidate entries) |
| Frozen canonical dataset | `data/manifests/phase1_decision_journal.json` (tracked) |
| Active formal submission pointer | `outputs/dissertation_integration/ACTIVE_FORMAL_SUBMISSION_POINTER.json` → Wave 7A September 2026 package |
| Rapid Research / Ebola / DRC code | **Not present** as a separate codebase; only future-work references and supervisor meeting material |

---

## 2. Git repository state

### 2.1 Branch, tags, remotes

| Item | Value |
|------|-------|
| **Current branch** | `main` |
| **Local branches** | `main`, `distinction/examiner-evidence`, `distinction/final-integrity-fixes`, `distinction/final-submission-freeze`, `distinction/offline-demo`, `distinction/presentation-deck`, `distinction/presentation-storyboard`, `distinction/viva-defence` |
| **Remote** | `origin` (all distinction branches mirrored) |
| **Tags** | `baseline-wave6c-corrected-2026-07-28`, `final-submission-candidate-september-2026` |

### 2.2 Working tree status (2026-08-31)

- **Modified (tracked):** 7 files — `dissertation/CHAPTER_*.md` (5), `dissertation/ABSTRACT.md`, `scripts/build_dissertation_docx.py`, `scripts/build_submission_docx.py`
- **Untracked:** ~176 paths including most Word/PDF dissertation builds, `experiments/`, `data/raw/**`, `data/processed/**`, bulk of `outputs/**`, supervisor materials, coursework PDFs, and personal notes
- **Staged:** none observed

### 2.3 Last 20 commits (`main`)

| Date | Hash | Message |
|------|------|---------|
| 2026-07-30 | `a42d935` | Freeze final September submission candidate |
| 2026-07-29 | `c1feba1` | Add evidence-led viva defence package |
| 2026-07-29 | `cb34b14` | Add validated examiner presentation decks |
| 2026-07-29 | `4a5cfb7` | Add evidence-led presentation storyboard |
| 2026-07-29 | `5aae5c0` | Add deterministic offline examiner demonstration |
| 2026-07-29 | `7b27085` | Add examiner reproducibility and evidence package |
| 2026-07-29 | `ee02346` | Resolve final dissertation integrity findings |
| 2026-07-29 | `72e9fc4` | Freeze corrected Wave 6C dissertation baseline for distinction audit |

*(Only 8 commits visible on `main`; distinction work appears concentrated in late July 2026.)*

### 2.4 Tracked files by top-level folder

| Folder | Tracked count | Notes |
|--------|---------------|-------|
| `outputs/` | 176 | Selective freeze exceptions in `.gitignore` |
| `docs/` | 48 | Examiner evidence, viva, partial revision_control |
| `scripts/` | 48 | Core pipeline + distinction packaging (not all local scripts tracked) |
| `configs/` | 24 | Evaluation manifests, annotations, defaults |
| `src/` | 21 | `decision_journal` package |
| `demo/` | 14 | Offline examiner demo |
| `tests/` | 13 | Wave 4–6 validation tests |
| `dissertation/` | 12 | Markdown chapters + appendices only (no `.docx`) |
| `presentation/` | 8 | Deck build tooling |
| `data/` | 5 | Manifests only (not raw/processed transcripts) |

### 2.5 Ignored but present research artefacts

Per `.gitignore` and `git check-ignore`:

| Path | Status | Committed? |
|------|--------|------------|
| `data/raw/**` | Present locally (8 inquiry PDFs + report PDF) | No |
| `data/processed/**` | Present locally (9 `.txt` transcripts) | No |
| `data/manifests/phase1_embedding_cache.json` | ~16.5 MB | Explicitly ignored |
| `outputs/**` (bulk) | ~188 MB tree | Mostly no; selective freeze paths excepted |
| `experiments/**` | ~12 MB | Entire tree ignored |
| `.env` | Present (150 bytes) | Ignored |
| `.venv/` | Present (~228 MB) | Ignored |
| `dissertation/Lib/`, `Scripts/`, `pyvenv.cfg` | Stray venv inside `dissertation/` | Partially ignored via patterns |

**Hash manifest for approved baseline:** `BASELINE_SHA256_MANIFEST.json` (tracked) documents SHA-256 for 125 approved tracked files; embedding cache and transcripts are **hash-manifest-only**.

---

## 3. Top-level folder inventory

### 3.1 `src/decision_journal/` — **Active (core library)**

| | |
|---|---|
| **Purpose** | Python package: inquiry harvest/download, PDF-to-text, LLM extraction, journal merge, review flags, confidence signals, clustering, structural reliability, language-edit submodule |
| **Key files** | `extraction.py`, `inquiry_harvest.py`, `inquiry_download.py`, `inquiry_client.py`, `pdf_text.py`, `journal.py`, `review_flags.py`, `clustering.py`, `confidence_signals.py`, `structural_reliability.py`, `language_edit/*` |
| **Inputs** | Processed transcript text, configs, OpenAI API |
| **Outputs** | Used by `scripts/`; no direct output dir |
| **Status** | Active core |
| **Docs** | `docs/ARCHITECTURE.md` |

### 3.2 `scripts/` — **Active (CLI orchestration)**

| | |
|---|---|
| **Purpose** | Runnable pipeline, evaluation, dissertation build, distinction packaging, post-60 audits |
| **Pipeline / extraction** | `run_pipeline.py`, `run_extraction.py`, `run_benchmark.py`, `pdf_to_text.py`, `build_phase1_journal.py`, `verify_phase1_data.py` |
| **Evaluation** | `build_annotation_excerpts.py`, `summarize_triangulation.py`, `keyword_baseline.py`, `build_error_taxonomy.py`, `summarize_grace.py`, `apply_review_flags.py`, `build_confidence_validation_sample.py`, `rate_confidence_sample.py`, `compare_confidence_signals.py`, `classify_discourse.py`, `run_clustering.py`, `visualize_clustering.py`, `run_structural_reliability.py` |
| **JEE/DQ / post-60** | `run_jee_dq_human_review.py`, `build_jee_dq_review_workbook.py`, `post60_*_audit_lib.py`, `run_post60_*`, `import_post60_*`, `stage1_supervisor_comment_planning.py` |
| **Dissertation / docx** | `build_dissertation_docx.py`, `build_submission_docx.py`, `build_surrey_dissertation_docx.py`, `_lot_fix_handbook_compliant.py`, `run_language_edit.py`, `rebuild_appendix_a_excerpts.py` |
| **Distinction / viva** | `build_wave7a_final_freeze.py`, `build_examiner_evidence_package.py`, `build_offline_demo_package.py`, `build_viva_defence_package.py`, `generate_viva_question_bank.py`, `validate_viva_defence_wave6.py` |
| **Figures** | `build_conceptual_framework_figure.py`, `build_figure33_pipeline.py`, `build_figure43_error_taxonomy.py`, `build_figure49_crosstab.py` |
| **Presentation / misc** | `build_covid_deck_v5.py`, `build_meeting_17_slide.py`, `create_progress_report_4.py`, `fill_two_weekly_report.py` |
| **Status** | Active; ~78 `.py` files locally, 48 tracked |
| **Note** | Many Aug 2026 scripts are **untracked** (chunk/model sensitivity integration, LoT fix, post-60 imports) |

### 3.3 `configs/` — **Active (frozen settings + evaluation manifests)**

| Subfolder / file | Purpose |
|------------------|---------|
| `default.json`, `inquiry_corpus.json`, `inquiry_phase1_seeds.json`, `phase1_journal_runs.json` | Pipeline and corpus configuration |
| `annotations/manual_phase1.json` | Manual triangulation workbook (6 excerpts) |
| `annotations/excerpts/excerpt_001–006.json` | Bounded excerpt definitions |
| `evaluation/confidence_validation_sample.json` | n=50 stratified human validation sample |
| `evaluation/confidence_comparison_results.json` | Automated vs human Rubric B |
| `evaluation/confidence_llm_cache.json` | LLM second-pass confidence cache |
| `evaluation/error_taxonomy_sample.json` | n=42 error taxonomy |
| `evaluation/grace_expansion.json`, `structural_reliability_*.json` | Supplementary eval |
| `evaluation/backups/*_pristine.json` | Frozen evaluation backups |
| `language_edit.json` | Language-edit wave config (untracked) |
| `manual_annotation_template.json`, `manual_annotation_workbook.example.json` | Annotation templates (untracked) |

### 3.4 `data/` — **Active inputs; mostly gitignored on disk**

| Path | Purpose | Tracked | Local |
|------|---------|---------|-------|
| `data/manifests/phase1_decision_journal.json` | **Frozen canonical 414-entry journal** | Yes | Yes (~417 KB) |
| `data/manifests/phase1_clustering_report.json` | Clustering output manifest | Yes | Yes |
| `data/manifests/inquiry_module2_phase1.csv/json` | Phase 1 corpus metadata | Yes | Yes |
| `data/manifests/phase1_embedding_cache.json` | Embedding vectors | No (ignored) | Yes (~16.5 MB) |
| `data/raw/inquiry/document/*.pdf` | Source inquiry PDFs (8 hearings + report) | No | Yes (~6.7 MB total) |
| `data/processed/inquiry/document/*.txt` | Extracted transcript text | No | Yes (~3.3 MB total) |
| `data/raw/README.md` | Documents raw data layout | Yes | Yes |

### 3.5 `outputs/` — **Generated / freeze packages (~188 MB)**

| Subtree | Purpose | Status |
|---------|---------|--------|
| `outputs/run_20260608_*` … `run_20260609_*` | Phase 1 per-hearing extraction JSON (11 runs) | Generated, gitignored |
| `outputs/figures/` | Thesis figures (`conceptual_framework.png`, clustering) | Partially tracked |
| `outputs/framework_mapping/run_*` | JEE/DQ human review, post-60 audits (Jul 2026) | Selective tracked freeze |
| `outputs/dissertation_integration/run_*` | Wave 1–7A dissertation integration builds | Selective tracked freeze |
| `outputs/distinction_strategy/03–07_*` | Reproducibility, demo, presentation, viva, final freeze | Tracked packages |
| `outputs/clustering_audit/run_*` | Cluster label review packs | Generated |
| `outputs/language_edit/run_*` | LLM language-edit dry runs | Generated |
| `outputs/_wave6a_guide_extracts/` | Audit guide extracts | Generated |

**Key pointer files:**
- `outputs/dissertation_integration/ACTIVE_FORMAL_SUBMISSION_POINTER.json` → Wave 7A September 2026 DOCX/PDF
- `outputs/distinction_strategy/07_final_submission_freeze/` — final examiner inspection bundle

### 3.6 `experiments/` — **Experimental, gitignored (Aug 2026)**

| Directory | Date | Purpose |
|-----------|------|---------|
| `experiments/chunk_overlap_sensitivity_2026-08-30/` | 2026-08-30 | Pre-registered chunk/overlap sensitivity; raw API responses; dissertation DOCX integration/repair scripts |
| `experiments/model_sensitivity_2026-08-31/` | 2026-08-31 | Model comparison (gpt-4o-mini, gpt-4o, gpt-5.6-*); `raw_responses_extended/`, `raw_responses_full_hearing/` |

Both contain protocols, CSV results, safety checks, and integration recommendations. **Not committed.**

### 3.7 `dissertation/` — **Active dissertation authoring (~363 MB; mostly Word/venv bloat)**

| Content | Purpose | Status |
|---------|---------|--------|
| `CHAPTER_1–5.md`, `ABSTRACT.md`, `APPENDIX_*.md`, `REFERENCES.md` | Source-of-truth markdown (tracked; 7 files modified unstaged) | Active |
| `Lawal_MSc_Dissertation*.docx/pdf` (many variants) | Word builds, handbook-compliant, submission copies | Generated, mostly untracked |
| `Submission/final submission/` | Final handbook-compliant submission DOCX | Active target |
| `Submission/*chunk*sensitivity*` | Post-experiment integration artefacts | Experimental |
| `CPHIA/` | Conference abstract drafts (CPHIA 2026) | Active side output |
| `Meeing 4.txt`, `Meeting 3.md`, `Meeting 4.md` | Supervisor meeting transcripts/notes | Personal/supervisor — **not for release** |
| `md backup/` | Markdown snapshots | Historical |
| `share/` | Share staging | Unclear |
| `Lib/`, `Scripts/`, `pyvenv.cfg` | **Accidental Python venv** inside dissertation folder | Pollution — exclude from release |
| `Methodology_Results_v2–v8.docx`, `*_Copy.docx`, `~$*.docx` | Version churn, Office lock files | Duplicates / temp |
| `gantt_chart.py/png`, `update_interim_review.py` | Early project planning | Historical |
| `SUBMISSION_CHECKLIST.md`, `SUBMISSION_ENGINEERING.md`, `VIVA_NOTES.md` | Submission ops | Active reference |

**Provenance docs:** `DISSERTATION_OUTLINE_MAP.md`, `SUBMISSION_CHECKLIST.md`, `_LoT_FIX_REPORT.json`

### 3.8 `dissertation_Backup_270726_1828/` — **Historical backup (~347 MB)**

Full snapshot from 2026-07-27 18:28 including markdown chapters, `SUBMISSION_CHECKLIST.md`, and a **complete embedded Python venv** (`Lib/`, `Scripts/`). Duplicate of dissertation state at Wave 6C era. **Exclude from any release.**

### 3.9 `docs/` — **Active documentation + revision control (~6.5 MB)**

| Subfolder | Purpose |
|-----------|---------|
| `docs/ARCHITECTURE.md`, `PROGRESS.md`, `*_SUMMARY.md` | Technical and evaluation summaries |
| `docs/revision_control/` | Wave 0–7A approval records, manifests, supervisor feedback register, chunk/model sensitivity integration reports (Aug 2026) |
| `docs/examiner_evidence/` | Reproducibility runbook, artefact manifest, SHA256SUMS |
| `docs/viva/` | Question bank, defence maps, mock viva scripts |
| `docs/presentation/` | Storyboard, speaker notes |
| `docs/review/` | Examiner-style review docs, annotated dissertation, **another student's EEEM073 submission** |
| `docs/my writtings/` | Personal writing (`old project in my words.doc`, PDFs) — **not for release** |
| `docs/md backup/` | Historical markdown copies |
| `docs/_anthropic_pages/`, `anthropic.pdf` | Reference material |

**Key manifests:** `REVISION_CONTROL_MANIFEST.json`, `REVISION_CONTROL_SHA256SUMS.txt`, `REVISION_EXECUTION_WAVES.md`

### 3.10 `tests/` — **Active (13 test modules)**

Coverage: phase2a flags, appendix A coordinates, post-60 audits, language-edit, offline demo, examiner evidence, presentation decks/storyboard, viva defence, leak-term scan. Run via `pytest`.

### 3.11 `demo/` — **Active (offline examiner demo)**

Static HTML/JS demo with embedded evidence JSON (`phase1-016`, `090`, `082`, `246`). Documented in `DEMO_RUNBOOK.md`. Tracked and copied into distinction packages.

### 3.12 `presentation/` — **Active (viva deck build)**

`build_presentation.py`, `presentation_content.py`, `presentation_theme.py`, validation scripts. Outputs go to `outputs/distinction_strategy/05_presentation_deck/`.

### 3.13 `Official dissertation resources/` — **Reference / admin (~24 MB)**

University templates (Word, LaTeX zip), ethics forms, interim review form, project handbook, supervisor allocations, two-weekly progress reports, literature guides. **Administrative — not core research code.**

### 3.14 `historical docs/` — **Historical (pre-pivot)**

Early concept docs (Apr 2026): `AI-Assisted Decision Journal Draft Concept.docx`, `Proposal (POSSIBLE TOPICS).docx`, `Expert Advice Breakdown.xlsx`.

### 3.15 `NLP Lectures/` — **Course material**

Transformers lab notebook and lecture text parts. Not project code.

### 3.16 `.venv/` — **Local environment (~228 MB)**

Standard project virtualenv. Gitignored.

### 3.17 Repository root (miscellaneous untracked)

| File | Notes |
|------|-------|
| `ProjectHandbook2025-26.pdf` | Handbook copy (also under Official resources) |
| `Transcript0.docx`, `Transcript0.txt` | Early exploratory transcript (outbreak/documentation themes in text) |
| `Jesutomiwa_Salam_Msc_Dissertation.*`, `Lohit_Dissertation_Report.pdf` | **Other students' dissertations — exclude** |
| `AI-assisted decision making journal*.docx` | Early title variants |
| `COVID_DATA_SLIDE_v5_5slides.pdf`, `Progress meeting.pptx` | Presentation artefacts |
| `feedback form 4 2026_ad.pdf` | Progress feedback |
| `_extracted_handbook.txt` | Tool-generated extraction (examiner session) |
| `BASELINE_SHA256_MANIFEST.json` | Tracked baseline hash register |
| `README.md`, `requirements.txt`, `.env.example` | Tracked project entry points |

---

## 4. Experiment directories (dated)

| Path | Date (folder name) | Protocol | Raw API archives | Dissertation integration |
|------|-------------------|----------|------------------|--------------------------|
| `experiments/chunk_overlap_sensitivity_2026-08-30/` | 2026-08-30 | `00_PROTOCOL_PRE_REGISTERED.md` | Via `run_experiment.py` logs | `integrate_dissertation_docx.py`, repair scripts, `DISSERTATION_INTEGRATION_RECOMMENDATION.md` |
| `experiments/model_sensitivity_2026-08-31/` | 2026-08-31 | `00_PROTOCOL.md` | `raw_responses_extended/`, `raw_responses_full_hearing/` | `06/13/18_*_INTEGRATION_RECOMMENDATION.md` |

Both experiment trees are **gitignored** in their entirety.

---

## 5. Major pipeline and evaluation scripts (grouped)

### 5.1 Ingestion → extraction → canonical journal

```
run_pipeline.py (harvest → download → text)
  → run_extraction.py / run_benchmark.py
  → outputs/run_YYYYMMDD_*/
  → build_phase1_journal.py
  → data/manifests/phase1_decision_journal.json
```

### 5.2 Phase 1 evaluation

`build_annotation_excerpts.py` → `summarize_triangulation.py` | `keyword_baseline.py` | `build_error_taxonomy.py` | `summarize_grace.py`

### 5.3 Phase 2 enrichment

`apply_review_flags.py` → `build_confidence_validation_sample.py` → `rate_confidence_sample.py` → `compare_confidence_signals.py` → `classify_discourse.py` → `run_clustering.py` → `visualize_clustering.py`

### 5.4 Framework mapping / post-60 (Jul 2026)

`build_jee_dq_review_workbook.py` → `run_jee_dq_human_review.py` → audit chain (`run_post60_source_integrity_audit.py` → `run_post60_coding_consistency_audit.py` → `run_post60_analytical_audit_E_final.py`)

### 5.5 Dissertation production

`build_dissertation_docx.py` / `build_submission_docx.py` → Word; `run_language_edit.py` for controlled LLM prose edits; wave freeze via `build_wave7a_final_freeze.py`

---

## 6. Annotation and manual-review files

| Location | Content |
|----------|---------|
| `configs/annotations/manual_phase1.json` | Master manual triangulation workbook |
| `configs/annotations/excerpts/excerpt_001–006.json` | Six bounded transcript spans |
| `configs/evaluation/confidence_validation_sample.json` | n=50 human Rubric A/B ratings |
| `configs/evaluation/confidence_validation_sample_provisional.json` | Provisional ratings snapshot |
| `configs/evaluation/backups/*_pristine.json` | Frozen backups |
| `dissertation/APPENDIX_A_MANUAL_EXCERPTS.md` | Appendix A source text |
| `outputs/framework_mapping/run_20260726_045745_JEE_DQ_human_adjudication/` | Interactive n=60 review (gitignored bulk) |
| `outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/` | **Frozen Audit E** (partially tracked) |
| `outputs/framework_mapping/run_20260727_094015_post60_coding_consistency_audit/CONSISTENCY_CORRECTED_REFERENCE.csv` | Tracked corrected reference |

---

## 7. Fixed / frozen dataset locations

| Artefact | Path | Version / note |
|----------|------|----------------|
| Canonical decision journal | `data/manifests/phase1_decision_journal.json` | 414 entries; Phase 2 reads this only |
| Flagged journal backup | `configs/evaluation/backups/phase1_decision_journal_v1.1_flagged.json` | Pre-canonical snapshot |
| Clustering report | `data/manifests/phase1_clustering_report.json` | 20 groups |
| Corpus manifest | `data/manifests/inquiry_module2_phase1.csv` | 8 transcripts |
| Confidence validation | `configs/evaluation/confidence_validation_sample.json` | n=50 frozen |
| Wave 6C submission package | `outputs/dissertation_integration/run_20260728_141045_wave6c_final_submission_package/` | Tagged `baseline-wave6c-corrected-2026-07-28` |
| Wave 2 integrity package | `outputs/dissertation_integration/run_20260729_153931_wave2_final_integrity_fixes/` | |
| Wave 7A active submission | `outputs/dissertation_integration/run_20260730_064035_wave7a_title_page_september/` | Pointer in `ACTIVE_FORMAL_SUBMISSION_POINTER.json` |
| Final distinction freeze | `outputs/distinction_strategy/07_final_submission_freeze/` | Examiner inspection bundle |
| Baseline hashes | `BASELINE_SHA256_MANIFEST.json` | 125 tracked files |

---

## 8. Dissertation integration and revision-control areas

| Area | Role |
|------|------|
| `docs/revision_control/` | Authoritative wave governance: `REVISION_EXECUTION_WAVES.md`, `WAVE_*_APPROVAL_RECORD.md`, supervisor feedback register (xlsx/csv), chunk/model sensitivity integration reports (2026-08-30) |
| `outputs/dissertation_integration/run_20260727_*` – `run_20260730_*` | Per-wave chapter integration with `pre_edit_backup/`, page images, manifests |
| `scripts/build_wave7a_final_freeze.py`, `active_formal_submission.py` | Submission freeze automation |
| `dissertation/Submission/` | Final submission staging (handbook-compliant DOCX) |
| `scripts/_lot_fix_handbook_compliant.py` | List of Tables / figures repair (Aug 2026) |

---

## 9. Generated output trees (summary)

- **11+ extraction runs** under `outputs/run_20260608_*` and `outputs/run_20260609_*`
- **15+ framework_mapping runs** (Jul 2026)
- **25+ dissertation_integration runs** (Jul 2026)
- **8 language_edit dry runs** (Jul 2026)
- **2 clustering_audit runs**
- **Distinction strategy waves 03–07** (partially committed)
- **2 experiment directories** (Aug 2026, ignored)

---

## 10. Duplicates, backups, and version churn

| Pattern | Examples | Risk |
|---------|----------|------|
| Date-stamped backup folder | `dissertation_Backup_270726_1828/` | Full duplicate + venv |
| Copy suffix | `Lawal_MSc_Dissertation - Copy.docx`, `*_handbook_compliant - Copy.docx` | Ambiguous canonical |
| Version series | `Methodology_Results_v2`–`v8.docx` | Historical only |
| PRE_/POST_ prefixes | `*_PRE_LoT_FIX.docx`, `*_PRE_CHUNK_SENSITIVITY*` | Pre-integration snapshots |
| Office temp files | `~$*.docx` | Delete before release |
| Stray venvs | `dissertation/Lib/`, `dissertation_Backup_*/Lib/` | ~700 MB wasted |
| `md backup/` folders | `dissertation/md backup/`, `docs/md backup/` | Stale markdown |
| Multiple dissertation PDFs | `Lawal_MSc_Dissertation.pdf`, `_submission.pdf`, `_handbook_compliant.pdf` | Need SHA256 tie-break |

---

## 11. Rapid Research / Ebola / DRC / outbreak material

| Finding | Detail |
|---------|--------|
| **Dedicated code folder** | **None** |
| **Future-work references** | `docs/revision_control/DEFERRED_LIMITATIONS_FUTURE_WORK_REVISIONS.md` mentions outbreak meeting transcripts, live outbreak documentation |
| **Supervisor meeting transcript** | `outputs/distinction_strategy/Final meeting_transcript.txt` (untracked) — discusses DRC Ebola outbreak, rapid research proposal, methodology transfer |
| **Root exploratory file** | `Transcript0.txt` / `.docx` — outbreak documentation themes (not COVID Inquiry corpus) |
| **Corpus keyword matches** | `phase1_decision_journal.json` contains inquiry testimony mentioning "outbreak" in COVID context only |
| **Unrelated coursework** | `docs/review/ai and sustainability/EEEM073_Submission/` — sustainability module, not Ebola |

**Conclusion:** Ebola/DRC is **planning/supervisor-discussion only**; no separate Rapid Research codebase exists yet.

---

## 12. Security, credentials, and path risks

| Risk | Location | Mitigation in repo |
|------|----------|-------------------|
| `.env` with API key | Root (exists, 150 bytes) | Gitignored; `.env.example` has placeholder only |
| `OPENAI_API_KEY` usage | `src/decision_journal/extraction.py`, experiment scripts | Documented in `OPENAI_API_USAGE_AND_COST_CHECK.md` |
| Secret scanning | `tests/test_*.py`, freeze scripts | Regex scans for `sk-` patterns in packages |
| Hard-coded Windows paths | `outputs/framework_mapping/*/AUDIT_E_MANIFEST.json`, `CONSISTENCY_DISCOVERY_REPORT.md` | `C:\SURREY\MODULES\SEMESTER 2\MSC PROJECT\code\...` |
| README setup example | `README.md` line 64 | `C:\SURREY\MODULES\...` |
| Raw API response archives | `experiments/model_sensitivity_2026-08-31/raw_responses_*` | May contain model outputs; review before release |
| `confidence_llm_cache.json` | `configs/evaluation/` | LLM responses (tracked) |
| Supervisor allocations PDF | `Official dissertation resources/Supervisor allocations/` | Contains staff names |
| Other students' work | Root + `docs/review/` | Must exclude |

---

## 13. Unusually large files and folders

| Size | Path |
|------|------|
| ~363 MB | `dissertation/` (venv + Word/PDF) |
| ~347 MB | `dissertation_Backup_270726_1828/` |
| ~228 MB | `.venv/` |
| ~188 MB | `outputs/` |
| ~87 MB each | `dissertation/Lib/.../playwright/driver/node.exe` (stray) |
| ~16.5 MB | `data/manifests/phase1_embedding_cache.json` |
| ~6.7 MB | `Official dissertation resources/.../Dissertation_Template2026.zip` |
| ~1.2 MB each | Final dissertation PDFs |

---

## 14. Raw API-response archives

| Location | Contents |
|----------|----------|
| `experiments/model_sensitivity_2026-08-31/raw_responses_extended/` | Per-model, per-rep, per-excerpt JSON |
| `experiments/model_sensitivity_2026-08-31/raw_responses_full_hearing/` | Full-hearing confirmation runs |
| `configs/evaluation/confidence_llm_cache.json` | Cached LLM confidence second-pass (tracked) |
| `outputs/language_edit/run_*/llm/` | Language-edit LLM outputs (gitignored) |

---

## 15. Personal, supervisor, and non-release material

**Should not appear in a shared code release without explicit curation:**

| Category | Paths |
|----------|-------|
| Meeting transcripts / notes | `dissertation/Meeing 4.txt`, `Meeting 3.md`, `Meeting 4.md`, `docs/MEETING_*.md`, `outputs/distinction_strategy/Final meeting_transcript.txt` |
| Supervisor briefs / feedback | `docs/SUPERVISOR_BRIEF_2026-06-17.md`, `docs/revision_control/Consolidated_Supervisor_Feedback_Register_Reconciled.xlsx`, `SUPERVISOR_ACTION_PLAN.csv`, `SUPERVISOR_HUMAN_DECISIONS.md` |
| Personal writings | `docs/my writtings/` |
| Other students' dissertations | `Jesutomiwa_Salam_*`, `Lohit_Dissertation_Report.pdf`, `docs/review/ai and sustainability/EEEM073_Submission/` |
| Progress / admin forms | `Official dissertation resources/Two-weekly progress form/`, `feedback form 4 2026_ad.pdf` |
| Viva rehearsal internals | `docs/viva/MOCK_VIVA_*`, `REHEARSAL_LOG_TEMPLATE.csv` |
| Supervisor correction report | `docs/review/Supervisor_Correction_Report.pdf` |
| Staff allocations | `Official dissertation resources/Supervisor allocations/` |

---

## 16. Development map

Chronological reconstruction from repository evidence only (file dates, folder names, commits, `docs/PROGRESS.md`, wave records).

### Stage 0 — Project conception (Mar–Apr 2026)

- `historical docs/`: proposal and concept documents (Mar–Apr 2026).
- Early topic exploration; decision-journal concept drafted.

### Stage 1 — Pipeline bootstrap (Jun 2026)

- `src/decision_journal/` package created (~Jun 7).
- `scripts/run_pipeline.py`, `run_extraction.py`, `pdf_to_text.py`.
- First extraction runs: `outputs/run_20260608_*`, `run_20260609_*` (8 Module 2 hearings + In Brief report).
- `build_phase1_journal.py` → frozen `phase1_decision_journal.json` (414 entries).
- Manual annotation: `configs/annotations/`, six excerpts, triangulation.

### Stage 2 — Phase 1 evaluation (Jun 9–18 2026)

- GRACE, keyword baseline, error taxonomy scripts and `docs/*_SUMMARY.md`.
- Figures: `build_figure49_crosstab.py`, error taxonomy figure.
- Phase 2a flags: `apply_review_flags.py`.
- Phase 2b: confidence sample build, human rating (`rate_confidence_sample.py`), discourse pilot.
- Phase 2c: clustering + visualization (`run_clustering.py`, Jun 22).
- Meeting notes: `dissertation/Meeting 3.md`, `Meeing 4.txt` (Jun 18).

### Stage 3 — Interim review and COVID pivot documentation (Jun 2026)

- `dissertation/Interim review.pdf`, Gantt chart, progress slides (`build_covid_deck_v5.py`).
- `docs/SCOPE_UPGRADE_PLAN.md`, inquiry-focused architecture in `docs/ARCHITECTURE.md`.
- README documents "pivot after interim review, April 2026" (narrative; files dated Jun 2026).

### Stage 4 — JEE/DQ framework mapping pilot (Jul 25–27 2026)

- `outputs/framework_mapping/run_20260725_*` through `run_20260727_133838_*`.
- Interactive review: `run_jee_dq_human_review.py` (large Streamlit-style tool).
- Audit chain A→E: source integrity, coding consistency, analytical audit, human approval gate.
- Frozen Audit E artefacts partially committed per `.gitignore` exceptions.

### Stage 5 — Dissertation revision waves (Jul 27–28 2026)

- `docs/revision_control/REVISION_EXECUTION_WAVES.md`: Waves 0–6C.
- `outputs/dissertation_integration/run_20260727_*` – `run_20260728_141045_wave6c_*`: chapter-by-chapter markdown→Word integration, language consistency, formatting.
- Language-edit dry runs: `outputs/language_edit/run_20260724_*` – `run_20260725_*`.
- Tag: `baseline-wave6c-corrected-2026-07-28`.

### Stage 6 — Distinction packaging (Jul 29–30 2026)

- Git commits: reproducibility package, offline demo, presentation deck, viva defence, integrity fixes.
- `outputs/distinction_strategy/03`–`07_*` bundles; `BASELINE_SHA256_MANIFEST.json`.
- Wave 7A: September title-page submission (`run_20260730_064035_wave7a_title_page_september`).
- Tag: `final-submission-candidate-september-2026`.
- Backup snapshot: `dissertation_Backup_270726_1828/`.

### Stage 7 — Post-freeze dissertation polish (Aug 2026)

- Handbook-compliant DOCX iterations in `dissertation/` and `Submission/final submission/`.
- LoT fix: `_lot_fix_handbook_compliant.py`, `_LoT_FIX_REPORT.json` (Aug 28).
- Chunk sensitivity experiment (Aug 30) and model sensitivity experiment (Aug 31) — **gitignored**.
- Chapter markdown updates (Aug 30, unstaged): sensitivity sections integrated.
- CPHIA abstract drafts: `dissertation/CPHIA/`.

### Stage 8 — Not started in repository

- Rapid Research / Ebola / DRC implementation (supervisor discussion only).
- Second-reviewer validation tooling.
- Production deployment / web interface.

---

## 17. Areas requiring later release audit

Shortlist for classification before creating (a) a **frozen MSc dissertation reproducibility release** and (b) a **separate reusable Rapid Research / Ebola code release**.

### 17.1 MSc dissertation reproducibility release — audit priority

| Priority | Path / item | Question for audit |
|----------|-------------|-------------------|
| **P0** | `data/manifests/phase1_decision_journal.json` | Confirm canonical version and SHA256 vs `BASELINE_SHA256_MANIFEST.json` |
| **P0** | `configs/evaluation/confidence_validation_sample.json` | Include human ratings? Redaction needed? |
| **P0** | `configs/annotations/manual_phase1.json` + excerpts | Core ground truth — required for reproduction |
| **P0** | `src/`, `scripts/` (tracked subset) | Define minimal script set vs full 78 local scripts |
| **P0** | `outputs/run_2026060*` extraction runs | Required to rebuild journal or journal sufficient? |
| **P1** | `data/raw/`, `data/processed/` | Public inquiry data — can redistribute PDFs/text? |
| **P1** | `outputs/framework_mapping/run_20260727_133838_*` | Audit E — partial commit; verify completeness |
| **P1** | `outputs/dissertation_integration/ACTIVE_FORMAL_SUBMISSION_POINTER.json` | Which DOCX is canonical vs `Submission/final submission/`? |
| **P1** | `experiments/chunk_overlap_sensitivity_2026-08-30/`, `model_sensitivity_2026-08-31/` | Include in reproducibility bundle or separate appendix? |
| **P2** | `dissertation/CHAPTER_*.md` vs Word builds | Source-of-truth alignment after Aug 30 edits |
| **P2** | `configs/evaluation/confidence_llm_cache.json` | Contains API outputs — license/redaction |
| **P2** | Hard-coded `C:\SURREY\...` paths in manifests | Portability scrub |
| **Exclude** | `dissertation/Lib/`, `dissertation_Backup_*`, `~$*`, other students' PDFs, meeting transcripts, supervisor xlsx | |

### 17.2 Rapid Research / Ebola code release — audit priority

| Priority | Path / item | Question for audit |
|----------|-------------|-------------------|
| **P0** | *(none)* | **No Ebola/DRC codebase exists yet** |
| **P1** | `Transcript0.txt` | Early domain notes — seed material or discard? |
| **P1** | `outputs/distinction_strategy/Final meeting_transcript.txt` | Supervisor planning — **exclude from code release**; extract requirements only |
| **P1** | `docs/revision_control/DEFERRED_LIMITATIONS_FUTURE_WORK_REVISIONS.md` | Future-work spec for genre transfer |
| **P2** | Generalisable modules in `src/decision_journal/` | `extraction.py`, `pdf_text.py`, `journal.py`, `review_flags.py` — candidate for fork |
| **P2** | `README.md` / `docs/ARCHITECTURE.md` | COVID-Inquiry-specific vs domain-agnostic framing |
| **Defer** | All `outputs/`, `configs/inquiry_*`, COVID corpus manifests | Inquiry-specific; not portable without new corpus |

---

## 18. Inventory metadata

| Field | Value |
|-------|-------|
| **Inventory file** | `docs/repository_release/REPOSITORY_DEVELOPMENT_INVENTORY.md` |
| **Repository path** | `C:\SURREY\MODULES\SEMESTER 2\MSC PROJECT\code` |
| **Git remote** | `origin` (distinction branches present) |
| **Files modified during inventory** | This file only (new) |
| **Next step (out of scope)** | Release/reproducibility audit using Section 17 shortlists |

---

*End of inventory.*
