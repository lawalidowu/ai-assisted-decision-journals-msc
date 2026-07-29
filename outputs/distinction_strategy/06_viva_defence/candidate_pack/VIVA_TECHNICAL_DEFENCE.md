# Technical and reproducibility defence

## What can be reproduced offline?

- Frozen journal, evaluation JSON/CSV, Audit E aggregates, demo evidence, presentation rebuild from tracked sources.  
- Offline demo: `python demo/launch_demo.py` (localhost only).

## What may need public downloads?

- Inquiry PDFs if examiner wants original hearing files (public URLs recorded as provenance text; not required to render the offline demo).

## What needs an OpenAI API key?

- Live regeneration / some historical generation pipelines.  
- **Not** required for examiner offline demo or frozen claim verification.

## Frozen historical outputs

- Phase 1 candidates locked in `phase1_decision_journal.json`.  
- Live regen is **not** claimed byte-identical.

## Human judgement dependence

- Rubrics A/B, faithfulness categories, JEE/DQ mappings — author adjudication.

## Untracked historical `outputs/run_*`

- Prefer frozen journal + hashes over raw run trees.  
- Demo JSON may cite historical run SHA if present locally.

## Hashes

- Journal `814cc7c4…`; Wave 2 DOCX/PDF; demo case SHA-256; Audit E file hashes; presentation deck SHA256SUMS.

## Audit E path ambiguity

- Resolved by `docs/examiner_evidence/AUDIT_E_CANONICAL_LOCATOR.md` (one authoritative path per claim).

## End-to-end claim follow

Evidence map → analytical path → stable ID → demo case / table.

## Git / baseline tag

- Late Git introduction acknowledged historically.  
- Baseline tag protects corrected Wave 6C dissertation freeze for distinction waves.  
- Do not rewrite protected history.

## Why raw transcripts/PDFs not committed

- Size, bulk, and packaging policy; public sources remain citable; frozen extracts suffice for claims.

## Security / privacy

- No API keys in demo; localhost bind; no full transcripts in demo JSON; privacy notes in examiner package.

## Statistical defence (do not invent CIs or p-values)

| Concept | Safe explanation |
| --- | --- |
| Exact agreement | Raw match rate vs Rubric B (rule 0.80; LLM 0.76 on n=50). |
| Weighted κ | Linear weighted; adjacent ordinal disagreements less severe (0.4813 → 0.48; 0.3927 → 0.39). |
| Why they differ | κ adjusts for chance / ordinal structure; exact agreement does not. |
| Prevalence | Imbalance can inflate/deflate κ; report both; interpret cautiously. |
| “Moderate” not “strong” | Do not upgrade κ language beyond what the dissertation states. |
| Sample size | Descriptive case-study samples — not population inferential claims. |
| 21/50 | Analytically important modal cell; **not** a universal rate. |
| Forbidden | Invented confidence intervals, p-values, or significance tests not in the study. |
