#!/usr/bin/env python3
"""Update page count, TOC, List of Figures, List of Tables in Word.

Close Microsoft Word before running. Takes ~30-60 seconds.

Usage:
    python scripts/finalize_word_fields.py
    python scripts/finalize_word_fields.py --doc dissertation/Lawal_MSc_Dissertation.docx
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_submission_docx import DISS, finalize_dissertation_in_word  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Finalize Word fields (pages, LOF, LOT).")
    parser.add_argument(
        "--doc",
        type=Path,
        default=DISS / "Lawal_MSc_Dissertation.docx",
        help="Dissertation .docx path",
    )
    args = parser.parse_args()
    docx = args.doc.resolve()
    if not docx.is_file():
        raise SystemExit(f"Not found: {docx}. Run build_submission_docx.py first.")

    print(f"Finalizing {docx.name} — ensure Word is closed...")
    stats = finalize_dissertation_in_word(docx)
    if not stats.get("ok"):
        raise SystemExit(
            "Word finalize failed. Close Word completely, then retry.\n"
            "If it still fails: open the doc, press Ctrl+A, F9, save."
        )
    print(
        f"Done: {stats.get('pages', '?')} pages | "
        f"{stats.get('figures', 0)} figures | {stats.get('tables', 0)} tables | fields updated."
    )


if __name__ == "__main__":
    main()
