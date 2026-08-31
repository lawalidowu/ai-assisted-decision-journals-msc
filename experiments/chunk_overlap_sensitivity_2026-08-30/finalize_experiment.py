#!/usr/bin/env python3
"""Finalize experiment outputs: alignment CSV, Stage 3, API manifest, reports."""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from run_experiment import (  # noqa: E402
    ApiUsage,
    build_alignment_rows,
    config_label,
    extract_on_text,
    finalize_metrics,
    load_excerpts,
    metrics_to_row,
    run_stage3,
    write_csv,
)
from decision_journal.extraction import get_client  # noqa: E402

EXPERIMENT_DIR = Path(__file__).resolve().parent


def rebuild_stage1_alignment(excerpts, client) -> tuple[list[dict], list[dict]]:
    """Re-run per-excerpt extraction to build auditable alignment (Stage 1)."""
    import csv

    rows_csv = list(
        csv.DictReader((EXPERIMENT_DIR / "01_STAGE1_CONFIGURATION_RESULTS.csv").open())
    )
    all_align: list[dict] = []
    api_rows: list[dict] = []

    for r in rows_csv:
        cs, ov = int(r["chunk_size"]), int(r["overlap"])
        cfg = r["configuration"]
        print(f"Alignment rebuild: {cfg}", flush=True)
        usage = ApiUsage()
        all_cands: list[dict] = []
        for ex in excerpts:
            cands, pre, dup = extract_on_text(
                ex["excerpt_text"], cs, ov, client, usage
            )
            for c in cands:
                c["_excerpt_id"] = ex["excerpt_id"]
            all_cands.extend(cands)

        align, _, _ = build_alignment_rows(cfg, excerpts, all_cands, "stage1", 1)
        all_align.extend(align)
        api_rows.append(
            {
                "stage": "stage1_alignment_rebuild",
                "configuration": cfg,
                "repetition": 1,
                "api_calls": usage.calls,
                "total_tokens": usage.total_tokens,
                "estimated_usd": round(usage.estimated_usd(), 4),
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }
        )
    return all_align, api_rows


def rebuild_stage2_alignment(excerpts, client) -> tuple[list[dict], list[dict]]:
    sel = json.loads((EXPERIMENT_DIR / "STAGE2_CONFIG_SELECTION.json").read_text())
    configs = [
        (7, 2),
        (5, 3),
        (5, 2),
    ]
    all_align: list[dict] = []
    api_rows: list[dict] = []

    for cs, ov in configs:
        cfg = config_label(cs, ov)
        for rep in range(1, 4):
            print(f"Stage2 alignment: {cfg} rep {rep}", flush=True)
            usage = ApiUsage()
            all_cands: list[dict] = []
            for ex in excerpts:
                cands, _, _ = extract_on_text(ex["excerpt_text"], cs, ov, client, usage)
                for c in cands:
                    c["_excerpt_id"] = ex["excerpt_id"]
                all_cands.extend(cands)
            align, _, _ = build_alignment_rows(cfg, excerpts, all_cands, "stage2", rep)
            all_align.extend(align)
            api_rows.append(
                {
                    "stage": "stage2",
                    "configuration": cfg,
                    "repetition": rep,
                    "api_calls": usage.calls,
                    "total_tokens": usage.total_tokens,
                    "estimated_usd": round(usage.estimated_usd(), 4),
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                }
            )
    return all_align, api_rows


def load_existing_api_manifest() -> list[dict]:
    path = EXPERIMENT_DIR / "API_RUN_MANIFEST.csv"
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-stage3", action="store_true")
    parser.add_argument("--skip-alignment-rebuild", action="store_true")
    args = parser.parse_args()

    excerpts = load_excerpts()
    client = get_client()
    all_align: list[dict] = []
    api_manifest: list[dict] = []

    if not args.skip_alignment_rebuild:
        a1, m1 = rebuild_stage1_alignment(excerpts, client)
        a2, m2 = rebuild_stage2_alignment(excerpts, client)
        all_align.extend(a1)
        all_align.extend(a2)
        api_manifest.extend(m1)
        api_manifest.extend(m2)

    if not args.skip_stage3:
        print("=== Stage 3: full-hearing confirmatory ===", flush=True)
        stage3_configs = [(7, 2), (5, 3), (5, 2)]
        stage3_metrics, stage3_align = run_stage3(
            excerpts, stage3_configs, client, api_manifest
        )
        all_align.extend(stage3_align)
        stage3_rows = [metrics_to_row(m) for m in stage3_metrics]
        write_csv(
            EXPERIMENT_DIR / "03_CONFIRMATORY_RESULTS.csv",
            stage3_rows,
            list(stage3_rows[0].keys()),
        )
        lines = ["# Stage 3 — confirmatory full-hearing results", ""]
        for r in stage3_rows:
            lines.append(
                f"- **{r['configuration']}**: recovered {r['manual_decisions_recovered']}/6 "
                f"within annotated spans; candidates {r['candidate_total']}; "
                f"traceability {r['traceability_pct']}%"
            )
        (EXPERIMENT_DIR / "03_CONFIRMATORY_RESULTS.md").write_text(
            "\n".join(lines), encoding="utf-8"
        )
    else:
        (EXPERIMENT_DIR / "03_CONFIRMATORY_RESULTS.md").write_text(
            "# Stage 3 — not performed\n\nSkipped during finalize (Stage 1 + 2 complete).\n",
            encoding="utf-8",
        )

    if all_align:
        write_csv(
            EXPERIMENT_DIR / "GOLD_DECISION_ALIGNMENT.csv",
            all_align,
            list(all_align[0].keys()),
        )

    if api_manifest:
        write_csv(
            EXPERIMENT_DIR / "API_RUN_MANIFEST.csv",
            api_manifest,
            list(api_manifest[0].keys()),
        )

    print("Finalize complete.", flush=True)


if __name__ == "__main__":
    main()
