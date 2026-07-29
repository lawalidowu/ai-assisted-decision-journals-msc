"""Verify Phase 1 Module 2 transcript download and text processing."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/manifests/inquiry_module2_phase1.csv"


def main() -> int:
    all_rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8")))
    rows = [r for r in all_rows if r.get("doc_type") == "Transcript" or "transcript" in r.get("slug", "")]
    if len(rows) != 8:
        print(f"FAIL: expected 8 transcript rows, got {len(rows)} (manifest total {len(all_rows)})")
        return 1

    print(f"Phase 1 manifest: {len(rows)} transcripts ({len(all_rows)} total rows incl. reports)\n")
    header = f"{'Date':<12} {'PDF':>6} {'TXT':>6} {'Chars':>8} {'Lines':>6} {'OK':>4}"
    print(header)
    print("-" * len(header))

    all_ok = True
    for r in rows:
        slug = r["slug"]
        date = slug.split("-on-")[-1].replace("-", " ")[:11]
        pdf = Path(r["local_pdf"])
        txt = Path(r["local_txt"])

        pdf_ok = pdf.is_file() and pdf.stat().st_size > 10_000
        txt_ok = txt.is_file() and txt.stat().st_size > 10_000

        chars = lines = 0
        text_ok = False
        if txt_ok:
            text = txt.read_text(encoding="utf-8", errors="replace")
            chars = len(text)
            lines = text.count("\n") + 1
            text_ok = chars > 50_000 and "LADY HALLETT" in text.upper()

        row_ok = pdf_ok and txt_ok and text_ok
        all_ok = all_ok and row_ok
        flag = "Y" if row_ok else "N"
        print(
            f"{date:<12} {pdf.stat().st_size if pdf_ok else 0:>6} "
            f"{txt.stat().st_size if txt_ok else 0:>6} {chars:>8} {lines:>6} {flag:>4}"
        )
        if not row_ok:
            issues = []
            if not pdf_ok:
                issues.append("missing/empty PDF")
            if not txt_ok:
                issues.append("missing/empty TXT")
            elif not text_ok:
                issues.append("text too short or missing inquiry markers")
            print(f"  -> {slug}: {', '.join(issues)}")

    print()
    if all_ok:
        print("RESULT: All 8 Module 2 transcripts downloaded and text-processed.")
        return 0
    print("RESULT: Gaps found — re-run pipeline download/text stages.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
