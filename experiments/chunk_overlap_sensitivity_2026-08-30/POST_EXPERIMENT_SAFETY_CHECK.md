# Post-experiment safety check

**Completed:** 2026-08-30

## Frozen artefact hash verification (before = after)

All SHA-256 values in `BASELINE_SHA256_SNAPSHOT.txt` verified unchanged after experiment completion.

```
ALL_UNCHANGED: True
```

Verified paths:

- `data/manifests/phase1_decision_journal.json` (414-record fixed reference dataset)
- `configs/annotations/manual_phase1.json`
- `configs/evaluation/confidence_validation_sample.json` (n=50 sample)
- `dissertation/Lawal_MSc_Dissertation_handbook_compliant.docx`
- `src/decision_journal/extraction.py`
- `configs/phase1_journal_runs.json`
- `configs/annotations/excerpts/excerpt_001.json` … `excerpt_006.json`

## Items explicitly not modified

| Artefact | Status |
|----------|--------|
| Original Phase 1 extraction run directories (`outputs/run_20260608_*` etc.) | Not written |
| 414-record journal | Unchanged |
| n=50 validation sample | Unchanged |
| n=60 post-60 audit outputs (`outputs/framework_mapping/run_*post60*`) | Not touched |
| Dissertation DOCX/PDF/chapters | Not edited |
| Production scripts (`scripts/run_extraction.py`, `extraction.py`) | Not edited |

## Experiment isolation

All new files confined to:

`experiments/chunk_overlap_sensitivity_2026-08-30/`

Including: protocol docs, `runs/`, CSV/MD results, `API_RUN_MANIFEST.csv`, wrapper scripts (`run_experiment.py`, `finalize_experiment.py`, `generate_reports.py`).

## Git working tree

Experiment added new untracked files under `experiments/` only. No staged changes to frozen dissertation artefacts.
