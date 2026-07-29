# Chapter 4: Results and evaluation

**Status:** Wave 3B restructured results chapter. Empirical outcomes only; discussion is reserved for Chapter 5.

---

## 4.1 Overview of key results

This chapter reports the evaluation outcomes for the Module 2 pilot. The findings are organised by sample: the fixed reference dataset of candidate decision-journal entries (n = 414), the stratified dual-rubric validation (n = 50), and the supplementary preparedness and Decision Quality pilot (n = 60). Figure 3.1 summarises the corresponding workflow.

The eight-transcript extraction produced 414 candidate entries, of which 351/414 (84.8%) passed mechanical source-quote traceability. In the stratified n = 50 validation sample, the most frequent Rubric A × Rubric B cell was no × high, 21/50 (42%): the quoted passage strongly supported the generated statement, but the item did not meet the operational journal definition. Automated confidence aligned more closely with evidence strength than with journal validity.

Exploratory clustering organised the 414 candidates into 20 groups for navigation, not verification. In the purposive n = 60 pilot, an observable Decision Quality element was found more often than a defensible Joint External Evaluation (JEE) mapping: 37/60 versus 11/60. The most frequent combined outcome in that pilot was observable Decision Quality without a defensible JEE mapping, 26/60 (43.3%). Candidate-decision wording was not always reliable enough to serve as evidence: 8/60 were exact or near-verbatim, 25/60 substantively faithful paraphrases, 20/60 materially unsupported or altered, and 7/60 non-traceable. All sample-specific findings apply only to the stated denominator.

---

## 4.2 Extraction and source traceability (n = 414)

Automated evaluation began with the inquiry-mode extractor on all eight Phase 1 Module 2 hearing transcripts. Table 4.1 summarises the corpus totals that define the fixed reference dataset.

| Metric | Value |
|--------|-------|
| Transcripts processed | 8 |
| Candidate entries | 414 |
| Traceability pass | 351/414 (84.8%) |
| Traceability fail | 63/414 (15.2%) |

Per-hearing traceability ranged from 78% (23 May 2024) to 91% (28 November 2023). Variation was mainly associated with processed-text and layout artefacts rather than absent quote fields. The full per-hearing table is reported in Appendix B.

On the two hearing days that received both default and inquiry-mode runs (30 November and 1 December 2023), inquiry mode extracted fewer candidates than the default prompt (50 versus 333; 32 versus 162). That comparison is limited to those two hearings and does not establish general model superiority. The full prompt-comparison table is in Appendix B.

Traceability failures were predominantly `source_quote_not_found_in_text`: the model returned a quote field that alphanumeric normalisation could not locate in the processed source text. These failures reflect PDF layout, line-break and normalisation effects. A smaller number involved bad source-location pointers. Mechanical pass/fail remains necessary but not sufficient for extraction quality.

---

## 4.3 Manual evaluation and extraction failure modes

Manual evaluation used the operational journal definition on six annotated excerpts from three hearing days. Triangulation followed the agreement / silence / dissonance categories in Table 4.2.

| Category | Meaning | Count |
|----------|---------|-------|
| Agreement | Same formal decision; meaning aligns | 5 |
| Silence | Present in one method only | 10 |
| Dissonance | Genuine disagreement on decision existence or content | 0 |

The comparison comprised 15 rows and six manual decisions, with no dissonance. The ten silence rows were LLM-only extractions without a corresponding manual decision. Recurring false-positive types included narrative description, future recommendations and ministerial advocacy. Detailed excerpt text, identifiers, source spans and linked extraction IDs are in Appendix A.

Where LLM items were reviewed for quote support independent of journal validity, grounding was scored yes for 5 items, partial for 2 and no for 8. The eight unsupported scores align with silence-row false positives: a quote may be present without supporting a formal decision claim.

To extend beyond six excerpts, a stratified sample of 42 items was examined: 9 author-validated false positives from triangulation silence rows and 33 heuristic-classified items from the wider inquiry corpus. Figure 4.3 shows the assigned categories. The distribution should not be treated as full human validation of all 42 items, nor as representative of all 414 candidates. Among the author-validated false positives, advocacy, future recommendation and narrative were recurring types. The heterogeneous “other” category collected cases that did not recur frequently enough to justify separate named labels. Detailed definitions and counts are in Appendix B.

A simple keyword baseline on the same six excerpts recovered 1/6 of the manual decisions, compared with 5/6 agreement-row recall for inquiry-mode extraction. The baseline was intentionally simple and applies only to those excerpts. Per-excerpt keyword results are in Appendix B.

[[FIGURE:4.3]]

---

## 4.4 Fixed reference dataset and non-destructive review flags

The eight Phase 1 extraction runs were merged into the fixed reference dataset used for all later review and analysis. Stable identifiers range from phase1-001 to phase1-414. Corpus totals are those already reported in Section 4.2; they are not repeated here.

Non-destructive review flags were applied using the rules defined in Chapter 3 Section 3.6. In the fixed reference dataset, 36/414 entries were flagged: 4 procedural and 32 possible duplicate, with some entries carrying both flags. No rows were deleted. Flag counts mark review need and are not performance scores. Procedural flags also illustrate why journal validity and evidence strength must be rated separately: a hearing adjournment can be quote-supported while still failing the journal definition.

---

## 4.5 Journal validity, evidence strength and automated confidence (n = 50)

Human validation on a stratified sample of fifty entries (Chapter 3 Section 3.7) rated Rubric A (valid decision-journal entry?) and Rubric B (strength of quote-to-decision support?) blind to automated confidence scores.

Figure 4.9 shows the Rubric A × Rubric B cross-tabulation. In the stratified n = 50 sample, the most frequent cross-tabulation cell was no × high (21/50, 42%). Clean yes × high entries accounted for 11/50 (22%). The remaining cells were no × medium (11/50), no × low (1/50), unclear × high (5/50) and unclear × medium (1/50). Marginally, Rubric A comprised 11 yes, 33 no and 6 unclear; Rubric B comprised 37 high, 12 medium and 1 low. High evidence strength was therefore common, but journal suitability was not.

[[FIGURE:4.9]]

After human rating, two automated confidence signals were compared with Rubric B (Table 4.3). Linear weighted kappa treats adjacent disagreements as less severe than disagreements across the full evidence-strength scale. Neither signal showed sufficient agreement to replace human judgement on journal inclusion. When automated confidence was high, only about one in four items were Rubric A = yes, which is consistent with confidence tracking evidence strength better than journal validity.

| Signal | Exact agreement | Linear weighted κ |
|--------|-----------------|-------------------|
| Rule baseline | 80% | 0.48 |
| LLM second pass | 76% | 0.39 |

An exploratory discourse-tag analysis on the same fifty items assigned all 21 no × high cases to non-policy inquiry-discourse tags. Fourteen of the fifty items remained unclassified where applicable. The genre-blindness reading is exploratory; the tags were not a validated classifier or a causal analysis.

---

## 4.6 Exploratory thematic clustering for navigation (n = 414)

Exploratory thematic clustering organised all 414 candidates into 20 groups using agglomerative clustering on OpenAI `text-embedding-3-small` embeddings with cosine distance. No entries were left unclustered under the configured cut. Labels were applied after the groups formed and remain heuristic navigation aids. Cluster membership is not JEE or Decision Quality mapping, and the framework-mapping pilot in Section 4.7 leaves cluster membership unchanged.

Figure 4.10 shows the distribution of group sizes. The largest groups provide starting points for navigation, although group size does not establish policy importance or journal validity. Smaller groups include inquiry-procedure content alongside policy themes, which is consistent with the n = 50 finding that quote support does not guarantee journal suitability. Detailed cluster composition and example entries are in Appendix C.

[[FIGURE:4.10]]

---

## 4.7 Supplementary preparedness and Decision Quality findings (n = 60)

The supplementary pilot applied JEE preparedness and Decision Quality categories to a purposive sample of 60 records (Chapter 3 Section 3.9). The sample is not statistically representative of the 414 candidates, and no inferential statistics were used. Validated source passages, rather than generated decision wording, were the evidential basis for framework interpretation.

Table 4.4 reports the framework-mapping outcomes. JEE mapping was assigned for 11/60 records (18.3%). The remaining outcomes were no_mapping (16/60, 26.7%), insufficient_evidence (22/60, 36.7%) and procedural or inquiry content (11/60, 18.3%). These last two outcomes are different: no_mapping means the passage was understood but did not support a preparedness capacity, whereas insufficient_evidence means the available excerpt was too thin to decide. An observable Decision Quality element was recorded for 37/60 records (61.7%). The most frequent combined outcome in this purposive 60-record pilot was an observable Decision Quality element without a defensible JEE mapping, 26/60 (43.3%).

| Result family | Outcome | Count | Percentage |
|---------------|---------|------:|-----------:|
| JEE | Mapped | 11/60 | 18.3% |
| JEE | no_mapping | 16/60 | 26.7% |
| JEE | insufficient_evidence | 22/60 | 36.7% |
| JEE | Procedural/inquiry | 11/60 | 18.3% |
| Decision Quality | Observable Decision Quality element | 37/60 | 61.7% |
| Combined JEE/DQ | Observable Decision Quality without defensible JEE mapping | 26/60 | 43.3% |

*Note. The four JEE rows partition the n = 60 sample. The Decision Quality and combined rows overlap with those JEE outcomes and should not be added to the JEE total.*

Decision Quality elements describe features visible in a decision passage, such as framing, values or commitment to follow through. JEE mapping requires evidence of a specific preparedness capacity. An observable Decision Quality element does not mean that the underlying decision was good, and a JEE mapping does not demonstrate adequate preparedness performance.

Among the 11 JEE-mapped records, Infection prevention and control (R4) occurred in 3/11 (27.3%), while IHR coordination, National IHR Focal Point functions and advocacy (P3), Surveillance (D2), and Risk communication and community engagement (R5) each occurred in 2/11 (18.2%). Those shares should not be overinterpreted given the small mapped denominator. Among the 37 Decision Quality-mapped records, the primary elements were commitment to follow through (22/37, 59.5%), helpful frame (8/37, 21.6%), clear values (6/37, 16.2%) and useful information (1/37, 2.7%).

Source-level traceability was available for 53/60 records (88.3%). That figure records the availability of a traceable source passage. It does not establish that the generated decision statement faithfully represented that passage.

Table 4.5 reports the candidate-statement faithfulness classifications. Generated decision statements were not treated as authoritative evidence. Of the 60 candidate decisions, 8 were exact or near-verbatim representations of their source passages and 25 were judged to be substantively faithful paraphrases. Twenty introduced materially unsupported or altered meaning despite retaining a traceable source passage, while 7 were classified as non-traceable (`Traceability=False`). Framework interpretation therefore relied on the validated source passage rather than the generated decision statement. These categories were assigned by a single reviewer and should be interpreted as a structured feasibility assessment rather than an independently validated estimate of model error.

| Classification | Count | Percentage |
|----------------|------:|-----------:|
| Exact or near-verbatim | 8/60 | 13.3% |
| Substantively faithful paraphrase | 25/60 | 41.7% |
| Materially unsupported or altered | 20/60 | 33.3% |
| Non-traceable (`Traceability=False`) | 7/60 | 11.7% |

The pilot used single-reviewer adjudication supported by AI-assisted source-integrity and consistency audits. Six proposed corrections received interactive confirmation; 52 records retained earlier coding without a new record-by-record review; and 2 records met the predefined automatic-clear rule. Further review-provenance detail is provided in Appendix B and retained in the project repository.

---

## 4.8 Supplementary robustness and transfer checks

Supplementary checks tested quality lenses and transfer beyond the main hearing corpus. Table 4.6 summarises the bounded outcomes. Detailed tables are in Appendix B.

| Check | Scope | Main result |
|-------|-------|-------------|
| GRACE-adapted assessment | n = 16 triangulation-linked items | Descriptive quality lens only; not a journal-validity filter |
| Keyword lower-bound comparison | Six annotated excerpts | Keyword recall 1/6; LLM agreement-row recall 5/6 |
| Report-genre pilot | One Module 2 “In Brief” report | 53 candidates; 50/53 mechanically traceable; no manual validation |
| Structural reliability stress-test | 50 regenerations at temperature 0.3 | 49/50 structural pass; schema robustness only |

The GRACE-adapted scores are a descriptive quality lens only. The report-genre pilot shows transfer to a second document type, but those 53 items were not merged into the fixed reference dataset and were not manually validated. The structural reliability stress-test used temperature 0.3 and measured structural consistency only; the 49/50 pass rate does not establish decision accuracy or journal validity.

---

## 4.9 Summary of key findings

The Module 2 pilot produced 414 candidate entries with 84.8% mechanical traceability. In the stratified n = 50 sample, the most frequent dual-rubric cell was no × high (21/50), so evidence strength and journal validity must be assessed separately. Automated confidence tracked Rubric B more closely than journal inclusion. Clustering organised the 414 candidates into 20 navigation groups without validating them. In the purposive n = 60 pilot, Decision Quality features were observable more often than defensible JEE mappings, and framework interpretation depended on validated source passages rather than generated decision wording.
