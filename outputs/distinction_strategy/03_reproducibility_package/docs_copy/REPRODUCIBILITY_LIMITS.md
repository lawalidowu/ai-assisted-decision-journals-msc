# Reproducibility limits

## Explicit non-claims

1. **No byte-identical LLM regeneration.** Phase 1 used `gpt-4o-mini` at temperature 0 without a pinned model snapshot hash. Re-running `scripts/run_extraction.py` may change decisions.
2. **Frozen journal is authoritative** for the 414 / 351 figures. Do not overwrite it to “match” a new live run.
3. **Human judgements are not auto-reproducible.** Rubric A/B, triangulation, taxonomy, JEE/DQ, and faithfulness classifications require the frozen human records.
4. **Clustering labels are heuristic navigation aids**, not a validated ontology.
5. **Mechanical traceability ≠ page-level PDF audit.** Quotes are checked against processed chunk text.
6. **Report-genre pilot (50/53) is not in the 414 journal** and was not manually validated.
7. **Structural reliability 49/50** measures schema robustness at temperature 0.3 only.

## Class misuse guard

Do **not** label any of the following as “fully reproducible offline” (class 1):

- LLM extraction of the corpus (class 3/4)
- Embedding-based cluster regeneration (class 3/4)
- Human Rubric / JEE / faithfulness codes (class 5)

## Dependency caution

Python package pins in `requirements.txt` (if present) may use `>=` ranges. Behaviour of PDF text extraction can vary slightly across `pypdf` versions.
