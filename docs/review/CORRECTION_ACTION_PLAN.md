# Correction Action Plan

**Dissertation:** AI-assisted decision journals from UK COVID-19 Inquiry transcripts  
**Companion:** `EXAMINER_ATTACK_LIST.md` · Source: `Supervisor_Correction_Report.pdf`  
**Rule:** Framing and precision only. No new data, no re-extraction, no methodology rebuild.  
**Frozen numbers (do not change):** 414 · 351 · 84.8% · 21/50 no×high · 11/50 yes×high · 36 flagged · 20 clusters

---

## Goal

Avoid a sustainability-project outcome (strong pipeline, mark dragged by **one misnamed or overclaimed pillar**). Finish with hedged, sample-scoped claims that match what the evidence supports.

---

## Recommended sequence (5 days)

| Day | Focus | Corrections | Done when |
|-----|--------|-------------|-----------|
| **1** | Language pass + sample scope | #1, #2 | Abstract + Ch 4 §4.9 / §4.11 + Ch 5 §5.1 no longer generalise 42% or use *demonstrates/proves/establishes/confirms* as claims about your own results |
| **2** | Annotator + citations | #3, #4, #6 | §5.3.2 expanded; Brown softened; GRACE preprint caveat in §2.4 and §4.6 |
| **3** | Methods precision | #5 + SHOULD #9, #10 | RAG sentence replaced; temperature explained; keyword baseline framed as lower bound |
| **4** | Novelty + remaining SHOULD | #7, #8 | Contributions / Power citation adjusted |
| **5** | IF TIME + audit | #11–#13 + full pass | Citation audit, cross-refs, proofread only — **no substantive rewrites in last 24h** |

---

## Day 1 — MUST FIX #1 and #2

### Find-and-replace (claims about *your* results only)

Do **not** change innocent uses (e.g. "Public inquiries exist to establish what happened", "I confirm" in the declaration).

| Avoid (as claim about your findings) | Prefer |
|--------------------------------------|--------|
| demonstrates | suggests / indicates |
| establishes | provides evidence that |
| confirms | is consistent with |
| proves | provides pilot-scale evidence that |
| the primary contribution is | one contribution of this dissertation is |
| the dominant outcome | the dominant outcome observed in the validation sample |

**Files to open:** `ABSTRACT.md`, `CHAPTER_1_INTRODUCTION.md`, `CHAPTER_4_RESULTS.md`, `CHAPTER_5_DISCUSSION.md` (also skim Ch 2/3 for claim verbs).

### Sample qualifier (insert after every 21/50 or 42% discussion)

- Abstract: after "21 of 50 items (42%)" → add *"within the stratified validation sample (n=50)"* (or equivalent).
- §4.9 opening → *"Within the stratified validation sample (n=50), the dominant outcome was…"*
- §4.11 → *"indicated, within the validation sample, that faithful extraction of the wrong artefact type was the most common pattern observed."*
- §5.1.3 → same sample tie-in before interpreting the pattern.

**Checklist Day 1**

- [ ] Abstract ¶3–4 revised
- [ ] Ch 4 opening, §4.9, §4.11 revised
- [ ] Ch 5 §5.1.3–5.1.4 revised (including "publishable finding" → softer wording)
- [ ] Grep for: `demonstrat`, `establish`, `confirm`, `prove`, `dominant outcome`, `42%`, `21/50`

---

## Day 2 — MUST FIX #3, #4, #6

### #3 — Expand §5.3.2 (after existing sole-annotator paragraph)

Add 3–4 sentences covering:

1. κ compares automation to a **single, non-adjudicated** gold standard — not multi-rater consensus.
2. Figures are consistency metrics, not validated inter-rater accuracy.
3. n=50 with 3×3 table → sparse cells; CIs would be wide and are not reported.
4. no×high (21/50) = **indicative pilot finding**, not stable corpus error distribution.
5. Second coder on 15–20 overlapping items = most urgent follow-up.

**File:** `CHAPTER_5_DISCUSSION.md` §5.3.2

### #4 — Soften Brown et al. (2020)

- **Ch 1 §1.1:** Replace "verbatim quotes in a single pass (Brown et al., 2020)" with the supervisor's longer hedge (few-shot ICL plausible; verbatim retention needs schema + traceability beyond prompting alone).
- **Ch 2 §2.6:** "demonstrates that LLMs can extract…" → "suggests that LLMs are capable of… though reliability for accountability-oriented tasks remains contingent on explicit provenance requirements"

**Files:** `CHAPTER_1_INTRODUCTION.md`, `CHAPTER_2_LITERATURE.md`

### #6 — GRACE preprint caveat

- **§2.4:** After introducing GRACE dimensions, add: unpublished preprint; used as supplementary quality lens, not validated benchmark.
- **§4.6:** End of opening paragraph: GRACE scores reported as **descriptive**, not normative.

**Files:** `CHAPTER_2_LITERATURE.md`, `CHAPTER_4_RESULTS.md`

**Checklist Day 2**

- [ ] §5.3.2 expanded
- [ ] Brown sentences in §1.1 and §2.6 updated
- [ ] GRACE caveats in §2.4 and §4.6

---

## Day 3 — MUST FIX #5 + SHOULD #9, #10

### #5 — Replace RAG sentence in §3.3

Delete the "fits within context window" justification. Replace with supervisor text: extraction on sequential fixed chunks (not retrieval across heterogeneous corpus); full chunk in context simplifies provenance; RAG = future work (Lewis et al., 2020).

**File:** `CHAPTER_3_METHODS.md`

### #9 — Temperature clarification after existing temp=0.3 sentence in §4.8.1

Add: Phase 1 used temp=0 (near-100% schema expected); 0.3 is a **conservative stress-test**; 98% = schema robustness under variation, **not** a direct characterisation of Phase 1 corpus consistency.

Also mirror briefly in §5.3.4 if needed.

**File:** `CHAPTER_4_RESULTS.md` (and optionally `CHAPTER_5_DISCUSSION.md`)

### #10 — Keyword baseline framing

- **§4.7.2:** Before aggregate table — keyword baseline is intentionally simplistic; lower-bound only; not competitive IE; recall gap ≠ validated LLM superiority.
- **§5.1.2:** Soften parenthetical to "keyword lower-bound check… confirming surface lexical triggers are insufficient…"

**Files:** `CHAPTER_4_RESULTS.md`, `CHAPTER_5_DISCUSSION.md` (and Ch 1 §1.4 if it still reads as superiority)

**Checklist Day 3**

- [ ] §3.3 RAG paragraph replaced
- [ ] §4.8.1 temperature stress-test sentence added
- [ ] §4.7.2 + §5.1.2 keyword framing fixed

---

## Day 4 — SHOULD FIX #7, #8

### #7 — Novelty language

- §5.2.1: "primary contribution is" → "central methodological contribution… adaptation and combination of existing evaluation methods into a layered validation framework"
- §5.2.4: "publishable methodological finding" → "may motivate future investigation… reported explicitly… transparency norms for pilot studies"
- §1.6: "four primary contributions" → "four contributions at MSc pilot scale"; soften "introduces"

**Files:** `CHAPTER_5_DISCUSSION.md`, `CHAPTER_1_INTRODUCTION.md`

### #8 — Power (2002)

Prefer Option B: cite `(Power, 2002; Bovens, 2007)` in §2.1 (and align Ch 1 §1.1 if same claim). Soften "long been recognised as good practice" → "has been advocated as useful practice" if keeping Power alone.

**File:** `CHAPTER_2_LITERATURE.md` (and `CHAPTER_1_INTRODUCTION.md` if needed)

**Checklist Day 4**

- [ ] §1.6, §5.2.1, §5.2.4 novelty wording
- [ ] Power/Bovens citation adjusted

---

## Day 5 — IF TIME + final audit

### IF TIME (do if schedule allows)

| # | Action | File |
|---|--------|------|
| 11 | Clarify BERT-era vs extended-context LLMs after context-window claim | `CHAPTER_2_LITERATURE.md` §2.2 |
| 12 | Prefer Jurafsky & Martin 2009 2nd edn, **or** flag 2023 as online draft | `REFERENCES.md` + in-text |
| 13 | Reframe genre-blindness as working hypothesis (14/50 unclassified) | `CHAPTER_5_DISCUSSION.md` §5.2.4 |

### Final audit (always do)

- [ ] Grep attack-list phrases again (`EXAMINER_ATTACK_LIST.md`)
- [ ] Every in-text citation in `REFERENCES.md`; no orphans
- [ ] Frozen numbers unchanged
- [ ] Rebuild Word: `python scripts/build_submission_docx.py`
- [ ] Figures 3.1, 4.9, 4.10a, 4.10b present and introduced
- [ ] One proofread pass only — **no new arguments in last 24 hours**

---

## Mapping: sustainability 62% → this plan

| What hurt EEEM073 | Equivalent here | Plan item |
|-------------------|-----------------|-----------|
| Called retraining "compression" | "Demonstrates / proves / publishable finding" | Day 1 #1 |
| n=20 validation under-discussed | 42% / dominant outcome without sample scope | Day 1 #2 |
| Inconsistent methods across models | κ without single-annotator implications | Day 2 #3 |
| Two different MLPs | temp=0 vs temp=0.3 unexplained | Day 3 #9 |
| Limitations not prominent enough | Expand §5.3.2; hedge Abstract/Conclusion | Days 1–2 |

---

## What not to do

- Do not re-run extraction or change 414 / 21/50 / κ values
- Do not add new experiments to "fix" the mark
- Do not rewrite Chapter 3 methodology structure
- Do not expand scope (second coder, full corpus) in the submitted text beyond future work
- Do not edit `VIVA_NOTES.md` / checklists instead of chapter sources — chapters are source of truth

---

## Progress tracker

| Correction | Priority | Status |
|------------|----------|--------|
| #1 Overclaiming language | MUST | [ ] |
| #2 n=50 generalisation | MUST | [ ] |
| #3 Single-annotator expansion | MUST | [ ] |
| #4 Brown et al. | MUST | [ ] |
| #5 RAG justification | MUST | [ ] |
| #6 GRACE preprint | MUST | [ ] |
| #7 Novelty claims | SHOULD | [ ] |
| #8 Power citation | SHOULD | [ ] |
| #9 Temperature | SHOULD | [ ] |
| #10 Keyword baseline | SHOULD | [ ] |
| #11 Transformer framing | IF TIME | [ ] |
| #12 Jurafsky citation | IF TIME | [ ] |
| #13 Genre-blindness hypothesis | IF TIME | [ ] |

When a row is done, tick it here and cross-check the matching rows in `EXAMINER_ATTACK_LIST.md`.
