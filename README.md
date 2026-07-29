# AI-assisted decision journals (MSc project)

Prompt-based LLM extraction of policy **decisions** and supporting **evidence** from unstructured emergency-response text, with traceability fields for audit.

**Case study:** UK COVID-19 Inquiry public archive (pivot after interim review, April 2026).

**Status (Jun 2026):** Phase 1 complete · Phase 2a–2c complete · dissertation Ch 1–5 drafted · abstract + Word polish remaining.

**Key artefacts:** [`docs/LITERATURE_AND_SAMPLES_INDEX.md`](docs/LITERATURE_AND_SAMPLES_INDEX.md) · [`dissertation/DISSERTATION_OUTLINE_MAP.md`](dissertation/DISSERTATION_OUTLINE_MAP.md) · [`docs/PHASE2B_RATING_DECISIONS.md`](docs/PHASE2B_RATING_DECISIONS.md) · [`data/manifests/phase1_decision_journal.json`](data/manifests/phase1_decision_journal.json) (v1.2) · [`data/manifests/phase1_clustering_report.json`](data/manifests/phase1_clustering_report.json)

---

## Project phases

### Phase 1 — Extraction and evaluation (complete)

| Step | Status | Artefact |
|------|--------|----------|
| Corpus construction (8 transcripts) | Done | `data/manifests/inquiry_module2_phase1.csv` |
| Inquiry harvesting pipeline | Done | `scripts/run_pipeline.py` |
| LLM extraction (`--inquiry`) | Done | 414 decisions across 8 runs |
| Traceability validation | Done | 351/414 pass (84.8%) |
| **Canonical journal (frozen)** | Done | `data/manifests/phase1_decision_journal.json` |
| Manual triangulation (6 excerpts) | Done | 5 agreement / 10 silence / 0 dissonance |
| GRACE, baseline, error taxonomy | Done | `docs/GRACE_SUMMARY.md`, `BASELINE_KEYWORD.md`, `ERROR_TAXONOMY.md` |
| Report genre pilot | Done | `docs/REPORT_PILOT.md` — 53 decisions @ 94% |

### Phase 2 — Enrichment (same journal artefact)

| Step | Status | Command / artefact |
|------|--------|-------------------|
| **2a Review flags** | Done | `python scripts/apply_review_flags.py` — 36/414 flagged |
| **2b Confidence validation design** | Done | Rubric A/B locked; n=50 sample built |
| **2b Human rating** | Done | `configs/evaluation/confidence_validation_sample.json` — 50/50 |
| **2b Confidence comparison** | Done | `python scripts/compare_confidence_signals.py` |
| **2b Discourse pilot** | Done | `python scripts/classify_discourse.py --validate` (n=50 exploratory) |
| **2c Clustering** | Done | `python scripts/run_clustering.py` — 20 themes, journal v1.2 |
| **2c Figures** | Done | `python scripts/visualize_clustering.py` → `outputs/figures/` |

Phase 2 reads **one file only:** `data/manifests/phase1_decision_journal.json`.

---

## Repository layout

```
code/
├── src/decision_journal/   # extraction library + review_flags
├── scripts/                # runnable CLI tools
├── configs/                # default settings + evaluation manifests
├── data/manifests/         # inquiry metadata + phase1_decision_journal.json
├── data/raw/               # source PDFs (gitignored)
├── data/processed/         # extracted text (gitignored)
├── outputs/                # extraction run JSON (gitignored)
├── docs/                   # summaries, chapter drafts, architecture
└── dissertation/           # writing, Gantt, interim review
```

---

## Setup

```powershell
cd "C:\SURREY\MODULES\SEMESTER 2\MSC PROJECT\code"

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

copy .env.example .env
# Edit .env with your OPENAI_API_KEY
```

---

## Commands

### Phase 1 pipeline

```powershell
python scripts/run_pipeline.py --stage harvest
python scripts/run_pipeline.py --stage download
python scripts/run_pipeline.py --stage text
python scripts/run_extraction.py data/processed/inquiry/document/<slug>.txt --label phase1 --inquiry
python scripts/verify_phase1_data.py
```

### Canonical journal + Phase 2

```powershell
python scripts/build_phase1_journal.py          # merge 8 runs → 414 entries
python scripts/apply_review_flags.py            # Phase 2a — flags, no deletions
python scripts/build_confidence_validation_sample.py   # Phase 2b — n=50 sample
python scripts/rate_confidence_sample.py --checklist   # Phase 2b — human rating
python scripts/rate_confidence_sample.py --summary     # progress + A×B cross-tab
python scripts/compare_confidence_signals.py           # Phase 2b — rule + LLM vs human B
python scripts/classify_discourse.py --validate        # exploratory discourse tags (n=50)
python scripts/run_clustering.py                       # Phase 2c — cluster 414 entries
python scripts/visualize_clustering.py                 # thesis clustering figures
python scripts/run_structural_reliability.py --build-manifest  # 10 fixed chunks
python scripts/run_structural_reliability.py           # structural consistency mini-test
```

### Evaluation summaries

```powershell
python scripts/summarize_triangulation.py
python scripts/run_benchmark.py
```

---

## Dissertation writing

| Chapter | Draft starter | Populate now? |
|---------|---------------|---------------|
| **Ch 3 Methods** | [`dissertation/CHAPTER_3_METHODS.md`](dissertation/CHAPTER_3_METHODS.md) | Yes |
| **Ch 4 Results** | [`dissertation/CHAPTER_4_RESULTS.md`](dissertation/CHAPTER_4_RESULTS.md) | §4.1–4.10 drafted; polish + Ch 5 |
| **Ch 5 Discussion** | [`dissertation/CHAPTER_5_DISCUSSION.md`](dissertation/CHAPTER_5_DISCUSSION.md) | §5.1–5.4 drafted; abstract next |

**Critical path:** Abstract → references → Word build → submission.

Completed work log: [`docs/PROGRESS.md`](docs/PROGRESS.md) · Architecture: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

**Annotation guidance:** [`docs/ANNOTATION_SESSION_NOTES.md`](docs/ANNOTATION_SESSION_NOTES.md) · [`docs/ANNOTATION_RUBRIC.md`](docs/ANNOTATION_RUBRIC.md)
