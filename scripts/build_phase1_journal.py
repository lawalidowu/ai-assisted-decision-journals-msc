"""Merge canonical Phase 1 extraction runs into one decision journal artefact."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS_CONFIG = ROOT / "configs/phase1_journal_runs.json"
OUTPUT_PATH = ROOT / "data/manifests/phase1_decision_journal.json"

PHASE2_PLACEHOLDER = {
    "confidence": None,
    "cluster_id": None,
    "cluster_label": None,
    "review_flags": [],
}


def build_journal() -> dict:
    config = json.loads(RUNS_CONFIG.read_text(encoding="utf-8"))
    runs = config["runs"]
    expected = config["expected_totals"]

    entries: list[dict] = []
    source_runs: list[str] = []
    model = chunk_size = chunk_overlap = None

    for run_meta in runs:
        run_id = run_meta["run_id"]
        run_dir = ROOT / "outputs" / run_id
        decisions_path = run_dir / "decisions.json"
        manifest_path = run_dir / "manifest.json"

        if not decisions_path.is_file():
            raise FileNotFoundError(f"Missing decisions.json for {run_id}")
        if not manifest_path.is_file():
            raise FileNotFoundError(f"Missing manifest.json for {run_id}")

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not manifest.get("inquiry_mode"):
            raise ValueError(f"{run_id} was not run with inquiry_mode=true")

        if model is None:
            model = manifest.get("model")
            chunk_size = manifest.get("chunk_size")
            chunk_overlap = manifest.get("chunk_overlap")

        decisions = json.loads(decisions_path.read_text(encoding="utf-8"))
        source_runs.append(run_id)

        for item_index, item in enumerate(decisions, start=1):
            global_num = len(entries) + 1
            entries.append(
                {
                    "id": f"phase1-{global_num:03d}",
                    "hearing_date": run_meta["hearing_date"],
                    "label": run_meta["label"],
                    "run_id": run_id,
                    "item_index": item_index,
                    "slug": run_meta["slug"],
                    "source_document_type": run_meta["source_document_type"],
                    "decision": item.get("decision", ""),
                    "evidence": item.get("evidence", ""),
                    "source_quote": item.get("source_quote", ""),
                    "source_location": item.get("source_location", ""),
                    "traceability_ok": bool(item.get("traceability_ok")),
                    "phase2": dict(PHASE2_PLACEHOLDER),
                }
            )

    pass_count = sum(1 for e in entries if e["traceability_ok"])
    fail_count = len(entries) - pass_count

    journal = {
        "version": "1.0",
        "artifact_type": "canonical_decision_journal",
        "journal_version": "phase1",
        "schema_note": "v1.0 = Phase 1 freeze; phase2 fields null. Bump to 1.1 when confidence populated.",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "source_runs": source_runs,
        "totals": {
            "decisions": len(entries),
            "traceability_pass": pass_count,
            "traceability_fail": fail_count,
        },
        "entries": entries,
    }

    if len(entries) != expected["decisions"]:
        raise SystemExit(
            f"FAIL: expected {expected['decisions']} decisions, got {len(entries)}"
        )
    if pass_count != expected["traceability_pass"]:
        raise SystemExit(
            f"FAIL: expected {expected['traceability_pass']} traceability pass, got {pass_count}"
        )
    if fail_count != expected["traceability_fail"]:
        raise SystemExit(
            f"FAIL: expected {expected['traceability_fail']} traceability fail, got {fail_count}"
        )

    return journal


def main() -> int:
    journal = build_journal()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(journal, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    totals = journal["totals"]
    print(f"Wrote {OUTPUT_PATH}")
    print(
        f"  {totals['decisions']} entries, "
        f"{totals['traceability_pass']} traceability_ok, "
        f"{totals['traceability_fail']} fail"
    )
    print(f"  IDs: {journal['entries'][0]['id']} .. {journal['entries'][-1]['id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
