# Reproducibility guide

**Audience:** A competent researcher or developer who does **not** know this project’s development history.  
**Goal:** Explain what to run, in what order, what inputs are required, what outputs mean, and how each output maps to dissertation results.

For a one-page overview, see the [root README](../README.md). For system design detail, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 1. Three ways to use this repository

| Mode | API key needed? | When to use |
|------|-----------------|-------------|
| **A. Inspect frozen results** | No | Verify dissertation numbers, run integrity tests, trace a single journal entry |
| **B. Rebuild case-study inputs** | No (download only) | Regenerate `data/processed/` text from public Inquiry PDFs |
| **C. Re-run LLM analyses** | Yes | Re-extract, re-embed, re-score — expect **non-identical** outputs (see §8) |

**Default recommendation:** Start with **Mode A**. The frozen journal (`data/manifests/phase1_decision_journal.json`) is the authoritative record for the 414 / 351 figures and all downstream evaluation.

---

## 2. Environment setup

```bash
# Repository root
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Copy the environment template (never commit secrets):

```bash
cp .env.example .env
# Edit .env: OPENAI_API_KEY=... and optionally OPENAI_MODEL=gpt-4o-mini
```

### Python dependencies

Pinned in `requirements.txt`: `openai`, `python-dotenv`, `pypdf`, `pandas`, `matplotlib`, `scikit-learn`, `numpy`, `httpx`, `beautifulsoup4`, `python-docx`.

Minor version drift in `pypdf` can slightly change PDF-to-text output and therefore traceability pass rates.

---

## 3. Inspect frozen results offline (Mode A)

### 3.1 Run integrity tests

These tests check excerpt coordinates, review-flag counts, and that no foreign-author leak terms appear in adjudication files:

```bash
python -m pytest tests/test_appendix_a_excerpt_coordinates.py \
  tests/test_phase2a_flag_counts_and_wordcount.py \
  tests/test_leak_term_scan.py -q
```

Optional — evidence-package validation:

```bash
python -m pytest tests/test_examiner_evidence_package.py -q
```

### 3.2 Recalculate headline statistics from committed JSON

```bash
python -c "
import json
from pathlib import Path

j = json.loads(Path('data/manifests/phase1_decision_journal.json').read_text(encoding='utf-8'))
print('Journal totals:', j['totals'])

flags = sum(1 for e in j['entries'] if e.get('phase2', {}).get('review_flags'))
print('Entries with review flags:', flags)

s = json.loads(Path('configs/evaluation/confidence_validation_sample.json').read_text(encoding='utf-8'))
cells = {}
for i in s['items']:
    key = (i['human_valid_decision'], i['human_confidence'])
    cells[key] = cells.get(key, 0) + 1
print('n=50 Rubric A x B cells:', dict(sorted(cells.items())))
print('no x high:', cells.get(('no', 'high'), 0))

k = json.loads(Path('configs/evaluation/confidence_comparison_results.json').read_text(encoding='utf-8'))
print('Rule kappa vs Rubric B:', round(k['metrics']['rule_vs_human_b']['weighted_kappa'], 2))
print('LLM kappa vs Rubric B:', round(k['metrics']['llm_vs_human_b']['weighted_kappa'], 2))

c = json.loads(Path('data/manifests/phase1_clustering_report.json').read_text(encoding='utf-8'))
print('Clusters:', c['n_clusters'])

sr = json.loads(Path('configs/evaluation/structural_reliability_results.json').read_text(encoding='utf-8'))
print('Structural reliability:', sr['summary'])
"
```

Expected headline values (dissertation):

| Metric | Expected |
|--------|----------|
| Journal entries | 414 |
| Traceability pass | 351 |
| Review-flagged entries | 36 (4 procedural, 32 possible_duplicate) |
| n=50 dominant cell (no × high) | 21 |
| Rule κ vs Rubric B | ≈ 0.48 |
| LLM κ vs Rubric B | ≈ 0.39 |
| Clusters | 20 |
| Structural reliability pass rate | 49/50 |

### 3.3 n=60 extended audit (JEE / Decision Quality / faithfulness)

Authoritative aggregated outputs:

```
outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/
  AUDIT_E_JEE_SUMMARY.csv
  AUDIT_E_DQ_SUMMARY.csv
  AUDIT_E_TRACEABILITY_HUMAN_CLASSIFICATION.csv
  AUDIT_E_MANIFEST.json
```

Regenerate summaries from frozen inputs (offline):

```bash
python scripts/run_post60_analytical_audit_E_final.py
```

Human adjudication that produced the n=60 codes was performed interactively (`run_jee_dq_human_review.py`). Those session files may be local only; the **published counts** come from the Audit E CSVs above.

---

## 4. Pipeline order (full case study)

This is the logical order if you were building the case study from scratch. **Steps marked FROZEN** should not be re-run when verifying dissertation claims.

```
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 1 — Obtain source text                                            │
├─────────────────────────────────────────────────────────────────────────┤
│ 1. Harvest metadata     scripts/run_pipeline.py --stage harvest         │
│ 2. Download PDFs        scripts/run_pipeline.py --stage download        │
│ 3. PDF → text           scripts/run_pipeline.py --stage text            │
│    Output: data/processed/inquiry/document/*.txt (8 hearings)           │
│    Verify:  scripts/verify_phase1_data.py                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 2 — Extract decisions (API)                         [FROZEN OUTPUT] │
├─────────────────────────────────────────────────────────────────────────┤
│ 4. Per-hearing extract  scripts/run_extraction.py <file.txt>            │
│                         --label phase1 --inquiry                        │
│    Output: outputs/run_<timestamp>_<label>/                           │
│            manifest.json, decisions.json, raw_llm_outputs.json          │
│    Repeat for each of 8 hearings (see configs/phase1_journal_runs.json) │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 3 — Canonical journal                             [FROZEN OUTPUT] │
├─────────────────────────────────────────────────────────────────────────┤
│ 5. Merge eight runs     scripts/build_phase1_journal.py                 │
│    Output: data/manifests/phase1_decision_journal.json (414 entries)    │
│ 6. Review flags         scripts/apply_review_flags.py                     │
│    Output: phase2.review_flags added in-place on journal                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 4 — Manual evaluation (six excerpts)                              │
├─────────────────────────────────────────────────────────────────────────┤
│ 7. Build excerpt shells scripts/build_annotation_excerpts.py            │
│ 8. Human annotation     configs/annotations/manual_phase1.json          │
│ 9. Summaries            scripts/summarize_triangulation.py              │
│                         scripts/keyword_baseline.py                     │
│                         scripts/summarize_grace.py                      │
│                         scripts/build_error_taxonomy.py                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 5 — Confidence validation (n=50)                    [FROZEN LABELS] │
├─────────────────────────────────────────────────────────────────────────┤
│ 10. Build sample        scripts/build_confidence_validation_sample.py   │
│ 11. Human rating        scripts/rate_confidence_sample.py               │
│ 12. Compare signals     scripts/compare_confidence_signals.py           │
│ 13. Discourse pilot     scripts/classify_discourse.py --validate        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 6 — Clustering (n=414)                                            │
├─────────────────────────────────────────────────────────────────────────┤
│ 14. Cluster             scripts/run_clustering.py                       │
│ 15. Figures             scripts/visualize_clustering.py                 │
│    Output: data/manifests/phase1_clustering_report.json                 │
│            outputs/figures/phase1_cluster_*.png                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 7 — Extended human audit (n=60)                     [FROZEN LABELS] │
├─────────────────────────────────────────────────────────────────────────┤
│ 16. Interactive review  scripts/run_jee_dq_human_review.py                │
│ 17. Aggregate Audit E   scripts/run_post60_analytical_audit_E_final.py  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 8 — Supplementary analyses (do not alter the 414-entry set)       │
├─────────────────────────────────────────────────────────────────────────┤
│ 18. Structural test     scripts/run_structural_reliability.py           │
│ 19. Report-genre pilot  scripts/run_extraction.py (no --inquiry)        │
│                         on data/processed/inquiry/report/...              │
│ 20. Chunk sensitivity   experiments/chunk_overlap_sensitivity_2026-08-30/│
│ 21. Model sensitivity   experiments/model_sensitivity_2026-08-31/       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Script reference (what you actually need)

### 5.1 Ingestion and extraction

| Script | Inputs | Outputs | API? |
|--------|--------|---------|------|
| `run_pipeline.py --stage harvest` | Inquiry API, `configs/inquiry_phase1_seeds.json` | `data/manifests/inquiry_module2_phase1.csv` | No |
| `run_pipeline.py --stage download` | Manifest CSV | `data/raw/inquiry/**/*.pdf` | No |
| `run_pipeline.py --stage text` | PDFs | `data/processed/inquiry/**/*.txt` | No |
| `pdf_to_text.py` | Single PDF | `.txt` alongside or specified path | No |
| `run_extraction.py` | `.txt` file; `--inquiry` for case-study prompt | `outputs/run_*/` | **Yes** |
| `verify_phase1_data.py` | Manifest + disk paths | Console report | No |

### 5.2 Journal construction

| Script | Inputs | Outputs | API? |
|--------|--------|---------|------|
| `build_phase1_journal.py` | Eight runs in `configs/phase1_journal_runs.json` | `phase1_decision_journal.json` | No |
| `apply_review_flags.py` | Canonical journal | Journal updated in place | No |

### 5.3 Evaluation and summaries

| Script | Inputs | Outputs | API? |
|--------|--------|---------|------|
| `build_annotation_excerpts.py` | Transcripts + runs | `configs/annotations/manual_phase1.json` shell | No |
| `summarize_triangulation.py` | Manual workbook | `docs/TRIANGULATION_SUMMARY.md` | No |
| `keyword_baseline.py` | Manual + LLM JSON | `docs/BASELINE_KEYWORD.md` | No |
| `summarize_grace.py` | Workbook + expansion JSON | `docs/GRACE_SUMMARY.md` | No |
| `build_error_taxonomy.py` | All inquiry runs | `docs/ERROR_TAXONOMY.md`, sample JSON | No |
| `build_confidence_validation_sample.py` | Journal | `confidence_validation_sample.json` | No |
| `rate_confidence_sample.py` | Sample JSON | Ratings written to sample | No (human) |
| `compare_confidence_signals.py` | Sample + journal | `confidence_comparison_results.json` | **Yes** (LLM pass; cache in `confidence_llm_cache.json`) |
| `classify_discourse.py --validate` | n=50 sample | Discourse pilot JSON | **Yes** |
| `run_clustering.py` | Journal | `phase1_clustering_report.json`, journal cluster fields | **Yes** (embeddings) |
| `visualize_clustering.py` | Clustering report | `outputs/figures/*.png` | No |
| `run_structural_reliability.py` | Fixed chunk manifest | `structural_reliability_results.json` | **Yes** |
| `run_jee_dq_human_review.py` | Purposive 60 from journal | Interactive session files | No (human) |
| `run_post60_analytical_audit_E_final.py` | Audit inputs | Audit E CSVs/MD | No |

### 5.4 Scripts you can usually ignore

These support dissertation Word builds, presentation decks, viva preparation, or one-off packaging — not core reproducibility:

- `build_dissertation_docx.py`, `build_submission_docx.py`, `build_surrey_dissertation_docx.py`
- `build_*_package.py`, `build_wave7a_final_freeze.py`, `build_examiner_evidence_package.py`
- `run_language_edit.py`, `stage1_supervisor_comment_planning.py`
- `build_covid_deck_*.py`, `generate_viva_question_bank.py`

---

## 6. Dissertation results index

Each row maps a **reported result** to its producing code, inputs, outputs, and whether the artefact is in git as of the release audit (2026-08-31).

| Dissertation result | Script(s) | Input data | Output artefact(s) | Manual files | In git? | Reproducible from release? |
|---------------------|-----------|------------|---------------------|--------------|---------|---------------------------|
| **414 fixed candidates** | `build_phase1_journal.py` ← `run_extraction.py` × 8 | `configs/phase1_journal_runs.json`, processed transcripts | `data/manifests/phase1_decision_journal.json` | — | Journal yes; runs often no | **Partial** — journal yes; full rebuild needs runs + text |
| **351/414 traceability** | `run_extraction.py` / `extraction.py` | Same | `traceability_ok` on each entry | — | Journal yes | **Yes** from journal; partial to recompute |
| **36 review flags** | `apply_review_flags.py` | Journal | `phase2.review_flags` | — | Yes (embedded) | **Yes** |
| **Six excerpts / six reference decisions** | `build_annotation_excerpts.py` | Transcripts | `configs/annotations/manual_phase1.json`, `excerpt_001–006.json` | Author labels | Yes | **Yes** |
| **Triangulation 5/10/0** | `summarize_triangulation.py` | Manual workbook | `docs/TRIANGULATION_SUMMARY.md` | manual_phase1 | Doc yes | **Yes** |
| **Keyword baseline 5/6 vs 1/6** | `keyword_baseline.py` | Six excerpts | `docs/BASELINE_KEYWORD.md` | manual_phase1 | Yes | **Yes** |
| **GRACE (n=16)** | `summarize_grace.py` | Triangulation items | `configs/evaluation/grace_expansion.json`, `docs/GRACE_SUMMARY.md` | Author scoring | Yes | **Yes** |
| **Error taxonomy (n=42)** | `build_error_taxonomy.py` | Inquiry runs | `docs/ERROR_TAXONOMY.md`, `error_taxonomy_sample.json` | 9 validated | Yes | **Yes** (needs runs for full rebuild) |
| **n=50 Rubric A/B** | `build_confidence_validation_sample.py`, `rate_confidence_sample.py` | Journal | `configs/evaluation/confidence_validation_sample.json` | Author ratings | Yes | **Yes** |
| **Automated confidence κ** | `compare_confidence_signals.py` | n=50 sample | `confidence_comparison_results.json`, `confidence_llm_cache.json` | Rubric B | Yes | **Yes** (LLM re-run needs API) |
| **Clustering 20 groups** | `run_clustering.py`, `visualize_clustering.py` | Journal + embeddings | `phase1_clustering_report.json`, figures | — | Report yes; embedding cache often no | **Partial** |
| **n=60 JEE/DQ** | `run_jee_dq_human_review.py` → Audit E | Purposive 60 | `AUDIT_E_JEE_SUMMARY.csv`, `AUDIT_E_DQ_SUMMARY.csv` | Single reviewer | **Partial** | **Partial** — summaries partially tracked |
| **Faithfulness 8/25/20/7** | Audit E chain | Source passages | `AUDIT_E_TRACEABILITY_HUMAN_CLASSIFICATION.csv` | Author | Partial | **Partial** |
| **Structural 49/50** | `run_structural_reliability.py` | `structural_reliability_chunks.json` | `structural_reliability_results.json` | — | Yes | **Yes** (re-run needs API) |
| **Report-genre pilot 53 / 50 traceable** | `run_extraction.py` (no `--inquiry`) | In Brief report text | `outputs/run_20260609_081454_*`, `docs/REPORT_PILOT.md` | None | **Yes** | **Yes** |
| **Chunk/overlap sensitivity** | `experiments/chunk_overlap_sensitivity_2026-08-30/run_experiment.py` | Six excerpts | `FINAL_CHUNK_SENSITIVITY_REPORT.md`, CSVs | Gold alignment | **Yes** | **Yes** (minimum audit set committed) |
| **Model sensitivity (excerpts)** | `experiments/model_sensitivity_2026-08-31/run_experiment.py` | Six excerpts | `05_FINAL_MODEL_SENSITIVITY_REPORT.md`, CSVs | Same | **Yes** | **Yes** (minimum audit set committed) |
| **Model sensitivity (extended)** | `run_extension.py` | Six excerpts | `12_EXTENDED_MODEL_SENSITIVITY_REPORT.md` | Same | **Yes** | **Yes** |
| **Full-hearing Terra 2/6** | `run_full_hearing_confirmation.py` | 3 full hearing `.txt` | `17_FULL_HEARING_CONFIRMATION_REPORT.md`, Terra raw JSON | Six decisions | **Yes** | **Yes** |
| **Full-hearing Sol** | Same (failed/incomplete) | Same | `*_invalidated_*`, `*_INCOMPLETE.json` | — | **Yes** (transparency only) | **Not valid evidence** — do not cite as performance |

### Release status (Aug 2026 supplementary evidence)

The minimum dissertation-supporting experiment evidence for chunk/overlap and model sensitivity is **committed** in the final reproducibility release under `experiments/`. Use tag `msc-dissertation-reproducibility-2026-08-31` or the public-safe tag `msc-dissertation-public-release-2026-08-31` after path sanitisation.

See `docs/repository_release/DUAL_RELEASE_AUDIT.md` for the full release manifest.

---

## 7. Supplementary experiments (Aug 2026)

These analyses were conducted **after** the 414-entry journal was frozen. They do not modify the canonical dataset. They test whether results are sensitive to chunking parameters and model choice.

**Committed in the reproducibility release:** the minimum audit-safe file sets for both experiment directories are tracked in git (see `docs/repository_release/DUAL_RELEASE_AUDIT.md` Part 3). Tag `msc-dissertation-reproducibility-2026-08-31` includes this evidence; tag `msc-dissertation-public-release-2026-08-31` is the public-safe snapshot after path sanitisation.

### 7.1 Chunk and overlap sensitivity

**Location:** `experiments/chunk_overlap_sensitivity_2026-08-30/`

| Item | Path |
|------|------|
| Pre-registered protocol | `00_PROTOCOL_PRE_REGISTERED.md` |
| Stage results | `01_`–`03_*.csv`, `FINAL_CHUNK_SENSITIVITY_REPORT.md` |
| Gold alignment | `GOLD_DECISION_ALIGNMENT.csv` |
| Runner | `run_experiment.py` |

**Minimum files for audit** (exclude Word repair debris and integration scratch scripts): protocol, CSV/MD reports, `GOLD_DECISION_ALIGNMENT.csv`, `runs/stage1_w*.json`, and the three Python runners.

### 7.2 Model sensitivity

**Location:** `experiments/model_sensitivity_2026-08-31/`

| Analysis | Key report | Notes |
|----------|------------|-------|
| Excerpt panel (multiple models) | `05_FINAL_MODEL_SENSITIVITY_REPORT.md` | Bounded six-excerpt comparison |
| Extended current-model run | `12_EXTENDED_MODEL_SENSITIVITY_REPORT.md` | Includes `gpt-5.6-*` aliases |
| Full-hearing confirmation | `17_FULL_HEARING_CONFIRMATION_REPORT.md` | **Only Terra 2/6 is valid full-hearing evidence** |

**Scientific distinction (important):**

| Run | Status | Use in dissertation? |
|-----|--------|----------------------|
| `gpt-5.6-terra` full-hearing | **Valid** | Yes — 2/6 recovery vs six reference decisions |
| `gpt-5.6-sol` full-hearing | **Invalid / incomplete** | **No** — failed and partial runs are transparency artefacts only |
| `gpt-5.6-sol` excerpt-level | Valid within excerpt bounds | Yes — 4/6 on bounded excerpts only |

Invalidated/incomplete Sol files (`*_invalidated_*`, `*_INCOMPLETE.json`) may be retained for audit transparency but must **not** be interpreted as model-performance evidence.

Large `raw_responses_extended/` trees are optional; manifest CSVs (`04_`, `11_`) usually suffice for verification.

---

## 8. Reproducibility limits

### 8.1 What is frozen and authoritative

| Artefact | Rule |
|----------|------|
| `phase1_decision_journal.json` | **Do not overwrite** when verifying dissertation claims |
| Human rating JSON (n=50, n=60, six excerpts) | Authoritative; not re-generated |
| Audit E summary CSVs | Authoritative for published JEE/DQ/faithfulness counts |

### 8.2 What will not be byte-identical on re-run

| Analysis | Why |
|----------|-----|
| LLM extraction (`run_extraction.py`) | Hosted `gpt-4o-mini` snapshots change; temperature 0 does not guarantee identical routing |
| LLM confidence second pass | Same model dependency; cached in `confidence_llm_cache.json` |
| Embedding clustering | Vectors depend on embedding API version; 16 MB cache may be local-only |
| Structural reliability | Temperature 0.3; schema stress test not a accuracy claim |
| Aug 2026 model aliases (`gpt-5.6-terra`, etc.) | Ephemeral product names; may be unavailable later |

### 8.3 What mechanical traceability does and does not mean

- **Does:** Checks that `source_quote` can be found (exact or normalised) in the **processed chunk text** used during extraction.  
- **Does not:** Prove the decision is correct policy analysis, or match PDF page numbers.  
- Failures are usually PDF-to-text layout artefacts, not missing quote fields.

### 8.4 Reproducibility classes

| Class | Meaning | Examples |
|-------|---------|----------|
| **Offline** | Deterministic on frozen files | Journal totals, review flags, rule-based confidence, pytest integrity |
| **Public download** | Needs Inquiry website PDFs | `run_pipeline.py` harvest/download/text |
| **API (non-deterministic)** | Live OpenAI calls | Re-extraction, embeddings, LLM confidence, structural test |
| **Frozen LLM output** | Historical model results treated as data | Canonical journal, Phase 1 run JSON |
| **Human adjudicated** | Researcher judgement | Excerpts, n=50, n=60, faithfulness codes |

---

## 9. Adapting the pipeline to a new corpus

The case-study-specific parts are **UK COVID-19 Inquiry ingestion** (`inquiry_harvest.py`, `inquiry_download.py`, `configs/inquiry_*.json`, `--inquiry` prompt). A new project (e.g. outbreak investigation reports) should reuse the generic pattern:

### 9.1 Reusable components

| Component | Module / script | Adapt how |
|-----------|-----------------|-----------|
| PDF → text | `pdf_text.py` | Point at your PDFs |
| Chunk + extract + traceability | `extraction.py`, `run_extraction.py` | New prompt template or `--inquiry` off |
| Merge runs → journal | `journal.py`, `build_phase1_journal.py` | New run registry JSON |
| Review flags | `review_flags.py`, `apply_review_flags.py` | Tune flag rules if needed |
| Confidence heuristics | `confidence_signals.py` | Optional |
| Evaluation pattern | Sample builder + rating scripts | **New samples** — do not reuse dissertation labels |

### 9.2 Suggested workflow for a new corpus

1. **Ingest** — Implement your own download/metadata step, or place `.txt` files in a `data/processed/<corpus>/` tree.  
2. **Extract** — `python scripts/run_extraction.py path/to/doc.txt --label mycorpus`  
3. **Register runs** — Create a new JSON modelled on `configs/phase1_journal_runs.json`.  
4. **Build journal** — Adapt `build_phase1_journal.py` or call `journal.py` merge functions directly.  
5. **Evaluate** — Design new human samples; reuse rubric **structure** (valid-decision × evidence-strength) not the COVID labels.  
6. **Document** — Record model name, temperature, chunk size in each run’s `manifest.json`.

### 9.3 Do not carry over by default

- `data/manifests/phase1_decision_journal.json` (414 COVID entries)  
- `configs/evaluation/confidence_validation_sample.json` (n=50 COVID labels)  
- n=60 JEE/DQ adjudication files  
- COVID-specific clustering labels  
- Dissertation prose and sensitivity experiment results  
- Supervisor meeting notes and personal paths in manifests  

---

## 10. Security and privacy

| Item | Handling |
|------|----------|
| `.env` / API keys | Never commit; use `.env.example` |
| Meeting transcripts, supervisor material | Not for public release (`dissertation/Meeing*.txt`, etc.) |
| Other students' work | Exclude from any shared repository |
| Absolute local paths in CSVs | `data/manifests/inquiry_module2_phase1.csv` may contain `C:\...` paths — regenerate via `run_pipeline.py` on a new machine |
| Virtual environments | `.venv/`, stray `dissertation/Lib/` — never commit |

Full audit: `docs/examiner_evidence/SECURITY_AND_PRIVACY_NOTE.md` and `docs/repository_release/DUAL_RELEASE_AUDIT.md` Part 4.

---

## 11. Quick command cheat sheet

```bash
# Offline verification
python -m pytest tests/test_appendix_a_excerpt_coordinates.py \
  tests/test_phase2a_flag_counts_and_wordcount.py tests/test_leak_term_scan.py -q

# Rebuild text from public PDFs (no API)
python scripts/run_pipeline.py --stage download
python scripts/run_pipeline.py --stage text

# Extract one document (API)
python scripts/run_extraction.py data/processed/inquiry/document/<slug>.txt --label phase1 --inquiry

# Re-apply review flags on frozen journal (offline)
python scripts/apply_review_flags.py

# Regenerate evaluation summaries (mostly offline)
python scripts/summarize_triangulation.py
python scripts/keyword_baseline.py
python scripts/summarize_grace.py

# Regenerate Audit E aggregates (offline)
python scripts/run_post60_analytical_audit_E_final.py
```

---

## 12. Related documents

| Document | Purpose |
|----------|---------|
| [../README.md](../README.md) | Project overview and navigation |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Schema, rubrics, evaluation scales |
| [ANNOTATION_RUBRIC.md](ANNOTATION_RUBRIC.md) | Manual annotation protocol |
| [INQUIRY_EXTRACTION_SUMMARY.md](INQUIRY_EXTRACTION_SUMMARY.md) | Per-hearing extraction statistics |
| [examiner_evidence/DATA_LINEAGE.md](examiner_evidence/DATA_LINEAGE.md) | Compact source-to-findings diagram |
| [repository_release/DUAL_RELEASE_AUDIT.md](repository_release/DUAL_RELEASE_AUDIT.md) | Release readiness and file classification |
| [examiner_evidence/REPRODUCTION_RUNBOOK.md](examiner_evidence/REPRODUCTION_RUNBOOK.md) | Short examiner-oriented command list (legacy; this guide supersedes it) |

---

*Last updated: 2026-08-31 — aligned with handbook-compliant dissertation and dual-release audit.*
