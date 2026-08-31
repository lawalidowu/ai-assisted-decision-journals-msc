# Chunk/Overlap Sensitivity Analysis

## 1. Research question

How sensitive is decision extraction performance to sentence-window size and overlap, and was the configured 7-sentence / 2-sentence-overlap setting a reasonable choice within the bounded manually annotated material?

## 2. Frozen baseline

See `BASELINE_MANIFEST.md`. Git HEAD at experiment start: `a42d93555e8619b567daf833a30528e84013f1d3`. No frozen artefacts were modified.

## 3. Existing 7/2 configuration

Code-verified: `chunk_size=7`, `overlap=2`, `gpt-4o-mini`, temperature 0, inquiry-mode prompt. Original human triangulation on frozen full-transcript runs: 5/6 agreement-row recall.

## 4. Experimental protocol

Pre-registered in `00_PROTOCOL_PRE_REGISTERED.md` before comparative results were examined.

## 5. Evaluation material

Six excerpts (`excerpt_001`–`excerpt_006`), **6 manual decisions** total (1+2+0+0+0+3). Source spans preserved in excerpt JSON char offsets.

## 6. Configuration grid

12 configurations: window sizes {5,7,9,11} × overlaps {1,2,3}. All valid under existing chunker.

## 7. Matching/evaluation method

Deterministic overlap alignment reused from `scripts/keyword_baseline.py` plus `quote_found_in_text`. Primary recovery requires **both** mechanical quote match and automated semantic correspondence. See `GOLD_DECISION_ALIGNMENT.csv`.

## 8. Stage 1 results

| Rank | Config | Recovered | Recall | Candidates | Traceability | Unmatched | Dup removed |
|------|--------|-----------|--------|------------|--------------|-----------|-------------|
| 1 | w5_o3 | 4/6 | 66.7% | 9 | 77.8% | 2 | 0 |
| 2 | w5_o2 | 3/6 | 50.0% | 6 | 83.3% | 2 | 0 |
| 3 | w5_o1 | 3/6 | 50.0% | 4 | 75.0% | 1 | 0 |
| 4 | w7_o2 | 3/6 | 50.0% | 4 | 75.0% | 1 | 0 |
| 5 | w7_o3 | 3/6 | 50.0% | 4 | 75.0% | 1 | 0 |
| 6 | w9_o1 | 3/6 | 50.0% | 4 | 75.0% | 1 | 0 |
| 7 | w11_o1 | 3/6 | 50.0% | 4 | 75.0% | 1 | 0 |
| 8 | w11_o3 | 3/6 | 50.0% | 4 | 75.0% | 1 | 1 |
| 9 | w9_o2 | 2/6 | 33.3% | 2 | 50.0% | 0 | 0 |
| 10 | w11_o2 | 2/6 | 33.3% | 3 | 33.3% | 0 | 0 |
| 11 | w7_o1 | 1/6 | 16.7% | 2 | 100.0% | 1 | 0 |
| 12 | w9_o3 | 0/6 | 0.0% | 0 | 0.0% | 0 | 0 |

**Baseline 7/2 (w7_o2):** recovered 3/6 (50.0%), 4 candidates, traceability 75.0%.

## 9. Stability results

- **w5_o2**: recovery ['3', '3', '3']
- **w5_o3**: recovery ['4', '4', '4']
- **w7_o2**: recovery ['3', '3', '3']


## 10. Confirmatory results (if performed)

- w7_o2: recovered 2/6
- w5_o3: recovered 2/6
- w5_o2: recovered 1/6

## 11. Pareto analysis

## Pareto dominance pairs (A dominates B)

- `w5_o1` dominates `w11_o3`
- `w7_o2` dominates `w11_o3`
- `w7_o3` dominates `w11_o3`
- `w9_o1` dominates `w11_o3`
- `w9_o2` dominates `w9_o3`
- `w9_o2` dominates `w11_o2`
- `w11_o1` dominates `w11_o3`
- `w11_o2` dominates `w9_o3`

**Pareto-optimal configurations:** ['w11_o1', 'w5_o1', 'w5_o2', 'w5_o3', 'w7_o1', 'w7_o2', 'w7_o3', 'w9_o1', 'w9_o2']

7/2 is **Pareto-optimal** within the tested grid.

## 12. Interpretation of 7/2

Within this bounded six-decision evaluation set, configuration **w7_o2** recovered **3/6** manual decisions with **75.0%** traceability and **1** unmatched candidates.

Top-ranked configuration by pre-specified hierarchy: **w5_o3** (4/6 recovered).

## 13. Limitations

- Moving `gpt-4o-mini` alias (contemporary API, not historical snapshot).
- Six manual labels only; automated matching ≠ human triangulation.
- Excerpt-isolated Stage 1/2 vs full-hearing chunk context in Stage 3.
- Historical Phase 1 outputs and 414-record journal intentionally unchanged.

## 14. Exact defensible conclusion

This supplementary analysis empirically explored chunk/overlap sensitivity on frozen manual excerpts. Results inform whether 7/2 was **reasonable** within the tested grid, not whether it was uniquely optimal at corpus scale.

## 15. Recommended dissertation impact

See `DISSERTATION_INTEGRATION_RECOMMENDATION.md`.

---

7/2 VERDICT: ALTERNATIVE CONFIGURATION MODESTLY PREFERRED
