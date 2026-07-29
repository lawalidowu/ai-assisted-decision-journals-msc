"""Slide content for primary (12) and fallback (8) examiner decks — Wave 5B."""
from __future__ import annotations

AIM = (
    "To design and evaluate an LLM-assisted method for creating traceable "
    "candidate decision-journal entries from complex public records, using "
    "UK COVID-19 Inquiry Module 2 transcripts as a case study."
)

MAIN_QUESTION = (
    "Can an LLM-assisted workflow produce useful, auditable decision-journal "
    "candidates from public inquiry transcripts without treating generated text "
    "as authoritative evidence?"
)

CLOSING = (
    "The system does not replace authoritative inquiry evidence or human policy "
    "judgement. It makes the route from source evidence to machine-generated "
    "candidate and human interpretation inspectable and auditable."
)

CASE_082 = {
    "id": "phase1-082",
    "decision": "The hearing will resume at 10 o'clock tomorrow.",
    "source_quote": "The hearing adjourned until 10 am on Friday, 1 December 2023",
    "traceability_ok": True,
    "rubric_a": "No",
    "rubric_b": "High",
    "flag": "procedural",
    "hash": "9b131dc2b403f51a3a1de366ee56793c6ff255986a57e683d525297963cca2c0",
    "teaching": "Quotation support does not by itself establish decision-journal validity.",
}

CASES_SUPPORT = [
    {
        "id": "phase1-016",
        "label": "Yes × High",
        "point": "Traceability and journal validity can align.",
        "hash": "e5d28326427f4108ed97922bf444a4467ce807e4aa198277e2ba46d6cd3a2953",
    },
    {
        "id": "phase1-090",
        "label": "Materially unsupported / altered",
        "point": "Source availability ≠ preserved meaning.",
        "hash": "7e94f16177c4ce820f956d64d27dfd9a1798e91627cb7e372ac43b0ba25ed430",
    },
    {
        "id": "phase1-246",
        "label": "JEE P3 + DQ commitment",
        "point": "Framework labels are interpretive aids after validation — not performance praise.",
        "hash": "30e2cf20540de86b618cc3790b006148fb50905e3c51b35c404dab88099440ee",
    },
]

# Speaker seconds for primary timing (~15 min)
PRIMARY_SECONDS = {
    "S01": 45,
    "S02": 60,
    "S03": 75,
    "S04": 90,
    "S05": 90,
    "S06": 120,
    "S07": 120,
    "S08": 90,
    "S09": 60,
    "S10": 75,
    "S11": 45,
    "S12": 60,
}

FALLBACK_IDS = ["S01", "S02", "S03", "S04", "S06", "S07", "S09", "S12"]
FALLBACK_SECONDS = {
    "S01": 40,
    "S02": 55,
    "S03": 55,
    "S04": 70,
    "S06": 100,
    "S07": 110,
    "S09": 55,
    "S12": 115,  # limitations folded here
}

SLIDES = {
    "S01": {
        "title": "Generated text is not authoritative evidence",
        "claim": (
            "This talk evaluates a governed workflow that keeps machine candidates, "
            "automated checks, human validation and source evidence visibly separate — "
            "not a deployed decision engine."
        ),
        "evidence_label": "EEEM004 viva · frozen research artefact",
        "notes": (
            "Open with the claim. Show freeze banner. Do not preview every result.\n"
            "Transition: Why is that distinction necessary?\n"
            "If late: skip chips narration."
        ),
        "caveat": "Not live, not deployed, not automatically authoritative.",
    },
    "S02": {
        "title": "Inquiry transcripts hide decisions in long, mixed discourse",
        "claim": (
            "Public inquiry text holds decision evidence that is lengthy, dispersed "
            "and easy to mis-extract as if authoritative."
        ),
        "bullets": [
            "Agreements sit beside questions and procedure.",
            "“Decision” language is mixed and dispersed.",
            "Naïve LLM summaries can look authoritative.",
        ],
        "evidence_label": "Dissertation Ch1 §§1.1–1.2",
        "notes": (
            "Agreements sit beside questions, procedure and narrative.\n"
            "Transition: So what did this project set out to do?\n"
            "If late: one sentence on mixed speech acts."
        ),
        "caveat": "Module 2 is a case study, not the sole purpose.",
    },
    "S03": {
        "title": "Aim: traceable candidates under human oversight",
        "claim": AIM,
        "question": MAIN_QUESTION,
        "objectives": [
            "1 Develop source-linked extraction",
            "2 Evaluate on eight hearings",
            "3 Freeze 414-candidate journal",
            "4 Validate n=50 validity/strength",
            "5 Organise + n=60 interpret/faithfulness",
            "6 Examine limits and scaling",
        ],
        "evidence_label": "Ch1 §1.3 exact aim (no numbered RQs)",
        "notes": (
            "Read the exact aim. State the main question.\n"
            "No numbered RQs in Chapter 1 — Aim + Objectives 1–6.\n"
            "If late: aim + question only."
        ),
        "caveat": "Do not rewrite the aim into a stronger claim.",
    },
    "S04": {
        "title": "Generation, checks, human review and source stay separate",
        "claim": (
            "Later stages do not retrospectively turn machine-generated text into "
            "authoritative evidence."
        ),
        "stages": [
            ("Public inquiry source", "source"),
            ("Source processing", "auto"),
            ("LLM candidate generation", "machine"),
            ("Automated traceability", "auto"),
            ("Frozen reference dataset", "machine"),
            ("Human review", "human"),
            ("Framework interpretation", "human"),
        ],
        "evidence_label": "Ch3 methods · Wave 4 workflow",
        "notes": (
            "Walk left to right once. Pause on frozen reference dataset.\n"
            "Transition: How was that evaluated?\n"
            "If late: emphasize separate colours only."
        ),
        "caveat": "Research prototype — not production deployment.",
    },
    "S05": {
        "title": "Evaluation is layered, not a single accuracy number",
        "claim": (
            "Bounded lenses answer different questions — none alone is “system accuracy”."
        ),
        "layers": [
            "6 manuals",
            "n=42 taxonomy",
            "n=50 stratified",
            "confidence κ",
            "20 clusters",
            "n=60 JEE/DQ",
            "faithfulness",
            "50/53 · 49/50 pilots",
        ],
        "evidence_label": "Examiner evidence map · Ch3–Ch4",
        "notes": (
            "List lenses quickly. Explicit: no single F1.\n"
            "Transition: Headline findings next.\n"
            "Removed in 10-minute deck."
        ),
        "caveat": "Do not report a single overall accuracy.",
    },
    "S06": {
        "title": "Traceable candidates are common; journal-ready ones are not",
        "claim": "Pass rates ≠ acceptance. no × high and moderate κ matter more than volume.",
        "groups": [
            {
                "name": "Scale & traceability",
                "items": [
                    ("414", "candidates"),
                    ("351/414", "traceability pass"),
                    ("1/6 vs 5/6", "keyword vs LLM"),
                ],
            },
            {
                "name": "Validity ≠ evidence strength",
                "items": [
                    ("21/50", "no × high"),
                    ("0.48", "rule κ vs B"),
                    ("0.39", "LLM κ vs B"),
                ],
            },
            {
                "name": "Framework & faithfulness",
                "items": [
                    ("11/60", "JEE mapped"),
                    ("37/60", "DQ mapped"),
                    ("8/25/20/7", "faithfulness"),
                ],
            },
        ],
        "evidence_label": "Frozen journal · n=50 · Audit E n=60",
        "notes": (
            "Lead with 351/414 and 21/50. Then κ and faithfulness.\n"
            "10-min: one line — layered eval, no single F1.\n"
            "If late: only 414, 351/414, 21/50, κ pair."
        ),
        "caveat": "Candidates are not accepted decisions.",
    },
    "S07": {
        "title": "Quote support ≠ journal membership (phase1-082)",
        "claim": CASE_082["teaching"],
        "case": CASE_082,
        "evidence_label": "Case phase1-082 · n=50 theme",
        "notes": (
            "Read candidate and quote. A=No, B=High, procedural.\n"
            "Pause after teaching line.\n"
            "Optional ≤2 min demo only if ahead of time.\n"
            "If late: teaching line only."
        ),
        "caveat": "Extraction tracked the wording; human criterion rejected journal membership.",
    },
    "S08": {
        "title": "Alignment, faithfulness failure and interpretive mapping",
        "claim": "Three verified contrasts; detail remains in the offline demo if requested.",
        "cases": CASES_SUPPORT,
        "evidence_label": "Wave 4 demo cases 016 · 090 · 246",
        "notes": (
            "20–25s per card. Warn that JEE/DQ are interpretive.\n"
            "Removed in 10-minute deck.\n"
            "If late: name IDs only."
        ),
        "caveat": "Framework mapping is not a judgement that performance was good.",
    },
    "S09": {
        "title": "Contribution is governance of the AI–source–human route",
        "claim": "Not a new SOTA extraction algorithm — a governed review process.",
        "blocks": [
            ("Methodological", "Link candidates to sources; separate validity, strength and faithfulness."),
            ("Artefact", "Fixed 414-entry journal plus offline examiner demonstration."),
            ("Empirical", "Bounded n=414 / n=50 / n=60 feasibility evidence."),
            ("Governance", "Keep machine, automated, human and source layers inspectable."),
        ],
        "evidence_label": "Ch1 §1.6 · Ch5 contribution",
        "notes": (
            "Stress governed review process.\n"
            "Transition: Boundaries of the claim…\n"
            "If late: methodology + governance only."
        ),
        "caveat": "Does not claim deployment readiness.",
    },
    "S10": {
        "title": "Claims stay bounded to one case, one model, one reviewer",
        "claim": "Feasibility evidence, not general policy truth or deployment readiness.",
        "limits": [
            ("One UK COVID-19 Inquiry case study", "External validity untested."),
            ("One main model", "Results are model-conditioned."),
            ("Single-reviewer validation", "No inter-rater κ."),
            ("Frozen historical outputs", "Live regen is not byte-identical."),
            ("Moderate agreement (κ 0.48 / 0.39)", "Cannot replace human judgement."),
            ("Framework mappings are interpretive aids", "Not official WHO/DQ audits."),
        ],
        "evidence_label": "Ch1.4 · Ch5 · reproducibility limits",
        "notes": (
            "Own each limit in one breath. No defensiveness.\n"
            "In 10-min deck limits fold into close.\n"
            "If late: case / model / reviewer only."
        ),
        "caveat": "Do not convert limits into soft claims of strength.",
    },
    "S11": {
        "title": "Next steps are replication and multi-reviewer checks",
        "claim": "Extend evaluation governance — not “add a chatbot and deploy”.",
        "items": [
            "Independent multi-reviewer validation",
            "Cross-inquiry replication",
            "Model comparison",
            "Domain-specific calibration",
            "Controlled deployment and access governance",
        ],
        "evidence_label": "Ch5 future / scaling conditions",
        "notes": (
            "Keep under 45s. Not a product roadmap.\n"
            "Removed in 10-minute deck."
        ),
        "caveat": "Not a deployment commitment.",
    },
    "S12": {
        "title": "Make the route from source to interpretation inspectable",
        "claim": CLOSING,
        "evidence_label": "Closing · ready for questions",
        "notes": (
            "Deliver close nearly verbatim. Stop. Hand over to examiners.\n"
            "10-min: speak key limitations briefly before the close."
        ),
        "caveat": "Presentation is complete without the live demo.",
        "limits_folded": [
            "One inquiry · one model · single reviewer",
            "Frozen outputs · moderate κ · interpretive mappings",
        ],
    },
}
