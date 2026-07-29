# Mock viva script 01 — balanced examiner

**Training only.** Not an official viva script or timed official duration.  
Approximately **30** questions. Partner scores with `MOCK_VIVA_SCORING_RUBRIC.md`.

**Mode:** Supportive but exacting; moves overview → methods → results → limitations → contribution.  
Follow-ups trigger when answers omit evidence, confuse constructs, or overclaim.

---

### Q01
- **Examiner:** What problem did you set out to address?
- **Expected:** Decision-rich inquiry text → auditable candidates without treating LLM as authority; speech-act / wrong-artefact risk.
- **Follow-up if:** Only “AI for COVID” without governance.
- **Evidence:** Ch1 §§1.1–1.2; `VIVA_DEFENCE_MAP.md`
- **Scoring:** Directness + contribution fidelity.

### Q02
- **Examiner:** Read your exact research aim.
- **Expected:** Quote Ch1 §1.3 aim (LLM-assisted traceable candidate decision-journal entries; Module 2 case study).
- **Follow-up if:** Paraphrases into “verify decisions.”
- **Evidence:** Ch1 §1.3
- **Scoring:** Technical accuracy.

### Q03
- **Examiner:** What were your research questions?
- **Expected:** No numbered RQs; Aim + Objectives 1–6.
- **Follow-up if:** Invents RQ1–RQ4.
- **Evidence:** Ch1 §1.3
- **Scoring:** Avoidance of overclaiming.

### Q04
- **Examiner:** Why public inquiry transcripts?
- **Expected:** Public, citable, decision-rich, mixed speech acts; reproducible corpus bound.
- **Follow-up if:** Claims generalisability to all government records.
- **Evidence:** Ch1.1
- **Scoring:** Limitation awareness.

### Q05
- **Examiner:** Why is this an AI project rather than document processing?
- **Expected:** LLM generates structured candidates; contribution is governing those candidates.
- **Follow-up if:** Claims new base model.
- **Evidence:** Ch3; Ch1.6
- **Scoring:** Methodological understanding.

### Q06
- **Examiner:** In one sentence, what is the contribution?
- **Expected:** Governed workflow separating machine candidates, automated checks, human validation, source evidence — not verified catalogue.
- **Follow-up if:** Softens into “automated policy catalogue.”
- **Evidence:** Ch1.6; Ch5
- **Scoring:** Overclaiming.

### Q07
- **Examiner:** Walk me through the pipeline briefly.
- **Expected:** Clean/chunk → generate → freeze → traceability → human A/B → faithfulness/frameworks → clusters/supplementary.
- **Follow-up if:** Skips freeze or human gate.
- **Evidence:** Presentation S04; Ch3
- **Scoring:** Clarity; length ≤90s.

### Q08
- **Examiner:** Why seven-sentence chunks with overlap two?
- **Expected:** Context vs localisation; alternative paragraph chunks; boundary limitation.
- **Follow-up if:** Claims universal optimum.
- **Evidence:** Ch3; `VIVA_METHODS_DEFENCE.md`
- **Scoring:** Methods defence structure.

### Q09
- **Examiner:** How is `traceability_ok` calculated, and what is it not?
- **Expected:** Mechanical link to source; not validity, not faithfulness. 351/414.
- **Follow-up if:** Calls it hallucination detector.
- **Evidence:** Journal `totals.traceability_pass=351`
- **Scoring:** Technical accuracy.

### Q10
- **Examiner:** Why freeze outputs before evaluation?
- **Expected:** Separate generation from evaluation; lock SHA; no live moving target.
- **Follow-up if:** Claims live regen is byte-identical.
- **Evidence:** Journal hash `814cc7c4…`
- **Scoring:** Reproducibility honesty.

### Q11
- **Examiner:** Why different sample sizes — 42, 50, 60?
- **Expected:** Different evaluation questions (taxonomy / stratified A-B / purposive frameworks+faithfulness).
- **Follow-up if:** Merges into one accuracy N.
- **Evidence:** Ch3–Ch4; methods defence
- **Scoring:** Methodological understanding.

### Q12
- **Examiner:** Why stratified validation for n=50?
- **Expected:** Cover strata; surface No×High; not probability sample of 414.
- **Follow-up if:** States 21/50 as population rate.
- **Evidence:** Ch4 §4.5
- **Scoring:** Statistics + limitation.

### Q13
- **Examiner:** Why 414 candidates?
- **Expected:** Frozen extractor total over eight Module 2 hearings; candidates ≠ accepted decisions.
- **Follow-up if:** “414 verified decisions.”
- **Evidence:** `totals.decisions=414`
- **Scoring:** Overclaiming.

### Q14
- **Examiner:** Interpret 351/414.
- **Expected:** Mechanical pass count; not acceptance/faithfulness/Rubric A.
- **Follow-up if:** “85% accuracy.”
- **Evidence:** Journal totals
- **Scoring:** Construct separation.

### Q15
- **Examiner:** What do 5 agreement, 10 silence, 0 dissonance mean?
- **Expected:** Triangulation tags on six manuals; bounded; not corpus-wide conflict rate.
- **Follow-up if:** Extrapolates to all 414.
- **Evidence:** Table 4.2
- **Scoring:** Evidence use.

### Q16
- **Examiner:** Keyword 1/6 vs LLM agreement-row 5/6 — explain carefully.
- **Expected:** Different metrics; keyword baseline vs agreement rows on six manuals; not full IR over 414.
- **Follow-up if:** “LLM always better everywhere.”
- **Evidence:** App B; `docs/BASELINE_KEYWORD.md`
- **Scoring:** Technical accuracy.

### Q17
- **Examiner:** Why are 21 of 50 No × High?
- **Expected:** Modal stratified cell; strong quote support without journal membership.
- **Follow-up if:** Universal 42%.
- **Evidence:** Fig 4.9; sample JSON
- **Scoring:** Limitation + interpretation.

### Q18
- **Examiner:** Tell me about phase1-082.
- **Expected:** Procedural adjournment; A=No B=High; teaching centrepiece.
- **Follow-up if:** Cannot open evidence path.
- **Evidence:** `demo/evidence/phase1-082.json` hash `9b131dc2…`
- **Scoring:** Evidence use; composure.

### Q19
- **Examiner:** Isn’t a highly supported quotation automatically a valid decision?
- **Expected:** No — Rubric B ≠ A; 082.
- **Follow-up if:** Agrees with examiner.
- **Evidence:** Ch4 §4.5
- **Scoring:** Contribution fidelity.

### Q20
- **Examiner:** Explain weighted kappa 0.48 and 0.39.
- **Expected:** Rule/LLM confidence vs Rubric B; moderate; supports automation insufficient.
- **Follow-up if:** Calls κ “strong.”
- **Evidence:** Table 4.3; comparison results JSON
- **Scoring:** Statistics defence.

### Q21
- **Examiner:** What do 20 clusters show?
- **Expected:** Navigational organisation; size ≠ importance.
- **Follow-up if:** Clusters = validity.
- **Evidence:** Clustering report `n_clusters=20`
- **Scoring:** Clarity.

### Q22
- **Examiner:** JEE 11/60, DQ 37/60, combined 26/60?
- **Expected:** Interpretive mapped counts; 26 = frequent unmapped×mapped cell; not preparedness grades.
- **Follow-up if:** WHO/official scores claim.
- **Evidence:** Audit E summaries; locator
- **Scoring:** Framework honesty.

### Q23
- **Examiner:** Faithfulness 8/25/20/7?
- **Expected:** Exact/near, paraphrase, materially unsupported/altered, non-traceable; single-reviewer n=60.
- **Follow-up if:** Single “hallucination rate.”
- **Evidence:** Audit E manifest; Table 4.5
- **Scoring:** Faithfulness taxonomy.

### Q24
- **Examiner:** Did the system hallucinate?
- **Expected:** Use categories; do not collapse all failures; distinguish wrong-artefact vs unsupported addition vs silence.
- **Follow-up if:** “Never” or “always.”
- **Evidence:** phase1-090; Table 4.5
- **Scoring:** Avoidance of overclaiming.

### Q25
- **Examiner:** Why single reviewer?
- **Expected:** Feasibility; limits IRR; confidence ≠ second human; structured case-study evaluation; future dual coding.
- **Follow-up if:** Claims supervisor was second rater.
- **Evidence:** Ch5; limitations defence
- **Scoring:** Limitation awareness (critical).

### Q26
- **Examiner:** Why one model?
- **Expected:** Bounded case; workflow claim not horse-race; no multi-model generality.
- **Follow-up if:** Claims other models identical.
- **Evidence:** Ch1.4; Ch5
- **Scoring:** Overclaiming.

### Q27
- **Examiner:** Can this be deployed now?
- **Expected:** No — research prototype / audit workflow.
- **Follow-up if:** “Almost ready.”
- **Evidence:** Ch1.4; governance defence
- **Scoring:** Governance.

### Q28
- **Examiner:** What is genuinely novel?
- **Expected:** Operational separation + No×High empirical lesson + frozen examiner artefacts — not “first LLM on transcripts.”
- **Follow-up if:** Novelty = using GPT.
- **Evidence:** Ch1.6; contribution doc
- **Scoring:** Contribution.

### Q29
- **Examiner:** What does the work not prove?
- **Expected:** Population performance; model independence; deployment readiness; byte-identical regen; framework preparedness quality.
- **Follow-up if:** Empty list.
- **Evidence:** Ch1.4; Ch5
- **Scoring:** Limitation.

### Q30
- **Examiner:** If you had six more months, what next?
- **Expected:** Independent reviewers; multi-model; cross-inquiry; deployment evaluation — proportionate.
- **Follow-up if:** Retroactive fake second reviewer.
- **Evidence:** Ch5
- **Scoring:** Recovery; future work honesty.

---

## Debrief checklist

- [ ] No invented CIs/p-values  
- [ ] No “verified decisions” language  
- [ ] 082 centrepiece solid  
- [ ] Single-reviewer candid  
- [ ] Answers ≤2 minutes on methods  
