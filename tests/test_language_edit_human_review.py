"""Tests for human-edit validation gate."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from decision_journal.language_edit.human_review import (  # noqa: E402
    apply_human_decisions,
    text_for_later_apply,
    validate_human_replacement,
)

CONFIG = json.loads((ROOT / "configs" / "language_edit.json").read_text(encoding="utf-8"))


class HumanReviewTests(unittest.TestCase):
    def test_human_edit_passes_when_qualifiers_kept(self) -> None:
        original = (
            "Human validation on a stratified sample (n = 50) revealed that the dominant "
            "outcome observed in the validation sample was not hallucination but faithful "
            "extraction of the wrong artefact type: 21 of 50 items (42%) within that sample "
            "fell in the no × high cell."
        )
        human = (
            "Human validation on a stratified sample (n = 50) showed that the dominant "
            "outcome in the validation sample was not hallucination but faithful extraction "
            "of the wrong artefact type: 21 of 50 items (42%) within that sample fell in the "
            "no × high cell."
        )
        gate = validate_human_replacement(
            paragraph_id="abstract/p003",
            original_text=original,
            human_revised_text=human,
            config=CONFIG,
        )
        self.assertTrue(gate["ok"], gate["reasons"])

    def test_human_edit_fails_when_scope_dropped(self) -> None:
        original = (
            "21 of 50 items (42%) within that sample fell in the no × high cell."
        )
        human = "21 of 50 items (42%) fell in the no × high cell."
        gate = validate_human_replacement(
            paragraph_id="t",
            original_text=original,
            human_revised_text=human,
            config=CONFIG,
        )
        self.assertFalse(gate["ok"])
        self.assertTrue(gate["reasons"])

    def test_cannot_approve_rejected_llm_without_human_text(self) -> None:
        records = [
            {
                "paragraph_id": "abstract/p003",
                "original_text": "stratified sample within that sample faithful",
                "revised_text": "bad",
                "review_state": "rejected_by_validation",
                "reject_reasons": ["scope_boundary_missing"],
                "change_summary": "x",
                "unchanged": False,
            }
        ]
        updated = apply_human_decisions(
            records,
            {
                "abstract/p003": {
                    "human_decision": "approved_by_human",
                    "human_notes": "try approve llm",
                }
            },
            config=CONFIG,
        )
        self.assertEqual(updated[0]["review_state"], "rejected_by_human")
        self.assertIsNone(text_for_later_apply(updated[0]))

    def test_apply_prefers_validated_human_text(self) -> None:
        original = (
            "The research design combines traceable LLM extraction on eight purposively "
            "selected hearings with validation on a frozen canonical journal."
        )
        human = (
            "The research design combines traceable LLM extraction on eight purposively "
            "selected hearings with validation on a frozen canonical journal of candidates."
        )
        records = [
            {
                "paragraph_id": "abstract/p002",
                "original_text": original,
                "revised_text": "llm version with purposively selected frozen canonical",
                "review_state": "validated_pending_review",
                "reject_reasons": [],
                "change_summary": "llm",
                "unchanged": False,
                "meaning_changed": False,
                "new_claim_added": False,
                "methodological_qualifiers_preserved": True,
                "scope_preserved": True,
                "british_english_used": True,
                "technical_distinctions_preserved": True,
            }
        ]
        updated = apply_human_decisions(
            records,
            {
                "abstract/p002": {
                    "human_decision": "approved_by_human",
                    "human_revised_text": human,
                    "human_notes": "edited",
                }
            },
            config=CONFIG,
        )
        self.assertEqual(updated[0]["review_state"], "approved_by_human")
        self.assertEqual(updated[0]["proposal_source"], "human_edit")
        self.assertEqual(text_for_later_apply(updated[0]), updated[0]["human_revised_text"])
        self.assertNotEqual(text_for_later_apply(updated[0]), records[0]["revised_text"])


if __name__ == "__main__":
    unittest.main()
