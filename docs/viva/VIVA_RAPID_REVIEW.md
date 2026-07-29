# Viva rapid-review sheet (~10 minutes)

**Training only.** Open this the day of presentation/viva. Do not invent official Q&A duration.

## Aim (memorise)

Design and evaluate an LLM-assisted method for creating **traceable candidate** decision-journal entries from complex public records, using UK COVID-19 Inquiry **Module 2** as a case study (Ch1 §1.3).

**RQs:** none numbered — Aim + Objectives 1–6.

## Contribution (one sentence)

A **governed decision-journaling workflow** that visibly separates machine-generated candidates, automated traceability checks, human validation and authoritative source evidence — **not** an automatically verified policy catalogue.

## Pipeline (six distinctions)

Generation → mechanical traceability → evidence strength (B) → faithfulness → journal validity (A) → framework interpretation.

## Key numbers (lock)

| Claim | Meaning | Not |
| --- | --- | --- |
| 414 | Frozen candidates | Accepted decisions |
| 351/414 | Mechanical traceability | Validity / faithfulness |
| 5 / 10 / 0 | Agreement / silence / dissonance on six manuals | Corpus-wide |
| 1/6 vs 5/6 | Keyword vs LLM agreement-row on manuals | Full IR over 414 |
| 21/50 | No×High in stratified sample | Universal rate |
| κ 0.48 / 0.39 | Rule / LLM vs Rubric B | Strong reliability |
| 20 clusters | Navigation | Importance ranking |
| 11/60 · 37/60 · 26/60 | JEE / DQ / combined cell | Preparedness grades |
| 8/25/20/7 | Faithfulness categories n=60 | Single hallucination % |
| 50/53 · 49/50 | Report pilot / structural | Semantic correctness |

## Four demo cases

| ID | Teach |
| --- | --- |
| 016 | Yes × High alignment |
| **082** | **No × High centrepiece** |
| 090 | Materially unsupported / altered meaning |
| 246 | JEE/DQ interpretive (not performance) |

## Main limitations

One inquiry · one model · single reviewer · moderate κ · purposive/stratified samples · interpretive frameworks · frozen historical outputs · no deployment evaluation · limited external validity.

## Most likely 15 questions + one-liners

1. **Problem?** Auditable candidates from inquiry text without treating LLM as authority.  
2. **Aim?** Exact Ch1 sentence — candidate entries, Module 2.  
3. **RQs?** Aim + Objectives; no numbered RQs.  
4. **Contribution?** Governed separation of layers.  
5. **Why AI?** LLM generates; governance is the point.  
6. **351/414?** Mechanical only.  
7. **21/50?** Quote support ≠ journal membership.  
8. **082?** Procedural adjournment — High support, No validity.  
9. **κ?** Moderate — automation insufficient.  
10. **Hallucinate?** Use categories; not one rate; 090 example.  
11. **One reviewer?** Feasibility; limits IRR; case-study evaluation.  
12. **One model?** Workflow case study; not model-independent.  
13. **Deploy?** No — prototype.  
14. **Reproduce?** Frozen hashes + offline demo; not byte-identical live gen.  
15. **Novel?** Separation + No×High finding — not “first LLM.”

## Files to open

- `docs/examiner_evidence/EXAMINER_EVIDENCE_MAP.md`  
- `docs/examiner_evidence/AUDIT_E_CANONICAL_LOCATOR.md`  
- `data/manifests/phase1_decision_journal.json` (totals)  
- `demo/evidence/phase1-082.json` (+ 090 if faithfulness)  
- `docs/viva/VIVA_QUESTION_BANK.md` / evidence index  
- Primary deck under `outputs/distinction_strategy/05_presentation_deck/`

## Demo launch / fallback

```text
python demo/launch_demo.py
```

Fallback: `demo/print.html` · `demo/evidence/*.json` · slide S07 alone.

## Emergency recovery

- “I will not invent the number — opening the frozen evidence.”  
- “Clarify: traceability or journal validity?”  
- “Correction: data show X; they do not show Y.”  
- “Not deployed; not a verified catalogue.”

## Presentation timing (handbook)

15–20 min, ≤20 hard, ≤12 slides; demo optional ≤2 min.  
**Never omit:** contribution, 082, non-claims, limitations.
