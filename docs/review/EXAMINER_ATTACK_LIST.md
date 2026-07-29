# Examiner Attack List

**Dissertation:** AI-assisted decision journals from UK COVID-19 Inquiry transcripts  
**Purpose:** Exact sentences an examiner is most likely to underline — priority order.  
**Companion:** `CORRECTION_ACTION_PLAN.md`  
**Basis:** Supervisor Correction Report (08 Jul 2026) + patterns from EEEM073 (62%) feedback.

---

## Priority 1 — Critical (same failure mode as the 62%)

These are category / generalisation errors. An examiner can mark you down without disputing your research design.

| # | Exact sentence / phrase | Location | Why they underline it |
|---|---|---|---|
| 1 | *"Human validation on a stratified sample (n = 50) revealed that **the dominant outcome** was not hallucination… 21 of 50 items (**42%**) fell in the no × high cell"* | Abstract ¶3 | Stratified sample ≠ corpus estimate. 42% cannot be read as prevalence across 414 entries. |
| 2 | *"**The dominant outcome** was not hallucination or weak quote support."* | Ch 4 §4.9 | Same claim without "within the validation sample (n=50)". |
| 3 | *"The central empirical result is the no × high pattern (21/50)"* — stated as if it characterises the journal | Ch 4 §4.11 | Headline result generalised beyond sample construction. |
| 4 | *"…while 21/50 (42%) fell in no × high, the largest cell. That pattern indicates…"* | Ch 5 §5.1.3 | Discussion restates sample finding as Phase 2 finding without sample qualifier. |
| 5 | *"**The primary contribution** is a validation and review framework **demonstrating** that candidate generation and candidate evaluation must remain separate"* | Abstract ¶4 | Pilot + n=50 cannot "demonstrate" a methodological necessity at population level. |
| 6 | *"Taken together, **the dissertation demonstrates** that inquiry-mode LLM extraction can produce…"* | Ch 5 §5.1.4 | Overclaim verb on pilot-scale evidence. |
| 7 | *"A negative or weak link between automated confidence and domain validity is itself a **publishable methodological finding**"* | Ch 5 §5.1.3 | Same trap as calling retraining "compression": claim name exceeds what was shown. |

---

## Priority 2 — High (defensibility under viva / close reading)

| # | Exact sentence / phrase | Location | Why they underline it |
|---|---|---|---|
| 8 | *"κ values compare automated signals to that single gold standard…"* (one sentence only) | Ch 5 §5.3.2 | Limitation acknowledged too briefly. Examiner asks: so κ is not inter-rater reliability — why lead with it in Abstract/Results? |
| 9 | *"Automated confidence correlated moderately with evidence strength (linear weighted κ ≈ 0.39–0.48)"* | Abstract ¶3 | No caveat that gold standard = sole annotator; sparse 3×3 cells → wide CIs not reported. |
| 10 | *"prompt-based extraction can identify decision-like statements and attach **verbatim quotes in a single pass** (Brown et al., 2020)"* | Ch 1 §1.1 | Brown (2020) = few-shot ICL, not verbatim legal/inquiry extraction. |
| 11 | *"Existing research **demonstrates** that LLMs can extract structured information from complex documents (Brown et al., 2020)"* | Ch 2 §2.6 | Same over-citation. |
| 12 | *"Retrieval-augmented generation was unnecessary at this scale because each chunk **fits within the model context window**…"* | Ch 3 §3.3 | Wrong reason. RAG is about retrieval across a corpus, not chunk-vs-window fit. |
| 13 | *"Bondaronek et al. (2026) introduce GRACE…"* (no preprint caveat) | Ch 2 §2.4; Ch 4 §4.6 | Named evaluation framework used as if peer-reviewed standard. |

---

## Priority 3 — Medium (keeps merit at 6/7 instead of 7/7)

| # | Exact sentence / phrase | Location | Why they underline it |
|---|---|---|---|
| 14 | *"**The dissertation makes four primary contributions**… Third, it **introduces** a governed enrichment process…"* | Ch 1 §1.6 | Novelty language; combination of existing methods, not invention. |
| 15 | *"**The primary contribution** is a layered validation framework…"* | Ch 5 §5.2.1 | Soften to adaptation/combination at MSc pilot scale. |
| 16 | *"keyword baseline (**17% recall vs 83%** for LLM agreement rows)…"* | Ch 1 §1.4; Ch 4 §4.7.2; Ch 5 §5.1.2 | Reads as LLM superiority; baseline is a lower-bound check only. |
| 17 | *"this supplementary test used temperature = 0.3…"* (without linking to Phase 1 temp=0) | Ch 4 §4.8.1 | Examiner: why does 98% at 0.3 characterise a temp=0 pipeline? |
| 18 | *"That finding has **direct implications** for anyone using LLM extraction… domain and discourse awareness… may be as important as quote-level fidelity"* | Ch 5 §5.2.4 | Genre-blindness rests on exploratory pilot (14/50 unclassified). Hypothesis, not confirmed mechanism. |
| 19 | *"has long been recognised as good practice… (Power, 2002)"* | Ch 1 §1.1; Ch 2 §2.1 | Citation stretched; Power is DSS textbook, not governance primary. |

---

## Priority 4 — If time (polish; less likely to move the mark alone)

| # | Exact sentence / phrase | Location | Why they underline it |
|---|---|---|---|
| 20 | *"inquiry transcripts exceed typical model context windows (Bommasani et al., 2021; Beltagy et al., 2020)"* | Ch 2 §2.2 | BERT-era framing; 2026 LLMs relax length; bottleneck is discourse/schema. |
| 21 | *"Jurafsky and Martin (2023)… 3rd edn draft"* | References | Unfinished draft; prefer 2nd edn or flag as draft. |

---

## Examiner one-liners to rehearse

If challenged in viva or written feedback, these are the safe replies:

1. **42% / dominant outcome:** "That figure is from a stratified validation sample of 50, deliberately enriched with flagged and traceability-fail entries. It characterises the sample pattern, not corpus prevalence across 414."
2. **κ:** "Those kappas compare automated signals to a single annotator gold standard, not multi-rater consensus. They are consistency metrics, not inter-rater reliability."
3. **Demonstrates / proves:** "At pilot scale the evidence *suggests* / *is consistent with* separation of generation and evaluation; we do not claim population-level proof."
4. **Keyword 17 vs 83:** "The keyword matcher is a lower-bound lexical check, not a competitive IE baseline."
5. **Compression parallel (from EEEM073):** "We do not claim a method we did not implement. Where a label is used (GRACE, compression-analogue claims, 'dominant'), the scope is stated."

---

## What is *not* under attack

Do not waste revision time defending these — they are already strong:

- Two-phase design (extract → freeze → validate)
- Traceability ≠ journal validity
- Dual rubrics (A vs B)
- Frozen canonical journal / no row deletion
- Explicit "candidates pending review, not verified catalogue"
- Limitations chapter existence (§5.3)

The mark risk is **claim precision**, not research quality.
