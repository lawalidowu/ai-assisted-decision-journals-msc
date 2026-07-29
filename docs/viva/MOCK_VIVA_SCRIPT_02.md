# Mock viva script 02 — sceptical / adversarial examiner

**Training only.** Not an official viva script.  
Approximately **30** questions. Interruptions and evidence requests are intentional.

**Focus:** one model, one reviewer, moderate κ, subjective mapping, reproducibility, deployment risk.

---

### Q01
- **Examiner:** Stop. In fifteen seconds — what did you actually contribute?
- **Expected:** Governed separation of generation, automated checks, human validation, source evidence.
- **Follow-up if:** Long essay.
- **Evidence:** Ch1.6
- **Scoring:** Directness; length.

### Q02 *(interrupt)*
- **Examiner:** That’s just using ChatGPT on transcripts.
- **Expected:** Deny novelty-as-LLM-use; point to No×High / wrong-artefact governance finding.
- **Follow-up if:** Agrees novelty is only LLM use.
- **Evidence:** Ch4 §4.5; phase1-082
- **Scoring:** Contribution under pressure.

### Q03
- **Examiner:** Show me the evidence for 21/50 — open the file.
- **Expected:** Open stratified sample / evidence map; state stratified not population.
- **Follow-up if:** Recites from memory only.
- **Evidence:** `configs/evaluation/confidence_validation_sample.json`; evidence index
- **Scoring:** Evidence use.

### Q04
- **Examiner:** So 42% of all decisions are invalid?
- **Expected:** Explicitly reject universal rate; 21/50 is stratified sample cell.
- **Follow-up if:** Accepts 42%.
- **Evidence:** Ch4 §4.5 caveat
- **Scoring:** Statistics / overclaiming.

### Q05
- **Examiner:** Your κ is 0.39. That’s poor. Thesis fails.
- **Expected:** Moderate κ reported deliberately; supports automation ≠ human; not “strong.”
- **Follow-up if:** Calls κ excellent or hides it.
- **Evidence:** Table 4.3
- **Scoring:** Limitation + composure.

### Q06
- **Examiner:** Exact agreement looks better than kappa — which is real?
- **Expected:** Both reported; κ adjusts for chance/ordinal; prevalence can affect κ; do not invent CIs.
- **Follow-up if:** Invents significance.
- **Evidence:** Table 4.3; statistical anchors
- **Scoring:** Statistics defence.

### Q07
- **Examiner:** One reviewer designed the rubrics and applied them — circular.
- **Expected:** Acknowledge independence limit; rubrics explicit/auditable; not equivalent to second independent human; future multi-rater.
- **Follow-up if:** Claims supervisor IRR.
- **Evidence:** Ch5; limitations defence
- **Scoring:** Single-reviewer defence (critical).

### Q08
- **Examiner:** Confidence comparison is your second rater.
- **Expected:** No — automated vs Rubric B; not independent human IRR.
- **Follow-up if:** Equates confidence to human2.
- **Evidence:** Table 4.3 methods
- **Scoring:** Technical accuracy.

### Q09
- **Examiner:** Why no second model? Without it you can’t generalise.
- **Expected:** Agree model generalisation limited; claim is workflow case study.
- **Follow-up if:** Claims other models would match.
- **Evidence:** Ch1.4; Ch5
- **Scoring:** One-model defence.

### Q10
- **Examiner:** If I re-run the API tonight, do I get the same 414?
- **Expected:** Not expected byte-identical; freeze is historical; evaluate frozen artefact.
- **Follow-up if:** Promises identical regen.
- **Evidence:** Reproducibility limits; journal SHA
- **Scoring:** Reproducibility honesty.

### Q11
- **Examiner:** Then how is this science?
- **Expected:** Frozen artefact evaluation of workflow + failure modes; hashes; examiner lineage — not live leaderboard.
- **Follow-up if:** Bluffs “API is deterministic.”
- **Evidence:** Examiner package; journal hash
- **Scoring:** Clarity under attack.

### Q12
- **Examiner:** Git was introduced late — why trust anything?
- **Expected:** Acknowledge process debt; baseline freeze + hashes + evidence package mitigate.
- **Follow-up if:** Says git timing irrelevant.
- **Evidence:** Baseline tag / Wave reports
- **Scoring:** Limitation awareness.

### Q13
- **Examiner:** Untracked historical run folders — prove they matter.
- **Expected:** Prefer frozen journal hashes; runs are provenance aids not override.
- **Follow-up if:** Elevates runs over journal.
- **Evidence:** Wave 3 limits notes
- **Scoring:** Technical defence.

### Q14
- **Examiner:** Audit E paths were ambiguous — how resolved?
- **Expected:** Canonical locator; one authoritative path per claim.
- **Follow-up if:** “Any alias is fine.”
- **Evidence:** `AUDIT_E_CANONICAL_LOCATOR.md`
- **Scoring:** Evidence use.

### Q15
- **Examiner:** Framework mapping is subjective storytelling.
- **Expected:** Interpretive by design; after source validation; not preparedness performance; phase1-246 warning.
- **Follow-up if:** Claims objective WHO scores.
- **Evidence:** Demo 246; Ch4 Table 4.4
- **Scoring:** Framework defence.

### Q16
- **Examiner:** Why is JEE coverage lower than Decision Quality?
- **Expected:** Different construct granularity; interpretive mapping; purposive n=60 — not model quality score.
- **Follow-up if:** “JEE failed.”
- **Evidence:** Audit E summaries 11 vs 37
- **Scoring:** Interpretation care.

### Q17
- **Examiner:** Combined 26/60 — cherry-picked?
- **Expected:** Most frequent combined cell reported; purposive sample; limitations stated.
- **Follow-up if:** Hides purposive design.
- **Evidence:** Crosstab unmapped×mapped=26
- **Scoring:** Honesty.

### Q18
- **Examiner:** Traceability 351/414 — so mostly fine?
- **Expected:** Mechanical pass ≠ validity; No×High shows insufficiency.
- **Follow-up if:** Equates to success rate.
- **Evidence:** 082; Ch4 §4.5
- **Scoring:** Construct separation.

### Q19
- **Examiner:** Isn’t High support enough to accept a candidate?
- **Expected:** No — governance control: human journal-validity gate.
- **Follow-up if:** Softens to auto-accept High.
- **Evidence:** 082; governance defence
- **Scoring:** Governance.

### Q20
- **Examiner:** phase1-082 — model failed, correct?
- **Expected:** Wording may be well-supported while artefact wrong; governance working by rejecting membership.
- **Follow-up if:** “Total model failure” or “no problem.”
- **Evidence:** Demo 082
- **Scoring:** Nuance.

### Q21
- **Examiner:** Better prompting would eliminate No × High.
- **Expected:** May reduce; not proven; mixed discourse structural risk remains.
- **Follow-up if:** Guarantees elimination.
- **Evidence:** Ch5
- **Scoring:** Future vs claim.

### Q22
- **Examiner:** Did it hallucinate? Give me a rate.
- **Expected:** Refuse single rate; give 8/25/20/7 for n=60; distinguish categories; 090 example.
- **Follow-up if:** Invents corpus hallucination %.
- **Evidence:** Table 4.5; demo 090
- **Scoring:** Faithfulness defence.

### Q23
- **Examiner:** Traceability_ok detects hallucination.
- **Expected:** Explicit no; quote can exist while meaning altered.
- **Follow-up if:** Agrees.
- **Evidence:** 090; methods
- **Scoring:** Technical accuracy.

### Q24
- **Examiner:** Report pilot 50/53 and structural 49/50 prove correctness.
- **Expected:** Supplementary lenses only; not semantic validity.
- **Follow-up if:** Treats as accuracy.
- **Evidence:** Ch4 §4.8
- **Scoring:** Overclaiming.

### Q25
- **Examiner:** Could this mislead officials tomorrow?
- **Expected:** Yes if accepted without oversight; hence prototype not deployment.
- **Follow-up if:** “No risk.”
- **Evidence:** Governance/ethics defence
- **Scoring:** Ethics.

### Q26
- **Examiner:** So when do you deploy?
- **Expected:** Not now; list multi-rater, access control, logging, change governance, domain calibration.
- **Follow-up if:** Timeline bluff.
- **Evidence:** Ch5
- **Scoring:** Deployment honesty.

### Q27
- **Examiner:** Secrets in the repo?
- **Expected:** No committed keys; raw bulk not committed; public sources cited; demo localhost.
- **Follow-up if:** Unsure — open security notes.
- **Evidence:** Security notes; `.gitignore`
- **Scoring:** Recovery.

### Q28 *(interrupt)*
- **Examiner:** Your demo just failed. Now what?
- **Expected:** Argument complete on slides; `print.html` / JSON evidence; do not bluff live API.
- **Follow-up if:** Panics or invents.
- **Evidence:** `VIVA_FAILURE_AND_RECOVERY.md`
- **Scoring:** Composure; recovery.

### Q29
- **Examiner:** Someone told you the Q&A portion has a fixed official length of forty minutes — treat that as University rule?
- **Expected:** Do **not** invent or endorse an official Q&A duration; handbook specifies presentation envelope only (15–20 / ≤20 / ≤12 slides).
- **Follow-up if:** Accepts invented duration as official.
- **Evidence:** Project handbook presentation rules; defence map
- **Scoring:** Overclaiming / process honesty.

### Q30
- **Examiner:** Last chance — what must never be claimed?
- **Expected:** Not verified catalogue; not deployed; not second independent reviewer; not multi-model general; not byte-identical regen; no invented CIs; no fabricated examiner feedback.
- **Follow-up if:** Misses centrepiece lesson.
- **Evidence:** Rapid review; defence map
- **Scoring:** Aggregate readiness.

---

## Debrief (adversarial)

- [ ] Held No×High under pressure  
- [ ] Refused invented statistics  
- [ ] Single-reviewer candid  
- [ ] Demo failure recovered  
- [ ] No fabricated official viva length  
