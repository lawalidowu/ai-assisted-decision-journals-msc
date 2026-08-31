# Final model-sensitivity integration recommendation

**Experiment:** `model_sensitivity_2026-08-31` (legacy panel + GPT-5.6 extension + limited full-hearing confirmation)  
**Date:** 2026-08-31  
**Advisory only.** No dissertation files were edited.

---

## Integration classification

### **USEFUL_AND_INTERPRETABLE** (excerpt-level model sensitivity)

### **PARTIALLY_COMPLETE** (full-hearing confirmation — Terra valid; Sol incomplete)

---

## 1. What valid full-hearing evidence exists?

Only **gpt-5.6-terra** produced a methodologically usable full-hearing confirmation:

| Evidence | Value |
|----------|-------|
| Model | gpt-5.6-terra |
| Scope | Three hearing days (2023-11-28, 2023-11-30, 2023-12-01); span-restricted evaluation |
| Recovery | **2/6** known manual decisions |
| Recovered IDs | `excerpt_001:m1`, `excerpt_002:m2` |
| API integrity | 487/487 calls succeeded; 0 parse failures |
| Traceability | 3/3 span-filtered candidates (100%) |

This is the **sole valid full-hearing datapoint** in the model-sensitivity experiment.

---

## 2. Was Sol full-hearing confirmation valid, invalid, or incomplete?

| Run | Status |
|-----|--------|
| Sol run 1 | **INVALID** — 365/487 API failures; preserved as invalidated raw output; excluded from recovery analysis |
| Sol retry | **INCOMPLETE** — terminated without complete output after extended runtime |
| Sol overall | **NOT INTERPRETABLE DUE TO EXECUTION FAILURE** |

Sol full-hearing extraction performance **remains unknown**. Do not infer extraction quality from invalidated or incomplete Sol outputs. Do not compare invalid Sol figures numerically with Terra.

---

## 3. Did Sol's excerpt-level 4/6 signal persist?

**Cannot be assessed.** No valid Sol full-hearing confirmation exists. The excerpt-level pattern (3/6 → 4/6 → 4/6) remains valid bounded-excerpt evidence only.

---

## 4. Did Terra remain comparable/stable?

| Scope | Terra recovery |
|-------|----------------|
| Bounded excerpt (3 reps) | 3/6, 3/6, 3/6 — stable |
| Full-hearing confirmation | **2/6** — lower than excerpt-level |

Terra remained **stable at excerpt level** and showed **lower bounded recovery at full-hearing scope** (3/6 → 2/6). This is interpretable evidence that extraction context affects bounded recovery for the same model and parameter profile.

---

## 5. Does Terra's 3/6 → 2/6 change strengthen the context-sensitivity conclusion?

**Yes — modestly.**

Combined with the chunk/overlap Stage 3 result (w7_o2 full-hearing: **2/6** with gpt-4o-mini), Terra's valid full-hearing confirmation supports that:

- bounded excerpt recovery can **decrease** when the same pipeline processes complete hearing-day inputs;
- this is a **context/scope sensitivity** finding, not evidence that any model is unsuitable in general;
- the fixed 414-entry Phase 1 corpus and historical human-triangulation result are unaffected.

The full-hearing check **does not weaken** the broader model-sensitivity experiment; it **narrows** what can be claimed about Terra-vs-Sol at full-hearing scope.

---

## 6. Does the broader five-model excerpt experiment remain suitable for dissertation integration?

**Yes — as optional, low-priority supplementary robustness evidence.**

Valid excerpt-level evidence across the completed panels:

| Panel | Models | Key finding |
|-------|--------|-------------|
| Legacy (temp=0) | gpt-4o-mini, gpt-4o | gpt-4o-mini stable 3/6; gpt-4o unstable 0–2/6 |
| Extended (reasoning=none) | gpt-5.6-terra, gpt-5.6-sol, gpt-5.6-luna | Terra stable 3/6; Sol up to 4/6 but unstable; Luna unstable 1–3/6 |

All excerpt runs completed without API failure. Together they support that **model choice affects bounded automated recovery** under fixed 7/2 extraction, without warranting corpus regeneration.

The incomplete Sol full-hearing stage does **not** invalidate the excerpt-level panel.

---

## 7. Is the evidence strong enough to justify dissertation integration?

| Component | Integration strength |
|-----------|---------------------|
| Excerpt-level model sensitivity (5 models) | **Moderate** — optional supporting paragraph |
| Full-hearing Terra confirmation | **Low–moderate** — one valid datapoint; supports context-sensitivity narrative already established by chunk/overlap Stage 3 |
| Full-hearing Terra vs Sol comparison | **None** — cannot integrate |

**Overall:** Excerpt-level integration remains defensible at low priority. Full-hearing integration should cite **Terra 2/6 only** as supplementary context-sensitivity evidence, not as a Terra-vs-Sol benchmark.

---

## 8. Minimum defensible dissertation wording

### Excerpt-level (optional, one sentence)

> A supplementary bounded model-sensitivity check on the same six-decision reference set found that automated recovery varied across tested models under fixed 7/2 extraction; gpt-5.6-terra recovered three of six decisions consistently across three repetitions, while gpt-5.6-sol reached four of six on two of three repetitions. These contemporary runs used `reasoning_effort='none'` with API-default temperature and do not replace the historical Phase 1 human-triangulation result.

### Full-hearing confirmation (optional, one sentence — use only if full-hearing scope is discussed)

> A limited full-hearing confirmation was completed for gpt-5.6-terra, which recovered two of six known decisions compared with three of six in each bounded-excerpt repetition. A corresponding gpt-5.6-sol confirmation could not be completed reliably because the initial run experienced extensive API failures and the retry did not complete successfully within the experiment time window. No interpretation of Sol full-hearing extraction performance is therefore made.

### Context-sensitivity bridge (optional, if linking to chunk/overlap Stage 3)

> This pattern is consistent with the chunk/overlap confirmatory full-hearing check, in which bounded recovery also fell when evaluation moved from annotated excerpts to complete hearing-day inputs under the same span-restricted matching rule.

### Do not write

- That Sol failed as an extraction model
- That Terra or Sol is best/superior/optimal
- That full-hearing Sol recovered 0/6 (invalid run excluded)
- Direct numerical comparison of invalid Sol outputs with Terra
- That model sensitivity replaces or contradicts the historical 5/6 human-triangulation result

---

## 9. Safeguards confirmed

- 414-entry dataset unchanged
- Manual annotations unchanged
- Dissertation untouched
- Chunk/overlap experiment outputs untouched
- Legacy model-sensitivity outputs (`02`–`06`, `raw_responses/`) untouched
- Extended GPT-5.6 excerpt outputs (`07`–`13`, `raw_responses_extended/`) untouched
- Invalid Sol run preserved and marked invalid
- Incomplete Sol retry status preserved

See `POST_FULL_HEARING_SAFETY_CHECK.md`.
