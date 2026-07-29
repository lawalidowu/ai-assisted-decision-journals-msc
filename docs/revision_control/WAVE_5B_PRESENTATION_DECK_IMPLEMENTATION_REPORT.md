# Wave 5B — Presentation Deck Implementation Report

**Branch:** `distinction/presentation-deck`  
**Starting commit:** `4a5cfb7412a8cea3569f62b6a6b6dc2ec20f31dc` (Wave 5A)  
**Status:** Decks generated, rendered, inspected and tested. **Not committed. Not pushed.**

---

## Production method (Select C verification)

| Order | Option | Result |
| --- | --- | --- |
| 1 | Existing repo presentation builder | Present: `scripts/build_meeting_17_slide.py`, `build_covid_deck_v5.py`, etc. — all **python-pptx** patterns |
| 2 | python-pptx already installed | **Selected** — version **1.0.2** |
| 3 | Local PptxGenJS | **Not present** under `node_modules` |
| 4 | New package install | **Not performed** |

**Rendering:** Microsoft PowerPoint **16.0** via `win32com` (already available) → PDF + 1920×1080 PNG. No internet dependency.

Lock file: `presentation/DEPENDENCY_LOCK.md`.

---

## Templates and fonts

- **Theme:** Neutral academic 16:9 (`presentation/presentation_theme.py`)
- **Fonts:** Calibri (system-safe Windows)
- **No** University of Surrey logo / unapproved branding
- **No** CDN fonts, stock imagery, or external media links
- Stage colour vocabulary: source / machine / automated / human

---

## Files created

### Tracked sources (`presentation/`)

| Path | Role |
| --- | --- |
| `build_presentation.py` | Regenerable builder + package writer + COM render |
| `presentation_content.py` | Slide text, cases, timing |
| `presentation_theme.py` | Layout helpers |
| `README.md` | How to regenerate |
| `DEPENDENCY_LOCK.md` | Tool versions |
| `validation/` | Copied render/inspection logs |

### Package (`outputs/distinction_strategy/05_presentation_deck/`)

| Artefact | Role |
| --- | --- |
| `Lawal_Akeeb_MSc_Presentation_15min_12slides.pptx` | Primary deck |
| `Lawal_Akeeb_MSc_Presentation_15min_12slides.pdf` | Primary PDF |
| `Lawal_Akeeb_MSc_Presentation_10min_8slides.pptx` | Fallback deck |
| `Lawal_Akeeb_MSc_Presentation_10min_8slides.pdf` | Fallback PDF |
| `PRESENTER_RUNBOOK.md` | Speaker prompts |
| `DEMO_CUE_CARD.md` | Optional ≤2 min demo |
| `TIMING_SHEET.csv` | Per-slide seconds |
| `SLIDE_MANIFEST.csv` | Evidence trace |
| `SHA256SUMS` | Hash lock |
| `rendered_slides/primary|fallback/` | PNG inspection set |
| `validation/RENDER_LOG.json` | Export log |
| `validation/VISUAL_INSPECTION.md` | Manual visual QA |

Also: `.gitignore` allow-list for `05_presentation_deck/`; `tests/test_presentation_decks_wave5b.py`.

---

## Slide structures

**Primary (exactly 12):** S01–S12 per Wave 5A storyboard.  
**Fallback (exactly 8):** S01, S02, S03, S04, S06, S07, S09, S12 (S05/S08/S11 removed; limitations folded into S12; no live demo).

Centrepiece **phase1-082** present in both decks with source vs candidate, Rubric A=No, Rubric B=High, teaching line.

---

## Timing (planning, within official 15–20 / ≤20)

| Deck | Sum of speaker seconds | Notes |
| --- | --- | --- |
| Primary | **930 s ≈ 15:30** | Trim S05/S11 if late |
| Fallback | **600 s = 10:00** | After timing calibration |

Demo: optional ≤2 min after S07 only if buffer remains (`DEMO_CUE_CARD.md`). Presentation complete without demo.

---

## Speaker notes

Embedded in both PPTX via `python-pptx` notes slides. External runbook mirrors Wave 5A speaker notes plus deck file pointers.

---

## Demo integration

Offline launcher only (`python demo/launch_demo.py`). Not embedded in PPTX. Cue card documents skip/fallback/`print.html` recovery.

---

## Rendering and visual inspection

- Primary: 12 PDF pages + 12 PNGs  
- Fallback: 8 PDF pages + 8 PNGs  
- Manual inspection recorded in `validation/VISUAL_INSPECTION.md`  
- Correction applied: S04 stage kind labels clarified; decks regenerated

---

## Test results

```
85 passed
```

(= prior 73 + Wave 5B deck tests)

Protected hashes unchanged:

| Artefact | SHA-256 |
| --- | --- |
| Wave 2 DOCX | `a829ff6d0b4a778f2a276f9fff45af05dbc47fa268f3a9b0b131a87099b0a2e2` |
| Wave 2 PDF | `40c123b9743277d9083d3b66eb855e0fa7a57101017d08a7d8a2d94558a63519` |
| Frozen journal | `814cc7c47a9f75bfc0a6c7b693feec7073e59131398d89fab7c9111fbb2e5e06` |
| Demo evidence 016/082/090/246 | Unchanged Wave 4 hashes |

---

## Package hashes (post-final rebuild)

| File | SHA-256 |
| --- | --- |
| `…_15min_12slides.pptx` | `5e6c5329e2191d48101719d548897806171b75a3fb99819c29d6a033347be70f` |
| `…_10min_8slides.pptx` | `83efb1a4c621b3fcaac8c46b1bba729d04492362e5b52e4739a42d8aedba3148` |
| `…_15min_12slides.pdf` | `b117f18266c1b2f959f6d2ff44a3760374f4649305a4a29deb7b707bf57022cd` |
| `…_10min_8slides.pdf` | `f2c907c9f2adc231dff38299ca0f2823eb7f6d4cace0e2fd51212796a972d2fc` |

Full inventory: package `SHA256SUMS`.

---

## Unresolved issues

| Rank | Issue | Notes |
| --- | --- | --- |
| Critical | None | — |
| High | None | — |
| Medium | Projector-dependent density on S06 | Acceptable at 1920×1080; footnote holds supporting metrics |
| Low | PPTX bytes change if PowerPoint re-saves | Regenerate via `python presentation/build_presentation.py` |
| Low | No official Surrey template used | None clearly authorised/suitable; neutral theme applied |

---

## Confirmation

Dissertation Markdown/DOCX/PDF, frozen journal, annotations, analytical datasets, examiner package and offline demo evidence were **not modified**.

**Stop:** awaiting approval before commit/push. No PPTX-only manual edits; regenerate from tracked sources.

---

## Desktop application verification (pre-commit)

Recorded in `outputs/distinction_strategy/05_presentation_deck/validation/DESKTOP_POWERPOINT_VERIFICATION.json` and `DESKTOP_APP_VERIFICATION.md`.

Both PPTX files opened in desktop Microsoft PowerPoint **without repair warnings**. Primary = 12 slides; fallback = 8; no hidden slides; notes present; phase1-082 readable; PDFs 12/8 pages with no blank pages.
