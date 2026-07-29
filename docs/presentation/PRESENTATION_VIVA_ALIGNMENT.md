# Presentation–viva alignment — Wave 5A

Maps major presentation claims to likely viva pressure, evidence answers, and limitations.  
Paths are relative to repo root.

---

## 1. Why this is an AI project rather than only document processing

| Field | Content |
| --- | --- |
| Likely question | “Isn’t this just PDF parsing / rules?” |
| Strongest answer | Candidate objects are produced by an LLM few-shot / prompt-based extractor; contribution is then **governing** those candidates with traceability, fixed freeze, and human constructs (validity ≠ strength ≠ faithfulness). |
| Limitation | Not a new foundation model or SOTA IR architecture. |
| Dissertation | Ch1 §§1.1–1.3; Ch3 extraction methods; Ch1.6. |
| Examiner package | `docs/examiner_evidence/README.md`; lineage docs. |
| Demo case | Any candidate object panel (016/082) — “Frozen LLM candidate” block. |

## 2. Why traceability is not the same as validity

| Field | Content |
| --- | --- |
| Likely question | “351/414 means the system works — yes?” |
| Strongest answer | Traceability checks whether a generated statement can be linked to source tokens/chunks; Rubric A asks whether the artefact belongs in a **policy decision journal**. n=50 modal cell is **no × high**. |
| Limitation | Traceability rules are automated approximations; human review remains required. |
| Dissertation | Ch4 §§4.2, 4.5. |
| Examiner package | Evidence map rows 414 / 351 / 21/50. |
| Demo | **phase1-082**. |

## 3. Why no × high occurs

| Field | Content |
| --- | --- |
| Likely question | “How can evidence be High if the answer is No?” |
| Strongest answer | Rubric B rates **quote support / evidence strength**; Rubric A rates **journal membership**. Procedural hearing administration can quote perfectly and still be the wrong artefact type. |
| Limitation | Rubrics are author-operationalised at MSc scale. |
| Dissertation | Ch4 §4.5; Fig 4.9; 21/50. |
| Examiner package | `confidence_validation_sample.json`. |
| Demo | **phase1-082** centrepiece. |

## 4. Why kappa is moderate

| Field | Content |
| --- | --- |
| Likely question | “0.48 / 0.39 — isn’t that poor?” |
| Strongest answer | Linear weighted κ vs Rubric B shows **neither** rule nor LLM confidence replaces human evidence-strength judgement; high automated confidence still rarely equals Rubric A = yes. |
| Limitation | Single human label set; adjacent disagreements count less but agreement remains moderate. |
| Dissertation | Ch4 Table 4.3. |
| Examiner package | `confidence_comparison_results.json` → `metrics.*.weighted_kappa`. |
| Demo | Conceptual — confidence not shown as authority in UI. |

## 5. Why one model was used

| Field | Content |
| --- | --- |
| Likely question | “Why not GPT-4 / multiple models?” |
| Strongest answer | Feasibility case study with a frozen extraction run; contribution emphasises governance over model horse-race. Multi-model comparison is explicit future work. |
| Limitation | Results are model-conditioned; no claim of model-independence. |
| Dissertation | Ch1.4; Ch5 limitations / future work. |
| Examiner package | Reproducibility limits. |
| Demo | Freeze banner — no live model call. |

## 6. Why a second reviewer was not included

| Field | Content |
| --- | --- |
| Likely question | “Where is inter-rater reliability?” |
| Strongest answer | Single-reviewer validation acknowledged; dual coding deferred as first future-work item. Findings are structured feasibility, not independently rated population estimates. |
| Limitation | No κ between human raters. |
| Dissertation | Ch4 faithfulness caveat; Ch5. |
| Examiner package | Security/limits notes; n=60 caveats. |
| Demo | Human review panel labelled as author review outcomes. |

## 7. Why the Module 2 case study is useful

| Field | Content |
| --- | --- |
| Likely question | “Why this Inquiry / why only eight hearings?” |
| Strongest answer | Public, citable transcripts of core UK pandemic decision-making forums; enough volume (414) for stratified validation without claiming full-archive coverage. |
| Limitation | One jurisdiction / one module / eight hearings. |
| Dissertation | Ch1.1; Ch1.4. |
| Examiner package | Lineage / demo selection. |
| Demo | Provenance fields (hearing date, slug). |

## 8. Whether results generalise

| Field | Content |
| --- | --- |
| Likely question | “Will this work on any inquiry / any domain?” |
| Strongest answer | No generalisation claim beyond feasibility for this public-record journaling problem; cross-inquiry replication is future work. |
| Limitation | External validity untested. |
| Dissertation | Ch1.4; Ch5. |
| Examiner package | Reproducibility limits. |
| Demo | Scope labels on landing. |

## 9. Whether the system could be deployed

| Field | Content |
| --- | --- |
| Likely question | “Can UKHSA / a department use this tomorrow?” |
| Strongest answer | Not evaluated as production; would need access governance, multi-reviewer process, domain calibration, and explicit non-authority of candidates. |
| Limitation | No deployment study. |
| Dissertation | Ch1.4; Ch5 scaling conditions. |
| Examiner package | Security note. |
| Demo | “Not live, not deployed, not automatically authoritative.” |

## 10. Whether framework mapping is subjective

| Field | Content |
| --- | --- |
| Likely question | “Aren’t JEE/DQ just your opinion?” |
| Strongest answer | Yes — **human interpretive aids** after source validation using recognised frameworks; aggregates are purposive n=60 feasibility, not official WHO/DQ audits of UK performance. |
| Limitation | Single mapper; many insufficient_evidence / no_mapping outcomes. |
| Dissertation | Ch4 Table 4.4 commentary. |
| Examiner package | Audit E locator. |
| Demo | **phase1-246** warning box. |

## 11. Whether the system hallucinates

| Field | Content |
| --- | --- |
| Likely question | “Does it hallucinate?” |
| Strongest answer | Faithfulness review found exact/near (8), paraphrase (25), **materially unsupported/altered (20)**, and non-traceable (7) in n=60. Source availability ≠ meaning preservation (**phase1-090**). |
| Limitation | Not a corpus-wide hallucination rate; single reviewer. |
| Dissertation | Ch4 Table 4.5. |
| Examiner package | Audit E manifest counts. |
| Demo | **phase1-090**. |

## 12. What is genuinely novel

| Field | Content |
| --- | --- |
| Likely question | “What’s new?” |
| Strongest answer | Not a novel LLM architecture. Novel as MSc contribution: **operational separation** of generation, mechanical traceability, evidence strength, semantic faithfulness, journal validity and framework interpretation on a frozen public-inquiry case with examiner-reproducible artefacts. |
| Limitation | Builds on known LLM extraction risks and auditability literature. |
| Dissertation | Ch1.6; Ch2 gap; Ch5. |
| Examiner package | Full Wave 3/4 packages. |
| Demo | End-to-end offline examiner walkthrough. |

---

## Presentation claim → recovery trio

| If challenged on… | Point to slide | Then to |
| --- | --- | --- |
| Authority of outputs | S01 / S12 | Ch1.2 |
| Numbers | S06 | Evidence map / journal SHA |
| Wrong artefact | S07 | Demo 082 |
| Faithfulness | S08 / S06 | Demo 090 + Audit E |
| Frameworks | S08 | Demo 246 + Audit E |
| Limits | S10 | Ch5 / reproducibility limits |
