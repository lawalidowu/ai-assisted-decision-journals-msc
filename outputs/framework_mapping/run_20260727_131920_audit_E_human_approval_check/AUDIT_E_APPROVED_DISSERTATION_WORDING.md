# Audit E — Approved Dissertation Wording (Draft for Human Review)

Generated (UTC): 2026-07-27T13:19:20.288213+00:00

**Status:** PROPOSED — not adopted until explicit human approval. Audit E outputs are **not frozen**.

---

## Original problematic wording (Audit E)

> "88.3% (53/60) of generated decisions diverge from source quotes"

**Why it must change:** The figure was produced by a crude string rule (`decision != source_quote` with no substring containment). It conflates faithful paraphrases with materially unsupported alterations. It must not be used in the dissertation.

---

## Proposed traceability limitation wording

> In this purposive 60-record pilot, generated decision fields were algorithmically produced screening candidates and were not treated as evidential sources. Seven entries (11.7%, 7/60) failed automated traceability checks (`traceability_ok=False`), indicating that the generated decision text could not be verified against the source quote. Among traceable entries, human adjudication rationales identified 20 records (37.7% of 53 traceable, 33.3% of 60 total) in which the generated decision introduced materially unsupported or altered content relative to the source passage; the remaining traceable entries were substantively faithful paraphrases or near-verbatim extractions. All framework interpretation in this study used source quotes and evidence fields, not generated decision wording.

---

## Proposed review and adjudication methodology wording

> Decision-journal entries underwent single-reviewer human adjudication of JEE preparedness and Decision Quality mappings (July 2026), supported by AI-assisted screening. A source-integrity audit (Audit C) reviewed traceability and corrected rationales where generated candidates introduced unsupported content. A coding-consistency audit (Audit D) screened all 60 records for label–rationale consistency; six flagged records received interactive human confirmation of AI-proposed corrections, while 52 flagged records retained prior adjudication via AI-assisted keep_all recommendations without interactive re-review. Two records passed consistency screening without flags. This workflow demonstrates feasibility and auditability; it does not constitute independent dual-coder validation or a gold-standard reference set.

---

## Proposed 60-record pilot description

> A purposive pilot sample of 60 Phase 1 decision-journal entries was selected for human adjudication and multi-layer audit. Findings are descriptive and bounded to this sample; they are not representative of the full 414-entry corpus and support no inferential or causal generalisation.

---

## Proposed status of 52 retained records

> Fifty-two records flagged in Audit D retained their pre-audit human adjudication labels through AI-assisted keep_all import. These records had already received manual human adjudication before Audit D; they did **not** receive new interactive human confirmation during the consistency audit. The status label `consistency_human_reviewed_keep` reflects import of an approved AI-assisted batch decision, not per-record interactive human re-adjudication.

**Recommended label clarification (documentation only, not to alter frozen Audit D):** consider describing these as "AI-assisted consistency keep (prior human adjudication retained)" in dissertation text.

---

## Proposed description of six human-confirmed corrections

> Six Audit D flagged records (phase1-003, phase1-161, phase1-182, phase1-246, phase1-311, phase1-382) were interactively reviewed and human-confirmed against AI-proposed corrections (19 substantive field changes). These edits refined edge cases—unsupported secondary JEE mappings, label–rationale mismatches, and one JEE demotion—without materially altering aggregate mapped/unmapped proportions.

---

## Proposed description of two auto-clear records

> Two records (phase1-298, phase1-307) raised no consistency flags in Audit D and required no consistency re-review. Both had completed prior human adjudication.

---

## Proposed description of seven non-traceable records

> Seven entries (11.7%, 7/60: phase1-007, phase1-117, phase1-161, phase1-274, phase1-314, phase1-382, phase1-396) had `traceability_ok=False`. Framework coding for these entries relied on source quotes and human rationales explicitly noting traceability failure; generated decision fields were not used as evidence.

---

## Assessment of candidate description

> "A single-reviewer, human-adjudicated pilot supported by AI-assisted source-integrity and coding-consistency audits, with targeted human confirmation of proposed corrections."

**Verdict:** **Defensible with the clarifications above.** The phrase is accurate if "human-adjudicated" refers to the original adjudication pass (all 60 records) and "targeted human confirmation" is scoped to six Audit D corrections (plus Audit C source-integrity approvals), not all 52 retained records.

---

## JEE / DQ frequency wording examples

> Among the 11 JEE-mapped records, R4 occurred in 3 (27.3%, 3/11), while P3, D2 and R5 each occurred in 2 (18.2%, 2/11).

> Among the 37 DQ-mapped records, commitment_to_follow_through was the primary element in 22 (59.5%, 22/37), helpful_frame in 8 (21.6%, 8/37), and clear_values in 6 (16.2%, 6/37). Secondary DQ elements (n=37 mapped records with any secondary): useful_information 3, clear_values 2, sound_reasoning 1, commitment_to_follow_through 1.
