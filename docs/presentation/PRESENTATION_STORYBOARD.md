# Presentation storyboard — Distinction Strategy Wave 5A

**Branch:** `distinction/presentation-storyboard`  
**Parent commit:** `5aae5c0e32bbd5855b6908fe4c09e7e65af054e4` (Wave 4)  
**Status:** Discovery + storyboard only. No PPTX. Not committed.

---

## Official requirements (authoritative)

| Requirement | Wording (faithful) | Source | Status |
| --- | --- | --- | --- |
| Presentation required | After report submission, student must “give a presentation on it, and answer questions in a viva.” | `Official dissertation resources/Project handbook/ProjectHandbook2025-26.pdf` p.3; extract `outputs/_wave6a_handbook_extract.txt` ll.115–117 | **Authoritative, current (EEEM004 2025/26)** |
| Hard duration cap | Presentation “should last **no longer than 20 minutes**” then questions afterwards. | Same, ll.117–119 | **Authoritative** |
| Duration range | Examiners schedule a “**15–20-minute presentation** … followed up with questions”. | Same, ll.125–128 | **Authoritative** |
| Slide max | “…**no more than 12 slides** in order to fit into that time window…” | Same, ll.118–119 | **Authoritative** |
| Live demo | Not mandatory. Examiner checklist asks whether a practical demonstration is present and convincing. | Handbook ~p.10; extract ll.447–464 | **Authoritative** (assessed if present) |
| Slide file submission | — | Searched handbook, templates, supervisor notes | **Not found** |
| Total viva length (incl. Q&A) | — | Same search | **Not found** |

**Source hierarchy:** Handbook PDF > Wave 6A text extract (faithful) > dissertation / supervisor notes (advisory only).

**Conflict note:** “≤20 minutes” and “15–20 minutes” are compatible: plan **15–20**, hard stop **20**, **≤12 slides**.

---

## Planning assumptions (not official)

| Model | Role | Rationale |
| --- | --- | --- |
| **15-minute expanded** | **Preferred working target** | Fits the official 15–20 window; leaves headroom before 20. Labelled **planning assumption**. |
| **10-minute core** | Compressed fallback | Same narrative; removes optional slides listed below. **Not** an official requirement. |
| Examiner Q&A after presentation | Treated as separate only for **planning** | Official handbook says questions afterwards; total Q&A duration is **not** officially specified. Do not assert a Q&A length. |

Continue searching official guidance if module/school updates appear; replace planning targets if they conflict with newer authoritative text.

---

## Central argument

**Claim (must not be softened into an “auto-verified catalogue”):**  
The contribution is not an automatically verified policy catalogue. It is a governed decision-journaling workflow that keeps machine-generated candidates, automated traceability checks, human validation and authoritative source evidence visibly separate.

**Main question:**  
Can an LLM-assisted workflow produce useful, auditable decision-journal candidates from public inquiry transcripts without treating generated text as authoritative evidence?

**Six distinctions (keep on visual vocabulary throughout):**

1. Candidate generation  
2. Mechanical traceability  
3. Evidence strength  
4. Semantic faithfulness  
5. Journal validity  
6. Framework-based interpretation  

---

## Demo integration (decision)

| Option | Assessment |
| --- | --- |
| Embedded short walkthrough | Narrative benefit high for phase1-082; time risk medium; technical risk low (offline localhost). |
| Opened separately after findings | Preferred default for **15-minute** plan: ≤**2 minutes** controlled demo **only if time remains** inside 15–20. |
| Examiner-requested backup only | Preferred if running late or for **10-minute** fallback. |

**Recommendation:** Presentation is **complete without live demo**. Centrepiece teaching uses **static slide of phase1-082**; live Wave 4 demo (`python demo/launch_demo.py`) is an optional controlled walkthrough (≤2 min, case 082 then stop). Fallback: `demo/print.html` or verbal quote from slide evidence. Live demo must never be required for narrative completeness.

---

## Slide inventory (≤12 slides — official max)

| ID | Title (conclusion-style) | Essential (15) | In 10-min? | Est. 15-min | Est. 10-min |
| --- | --- | --- | --- | --- | --- |
| S01 | Generated text is not authoritative evidence | Essential | Yes | 0:45 | 0:30 |
| S02 | Inquiry transcripts hide decisions in long, mixed discourse | Essential | Yes | 1:00 | 0:45 |
| S03 | Aim: traceable candidates under human oversight | Essential | Yes | 1:15 | 0:45 |
| S04 | Generation, checks, human review and source stay separate | Essential | Yes | 1:30 | 1:00 |
| S05 | Evaluation is layered, not a single accuracy number | Essential | Compress verbally into S06 | 1:30 | — (merged) |
| S06 | Traceable candidates are common; journal-ready ones are not | Essential | Yes (merged eval cues) | 2:00 | 1:30 |
| S07 | Quote support ≠ journal membership (phase1-082) | Essential | Yes | 2:00 | 1:30 |
| S08 | Alignment, faithfulness failure and interpretive mapping | Optional-for-10 | No — verbal only | 1:30 | — |
| S09 | Contribution is governance of the AI–source–human route | Essential | Yes | 1:00 | 0:45 |
| S10 | Claims stay bounded to one case, one model, one reviewer | Essential | Merge with S12 | 1:15 | 1:00 (with close) |
| S11 | Next steps are replication and multi-reviewer checks | Optional-for-10 | No | 0:45 | — |
| S12 | Make the route from source to interpretation inspectable | Essential | Yes | 1:00 | 1:00 |
| **Total speaking** | | | | **≈15:30** (trim S05/S11 if late) | **≈10:00** |

**Optional / removed for 10-minute model (exact list):**

1. **S05** as a standalone slide — fold “layered evaluation” into one line on S06.  
2. **S08** supporting cases — keep only verbal mention of 016 / 090 / 246 if asked.  
3. **S11** future work — one clause on S12 if needed.  
4. **Live demo** — omit; use static S07 only.  
5. Skip extended κ / cluster commentary on S06; keep headline cells only.

**Contingency if interrupted / time reduced mid-presentation:** Jump to **S07 → S09 → S12**. Do not open live demo.

**Stopping point:** End of **S12**. Do not invent extra slides beyond 12.

---

## Per-slide storyboard

### S01 — Generated text is not authoritative evidence

| Field | Content |
| --- | --- |
| Purpose | State claim and freeze status before numbers. |
| Main message | This presentation evaluates a **governed workflow**, not a deployed decision engine. |
| Visual | Title + one-line claim; freeze chip: “Frozen research artefact — no live model call”; four chips: Machine / Automated / Human / Source. |
| Max on-slide text | Title; claim (≤35 words); “EEEM004 viva presentation · Module 2 case study”. |
| Evidence source | Handbook presentation requirement; Wave 4 freeze banner convention. |
| Speaker notes | Open with the claim. Do not preview every result. |
| Transition | “Why is that distinction necessary?” → S02 |
| Examiner challenge | “Isn’t this just document processing?” |
| Response anchor | LLM generation is the candidate engine; contribution is separating generation from acceptance (Ch1 / Ch5). |
| Priority | Essential |

### S02 — Inquiry transcripts hide decisions in long, mixed discourse

| Field | Content |
| --- | --- |
| Purpose | Motivate the problem without policy advocacy. |
| Main message | Public inquiry text holds decision evidence that is lengthy, dispersed and easy to mis-extract as if authoritative. |
| Visual | Simple “long transcript → mixed speech acts” sketch (question / procedure / measure / recall). No stock photos. |
| Max on-slide text | Three bullets, ≤12 words each. |
| Evidence | Ch1 §§1.1–1.2; problem statement exact themes. |
| Speaker | “Agreements sit beside questions, procedure and narrative.” |
| Transition | “So what did this project set out to do?” → S03 |
| Challenge | “Why Module 2 / COVID?” |
| Anchor | Public, reproducible case study of a broader journaling problem (Ch1.1) — not the Inquiry as sole purpose. |
| Priority | Essential |

### S03 — Aim: traceable candidates under human oversight

| Field | Content |
| --- | --- |
| Purpose | Reproduce dissertation aim; show objectives without rewriting into RQs that do not exist. |
| Main message | Exact aim: design and evaluate an LLM-assisted method for **traceable candidate** decision-journal entries. |
| Visual | Aim box (exact wording). Sidebar: “No numbered RQs in Ch1 — Aim + Objectives 1–6.” Condensed objective verbs only (develop / evaluate / freeze / validate / organise+interpret / examine limits). |
| Max on-slide text | Full aim sentence; six short objective labels (not full paragraphs). |
| Evidence | `dissertation/CHAPTER_1_INTRODUCTION.md` §1.3 — exact aim. |
| Speaker | Read aim carefully. State main presentation question aloud. |
| Transition | “How is that implemented without treating output as evidence?” → S04 |
| Challenge | “What are your research questions?” |
| Anchor | Aim + six objectives are the formal research framing; no separate numbered RQs. |
| Priority | Essential |

### S04 — Generation, checks, human review and source stay separate

| Field | Content |
| --- | --- |
| Purpose | Show the frozen two-phase workflow; colour-code stages. |
| Main message | Machine candidates, automated traceability, human validity/faithfulness review and source evidence are **visibly separate**. |
| Visual | Horizontal workflow matching Wave 4 demo: Public transcript → chunks → LLM candidate → mechanical traceability → fixed reference dataset → human review → interpretation. Colour: machine / auto / human / source. |
| Max on-slide text | Stage labels only; footnote “Not live / not deployed”. |
| Evidence | Ch3 methods; Wave 4 `demo/index.html` workflow; Ch1.6 methodological contribution. |
| Speaker | Walk stages once left-to-right. Pause on “fixed reference dataset”. |
| Transition | “How was that evaluated?” → S05 |
| Challenge | “Is the pipeline production software?” |
| Anchor | Research prototype / fixed journal; explicitly not production deployment (Ch1.4). |
| Priority | Essential |

### S05 — Evaluation is layered, not a single accuracy number

| Field | Content |
| --- | --- |
| Purpose | Prevent “what’s your accuracy?” traps. |
| Main message | Multiple bounded lenses: manuals, taxonomy, n=50, confidence, clustering, n=60, pilots — none alone equals “system accuracy”. |
| Visual | Compact strip/timeline: 6 manuals · n=42 · n=50 · κ · 20 clusters · n=60 · 50/53 · 49/50. |
| Max on-slide text | Stage names + sample sizes only. |
| Evidence | Ch3–Ch4 structure; examiner evidence map. |
| Speaker | “I will show headline findings next, not every appendix table.” |
| Transition | → S06 |
| Challenge | “Why no overall F1?” |
| Anchor | Task is governance + multiple constructs; single F1 would conflate validity, traceability and faithfulness. |
| Priority | Essential in **15-minute**; **remove as slide** in **10-minute** (one spoken line on S06). |

### S06 — Traceable candidates are common; journal-ready ones are not

| Field | Content |
| --- | --- |
| Purpose | Deliver verified headline numbers without table dump. |
| Main message | Corpus and validation show **pass rates ≠ acceptance**; no×high and moderate κ matter more than raw extraction volume. |
| Visual | Two panels: (A) corpus 414 / 351/414 / triangulation 5 agreement / 10 silence / 0 dissonance / keyword 1/6 vs LLM 5/6; (B) n=50 no×high 21/50; κ rule 0.48 / LLM 0.39; 20 clusters; n=60 JEE 11/60 / DQ 37/60 / combined 26/60; faithfulness 8/25/20/7; report pilot 50/53; structural 49/50. Prefer two big callouts for **351/414** and **21/50**. |
| Max on-slide text | Prefer **≤8 number-units** prominent; list full set only if readable at 1920×1080. Else two slides’ worth of data in one dense board with large callouts for **351/414** and **21/50**. |
| Evidence | See `SLIDE_EVIDENCE_MAP.csv` rows S06a–S06n; journal SHA `814cc7c4…`. |
| Speaker | Speak callouts; do not race every cell. |
| Transition | “The centrepiece finding is simpler…” → S07 |
| Challenge | “Is 351/414 success?” |
| Anchor | Traceability ≠ journal validity; most common n=50 cell is no×high. |
| Priority | Essential |

### S07 — Quote support ≠ journal membership (phase1-082)

| Field | Content |
| --- | --- |
| Purpose | Centrepiece teaching case. |
| Main message | A candidate may be strongly quote-supported and still be the **wrong artefact type** for a policy decision journal (Rubric A = No, Rubric B = High). |
| Visual | Side-by-side: frozen candidate wording vs source quote; chips YES/NO for A/B; “procedural” flag; evidence path `demo/evidence/phase1-082.json`. Optional small screenshot of Wave 4 case panel (still image — Wave 5B). |
| Max on-slide text | Candidate one sentence; quote one sentence; A=No B=High; teaching line. |
| Evidence | Wave 3/4 case; Ch4 no×high theme; evidence hash `9b131dc2…`. |
| Speaker | Pause after teaching line. Offer ≤2 min demo **only if ahead of time**. |
| Transition | “Three other verified cases show complementary lessons…” → S08 (or → S09 if 10-min) |
| Challenge | “So the model failed?” |
| Anchor | Extraction tracked the adjournment language; **human journal criterion** correctly rejected it — that is the method working. |
| Priority | Essential |

### S08 — Alignment, faithfulness failure and interpretive mapping

| Field | Content |
| --- | --- |
| Purpose | Supporting contrast set. |
| Main message | 016: alignment; 090: source available ≠ meaning preserved; 246: frameworks only after validated source — interpretive, not performance praise. |
| Visual | Three mini cards (016 / 090 / 246). Warning box on 246. |
| Max on-slide text | One line per case. |
| Evidence | `demo/evidence/phase1-{016,090,246}.json`; Audit E for framework definitions. |
| Speaker | 20–25s per card. |
| Transition | → S09 |
| Challenge | “Are JEE/DQ objective?” |
| Anchor | Human interpretive aids after validation; not WHO/scoring authority (Ch4). |
| Priority | **Optional for 10-minute** (remove slide). |

### S09 — Contribution is governance of the AI–source–human route

| Field | Content |
| --- | --- |
| Purpose | Separate four contribution types. |
| Main message | Methodological + artefact + empirical + governance — not a new SOTA extraction algorithm. |
| Visual | Four labelled blocks matching Ch1.6 / Ch5 wording. |
| Max on-slide text | Four 8–12 word statements. |
| Evidence | Ch1.6; Ch5 contribution section. |
| Speaker | Stress “governed review process”. |
| Transition | → S10 |
| Challenge | “What’s novel?” |
| Anchor | Explicit separation of constructs + fixed journal freeze + auditable route in this public-record setting. |
| Priority | Essential |

### S10 — Claims stay bounded to one case, one model, one reviewer

| Field | Content |
| --- | --- |
| Purpose | State limitations without apology theatre. |
| Main message | Feasibility evidence, not general policy truth or deployment readiness. |
| Visual | Limit chips: 1 inquiry · 1 main model · single reviewer · frozen historical outputs · live regen ≠ byte-identical · moderate κ · interpretive mappings. |
| Max on-slide text | Chip labels only. |
| Evidence | Ch1.4; Ch5 limitations; Wave 3 reproducibility limits. |
| Speaker | Own each limit in one breath. |
| Transition | → S11 (15-min) or → S12 (10-min merge) |
| Challenge | “Why no second reviewer?” |
| Anchor | MSc scale; dual rating deferred as future work; single-reviewer acknowledged throughout. |
| Priority | Essential |

### S11 — Next steps are replication and multi-reviewer checks

| Field | Content |
| --- | --- |
| Purpose | Realistic future work only. |
| Main message | Extend evaluation governance — not “add chatbot UI and deploy”. |
| Visual | Five short items: multi-reviewer; cross-inquiry; model comparison; domain calibration; controlled access governance. |
| Max on-slide text | Five lines. |
| Evidence | Ch5 future work / scaling conditions. |
| Speaker | Keep under 45s. |
| Transition | → S12 |
| Challenge | “When will it ship?” |
| Anchor | Not a deployment roadmap. |
| Priority | **Optional for 10-minute** (remove). |

### S12 — Make the route from source to interpretation inspectable

| Field | Content |
| --- | --- |
| Purpose | Closing statement; readiness for questions. |
| Main message | Exact close: system does not replace authoritative inquiry evidence or human policy judgement; it makes the route inspectable and auditable. |
| Visual | Closing quote; “Questions”; optional tiny demo URL `127.0.0.1` note (offline). |
| Max on-slide text | Closing paragraph ≤45 words. |
| Evidence | Matches user-specified closing; aligns Ch5 / Wave 4 walkthrough close. |
| Speaker | Deliver close verbatim; stop. |
| Transition | Hand over to examiners. |
| Challenge | — |
| Priority | Essential |

---

## Timing models (planning — within official ≤20 / ≤12)

### Model A — 15-minute preferred (primary)

- **Slides shown:** S01–S12 (12)  
- **Demo:** Optional ≤2:00 after S07 if ≥2:00 buffer remains before minute 15; otherwise skip.  
- **If late at minute 12:** Skip S11, compress S08 to 30s, go S09→S10→S12.  
- **Hard stop:** Minute 20 (official). Aim to finish speaking by ~15–16.

### Model B — 10-minute core fallback

- **Slides shown:** S01, S02, S03, S04, S06 (with one-line eval), S07, S09, S10+S12 merged wording on S12 (8 slides) OR keep S10 and S12 separate (9). Recommended: **8 slides** — S01–S04, S06, S07, S09, S12 (limitations spoken in close).  
- **Removed:** S05, S08, S11, live demo, and optional S10 if limits are verbalised on S12.  
- **Demo:** Not allocated.

---

## Wave 5B production inputs (do not produce PPTX here)

- This storyboard  
- `SLIDE_EVIDENCE_MAP.csv`  
- `PRESENTATION_SPEAKER_NOTES.md`  
- `VISUAL_ASSET_PLAN.md`  
- Offline demo still images (capture later, offline)  
- Existing figures listed in visual plan (if present on disk)
