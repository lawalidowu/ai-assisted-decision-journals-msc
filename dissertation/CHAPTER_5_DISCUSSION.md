# Chapter 5: Discussion and conclusion

This chapter considers what the findings mean for AI-assisted decision journaling and for the use of extracted public records in policy review. The results show that producing traceable candidate records is technically feasible at the scale examined, but traceability alone does not establish that an entry belongs in a decision journal or that its generated summary faithfully represents the source. The discussion therefore focuses on the distinction between candidate generation and human validation, the complementary roles of clustering and recognised policy frameworks, and the conditions under which the approach could support organisational learning.

## 5.1 Interpretation of the main findings

### 5.1.1 Traceability, fidelity and journal validity

Mechanical source-quote traceability on the fixed reference dataset of candidate decision-journal entries showed that most extracted quotes could be located in the processed hearing text (Chapter 4 Section 4.2). That check matters: without a locatable anchor, a candidate cannot be audited against the public record. It is not, however, a test of journal membership. The stratified n = 50 validation separated evidence strength from journal validity and showed that strong quote support can accompany items that still fail the operational journal definition (Chapter 4 Section 4.5). In short, the extractor can reproduce decision-like language accurately while proposing the wrong kind of artefact for a decision journal.

The purposive n = 60 pilot sharpens the same point from another direction. Source-level traceability records whether a usable source passage is available; candidate-statement faithfulness asks whether the generated decision wording accurately represents that passage (Chapter 4 Section 4.7). Those questions are related but not identical. A passage can be available while the generated summary introduces unsupported or altered meaning. For policy interpretation, therefore, the validated source passage remains authoritative. Generated candidate statements are working products for review, not substitutes for the underlying transcript evidence [6], [26].

### 5.1.2 Confidence, discourse and human judgement

In the stratified n = 50 sample, the most frequent Rubric A × Rubric B cell was no × high: the quoted passage strongly supported the generated text, yet the item did not meet the journal definition (Chapter 4 Section 4.5). That cell pattern should not be read as a corpus-wide prevalence estimate. It is a sample-specific signal that discourse or artefact type can be misclassified even where quote support is strong. The exploratory discourse tags applied to the same fifty items are consistent with a genre-blindness working hypothesis, but they left some records unclassified and do not establish a causal mechanism. The safer claim is narrower: human judgement is still required to decide whether an extraction belongs in a decision journal, and that judgement is not reducible to quote matching alone [22], [23].

Automated confidence behaved in line with that separation. Both the rule baseline and the LLM second pass aligned more closely with evidence strength than with journal inclusion (Chapter 4 Section 4.5). High automated confidence may help reviewers decide where to look first. It cannot replace a domain decision about artefact type, and it should not be treated as a self-reported guarantee of quality [5], [6]. The practical implication is a review posture rather than a new failure-mode claim: treat confidence as an inspection aid, keep journal validity as a human call, and avoid collapsing fidelity and suitability into a single score.

### 5.1.3 Clustering and framework mapping as complementary methods

Exploratory clustering organised all 414 candidates into thematic groups for navigation (Chapter 4 Section 4.6). Heuristic labels were applied after the groups formed. Those labels help a reviewer find related candidates; they are not a validated policy ontology and they do not verify journal membership. Separately, the purposive n = 60 pilot applied recognised Joint External Evaluation (JEE) preparedness and Decision Quality categories to source passages (Chapter 4 Section 4.7; Chapter 3 Section 3.9). Framework mapping did not rerun, replace or validate clustering. The two analyses answer different questions.

Clustering can make a large candidate pool easier to navigate. Decision Quality mapping asks which features of the decision process are visible in a passage, such as framing, information use, values or commitment to follow through [10]. JEE mapping asks whether the available evidence supports assignment to a recognised preparedness capacity [9]. In the purposive 60-record pilot, an observable Decision Quality element was recorded for 37/60 records and a defensible JEE mapping for 11/60. Within that pilot, the most frequent combined outcome was an observable Decision Quality element without a defensible JEE mapping, 26/60 (Chapter 4 Section 4.7). A defensible reading is that a transcript passage may show how an issue was framed, what information was used or whether implementation followed, while still lacking enough capacity-specific evidence for a preparedness assignment. That pattern does not mean Decision Quality mapping proves a decision was good, that JEE non-mapping indicates poor preparedness, or that the n = 60 distribution estimates the full 414-entry set.

## 5.2 Methodological and policy contribution

### 5.2.1 Governed candidate generation and review

The main methodological contribution is a governed process for creating and reviewing candidate decision-journal entries from public inquiry text. The pipeline generates candidates with mandatory provenance fields, checks mechanical traceability, and stores a fixed reference dataset so later enrichment does not silently rewrite the extraction object. Non-destructive review flags mark caution without deleting rows. Dual-rubric human validation separates journal validity from evidence strength. Automated confidence is compared with those judgements rather than accepted at face value. Clustering supports navigation across the candidate pool, while recognised frameworks support structured interpretation on a bounded supplementary sample. Human judgement determines journal inclusion.

That contribution is deliberately bounded. It is not a new clustering algorithm, a new JEE instrument, a new Decision Quality theory, an automatically verified policy catalogue, or a deployment-ready application for inquiry staff. Its claim is procedural: candidate generation and candidate evaluation can be kept separate, auditable and inspectable at MSc pilot scale, in a form that makes failure modes visible before any institutional use [17], [18], [19].

### 5.2.2 Organisational learning and public-sector relevance

UK COVID-19 Inquiry Module 2 is the empirical case study through which the dissertation examines a broader problem: how public-health and crisis institutions can reconstruct decision records from complex public transcripts under auditable governance. Structured decision recording has long been linked to accountability and organisational learning [1], [2], [3]. Public inquiries extend that logic to society-wide events, but hearing transcripts are not themselves decision journals. A governed extraction-and-review workflow sits between those two artefacts.

Used carefully, such a workflow could support retrospective reconstruction of what was said to have been decided; source-linked review of the evidence attached to candidate records; inspection of framing, information use and follow-through where those features are visible; and navigation across large candidate sets. It can also keep AI-generated candidates visibly distinct from human-validated entries, which is a minimum requirement if institutions are to use language models without mistaking generated summaries for settled findings [17], [18], [19]. Decision Quality and JEE categories can help public-health readers ask recognisable review questions about process features and preparedness capacities, provided the mappings remain interpretive aids rather than performance scores [9], [10].

The claim stops there. The prototype does not determine whether a government decision was correct, evaluate political performance, measure preparedness adequacy, guarantee improved outcomes, provide live decision support, or stand ready for deployment. Its policy value is methodological and organisational: it shows how candidate records from public text can be generated, challenged and reviewed in a form that supports institutional memory without pretending that machine output has already settled the record.

## 5.3 Limitations and threats to validity

### 5.3.1 Case-study and corpus scope

The evaluation used eight Module 2 hearing transcripts rather than the wider Inquiry archive of approximately 300 documents. The corpus was purposive, chosen for pilot feasibility and for hearings concerned with core decision-making and political governance. Public inquiry hearings are an adversarial and retrospective genre; transfer to other document types remains limited. A single report-genre pilot showed that the pipeline can run beyond hearing transcripts, but those outputs were not manually validated and were not merged into the fixed reference dataset (Chapter 4 Section 4.8). Feasibility at MSc scale does not establish production scalability or economic efficiency.

### 5.3.2 Human review and sample design

Both principal human evaluations were single-reviewer designs. In the stratified n = 50 validation, all ratings were made by the author. The reported kappa values measure alignment between automated confidence signals and the author’s Rubric B ratings; they are not inter-rater reliability coefficients [28]. Sparse cells in the Rubric A × Rubric B cross-tabulation also limit how firmly cell proportions, including the no × high pattern, can be interpreted. That pattern remains a sample-specific finding, not a corpus-wide error rate (Chapter 4 Section 4.5).

In the purposive n = 60 framework-mapping pilot, original adjudication was likewise by one reviewer. Six proposed corrections received interactive confirmation, 52 records retained earlier coding without a new record-by-record review, and two met the predefined automatic-clear rule (Chapter 4 Section 4.7; Appendix B.8). Candidate-statement faithfulness classifications were also assigned by a single reviewer. These outputs support a structured feasibility assessment; they are not independently validated gold-standard annotations, and the n = 60 sample is not representative of all 414 candidates.

### 5.3.3 Technical and analytical limitations

Mechanical traceability tests presence in processed plain text, not page-level linkage to published Inquiry PDFs, and source locations remain chunk-relative. Extraction used a single model with fixed inquiry-mode prompting and chunking; no model or prompt ablation was run at corpus scale. Detailed token-usage and cost records were not retained for the Phase 1 runs, so computational cost was not evaluated as part of the study. The keyword baseline was intentionally simple, and GRACE scoring provided only a supplementary quality lens. The structural reliability stress-test measured schema robustness under limited output variation; it did not establish decision accuracy or journal validity (Chapter 4 Section 4.8).

Clustering structure depends on embedding choice, linkage and cut; heuristic labels are navigation aids rather than a verified ontology, and exploratory projections were illustrative only (Chapter 4 Section 4.6). Framework mapping used cosine similarity only to rank candidate categories for human review; final assignments rested on source-passage adjudication in a purposive sample and should not be read as performance judgements about decision quality or preparedness (Chapter 3 Section 3.9; Chapter 4 Section 4.7).

### 5.3.4 Ethical and use boundaries

All source material came from the public Inquiry archive. The study did not use private submissions or unpublished evidence bundles. Generated candidate records must not be cited as official Inquiry findings, and source passages should be checked before any interpretive use. AI-generated and human-validated states need to remain visibly distinct. Any organisational deployment would require roles, review capacity and accountability mechanisms beyond the scope of this dissertation [17], [18], [19].

## 5.4 Conditions for responsible development and scaling

Future development should follow one governing principle: trustworthiness before scale. The sequence below follows the risks already visible in the results.

Inter-rater validation comes first. Both the n = 50 Rubric A/B assessments and the n = 60 framework and faithfulness codes currently depend on one reviewer; stability beyond that reviewer must be established before scaling interpretive claims.

Discourse- and speaker-aware checks on journal validity should follow, because the no × high pattern in the n = 50 sample points to artefact-type confusion rather than missing quotes alone. Stronger page-level provenance would then improve audit against published PDFs.

Controls for candidate-statement faithfulness are needed before generated wording is treated as an evidence layer. Confidence signals should be recalibrated toward journal validity rather than evidence strength alone, because confidence here related more closely to the latter. Periodic coding-consistency review is advisable if framework-mapping work expands.

Only after those validation layers are strengthened does wider corpus expansion make methodological sense; expanding earlier would scale existing weaknesses. Interface, product and deployment work come last: web tools, dependency networks, actionability scoring, live inquiry support and staff deployment all presuppose a validated candidate set and institutional governance that this dissertation does not design.

That order also states the responsible-use conclusion of the supplementary n = 60 analysis. The pilot is suitable as feasibility evidence when its purposive sampling, single-reviewer limits and non-representativeness of the 414-entry set are kept explicit. Broader scaling should wait for stronger independent human validation and planned review capacity. Generated decision statements should not become the evidential basis.

## 5.5 Conclusion

This dissertation designed and evaluated an LLM-assisted method for producing traceable candidate decision-journal entries from complex public records, using UK COVID-19 Inquiry Module 2 hearings as a case study of a broader public-record decision-journaling problem. At the eight-transcript scale examined, the pipeline produced a fixed reference dataset with mechanical provenance checks, indicating that the workflow was feasible within the study’s bounded scope. Extraction alone was not enough. Journal validity, semantic faithfulness and framework interpretation still required human judgement.

The main contribution is therefore the governed separation of candidate generation from later evaluation: flags, dual rubrics, tested confidence, navigational clustering and bounded framework interpretation operate on one inspectable object without treating machine output as a verified policy catalogue. Used under those constraints, the workflow can support source-linked retrospective review and organisational learning from public emergency records. The next justified step is stronger independent human validation before any expansion of the corpus.
