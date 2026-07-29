#!/usr/bin/env python3
"""Assemble Wave 6 viva defence package from tracked docs + frozen evidence keys."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIVA = ROOT / "docs" / "viva"
PKG = ROOT / "outputs" / "distinction_strategy" / "06_viva_defence"

HEADLINE_NUMBERS = {
    "414": ("Ch4 Table 4.1", "data/manifests/phase1_decision_journal.json", "totals.decisions=414", "814cc7c47a9f75bfc0a6c7b693feec7073e59131398d89fab7c9111fbb2e5e06"),
    "351/414": ("Ch4 Table 4.1", "data/manifests/phase1_decision_journal.json", "totals.traceability_pass=351", "814cc7c47a9f75bfc0a6c7b693feec7073e59131398d89fab7c9111fbb2e5e06"),
    "5/10/0": ("Ch4 Table 4.2", "configs/annotations/excerpts/excerpt_00{1-6}.json", "agreement/silence/dissonance", "see examiner SHA256SUMS"),
    "1/6": ("Ch4; App B", "docs/BASELINE_KEYWORD.md", "keyword recall 1/6", "n/a"),
    "5/6": ("App B", "triangulation agreement vs manuals", "LLM agreement-row recall 5/6", "n/a"),
    "21/50": ("Ch4 §4.5", "configs/evaluation/confidence_validation_sample.json", "A=no & B=high count", "9d74936c490de586…"),
    "0.48": ("Ch4 Table 4.3", "configs/evaluation/confidence_comparison_results.json", "metrics.rule_vs_human_b.weighted_kappa=0.4813", "e197b7f28d2bb08a…"),
    "0.39": ("Ch4 Table 4.3", "configs/evaluation/confidence_comparison_results.json", "metrics.llm_vs_human_b.weighted_kappa=0.3927", "e197b7f28d2bb08a…"),
    "20": ("Ch4 §4.6", "data/manifests/phase1_clustering_report.json", "n_clusters=20", "08a6bf8d48191978…"),
    "11/60": ("Ch4 Table 4.4", "…/AUDIT_E_JEE_SUMMARY.csv", "mapped=11", "499b82c045713821…"),
    "37/60": ("Ch4 Table 4.4", "…/AUDIT_E_DQ_SUMMARY.csv", "mapped=37", "2bdd445b3fa7782a…"),
    "26/60": ("Ch4 Table 4.4", "…/crosstabs/AUDIT_E_jee_vs_dq_mapped.csv", "unmapped×mapped=26", "773724149e29f231…"),
    "8/25/20/7": ("Ch4 Table 4.5", "…/AUDIT_E_MANIFEST.json", "traceability_category_counts", "8262948f55a04950…"),
    "50/53": ("Ch4 §4.8", "docs/REPORT_PILOT.md", "50/53", "n/a"),
    "49/50": ("Ch4 §4.8", "configs/evaluation/structural_reliability_results.json", "summary.structural_pass_count=49", "8c9ce78f9eecfe01…"),
}

DEMO = {
    "phase1-016": ("yes", "high", "e5d28326427f4108ed97922bf444a4467ce807e4aa198277e2ba46d6cd3a2953"),
    "phase1-082": ("no", "high", "9b131dc2b403f51a3a1de366ee56793c6ff255986a57e683d525297963cca2c0"),
    "phase1-090": ("materially_unsupported_or_altered", "", "7e94f16177c4ce820f956d64d27dfd9a1798e91627cb7e372ac43b0ba25ed430"),
    "phase1-246": ("P3", "commitment_to_follow_through", "30e2cf20540de86b618cc3790b006148fb50905e3c51b35c404dab88099440ee"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assemble_package() -> None:
    if PKG.exists():
        shutil.rmtree(PKG)
    for sub in ("candidate_pack", "examiner_style_questions", "rehearsal", "validation"):
        (PKG / sub).mkdir(parents=True)

    # Copy viva docs into package mirrors
    for path in sorted(VIVA.glob("*")):
        if path.is_file():
            if path.name.startswith("MOCK_VIVA_SCRIPT") or path.name.startswith("VIVA_QUESTION"):
                dest = PKG / "examiner_style_questions" / path.name
            elif (
                path.name.startswith("REHEARSAL")
                or "REHEARSAL" in path.name
                or path.name.startswith("MOCK_VIVA_SCORING")
                or path.name == "PRESENTATION_REHEARSAL_PLAN.md"
            ):
                dest = PKG / "rehearsal" / path.name
            else:
                dest = PKG / "candidate_pack" / path.name
            shutil.copy2(path, dest)

    # Also put rehearsal template in rehearsal/
    for name in ("REHEARSAL_LOG_TEMPLATE.csv", "MOCK_VIVA_SCORING_RUBRIC.md"):
        src = VIVA / name
        if src.exists():
            shutil.copy2(src, PKG / "rehearsal" / name)

    # Evidence index already in viva/
    idx = VIVA / "VIVA_EVIDENCE_INDEX.csv"
    if idx.exists():
        shutil.copy2(idx, PKG / "candidate_pack" / "VIVA_EVIDENCE_INDEX.csv")

    manifest = {
        "title": "Wave 6 viva defence package",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "wave5b_commit": "cb34b144a49064b18939d37ea06b22ff936086af",
        "note": "Training/rehearsal materials only — not official examiner questions or mark schemes.",
        "headline_numbers": list(HEADLINE_NUMBERS.keys()),
        "demo_cases": list(DEMO.keys()),
    }
    (PKG / "PACKAGE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    (PKG / "validation" / "NUMBER_LOCK.json").write_text(
        json.dumps({"headline_numbers": HEADLINE_NUMBERS, "demo": DEMO}, indent=2) + "\n",
        encoding="utf-8",
    )

    sums = []
    for path in sorted(PKG.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS":
            sums.append(f"{sha256(path)}  {path.relative_to(PKG).as_posix()}")
    (PKG / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
    print(f"Wrote {PKG} ({len(sums)} files)")


if __name__ == "__main__":
    assemble_package()
    # Re-run validation into package/validation after assemble (rmtree clears prior)
    import subprocess
    import sys

    rc = subprocess.call([sys.executable, str(ROOT / "scripts" / "validate_viva_defence_wave6.py")])
    # Refresh SHA256SUMS to include validation report
    sums = []
    for path in sorted(PKG.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS":
            sums.append(f"{sha256(path)}  {path.relative_to(PKG).as_posix()}")
    (PKG / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
    raise SystemExit(rc)