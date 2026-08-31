# Chapter 1: Introduction

## 1.1 Background and context

Modern governments responding to national emergencies must often decide quickly, under uncertainty, and across organisational boundaries. The records of those decisions are rarely held in one place. Instead they are scattered through reports, meeting notes, correspondence and public inquiries, which makes later reconstruction of what was decided, on what evidence, and with what follow-through a persistent institutional-memory problem [1], [2].

Structured records of decisions, supporting evidence and rationale offer one response to this problem. In this dissertation, a decision journal is defined as a structured record that pairs a decision claim with the evidence, provenance and contextual information needed for later review. This form of record-keeping can support accountability, audit and organisational learning [1], [2], [3]. In practice, however, many of the richest public sources are not journals at all. They are long, mixed texts in which agreements, adopted measures and authoritative directions sit beside questions, procedure, advocacy and narrative.

Large language models (LLMs) offer a plausible technical response to that documentation gap. Brown et al. [4] show that few-shot, in-context prompting can support task adaptation without task-specific fine-tuning, which motivates prompt-based structured extraction as an application of that capability. Reliable provenance and accountable acceptance into a decision journal are not established by that work alone. Foundation-model research documents risks such as hallucination, over-generation and sensitivity to prompt wording [5], [6]. In inquiry transcripts, these risks can blur the practical distinction between what was agreed and what was only urged or recalled. For high-stakes public records, extraction therefore needs mechanical source checks and human review, not face-value acceptance of model output.

The empirical case study used here is UK COVID-19 Inquiry Module 2. Established under its Terms of Reference in 2022, the Inquiry examines core decision-making and political governance during the pandemic [7]. Its hearing transcripts provide a reproducible public corpus in which ministers, officials and advisers recall decisions taken in COBR, COVID-O and related forums. The Inquiry is treated as a case study of a broader public-record decision-journaling problem, not as the sole purpose of the method.

## 1.2 Problem statement

The core problem is how to convert complex public records such as inquiry transcripts into structured, auditable candidate decision-journal entries without sacrificing provenance or human oversight. Transcripts use “decision” loosely: ministers urge action, witnesses offer retrospective lessons, and procedural business interrupts substantive testimony. A practical journal definition therefore has to distinguish agreements, adopted measures and authoritative directions from decision-like language that should not enter the record.

Automated extraction faces a further difficulty. An LLM may locate and quote a passage faithfully while still proposing the wrong kind of artefact for a decision journal, or it may generate a summary that alters the meaning of a usable source passage. Strong quote support is not the same as journal validity, and source-level availability is not the same as semantic faithfulness. Any useful system must therefore help humans review candidates rather than treat model output as accepted evidence.

## 1.3 Research aim and objectives

### Aim

To design and evaluate an LLM-assisted method for creating traceable candidate decision-journal entries from complex public records, using UK COVID-19 Inquiry Module 2 transcripts as a case study.

### Objectives

1. Develop a reproducible LLM-assisted method for extracting candidate decision-journal entries and associated source evidence from public inquiry transcripts.

2. Develop an auditable decision-journal representation that links candidate entries to their source evidence and provenance for later human review.

3. Evaluate the reliability and limitations of the extraction and review process, including source traceability, journal validity, evidence strength, summary faithfulness and recurring failure modes.

4. Assess how AI-assisted decision journaling can support transparent human review, organisational learning and structured policy interpretation, and identify conditions for responsible future development.

## 1.4 Scope and boundaries

The empirical work used eight Module 2 hearing transcripts and produced candidate decision-journal entries rather than an accepted catalogue of government decisions. Human evaluation used a stratified n = 50 sample for journal validity and evidence strength, and a purposive n = 60 pilot for Joint External Evaluation preparedness mapping, Decision Quality mapping and candidate-statement faithfulness. The study did not process or manually validate the full Inquiry archive, and the prototype was not evaluated as a production system. The conclusions concern feasibility and governed review at MSc scale.

## 1.5 Dissertation outline

**Chapter 1** sets the problem, scope, aim and contribution. **Chapter 2** reviews decision journaling, extraction, provenance, human evaluation and policy-framework literature, then identifies the research gap. **Chapter 3** describes methods for extraction, traceability, fixed reference dataset construction, bounded validation, clustering and supplementary JEE/Decision Quality work. **Chapter 4** reports results for n = 414, n = 50 and n = 60 separately. **Chapter 5** interprets findings, states the contribution and limitations, sets scaling conditions and concludes. **Appendices** provide manual excerpts and supporting material.

## 1.6 Contributions

The methodological contribution is a governed extraction-and-review process rather than a new extraction or clustering algorithm. Candidate generation is kept separate from later evaluation: entries are linked to source evidence, kept unchanged in a fixed reference dataset, and assessed separately for journal validity and evidence strength. Review flags, confidence checks, clustering and recognised frameworks support that process, but human judgement remains necessary.

The empirical contribution is bounded feasibility evidence from an eight-transcript case study and two separate evaluation samples: n = 50 for journal validity and evidence strength, and n = 60 for framework interpretation and for assessing whether generated statements accurately reflected their source passages.

The policy and organisational-learning contribution is a practical model for source-linked retrospective review and institutional memory. It keeps AI-generated candidates visibly separate from human-validated records and does not claim deployment readiness or automated policy judgement.
