# Full-hearing confirmation report — GPT-5.6 panel

**Experiment:** `model_sensitivity_2026-08-31`  
**Stage:** Limited full-hearing confirmation  
**Date finalised:** 2026-08-31

---

## 1. Purpose

This stage tested whether the excerpt-level difference between **gpt-5.6-terra** (stable 3/6 across three repetitions) and **gpt-5.6-sol** (3/6, 4/6, 4/6) persists when processing the three corresponding complete hearing-day inputs under the same GPT-5.6 parameter profile.

Evaluation remained restricted to the six frozen manual decisions within existing annotated char spans only.

---

## 2. Run status summary

| Model | Run status | Known decisions recovered / 6 | Methodologically usable? |
|-------|------------|--------------------------------|--------------------------|
| gpt-5.6-terra | **VALID — complete** | **2/6** | Yes |
| gpt-5.6-sol | **INCOMPLETE — execution failure** | *Not reported* | No |

A limited full-hearing confirmation was completed for **gpt-5.6-terra**, which recovered **2/6** known decisions compared with **3/6** in each bounded-excerpt repetition. A corresponding **gpt-5.6-sol** confirmation could not be completed reliably because the initial run experienced extensive API failures and the retry did not complete successfully within the experiment time window. **No interpretation of Sol full-hearing extraction performance is therefore made.**

---

## 3. Valid evidence — gpt-5.6-terra

### Configuration (matches GPT-5.6 excerpt panel)

| Parameter | Value |
|-----------|-------|
| Window / overlap | 7 / 2 |
| Prompt | inquiry-mode |
| Endpoint | `chat.completions` |
| `reasoning_effort` | `'none'` |
| Temperature | omitted (API default) |
| Matching | deterministic automated |

### Hearing inputs

| Date | Transcript slug | API calls (successful) | Pre-span candidates | Span-filtered candidates |
|------|-----------------|------------------------|----------------------|--------------------------|
| 2023-11-28 | `transcript-of-module-2-public-hearing-on-28-november-2023` | 212 | 7 | 2 (excerpt_001) |
| 2023-11-30 | `transcript-of-module-2-public-hearing-on-30-november-2023` | 181 | 15 | 1 (excerpt_002) |
| 2023-12-01 | `transcript-of-module-2-public-hearing-on-01-december-2023` | 94 | 13 | 0 (excerpt_006) |

### Recovery metrics

| Metric | Value |
|--------|-------|
| Known manual decisions recovered | **2 / 6** (33.3%) |
| Span-filtered candidates (total) | 3 |
| Traceable candidates | 3 (100.0%) |
| Parse/schema failures | 0 |
| API/runtime failures | 0 |
| Total tokens | 834,334 |
| Wall-clock time | 421.5 s (~7.0 min) |
| Returned model identifier | `gpt-5.6-terra` |

### Recovery by manual decision ID

| Excerpt | Manual ID | Recovered | Span candidates |
|---------|-----------|-----------|-----------------|
| excerpt_001 | m1 | **Yes** | 2 |
| excerpt_002 | m1 | No | 1 |
| excerpt_002 | m2 | **Yes** | 1 |
| excerpt_006 | m1 | No | 0 |
| excerpt_006 | m2 | No | 0 |
| excerpt_006 | m3 | No | 0 |

**Recovered:** `excerpt_001:m1`, `excerpt_002:m2`  
**Not recovered:** `excerpt_002:m1`, `excerpt_006:m1`, `excerpt_006:m2`, `excerpt_006:m3`

Raw output: `raw_responses_full_hearing/gpt-5.6-terra/full_hearing_confirmation.json`

---

## 4. Sol execution record (not interpretable as recovery evidence)

### Run 1 — invalidated

| Metric | Value |
|--------|-------|
| Status | **INVALID — extensive API failure** |
| API calls attempted | 487 |
| Successful API calls | 122 |
| API/runtime failures | **365** (75.0%) |
| Span-filtered candidates | 0 |
| Reported recovery | *Excluded from analysis* |

Raw output (preserved, clearly marked invalid):  
`raw_responses_full_hearing/gpt-5.6-sol/full_hearing_confirmation_invalidated_run1.json`

The 365/487 failure rate makes this run methodologically unusable. **It is not included as a recovery datapoint.**

### Run 2 — retry terminated incomplete

| Metric | Value |
|--------|-------|
| Status | **INCOMPLETE — terminated after time window** |
| Retry started | 2026-08-31T07:39:33Z |
| Retry terminated | ~50 min runtime, no complete output |
| Recovery metrics | *None produced* |

Partial status preserved:  
`raw_responses_full_hearing/gpt-5.6-sol/full_hearing_confirmation_retry1_INCOMPLETE.json`

No third Sol attempt was made.

**Cross-model Terra vs Sol comparison is not permitted** because Sol produced no valid full-hearing confirmation result.

---

## 5. Context: excerpt-level vs full-hearing (Terra only)

| Scope | gpt-5.6-terra recovery |
|-------|------------------------|
| Bounded excerpt (rep 1–3) | 3/6, 3/6, 3/6 |
| Full-hearing confirmation | **2/6** |

Terra bounded excerpts recovered three of six known decisions consistently; the valid full-hearing confirmation recovered two of six. This suggests recovery can change when moving from bounded excerpts to full-hearing context.

This pattern is **consistent with the earlier chunk/overlap full-hearing sensitivity result** (Stage 3, w7_o2: **2/6** within annotated spans using gpt-4o-mini).

---

## 6. Cross-model excerpt context (for reference only — not full-hearing)

Excerpt-level GPT-5.6 panel (valid, completed earlier):

| Model | Rep 1 | Rep 2 | Rep 3 |
|-------|-------|-------|-------|
| gpt-5.6-terra | 3/6 | 3/6 | 3/6 |
| gpt-5.6-sol | 3/6 | 4/6 | 4/6 |

The original research question — whether excerpt-level Terra/Sol difference persists in full-hearing confirmation — **cannot be answered** because Sol full-hearing confirmation was not completed. Sol full-hearing performance **remains unknown**.

---

## 7. Interpretation safeguards

- No model is described as best, superior, or optimal.
- Historical Phase 1 human-triangulation **5/6** is not used as a comparator here.
- Unannotated full-hearing candidates are not treated as false positives.
- No inferential significance testing was applied.
- Sol is **not** described as having failed as an extraction model; the Sol full-hearing stage failed at **execution**, not at interpretable bounded recovery measurement.

---

## 8. Classification

| Component | Classification |
|-----------|----------------|
| Terra full-hearing confirmation | **VALID — interpretable** |
| Sol full-hearing confirmation | **INCOMPLETE / NOT INTERPRETABLE DUE TO EXECUTION FAILURE** |
| Overall full-hearing stage | **PARTIALLY COMPLETE** — Terra evidence only |

---

## 9. Output files

| File | Description |
|------|-------------|
| `14_FULL_HEARING_CONFIRMATION_PROTOCOL.md` | Pre-registered protocol |
| `15_FULL_HEARING_RUN_RESULTS.csv` | Run-level metrics (Terra valid; Sol status only) |
| `16_FULL_HEARING_ALIGNMENT.csv` | Per-decision Terra alignment |
| `raw_responses_full_hearing/` | Raw Terra output; invalid/incomplete Sol records |
| `logs/full_hearing_comparison.json` | Terra-only cross-decision summary |
