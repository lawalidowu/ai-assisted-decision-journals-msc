# Phase 1 `--inquiry` extraction summary (all 8 transcripts)

**Model:** gpt-4o-mini · **Mode:** `--inquiry` · **Chunk:** 7 sentences, overlap 2

## Corpus totals

| Metric | Value |
|--------|-------|
| Transcripts | 8 |
| Total decisions extracted | 414 |
| Traceability pass | 351/414 (84.8%) |
| Traceability fail | 63 |

**Canonical journal:** `data/manifests/phase1_decision_journal.json` — merged from the 8 runs below via `python scripts/build_phase1_journal.py` (IDs `phase1-001` … `phase1-414`).

## Per-transcript

| Hearing date | Run folder | Chunks | Decisions | Traceability pass | Pass rate |
|--------------|------------|--------|-----------|-------------------|-----------|
| 28 Nov 2023 | `run_20260608_005512_module2_2023-11-28` | 212 | 32 | 29/32 | 91% |
| 30 Nov 2023 | `run_20260609_014425_module2_2023-11-30` | 181 | 50 | 43/50 | 86% |
| 01 Dec 2023 | `run_20260609_014914_module2_2023-12-01` | 94 | 32 | 28/32 | 88% |
| 07 Dec 2023 | `run_20260609_070847_module2_2023-12-07` | 144 | 36 | 32/36 | 89% |
| 11 Dec 2023 | `run_20260609_071309_module2_2023-12-11` | 185 | 56 | 45/56 | 80% |
| 13 Dec 2023 | `run_20260609_071809_module2_2023-12-13` | 168 | 106 | 93/106 | 88% |
| 14 Dec 2023 | `run_20260609_072425_module2_2023-12-14` | 78 | 57 | 46/57 | 81% |
| 23 May 2024 | `run_20260609_072813_module2_2024-05-23` | 168 | 45 | 35/45 | 78% |

## Notes for evaluation write-up

- **Broader LLM run complete:** all Phase 1 Module 2 transcripts processed with inquiry-mode prompt.
- **Traceability:** ~85% of items have verbatim quotes locatable in source text; failures mainly `source_quote_not_found_in_text` (PDF extraction artefacts) and occasional `bad_source_location`.
- **Manual verification:** 6 excerpts on 3 transcripts (28 Nov, 30 Nov, 01 Dec) — see `docs/TRIANGULATION_SUMMARY.md`. Remaining 5 runs are available for post-hoc spot-checks, not full manual annotation.
- **13 Dec outlier:** highest decision count (106) — likely witness-heavy day with many recalled agreements; worth spot-checking for false positives.

*Generated 2026-05-22 after completing runs on 07, 11, 13, 14 Dec and 23 May.*
