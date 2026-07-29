# Appendix B: Supporting extraction and robustness results

This appendix holds detailed tables moved out of Chapter 4 so that the main results chapter can focus on key findings. Corpus totals and interpretation remain in Chapter 4 Sections 4.2–4.8.

## B.1 Per-hearing extraction and traceability

| Hearing date | Chunks | Decisions | Traceability pass | Pass rate |
|--------------|--------|-----------|-------------------|-----------|
| 28 Nov 2023 | 212 | 32 | 29/32 | 91% |
| 30 Nov 2023 | 181 | 50 | 43/50 | 86% |
| 01 Dec 2023 | 94 | 32 | 28/32 | 88% |
| 07 Dec 2023 | 144 | 36 | 32/36 | 89% |
| 11 Dec 2023 | 185 | 56 | 45/56 | 80% |
| 13 Dec 2023 | 168 | 106 | 93/106 | 88% |
| 14 Dec 2023 | 78 | 57 | 46/57 | 81% |
| 23 May 2024 | 168 | 45 | 35/45 | 78% |

## B.2 Default versus inquiry prompt extraction counts

| Transcript | Default prompt decisions | Inquiry prompt decisions |
|------------|--------------------------|--------------------------|
| 30 Nov 2023 | 333 | 50 |
| 01 Dec 2023 | 162 | 32 |

## B.3 Error taxonomy definitions and counts (n = 42)

| Error type | Definition | Count | % |
|------------|------------|------:|--:|
| Advocacy or urging | Ministerial or colloquial urging; not a recorded agreement | 3 | 7% |
| Future recommendation | Retrospective lesson or future “should”; not adopted | 3 | 7% |
| Narrative description | Descriptive account; not a decision event | 4 | 10% |
| Duplicate | Near-duplicate extraction of the same passage | 1 | 2% |
| Traceability failure | Quote not locatable in the source text | 2 | 5% |
| Bundled measures | Multiple distinct measures in one LLM item | 4 | 10% |
| Witness opinion | Belief or state of mind; not a formal decision | 0 | 0% |
| Valid or borderline | Plausible decision recall; may be a true positive | 10 | 24% |
| Other | Unclassified by heuristics | 15 | 36% |

Nine items were author-validated; 33 were heuristic-classified. The distribution is not a full human validation of all 42 items and is not representative of all 414 candidates.

## B.4 Keyword-baseline results by excerpt

| Excerpt | Manual decisions | LLM agreement rows | Keyword candidates | KW recall (manual) |
|---------|------------------|--------------------|--------------------|---------------------|
| excerpt_001 | 1 | 1 | 2 | 1/1 |
| excerpt_002 | 2 | 2 | 0 | 0/2 |
| excerpt_003 | 0 | 0 | 0 | n/a |
| excerpt_004 | 0 | 0 | 0 | n/a |
| excerpt_005 | 0 | 0 | 0 | n/a |
| excerpt_006 | 3 | 2 | 1 | 0/3 |

Aggregate recall versus the six manual decisions: keyword baseline 1/6; inquiry-mode LLM agreement rows 5/6.

## B.5 GRACE-adapted quality scores

| Dimension | Mean (1–5) | n |
|-----------|------------|---|
| Interpretability | 3.06 | 16 |
| Actionability | 2.69 | 16 |
| Nuance | 2.38 | 16 |
| Redundancy | 4.31 | 16 |

Scores are descriptive only and are not interpreted as normative journal-validity benchmarks.

## B.6 Report-genre pilot summary

| Metric | Value |
|--------|-------|
| Document | Module 2, 2A, 2B, 2C Report *In Brief* |
| Processed text length | 12,659 characters |
| Extraction mode | Default prompt (not inquiry mode) |
| Decisions extracted | 53 |
| Traceability pass | 50/53 (94%) |
| Traceability fail | 3 |

No manual annotation was performed on the report pilot. These items were not merged into the fixed reference dataset.

## B.7 Structural reliability stress-test

| Metric | Value |
|--------|-------|
| Total outputs | 50 |
| Structural pass (all checks) | 49 |
| Structural consistency rate | 98% |
| JSON parse failures | 0 |
| Schema / missing-field failures | 0 |
| Sole failure mode | Source quote not found in text (1 output) |

Design: ten fixed transcript chunks × five regenerations at temperature 0.3. The rate characterises schema robustness under limited variation; it does not establish decision accuracy or journal validity (Chapter 3 Section 3.1; Chapter 4 Section 4.8).

## B.8 n = 60 review provenance note

Detailed machine-readable provenance for the n = 60 review is retained in the final analytical-audit repository output.

| Route | n | Meaning |
|-------|--:|---------|
| Interactive confirmation of proposed corrections | 6 | Earlier coding updated after interactive review |
| Retained without new record-by-record review | 52 | Earlier coding retained after consistency screening |
| Automatic-clear | 2 | No consistency flags; earlier coding unchanged |

The pilot remains a single-reviewer feasibility assessment, not independently validated gold-standard annotation.
