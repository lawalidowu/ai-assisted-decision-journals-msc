# Wave 2 Gate — Joint External Evaluation leak-term warning

**Branch:** `distinction/final-integrity-fixes`  
**Baseline commit:** `72e9fc4e7b8d4979fb3de9a63a9e8350056aed28`  
**Status:** Scanner-only false-positive fix. **Not committed. Not pushed.**

## Root cause

`scripts/build_submission_docx.py` `verify_output()` scans DOCX XML for `LEAK_TERMS`.
The list incorrectly included **`Joint External Evaluation`**, a legitimate WHO / IHR
domain phrase that this dissertation intentionally uses for the JEE preparedness-mapping
pilot. Classification: **(c) legitimate domain term** + **(d) overly broad validation rule**.

Original purpose of the scan: catch template placeholders and foreign-sample author names
(`Jesutomiwa`, `Kanojia`, `<Technical CHAPTER>`, etc.) leaking into submission output.

## Triggering files (examiner-facing, intentional)

Occurrences of the phrase in active dissertation markdown (pre-existing; **unchanged**):

| File | Role |
| --- | --- |
| `dissertation/ABSTRACT.md` | Full phrase in methods summary |
| `dissertation/CHAPTER_1_INTRODUCTION.md` | Full phrase + later `JEE` |
| `dissertation/CHAPTER_2_LITERATURE.md` | Literature first domain discussion |
| `dissertation/CHAPTER_3_METHODS.md` | Formal expansion `Joint External Evaluation (JEE)` + methods |
| `dissertation/CHAPTER_4_RESULTS.md` | Results use expanded form then `JEE` |
| `dissertation/CHAPTER_5_DISCUSSION.md` | Discussion expansion + abbreviation |
| Capction text in `scripts/build_dissertation_docx.py` | Figure 3.1 caption (build helper) |

No occurrence was a placeholder, drafting note, or foreign dissertation leak.

## Scanner change

In `scripts/build_submission_docx.py`:

- Removed exact phrase `"Joint External Evaluation"` from `LEAK_TERMS`.
- Documented why in a short comment.
- Retained all genuine leak terms (`Jesutomiwa`, `Kanojia`, template placeholders, etc.).
- Did **not** disable leak-term scanning.

## Tests added

`tests/test_leak_term_scan.py`:

- JEE phrase / `JEE` absent from `LEAK_TERMS`
- Genuine leak terms still configured and detected on synthetic DOCX probes
- Legitimate JEE sentence does not trigger `verify_output`
- Wave 2 candidate DOCX does not flag JEE / foreign authors
- Dissertation JEE expansion strings remain present (prose lock; no rewrite)

## Dissertation / binaries

| Item | Changed? |
| --- | --- |
| Dissertation prose | **No** |
| Analytical JSON/CSV/annotations | **No** |
| Candidate DOCX/PDF | **No** (not rebuilt) |

## Candidate package hash confirmation

| Artefact | Expected SHA-256 | Status |
| --- | --- | --- |
| DOCX | `a829ff6d0b4a778f2a276f9fff45af05dbc47fa268f3a9b0b131a87099b0a2e2` | unchanged |
| PDF | `40c123b9743277d9083d3b66eb855e0fa7a57101017d08a7d8a2d94558a63519` | unchanged |

## Final warning status

`verify_output(Wave2 DOCX)` → **`[]`** (empty).  
`verify_output(working Lawal_MSc_Dissertation.docx)` → **`[]`**.  
No `Joint External Evaluation` warning. Genuine leak terms still configured and regression-tested.

## Test results

**36 passed** (21 Appendix A + 3 flag/word + 12 leak-term scan cases).  
DOCX/PDF hashes confirmed unchanged. No commit / no push.
