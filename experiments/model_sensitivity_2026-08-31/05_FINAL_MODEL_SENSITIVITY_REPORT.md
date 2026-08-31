# Final model sensitivity report

**Experiment:** `model_sensitivity_2026-08-31`  
**Completed:** 2026-08-31  
**Protocol:** `00_PROTOCOL.md` (pre-registered before results examined)

---

## 1. Research question

Under otherwise identical extraction conditions (7/2 window, inquiry-mode prompt, temperature 0), is recovery of the existing six manually annotated decisions sensitive to the LLM used?

**Answer:** **Yes.** Recovery differed between models and was stable for `gpt-4o-mini` but unstable across repetitions for `gpt-4o` on this six-decision reference set.

---

## 2. Models used

| Role | Requested identifier | Returned snapshot (API) |
|------|---------------------|-------------------------|
| Baseline | `gpt-4o-mini` | `gpt-4o-mini-2024-07-18` |
| Comparison | `gpt-4o` | `gpt-4o-2024-08-06` |

Both invoked via existing OpenAI API credentials. No parameter substitutions required (`temperature=0` accepted by both).

---

## 3. Fixed configuration

- Window: 7 sentences; overlap: 2  
- Inquiry-mode prompt; temperature 0  
- Same preprocessing, schema, traceability, deduplication, and matching as chunk/overlap sensitivity experiment  

---

## 4. Runs completed

| Model | Repetitions completed | Recovery (rep 1 / 2 / 3) |
|-------|----------------------|--------------------------|
| gpt-4o-mini | 3/3 | 3/6 · 3/6 · 3/6 |
| gpt-4o | 3/3 | 0/6 · 1/6 · 2/6 |

All six model×repetition runs completed. No API runtime failures. No parse/schema failures.

---

## 5. Key numerical results

### Per run (`02_RUN_RESULTS.csv`)

| Model | Rep | Recovered | Candidates | Traceability | Unmatched |
|-------|-----|-----------|------------|--------------|-----------|
| gpt-4o-mini | 1 | 3/6 (50.0%) | 5 | 60.0% | 1 |
| gpt-4o-mini | 2 | 3/6 (50.0%) | 4 | 75.0% | 1 |
| gpt-4o-mini | 3 | 3/6 (50.0%) | 4 | 75.0% | 1 |
| gpt-4o | 1 | 0/6 (0.0%) | 0 | — | 0 |
| gpt-4o | 2 | 1/6 (16.7%) | 1 | 0.0% | 0 |
| gpt-4o | 3 | 2/6 (33.3%) | 2 | 50.0% | 0 |

### Per-model summary (`03_MODEL_SUMMARY.csv`)

| Model | Recovery range | Mean (descriptive) | Identical across 3 reps? |
|-------|----------------|--------------------|-------------------------|
| gpt-4o-mini | 3–3 | 3.0/6 | **Yes** |
| gpt-4o | 0–2 | 1.0/6 | **No** |

---

## 6. Interpretation (bounded)

- Recovery **is sensitive** to model choice on this six-decision excerpt set under fixed 7/2 configuration.
- **`gpt-4o-mini`** recovered **3/6** consistently across all three repetitions — aligning with the contemporary 7/2 rerun in the chunk/overlap sensitivity experiment (also 3/6 under automated matching).
- **`gpt-4o`** showed **lower and unstable** recovery (0, 1, then 2 across repetitions), with rep 1 producing zero candidates from excerpt processing (many chunk calls returned empty JSON arrays `[]`).
- These figures **do not** replace the historical Phase 1 human-triangulation result of **5/6** on frozen full-transcript outputs.
- No claim that either model is optimal, superior, or should replace the frozen 414-entry dataset.

---

## 7. Comparability caveats

| Caveat | Detail |
|--------|--------|
| Small reference set | Six manual decisions only |
| Automated matching | Differs from original human triangulation |
| Moving model aliases | Contemporary API snapshots; not June 2025 historical state |
| Same provider | Both OpenAI; not a cross-provider comparison |
| gpt-4o instability | Repetition variance (0→1→2) limits single-run conclusions for that model |
| Empty outputs | gpt-4o rep 1 returned `[]` on multiple chunks without parse errors |

---

## 8. Safeguards confirmed

- 414-entry dataset **unchanged**
- Manual annotations **unchanged**
- Chunk/overlap experiment outputs **unchanged**
- Dissertation files **not edited**
- Frozen artefact SHA-256 hashes **verified PASS** (see `POST_EXPERIMENT_SAFETY_CHECK.md`)

---

## 9. Files produced

- `00_PROTOCOL.md`
- `01_MODEL_AVAILABILITY_ASSESSMENT.md`
- `02_RUN_RESULTS.csv`
- `03_MODEL_SUMMARY.csv`
- `04_RAW_OUTPUT_MANIFEST.csv`
- `GOLD_DECISION_ALIGNMENT.csv`
- `raw_responses/{model}/rep{n}/excerpt_*.json`
- `logs/run_log.json`
- `05_FINAL_MODEL_SENSITIVITY_REPORT.md` (this file)
- `06_DISSERTATION_INTEGRATION_RECOMMENDATION.md`
