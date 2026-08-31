# Extended model sensitivity report — current-generation OpenAI models

**Experiment:** `model_sensitivity_2026-08-31` (extension)  
**Completed:** 2026-08-31  
**Amendment:** `07_PROTOCOL_AMENDMENT_CURRENT_MODELS.md`

---

## 1. Models probed and qualified

| Model | Probed | Qualified for extended panel | Strict temp=0 parity |
|-------|--------|------------------------------|----------------------|
| gpt-5.6-terra | Yes | **Yes** | No |
| gpt-5.6-sol | Yes | **Yes** | No |
| gpt-5.6-luna | Yes | **Yes** (optional; included) | No |
| gpt-4o-mini | Legacy complete | Not rerun | Yes (original panel) |
| gpt-4o | Legacy complete | Not rerun | Yes (original panel) |

---

## 2. API / parameter settings (extended panel)

| Setting | Legacy panel (preserved) | Extended GPT-5.6 panel |
|---------|--------------------------|-------------------------|
| Endpoint | `chat.completions` | `chat.completions` |
| Temperature | **0** | **Omitted** (API default only; temp=0 rejected) |
| Reasoning | n/a | **`reasoning_effort='none'`** (explicit every call) |
| Prompt | `INQUIRY_PROMPT_TEMPLATE` | Same |
| Window / overlap | 7 / 2 | Same |
| Matching | Deterministic automated | Same |

**Reasoning tokens observed:** 0 across all extended runs (with explicit `reasoning_effort='none'`).

---

## 3. Legacy results preserved (unchanged)

| Model | Rep 1 | Rep 2 | Rep 3 | Stable? |
|-------|-------|-------|-------|---------|
| gpt-4o-mini | 3/6 | 3/6 | 3/6 | Yes |
| gpt-4o | 0/6 | 1/6 | 2/6 | No |

Source: `02_RUN_RESULTS.csv`, `03_MODEL_SUMMARY.csv`, `raw_responses/` — verified unmodified.

---

## 4. Extended GPT-5.6 results (new)

### Per repetition (`09_EXTENDED_RUN_RESULTS.csv`)

| Model | Rep | Recovered | Candidates | Traceability | Unmatched |
|-------|-----|-----------|------------|--------------|-----------|
| gpt-5.6-terra | 1 | 3/6 (50.0%) | 6 | 66.7% | 1 |
| gpt-5.6-terra | 2 | 3/6 (50.0%) | 6 | 66.7% | 1 |
| gpt-5.6-terra | 3 | 3/6 (50.0%) | 6 | 66.7% | 1 |
| gpt-5.6-sol | 1 | 3/6 (50.0%) | 7 | 71.4% | 2 |
| gpt-5.6-sol | 2 | **4/6 (66.7%)** | 7 | 85.7% | 1 |
| gpt-5.6-sol | 3 | **4/6 (66.7%)** | 7 | 85.7% | 1 |
| gpt-5.6-luna | 1 | 1/6 (16.7%) | 3 | 100.0% | 2 |
| gpt-5.6-luna | 2 | 2/6 (33.3%) | 3 | 100.0% | 1 |
| gpt-5.6-luna | 3 | 3/6 (50.0%) | 4 | 75.0% | 1 |

### Per-model summary (`10_EXTENDED_MODEL_SUMMARY.csv`)

| Model | Range | Mean (descriptive) | Stable? | Total tokens (3 reps) |
|-------|-------|--------------------|---------|------------------------|
| gpt-5.6-terra | 3–3 | 3.0/6 | **Yes** | 25,969 |
| gpt-5.6-sol | 3–4 | 3.67/6 | **No** | 26,458 |
| gpt-5.6-luna | 1–3 | 2.0/6 | **No** | 25,086 |

All 9 runs completed. Zero API failures. Zero parse/schema failures.

---

## 5. Cross-panel descriptive comparison (caveated)

Under **different temperature settings**, excerpt-level automated recovery patterns were:

| Model | Panel | Stable recovery | Notable pattern |
|-------|-------|-----------------|-----------------|
| gpt-4o-mini | Legacy (temp=0) | 3/6 | Production baseline reference |
| gpt-4o | Legacy (temp=0) | 0→1→2/6 | Lower, unstable |
| gpt-5.6-terra | Extended | 3/6 | Matches mini contemporary rerun |
| gpt-5.6-sol | Extended | 3→4→4/6 | Highest bounded recovery observed (4/6) |
| gpt-5.6-luna | Extended | 1→2→3/6 | Lower, unstable |

**Appropriate bounded conclusions:**

- Recovery **varied across tested models** on this six-decision reference set.
- **gpt-5.6-terra** was stable at 3/6 under extended settings, aligning with the contemporary `gpt-4o-mini` rerun.
- **gpt-5.6-sol** showed **higher but less stable** recovery (up to 4/6) under extended settings.
- **gpt-5.6-luna** was **less stable and generally lower** than terra/sol on this set.
- Model choice is an **empirical design parameter** requiring validation; these runs do **not** reproduce historical Phase 1 model state.

**Do not claim:** best/superior/optimal model; corpus-wide superiority; equivalence with historical **5/6** human triangulation.

---

## 6. Full-hearing confirmation gate

### Assessment

| Criterion | Met? |
|-----------|------|
| Materially different excerpt-level pattern for ≥1 current model | **Yes** — gpt-5.6-sol reached 4/6 on reps 2–3 |
| Chunk/overlap Stage 3 machinery reusable | **Yes** — `chunk_overlap_sensitivity_2026-08-30/run_experiment.py` Stage 3 |
| Same six manual decisions / annotated spans | **Yes** |
| Without methodological redesign | **Partial** — full-hearing would need GPT-5.6 parameter profile (reasoning_effort=none, no temp=0) documented separately from legacy Stage 3 |

### Recommendation

**Optional limited full-hearing confirmation is recommended for `gpt-5.6-sol` only**, not automatically executed.

**Proposed plan (if pursued later):**

1. Rerun Stage 3 from chunk/overlap experiment on hearing days 2023-11-28, 2023-11-30, 2023-12-01.
2. Models: **gpt-5.6-sol** only (materially different excerpt signal); optionally **gpt-5.6-terra** as stable reference.
3. Fixed 7/2; `reasoning_effort='none'`; temperature omitted.
4. Report span-restricted recovery of six known manual decisions only.
5. Store under new extension subdirectory; do not alter existing Stage 3 CSVs.

**Not recommended for:** gpt-5.6-luna (unstable excerpt pattern); legacy gpt-4o (already unstable at excerpt level).

---

## 7. Safeguards

- Legacy `02_*`–`06_*` outputs and `raw_responses/` **unchanged**
- Frozen artefact hashes **PASS** (`POST_EXTENSION_SAFETY_CHECK.md`)
- 414-entry dataset **unchanged**
- Dissertation **not edited**

---

## 8. Files added

- `07_PROTOCOL_AMENDMENT_CURRENT_MODELS.md`
- `08_CURRENT_MODEL_AVAILABILITY_PARITY.md`
- `09_EXTENDED_RUN_RESULTS.csv`
- `10_EXTENDED_MODEL_SUMMARY.csv`
- `11_EXTENDED_RAW_OUTPUT_MANIFEST.csv`
- `raw_responses_extended/{model}/rep{n}/excerpt_*.json` (54 files)
- `logs/extended_run_log.json`
- `run_extension.py`
- `12_EXTENDED_MODEL_SENSITIVITY_REPORT.md` (this file)
- `13_EXTENDED_DISSERTATION_INTEGRATION_RECOMMENDATION.md`
