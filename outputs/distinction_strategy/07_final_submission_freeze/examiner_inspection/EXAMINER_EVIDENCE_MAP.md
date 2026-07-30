# Examiner evidence map

Every mandatory claim below resolves to a frozen analytical path. SHA-256 values are locked in `SHA256SUMS`.

| Claim | Dissertation locus | Analytical source | Key / row | Code / function | Human source | Stable ID / hash |
| --- | --- | --- | --- | --- | --- | --- |
| **414 candidates** | Abstract; Ch4 §4.2 Table 4.1 | `data/manifests/phase1_decision_journal.json` | `totals.decisions=414` | `scripts/build_phase1_journal.py` | — | Journal SHA `814cc7c4…` |
| **351/414 traceability** | Ch4 Table 4.1 | same | `totals.traceability_pass=351` | `validate_traceability` | — | 351 |
| **5 agreement / 10 silence / 0 dissonance** | Ch4 Table 4.2 | `configs/annotations/excerpts/excerpt_00{1–6}.json` | comparison tags agreement/silence/dissonance | `tests/test_appendix_a_excerpt_coordinates.py` | Manual excerpts | 5 / 10 / 0 |
| **Six manual decisions** | Ch4 §4.3; App. A | same excerpts | `manual_decisions` arrays | `rebuild_appendix_a_excerpts.py` | Author annotation | 6 manuals |
| **Keyword recall 1/6** | Ch4; App. B Table B.4 | excerpts + `docs/BASELINE_KEYWORD.md` | aggregate 1/6 | `scripts/keyword_baseline.py` | Manual decisions | 1/6 |
| **LLM agreement-row recall 5/6** | App. B | triangulation agreement vs manuals | 5/6 | frozen extraction + excerpts | Manual | 5/6 |
| **no × high = 21/50** | Ch4 §4.5; Fig 4.9 | `configs/evaluation/confidence_validation_sample.json` | count A=no & B=high | sample builder / rater | Author Rubrics | 21/50; sample SHA `9d74936c…` |
| **Rule exact 80%, κ 0.48** | Ch4 Table 4.3 | `configs/evaluation/confidence_comparison_results.json` | `rule_vs_human_b` exact 0.8; κ **0.4813** | `linear_weighted_kappa`; `rule_based_confidence` | Rubric B | κ→0.48 |
| **LLM exact 76%, κ 0.39** | Table 4.3 | same | `llm_vs_human_b` exact 0.76; κ **0.3927** | `call_llm_confidence` (cached) | Rubric B | κ→0.39 |
| **20 clusters** | Ch4 §4.6; Fig 4.10 | `data/manifests/phase1_clustering_report.json` | `n_clusters=20` | `clustering.cluster_embeddings` | Heuristic labels | 20 clusters; SHA `08a6bf8d…` |
| **JEE 11/60** | Ch4 Table 4.4 | `AUDIT_E_JEE_SUMMARY.csv` | mapped total 11 | Audit E final | Human n=60 | See locator |
| **DQ 37/60** | Table 4.4 | `AUDIT_E_DQ_SUMMARY.csv` | mapped 37 | Audit E final | Human n=60 | locator |
| **Combined 26/60** | Table 4.4 | `crosstabs/AUDIT_E_jee_vs_dq_mapped.csv` | unmapped×mapped=26 | Audit E final | Human | locator |
| **Faithfulness 8/25/20/7** | Ch4 Table 4.5 | `AUDIT_E_MANIFEST.json` | category counts | human-approval gate | Author | 8/25/20/7 |
| **Report pilot 50/53** | Ch4 §4.8; App. B.6 | `docs/REPORT_PILOT.md` (+ local run if present) | 50/53 | prior non-inquiry extraction | None | narrative freeze |
| **Structural 49/50** | Ch4 §4.8; App. B.7 | `configs/evaluation/structural_reliability_results.json` | `structural_pass_count=49` | `run_structural_reliability.py` | — | SHA `8c9ce78f…` |

Wave 7A active formal submission package (title month **September 2026**):  
`outputs/dissertation_integration/run_20260730_064035_wave7a_title_page_september/`  
DOCX `70df0ee0…` · PDF `fa685483…`.  

Historical Wave 2 May-title integrity package (superseded for title-page month only):  
`outputs/dissertation_integration/run_20260729_153931_wave2_final_integrity_fixes/`  
DOCX `a829ff6d…` · PDF `40c123b9…`.
