# Wave 7A — Title-page month gate

**Status:** **CLOSED** — September 2026 applied, rebuilt, and revalidated.  
**Branch:** `distinction/final-submission-freeze`  
**Parent HEAD at gate open:** `c1feba145bdc46164b5daae79ec1a0d3901e97d0`

## Confirmed official submission month

**September 2026**

## Previous value

**May 2026** (title-page month only)

## Exact source file changed

| File | Change |
| --- | --- |
| `scripts/build_submission_docx.py` | `SUBMISSION_MONTH = "September 2026"` (was `"May 2026"`) |
| `scripts/build_surrey_dissertation_docx.py` | Same constant updated for consistency (secondary/legacy builder) |

**Authoritative controller for the active Surrey title page:** `scripts/build_submission_docx.py` → `SUBMISSION_MONTH`, applied by `patch_front_matter()`.

Dissertation Markdown chapters were **not** edited. Generated DOCX/PDF were rebuilt from this constant — not hand-edited.

## Reason for correction

Author confirmed the official University submission month is **September 2026** (aligned with `MScDissertationTemplate2026.docx` / handbook timing). Resolves the Wave 7A Medium title-page month gate without prose or analytical changes.

## What did not change

- Dissertation body prose, analysis, tables, figures
- Annotations, frozen journal (`814cc7c4…`), evaluation data
- Demo evidence hashes; presentation PPTX/PDF hashes
- Blank declaration **Author Signature** and **Date** fields

## Historical / non-title occurrences of “May 2026”

Left unchanged where they are **not** the active title-page month:

- Reference “Accessed: 22 May 2026” dates in `dissertation/REFERENCES.md`
- Historical Wave 6B/6C approval records (superseded for title-page month)
- Working notes / meeting logs
- Wave 2 package `run_20260729_153931_wave2_final_integrity_fixes/` — May-title historical integrity package (**byte-stable**; superseded for title month only)

## Affected generated artefacts

| Artefact | Effect |
| --- | --- |
| `dissertation/Lawal_MSc_Dissertation.docx` | Rebuilt |
| `outputs/dissertation_integration/run_20260730_064035_wave7a_title_page_september/` | **Active** formal DOCX/PDF |
| `outputs/dissertation_integration/ACTIVE_FORMAL_SUBMISSION_POINTER.json` | Points to active package |
| `outputs/distinction_strategy/07_final_submission_freeze/` | Refreshed |
| `docs/examiner_evidence/EXAMINER_EVIDENCE_MAP.md` | Active package pointer updated |

## Validation performed

| Check | Result |
| --- | --- |
| Title page shows September 2026 | **PASS** (visual + text) |
| Standalone title-month “May 2026” absent in active DOCX/PDF | **PASS** |
| Signature/date blank | **PASS** |
| Body words (markdown / displayed) | **14,558 / 14,558** |
| Pages (displayed / physical) | **77 / 77** |
| DOCX SHA-256 | `70df0ee0992cd55635053f00926923d1b39357312f820fe29883810a0d9e96b5` |
| PDF SHA-256 | `fa685483df8e19972d798dffd58801fbb14b48f1928e62af12153b971406c0b5` |
| Pytest | **109 passed** |
| Journal / demo / deck hashes | Unchanged |
| Historical Wave 2 DOCX/PDF hashes | Unchanged (`a829ff6d…` / `40c123b9…`) |

## Do not commit

Await explicit approval before commit/push/merge/tag.
