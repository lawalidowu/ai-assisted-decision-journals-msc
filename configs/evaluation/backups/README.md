# Evaluation artefact backups

**Created:** Jun 2026 — before any provisional AI ratings.

These copies are **read-only references**. Do not edit them in place.

| File | What it preserves |
|------|-------------------|
| `confidence_validation_sample_pristine.json` | n=50 validation sample with **no** human/AI ratings (`human_*` all null) |
| `phase1_decision_journal_v1.1_flagged.json` | Canonical 414 entries **with** Phase 2a review flags |
| `manual_phase1_pristine.json` | Phase 1 triangulation workbook (6 excerpts) |

## Restore if needed

**Reset validation sample to pristine (no ratings):**

```powershell
Copy-Item configs/evaluation/backups/confidence_validation_sample_pristine.json `
  configs/evaluation/confidence_validation_sample.json -Force
```

**Reset journal to flagged canonical state** (only if journal was corrupted):

```powershell
Copy-Item configs/evaluation/backups/phase1_decision_journal_v1.1_flagged.json `
  data/manifests/phase1_decision_journal.json -Force
```

## Provisional vs pristine

| Path | Purpose |
|------|---------|
| `configs/evaluation/confidence_validation_sample.json` | **Pristine** — for your real human `--checklist` rating |
| `configs/evaluation/confidence_validation_sample_provisional.json` | **Dev only** — AI provisional ratings for pipeline testing |

**Thesis rule:** cite human validation only from ratings you apply yourself to the **pristine** manifest.

## Git

This repo had no git history at backup time. Consider `git init` and committing after major milestones.
