# Pre-registered protocol — chunk/overlap sensitivity analysis

**Registered:** 2026-08-30 (before any comparative API results were examined)  
**Experiment ID:** `chunk_overlap_sensitivity_2026-08-30`  
**Analyst:** supplementary bounded validation (author pipeline, contemporary API)

---

## 1. Research question

How sensitive is decision extraction performance to sentence-window size and overlap, and was the configured **7-sentence / 2-sentence-overlap** setting a reasonable choice within the bounded manually annotated material?

**Not** framed as proving 7/2 is optimal. 7/2 is the baseline configuration under test.

---

## 2. Frozen baseline

All dissertation artefacts listed in `BASELINE_MANIFEST.md` remain unchanged. Phase 1 used:

- `gpt-4o-mini` (moving alias)
- temperature `0`
- inquiry-mode prompt (`INQUIRY_PROMPT_TEMPLATE`)
- sentence-based overlapping windows
- existing deduplication and traceability pipeline

See `IMPLEMENTATION_RECONSTRUCTION.md` for code-verified parameters.

---

## 3. Evaluation data

**Only** the six existing manually annotated excerpts (`excerpt_001` … `excerpt_006`) and their frozen manual decisions in `configs/annotations/excerpts/*.json` (aggregated in `manual_phase1.json`).

- **6 manual decisions** total (not 6 excerpts with one decision each — distribution: 1+2+0+0+0+3).
- No new gold labels.
- No modification of manual decisions or comparison tags in frozen files.

Excerpt texts are processed as standalone inquiry-mode inputs (same normalization as full-transcript runs).

---

## 4. Configuration grid (fixed; 12 cells)

| Window size | Overlap values |
|-------------|----------------|
| 5 | 1, 2, 3 |
| 7 | 1, 2, 3 |
| 9 | 1, 2, 3 |
| 11 | 1, 2, 3 |

**Baseline cell:** 7 / 2.

**Invalidity rule:** A configuration is invalid if `overlap >= chunk_size` or `chunk_size - overlap < 1`. All 12 pre-specified pairs satisfy the chunker constraints.

**Fixed across all cells:** source text, preprocessing, sentence splitter, prompt, model string, temperature, schema, deduplication, traceability, post-processing.

**Independent variables:** (1) window size, (2) overlap only.

---

## 5. Primary metric

**Manual decision recovery**

- For each configuration, count manual decisions for which ≥1 extracted candidate **corresponds** to that manual decision (see §8).
- Report: count recovered / 6 and recall percentage.

---

## 6. Secondary metrics

1. **Mechanical traceability:** traceable candidates / all candidates; percentage.
2. **Candidate burden:** total candidates in six excerpts; per-excerpt mean; candidates per recovered manual decision.
3. **Unmatched candidate burden:** candidates with no aligned manual decision (same alignment rules).
4. **Duplicate burden:** pre-dedupe minus post-dedupe count; proportion of pre-dedupe items removed by `dedupe_decisions`.
5. **Extraction efficiency:** API calls, prompt/completion tokens, wall time, estimated USD cost (experiment runs only).

No post-hoc weighted quality score.

---

## 7. Matching / alignment method

Reuse deterministic overlap logic from `scripts/keyword_baseline.py` (min shared substring 25 characters, case-insensitive), extended to LLM candidate fields.

For each (configuration, excerpt, manual decision, candidate) pair:

**A. Mechanical quote recovery:** `overlaps(candidate.source_quote, manual.source_quote)` OR `quote_found_in_text` (alphanumeric fold from `extraction.py`).

**B. Semantic correspondence (automated, labeled):** `overlaps` between candidate `decision`/`evidence` and manual `decision`/`source_quote`.

**Primary recovery (manual decision matched):** requires **both** A and B for at least one candidate in that excerpt.

**Match basis labels:** `mechanical_and_semantic`, `mechanical_only`, `semantic_only`, `none`.

Output: auditable `GOLD_DECISION_ALIGNMENT.csv`.

---

## 8. Ranking rule (pre-specified hierarchy)

1. **First:** higher manual-decision recovery (count / 6).
2. **Second:** among ties, higher traceability percentage.
3. **Third:** among ties, lower unmatched candidate count.
4. **Fourth:** among ties, lower duplicate burden (count removed by dedupe).

**Pareto dominance:** A dominates B iff A is no worse on all four dimensions and strictly better on ≥1.

**7/2 interpretation classes (report only):**

- uniquely best under hierarchy
- tied / competitive
- Pareto-optimal but not hierarchy-best
- materially dominated
- clearly inferior

Avoid "optimal" unless narrowly justified.

---

## 9. Tie treatment

Exact ties on all four hierarchy metrics → configurations ranked equal; both/all retained for stability stage selection if among top performers.

---

## 10. Stage 1 — bounded configuration screen

Run all 12 configurations on six excerpt texts. Outputs:

- `01_STAGE1_CONFIGURATION_RESULTS.csv`
- `01_STAGE1_CONFIGURATION_RESULTS.md`
- `GOLD_DECISION_ALIGNMENT.csv` (all Stage 1 runs)

---

## 11. Stage 2 — stability check

After Stage 1:

- **Always retain** 7/2.
- Select **two strongest alternatives** by §8 hierarchy (automatic; not cherry-picked to favour 7/2).

Run **3 independent repetitions** (temperature 0) for:

- 7/2
- alternative 1
- alternative 2

Same six excerpts. Report variability in recovery, candidates, traceability, unmatched burden, duplicates.

Outputs: `02_STABILITY_RESULTS.csv`, `02_STABILITY_RESULTS.md`.

---

## 12. Stage 3 — limited confirmatory full-hearing check

**Pre-run cost gate:** estimate API calls/tokens for three hearing days:

- 2023-11-28
- 2023-11-30
- 2023-12-01

Configurations: **only** 7/2, alternative 1, alternative 2 (from Stage 2 selection).

**Proceed if** estimated cost is proportionate (documented in `STAGE3_COST_ESTIMATE.md`). If skipped, Stages 1–2 constitute the completed analysis.

If run: report corpus-level candidates, traceability, duplicates, burden, and recovery of the six manual decisions **within their annotated char spans** on full hearings.

Outputs: `03_CONFIRMATORY_RESULTS.csv`, `03_CONFIRMATORY_RESULTS.md` (if executed).

---

## 13. Interpretation rules

Honest reporting permitted:

- 7/2 best within bounded test
- 7/2 competitive / non-dominated
- alternative modestly preferred
- alternative clearly preferred

**Under any outcome:** do **not** regenerate the 414-record journal or replace original Phase 1 outputs.

---

## 14. Limitations (pre-declared)

- Six manual decisions across six excerpts — not corpus-representative.
- Contemporary `gpt-4o-mini` alias may differ from June 2025 weights.
- Excerpt-only Stage 1/2 differ from full-transcript chunk context at boundaries.
- Automated matching approximates human triangulation; human agreement was 5/6 on frozen 7/2 runs.
- Stage 3 span-restricted recovery may differ from excerpt-isolated Stage 1/2.

---

## 15. Protocol deviations

Recorded separately in `PROTOCOL_DEVIATIONS.md`.

---

## 16. Final deliverables

As specified in the parent experiment brief (`FINAL_CHUNK_SENSITIVITY_REPORT.md`, `DISSERTATION_INTEGRATION_RECOMMENDATION.md`, `API_RUN_MANIFEST.csv`, etc.).

---

*This document was written before examining Stage 1 comparative results.*
