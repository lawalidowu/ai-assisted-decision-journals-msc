#!/usr/bin/env python3
"""Build Wave 3 examiner reproducibility package artefacts (offline, no API)."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "examiner_evidence"
PKG = ROOT / "outputs" / "distinction_strategy" / "03_reproducibility_package"

AUDIT_E = (
    ROOT
    / "outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final"
)
CONSISTENCY = (
    ROOT
    / "outputs/framework_mapping/run_20260727_094015_post60_coding_consistency_audit"
)
WAVE2 = (
    ROOT
    / "outputs/dissertation_integration/run_20260729_153931_wave2_final_integrity_fixes"
)

DEMO_IDS = {
    "yes_high": "phase1-016",
    "no_high": "phase1-082",
    "faithfulness": "phase1-090",
    "jee_dq": "phase1-246",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    (PKG / "demos").mkdir(parents=True, exist_ok=True)
    (PKG / "validation").mkdir(parents=True, exist_ok=True)
    (PKG / "docs_copy").mkdir(parents=True, exist_ok=True)

    journal = load_json(ROOT / "data/manifests/phase1_decision_journal.json")
    by_id = {e["id"]: e for e in journal["entries"]}
    sample = load_json(ROOT / "configs/evaluation/confidence_validation_sample.json")
    sby = {i["journal_id"]: i for i in sample["items"]}
    kappa = load_json(ROOT / "configs/evaluation/confidence_comparison_results.json")
    audit_manifest = load_json(AUDIT_E / "AUDIT_E_MANIFEST.json")
    structural = load_json(ROOT / "configs/evaluation/structural_reliability_results.json")
    clustering = load_json(ROOT / "data/manifests/phase1_clustering_report.json")
    inquiry = load_json(ROOT / "data/manifests/inquiry_module2_phase1.json")
    inquiry_by_slug = {r["slug"]: r for r in inquiry}

    faith_rows = list(
        csv.DictReader(
            (AUDIT_E / "AUDIT_E_TRACEABILITY_HUMAN_CLASSIFICATION.csv").open(encoding="utf-8")
        )
    )
    faith_by = {r["entry_id"]: r for r in faith_rows}
    corr_rows = list(
        csv.DictReader((CONSISTENCY / "CONSISTENCY_CORRECTED_REFERENCE.csv").open(encoding="utf-8"))
    )
    corr_by = {r["entry_id"]: r for r in corr_rows}

    # Verify claims for validation log
    n_yes_high = sum(
        1
        for i in sample["items"]
        if i.get("human_valid_decision") == "yes" and i.get("human_confidence") == "high"
    )
    n_no_high = sum(
        1
        for i in sample["items"]
        if i.get("human_valid_decision") == "no" and i.get("human_confidence") == "high"
    )
    claim_checks = {
        "414": journal["totals"]["decisions"] == 414,
        "351_414": journal["totals"]["traceability_pass"] == 351,
        "no_x_high_21": n_no_high == 21,
        "yes_high_11": n_yes_high == 11,
        "kappa_rule": abs(kappa["metrics"]["rule_vs_human_b"]["weighted_kappa"] - 0.4813) < 1e-6,
        "kappa_llm": abs(kappa["metrics"]["llm_vs_human_b"]["weighted_kappa"] - 0.3927) < 1e-6,
        "clusters_20": clustering.get("n_clusters") == 20,
        "faith_8_25_20_7": audit_manifest.get("traceability_category_counts")
        == {
            "exact_or_near_verbatim": 8,
            "substantively_faithful_paraphrase": 25,
            "materially_unsupported_or_altered": 20,
            "traceability_false": 7,
        }
        or (
            audit_manifest.get("exact_or_near_verbatim") == 8
            and audit_manifest.get("substantively_faithful_paraphrase") == 25
            and audit_manifest.get("materially_unsupported_or_altered") == 20
            and audit_manifest.get("traceability_false") == 7
        ),
        "structural_49_50": structural["summary"]["structural_pass_count"] == 49,
    }
    # faith from known keys in manifest
    tc = audit_manifest.get("traceability_category_counts") or {
        k: audit_manifest[k]
        for k in (
            "exact_or_near_verbatim",
            "substantively_faithful_paraphrase",
            "materially_unsupported_or_altered",
            "traceability_false",
        )
        if k in audit_manifest
    }
    claim_checks["faith_8_25_20_7"] = (
        tc.get("exact_or_near_verbatim") == 8
        and tc.get("substantively_faithful_paraphrase") == 25
        and tc.get("materially_unsupported_or_altered") == 20
        and tc.get("traceability_false") == 7
    )

    # Demo snapshots (no reviewer_name)
    demo_payload = []
    run_map = {
        "phase1-016": (
            "run_20260608_005512_module2_2023-11-28",
            "transcript-of-module-2-public-hearing-on-28-november-2023",
            "2023-11-28",
        ),
        "phase1-082": (
            "run_20260609_014425_module2_2023-11-30",
            "transcript-of-module-2-public-hearing-on-30-november-2023",
            "2023-11-30",
        ),
        "phase1-090": (
            "run_20260609_014914_module2_2023-12-01",
            "transcript-of-module-2-public-hearing-on-01-december-2023",
            "2023-12-01",
        ),
        "phase1-246": (
            "run_20260609_071809_module2_2023-12-13",
            "transcript-of-module-2-public-hearing-on-13-december-2023",
            "2023-12-13",
        ),
    }
    for role, jid in DEMO_IDS.items():
        e = by_id[jid]
        run_id, slug, hearing = run_map[jid]
        decisions_path = ROOT / "outputs" / run_id / "decisions.json"
        row = {
            "demo_role": role,
            "journal_id": jid,
            "hearing_date": hearing,
            "slug": slug,
            "run_id": run_id,
            "public_pdf_url": inquiry_by_slug.get(slug, {}).get("pdf_url", ""),
            "local_historical_run_decisions": rel(decisions_path) if decisions_path.exists() else "",
            "local_run_decisions_sha256": sha256(decisions_path) if decisions_path.exists() else "",
            "decision": e["decision"],
            "source_quote": e["source_quote"],
            "source_location": e["source_location"],
            "evidence": e["evidence"],
            "traceability_ok": e["traceability_ok"],
            "review_flags": (e.get("phase2") or {}).get("review_flags") or [],
            "journal_entry_hash_note": "Fields copied from frozen phase1_decision_journal.json",
            "journal_sha256": sha256(ROOT / "data/manifests/phase1_decision_journal.json"),
        }
        if jid in sby:
            s = sby[jid]
            row["rubric_a"] = s.get("human_valid_decision")
            row["rubric_b"] = s.get("human_confidence")
            row["n50_notes"] = (s.get("human_notes") or "")[:240]
        if jid in faith_by:
            row["faithfulness_category"] = faith_by[jid].get("approved_traceability_category")
        if jid in corr_by:
            c = corr_by[jid]
            row["jee_decision"] = c.get("human_JEE_decision")
            row["jee_primary"] = c.get("human_primary_JEE")
            row["dq_decision"] = c.get("human_DQ_decision")
            row["dq_primary"] = c.get("human_primary_DQ")
            # intentionally omit reviewer_name / session_id
        demo_payload.append(row)
        out = PKG / "demos" / f"{jid}.json"
        out.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")

    (PKG / "demos" / "DEMO_CASE_INDEX.json").write_text(
        json.dumps(
            {
                "selected": DEMO_IDS,
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "cases": demo_payload,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    # Hash inventory for SHA256SUMS
    tracked_paths = [
        ROOT / "data/manifests/phase1_decision_journal.json",
        ROOT / "data/manifests/phase1_clustering_report.json",
        ROOT / "data/manifests/inquiry_module2_phase1.json",
        ROOT / "data/manifests/inquiry_module2_phase1.csv",
        ROOT / "configs/phase1_journal_runs.json",
        ROOT / "configs/evaluation/confidence_validation_sample.json",
        ROOT / "configs/evaluation/confidence_comparison_results.json",
        ROOT / "configs/evaluation/error_taxonomy_sample.json",
        ROOT / "configs/evaluation/structural_reliability_results.json",
        AUDIT_E / "AUDIT_E_MANIFEST.json",
        AUDIT_E / "AUDIT_E_JEE_SUMMARY.csv",
        AUDIT_E / "AUDIT_E_DQ_SUMMARY.csv",
        AUDIT_E / "AUDIT_E_EXECUTIVE_SUMMARY.md",
        AUDIT_E / "AUDIT_E_TRACEABILITY_HUMAN_CLASSIFICATION.csv",
        AUDIT_E / "crosstabs/AUDIT_E_jee_vs_dq_mapped.csv",
        CONSISTENCY / "CONSISTENCY_CORRECTED_REFERENCE.csv",
        WAVE2 / "Lawal_Akeeb_Idowu_MSc_Dissertation_FINAL.docx",
        WAVE2 / "Lawal_Akeeb_Idowu_MSc_Dissertation_FINAL.pdf",
    ]
    for i in range(1, 7):
        tracked_paths.append(ROOT / f"configs/annotations/excerpts/excerpt_{i:03d}.json")

    sums_lines = []
    hash_map = {}
    for p in tracked_paths:
        if not p.exists():
            raise SystemExit(f"Missing required path: {p}")
        digest = sha256(p)
        hash_map[rel(p)] = digest
        sums_lines.append(f"{digest}  {rel(p)}")

    # also hash demo snapshots
    for p in sorted((PKG / "demos").glob("*.json")):
        digest = sha256(p)
        hash_map[rel(p)] = digest
        sums_lines.append(f"{digest}  {rel(p)}")

    (PKG / "SHA256SUMS").write_text("\n".join(sums_lines) + "\n", encoding="utf-8")
    (DOCS / "SHA256SUMS").write_text("\n".join(sums_lines) + "\n", encoding="utf-8")

    validation = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "wave2_commit": "ee02346b3f1e60704c59d08e891c2a4735fa1307",
        "baseline_commit": "72e9fc4e7b8d4979fb3de9a63a9e8350056aed28",
        "claim_checks": claim_checks,
        "demo_ids": DEMO_IDS,
        "hashes": hash_map,
        "secret_scan_patterns": ["OPENAI_API_KEY=", "sk-proj-", "sk-live-"],
    }
    (PKG / "validation" / "PACKAGE_VALIDATION_LOG.json").write_text(
        json.dumps(validation, indent=2) + "\n", encoding="utf-8"
    )

    # Package manifest
    pkg_manifest = {
        "title": "Distinction Strategy Wave 3 examiner reproducibility package",
        "package_dir": rel(PKG),
        "docs_dir": rel(DOCS),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "demo_ids": DEMO_IDS,
        "sha256sums": rel(PKG / "SHA256SUMS"),
        "notes": [
            "Does not duplicate large analytical trees; references tracked paths by hash.",
            "LLM regeneration is not expected to be byte-identical.",
            "reviewer_name fields intentionally omitted from demo snapshots.",
        ],
    }
    (PKG / "PACKAGE_MANIFEST.json").write_text(json.dumps(pkg_manifest, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"pkg": str(PKG), "claim_checks": claim_checks, "demos": DEMO_IDS}, indent=2))


if __name__ == "__main__":
    main()
