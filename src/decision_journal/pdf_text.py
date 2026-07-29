"""Extract plain text from inquiry PDFs."""

from __future__ import annotations

import argparse
from pathlib import Path

from pypdf import PdfReader

from .extraction import clean_inquiry_text


def pdf_to_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n\n".join(p.strip() for p in pages if p.strip())


def default_output_path(pdf_path: Path) -> Path:
    rel = pdf_path.name
    if "inquiry" in pdf_path.parts:
        idx = pdf_path.parts.index("inquiry")
        rel = "/".join(pdf_path.parts[idx:])
    out_name = Path(rel).with_suffix(".txt").name
    return Path("data/processed/inquiry") / out_name


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert inquiry PDF to plain text")
    parser.add_argument("pdf", help="Path to PDF file")
    parser.add_argument(
        "-o",
        "--output",
        default="",
        help="Output .txt path (default: data/processed/inquiry/<name>.txt)",
    )
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        raise SystemExit(f"PDF not found: {pdf_path}")

    text = clean_inquiry_text(pdf_to_text(pdf_path))
    if not text:
        raise SystemExit(f"No text extracted from {pdf_path}. PDF may be scanned/image-only.")

    out_path = Path(args.output) if args.output else default_output_path(pdf_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    print(f"Wrote {len(text)} characters to {out_path}")


if __name__ == "__main__":
    main()
