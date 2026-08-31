# Chapter 3: Methodology

**Status:** Wave 1C revised methodology draft. Empirical outcomes are reported in Chapter 4.

**Figure references:** Figure 3.1, `outputs/figures/conceptual_framework.png`; Figure 3.2, `outputs/figures/implemented_pipeline.png`.

---

## 3.1 Research design and conceptual framework

This study designs and evaluates an LLM-assisted method for creating traceable candidate decision-journal entries from UK COVID-19 Inquiry Module 2 hearing transcripts. The work proceeds in two phases. Phase 1 generates candidate entries and checks whether each quoted source passage can be located in the processed transcript. Phase 2 then reviews and organises those candidates without changing the extracted text. Candidate generation and candidate evaluation therefore remain separate.

All later analyses use the same fixed reference dataset of candidate decision-journal entries. Different evaluation methods answer different questions: one checks source-quote location; another asks whether an entry belongs in a decision journal; another organises entries for navigation; a supplementary pilot asks whether source passages can support preparedness and Decision Quality interpretation. Human judgement remains necessary for deciding what the candidates mean and which of them belong in an auditable journal.

In this study, feasible MSc scale means a reproducible workflow bounded by eight processed hearing transcripts, 414 extracted candidate entries, the available manual evaluation samples, the research timeframe, and the available computing and API resources. It does not establish production scalability, economic efficiency, complete processing or full manual annotation of the wider Inquiry archive, or deployment readiness.

Figure 3.1 shows the workflow.

[[FIGURE:3.1]]

| Method | Question answered | Population or sample |
|--------|-------------------|----------------------|
| Mechanical traceability | Can the source quote be located in the processed transcript? | All 414 candidates |
| Review flags | Which candidates need human caution? | All 414 candidates |
| n = 50 human validation | Is the entry a valid journal item, and how strongly does the quote support the extracted text? | Stratified sample of 50 |
| Exploratory clustering | How can reviewers navigate the candidate pool? | All 414 candidates |
| n = 60 JEE/DQ mapping | Can source passages support preparedness or Decision Quality interpretation? | Purposive sample of 60 |

---

## 3.2 Case study and corpus

### 3.2.1 Case study: UK COVID-19 Inquiry Module 2

The empirical case is Module 2 of the UK COVID-19 Inquiry public archive, which focuses on core UK decision-making and political governance. Public hearing transcripts are suitable for decision extraction because they contain formal governance discussion, are publicly available for reproducibility, and require provenance for any claim attributed to the record. Module 2 concentrates on the core decision-making period the journal is designed to capture, while remaining small enough to evaluate carefully within an MSc project.

### 3.2.2 Phase 1 corpus: eight hearing transcripts

Phase 1 used eight Module 2 hearing transcripts spanning 28 November 2023 to 23 May 2024. Selection was purposive: complete PDF and text availability, a mix of witness types, and coverage of early and late Module 2 hearings. Eight transcripts provided enough variation to evaluate extraction behaviour while remaining feasible for manual validation. The wider Inquiry archive is much larger; that archive was not fully processed or manually annotated in this study.

| Hearing date | Approx. role in sample |
|--------------|------------------------|
| 28 Nov 2023 | Manual annotation (Gove / Cabinet Office) |
| 30 Nov 2023 | Manual annotation (Gove narrative excerpts) |
| 01 Dec 2023 | Manual annotation (Hancock) |
| 07, 11, 13, 14 Dec 2023 | Broader automated extraction only |
| 23 May 2024 | Broader automated extraction only |

A report-genre pilot (one Inquiry “In Brief” PDF) illustrates a second document type but is not part of the fixed reference dataset; it is reported separately in Chapter 4.

### 3.2.3 Operational definition of a decision-journal entry

Manual annotation and Phase 2 validity assessment (Rubric A) use the following operational definition:

> **Decision journal entries** record pandemic-response **agreements, adopted measures, and authoritative directions** (who decided or agreed what), as stated in the source text, including when recalled in inquiry evidence, each backed by a **verbatim source quote**. Witness opinion, speculation, and options that were not agreed are excluded.

This definition is stricter than colloquial use of “decision” in transcript dialogue. Advocacy, retrospective lessons, procedural hearing administration, and invitations to recommend are excluded even when the LLM extracts them with a supporting quote.

The inquiry-mode LLM prompt asks for “formal decisions announced during the hearing,” which partially aligns with this definition but can blur historical COBR or COVID-O decisions cited in testimony. That definitional tension is an evaluation finding reported in Chapter 4.

---

## 3.3 Extraction and source traceability

### 3.3.1 Data ingestion

Public inquiry documents were ingested through a staged, reproducible pipeline:

1. **Harvest:** Module 2 hearing metadata from the public inquiry API.
2. **Download:** hearing PDFs to local storage.
3. **Text extraction:** PDF-to-text with inquiry-aware cleanup of line breaks, page artefacts, and spacing.

The source list and processing settings were version-controlled so that the same corpus can be reproduced. Raw PDFs were not stored in the project repository because of file size; processed text and extraction outputs were retained for audit.

[[FIGURE:3.2]]

Retrieval-augmented generation was not adopted because extraction operated on sequential, fixed transcript chunks rather than retrieval across a heterogeneous collection. Each complete chunk is supplied directly to the model, which simplifies item-level provenance and mechanical traceability.

### 3.3.2 Model, chunking and temperature

Extraction used gpt-4o-mini through the OpenAI API. Transcripts were split into overlapping sentence windows of seven sentences per chunk with overlap of two. Sentence boundaries were preferred over fixed token windows so that source-location pointers remain interpretable and align with the mechanical traceability check.

Temperature controls how much variation the model is allowed to introduce when generating text. The main Phase 1 extraction used temperature 0 to reduce avoidable variation and support reproducibility of the fixed reference dataset. Temperature 0 does not guarantee identical semantic wording in every regeneration, but it removes one controllable source of randomness. Temperature 0.3 was used only in a separate structural reliability stress-test, reported in Section 4.8, to introduce limited output variation while checking schema consistency.

All eight Phase 1 transcript runs used the inquiry-mode prompt. Each chunk is processed independently; candidate entries from all chunks are merged and deduplicated within the run.

### 3.3.3 Decision object schema

Each extracted item is a structured object with four mandatory fields:

| Field | Purpose |
|-------|---------|
| `decision` | The extracted decision claim (normalised statement) |
| `evidence` | The model’s explanation of why the quote supports the decision |
| `source_quote` | Verbatim quote from the chunk text |
| `source_location` | Sentence-level pointer (for example, `sentence_2`, `sentences_4-5`) |

Each run also records `traceability_ok`: a mechanical check that `source_quote` can be located in the processed source text after alphanumeric normalisation.

### 3.3.4 Traceability as an auditable floor

A pass confirms a quotable anchor in the source document. It does not confirm that the extraction is a valid decision-journal entry. Failures are classified by type and reported in Chapter 4. Traceability failure does not automatically imply low human confidence on evidence support; those dimensions are evaluated separately later.

---

## 3.4 Fixed reference dataset of candidate decision-journal entries

Phase 1 establishes a fixed reference dataset of candidate decision-journal entries before any interpretive processing begins. Extraction outputs from the eight inquiry runs were merged into one dataset with stable identifiers, hearing provenance, extraction fields, traceability outcomes, and space for later annotations.

The fixed reference dataset is the unchanged set of 414 candidate entries created in Phase 1. It is used as the common input for review flags, the n = 50 validation, exploratory clustering, and the n = 60 framework-mapping pilot. Keeping the dataset unchanged allows extraction quality to be evaluated separately from later review and interpretation.

This design supports three practical properties:

1. **Auditability:** every entry traces to a source transcript and extraction run.
2. **Reviewability:** humans can inspect or rate entries without re-running extraction.
3. **Reproducibility:** rebuilding from the same eight runs yields the same identifiers and counts.

The fixed reference dataset is not a verified catalogue of policy decisions. It is a candidate pool for review.

---

## 3.5 Phase 1 evaluation

Phase 1 evaluation combines detailed manual review of a small purposive sample with automated measures across the pilot corpus. The manual analysis compares human and LLM extraction, applies adapted GRACE dimensions, and identifies recurring error types. Automated checks assess traceability and compare the LLM with a simple keyword baseline. A separate structural reliability test examines schema consistency under limited output variation (Section 4.8). These methods answer different questions and are therefore reported separately rather than combined into a single quality score [23].

### 3.5.1 Manual triangulation sample

Six excerpts (approximately 200–450 words each) were drawn from three hearing days (28 November, 30 November and 1 December 2023) and two witness types. The author labelled decisions in each excerpt before inspecting model outputs in the same text regions, then compared manual and LLM extraction using MATA-style convergence categories [23].

Agreement means the manual and LLM labels refer to the same formal decision. Silence means a decision appears in one method only. Dissonance means genuine disagreement on whether a decision exists or what it was. Results are reported in Chapter 4.

### 3.5.2 GRACE-adapted quality assessment

A subset of LLM items from the triangulation workbook was scored on four dimensions adapted from the GRACE framework [24]: interpretability, actionability, nuance, and redundancy. GRACE characterises output-quality dimensions that traceability and the later confidence rubrics do not capture. It does not replace those methods.

### 3.5.3 Error taxonomy

To extend analysis beyond six excerpts, a stratified sample of 42 items was constructed: nine author-validated false positives from triangulation silence rows plus 33 heuristic-classified samples from the full inquiry corpus (random seed = 42). Items were labelled by error type. This provides sampled error-pattern evidence without claiming item-by-item manual verification of all 414 candidates.

### 3.5.4 Keyword baseline

A simple keyword baseline was applied to the same six excerpt regions to establish a lower bound for decision-detection recall against manual labels. Keyword matching isolates lexical trigger sensitivity from LLM semantic extraction. Results are compared in Chapter 4.

---

## 3.6 Non-destructive review flags

Review flags mark candidates that need human caution while leaving the full candidate pool intact. Flagged entries remain in the fixed reference dataset so that later analysis can still examine false positives and boundary cases. Flags identify entries for attention; they do not determine journal validity and they do not delete rows.

| Flag | Rule (summary) |
|------|----------------|
| `procedural` | Hearing adjournment, resume time, scheduling, or meta-inquiry text |
| `possible_duplicate` | Identical normalised decision text or shared source quote (at least 50 characters) |

Flag rules were implemented as deterministic pattern checks over decision text and source quotes. Outcomes are reported in Chapter 4.

---

## 3.7 Confidence and journal-validity evaluation (n = 50)

The n = 50 evaluation tests whether automated confidence aligns with human judgement. It is separate from the later n = 60 preparedness and Decision Quality pilot.

### 3.7.1 Stratified sample

Human validation uses a stratified sample of fifty entries drawn from the fixed reference dataset after review flags (random seed = 42). The sample balances triangulation-linked cases, flagged entries, traceability failures, and unflagged traceable entries while remaining practical for detailed manual assessment.

| Stratum | n | Selection |
|---------|---|-----------|
| Triangulation workbook | 15 | Comparison rows mapped to journal IDs where possible |
| Flagged | 10 | Mix of procedural and possible_duplicate |
| Traceability fail | 10 | Random from traceability failures |
| Random unflagged traceable | 15 | `traceability_ok = true`, empty `review_flags` |

The author rated items blind to automated confidence scores. Automated scores were generated only after the human labels were complete. Each item was presented as an audit package containing the decision text, evidence field, source quote, and source location.

### 3.7.2 Rubric A: journal validity

Rubric A asks whether the entry belongs in a policy or governance decision journal. It requires domain judgement.

| Rating | Criterion |
|--------|-----------|
| **Yes** | Agreed measure, authoritative direction, or adopted action (including recalled in testimony), with plausible quote support |
| **No** | Procedural, advocacy, witness opinion, narrative, or unadopted recommendation |
| **Unclear** | Borderline; ambiguous cases are retained as findings |

### 3.7.3 Rubric B: evidence strength

Rubric B asks how strongly the audit package supports the stated decision text. It does not ask whether the entry belongs in the journal.

| Level | Criterion |
|-------|-----------|
| **High** | Quote clearly supports the decision text with minimal inference |
| **Medium** | Partial or indirect support; some inference or bundling required |
| **Low** | Quote missing, unreadable, or does not support the decision |

Rubric B used two yes/no checks: whether the quote is present and readable, and whether it supports the decision text, scored as 0 = low, 1 = medium, and 2 = high.

### 3.7.4 Interpretation framework

Because Rubric A and Rubric B answer different questions, they are cross-tabulated rather than combined into a single score. A candidate may receive strong quote support (Rubric B) while still failing the journal definition (Rubric A), as when a procedural adjournment is extracted faithfully but is not a policy or governance decision. Examining the two ratings together therefore helps distinguish strong journal entries, valid decisions with weaker evidence, faithful extractions of the wrong type of content, and weak or noisy candidates. The table below summarises these joint patterns for interpretation in Chapter 4.

| Rubric A | Rubric B | Interpretation |
|----------|----------|----------------|
| Yes | High | Strong journal entries |
| Yes | Medium | Valid decision; partial or indirect quote support |
| Yes | Low | Decision-like but weakly evidenced |
| No | High | Correct extraction of the wrong artefact type |
| No | Medium | Not a journal entry; quote only partly supports text |
| No | Low | Noise |
| Unclear | High | Borderline inclusion; evidence supports extraction well |
| Unclear | Medium | Borderline inclusion; partial support |
| Unclear | Low | Borderline inclusion; weak support |

### 3.7.5 Automated confidence signals

Automated confidence is not treated as ground truth. This step tests whether an automated signal could assist human review and whether its use is supported by comparison with human judgement.

On the same stratified sample of 50 items, two automated confidence signals were generated only after the human Rubric A and Rubric B labels were complete:

1. **Rule-based baseline:** heuristics over decision verbs, hedging language, quote length, and traceability outcome.
2. **LLM-assigned confidence:** a second pass over decision and quote only, with an explicit reasoning field.

Both signals are intended to represent evidence strength — how strongly the quotation supports the generated statement — rather than journal validity. Rubric B is therefore the primary comparison. The signals were compared with Rubric B using linear weighted kappa and were cross-tabulated separately with Rubric A to examine how the confidence signals related to journal-validity ratings without treating journal validity as their primary target. Linear weighting treats adjacent disagreements (for example High versus Medium) as less severe than larger disagreements (High versus Low) on the ordinal evidence-strength scale. The analysis asks whether each signal shows sufficient agreement with human evidence-strength judgement to be informative as a review aid; weak agreement is retained as a meaningful finding and does not justify replacing human review. Because the ratings were produced by a single author, the comparison is a structured feasibility assessment rather than an independently validated reliability study. Outcomes are reported in Chapter 4.

---

## 3.8 Exploratory thematic clustering for journal navigation

Exploratory thematic clustering organises the fixed reference dataset so that reviewers can navigate related candidates. It is an unsupervised organisational method rather than a validity test or formal policy classification.

All 414 candidate entries were included. Each entry was embedded from the concatenated decision text, evidence field, and source quote. OpenAI `text-embedding-3-small` vectors were clustered with agglomerative clustering using cosine distance. A cosine-distance threshold of 0.68 was used to cut the agglomerative hierarchy, producing 20 groups in this pilot. That value was the configured pilot threshold; it was not established as a universally optimal threshold, and a different cut could change cluster granularity.

Cluster membership was determined before labels were assigned. Heuristic thematic labels were added after the groups formed. The labels are navigation aids for reviewers. They are not a validated public-health taxonomy, and Joint External Evaluation or Decision Quality categories did not determine cluster membership.

The framework-mapping pilot in Section 3.9 uses source-based category assignment rather than clustering and leaves cluster membership unchanged. Results are reported in Chapter 4.

---

## 3.9 Supplementary preparedness and Decision Quality mapping pilot

The supplementary pilot applies established preparedness and Decision Quality categories to selected source passages. It is separate from the clustering analysis and does not change cluster membership. It uses a purposive sample of 60 entries. The sample is not statistically representative of all 414 candidates, and no inferential statistics were used. The pilot is supplementary to the main extraction and validation workflow.

### 3.9.1 Frameworks

The preparedness mapping used the Joint External Evaluation (JEE) tool for International Health Regulations (2005) core capacities [9]. The Decision Quality mapping used the six elements of Decision Quality as presented by Spetzler, Winter and Meyer [10] and operationalised from Decision Education Foundation definitions [11]:

| Element | Meaning in this study |
|---------|------------------------|
| `helpful_frame` | The passage helps define the decision problem or framing |
| `clear_values` | The passage makes trade-offs, priorities, or values explicit |
| `creative_alternatives` | The passage identifies or compares credible alternatives |
| `useful_information` | The passage supplies information relevant to the decision |
| `sound_reasoning` | The passage shows reasoned justification linking evidence and action |
| `commitment_to_follow_through` | The passage shows authorised action, implementation, or follow-through |

Technical labels are retained for reproducibility; the table above gives their practical meaning.

### 3.9.2 Evidence basis

Generated decision statements were treated as candidate summaries. Validated source passages were the evidential basis for framework interpretation. Generated wording was not treated as authoritative. Two distinct boundary outcomes were allowed: `no_mapping`, where the passage did not support a framework category, and `insufficient_evidence`, where the available excerpt was too thin to decide.

### 3.9.3 Candidate ranking and adjudication

Cosine similarity ranked possible framework categories for each record. The ranking supported reviewer attention but did not determine the final assignment. Final assignments were based on source evidence and human adjudication. Category descriptions and evidence rules were fixed before the final analytical audit.

### 3.9.4 Review provenance

This subsection records how the final n = 60 classifications were reached. Its purpose is transparency about human re-review, not a separate evaluation experiment. All 60 records had been reviewed previously; the final audit stage did not imply that every record was newly or independently re-reviewed.

The n = 60 pilot was adjudicated by one reviewer and supported by AI-assisted source-integrity and coding-consistency audits. Those automated checks screened prior coding for consistency; they did not replace human adjudication or validate substantive correctness. Three routes produced the final classifications: six proposed corrections were interactively confirmed by the reviewer; for 52 records, the consistency audit recommended no change and the earlier coding was retained without a new record-by-record review; and two records met the predefined automatic-clear rule. The resulting classifications should therefore be treated as a single-reviewer feasibility assessment, not as independently validated or gold-standard annotations.

### 3.9.5 Source-passage traceability classifications

One reviewer also classified how closely each generated decision statement related to its source passage using four categories: exact or near-verbatim; substantively faithful paraphrase; materially unsupported or altered; and non-traceable (`Traceability=False`). These classifications form a structured feasibility assessment rather than an independently validated estimate of model error.

Empirical mapping outcomes are reported in Chapter 4. This section describes only the method.

---

## 3.10 Scope, limitations and ethical considerations

### 3.10.1 What the research delivers

This project delivers a research pipeline: reproducible scripts, structured artefacts, annotation materials, and evaluation summaries suitable for independent audit within the eight-transcript pilot.

### 3.10.2 What was not built

| Deferred item | Rationale |
|---------------|-----------|
| Full processing of the wider Inquiry archive | Eight transcripts were processed; the larger archive was not fully processed or manually annotated within MSc scope |
| Decision dependency network | Outside the contribution of this extraction and validation study; reserved for future work |
| Model retraining / feedback loop | The study evaluated prompt-based extraction and validation rather than supervised model development; a sufficiently large, independently validated labelled dataset was unavailable |
| Actionability scoring | Would require a validated entry set and stakeholder-agreed criteria beyond the present pilot |
| Full deployment or live decision support | Outside the research scope of this MSc project |

Recognised preparedness and Decision Quality frameworks were examined through the supplementary n = 60 pilot in Section 3.9 rather than being deferred.

### 3.10.3 Ethical and data considerations

All source materials are from the public UK COVID-19 Inquiry archive. No private or participant-identifiable data beyond what is already published in hearing transcripts was collected. The author conducted the manual annotation and validation on the bounded samples; inter-rater reliability with a second human coder was not performed within project scope and is noted as a limitation in Chapter 5.

The extraction used the OpenAI API. Detailed token-usage and cost records were not retained for the Phase 1 runs, so computational cost was not evaluated as part of the study.

---

## 3.11 Chapter summary

Chapter 3 specified a two-phase methodology. Phase 1 extracts candidate entries from eight Module 2 transcripts, checks source-quote location, and stores the results as a fixed reference dataset of 414 candidates. Phase 2 then applies non-destructive review flags, an n = 50 dual-rubric human validation of journal validity and evidence strength, exploratory clustering for navigation, and a supplementary n = 60 Joint External Evaluation and Decision Quality mapping pilot. Human judgement remains necessary for interpretation. Chapter 4 reports the empirical outcomes.
