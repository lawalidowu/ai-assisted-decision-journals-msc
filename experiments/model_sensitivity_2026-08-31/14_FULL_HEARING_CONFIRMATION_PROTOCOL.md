# Full-hearing confirmation protocol — GPT-5.6 Terra vs Sol

**Registered:** 2026-08-31 (before confirmation results examined)  
**Experiment:** `model_sensitivity_2026-08-31`  
**Stage:** Limited full-hearing confirmation

---

## 1. Purpose

Excerpt-level GPT-5.6 panel showed:

| Model | Rep 1 | Rep 2 | Rep 3 |
|-------|-------|-------|-------|
| gpt-5.6-terra | 3/6 | 3/6 | 3/6 |
| gpt-5.6-sol | 3/6 | 4/6 | 4/6 |

This stage asks: **Does the excerpt-level difference between Terra (stable 3/6) and Sol (higher but less stable, up to 4/6) persist when processing the corresponding complete hearing-day inputs?**

This is confirmation only — not a model benchmark, not a stability experiment, and not a corpus-wide evaluation.

---

## 2. Models

| Model | Runs |
|-------|------|
| gpt-5.6-terra | 1 full-hearing confirmation |
| gpt-5.6-sol | 1 full-hearing confirmation |

**Not run:** gpt-5.6-luna, gpt-4o-mini, gpt-4o (legacy and Luna panels preserved).

---

## 3. Hearing inputs

Three full hearing-day transcripts associated with annotated excerpts:

| Date | Source file |
|------|-------------|
| 2023-11-28 | `data/processed/inquiry/document/transcript-of-module-2-public-hearing-on-28-november-2023.txt` |
| 2023-11-30 | `data/processed/inquiry/document/transcript-of-module-2-public-hearing-on-30-november-2023.txt` |
| 2023-12-01 | `data/processed/inquiry/document/transcript-of-module-2-public-hearing-on-01-december-2023.txt` |

---

## 4. Evaluation scope

- **Six frozen manual decisions** across six excerpt JSON files
- Recovery assessed only for candidates whose `source_quote` falls within the existing annotated char spans
- **No** new full-hearing annotations
- **No** treatment of unannotated hearing content as false positives

---

## 5. Fixed configuration (matches GPT-5.6 excerpt panel)

| Parameter | Value |
|-----------|-------|
| Window | 7 sentences |
| Overlap | 2 |
| Prompt | `INQUIRY_PROMPT_TEMPLATE` |
| Preprocessing / schema / traceability / deduplication | Unchanged |
| Matching | Deterministic automated (chunk/overlap experiment logic) |
| Endpoint | `chat.completions` |
| `reasoning_effort` | `'none'` |
| Temperature | Omitted (API default) |

---

## 6. Run plan

- **One confirmation run per model** (no triple repetition unless API failure invalidates a run)
- Raw outputs preserved under `raw_responses_full_hearing/{model}/`

---

## 7. Metrics

Per model:

- Known manual decisions recovered / 6
- Recovery by manual decision ID (excerpt_id + manual_id)
- Candidate count across three hearings (span-filtered)
- Traceability count/rate
- Parse/schema and API failures
- Token usage, wall-clock time, returned model identifier

Cross-model:

- Recovered by both Terra and Sol
- Recovered only by Terra
- Recovered only by Sol
- Recovered by neither

---

## 8. Interpretation rules

- Do not call either model best/superior/optimal
- Do not equate with historical Phase 1 **5/6** human triangulation
- Do not claim unannotated candidates are false positives
- No inferential significance testing

Valid question: Does excerpt-level Terra/Sol difference persist under full-hearing confirmation with the same GPT-5.6 parameter profile?

---

*Protocol written before examining confirmation run results.*
