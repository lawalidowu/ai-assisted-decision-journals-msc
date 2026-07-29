"""Prompt packs for language-edit modes."""

from __future__ import annotations

from typing import Any

MODES = (
    "language_simplification",
    "policy_framing",
    "clustering_clarification",
)

SHARED_CONSTRAINTS = """
Shared constraints (all modes):
- Preserve the author's meaning, academic argument, evidence, limitations and voice.
- Do not add, remove or alter claims, methods, findings, citations, numbers,
  terminology or scope.
- Do not make the writing informal.
- Do not introduce IHR, Decision Quality taxonomy mapping, or any ontology not
  already present in the text.
- Preserve Markdown markers exactly where present (**bold**, *italic*, `code`,
  links, [[FIGURE:...]]).
- Preserve citations, numbers, percentages, dates, model names, dataset sizes,
  figure/table/section references, statistical symbols and defined technical terms.
- Use British English spelling (judgement, emphasise, organisation, prioritise).
- Neighbouring context paragraphs are READ-ONLY. Revise ONLY the listed target IDs.
- Return ONLY valid JSON matching the schema. No markdown fences.
""".strip()

MODE_INSTRUCTIONS = {
    "language_simplification": """
Mode: language_simplification
Improve clarity and readability while preserving meaning, evidence, academic
tone, limitations, citations, numbers, terminology and scope.

Hard preservation rules:
- Preserve methodological and scope qualifiers exactly unless the revised
  sentence clearly retains their full meaning. Required examples include:
  purposively selected; stratified sample; within the sample / validation
  sample; faithful extraction; frozen; canonical; non-destructive;
  supplementary; exploratory; heuristic; pilot scale.
- Do not replace “faithful” with “accurate” where evidence fidelity versus
  journal validity matters.
- Preserve explicit limitations and population/sample boundaries. Do not
  broaden a finding from “within the validation sample” (or similar) to an
  unqualified general finding.
- Preserve the meaning of “interleaved”: the difficulty arises because policy
  decisions, procedure, questions and narrative are mixed together, not merely
  because they are all present.
- Prefer genuine simplification with common verbs (combines not integrates;
  uses not employs; shows not demonstrates; helps not aids). Do not replace
  clear wording with equally formal synonyms.
- Do not make cosmetic synonym substitutions (for example define→outline,
  separates→distinguishes, produce→create) when the original wording is
  already clear.
- If the paragraph is already clear, return the original paragraph unchanged
  and say so in change_summary.
- Preserve “whether” in formal research questions and investigation statements;
  do not replace it with “if”.
- If simplification would require removing methodological precision, return
  the original paragraph unchanged and say so in change_summary.

Self-check fields (all must be true, or leave the paragraph unchanged):
- methodological_qualifiers_preserved
- scope_preserved
- british_english_used
- technical_distinctions_preserved
""".strip(),
    "policy_framing": """
Mode: policy_framing
Strengthen the dissertation’s explanation of why the work matters for
retrospective policy review, public-sector accountability and organisational
learning from public health emergencies. This is NOT a general rewrite and NOT
a second language-simplification pass. Preserve the approved wording unless a
targeted policy-framing change adds clear and necessary meaning.

Objectives (only where already supported by the text):
- Make clearer that the system supports retrospective examination of how
  decisions were reached, documented and reviewed.
- Explain relevance of structured, traceable candidate records to institutional
  accountability, organisational learning, preparedness for future public
  health emergencies, and human review of large public-record collections.
- Clarify that policy value arises from the governed process: traceable
  extraction; separation of candidate generation from evaluation; human
  validation; non-destructive review; and thematic navigation.
- Preserve the AI / information-extraction identity; policy relevance must
  complement, not replace, the technical contribution.
- Preserve the UK COVID-19 Inquiry Module 2 and MSc pilot boundaries.

Hard prohibitions — do NOT claim or imply that the dissertation:
- produces a verified catalogue of UK government pandemic decisions;
- evaluates whether the underlying policy decisions were good or bad;
- establishes causal explanations for pandemic outcomes;
- demonstrates improved policy quality or emergency preparedness;
- provides real-time policy or decision support;
- provides a deployment-ready system;
- replaces inquiry analysts, policymakers or human judgement;
- establishes corpus-wide prevalence from the validation sample;
- proves the genre-blindness mechanism;
- treats cluster labels as a verified policy taxonomy;
- directly improves future emergency decisions;
- generalises beyond the pilot evidence.

Preserve these distinctions exactly:
- candidate entries vs verified policy decisions;
- extraction quality vs journal validity;
- evidence strength vs journal validity;
- faithful extraction vs correct artefact classification;
- human review support vs automated decision-making;
- retrospective accountability vs real-time policy support;
- organisational-learning potential vs demonstrated policy impact;
- pilot findings vs corpus-wide conclusions;
- findings vs interpretations and hypotheses;
- heuristic cluster labels vs verified policy ontology;
- future proposals vs demonstrated remedies;
- demonstrated findings vs possible future application.

Appropriate additions may refer to: making decision evidence easier to locate
and review; examining how decisions were recorded and justified; helping
reviewers identify patterns, omissions and questions requiring further review;
supporting institutional memory; creating an auditable basis for human-led
organisational learning; potential relevance to future emergency preparedness
as a bounded implication (not a demonstrated outcome).

Chapter 5 section guidance (when editing discussion paragraphs):
- Section 5.1: strengthen interpretation of why findings matter for
  accountability and human-led review; do not add policy wording to every
  paragraph; do not interrupt quantitative result reporting with repetitive
  policy statements.
- Section 5.2: primary policy-framing target; keep methodological, technical
  and policy contributions distinct; explain the value of traceability, frozen
  artefacts, dual rubrics and thematic navigation for human-led review; retain
  that the output is not a verified policy catalogue; express future
  preparedness only as a possible implication.
- Section 5.3: preserve all limitations; make clear how limitations constrain
  policy and organisational-learning claims; do not weaken caveats on pilot
  scale, sole annotation, corpus scope, clustering or discourse tags; change
  only where policy framing genuinely improves the limitation discussion.
- Do not edit Opening or Section 5.4 in this mode when those blocks are
  outside the target set.

Do not add: IHR or Decision Quality taxonomies; new experiments, results,
models, datasets or methods; unsupported citations; CPHIA/publication plans;
clustering clarification; new cluster labels; causal or deployment claims.

Editing discipline:
- Make only targeted changes that add genuine policy meaning.
- Do not make cosmetic synonym substitutions.
- Avoid repetitive insertion of the same accountability or organisational
  learning phrases across consecutive paragraphs.
- If the paragraph already adequately frames policy relevance, return it
  unchanged and say so in change_summary.
- Prefer common verbs and clear academic English; use British English.
- Preserve citations, numbers, dates, percentages, symbols, protected
  terminology, model names, artefact names and cross-references.
- Preserve methodological and scope qualifiers.
- Preserve Markdown structure.
- Do not remove technical detail needed to understand the AI contribution.
- Do not convert cautious claims into definitive claims.
- Do not invent new empirical findings; framing must stay within what the
  dissertation already supports.
""".strip(),
    "clustering_clarification": """
Mode: clustering_clarification
Clarify the actual heuristic-label assignment process, explain why semantic
concepts may overlap across clusters, and state that clustering supports
navigation rather than forming a mutually exclusive ontology. Do not invent
steps that were not performed.
Use British English. Preserve methodological and scope qualifiers.
""".strip(),
}

JSON_SCHEMA_INSTRUCTION = """
Return this JSON object:
{
  "mode": "<mode name>",
  "revisions": [
    {
      "paragraph_id": "<id>",
      "original_text": "<exact original markdown paragraph>",
      "revised_text": "<revised markdown paragraph or identical if unchanged>",
      "change_summary": "<short description of wording changes>",
      "meaning_changed": false,
      "new_claim_added": false,
      "methodological_qualifiers_preserved": true,
      "scope_preserved": true,
      "british_english_used": true,
      "technical_distinctions_preserved": true
    }
  ]
}

Include every target paragraph_id exactly once. Do not omit any target ID.
If no safe edit is possible without losing methodological precision, or if the
paragraph is already clear, set revised_text equal to original_text and say so
in change_summary.
All boolean fields must be present. Any false self-check must correspond to
leaving the paragraph unchanged OR will cause automated rejection.
""".strip()


def build_batch_prompt(
    *,
    mode: str,
    targets: list[dict[str, Any]],
    context_by_id: dict[str, dict[str, list[dict]]],
) -> str:
    if mode not in MODE_INSTRUCTIONS:
        raise ValueError(f"Unknown mode: {mode}")

    parts = [
        MODE_INSTRUCTIONS[mode],
        SHARED_CONSTRAINTS,
        JSON_SCHEMA_INSTRUCTION,
        f"mode = {mode}",
        "",
        "TARGET PARAGRAPHS (revise these):",
    ]
    for t in targets:
        pid = t["paragraph_id"]
        ctx = context_by_id.get(pid, {})
        before = ctx.get("before") or []
        after = ctx.get("after") or []
        parts.append(f"--- target_id: {pid} ---")
        if before:
            parts.append("context_before (read-only):")
            for b in before:
                parts.append(f"  [{b.get('block_type')}] {b.get('text')}")
        parts.append("original_text:")
        parts.append(t["text"])
        if after:
            parts.append("context_after (read-only):")
            for a in after:
                parts.append(f"  [{a.get('block_type')}] {a.get('text')}")
        parts.append("")
    return "\n".join(parts)
