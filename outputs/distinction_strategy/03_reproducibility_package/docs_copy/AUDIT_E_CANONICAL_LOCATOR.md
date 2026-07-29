# Audit E canonical locator

**Purpose:** Resolve path ambiguity for the n=60 framework-mapping freeze.  
**Rule:** Exactly **one** authoritative path per dissertation claim. Historical aliases are non-authoritative.

**Precedence:**  
1. `AUDIT_E_*` artefacts under `run_20260727_133838_post60_analytical_audit_E_final/` for **aggregate** dissertation counts.  
2. `CONSISTENCY_CORRECTED_REFERENCE.csv` for **record-level** human JEE/DQ codes.  
3. Earlier framework_mapping runs are **aliases only** and must not be used to re-state counts.

If two files appear to support the same claim without this precedence rule, package validation **fails**.

## Authoritative inventory

| Logical name | Authoritative path | SHA-256 | Role | Git | Aliases (do not use for claims) |
| --- | --- | --- | --- | --- | --- |
| Audit E manifest | `outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/AUDIT_E_MANIFEST.json` | `8262948f55a04950983dcc146073a51822422237fdc8d92abf966c377c4bcd20` | Aggregate lock; faithfulness category counts **8/25/20/7** | Tracked | Earlier `run_20260727_131920_*` approval gate trees |
| JEE summary | `…/AUDIT_E_JEE_SUMMARY.csv` | `499b82c045713821f8610788b395b4ef6f82342b1577bbc6380d00fbfd326200` | **JEE mapped = 11/60** | Tracked | Pre-final Audit E/D scratch CSVs |
| DQ summary | `…/AUDIT_E_DQ_SUMMARY.csv` | `2bdd445b3fa7782ac831e626d862d5661feab7c0c6e253302afd75725784c049` | **DQ mapped = 37/60** | Tracked | Same |
| Executive summary | `…/AUDIT_E_EXECUTIVE_SUMMARY.md` | `ab964480adffd1e7bf149b42ecdd1142e13aaa8f30fed260d83f12cbdefd74db` | Narrative of 11/60, 37/60, 26/60, faithfulness | Tracked | `AUDIT_E_ANALYTICAL_REPORT.md`, `AUDIT_E_DISSERTATION_FINDINGS.md` (supporting) |
| JEE×DQ crosstab | `…/crosstabs/AUDIT_E_jee_vs_dq_mapped.csv` | `773724149e29f2314e6d7b9c28ab3006ba73cb010322e17e8c722496c691f51d` | **Combined DQ mapped ∩ JEE unmapped = 26/60** | To be allow-listed | Manual recount from other crosstabs |
| Faithfulness row file | `…/AUDIT_E_TRACEABILITY_HUMAN_CLASSIFICATION.csv` | `32a51e3f724d58c86441cf1b505e213d4a87fb320047ae098f0ab571708df84c` | Per-ID category; aggregates must match manifest | To be allow-listed | Human-approval intermediate CSVs under `run_20260727_131920_*` |
| Corrected human codes | `outputs/framework_mapping/run_20260727_094015_post60_coding_consistency_audit/CONSISTENCY_CORRECTED_REFERENCE.csv` | `eec6c4e87dfa9b42421a13fce4ebca9c84701ad80d765f19fbdba59ab0c75770` | Record-level JEE/DQ after consistency corrections | Tracked | `CONSISTENCY_SCREENING_RESULTS.csv`, unrepaired review workbooks |

## Claim → authoritative path (mandatory)

| Claim | Use this path only | Key / row |
| --- | --- | --- |
| JEE = 11/60 | `AUDIT_E_JEE_SUMMARY.csv` | `jee_mapped_total,mapped,11` |
| DQ = 37/60 | `AUDIT_E_DQ_SUMMARY.csv` | `dq_mapped_total` mapped row (`37`) |
| Combined = 26/60 | `crosstabs/AUDIT_E_jee_vs_dq_mapped.csv` | `jee_outcome=unmapped`, `dq_outcome=mapped`, `count=26` |
| Faithfulness 8/25/20/7 | `AUDIT_E_MANIFEST.json` | `traceability_category_counts`: exact=8, paraphrase=25, materially_unsupported=20, traceability_false=7 |

Executive summary may **narrate** these numbers but is not a second count authority when disagreement occurs—counts win via the rows above.
