# Wave 5A — Presentation Storyboard Report

**Branch:** `distinction/presentation-storyboard`  
**Starting commit:** `5aae5c0e32bbd5855b6908fe4c09e7e65af054e4` (Wave 4)  
**Status:** Discovery + storyboard complete. **No PPTX. Not committed. Not pushed.**

Planning choice (user Select B): **15-minute expanded model** as preferred working target, clearly labelled as a **planning assumption** within the official handbook envelope; **10-minute core** retained as fallback.

---

## 1. Official requirements found

| Topic | Finding | Class |
| --- | --- | --- |
| Presentation required | Yes — presentation + viva questions after dissertation submission | Authoritative |
| Duration | **15–20 minutes**, hard cap **≤20 minutes**, then questions | Authoritative |
| Slide max | **≤12 slides** | Authoritative |
| Live demo | Not mandatory; checklist assesses demonstration **if present** | Authoritative |
| Total viva (Q&A) duration | **Not found** | — |
| Slide file submission format/deadline | **Not found** | — |

**Authoritative source:**  
`Official dissertation resources/Project handbook/ProjectHandbook2025-26.pdf` (EEEM004 2025/26), mirrored in `outputs/_wave6a_handbook_extract.txt`.

**Source hierarchy:** Handbook PDF → Wave 6A extract → dissertation / supervisor notes (advisory) → self-authored demo walkthrough timing (advisory only).

**Conflict:** “≤20” vs “15–20” are compatible. Treat as plan 15–20, hard stop 20, ≤12 slides.

**Planning vs official:** The **15-minute** preferred model is a **working target inside** the official range, not a replacement for handbook wording. Continue searching if school guidance updates.

---

## 2. Central narrative

- **Claim:** Not an automatically verified policy catalogue; a governed workflow keeping machine candidates, automated checks, human validation and source evidence separate.  
- **Question:** Can an LLM-assisted workflow produce useful, auditable candidates without treating generated text as authoritative evidence?  
- **Centrepiece:** phase1-082 — quote support ≠ journal membership.  
- **Six distinctions:** generation · mechanical traceability · evidence strength · semantic faithfulness · journal validity · framework interpretation.

Exact Ch1 aim retained (no rewrite into stronger claims). No numbered RQs in Ch1 — Aim + Objectives 1–6 only.

---

## 3. Proposed slide counts and timing models

| Model | Label | Slides shown | Role |
| --- | --- | --- | --- |
| Official envelope | Authoritative | ≤12 | Hard max |
| **15-minute expanded** | **Preferred planning** | **12 (S01–S12)** | Primary storyboard + speaker timing |
| **10-minute core** | Planning fallback | **8** (S01–S04, S06, S07, S09, S12) | Removes S05, S08, S11; limits spoken into close; **no live demo** |

Demo allocation (15-min only): optional ≤**2 minutes** controlled offline walkthrough after S07 **if buffer remains**; presentation remains complete if omitted.

---

## 4. Demo integration recommendation

**Preferred:** Retain Wave 4 demo as **examiner-requested / time-buffered backup**; static S07 carries the centrepiece.  
**Allowed:** Short controlled `python demo/launch_demo.py` open of phase1-082 only (≤2 min).  
**Fallback:** `demo/print.html` or verbal evidence.  
**Reject:** Embedding a full five-minute demo inside the formal presentation.

---

## 5. Required visuals (for Wave 5B — not produced here)

- Simplified governed workflow (S04)  
- Evaluation layer strip (S05)  
- Headline number board + highlighted no×high (S06)  
- phase1-082 candidate vs quote card (S07)  
- Optional 016/090/246 mini cards (S08)  
- Contribution four-block + limitation chips + closing quote  
- Optional offline screenshots (capture later)

See `docs/presentation/VISUAL_ASSET_PLAN.md`.

---

## 6. Likely viva pressure points

Documented in `PRESENTATION_VIVA_ALIGNMENT.md`: AI vs document processing; traceability≠validity; no×high; moderate κ; one model; no second reviewer; case selection; generalisation; deployment; framework subjectivity; hallucination/faithfulness; novelty.

---

## 7. Files created (Wave 5A)

| Path | Role |
| --- | --- |
| `docs/presentation/PRESENTATION_STORYBOARD.md` | Requirements + storyline + per-slide board + timing |
| `docs/presentation/SLIDE_EVIDENCE_MAP.csv` | Claim → frozen evidence |
| `docs/presentation/PRESENTATION_SPEAKER_NOTES.md` | Speaking prompts / cuts |
| `docs/presentation/VISUAL_ASSET_PLAN.md` | Asset inventory only |
| `docs/presentation/PRESENTATION_VIVA_ALIGNMENT.md` | Viva pressure map |
| `docs/revision_control/WAVE_5A_PRESENTATION_STORYBOARD_REPORT.md` | This report |
| `tests/test_presentation_storyboard_wave5a.py` | Validation checks |

**Unchanged (verified):** dissertation MD/DOCX/PDF intent (hashes), frozen journal, analytical JSON/CSV, annotations, Wave 3 examiner package, Wave 4 offline demo evidence hashes.

---

## 8. Exact files proposed for Wave 5B slide production

1. `docs/presentation/PRESENTATION_STORYBOARD.md`  
2. `docs/presentation/SLIDE_EVIDENCE_MAP.csv`  
3. `docs/presentation/PRESENTATION_SPEAKER_NOTES.md`  
4. `docs/presentation/VISUAL_ASSET_PLAN.md`  
5. Wave 4 `demo/` for optional screenshots (read-only)  
6. Existing figures under `outputs/figures/` **if present on disk**  
7. Handbook citation for title-slide compliance note (≤12 / 15–20)

Wave 5B may create PPTX/PDF slides — **not** done in 5A.

---

## 9. Unresolved gaps

| Rank | Gap | Notes |
| --- | --- | --- |
| Critical | None for storyboard stage | — |
| High | Confirm figure PNGs exist on presentation machine | Visual plan lists expected paths; regenerate offline in 5B if missing |
| Medium | Total viva Q&A duration unknown | Do not invent; examiners set slot |
| Medium | No official slide **submission** channel/format found | Bring slides to viva; do not assert upload rule |
| Low | Dense S06 number board may need split visual treatment in 5B | Keep ≤12 slides via design, not extra slide count |
| Low | Annotated handbook tag object vs peel | Requirements use PDF wording via extract |

---

## 10. Stop condition

Storyboard, evidence map, speaker notes, visual plan, viva alignment and this report are complete.  
**Do not create PPTX. Do not commit or push until approval.**
