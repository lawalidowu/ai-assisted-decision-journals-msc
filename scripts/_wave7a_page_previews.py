#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from active_formal_submission import active_pdf  # noqa: E402

PKG = ROOT / "outputs" / "distinction_strategy" / "07_final_submission_freeze"


def main() -> None:
    pdf = active_pdf()
    doc = fitz.open(pdf)
    outdir = PKG / "validation" / "page_previews"
    outdir.mkdir(parents=True, exist_ok=True)
    for i in [0, 1, 2, 3, 33, 48, 76]:
        pix = doc[i].get_pixmap(matrix=fitz.Matrix(1.3, 1.3), alpha=False)
        pix.save(str(outdir / f"page_{i+1:02d}.png"))
    sums = []
    for path in sorted(PKG.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS":
            sums.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(PKG).as_posix()}")
    (PKG / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
    text0 = doc[0].get_text("text")
    print("title_has_september", "September 2026" in text0)
    print("title_has_may_line", bool(__import__("re").search(r"(?m)^May 2026\\s*$", text0)))
    print(f"previews={len(list(outdir.glob('*.png')))} sums={len(sums)}")


if __name__ == "__main__":
    main()
