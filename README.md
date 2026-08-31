# AI-assisted decision journals

Research software that extracts **candidate policy decisions** and supporting **evidence quotes** from long-form emergency-response text (public inquiry hearing transcripts), checks whether each quote can be found in the source text, and evaluates extraction quality with human rubrics and automated checks.

**Case study (MSc dissertation):** UK COVID-19 Inquiry Module 2 — eight public hearing transcripts → **414** frozen candidate entries, with manual and automated evaluation reported in the dissertation.

**Author:** Akeeb Idowu Lawal · University of Surrey · MSc Artificial Intelligence (EEEM004)

**Reproducibility release:** tag `msc-dissertation-reproducibility-2026-08-31` (commit `9e4452a`); public-safe paths in tag `msc-dissertation-public-release-2026-08-31`. Frozen journal SHA-256: `814cc7c47a9f75bfc0a6c7b693feec7073e59131398d89fab7c9111fbb2e5e06` (414 entries). Supplementary robustness experiment evidence is included under `experiments/`.

---

## What this repository contains

| Layer | What it is | Where to look |
|-------|------------|---------------|
| **Pipeline code** | PDF/text ingestion, LLM extraction, journal merge, review flags, clustering, evaluation scripts | `src/decision_journal/`, `scripts/` |
| **Frozen research dataset** | The fixed 414-entry decision journal used in all dissertation analyses | `data/manifests/phase1_decision_journal.json` |
| **Human evaluation records** | Six annotated excerpts, n=50 confidence sample, n=60 framework review | `configs/annotations/`, `configs/evaluation/` |
| **Result summaries** | Markdown reports for triangulation, baseline, taxonomy, pilots | `docs/*.md` |
| **Dissertation** | Source chapters and submitted Word document | `dissertation/` |
| **Supplementary robustness experiments** | These exploratory experiments examined sensitivity to chunk/overlap settings and model choice. They were conducted after the main Phase 1 dataset had been fixed and did not alter the 414-entry reference dataset. | `experiments/` (minimum dissertation-supporting evidence committed) |

This is a **CLI research prototype**, not a deployed web application. There is no fine-tuned model and no retrieval-augmented generation layer — each text chunk is sent to the LLM in full with a structured JSON schema and mandatory `source_quote` fields.

---

## Start here (new researcher)

1. **Understand the system** — read [How data flows](#how-data-flows-through-the-system) below, then [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for technical detail.
2. **Verify dissertation numbers without an API key** — follow [`docs/REPRODUCIBILITY_GUIDE.md`](docs/REPRODUCIBILITY_GUIDE.md) § “Inspect frozen results offline”.
3. **Find a specific dissertation claim** — use the mapping table in [`docs/REPRODUCIBILITY_GUIDE.md`](docs/REPRODUCIBILITY_GUIDE.md) § “Dissertation results index”.
4. **Re-run extraction on new documents** — see [`docs/REPRODUCIBILITY_GUIDE.md`](docs/REPRODUCIBILITY_GUIDE.md) § “Adapting the pipeline to a new corpus”.

Historical development notes (internal revision logs, packaging folders) live under `docs/revision_control/` and `docs/examiner_evidence/` for audit only — they are **not** the primary navigation path.

---

## Setup

```bash
# From the repository root (Windows PowerShell or Unix shell)
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env    # then add your OPENAI_API_KEY
```

You do **not** need an API key to inspect frozen JSON, run integrity tests, or recalculate counts from committed evaluation files.

---

## How data flows through the system

```
Public source documents (PDFs)
        │
        ▼
  Text extraction + inquiry-specific cleanup
        │
        ▼
  Sentence-based chunking (default: 7 sentences, overlap 2)
        │
        ▼
  LLM extraction (structured JSON per chunk: decision, evidence, source_quote)
        │
        ▼
  Deduplication + mechanical traceability check (quote found in chunk text?)
        │
        ▼
  Per-document run folders (outputs/run_<timestamp>_<label>/)
        │
        ▼
  Canonical decision journal — ONE frozen file for all downstream work
        (data/manifests/phase1_decision_journal.json — 414 entries)
        │
        ├── Review flags (procedural wording, possible duplicates)
        ├── Human confidence validation (n=50, dual rubrics)
        ├── Automated confidence comparison (rules + LLM vs human)
        ├── Embedding clustering (20 theme groups)
        ├── Manual excerpt evaluation (6 excerpts, triangulation, GRACE)
        ├── Extended audits (n=60 JEE / Decision Quality / faithfulness)
        └── Supplementary sensitivity studies (chunk size, model choice)
```

**Important design rule:** After the journal was frozen, every dissertation analysis reads **that single journal file** (or derivatives stored in `configs/evaluation/`). Analyses do not silently re-extract the corpus.

---

## Main components

### Python package — `src/decision_journal/`

| Module | Role |
|--------|------|
| `extraction.py` | Prompts, chunking, LLM calls, traceability validation, deduplication |
| `pdf_text.py` | PDF → plain text |
| `journal.py` | Load and validate the canonical journal |
| `review_flags.py` | Non-destructive quality flags on journal entries |
| `confidence_signals.py` | Rule-based and LLM-based confidence heuristics |
| `clustering.py` | Embedding + agglomerative clustering |
| `structural_reliability.py` | Schema robustness stress test |
| `inquiry_*.py` | UK COVID-19 Inquiry API harvest and download (case-study specific) |

### Runnable scripts — `scripts/`

Scripts are grouped by purpose in [`docs/REPRODUCIBILITY_GUIDE.md`](docs/REPRODUCIBILITY_GUIDE.md). In practice, most users need only a subset:

| Purpose | Key scripts |
|---------|-------------|
| **Ingest case-study corpus** | `run_pipeline.py`, `pdf_to_text.py` |
| **Extract decisions** | `run_extraction.py` |
| **Build / verify frozen journal** | `build_phase1_journal.py`, `verify_phase1_data.py` |
| **Enrich journal** | `apply_review_flags.py`, `run_clustering.py`, `visualize_clustering.py` |
| **Human validation workflow** | `build_confidence_validation_sample.py`, `rate_confidence_sample.py`, `compare_confidence_signals.py` |
| **Manual evaluation summaries** | `build_annotation_excerpts.py`, `summarize_triangulation.py`, `keyword_baseline.py`, `summarize_grace.py`, `build_error_taxonomy.py` |
| **Extended human audit (n=60)** | `run_jee_dq_human_review.py`, `run_post60_analytical_audit_E_final.py` |
| **Supplementary tests** | `run_structural_reliability.py` |
| **Integrity checks** | `pytest` (see reproducibility guide) |

Many other scripts under `scripts/` build dissertation Word files, presentation decks, or one-off packaging — they are **not** required to understand or verify the research pipeline.

### Configuration and frozen data

| Path | Role |
|------|------|
| `configs/phase1_journal_runs.json` | Maps the eight canonical extraction runs to the 414-entry journal |
| `configs/inquiry_*.json` | Case-study corpus selection (Module 2 hearings) |
| `configs/annotations/manual_phase1.json` | Six manually annotated excerpts |
| `configs/evaluation/*.json` | Frozen evaluation samples and computed metrics |
| `data/manifests/phase1_decision_journal.json` | **Authoritative dataset** (414 candidates; 351 pass traceability) |
| `data/manifests/phase1_clustering_report.json` | Clustering output (20 groups) |
| `data/processed/inquiry/` | Processed transcript text used in the released study |
| `data/raw/inquiry/` | Source PDFs (usually local only; public URLs in manifest) |

---

## Dissertation results at a glance

| Result reported in dissertation | Primary artefact |
|-----------------------------------|------------------|
| 414 candidate entries | `data/manifests/phase1_decision_journal.json` |
| 351/414 mechanical traceability | `totals` field in journal; per-entry `traceability_ok` |
| 36 review flags | `phase2.review_flags` on journal entries |
| Six manual excerpts / reference decisions | `configs/annotations/manual_phase1.json`, `configs/annotations/excerpts/` |
| Triangulation (5 agreement / 10 silence / 0 dissonance) | `docs/TRIANGULATION_SUMMARY.md` |
| Keyword baseline (5/6 vs 1/6) | `docs/BASELINE_KEYWORD.md` |
| GRACE-adapted assessment (n=16) | `docs/GRACE_SUMMARY.md`, `configs/evaluation/grace_expansion.json` |
| Error taxonomy (n=42) | `docs/ERROR_TAXONOMY.md` |
| n=50 dual-rubric validation (e.g. 21/50 no×high) | `configs/evaluation/confidence_validation_sample.json` |
| Automated confidence (κ ≈ 0.48 / 0.39) | `configs/evaluation/confidence_comparison_results.json` |
| Clustering (20 groups, n=414) | `data/manifests/phase1_clustering_report.json`, `outputs/figures/` |
| n=60 JEE / Decision Quality / faithfulness | `outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/` |
| Structural reliability (49/50) | `configs/evaluation/structural_reliability_results.json` |
| Report-genre pilot (53 candidates) | `docs/REPORT_PILOT.md` |
| Chunk/overlap sensitivity | `experiments/chunk_overlap_sensitivity_2026-08-30/` |
| Model sensitivity + limited full-hearing check | `experiments/model_sensitivity_2026-08-31/` |

Full traceability (scripts, inputs, what is committed vs local) is in [`docs/REPRODUCIBILITY_GUIDE.md`](docs/REPRODUCIBILITY_GUIDE.md).

### Primary vs supplementary analyses

| **Primary** (define the frozen dataset and main evaluation) | **Supplementary** (robustness / sensitivity; do not redefine the 414-entry set) |
|-------------------------------------------------------------|----------------------------------------------------------------------------------|
| Eight-hearing extraction → 414 journal | Report-genre pilot on a separate In Brief document |
| Six-excerpt manual triangulation | Error taxonomy extended sample (n=42) |
| n=50 confidence validation | Structural reliability stress test |
| n=60 JEE/DQ/faithfulness audit | Chunk/overlap sensitivity |
| Clustering of n=414 | Model comparison on six excerpts |
| Keyword baseline on six excerpts | Limited full-hearing confirmation (three hearings, one valid model run) |

---

## Typical command sequences

### A. Inspect frozen results (no API — recommended first step)

```bash
python -m pytest tests/test_appendix_a_excerpt_coordinates.py \
  tests/test_phase2a_flag_counts_and_wordcount.py \
  tests/test_leak_term_scan.py -q
```

Then recalculate headline counts from JSON — commands in [`docs/REPRODUCIBILITY_GUIDE.md`](docs/REPRODUCIBILITY_GUIDE.md).

### B. Rebuild case-study corpus from public sources

```bash
python scripts/run_pipeline.py --stage harvest
python scripts/run_pipeline.py --stage download
python scripts/run_pipeline.py --stage text
python scripts/verify_phase1_data.py
```

### C. Extract decisions from one transcript (requires API)

```bash
python scripts/run_extraction.py data/processed/inquiry/document/<slug>.txt \
  --label phase1 --inquiry
```

### D. Reproduce journal merge (only if you have the eight canonical run folders)

```bash
python scripts/build_phase1_journal.py
python scripts/apply_review_flags.py
```

**Do not overwrite** `data/manifests/phase1_decision_journal.json` when verifying historical dissertation claims. The committed journal is authoritative.

### E. Re-run downstream analyses on the frozen journal

```bash
python scripts/build_confidence_validation_sample.py   # design only — sample already frozen
python scripts/compare_confidence_signals.py         # needs API for LLM pass unless cache present
python scripts/run_clustering.py                     # needs API for embeddings unless cache present
python scripts/run_structural_reliability.py         # needs API
python scripts/summarize_triangulation.py
python scripts/keyword_baseline.py
```

---

## What cannot be reproduced exactly

- **LLM extraction outputs** — Phase 1 used `gpt-4o-mini` at temperature 0; hosted model snapshots change over time. Re-running extraction may yield different decisions.
- **Human judgements** — Rubric ratings, triangulation codes, JEE/DQ, and faithfulness classifications are stored in frozen JSON/CSV; they are not regenerated by scripts.
- **Embedding clustering** — Re-clustering needs the embedding cache or new API calls; cluster labels are navigation aids, not a validated ontology.
- **Supplementary model runs** — Robustness experiments used then-current model aliases (`gpt-5.6-terra`, etc.) that may not remain available.

See [`docs/REPRODUCIBILITY_GUIDE.md`](docs/REPRODUCIBILITY_GUIDE.md) for the full limits table and what each analysis class requires (offline / download / API / human records).

---

## Adapting to a new corpus

The reusable pattern (independent of the UK COVID-19 case study):

1. Place source documents as `.txt` or convert PDFs with `pdf_text.py`.
2. Run `run_extraction.py` **without** `--inquiry` for a generic prompt, or adapt `INQUIRY_PROMPT_TEMPLATE` in `extraction.py` for your domain.
3. Merge runs with a new journal config (copy the pattern in `build_phase1_journal.py` and `journal.py`).
4. Apply `apply_review_flags.py` for non-destructive quality markers.
5. Build your own evaluation samples — do not reuse the dissertation’s n=50/n=60 labels.

Case-study-specific ingestion (`inquiry_harvest.py`, `inquiry_download.py`, Module 2 configs) should be replaced for a different document source (e.g. outbreak investigation reports).

---

## Repository layout

```
.
├── src/decision_journal/     # Core library
├── scripts/                  # Command-line tools
├── configs/                  # Settings, annotations, evaluation manifests
├── data/
│   ├── manifests/            # Committed metadata + frozen journal
│   ├── raw/                  # Source PDFs (local)
│   └── processed/            # Processed transcript text used in the released study
├── outputs/                  # Extraction runs, figures, audit workspaces
├── experiments/              # Supplementary sensitivity studies
├── docs/                     # Summaries, architecture, reproducibility guide
├── dissertation/             # Thesis source and submission files
├── tests/                    # Integrity and coordinate tests
└── demo/                     # Small offline demonstration assets
```

---

## Further reading

| Document | Audience |
|----------|----------|
| [`docs/REPRODUCIBILITY_GUIDE.md`](docs/REPRODUCIBILITY_GUIDE.md) | **Start here** for commands, claim index, and reproduction classes |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Technical architecture, schema, evaluation scales |
| [`docs/ANNOTATION_RUBRIC.md`](docs/ANNOTATION_RUBRIC.md) | Manual annotation protocol |
| [`docs/repository_release/DUAL_RELEASE_AUDIT.md`](docs/repository_release/DUAL_RELEASE_AUDIT.md) | Release-readiness audit (MSc vs future reuse) |
| [`docs/examiner_evidence/`](docs/examiner_evidence/) | Compact evidence pack for examiners (secondary to guide above) |
| [`data/raw/README.md`](data/raw/README.md) | How to obtain and place source PDFs |

---

## Citation and source materials

MSc dissertation: *AI-assisted decision journaling from UK COVID-19 Inquiry transcripts* — Akeeb Idowu Lawal, University of Surrey, 2026.

Source documents are public UK COVID-19 Inquiry materials. Do not commit API keys (`.env` is gitignored; use `.env.example` as a template).
