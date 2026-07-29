#!/usr/bin/env python3
"""Wave 6 claim / privacy / path validation for viva defence package."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIVA = ROOT / "docs" / "viva"
OUT = ROOT / "outputs" / "distinction_strategy" / "06_viva_defence" / "validation"

SECRET_RE = re.compile(
    r"(?i)(openai_api_key\s*=\s*sk-|sk-(?:proj|live)-[A-Za-z0-9]{10,}|BEGIN (?:RSA |OPENSSH )?PRIVATE KEY)"
)

PROTECTED = {
    "wave2_docx": (
        ROOT
        / "outputs/dissertation_integration/run_20260729_153931_wave2_final_integrity_fixes/Lawal_Akeeb_Idowu_MSc_Dissertation_FINAL.docx",
        "a829ff6d0b4a778f2a276f9fff45af05dbc47fa268f3a9b0b131a87099b0a2e2",
    ),
    "wave2_pdf": (
        ROOT
        / "outputs/dissertation_integration/run_20260729_153931_wave2_final_integrity_fixes/Lawal_Akeeb_Idowu_MSc_Dissertation_FINAL.pdf",
        "40c123b9743277d9083d3b66eb855e0fa7a57101017d08a7d8a2d94558a63519",
    ),
    "journal": (
        ROOT / "data/manifests/phase1_decision_journal.json",
        "814cc7c47a9f75bfc0a6c7b693feec7073e59131398d89fab7c9111fbb2e5e06",
    ),
    "demo_016": (ROOT / "demo/evidence/phase1-016.json", "e5d28326427f4108ed97922bf444a4467ce807e4aa198277e2ba46d6cd3a2953"),
    "demo_082": (ROOT / "demo/evidence/phase1-082.json", "9b131dc2b403f51a3a1de366ee56793c6ff255986a57e683d525297963cca2c0"),
    "demo_090": (ROOT / "demo/evidence/phase1-090.json", "7e94f16177c4ce820f956d64d27dfd9a1798e91627cb7e372ac43b0ba25ed430"),
    "demo_246": (ROOT / "demo/evidence/phase1-246.json", "30e2cf20540de86b618cc3790b006148fb50905e3c51b35c404dab88099440ee"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    report: dict = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "checks": {},
        "ok": True,
    }

    # Protected hashes
    hash_ok = True
    hash_detail = {}
    for key, (path, expected) in PROTECTED.items():
        got = sha256(path) if path.is_file() else None
        match = got == expected
        hash_detail[key] = {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "match": match}
        hash_ok = hash_ok and match
    report["checks"]["protected_hashes"] = {"ok": hash_ok, "detail": hash_detail}

    # Presentation deck hashes vs SHA256SUMS
    deck_dir = ROOT / "outputs/distinction_strategy/05_presentation_deck"
    deck_ok = True
    deck_detail = []
    sums = deck_dir / "SHA256SUMS"
    if sums.is_file():
        for line in sums.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            digest, rel = line.split(None, 1)
            path = deck_dir / rel.strip()
            if path.suffix.lower() in {".pptx", ".pdf"} and path.is_file():
                match = sha256(path) == digest
                deck_detail.append({"file": rel.strip(), "match": match})
                deck_ok = deck_ok and match
    report["checks"]["presentation_decks"] = {"ok": deck_ok, "detail": deck_detail}

    # Secret scan over viva docs
    secret_hits = []
    for path in VIVA.glob("*"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if SECRET_RE.search(text):
            secret_hits.append(path.name)
    report["checks"]["secret_scan"] = {"ok": len(secret_hits) == 0, "hits": secret_hits}

    # Evidence path validation
    path_issues = []
    rows = list(csv.DictReader((VIVA / "VIVA_EVIDENCE_INDEX.csv").open(encoding="utf-8")))
    for row in rows:
        src = row["authoritative_source"].strip()
        eh = row["evidence_hash"].strip().lower()
        if eh.startswith("hash_only") or eh.startswith("see_") or src.endswith("/"):
            continue
        path = ROOT / src
        if not path.exists():
            path_issues.append(src)
    report["checks"]["evidence_paths"] = {"ok": len(path_issues) == 0, "missing": path_issues}

    # Claim lock: headline numbers present in viva corpus
    blob = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in VIVA.glob("*.md"))
    tokens = ["414", "351/414", "21/50", "0.48", "0.39", "11/60", "37/60", "26/60", "8/25/20/7", "phase1-082"]
    missing = [t for t in tokens if t not in blob]
    report["checks"]["claim_tokens"] = {"ok": len(missing) == 0, "missing": missing}

    # Forbidden affirmative overclaims
    forbidden = [
        "official viva is forty",
        "ready for production deployment",
        "second independent reviewer existed",
        "supervisor was the second reviewer",
        "byte-identical llm reproducibility is expected",
        "confidence interval of",
    ]
    found = [f for f in forbidden if f in blob.lower()]
    report["checks"]["forbidden_overclaims"] = {"ok": len(found) == 0, "found": found}

    report["ok"] = all(c.get("ok") for c in report["checks"].values())
    (OUT / "WAVE6_VALIDATION_REPORT.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": report["ok"], "checks": {k: v["ok"] for k, v in report["checks"].items()}}, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
