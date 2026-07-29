"""Unit tests for language-edit protected-element checks."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from decision_journal.language_edit.protect import (  # noqa: E402
    compare_protected,
    extract_protected,
    find_us_spellings,
    language_policy_issues,
    markdown_structure_issues,
)
from decision_journal.language_edit.validate import validate_revision  # noqa: E402

GLOSSARY = ["Module 2", "Phase 1", "Phase 2", "UK COVID-19 Inquiry", "decision journal"]
QUALIFIERS = [
    "purposively selected",
    "stratified sample",
    "within that sample",
    "validation sample",
    "faithful extraction",
    "faithful",
    "frozen",
    "canonical",
    "non-destructive",
    "supplementary",
    "interleaved",
]
SCOPE = [
    "within that sample",
    "validation sample",
    "stratified sample",
    "purposively selected",
]
US_TO_UK = {
    "judgment": "judgement",
    "emphasize": "emphasise",
    "organization": "organisation",
    "prioritize": "prioritise",
}


class ProtectTests(unittest.TestCase):
    def test_extract_sample_size_and_percent_and_kappa(self) -> None:
        text = (
            "Human validation on a stratified sample (n = 50) found 21 of 50 items "
            "(42%) in the no × high cell. Agreement (linear weighted κ ≈ 0.39–0.48) "
            "on 414 entries with 84.8% traceability."
        )
        bundle = extract_protected(text, glossary=GLOSSARY)
        self.assertIn("n=50", [s.lower().replace(" ", "") for s in bundle.sample_sizes])
        self.assertTrue(any(n.startswith("42%") for n in bundle.numbers))
        self.assertTrue(any(n.startswith("84.8%") for n in bundle.numbers))
        self.assertTrue(any("414" == n for n in bundle.numbers))
        self.assertTrue(
            any("κ" in g for g in bundle.greek_stats)
            or any("0.39" in g for g in bundle.greek_stats)
        )
        self.assertTrue(any(p.lower().replace(" ", "") for p in bundle.special_phrases))

    def test_compare_rejects_number_change(self) -> None:
        original = "Corpus-scale extraction achieved 84.8% mechanical traceability on 414 entries."
        revised = "Corpus-scale extraction achieved 85% mechanical traceability on 414 entries."
        result = compare_protected(original, revised, glossary=GLOSSARY)
        self.assertFalse(result["ok"])
        self.assertIn("numbers", result["mismatches"])

    def test_compare_accepts_paraphrase_with_same_tokens(self) -> None:
        original = (
            "This dissertation presents a layered validation framework for AI-assisted "
            "decision journaling from UK COVID-19 Inquiry Module 2 public hearing transcripts."
        )
        revised = (
            "This dissertation presents a layered validation framework that supports "
            "AI-assisted decision journaling from UK COVID-19 Inquiry Module 2 public hearing transcripts."
        )
        result = compare_protected(original, revised, glossary=GLOSSARY)
        self.assertTrue(result["ok"], result["mismatches"])

    def test_structure_rejects_heading_injection(self) -> None:
        issues = markdown_structure_issues("Plain prose.", "## Injected\nPlain prose.")
        self.assertIn("introduced_heading_marker", issues)

    def test_figure_marker_preservation(self) -> None:
        original = "See [[FIGURE:4.10a]] for sizes."
        revised = "See [[FIGURE:4.10b]] for sizes."
        issues = markdown_structure_issues(original, revised)
        self.assertIn("figure_marker_changed", issues)
        result = compare_protected(original, revised)
        self.assertFalse(result["ok"])

    def test_us_spelling_lint(self) -> None:
        hits = find_us_spellings(
            "Automated confidence showed moderate agreement with human judgment.",
            US_TO_UK,
        )
        self.assertTrue(any(h["us"] == "judgment" for h in hits))

    def test_missing_methodological_qualifier(self) -> None:
        original = (
            "The research design combines traceable LLM extraction on eight "
            "purposively selected hearings with validation on a frozen canonical journal."
        )
        revised = (
            "The research design combines traceable LLM extraction on eight "
            "selected hearings with validation on a journal."
        )
        policy = language_policy_issues(
            original,
            revised,
            qualifiers=QUALIFIERS,
            scope_phrases=SCOPE,
            us_to_uk=US_TO_UK,
        )
        self.assertFalse(policy["ok"])
        self.assertIn("purposively selected", policy["missing_qualifiers"])
        self.assertIn("frozen", policy["missing_qualifiers"])
        self.assertIn("canonical", policy["missing_qualifiers"])

    def test_faithful_not_replaced_by_accurate(self) -> None:
        original = "The outcome was faithful extraction of the wrong artefact type."
        revised = "The outcome was accurate extraction of the wrong artefact type."
        policy = language_policy_issues(
            original,
            revised,
            qualifiers=QUALIFIERS,
            forbidden_faithful_substitutes=["accurate extraction"],
        )
        self.assertIn("faithful_replaced_by_accurate", policy["reasons"])

    def test_interleaved_meaning_must_be_kept(self) -> None:
        original = (
            "Public inquiry transcripts contain interleaved policy decisions, "
            "procedural exchanges, counsel questions, and witness narrative."
        )
        revised = (
            "Public inquiry transcripts contain policy decisions, procedural "
            "exchanges, counsel questions, and witness narrative."
        )
        policy = language_policy_issues(original, revised, qualifiers=QUALIFIERS)
        self.assertIn("interleaved_meaning_lost", policy["reasons"])

    def test_scope_boundary_must_not_broaden(self) -> None:
        original = (
            "21 of 50 items (42%) within that sample fell in the no × high cell."
        )
        revised = "21 of 50 items (42%) fell in the no × high cell."
        policy = language_policy_issues(
            original,
            revised,
            qualifiers=QUALIFIERS,
            scope_phrases=SCOPE,
        )
        self.assertIn("scope_boundary_missing", policy["reasons"])

    def test_whether_must_be_preserved(self) -> None:
        original = (
            "This dissertation investigates whether a governed, prompt-based pipeline "
            "can produce auditable decision-journal entries."
        )
        revised = (
            "This dissertation investigates if a governed, prompt-based pipeline "
            "can produce auditable decision-journal entries."
        )
        policy = language_policy_issues(original, revised, qualifiers=QUALIFIERS)
        self.assertIn("whether_replaced", policy["reasons"])

    def test_self_check_false_rejects(self) -> None:
        original = "Phase 2 applies non-destructive review flags."
        revised = "Phase 2 applies non-destructive review flags with clearer wording."
        record = validate_revision(
            paragraph_id="t1",
            original_text=original,
            revision={
                "paragraph_id": "t1",
                "original_text": original,
                "revised_text": revised,
                "change_summary": "minor clarity",
                "meaning_changed": False,
                "new_claim_added": False,
                "methodological_qualifiers_preserved": True,
                "scope_preserved": True,
                "british_english_used": False,
                "technical_distinctions_preserved": True,
            },
            qualifiers=QUALIFIERS,
            scope_phrases=SCOPE,
            us_to_uk=US_TO_UK,
        )
        self.assertEqual(record["review_state"], "rejected_by_validation")
        self.assertIn("self_check_false:british_english_used", record["reject_reasons"])


if __name__ == "__main__":
    unittest.main()
