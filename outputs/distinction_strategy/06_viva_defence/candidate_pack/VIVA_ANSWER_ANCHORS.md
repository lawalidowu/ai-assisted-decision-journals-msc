# Viva answer anchors

Short prompts for high-frequency and adversarial challenges.
Hierarchy: data → inference → uncertainty → future work.

## Q001 — What problem did the dissertation address?
- **Direct:** Convert complex public inquiry text into auditable candidate decision-journal entries without treating LLM output as authoritative.
- **Evidence:** Ch1 §§1.1–1.2
- **Caveat:** Case-study scope only
- **Avoid:** We solved pandemic decision-making

## Q002 — What was the exact research aim?
- **Direct:** Read exact Ch1 aim: design and evaluate an LLM-assisted method for traceable candidate decision-journal entries using Module 2 as case study.
- **Evidence:** Ch1 §1.3
- **Caveat:** Do not rewrite aim
- **Avoid:** Aim was to verify government decisions

## Q003 — What were the research questions?
- **Direct:** No numbered RQs in Ch1; Aim + Objectives 1–6 are the formal framing.
- **Evidence:** Ch1 §1.3
- **Caveat:** Do not invent RQ1–RQn
- **Avoid:** We had four RQs

## Q004 — Why are public inquiry transcripts suitable?
- **Direct:** Public, citable, decision-rich discourse with mixed speech acts; reproducible corpus.
- **Evidence:** Ch1.1
- **Caveat:** One module/eight hearings
- **Avoid:** Works for all inquiries

## Q005 — Why is this an AI project rather than document processing?
- **Direct:** LLM generates structured candidates; contribution is governing those candidates.
- **Evidence:** Ch3; Ch1.6
- **Caveat:** Not a new base model
- **Avoid:** Pure NLP parsing without LLM

## Q006 — What is the central contribution?
- **Direct:** Governed workflow separating machine candidates, automated checks, human validation and source evidence.
- **Evidence:** Ch1.6; Ch5
- **Caveat:** Not an auto-verified catalogue
- **Avoid:** Production policy engine

## Q007 — What is genuinely novel?
- **Direct:** Operational separation of constructs plus frozen examiner-auditable artefacts on this case — not SOTA extraction.
- **Evidence:** Ch1.6
- **Caveat:** Builds on known LLM risks
- **Avoid:** First ever LLM on transcripts

## Q008 — Why useful for policymaking?
- **Direct:** Supports institutional memory / retrospective review with inspectable route — not automated policy.
- **Evidence:** Ch1.6
- **Caveat:** Prototype only
- **Avoid:** Ready for operational use

## Q009 — What does the system not claim to do?
- **Direct:** Not deployed; not authoritative decisions; not byte-identical regen; not multi-model generalisation.
- **Evidence:** Ch1.4; reproducibility limits
- **Caveat:** Keep list tight
- **Avoid:** It verifies truth

## Q011 — Why seven-sentence chunks with overlap two?
- **Direct:** Balance context and localisation for quote anchoring.
- **Evidence:** Ch3
- **Caveat:** Boundary effects
- **Avoid:** Universal optimum

## Q013 — Why the temperature/prompt configuration?
- **Direct:** Favour reproducibility; Phase 1 notes emphasise low temperature.
- **Evidence:** Ch3; structural reliability production_note
- **Caveat:** Model-specific
- **Avoid:** Config is optimal forever

## Q015 — How was deduplication handled?
- **Direct:** Non-destructive review flags rather than silent deletion.
- **Evidence:** Ch3/Ch4 flags
- **Caveat:** Heuristic flags
- **Avoid:** All duplicates removed automatically

## Q017 — Why freeze model output before evaluation?
- **Direct:** Separate generation from evaluation; prevent moving targets; lock SHA.
- **Evidence:** journal SHA 814cc7c4…
- **Caveat:** Historical snapshot
- **Avoid:** Live API is identical

## Q019 — Why six manual decision excerpts?
- **Direct:** Bounded gold for triangulation and keyword baseline.
- **Evidence:** App A; Table 4.2
- **Caveat:** Not full-corpus labels
- **Avoid:** Representative of 414

## Q020 — Why n=42, n=50 and n=60?
- **Direct:** Different evaluation questions: taxonomy, stratified A/B, purposive frameworks/faithfulness.
- **Evidence:** Ch3–Ch4
- **Caveat:** Bounded feasibility
- **Avoid:** One accuracy sample

## Q022 — Why examine confidence separately?
- **Direct:** High automated confidence ≠ journal membership; compare to Rubric B.
- **Evidence:** Table 4.3
- **Caveat:** Moderate κ
- **Avoid:** Confidence replaces humans

## Q024 — Why JEE and Decision Quality?
- **Direct:** Recognised interpretive frameworks after validated source.
- **Evidence:** Ch4 Table 4.4
- **Caveat:** Subjective mapping
- **Avoid:** Official WHO scores

## Q026 — Why one main model?
- **Direct:** Bounded feasibility case; contribution is workflow governance not horse-race.
- **Evidence:** Ch1.4; Ch5
- **Caveat:** Model-conditioned
- **Avoid:** Model-independent

## Q027 — Would another model reproduce the same journal?
- **Direct:** Unknown; not tested; no byte-identical claim even for same model live regen.
- **Evidence:** reproducibility limits
- **Caveat:** Future multi-model study
- **Avoid:** Yes, identical

## Q028 — Does one model weaken generalisability?
- **Direct:** Yes for model generalisation; claim is workflow feasibility in one case.
- **Evidence:** Ch5
- **Caveat:** Acknowledge
- **Avoid:** Still general

## Q030 — What would proper model comparison require?
- **Direct:** Same corpus, frozen configs, paired human labels, pre-registered metrics — future work.
- **Evidence:** Ch5
- **Caveat:** Not done here
- **Avoid:** We already compared models

## Q031 — Temperature zero removes all error.
- **Direct:** Reduces randomness not semantic/wrong-artefact errors.
- **Evidence:** methods
- **Caveat:** Still errors
- **Avoid:** Zero error

## Q032 — Why were there 414 candidates?
- **Direct:** Extractor over eight Module 2 hearings; frozen totals.decisions=414.
- **Evidence:** journal totals.decisions
- **Caveat:** Candidates ≠ accepted decisions
- **Avoid:** 414 verified decisions

## Q033 — What does 351/414 traceability mean?
- **Direct:** Mechanical traceability pass count.
- **Evidence:** totals.traceability_pass=351
- **Caveat:** Not journal validity
- **Avoid:** 85% accuracy

## Q034 — What does 351/414 not mean?
- **Direct:** Not acceptance; not faithfulness; not Rubric A yes.
- **Evidence:** Ch4; No×High
- **Caveat:** Keep sharp
- **Avoid:** Success rate

## Q035 — What do 5 agreement, 10 silence and 0 dissonance indicate?
- **Direct:** Triangulation tags on six manuals: some matches, many silences, no direct conflicts tagged.
- **Evidence:** Table 4.2
- **Caveat:** Bounded excerpts
- **Avoid:** Corpus-wide

## Q036 — Why keyword recall 1/6 while LLM agreement rows 5/6?
- **Direct:** Keyword baseline weak on manuals; LLM agreement-row recall higher on those six — not full IR over 414.
- **Evidence:** App B; BASELINE_KEYWORD
- **Caveat:** Agreement-row metric
- **Avoid:** LLM always better everywhere

## Q037 — Why were 21/50 items No × High?
- **Direct:** Most frequent A×B cell: strong quote support but not journal-valid.
- **Evidence:** Fig 4.9; sample
- **Caveat:** Stratified sample
- **Avoid:** Universal 42%

## Q038 — Why is phase1-082 important?
- **Direct:** Centrepiece: procedural adjournment — High support, No validity.
- **Evidence:** demo phase1-082
- **Caveat:** One case
- **Avoid:** Proves all High are wrong

## Q039 — Why was rule weighted kappa 0.48?
- **Direct:** Linear weighted κ vs Rubric B; neither replaces human.
- **Evidence:** confidence_comparison_results metrics
- **Caveat:** Moderate
- **Avoid:** Strong agreement

## Q040 — Why was LLM weighted kappa 0.39?
- **Direct:** Same comparison for LLM confidence vs Rubric B.
- **Evidence:** metrics.llm_vs_human_b
- **Caveat:** Moderate
- **Avoid:** Strong agreement

## Q041 — Are those agreement values acceptable?
- **Direct:** Acceptable as evidence automation is insufficient — not as strong reliability.
- **Evidence:** Table 4.3
- **Caveat:** Do not call strong
- **Avoid:** Excellent reliability

## Q042 — What do the 20 clusters show?
- **Direct:** Exploratory grouping for navigation.
- **Evidence:** clustering_report n_clusters=20
- **Caveat:** Not validity
- **Avoid:** Policy importance ranking

## Q043 — What do JEE 11/60 and Decision Quality 37/60 mean?
- **Direct:** Mapped counts in purposive n=60; interpretive.
- **Evidence:** Audit E summaries
- **Caveat:** Not performance scores
- **Avoid:** UK preparedness grades

## Q044 — Why was the combined count 26/60?
- **Direct:** Most frequent combined cell: DQ mapped with JEE unmapped.
- **Evidence:** crosstab unmapped×mapped=26
- **Caveat:** Purposive
- **Avoid:** Always true

## Q045 — How should faithfulness 8/25/20/7 be interpreted?
- **Direct:** Exact/near 8; paraphrase 25; materially unsupported/altered 20; non-traceable 7.
- **Evidence:** AUDIT_E_MANIFEST counts
- **Caveat:** Single reviewer
- **Avoid:** Hallucination rate for all 414

## Q046 — What do report pilot 50/53 and structural reliability 49/50 establish?
- **Direct:** Supplementary report-pilot and structural checklist outcomes.
- **Evidence:** REPORT_PILOT; structural summary
- **Caveat:** Not semantic validity
- **Avoid:** Full correctness

## Q047 — Isn’t a highly supported quotation automatically a valid decision?
- **Direct:** No — Rubric B≠A; phase1-082.
- **Evidence:** Ch4 §4.5; demo 082
- **Caveat:** Rubrics author-defined
- **Avoid:** Yes always

## Q048 — Why did the model extract the wrong artefact?
- **Direct:** Hearing discourse contains decision-like procedural language; model tracked wording.
- **Evidence:** phase1-082
- **Caveat:** Prompting limits
- **Avoid:** Model always fails

## Q049 — Does this mean the model failed?
- **Direct:** Shows generation can succeed at wording while governance must reject membership — method working.
- **Evidence:** 082 teaching
- **Caveat:** Not all cases
- **Avoid:** Total failure

## Q050 — Is the rubric subjective?
- **Direct:** Operationalised by author; single-reviewer limit acknowledged.
- **Evidence:** Ch4/Ch5
- **Caveat:** Need multi-rater
- **Avoid:** Objective law

## Q051 — Could better prompting eliminate No × High?
- **Direct:** May reduce but not guaranteed; wrong-artefact risk is structural in mixed discourse.
- **Evidence:** Ch5
- **Caveat:** Unproven
- **Avoid:** Prompting solves all

## Q052 — Why retain these candidates rather than delete them?
- **Direct:** Audit trail; teach governance; non-destructive flags.
- **Evidence:** methods flags
- **Caveat:** Storage cost
- **Avoid:** Delete all No

## Q053 — What governance control follows from this result?
- **Direct:** Human journal-validity gate cannot be replaced by quote strength alone.
- **Evidence:** Ch5 governance
- **Caveat:** Prototype
- **Avoid:** Auto-accept High

## Q054 — Did the system hallucinate?
- **Direct:** Use faithfulness categories; do not collapse all failures into hallucination. 20/60 materially unsupported/altered in n=60.
- **Evidence:** Table 4.5
- **Caveat:** Not corpus rate
- **Avoid:** Never hallucinated

## Q055 — How often did it hallucinate?
- **Direct:** Do not give a single hallucination rate; report 8/25/20/7 categories for n=60.
- **Evidence:** AUDIT_E_MANIFEST
- **Caveat:** Single reviewer
- **Avoid:** X% hallucination

## Q056 — Is traceability_ok a hallucination detector?
- **Direct:** No — mechanical presence ≠ meaning.
- **Evidence:** Ch4.5 vs 4.2
- **Caveat:** Need faithfulness review
- **Avoid:** Yes it is

## Q057 — Can a quote be found while meaning is still altered?
- **Direct:** Yes — phase1-090 counsel question vs asserted decision.
- **Evidence:** demo 090
- **Caveat:** Purposive example
- **Avoid:** Impossible

## Q058 — Why was a separate faithfulness review necessary?
- **Direct:** Traceability insufficient for summary meaning.
- **Evidence:** Ch4 Table 4.5
- **Caveat:** Single reviewer
- **Avoid:** Redundant with traceability

## Q059 — How could faithfulness evaluation be improved?
- **Direct:** Multi-rater labels; clearer taxonomy; larger samples — future work.
- **Evidence:** Ch5
- **Caveat:** Not done
- **Avoid:** Already solved

## Q061 — Could generated candidates mislead officials?
- **Direct:** Yes if accepted without human review — hence separation.
- **Evidence:** governance defence
- **Caveat:** Need controls
- **Avoid:** Safe to publish raw

## Q063 — Could the system be deployed now?
- **Direct:** No — research prototype.
- **Evidence:** Ch1.4
- **Caveat:** List deployment gates
- **Avoid:** Yes tomorrow

## Q064 — What additional validation would deployment require?
- **Direct:** Multi-reviewer, access control, logging, change governance, domain calibration.
- **Evidence:** Ch5
- **Caveat:** Not implemented
- **Avoid:** UI only

## Q067 — Which components require an OpenAI API key?
- **Direct:** Live regeneration paths — not offline demo/frozen checks.
- **Evidence:** repro limits
- **Caveat:** Cost/privacy
- **Avoid:** No API ever used

## Q068 — Why should the examiner trust untracked historical run artefacts?
- **Direct:** Prefer frozen journal hashes; runs are historical provenance only.
- **Evidence:** Wave3 limits
- **Caveat:** Gap acknowledged
- **Avoid:** Runs override journal

## Q070 — How was Audit E authoritative-path ambiguity resolved?
- **Direct:** Canonical locator — one path per claim.
- **Evidence:** AUDIT_E_CANONICAL_LOCATOR.md
- **Caveat:** Aliases exist
- **Avoid:** Any file is fine

## Q072 — What does the baseline tag protect?
- **Direct:** Corrected Wave 6C dissertation freeze for distinction waves.
- **Evidence:** baseline-wave6c-corrected-2026-07-28
- **Caveat:** Historical process
- **Avoid:** All history immutable forever

## Q073 — Is the novelty merely using an LLM on transcripts?
- **Direct:** No — governed separation and No×High empirical lesson.
- **Evidence:** Ch1.6
- **Caveat:** Not SOTA model
- **Avoid:** Yes only LLM use

## Q074 — How does this differ from summarisation / RAG / IE?
- **Direct:** Structured candidates + validity/faithfulness/framework layers + freeze.
- **Evidence:** contribution doc
- **Caveat:** Overlaps exist
- **Avoid:** Completely unique field

## Q076 — What would be publishable from this work?
- **Direct:** Governed extraction evaluation + wrong-artefact finding + faithfulness taxonomy case study.
- **Evidence:** Ch5
- **Caveat:** Needs peer review
- **Avoid:** Ready Nature paper

## Q078 — Does moderate kappa kill the thesis?
- **Direct:** No — it supports the claim that automation cannot replace humans.
- **Evidence:** Table 4.3
- **Caveat:** Still limited
- **Avoid:** κ proves success

## Q079 — Why no multi-model comparison?
- **Direct:** Scope; future work; one-model bound stated.
- **Evidence:** Ch5
- **Caveat:** Weakens model generalisation
- **Avoid:** Unnecessary

## Q081 — Isn’t this ready if the demo works?
- **Direct:** Demo is frozen inspection aid; not production authority.
- **Evidence:** demo freeze banner
- **Caveat:** Need deployment study
- **Avoid:** Demo=deployed

## Q082 — Who should approve journal entries?
- **Direct:** Human role with clear criteria; not the model.
- **Evidence:** governance defence
- **Caveat:** Org-specific
- **Avoid:** Auto-approve High

## Q085 — Why is the live demo optional?
- **Direct:** Handbook assesses demo if present; presentation complete without it.
- **Evidence:** handbook checklist; DEMO_CUE_CARD
- **Caveat:** ≤2 min if used
- **Avoid:** Demo mandatory

## Q086 — If time is short what do you cut?
- **Direct:** S05/S08/S11 and demo; never omit 082 centrepiece and contribution/close.
- **Evidence:** storyboard 10-min model
- **Caveat:** Planning cuts
- **Avoid:** Cut the centrepiece

## Q089 — Why do exact agreement and kappa differ?
- **Direct:** Agreement is raw match rate; κ adjusts for chance / ordinal structure.
- **Evidence:** Table 4.3
- **Caveat:** Prevalence effects possible
- **Avoid:** They must match

## Q090 — Why not report p-values or confidence intervals?
- **Direct:** Not computed/reported in study — will not invent.
- **Evidence:** results chapters
- **Caveat:** Descriptive framing
- **Avoid:** Secret significant results

## Q091 — Why is 21/50 important without being a universal rate?
- **Direct:** Modal cell in stratified sample teaching construct separation.
- **Evidence:** Fig 4.9
- **Caveat:** Not population rate
- **Avoid:** 42% of all decisions

## Q092 — Class imbalance makes kappa meaningless.
- **Direct:** Prevalence can affect κ; still reported with exact agreement; interpretation cautious.
- **Evidence:** Table 4.3
- **Caveat:** No CI
- **Avoid:** Meaningless so ignore

## Q094 — How do review flags help quality?
- **Direct:** Non-destructive navigation of procedural/duplicate risks.
- **Evidence:** Ch4 flags
- **Caveat:** Heuristic
- **Avoid:** Perfect filter

## Q095 — Haven’t you just built a summariser with extra labels?
- **Direct:** No — journal validity gate and No×High finding are central.
- **Evidence:** Ch4; contribution
- **Caveat:** Overlaps with IE
- **Avoid:** Just summariser

## Q096 — Your human labels are circular because you designed the rubrics.
- **Direct:** Rubrics are explicit and auditable; independence limit acknowledged; future multi-rater.
- **Evidence:** Ch5
- **Caveat:** Single author
- **Avoid:** Fully independent

## Q097 — Without IRR how can examiners trust n=50?
- **Direct:** As structured case-study evaluation with frozen IDs — not as population estimate.
- **Evidence:** Ch4 caveat
- **Caveat:** Need IRR later
- **Avoid:** Equivalent to multi-rater

## Q098 — Framework mapping is story-telling.
- **Direct:** Interpretive by design; after source validation; not performance proof — phase1-246 warning.
- **Evidence:** Ch4; demo 246
- **Caveat:** Subjective
- **Avoid:** Objective scoring

## Q099 — If regen changes outputs, what is science here?
- **Direct:** Frozen artefact evaluation of a workflow and failure modes; not live leaderboard.
- **Evidence:** journal freeze
- **Caveat:** Model drift risk
- **Avoid:** Regen identical

## Q100 — Why should policymakers care about phase1-082?
- **Direct:** Shows automation can look right and still be wrong artefact — oversight design implication.
- **Evidence:** demo 082
- **Caveat:** One case
- **Avoid:** All policy decisions

## Q101 — You hid weak kappa behind narrative.
- **Direct:** κ reported plainly; used to argue against replacement of humans.
- **Evidence:** Table 4.3
- **Caveat:** Still moderate
- **Avoid:** Strong κ

## Q102 — Git late means results untrustworthy.
- **Direct:** Baseline freeze + hashes + examiner package mitigate; process debt acknowledged.
- **Evidence:** baseline tag
- **Caveat:** Historical gap
- **Avoid:** Git timing irrelevant

