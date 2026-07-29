# Presentation speaker notes — Wave 5A

Planning target: **15-minute expanded model** (assumption within official 15–20 / ≤12 slides).  
Fallback: **10-minute core** (see cuts at end). Examiner Q&A planning is separate; **do not** assert an official Q&A duration.

Use these as **prompts**, not a memorised essay.

---

## Global rules while speaking

**Must not overstate**

- Do not say the system is deployed, production-ready, or automatically authoritative.  
- Do not call candidates “verified decisions” or “the Inquiry’s findings”.  
- Do not treat JEE/DQ labels as judgements that preparedness performance was good.  
- Do not invent a single overall accuracy / F1.  
- Do not claim multi-reviewer reliability.  
- Do not claim live regeneration matches frozen bytes.

**Phrases to avoid**

- “The AI decided…”  
- “We proved government X failed / succeeded…”  
- “Fully automated journal…”  
- “State of the art extraction…”  
- “The official duration is 15 minutes” (official is **15–20, max 20**; 15 is our **planning** target)

**Safe recovery points**

1. Restate the six distinctions (generation / traceability / evidence strength / faithfulness / journal validity / interpretation).  
2. Return to phase1-082.  
3. Point to frozen journal / examiner evidence map / offline demo.

**Pause points**

- After S01 claim.  
- After S07 teaching line (“quotation support is not journal membership”).  
- After S12 closing sentence — then stop.

---

## S01 — Open (≈0:45)

**Prompts**

- Title. Freeze notice: frozen research artefact — no live model call.  
- Core claim in one breath.  
- Promise: show how candidates can be useful without being treated as evidence.

**Transition:** “Why does that matter for inquiry text?”

**If interrupted:** Skip witty intro; go to problem.

**Non-technical wording:** “We built a checked review process around an AI draft, not an AI that writes the official record.”

**Technical wording:** “Contribution is process governance across generation, automated checks and human constructs.”

---

## S02 — Problem (≈1:00)

**Prompts**

- Decisions scattered in long public records.  
- “Decision” language mixes measures, questions, procedure, advocacy.  
- Naïve LLM summaries can look authoritative.

**Transition:** “So the dissertation aim was…”

**Likely interruption:** “Why COVID Inquiry?”  
**Recovery:** Public reproducible Module 2 case for a broader journaling problem — not the sole purpose.

---

## S03 — Aim (≈1:15)

**Prompts**

- Read **exact** aim from slide (do not paraphrase into a stronger claim).  
- Mention objectives exist as 1–6; do not invent numbered RQs.  
- State main question: useful auditable candidates **without** treating generated text as authoritative evidence.

**Transition:** “The workflow that enforces that separation looks like this.”

**Likely interruption:** “What are your RQs?”  
**Recovery:** Aim + six objectives are the formal framing in Chapter 1.

---

## S04 — Workflow (≈1:30)

**Prompts**

- Walk left → right once.  
- Stress **fixed reference dataset** (414 frozen).  
- Colour story: machine vs automated vs human vs source.

**Transition:** “Evaluation used several bounded lenses…”

**Likely interruption:** “Is this production software?”  
**Recovery:** Research prototype; scope says not evaluated as production.

---

## S05 — Evaluation design (≈1:30) — *drop slide in 10-min*

**Prompts**

- List lenses quickly: 6 manuals → n=42 → n=50 → confidence → clusters → n=60 → pilots.  
- Explicit: no single accuracy number.

**Transition:** “Headline findings next.”

---

## S06 — Findings (≈2:00)

**Prompts**

- Lead with **351/414** and **21/50 no×high**.  
- Then triangulation 5/10/0; keyword 1/6 vs LLM 5/6.  
- κ 0.48 / 0.39 — moderate; cannot replace humans.  
- 20 clusters — navigation only.  
- n=60: JEE 11, DQ 37, combined 26; faithfulness 8/25/20/7.  
- Pilots 50/53 and 49/50 as supplementary.

**If time pressure:** Keep only 414, 351/414, 21/50, κ pair, faithfulness 20/60 materially altered theme.

**Transition:** “One case makes the distinction concrete.”

---

## S07 — Centrepiece 082 (≈2:00)

**Prompts**

- Read candidate: hearing will resume…  
- Read quote: hearing adjourned…  
- Traceability pass + High evidence; Rubric A = No; procedural.  
- Teaching line: quotation support ≠ journal membership.  
- Pause.

**Optional ≤2:00 demo:** Launch offline demo → case 082 only → stop. If lag or doubt: **do not** open demo.

**Transition (15-min):** “Three supporting cases…”  
**Transition (10-min):** “What does this contribute?”

---

## S08 — Supporting cases (≈1:30) — *drop in 10-min*

**Prompts**

- 016: Yes×High alignment.  
- 090: counsel question vs asserted decision — faithfulness.  
- 246: P3 + commitment_to_follow_through with interpretive warning.

**Transition:** “Pulling the contribution together…”

---

## S09 — Contribution (≈1:00)

**Prompts**

- Method: governed review process.  
- Artefact: fixed journal + offline examiner demo.  
- Empirical: bounded n=414 / 50 / 60 evidence.  
- Governance: keep layers inspectable.

**Transition:** “Boundaries of the claim…”

---

## S10 — Limitations (≈1:15)

**Prompts**

- One inquiry; one main model; single reviewer.  
- Frozen historical outputs; regen not byte-identical.  
- Moderate agreement; interpretive mappings.

**Transition:** “Realistic extensions…” or jump to close.

---

## S11 — Future (≈0:45) — *drop in 10-min*

**Prompts**

- Multi-reviewer; cross-inquiry; model comparison; calibration; access governance.  
- Not “ship a product”.

**Transition:** Close.

---

## S12 — Close (≈1:00)

**Deliver nearly verbatim:**

> The system does not replace authoritative inquiry evidence or human policy judgement. It makes the route from source evidence to machine-generated candidate and human interpretation inspectable and auditable.

Then: “I’m ready for questions.” Stop.

---

## 10-minute fallback timing

| Slide | Time |
| --- | --- |
| S01 | 0:30 |
| S02 | 0:45 |
| S03 | 0:45 |
| S04 | 1:00 |
| S06 | 1:30 (include one line: “layered eval, no single F1”) |
| S07 | 1:30 |
| S09 | 0:45 |
| S12 (+ limits spoken) | 1:15 |
| **Total** | **≈10:00** |

**Removed:** S05, S08, S11, live demo; S10 as standalone (limits on S12).

---

## If examiners seize the laptop

- Prefer verbal S07.  
- Or `demo/print.html`.  
- Or examiner package demos JSON under Wave 3/4 paths.
