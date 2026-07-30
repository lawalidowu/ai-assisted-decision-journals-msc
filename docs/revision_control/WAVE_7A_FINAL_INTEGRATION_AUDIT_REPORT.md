# Wave 7A — Final integration and submission-freeze audit report

**Branch:** `distinction/final-submission-freeze`  
**Parent content commit (Wave 6):** `c1feba145bdc46164b5daae79ec1a0d3901e97d0`  
**Status:** Freeze candidate refreshed after **September 2026** title-page month gate — **not committed / not pushed**; main **not** fast-forwarded; **no** final tag.

---

## Title-page month gate (resolved)

| Item | Value |
| --- | --- |
| Previous title month | May 2026 |
| Confirmed official month | **September 2026** |
| Source change | `scripts/build_submission_docx.py` (`SUBMISSION_MONTH`) |
| Gate record | `docs/revision_control/WAVE_7A_TITLE_PAGE_MONTH_GATE.md` |
| Active package | `outputs/dissertation_integration/run_20260730_064035_wave7a_title_page_september/` |

---

## A. Repository history

Unchanged from prior Wave 7A audit: linear Wave 2–6 ancestry; `origin/main` at `72e9fc4e…`; baseline tag peel unchanged; FF of main possible but **not performed**.

---

## B–C. Requirements and artefact roles

Unchanged. Formal dissertation candidates are now the **September** package; Wave 2 May-title package remains historical.

---

## D. Dissertation verification (active September build)

| Check | Result |
| --- | --- |
| DOCX SHA-256 | `70df0ee0992cd55635053f00926923d1b39357312f820fe29883810a0d9e96b5` |
| PDF SHA-256 | `fa685483df8e19972d798dffd58801fbb14b48f1928e62af12153b971406c0b5` |
| Physical / displayed pages | **77 / 77** |
| Official / displayed words | **14,558 / 14,558** (no discrepancy) |
| Title page | **September 2026** |
| Signature/date | **Blank** |
| Visual inspection | **77/77 PASS** |
| Flag counts / Appendix A / JEE leak | PASS |

Historical Wave 2 May binaries remain byte-stable (`a829ff6d…` / `40c123b9…`).

---

## E–G. Presentation, demo, examiner/viva

| Area | Result |
| --- | --- |
| Presentation PPTX/PDF hashes | Unchanged vs Wave 5B |
| Demo evidence hashes | Unchanged |
| Demo smoke | PASS |
| Viva bank | 102 / 28 adversarial; mocks 30/30 |
| Examiner map | Updated to cite active September package |

---

## H. Regression

```
109 passed
```

Protected analytical journal, annotations (via suite), demo, and decks unchanged.

---

## I. Security / GitHub

Secret scan PASS on scanned trees. Repository remains **PRIVATE**.

---

## J. Freeze package

Path: `outputs/distinction_strategy/07_final_submission_freeze/`  
Formal submission copies match active September hashes exactly.

---

## Issue register

| Rank | Issue | Notes |
| --- | --- | --- |
| Critical | None | — |
| High | None | — |
| Medium | ~~Title-page May vs September~~ | **CLOSED** — September 2026 |
| Medium | Portal PDF/DOCX/filename unknown until email | Author portal action |
| Low | Presentation portal upload unknown | Viva-use unless email requires |

---

## Remaining author actions

1. Sign and date declaration at submission  
2. Follow emailed SurreyLearn instructions; upload ≤20 MB by 1 Sep 2026  
3. Bring presentation / optional demo to viva  
4. Approve commit of Wave 7A artefacts when ready; later main FF + final tag  

**Do not commit or push until approval.**
