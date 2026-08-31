# Audit E — Analytical Report (Final)

Generated (UTC): 2026-07-27T13:38:38.779881+00:00  
Status: **FROZEN**

## 1. Verification

| Check | Result |
|-------|--------|
| Input SHA256 | `eec6c4e87dfa9b42421a13fce4ebca9c84701ad80d765f19fbdba59ab0c75770` — verified |
| Records | 60 |
| Pending review | 0 |
| Coding values changed | No |

## 2. Traceability interpretation

Generated decision statements were not treated as authoritative evidence. Of the 60 candidate decisions:

- 8 (13.3% (8/60)) exact or near-verbatim
- 25 (41.7% (25/60)) substantively faithful paraphrases
- 20 (33.3% (20/60)) materially unsupported or altered despite traceable source
- 7 (11.7% (7/60)) non-traceable (`traceability_ok=False`)

**Limitation:** Single-reviewer human classification; structured feasibility assessment, not independent gold standard.

**Technical diagnostic only:** 53 of 60 records (88.3% (53/60)) show the lexical flag `non_exact_non_substring_string_match` (non-identical strings with no substring containment). This must not be interpreted as substantive divergence.

**Analytical implications retained:**
- Source quotations must remain attached to decision objects
- Human review required before decision-journal records are used for audit or accountability
- Generated decisions are candidate summaries, not authoritative records
- Textual traceability and framework applicability are separate dimensions

## 3. Review provenance

See `AUDIT_E_REVIEW_PROVENANCE_NOTE.md`. Fifty-two flagged records retained prior adjudication via AI-assisted keep_all **without individual interactive Audit D re-review**.

## 4. JEE and DQ findings

JEE mapped: 18.3% (11/60). DQ mapped: 61.7% (37/60). `no_mapping` and `insufficient_evidence` reported separately.

The most frequent combined outcome in this purposive 60-record pilot was DQ mapped / JEE unmapped: 43.3% (26/60) (26/60). This pattern must not be generalised to the 414-entry corpus.

## 5. Audit D sensitivity

19 field changes across 6 records; JEE mapped 12→11; DQ mapped unchanged at 37. Edge-case refinement only.

## 6. GO/NO-GO

Dissertation integration: **GO WITH LIMITATIONS**. Full-corpus scaling: **GO AFTER SPECIFIED CHANGES**.
