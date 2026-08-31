# AI-assisted decision journals

**Author:** Akeeb Idowu Lawal · University of Surrey · MSc Artificial Intelligence (EEEM004)

This repository supports an MSc dissertation on whether large language models (LLMs) can help researchers build **traceable candidate decision journals** from long public-inquiry hearing transcripts. It is a **command-line research prototype**, not a deployed web application.

---

## What this project does

During emergencies, decision-makers often need a clear record of what was decided, when, and on what evidence. A **decision journal** is a structured record of that kind. This project asks whether an LLM can **propose** candidate journal entries from long transcripts: each entry includes a decision statement, supporting evidence, and a **source quote** that can be checked against the original text.

The software:

1. Takes long documents (PDFs or plain text).
2. Splits them into overlapping sentence-based chunks.
3. Asks an LLM to return structured JSON for each chunk.
4. Checks mechanically whether each quoted passage appears in the chunk text (**traceability**).
5. Merges results into a single dataset for human review and evaluation.

**Important:** The outputs are **candidate** decision-journal entries. They are **not** verified policy decisions. Human review remains necessary before any entry could be treated as authoritative.

---

## What problem this addresses

Manual decision journaling from long transcripts is slow and does not scale easily. Automated keyword search misses context and cannot reliably produce structured entries with linked evidence. This project tests a middle path: use an LLM to **propose** entries under a fixed schema, then evaluate how often those proposals are traceable, how they compare to human judgement, and how sensitive results are to chunking and model choice.

The case study uses **UK COVID-19 Inquiry Module 2** public hearing transcripts — eight hearings processed into text, then analysed as one fixed dataset.

---

## What was done in the MSc study

The dissertation workflow had three broad stages:

1. **Extraction** — Run the pipeline on eight public hearings to produce a **fixed set of 414 candidate entries**. This file was then locked for all later analysis. Nothing in the supplementary robustness work changed these 414 entries.
2. **Evaluation** — Human and automated checks on samples from that fixed set: six annotated excerpts, a stratified sample of 50 entries, clustering of all 414 entries, and an extended human review of 60 purposively selected entries.
3. **Supplementary robustness experiments** — Exploratory checks of whether results were sensitive to chunk/overlap settings and model choice, conducted **after** the 414-entry dataset was fixed.

Submitted thesis and supporting files are under `dissertation/`. The fixed candidate dataset is `data/manifests/phase1_decision_journal.json`.

---

## What the study found

Headline results reported in the dissertation (full artefact mapping in [`docs/REPRODUCIBILITY_GUIDE.md`](docs/REPRODUCIBILITY_GUIDE.md)):

| Finding | Value | Where to verify |
|---------|-------|-----------------|
| Candidate entries extracted | **414** | `data/manifests/phase1_decision_journal.json` |
| Quotes found in source chunk text (mechanical traceability) | **351/414** | Same file — `traceability_ok` per entry |
| Entries flagged for review (non-destructive) | **36** | `phase2.review_flags` on journal entries |
| Six-excerpt manual triangulation | **5 agreement / 10 silence / 0 dissonance** | [`docs/TRIANGULATION_SUMMARY.md`](docs/TRIANGULATION_SUMMARY.md) |
| Keyword baseline vs LLM on six excerpts | **5/6 vs 1/6** | [`docs/BASELINE_KEYWORD.md`](docs/BASELINE_KEYWORD.md) |
| GRACE-adapted assessment | **n = 16** | [`docs/GRACE_SUMMARY.md`](docs/GRACE_SUMMARY.md) |
| Error taxonomy extended sample | **n = 42** | [`docs/ERROR_TAXONOMY.md`](docs/ERROR_TAXONOMY.md) |
| Dual-rubric validation sample | **n = 50** (e.g. **21/50** no × high) | `configs/evaluation/confidence_validation_sample.json` |
| Automated confidence vs human rubrics | **κ ≈ 0.48 / 0.39** | `configs/evaluation/confidence_comparison_results.json` |
| Theme grouping of all 414 entries | **20 groups** | `data/manifests/phase1_clustering_report.json` |
| Extended human framework review | **n = 60** | `outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/` |
| Structural reliability (schema adherence under perturbation) | **49/50** | `configs/evaluation/structural_reliability_results.json` |
| Report-genre pilot (separate document) | **53 candidates** | [`docs/REPORT_PILOT.md`](docs/REPORT_PILOT.md) |

### Main dissertation analyses vs supplementary robustness checks

| **Main dissertation analyses** (reported in the dissertation) | **Supplementary robustness checks** (do not change the 414 entries) |
|---------------------------------------------------------------|-----------------------------------------------------------------------|
| Eight-hearing extraction → 414 candidates | Report-genre pilot on a separate In Brief document |
| Six-excerpt manual triangulation | Error taxonomy extended sample (n = 42) |
| n = 50 confidence validation | Structural reliability stress test |
| Extended human review (n = 60) | Chunk/overlap sensitivity |
| Clustering of n = 414 | Model comparison on six excerpts |
| Keyword baseline on six excerpts | Limited full-hearing confirmation (three hearings; one valid model run) |

**Supplementary robustness experiments** (`experiments/`) tested chunk/overlap settings and model choice. They were exploratory and did **not** alter the 414-entry reference dataset. For model sensitivity, only the **Terra** full-hearing run (2/6 recovery) is valid performance evidence; the **Sol** full-hearing run failed and is retained for transparency only — **not** as model-performance evidence.

### What traceability does and does not mean

- **Does:** Checks that the `source_quote` can be found in the processed chunk text used during extraction.
- **Does not:** Prove that an entry is a valid decision-journal item, correct policy analysis, or faithful paraphrase of intent. Many traceable quotes still failed human validity checks (e.g. 21/50 no × high in the n = 50 sample).

---

## How the system works

```
Public source documents (PDFs)
        │
        ▼
  Text extraction and cleanup
        │
        ▼
  Sentence-based chunking (default: 7 sentences, overlap 2)
        │
        ▼
  LLM extraction — structured JSON per chunk (decision, evidence, source_quote)
        │
        ▼
  Deduplication + mechanical traceability check
        │
        ▼
  Per-document run folders (outputs/run_<timestamp>_<label>/)
        │
        ▼
  Fixed candidate dataset — one JSON file for all downstream work
        (data/manifests/phase1_decision_journal.json — 414 entries)
        │
        ├── Review flags (procedural wording, possible duplicates)
        ├── Human confidence validation (n = 50)
        ├── Automated confidence comparison (rules + LLM vs human)
        ├── Embedding-based grouping (agglomerative clustering → 20 theme groups)
        ├── Manual excerpt evaluation (6 excerpts)
        ├── Extended human review (n = 60)
        └── Supplementary robustness experiments (chunk size, model choice)
```

**Design rule:** After the 414-entry dataset was fixed, every dissertation analysis reads **that single file** or **derivatives** (outputs produced from it, stored in `configs/evaluation/` and related folders). Analyses do not silently re-extract the corpus.

There is no fine-tuned model and no retrieval-augmented generation layer. Each chunk is sent to the LLM in full with a structured schema and mandatory `source_quote` field.

**Structural reliability** in this project means checking whether repeated model outputs still followed the required JSON structure when inputs were perturbed — a format-stability check, not a claim about decision quality.

For schema detail, rubrics, and evaluation scales, see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and [`docs/ANNOTATION_RUBRIC.md`](docs/ANNOTATION_RUBRIC.md).

---

## How to inspect or reproduce the study

You can verify most dissertation numbers **without an API key** by reading committed JSON/CSV files and running offline tests. Re-running LLM extraction may yield different outputs because hosted models change over time.

### Setup

```bash
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env    # add OPENAI_API_KEY only if re-running LLM steps
```

### Task-based guide

| If you want to… | Start here |
|-----------------|------------|
| **Obtain or inspect processed transcripts** | `data/processed/inquiry/` (committed for this release). To rebuild from public PDFs: `scripts/run_pipeline.py` — see [`data/raw/README.md`](data/raw/README.md) |
| **Split text into overlapping chunks and extract candidates** | `scripts/run_extraction.py` (requires API). Core logic: `src/decision_journal/extraction.py` |
| **Check source traceability** | Built into extraction; counts in `phase1_decision_journal.json` (`traceability_ok`) |
| **Build or inspect the fixed 414-entry dataset** | `data/manifests/phase1_decision_journal.json`. Merge script: `scripts/build_phase1_journal.py` — **do not overwrite** this file when verifying dissertation claims |
| **Review or evaluate candidates** | Human labels: `configs/annotations/`, `configs/evaluation/`. Summaries: `docs/TRIANGULATION_SUMMARY.md`, `docs/BASELINE_KEYWORD.md`, etc. Extended review outputs: `outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/` |
| **Inspect supplementary robustness experiments** | `experiments/chunk_overlap_sensitivity_2026-08-30/`, `experiments/model_sensitivity_2026-08-31/` |
| **Run offline integrity checks** | `python -m pytest tests/test_appendix_a_excerpt_coordinates.py tests/test_phase2a_flag_counts_and_wordcount.py tests/test_leak_term_scan.py -q` |
| **Map a specific dissertation claim to files** | [`docs/REPRODUCIBILITY_GUIDE.md`](docs/REPRODUCIBILITY_GUIDE.md) — “Dissertation results index” |

### Quick offline verification

```bash
python -m pytest tests/test_appendix_a_excerpt_coordinates.py \
  tests/test_phase2a_flag_counts_and_wordcount.py \
  tests/test_leak_term_scan.py -q
```

Recalculate headline counts from JSON — commands in [`docs/REPRODUCIBILITY_GUIDE.md`](docs/REPRODUCIBILITY_GUIDE.md) § “Inspect frozen results offline”.

### What cannot be reproduced exactly

- **LLM extraction** — Phase 1 used `gpt-4o-mini` at temperature 0; hosted snapshots change.
- **Human judgements** — Ratings and classifications are stored in frozen files; scripts do not regenerate them.
- **Embedding-based clustering** — Re-clustering needs the embedding cache or new API calls; cluster labels are navigation aids, not a validated ontology.
- **Supplementary model runs** — Robustness experiments used then-current model aliases (`gpt-5.6-terra`, etc.) that may not remain available.

See [`docs/REPRODUCIBILITY_GUIDE.md`](docs/REPRODUCIBILITY_GUIDE.md) for the full limits table.

---

## Using the approach on another corpus

The reusable pattern does not depend on the UK COVID-19 case study:

1. Place source documents as `.txt`, or convert PDFs with `scripts/pdf_to_text.py`.
2. Run `scripts/run_extraction.py` **without** `--inquiry` for a generic prompt, or adapt the prompt template in `src/decision_journal/extraction.py` for your domain.
3. Merge extraction runs into a new journal file (copy the pattern in `scripts/build_phase1_journal.py` and `src/decision_journal/journal.py`).
4. Apply `scripts/apply_review_flags.py` for non-destructive quality markers.
5. Design **new** human evaluation samples — do not reuse this dissertation’s n = 50 / n = 60 labels.

Replace case-study-specific ingestion (`inquiry_harvest.py`, `inquiry_download.py`, `configs/inquiry_*.json`) when working with a different document source (e.g. outbreak investigation reports).

Full step-by-step guidance: [`docs/REPRODUCIBILITY_GUIDE.md`](docs/REPRODUCIBILITY_GUIDE.md) § “Adapting the pipeline to a new corpus”.

---

## Repository contents

| What | Where |
|------|-------|
| Pipeline code | `src/decision_journal/`, `scripts/` |
| Fixed 414-entry candidate dataset | `data/manifests/phase1_decision_journal.json` |
| Processed transcript text (released study) | `data/processed/inquiry/` |
| Human evaluation records | `configs/annotations/`, `configs/evaluation/` |
| Result summaries | `docs/*.md` |
| Dissertation | `dissertation/` |
| Supplementary robustness experiments | `experiments/` |

```
.
├── src/decision_journal/     # Core library
├── scripts/                  # Command-line tools
├── configs/                  # Settings, annotations, evaluation manifests
├── data/
│   ├── manifests/            # Metadata + fixed candidate dataset
│   ├── raw/                  # Source PDFs (public URLs in manifest)
│   └── processed/            # Processed transcript text used in the released study
├── outputs/                  # Extraction runs, figures, review workspaces
├── experiments/              # Supplementary robustness experiments
├── docs/                     # Summaries, architecture, reproducibility guide
├── dissertation/             # Thesis source and submission files
├── tests/                    # Integrity tests
└── demo/                     # Small offline demonstration assets
```

---

## Detailed technical documentation

| Document | Purpose |
|----------|---------|
| [`docs/REPRODUCIBILITY_GUIDE.md`](docs/REPRODUCIBILITY_GUIDE.md) | **Primary technical guide** — commands, claim index, reproduction classes, script reference |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | System design, schema, evaluation scales |
| [`docs/ANNOTATION_RUBRIC.md`](docs/ANNOTATION_RUBRIC.md) | Manual annotation protocol |
| [`docs/INQUIRY_EXTRACTION_SUMMARY.md`](docs/INQUIRY_EXTRACTION_SUMMARY.md) | Per-hearing extraction statistics |
| [`docs/examiner_evidence/DATA_LINEAGE.md`](docs/examiner_evidence/DATA_LINEAGE.md) | Compact source-to-findings diagram |
| [`data/raw/README.md`](data/raw/README.md) | How to obtain and place source PDFs |

Internal development notes under `docs/revision_control/` and `docs/examiner_evidence/` are retained for audit but are not the main navigation path.

---

## Reproducibility and release information

| Item | Value |
|------|-------|
| Reproducibility tag | `msc-dissertation-reproducibility-2026-08-31` (commit `9e4452a`) |
| Public-safe release tag | `msc-dissertation-public-release-2026-08-31` |
| Fixed 414-entry dataset SHA-256 | `814cc7c47a9f75bfc0a6c7b693feec7073e59131398d89fab7c9111fbb2e5e06` |
| Supplementary experiment evidence | Committed under `experiments/` |

Release audits: [`docs/repository_release/PUBLIC_GITHUB_RELEASE_CHECK.md`](docs/repository_release/PUBLIC_GITHUB_RELEASE_CHECK.md), [`docs/repository_release/DUAL_RELEASE_AUDIT.md`](docs/repository_release/DUAL_RELEASE_AUDIT.md).

---

## Citation and source materials

MSc dissertation: *AI-assisted decision journaling from UK COVID-19 Inquiry transcripts* — Akeeb Idowu Lawal, University of Surrey, 2026.

Source documents are public UK COVID-19 Inquiry materials. Do not commit API keys (`.env` is gitignored; use `.env.example` as a template).
