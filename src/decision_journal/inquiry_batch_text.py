"""Batch convert manifest PDFs to plain text."""

from __future__ import annotations

from pathlib import Path

from decision_journal.inquiry_harvest import MANIFEST_FIELDS, read_manifest, slugify_filename
from decision_journal.pdf_text import pdf_to_text


def run_batch_text(
    manifest_path: Path,
    *,
    processed_dir: Path,
    only_phase1: bool = True,
    limit: int | None = None,
) -> int:
    rows = read_manifest(manifest_path)
    converted = 0
    for row in rows:
        if only_phase1 and row.get("selected_phase1") != "true":
            continue
        pdf_path = Path(row.get("local_pdf") or "")
        if not pdf_path.exists():
            continue
        if limit is not None and converted >= limit:
            break

        category = row.get("doc_category") or "document"
        out_dir = processed_dir / category
        out_dir.mkdir(parents=True, exist_ok=True)
        out_name = slugify_filename(row.get("slug") or pdf_path.stem) + ".txt"
        out_path = out_dir / out_name

        text = pdf_to_text(pdf_path)
        out_path.write_text(text, encoding="utf-8")
        row["local_txt"] = str(out_path.as_posix())
        row["text_chars"] = str(len(text))
        row["text_ok"] = "true" if len(text.strip()) > 100 else "false"
        converted += 1

    with manifest_path.open("w", encoding="utf-8", newline="") as handle:
        import csv

        writer = csv.DictWriter(handle, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return converted
