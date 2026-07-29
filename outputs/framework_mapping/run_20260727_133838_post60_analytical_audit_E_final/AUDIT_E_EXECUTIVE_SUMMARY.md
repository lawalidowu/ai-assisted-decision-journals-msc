# Audit E — Executive Summary (Final)

Generated (UTC): 2026-07-27T13:38:38.779881+00:00  
Status: **FROZEN** — human-approved corrected terminology

## What was analysed

Read-only descriptive analysis of 60 human-adjudicated decision-journal entries from `CONSISTENCY_CORRECTED_REFERENCE.csv` (SHA256 verified). Input: single-reviewer human-adjudicated reference set after AI-assisted source-integrity (Audit C) and coding-consistency (Audit D) audits.

## Key descriptive findings

| Domain | Finding |
|--------|---------|
| JEE mapped | 18.3% (11/60) |
| JEE no_mapping | 26.7% (16/60) |
| JEE insufficient_evidence | 36.7% (22/60) |
| DQ mapped | 61.7% (37/60) |
| Source-level traceable (`traceability_ok=True`) | 88.3% (53/60) |

**Human-reviewed candidate-decision traceability (single reviewer):**

| Category | n | % |
|----------|--:|---|
| Exact or near-verbatim | 8 | 13.3% (8/60) |
| Substantively faithful paraphrase | 25 | 41.7% (25/60) |
| Materially unsupported or altered | 20 | 33.3% (20/60) |
| Traceability=False | 7 | 11.7% (7/60) |

Among the 11 JEE-mapped records, R4 occurred in 3 (27.3%, 3/11), while P3, D2 and R5 each occurred in 2 (18.2%, 2/11).

Among the 37 DQ-mapped records, commitment_to_follow_through was the **primary** element in 22 (59.5%, 22/37), helpful_frame in 8 (21.6%, 8/37), and clear_values in 6 (16.2%, 6/37).

The most frequent combined outcome in this purposive 60-record pilot was an observable Decision Quality element without a defensible JEE mapping, occurring in 26 of 60 records (43.3%).

## Did the frameworks add useful interpretation?

**Yes, with boundaries.** JEE mapping identifies specific preparedness capacities where passage evidence supports it. Decision Quality elements are more frequently observable than JEE capacities. `no_mapping` and `insufficient_evidence` are analytically distinct boundary conditions, not extraction failures.

## Traceability finding

Generated decision statements were not treated as authoritative evidence. Framework interpretation relied on validated source passages rather than generated decision wording. These categories were assigned by a single reviewer and should be interpreted as a structured feasibility assessment rather than an independently validated estimate of model error.

## Principal limitations

Purposive 60-record pilot; not representative of the 414-entry corpus. Single-reviewer workflow. No inferential or causal claims.

## Recommendations

| Decision | Recommendation |
|----------|----------------|
| **Dissertation integration** | **GO WITH LIMITATIONS** — supplementary feasibility analysis; does not require mapping all 414 records |
| **Full-corpus scaling** | **GO AFTER SPECIFIED CHANGES** — workflow stable; plan human review burden and periodic consistency audits |
