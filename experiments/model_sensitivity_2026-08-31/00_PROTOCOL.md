# Model sensitivity experiment — protocol

**Registered:** 2026-08-31 (before any comparative results were examined)  
**Experiment ID:** `model_sensitivity_2026-08-31`  
**Methodological reference:** `experiments/chunk_overlap_sensitivity_2026-08-30/`

---

## 1. Research question

Under otherwise identical extraction conditions, is recovery of the existing six manually annotated decisions sensitive to the LLM used?

This is a **supplementary robustness check only**. It is **not** model benchmarking, model superiority testing, or selection of a universally best model.

---

## 2. Baseline model

| Role | API identifier | Notes |
|------|----------------|-------|
| **Baseline** | `gpt-4o-mini` | Same alias used for frozen Phase 1 production extraction |

Hosted OpenAI aliases may resolve to dated snapshots at call time (e.g. `gpt-4o-mini-2024-07-18`). The protocol records the **requested** identifier and the **returned** model field from each API response.

---

## 3. Comparison model

| Role | API identifier | Rationale for selection |
|------|----------------|----------------------|
| **Comparison** | `gpt-4o` | Only materially different chat model already allowlisted in repository config (`configs/language_edit.json`) and callable programmatically via existing `OPENAI_API_KEY` without new provider infrastructure |

**Not selected:** Anthropic, Azure OpenAI, Ollama, or other providers — none are wired in project code. A second OpenAI chat model provides a bounded same-API comparison of model choice while changing provider architecture is out of scope for this MSc supplementary check.

**Availability verification:** See `01_MODEL_AVAILABILITY_ASSESSMENT.md`. Minimal pre-run API probe confirmed both models accept `temperature=0` and return structured JSON-capable responses.

---

## 4. Fixed extraction configuration

Held constant across both models:

| Parameter | Value |
|-----------|-------|
| Window size | 7 sentences |
| Overlap | 2 sentences |
| Prompt | `INQUIRY_PROMPT_TEMPLATE` (inquiry-mode) |
| Temperature | 0 |
| Preprocessing | `clean_inquiry_text` |
| Chunking | `chunk_text_by_sentences` |
| Schema | Four-field decision object + traceability |
| Traceability | `validate_traceability` / `quote_found_in_text` |
| Deduplication | `dedupe_decisions` |
| Matching | Same deterministic logic as chunk/overlap experiment (`assess_pair`: mechanical quote + semantic overlap) |

**Independent variable:** model string passed to `client.chat.completions.create(model=...)`.

---

## 5. Reference set

Reuse **exactly**:

- Six existing manually annotated excerpts: `configs/annotations/excerpts/excerpt_001.json` … `excerpt_006.json`
- **Six manual decisions** total (frozen labels; distribution 1+2+0+0+0+3)
- **No** new gold labels; **no** alteration or reinterpretation of manual decisions

---

## 6. Metrics (per model × repetition)

Primary:

- Manual decisions recovered / 6
- Recall (%)

Supporting:

- Total candidates (post-dedupe)
- Mechanically traceable candidates and traceability rate
- Unmatched candidates
- Duplicates removed (pre-dedupe minus post-dedupe)
- Parse/schema failures (chunk calls returning invalid JSON or non-array)
- API/runtime failures (exceptions or empty failures)

Per-model descriptive summaries (no inferential tests):

- Recovery range across three repetitions
- Mean recovery (descriptive only)
- Whether recovery was identical across all three repetitions

---

## 7. Repetition plan

- **3 independent repetitions** per model
- **6 excerpts** processed per repetition under fixed 7/2 configuration
- Outputs **not reused** between repetitions
- Every raw model response preserved under `raw_responses/`

Run order: baseline (`gpt-4o-mini`) repetitions 1–3, then comparison (`gpt-4o`) repetitions 1–3.

---

## 8. Decision rules

| Rule | Application |
|------|-------------|
| Small-n caution | Six-decision set is extremely small; no “better/best/superior/optimal” language |
| No corpus generalisation | Results bounded to six excerpts only |
| No provider superiority | Same OpenAI API; comparison is model alias only |
| Historical 5/6 safeguard | Original Phase 1 human-triangulation 5/6 is **not** replaced or equated with these automated-matching figures |
| Frozen dataset | 414-entry journal unchanged |
| Parameter parity | If either model rejects temperature 0 or structured behaviour, record incompatibility and classify comparability accordingly |

---

## 9. Limitations (pre-declared)

- Six manual decisions — not corpus-representative
- Automated matching ≠ original human triangulation procedure
- Contemporary hosted model aliases may differ from June 2025 Phase 1 API state
- Same-provider comparison limits claims about provider-level differences
- Descriptive repetition stability only; no significance testing on n = 6

---

## 10. Deliverables

- `01_MODEL_AVAILABILITY_ASSESSMENT.md`
- `02_RUN_RESULTS.csv`
- `03_MODEL_SUMMARY.csv`
- `04_RAW_OUTPUT_MANIFEST.csv`
- `05_FINAL_MODEL_SENSITIVITY_REPORT.md`
- `06_DISSERTATION_INTEGRATION_RECOMMENDATION.md`
- Raw responses in `raw_responses/`

---

*This protocol was written before examining comparative run results.*
