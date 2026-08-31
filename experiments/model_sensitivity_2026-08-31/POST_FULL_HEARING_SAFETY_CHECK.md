# Post-full-hearing safety check

**Date:** 2026-08-31  
**Experiment:** `model_sensitivity_2026-08-31` (full-hearing confirmation stage)

---

## New outputs (this stage only)

| File / directory | Status |
|------------------|--------|
| `14_FULL_HEARING_CONFIRMATION_PROTOCOL.md` | Created |
| `15_FULL_HEARING_RUN_RESULTS.csv` | Created (Terra valid; Sol status only) |
| `16_FULL_HEARING_ALIGNMENT.csv` | Created (Terra valid rows only) |
| `17_FULL_HEARING_CONFIRMATION_REPORT.md` | Created |
| `18_FINAL_MODEL_SENSITIVITY_INTEGRATION_RECOMMENDATION.md` | Created |
| `run_full_hearing_confirmation.py` | Created |
| `raw_responses_full_hearing/gpt-5.6-terra/full_hearing_confirmation.json` | Created — valid |
| `raw_responses_full_hearing/gpt-5.6-sol/full_hearing_confirmation_invalidated_run1.json` | Preserved — **INVALID** |
| `raw_responses_full_hearing/gpt-5.6-sol/full_hearing_confirmation_retry1_INCOMPLETE.json` | Created — **INCOMPLETE** |
| `logs/full_hearing_comparison.json` | Created (Terra-only) |

---

## Prior model-sensitivity outputs preserved

| File / directory | Status |
|------------------|--------|
| `00_PROTOCOL.md` | Unchanged |
| `02_RUN_RESULTS.csv` | Unchanged |
| `03_MODEL_SUMMARY.csv` | Unchanged |
| `04_RAW_OUTPUT_MANIFEST.csv` | Unchanged |
| `05_FINAL_MODEL_SENSITIVITY_REPORT.md` | Unchanged |
| `06_DISSERTATION_INTEGRATION_RECOMMENDATION.md` | Unchanged |
| `07_PROTOCOL_AMENDMENT_CURRENT_MODELS.md` | Unchanged |
| `09_EXTENDED_RUN_RESULTS.csv` | Unchanged |
| `10_EXTENDED_MODEL_SUMMARY.csv` | Unchanged |
| `11_EXTENDED_RAW_OUTPUT_MANIFEST.csv` | Unchanged |
| `12_EXTENDED_MODEL_SENSITIVITY_REPORT.md` | Unchanged |
| `13_EXTENDED_DISSERTATION_INTEGRATION_RECOMMENDATION.md` | Unchanged |
| `POST_EXPERIMENT_SAFETY_CHECK.md` | Unchanged |
| `POST_EXTENSION_SAFETY_CHECK.md` | Unchanged |
| `raw_responses/gpt-4o-mini/` | Unchanged |
| `raw_responses/gpt-4o/` | Unchanged |
| `raw_responses_extended/` | Unchanged |

---

## Frozen artefact verification

Hashes compared against `experiments/chunk_overlap_sensitivity_2026-08-30/BASELINE_SHA256_SNAPSHOT.txt`:

| Artefact | Status |
|----------|--------|
| `data/manifests/phase1_decision_journal.json` | PASS |
| `configs/annotations/manual_phase1.json` | PASS |
| `configs/evaluation/confidence_validation_sample.json` | PASS |
| `dissertation/Lawal_MSc_Dissertation_handbook_compliant.docx` | PASS |
| `src/decision_journal/extraction.py` | PASS |
| `configs/phase1_journal_runs.json` | PASS |
| `configs/annotations/excerpts/excerpt_001.json` | PASS |
| `configs/annotations/excerpts/excerpt_002.json` | PASS |
| `configs/annotations/excerpts/excerpt_003.json` | PASS |
| `configs/annotations/excerpts/excerpt_004.json` | PASS |
| `configs/annotations/excerpts/excerpt_005.json` | PASS |
| `configs/annotations/excerpts/excerpt_006.json` | PASS |

---

## Other safeguards

| Item | Status |
|------|--------|
| 414-entry dataset regenerated | **No** |
| Manual annotations altered | **No** |
| Dissertation DOCX/PDF edited | **No** |
| Chunk/overlap experiment outputs modified | **No** |
| n=50 / n=60 analyses altered | **No** |
| Legacy gpt-4o-mini / gpt-4o reruns | **No** |
| Invalid Sol run excluded from recovery CSV | **Yes** |
| Third Sol attempt | **No** |

---

**POST-FULL-HEARING SAFETY CHECK: PASS**
