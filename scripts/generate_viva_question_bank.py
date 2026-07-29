#!/usr/bin/env python3
"""Generate Wave 6 question bank, anchors, and evidence index."""
from __future__ import annotations

import csv
from pathlib import Path

VIVA = Path(__file__).resolve().parents[1] / "docs" / "viva"


def main() -> None:
    qs: list[dict] = []

    def add(cat: str, diff: str, q: str, anchor: str, evidence: str, caveat: str, unsafe: str) -> None:
        qs.append(
            {
                "question_id": f"Q{len(qs) + 1:03d}",
                "category": cat,
                "difficulty": diff,
                "question": q,
                "answer_anchor": anchor,
                "evidence_reference": evidence,
                "admission_or_caveat": caveat,
                "unsafe_overclaim_to_avoid": unsafe,
            }
        )

    add("fundamentals", "foundational", "What problem did the dissertation address?", "Convert complex public inquiry text into auditable candidate decision-journal entries without treating LLM output as authoritative.", "Ch1 §§1.1–1.2", "Case-study scope only", "We solved pandemic decision-making")
    add("fundamentals", "foundational", "What was the exact research aim?", "Read exact Ch1 aim: design and evaluate an LLM-assisted method for traceable candidate decision-journal entries using Module 2 as case study.", "Ch1 §1.3", "Do not rewrite aim", "Aim was to verify government decisions")
    add("fundamentals", "foundational", "What were the research questions?", "No numbered RQs in Ch1; Aim + Objectives 1–6 are the formal framing.", "Ch1 §1.3", "Do not invent RQ1–RQn", "We had four RQs")
    add("fundamentals", "probing", "Why are public inquiry transcripts suitable?", "Public, citable, decision-rich discourse with mixed speech acts; reproducible corpus.", "Ch1.1", "One module/eight hearings", "Works for all inquiries")
    add("fundamentals", "probing", "Why is this an AI project rather than document processing?", "LLM generates structured candidates; contribution is governing those candidates.", "Ch3; Ch1.6", "Not a new base model", "Pure NLP parsing without LLM")
    add("fundamentals", "foundational", "What is the central contribution?", "Governed workflow separating machine candidates, automated checks, human validation and source evidence.", "Ch1.6; Ch5", "Not an auto-verified catalogue", "Production policy engine")
    add("fundamentals", "probing", "What is genuinely novel?", "Operational separation of constructs plus frozen examiner-auditable artefacts on this case — not SOTA extraction.", "Ch1.6", "Builds on known LLM risks", "First ever LLM on transcripts")
    add("fundamentals", "probing", "Why useful for policymaking?", "Supports institutional memory / retrospective review with inspectable route — not automated policy.", "Ch1.6", "Prototype only", "Ready for operational use")
    add("fundamentals", "foundational", "What does the system not claim to do?", "Not deployed; not authoritative decisions; not byte-identical regen; not multi-model generalisation.", "Ch1.4; reproducibility limits", "Keep list tight", "It verifies truth")

    add("methodology", "foundational", "Why clean and segment transcript text?", "Reduce noise; enable localisable chunks for provenance.", "Ch3", "May drop context", "Perfect cleaning")
    add("methodology", "probing", "Why seven-sentence chunks with overlap two?", "Balance context and localisation for quote anchoring.", "Ch3", "Boundary effects", "Universal optimum")
    add("methodology", "foundational", "Why a structured candidate schema?", "Forces decision/evidence/location fields for audit.", "Ch3", "May bias toward decision-shaped text", "Schema proves validity")
    add("methodology", "probing", "Why the temperature/prompt configuration?", "Favour reproducibility; Phase 1 notes emphasise low temperature.", "Ch3; structural reliability production_note", "Model-specific", "Config is optimal forever")
    add("methodology", "foundational", "How were stable IDs assigned?", "phase1-NNN identifiers in frozen journal enabling lineage.", "phase1_decision_journal.json", "Study-local IDs", "Global standard IDs")
    add("methodology", "probing", "How was deduplication handled?", "Non-destructive review flags rather than silent deletion.", "Ch3/Ch4 flags", "Heuristic flags", "All duplicates removed automatically")
    add("methodology", "foundational", "How is traceability_ok calculated?", "Mechanical link of generated statement to source material in chunk — not validity/faithfulness.", "journal totals; validate_traceability", "Approximation", "Hallucination detector")
    add("methodology", "adversarial", "Why freeze model output before evaluation?", "Separate generation from evaluation; prevent moving targets; lock SHA.", "journal SHA 814cc7c4…", "Historical snapshot", "Live API is identical")
    add("methodology", "foundational", "Why separate candidate generation and evaluation?", "Core governance contribution; avoids treating generation as acceptance.", "Ch1.6; Ch3", "Still one pipeline study", "Fully independent labs")
    add("methodology", "probing", "Why six manual decision excerpts?", "Bounded gold for triangulation and keyword baseline.", "App A; Table 4.2", "Not full-corpus labels", "Representative of 414")
    add("methodology", "probing", "Why n=42, n=50 and n=60?", "Different evaluation questions: taxonomy, stratified A/B, purposive frameworks/faithfulness.", "Ch3–Ch4", "Bounded feasibility", "One accuracy sample")
    add("methodology", "foundational", "Why stratified validation?", "Cover strata and surface No×High; not a probability sample of all 414.", "Ch4 §4.5", "Not universal rate", "Random population sample")
    add("methodology", "probing", "Why examine confidence separately?", "High automated confidence ≠ journal membership; compare to Rubric B.", "Table 4.3", "Moderate κ", "Confidence replaces humans")
    add("methodology", "foundational", "Why clustering?", "Navigational organisation of 414; size ≠ importance.", "Ch4 §4.6; 20 clusters", "Heuristic labels", "Clusters prove validity")
    add("methodology", "probing", "Why JEE and Decision Quality?", "Recognised interpretive frameworks after validated source.", "Ch4 Table 4.4", "Subjective mapping", "Official WHO scores")
    add("methodology", "foundational", "Why report-genre and structural reliability checks?", "Supplementary quality lenses (50/53; 49/50), not semantic validity.", "Ch4 §4.8", "Limited transfer", "Prove correctness")

    add("AI/LLM design", "probing", "Why one main model?", "Bounded feasibility case; contribution is workflow governance not horse-race.", "Ch1.4; Ch5", "Model-conditioned", "Model-independent")
    add("AI/LLM design", "adversarial", "Would another model reproduce the same journal?", "Unknown; not tested; no byte-identical claim even for same model live regen.", "reproducibility limits", "Future multi-model study", "Yes, identical")
    add("AI/LLM design", "adversarial", "Does one model weaken generalisability?", "Yes for model generalisation; claim is workflow feasibility in one case.", "Ch5", "Acknowledge", "Still general")
    add("AI/LLM design", "foundational", "Why are historical outputs frozen?", "Auditability and evaluation stability.", "journal freeze", "Snapshot", "Live always matches")
    add("AI/LLM design", "probing", "What would proper model comparison require?", "Same corpus, frozen configs, paired human labels, pre-registered metrics — future work.", "Ch5", "Not done here", "We already compared models")
    add("AI/LLM design", "adversarial", "Temperature zero removes all error.", "Reduces randomness not semantic/wrong-artefact errors.", "methods", "Still errors", "Zero error")

    add("evaluation", "foundational", "Why were there 414 candidates?", "Extractor over eight Module 2 hearings; frozen totals.decisions=414.", "journal totals.decisions", "Candidates ≠ accepted decisions", "414 verified decisions")
    add("evaluation", "foundational", "What does 351/414 traceability mean?", "Mechanical traceability pass count.", "totals.traceability_pass=351", "Not journal validity", "85% accuracy")
    add("evaluation", "adversarial", "What does 351/414 not mean?", "Not acceptance; not faithfulness; not Rubric A yes.", "Ch4; No×High", "Keep sharp", "Success rate")
    add("evaluation", "foundational", "What do 5 agreement, 10 silence and 0 dissonance indicate?", "Triangulation tags on six manuals: some matches, many silences, no direct conflicts tagged.", "Table 4.2", "Bounded excerpts", "Corpus-wide")
    add("evaluation", "probing", "Why keyword recall 1/6 while LLM agreement rows 5/6?", "Keyword baseline weak on manuals; LLM agreement-row recall higher on those six — not full IR over 414.", "App B; BASELINE_KEYWORD", "Agreement-row metric", "LLM always better everywhere")
    add("evaluation", "foundational", "Why were 21/50 items No × High?", "Most frequent A×B cell: strong quote support but not journal-valid.", "Fig 4.9; sample", "Stratified sample", "Universal 42%")
    add("evaluation", "adversarial", "Why is phase1-082 important?", "Centrepiece: procedural adjournment — High support, No validity.", "demo phase1-082", "One case", "Proves all High are wrong")
    add("evaluation", "foundational", "Why was rule weighted kappa 0.48?", "Linear weighted κ vs Rubric B; neither replaces human.", "confidence_comparison_results metrics", "Moderate", "Strong agreement")
    add("evaluation", "foundational", "Why was LLM weighted kappa 0.39?", "Same comparison for LLM confidence vs Rubric B.", "metrics.llm_vs_human_b", "Moderate", "Strong agreement")
    add("evaluation", "adversarial", "Are those agreement values acceptable?", "Acceptable as evidence automation is insufficient — not as strong reliability.", "Table 4.3", "Do not call strong", "Excellent reliability")
    add("evaluation", "foundational", "What do the 20 clusters show?", "Exploratory grouping for navigation.", "clustering_report n_clusters=20", "Not validity", "Policy importance ranking")
    add("evaluation", "foundational", "What do JEE 11/60 and Decision Quality 37/60 mean?", "Mapped counts in purposive n=60; interpretive.", "Audit E summaries", "Not performance scores", "UK preparedness grades")
    add("evaluation", "probing", "Why was the combined count 26/60?", "Most frequent combined cell: DQ mapped with JEE unmapped.", "crosstab unmapped×mapped=26", "Purposive", "Always true")
    add("evaluation", "foundational", "How should faithfulness 8/25/20/7 be interpreted?", "Exact/near 8; paraphrase 25; materially unsupported/altered 20; non-traceable 7.", "AUDIT_E_MANIFEST counts", "Single reviewer", "Hallucination rate for all 414")
    add("evaluation", "foundational", "What do report pilot 50/53 and structural reliability 49/50 establish?", "Supplementary report-pilot and structural checklist outcomes.", "REPORT_PILOT; structural summary", "Not semantic validity", "Full correctness")

    add("traceability", "adversarial", "Isn’t a highly supported quotation automatically a valid decision?", "No — Rubric B≠A; phase1-082.", "Ch4 §4.5; demo 082", "Rubrics author-defined", "Yes always")
    add("traceability", "probing", "Why did the model extract the wrong artefact?", "Hearing discourse contains decision-like procedural language; model tracked wording.", "phase1-082", "Prompting limits", "Model always fails")
    add("traceability", "adversarial", "Does this mean the model failed?", "Shows generation can succeed at wording while governance must reject membership — method working.", "082 teaching", "Not all cases", "Total failure")
    add("traceability", "probing", "Is the rubric subjective?", "Operationalised by author; single-reviewer limit acknowledged.", "Ch4/Ch5", "Need multi-rater", "Objective law")
    add("traceability", "adversarial", "Could better prompting eliminate No × High?", "May reduce but not guaranteed; wrong-artefact risk is structural in mixed discourse.", "Ch5", "Unproven", "Prompting solves all")
    add("traceability", "probing", "Why retain these candidates rather than delete them?", "Audit trail; teach governance; non-destructive flags.", "methods flags", "Storage cost", "Delete all No")
    add("traceability", "adversarial", "What governance control follows from this result?", "Human journal-validity gate cannot be replaced by quote strength alone.", "Ch5 governance", "Prototype", "Auto-accept High")

    add("faithfulness", "foundational", "Did the system hallucinate?", "Use faithfulness categories; do not collapse all failures into hallucination. 20/60 materially unsupported/altered in n=60.", "Table 4.5", "Not corpus rate", "Never hallucinated")
    add("faithfulness", "probing", "How often did it hallucinate?", "Do not give a single hallucination rate; report 8/25/20/7 categories for n=60.", "AUDIT_E_MANIFEST", "Single reviewer", "X% hallucination")
    add("faithfulness", "probing", "Is traceability_ok a hallucination detector?", "No — mechanical presence ≠ meaning.", "Ch4.5 vs 4.2", "Need faithfulness review", "Yes it is")
    add("faithfulness", "adversarial", "Can a quote be found while meaning is still altered?", "Yes — phase1-090 counsel question vs asserted decision.", "demo 090", "Purposive example", "Impossible")
    add("faithfulness", "foundational", "Why was a separate faithfulness review necessary?", "Traceability insufficient for summary meaning.", "Ch4 Table 4.5", "Single reviewer", "Redundant with traceability")
    add("faithfulness", "probing", "How could faithfulness evaluation be improved?", "Multi-rater labels; clearer taxonomy; larger samples — future work.", "Ch5", "Not done", "Already solved")

    add("governance and ethics", "foundational", "What are the policy risks of using an LLM here?", "Authoritative-looking wrong artefacts; meaning drift; misuse without oversight.", "Ch1.2; Ch5", "Prototype", "No risk")
    add("governance and ethics", "adversarial", "Could generated candidates mislead officials?", "Yes if accepted without human review — hence separation.", "governance defence", "Need controls", "Safe to publish raw")
    add("governance and ethics", "foundational", "What human oversight is required?", "Validity, strength, faithfulness; mapping after source validation.", "Ch3–Ch4", "Single-reviewer now", "None needed")
    add("governance and ethics", "probing", "Could the system be deployed now?", "No — research prototype.", "Ch1.4", "List deployment gates", "Yes tomorrow")
    add("governance and ethics", "probing", "What additional validation would deployment require?", "Multi-reviewer, access control, logging, change governance, domain calibration.", "Ch5", "Not implemented", "UI only")
    add("governance and ethics", "foundational", "How does the workflow support accountability?", "Visible separation of source/machine/automated/human layers.", "Ch1.6", "Prototype", "Replaces accountability")

    add("reproducibility", "foundational", "Can the complete study be reproduced offline?", "Claim verification and demo yes; live generation needs API; PDFs may need download.", "examiner package limits", "Not full byte-identical generation", "Everything offline including regen")
    add("reproducibility", "probing", "Which components require an OpenAI API key?", "Live regeneration paths — not offline demo/frozen checks.", "repro limits", "Cost/privacy", "No API ever used")
    add("reproducibility", "adversarial", "Why should the examiner trust untracked historical run artefacts?", "Prefer frozen journal hashes; runs are historical provenance only.", "Wave3 limits", "Gap acknowledged", "Runs override journal")
    add("reproducibility", "foundational", "How were hashes used?", "Lock journal, decks, demo evidence, Audit E paths.", "SHA256SUMS files", "Human labels still needed", "Hashes prove truth")
    add("reproducibility", "probing", "How was Audit E authoritative-path ambiguity resolved?", "Canonical locator — one path per claim.", "AUDIT_E_CANONICAL_LOCATOR.md", "Aliases exist", "Any file is fine")
    add("reproducibility", "foundational", "Why were raw transcripts and PDFs not committed?", "Bulk/packaging; public sources citable; extracts suffice.", "security note", "Examiner may download", "Hidden data")
    add("reproducibility", "probing", "What does the baseline tag protect?", "Corrected Wave 6C dissertation freeze for distinction waves.", "baseline-wave6c-corrected-2026-07-28", "Historical process", "All history immutable forever")

    add("contribution and novelty", "adversarial", "Is the novelty merely using an LLM on transcripts?", "No — governed separation and No×High empirical lesson.", "Ch1.6", "Not SOTA model", "Yes only LLM use")
    add("contribution and novelty", "probing", "How does this differ from summarisation / RAG / IE?", "Structured candidates + validity/faithfulness/framework layers + freeze.", "contribution doc", "Overlaps exist", "Completely unique field")
    add("contribution and novelty", "foundational", "What is the single most important finding?", "Quote support ≠ journal membership (No×High / 082).", "Ch4 §4.5", "One study", "Universal law")
    add("contribution and novelty", "probing", "What would be publishable from this work?", "Governed extraction evaluation + wrong-artefact finding + faithfulness taxonomy case study.", "Ch5", "Needs peer review", "Ready Nature paper")

    add("limitations", "foundational", "Why was a second reviewer not included?", "MSc feasibility; rubrics+freeze for auditability; dual coding future.", "Ch5", "No IRR", "Supervisor was second rater")
    add("limitations", "adversarial", "Does moderate kappa kill the thesis?", "No — it supports the claim that automation cannot replace humans.", "Table 4.3", "Still limited", "κ proves success")
    add("limitations", "probing", "Why no multi-model comparison?", "Scope; future work; one-model bound stated.", "Ch5", "Weakens model generalisation", "Unnecessary")
    add("limitations", "foundational", "Does one inquiry case study limit external validity?", "Yes — stated in Ch1.4; cross-inquiry replication future.", "Ch1.4", "Acknowledge", "Fully general")

    add("deployment", "adversarial", "Isn’t this ready if the demo works?", "Demo is frozen inspection aid; not production authority.", "demo freeze banner", "Need deployment study", "Demo=deployed")
    add("deployment", "probing", "Who should approve journal entries?", "Human role with clear criteria; not the model.", "governance defence", "Org-specific", "Auto-approve High")
    add("deployment", "foundational", "What should be logged in a real deployment?", "Candidate, source, checks, reviewer, outcome, model/prompt version.", "governance defence", "Not implemented", "Already logged in production")

    add("presentation-specific", "foundational", "Why ≤12 slides / 15–20 minutes?", "EEEM004 handbook requirements.", "ProjectHandbook2025-26", "Q&A length unknown", "Officially exactly 15")
    add("presentation-specific", "probing", "Why is the live demo optional?", "Handbook assesses demo if present; presentation complete without it.", "handbook checklist; DEMO_CUE_CARD", "≤2 min if used", "Demo mandatory")
    add("presentation-specific", "adversarial", "If time is short what do you cut?", "S05/S08/S11 and demo; never omit 082 centrepiece and contribution/close.", "storyboard 10-min model", "Planning cuts", "Cut the centrepiece")
    add("presentation-specific", "foundational", "What files do you open if asked for evidence?", "Evidence map, journal totals, demo 082/090, Audit E locator.", "docs/examiner_evidence", "Paths may be hash-locked", "Memory only")

    add("statistics", "foundational", "What is weighted kappa here?", "Linear weighted κ treating adjacent Rubric B disagreements as less severe.", "Table 4.3 methods", "Single label set", "Unweighted only")
    add("statistics", "probing", "Why do exact agreement and kappa differ?", "Agreement is raw match rate; κ adjusts for chance / ordinal structure.", "Table 4.3", "Prevalence effects possible", "They must match")
    add("statistics", "adversarial", "Why not report p-values or confidence intervals?", "Not computed/reported in study — will not invent.", "results chapters", "Descriptive framing", "Secret significant results")
    add("statistics", "probing", "Why is 21/50 important without being a universal rate?", "Modal cell in stratified sample teaching construct separation.", "Fig 4.9", "Not population rate", "42% of all decisions")
    add("statistics", "adversarial", "Class imbalance makes kappa meaningless.", "Prevalence can affect κ; still reported with exact agreement; interpretation cautious.", "Table 4.3", "No CI", "Meaningless so ignore")

    add("data quality", "foundational", "What speech-act problem exists in transcripts?", "Questions, procedure, advocacy mixed with measures.", "Ch1.2", "Genre limit", "Clean decisions only")
    add("data quality", "probing", "How do review flags help quality?", "Non-destructive navigation of procedural/duplicate risks.", "Ch4 flags", "Heuristic", "Perfect filter")

    add("adversarial", "adversarial", "Haven’t you just built a summariser with extra labels?", "No — journal validity gate and No×High finding are central.", "Ch4; contribution", "Overlaps with IE", "Just summariser")
    add("adversarial", "adversarial", "Your human labels are circular because you designed the rubrics.", "Rubrics are explicit and auditable; independence limit acknowledged; future multi-rater.", "Ch5", "Single author", "Fully independent")
    add("adversarial", "adversarial", "Without IRR how can examiners trust n=50?", "As structured case-study evaluation with frozen IDs — not as population estimate.", "Ch4 caveat", "Need IRR later", "Equivalent to multi-rater")
    add("adversarial", "adversarial", "Framework mapping is story-telling.", "Interpretive by design; after source validation; not performance proof — phase1-246 warning.", "Ch4; demo 246", "Subjective", "Objective scoring")
    add("adversarial", "adversarial", "If regen changes outputs, what is science here?", "Frozen artefact evaluation of a workflow and failure modes; not live leaderboard.", "journal freeze", "Model drift risk", "Regen identical")
    add("adversarial", "adversarial", "Why should policymakers care about phase1-082?", "Shows automation can look right and still be wrong artefact — oversight design implication.", "demo 082", "One case", "All policy decisions")
    add("adversarial", "adversarial", "You hid weak kappa behind narrative.", "κ reported plainly; used to argue against replacement of humans.", "Table 4.3", "Still moderate", "Strong κ")
    add("adversarial", "adversarial", "Git late means results untrustworthy.", "Baseline freeze + hashes + examiner package mitigate; process debt acknowledged.", "baseline tag", "Historical gap", "Git timing irrelevant")

    assert len(qs) >= 80, len(qs)
    adv = sum(1 for q in qs if q["difficulty"] == "adversarial")
    assert adv >= 20, adv

    lines = [
        "# Viva question bank",
        "",
        "**Important:** Candidate rehearsal questions only — **not** official examiner questions, mark schemes, or recorded feedback.",
        "",
        f"Total questions: **{len(qs)}** · Adversarial: **{adv}**",
        "",
        "| ID | Category | Difficulty | Question | Concise answer anchor | Evidence | Caveat | Unsafe overclaim |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for q in qs:
        def esc(s: str) -> str:
            return s.replace("|", "\\|")

        lines.append(
            "| "
            + " | ".join(
                esc(q[k])
                for k in (
                    "question_id",
                    "category",
                    "difficulty",
                    "question",
                    "answer_anchor",
                    "evidence_reference",
                    "admission_or_caveat",
                    "unsafe_overclaim_to_avoid",
                )
            )
            + " |"
        )
    (VIVA / "VIVA_QUESTION_BANK.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    anchors = [
        "# Viva answer anchors",
        "",
        "Short prompts for high-frequency and adversarial challenges.",
        "Hierarchy: data → inference → uncertainty → future work.",
        "",
    ]
    for q in qs:
        if q["difficulty"] in ("adversarial", "probing") or q["category"] in (
            "fundamentals",
            "evaluation",
            "traceability",
            "faithfulness",
        ):
            anchors.extend(
                [
                    f"## {q['question_id']} — {q['question']}",
                    f"- **Direct:** {q['answer_anchor']}",
                    f"- **Evidence:** {q['evidence_reference']}",
                    f"- **Caveat:** {q['admission_or_caveat']}",
                    f"- **Avoid:** {q['unsafe_overclaim_to_avoid']}",
                    "",
                ]
            )
    (VIVA / "VIVA_ANSWER_ANCHORS.md").write_text("\n".join(anchors) + "\n", encoding="utf-8")

    with (VIVA / "VIVA_QUESTION_BANK.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(qs[0].keys()))
        w.writeheader()
        w.writerows(qs)

    rows = []

    def erow(topic, qid, claim, diss, src, key, sid, eh, human, lim):
        rows.append(
            {
                "topic": topic,
                "question_id": qid,
                "answer_claim": claim,
                "dissertation_location": diss,
                "authoritative_source": src,
                "source_key_or_row": key,
                "stable_id": sid,
                "evidence_hash": eh,
                "human_adjudicated": human,
                "limitation": lim,
                "verification_status": "verified_map",
            }
        )

    erow("corpus", "Q032", "414 candidates", "Ch4 T4.1", "data/manifests/phase1_decision_journal.json", "totals.decisions=414", "phase1_journal", "814cc7c47a9f75bfc0a6c7b693feec7073e59131398d89fab7c9111fbb2e5e06", "no", "not accepted decisions")
    erow("corpus", "Q033", "351/414 traceability", "Ch4 T4.1", "data/manifests/phase1_decision_journal.json", "totals.traceability_pass=351", "phase1_journal", "814cc7c47a9f75bfc0a6c7b693feec7073e59131398d89fab7c9111fbb2e5e06", "no", "not validity")
    erow("triangulation", "Q035", "5/10/0", "Ch4 T4.2", "configs/annotations/excerpts/", "agreement/silence/dissonance", "manual_6", "see_examiner_SHA256SUMS", "yes", "six excerpts")
    erow("baseline", "Q036", "keyword 1/6", "App B", "docs/BASELINE_KEYWORD.md", "1/6", "keyword", "hash_only_doc", "yes", "not full IR")
    erow("baseline", "Q036b", "LLM 5/6", "App B", "docs/examiner_evidence/EXAMINER_EVIDENCE_MAP.md", "5/6 agreement-row", "llm_agree", "hash_only_map", "yes", "agreement-row")
    erow("n50", "Q037", "21/50 no×high", "Ch4 §4.5", "configs/evaluation/confidence_validation_sample.json", "A=no B=high", "n50", "9d74936c490de586c126bd4ad059cc20345702655a3a9f3b2455677d195d8169", "yes", "stratified")
    erow("kappa", "Q039", "rule κ 0.48", "Ch4 T4.3", "configs/evaluation/confidence_comparison_results.json", "metrics.rule_vs_human_b.weighted_kappa=0.4813", "kappa_rule", "e197b7f28d2bb08ab2dc3160aacf2cccd528938deebdf5298647a8a502103852", "yes", "moderate")
    erow("kappa", "Q040", "LLM κ 0.39", "Ch4 T4.3", "configs/evaluation/confidence_comparison_results.json", "metrics.llm_vs_human_b.weighted_kappa=0.3927", "kappa_llm", "e197b7f28d2bb08ab2dc3160aacf2cccd528938deebdf5298647a8a502103852", "yes", "moderate")
    erow("kappa", "Q039b", "rule exact agreement 0.80", "Ch4 T4.3", "configs/evaluation/confidence_comparison_results.json", "metrics.rule_vs_human_b.exact_agreement=0.8", "exact_rule", "e197b7f28d2bb08ab2dc3160aacf2cccd528938deebdf5298647a8a502103852", "yes", "not kappa")
    erow("kappa", "Q040b", "LLM exact agreement 0.76", "Ch4 T4.3", "configs/evaluation/confidence_comparison_results.json", "metrics.llm_vs_human_b.exact_agreement=0.76", "exact_llm", "e197b7f28d2bb08ab2dc3160aacf2cccd528938deebdf5298647a8a502103852", "yes", "not kappa")
    erow("clusters", "Q042", "20 clusters", "Ch4 §4.6", "data/manifests/phase1_clustering_report.json", "n_clusters=20", "clusters", "08a6bf8d48191978403bcaa146c6714b4fe2c7dc38ffd16a2b5c469ccbedaa8c", "no", "navigational")
    erow("jee", "Q043", "JEE 11/60", "Ch4 T4.4", "outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/AUDIT_E_JEE_SUMMARY.csv", "mapped=11", "audit_e", "499b82c045713821f8610788b395b4ef6f82342b1577bbc6380d00fbfd326200", "yes", "interpretive")
    erow("dq", "Q043b", "DQ 37/60", "Ch4 T4.4", "outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/AUDIT_E_DQ_SUMMARY.csv", "mapped=37", "audit_e", "2bdd445b3fa7782ac831e626d862d5661feab7c0c6e253302afd75725784c049", "yes", "interpretive")
    erow("combined", "Q044", "26/60 combined", "Ch4 T4.4", "outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/crosstabs/AUDIT_E_jee_vs_dq_mapped.csv", "unmapped×mapped=26", "audit_e", "773724149e29f2314e6d7b9c28ab3006ba73cb010322e17e8c722496c691f51d", "yes", "purposive")
    erow("faithfulness", "Q045", "8/25/20/7", "Ch4 T4.5", "outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/AUDIT_E_MANIFEST.json", "traceability_category_counts", "audit_e", "8262948f55a04950983dcc146073a51822422237fdc8d92abf966c377c4bcd20", "yes", "single reviewer")
    erow("pilot", "Q046", "50/53", "Ch4 §4.8", "docs/REPORT_PILOT.md", "50/53", "report_pilot", "hash_only_doc", "partial", "supplementary")
    erow("structural", "Q046b", "49/50", "Ch4 §4.8", "configs/evaluation/structural_reliability_results.json", "summary.structural_pass_count=49", "structural", "8c9ce78f9eecfe0165f5a0ccda84670f3a6c4bb4777f2b45d3a848b093c07eba", "no", "not semantic")
    erow("demo", "Q038", "phase1-082 No×High", "Ch4; demo", "demo/evidence/phase1-082.json", "rubric_a=no rubric_b=high", "phase1-082", "9b131dc2b403f51a3a1de366ee56793c6ff255986a57e683d525297963cca2c0", "yes", "centrepiece")
    erow("demo", "Q054", "phase1-090 faithfulness", "Ch4 T4.5", "demo/evidence/phase1-090.json", "materially_unsupported_or_altered", "phase1-090", "7e94f16177c4ce820f956d64d27dfd9a1798e91627cb7e372ac43b0ba25ed430", "yes", "purposive")
    erow("demo", "demo-016", "phase1-016 Yes×High", "demo", "demo/evidence/phase1-016.json", "yes/high", "phase1-016", "e5d28326427f4108ed97922bf444a4467ce807e4aa198277e2ba46d6cd3a2953", "yes", "alignment")
    erow("demo", "demo-246", "phase1-246 JEE/DQ", "demo", "demo/evidence/phase1-246.json", "P3 + commitment_to_follow_through", "phase1-246", "30e2cf20540de86b618cc3790b006148fb50905e3c51b35c404dab88099440ee", "yes", "interpretive")

    with (VIVA / "VIVA_EVIDENCE_INDEX.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"questions={len(qs)} adversarial={adv} evidence_rows={len(rows)}")


if __name__ == "__main__":
    main()
