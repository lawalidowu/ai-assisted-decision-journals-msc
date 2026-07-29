# Examiner evidence pack — AI-assisted decision journals

**Project:** AI-assisted decision journaling from UK COVID-19 Inquiry Module 2 transcripts  
**Author:** Akeeb Idowu Lawal · University of Surrey MSc  
**Branch freeze context:** Wave 2 commit `ee02346` on `distinction/final-integrity-fixes`  
**Standing rule:** LLM regeneration is **not** expected to be byte-identical.

## Five-minute examiner path

1. Read this page (2 min).
2. Open the frozen journal: [`data/manifests/phase1_decision_journal.json`](../../data/manifests/phase1_decision_journal.json) — **414** candidates; **351** pass mechanical traceability (`totals`).
3. Open n=50 ratings: [`configs/evaluation/confidence_validation_sample.json`](../../configs/evaluation/confidence_validation_sample.json) — Rubric A (journal validity) × Rubric B (evidence strength); dominant cell **no × high = 21/50**.
4. Open n=60 Audit E locator: [`AUDIT_E_CANONICAL_LOCATOR.md`](AUDIT_E_CANONICAL_LOCATOR.md) — JEE **11/60**, Decision Quality **37/60**, combined **26/60**, faithfulness **8/25/20/7**.
5. Skim four offline demos: [`DEMO_CASE_SELECTION.md`](DEMO_CASE_SELECTION.md).

Optional deep dive: [`EXAMINER_EVIDENCE_MAP.md`](EXAMINER_EVIDENCE_MAP.md) · [`DATA_LINEAGE.md`](DATA_LINEAGE.md) · [`REPRODUCTION_RUNBOOK.md`](REPRODUCTION_RUNBOOK.md).

## What this artefact is

A research prototype that:

1. **Generates candidate decision-journal entries** from public Inquiry hearing transcripts using an inquiry-mode LLM prompt (`gpt-4o-mini`, temperature 0, 7-sentence chunks / overlap 2).
2. **Checks mechanical source-quote traceability** against the processed chunk text.
3. **Freezes** candidates into a fixed reference dataset (`phase1-001` … `phase1-414`).
4. **Separates human validation** (journal membership, evidence strength, framework mapping, faithfulness) from automatic generation.

Candidate generation ≠ accepted government decisions. Human judgement remains authoritative for interpretation.

## Where the frozen 414-entry journal is

| Item | Path |
| --- | --- |
| Journal | `data/manifests/phase1_decision_journal.json` |
| SHA-256 | `814cc7c47a9f75bfc0a6c7b693feec7073e59131398d89fab7c9111fbb2e5e06` |
| Run registry | `configs/phase1_journal_runs.json` |

Do **not** regenerate the 414-entry journal to “verify” historical dissertation numbers.

## How to inspect n=50 and n=60

| Sample | Path | What to look for |
| --- | --- | --- |
| n=50 | `configs/evaluation/confidence_validation_sample.json` | `human_valid_decision`, `human_confidence` |
| n=50 κ | `configs/evaluation/confidence_comparison_results.json` | rule κ ≈ 0.48; LLM κ ≈ 0.39 vs Rubric B |
| n=60 aggregates | Audit E final pack (see locator) | JEE/DQ/faithfulness counts |
| n=60 record codes | `…/CONSISTENCY_CORRECTED_REFERENCE.csv` | human JEE/DQ fields (omit `reviewer_name` in public extracts) |

## Reproducibility classes (quick)

| Class | Meaning | Examples |
| --- | --- | --- |
| **1 Offline** | Deterministic on frozen inputs | Traceability checks; review flags; rule confidence; most hash/tests |
| **2 Public download** | Needs Inquiry site PDFs | Harvest/download → PDF → text |
| **3 OpenAI API** | Live model/embedding calls | Re-extraction; embedding regen; LLM confidence re-score |
| **4 Frozen LLM output** | Historical model results | Canonical journal; Phase 1 runs; structural/report pilots |
| **5 Human-adjudicated** | Author judgement | Excerpts; n=50; n=42; n=60 JEE/DQ/faithfulness |
| **6 Supporting** | Packaging / docs | This pack; Wave 2 DOCX/PDF submission files |

## Follow one item end-to-end

Example: `phase1-016` (Yes × High demo).

1. Journal row `id=phase1-016` → decision, quote, `traceability_ok`.
2. Source hearing date / slug from the same row; public PDF URL in `data/manifests/inquiry_module2_phase1.json`.
3. Human Rubric A/B in the n=50 sample for the same `journal_id`.
4. Dissertation claim locus in [`EXAMINER_EVIDENCE_MAP.md`](EXAMINER_EVIDENCE_MAP.md).

## Documents in this folder

| File | Role |
| --- | --- |
| `ARTEFACT_MANIFEST.csv` | Master inventory |
| `DATA_LINEAGE.md` | Source → findings chain |
| `REPRODUCTION_RUNBOOK.md` | Commands (offline / download / API) |
| `REPRODUCIBILITY_LIMITS.md` | Explicit non-claims |
| `EXAMINER_EVIDENCE_MAP.md` | Claim → evidence |
| `COMMAND_REFERENCE.md` | Compact CLI list |
| `DEMO_CASE_SELECTION.md` | Four validated offline demos |
| `AUDIT_E_CANONICAL_LOCATOR.md` | Single authoritative Audit E paths |
| `SECURITY_AND_PRIVACY_NOTE.md` | Secrets / redaction rules |
| `SHA256SUMS` | Hash lock for referenced artefacts |

Generated package mirror: `outputs/distinction_strategy/03_reproducibility_package/`.
