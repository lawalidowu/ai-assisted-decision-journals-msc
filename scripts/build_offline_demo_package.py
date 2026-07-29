#!/usr/bin/env python3
"""Assemble Wave 4 offline demo package (copy demo/ + manifests)."""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo"
PKG = ROOT / "outputs" / "distinction_strategy" / "04_offline_demo"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    # Keep embed / print.html aligned with evidence JSON before packaging
    import importlib.util

    regen_path = Path(__file__).with_name("regenerate_offline_demo_embed.py")
    spec = importlib.util.spec_from_file_location("regen_offline_embed", regen_path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.main()

    if PKG.exists():
        shutil.rmtree(PKG)
    PKG.mkdir(parents=True)
    dest = PKG / "demo"
    shutil.copytree(
        DEMO,
        dest,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )

    sums = []
    for path in sorted(dest.rglob("*")):
        if path.is_file():
            rel = path.relative_to(PKG).as_posix()
            digest = sha256(path)
            sums.append(f"{digest}  {rel}")

    (PKG / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
    manifest = {
        "title": "Wave 4 offline examiner demo package",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "wave3_commit": "7b270854ddbb7b8c21e06de6711d90b856d95859",
        "demo_relative": "demo/",
        "launch": "python demo/launch_demo.py",
        "sha256sums": "SHA256SUMS",
        "cases": ["phase1-016", "phase1-082", "phase1-090", "phase1-246"],
        "notes": [
            "Self-contained offline HTML demo.",
            "No CDN, no API calls, localhost-only launcher.",
            "Screenshots not included (optional; no external capture dependency).",
        ],
    }
    (PKG / "PACKAGE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (PKG / "validation" ).mkdir(exist_ok=True)
    (PKG / "validation" / "OFFLINE_DEMO_VALIDATION.json").write_text(
        json.dumps(
            {
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "evidence_manifest": json.loads((DEMO / "DEMO_EVIDENCE_MANIFEST.json").read_text(encoding="utf-8")),
                "journal_sha256_expected": "814cc7c47a9f75bfc0a6c7b693feec7073e59131398d89fab7c9111fbb2e5e06",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {PKG}")


if __name__ == "__main__":
    main()
