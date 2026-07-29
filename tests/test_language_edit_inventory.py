"""Unit tests for language-edit Markdown inventory."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from decision_journal.language_edit.inventory import (  # noqa: E402
    batch_editable,
    inventory_file,
    inventory_paths,
)

DISS = ROOT / "dissertation"


class InventoryTests(unittest.TestCase):
    def test_abstract_has_four_editable_paragraphs(self) -> None:
        inv = inventory_file(DISS / "ABSTRACT.md", relative_to=ROOT)
        self.assertEqual(inv.slug, "abstract")
        self.assertEqual(len(inv.editable_blocks), 4)
        ids = [b.paragraph_id for b in inv.editable_blocks]
        self.assertEqual(ids[0], "abstract/p001")
        self.assertTrue(all(i.startswith("abstract/p") for i in ids))

    def test_headings_tables_lists_not_editable(self) -> None:
        inv = inventory_file(DISS / "CHAPTER_1_INTRODUCTION.md", relative_to=ROOT)
        types = {b.block_type for b in inv.blocks}
        self.assertIn("heading", types)
        for b in inv.blocks:
            if b.block_type in {"heading", "table", "list_item", "figure_marker", "blockquote"}:
                self.assertFalse(b.editable)

    def test_clustering_filters_target_sections(self) -> None:
        paths = [
            DISS / "CHAPTER_3_METHODS.md",
            DISS / "CHAPTER_4_RESULTS.md",
            DISS / "CHAPTER_5_DISCUSSION.md",
        ]
        filters = {"ch3": ["3.9"], "ch4": ["4.10"], "ch5": ["5.3.6", "5.4"]}
        inventories = inventory_paths(paths, relative_to=ROOT, section_filters=filters)
        by_slug = {inv.slug: inv for inv in inventories}
        self.assertTrue(by_slug["ch3"].editable_count > 0)
        self.assertTrue(all("/3.9" in (b.section_path or "") for b in by_slug["ch3"].editable_blocks))
        self.assertTrue(all("/4.10" in (b.section_path or "") for b in by_slug["ch4"].editable_blocks))
        for b in by_slug["ch5"].editable_blocks:
            self.assertTrue(
                "/5.3.6" in b.section_path or "/5.4" in b.section_path or b.section_path.endswith("/5.4"),
                b.section_path,
            )

    def test_batches_do_not_overlap(self) -> None:
        inv = inventory_file(DISS / "ABSTRACT.md", relative_to=ROOT)
        batches = batch_editable([inv], batch_size=3)
        seen = []
        for batch in batches:
            for b in batch:
                self.assertNotIn(b.paragraph_id, seen)
                seen.append(b.paragraph_id)


if __name__ == "__main__":
    unittest.main()
