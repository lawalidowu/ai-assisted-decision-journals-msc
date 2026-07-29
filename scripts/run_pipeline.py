"""Orchestrate inquiry data pipeline stages."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from decision_journal.inquiry_batch_text import run_batch_text  # noqa: E402
from decision_journal.inquiry_client import InquiryFeedClient  # noqa: E402
from decision_journal.inquiry_download import run_download  # noqa: E402
from decision_journal.inquiry_harvest import (  # noqa: E402
    apply_phase1_selection,
    enrich_pdf_urls,
    harvest_corpus,
    load_config,
    write_manifest,
    write_manifest_json,
)


def stage_harvest(config_path: Path, *, resolve_pdfs: bool, quick: bool) -> Path:
    config = load_config(config_path)
    config["_root"] = str(config_path.parent.parent)
    if quick:
        for source in config.get("sources", []):
            source["max_pages"] = min(int(source.get("max_pages") or 3), 3)

    manifest_csv = ROOT / config["manifest_csv"]
    manifest_json = ROOT / config.get("manifest_json", manifest_csv.with_suffix(".json"))
    delay = float(config.get("delay_seconds", 0.75))

    with InquiryFeedClient(delay_seconds=delay) as client:
        records = harvest_corpus(config, client)
        apply_phase1_selection(records, config)
        if resolve_pdfs:
            phase1 = [r for r in records if r.get("selected_phase1") == "true"]
            enrich_pdf_urls(phase1, client)

    write_manifest(records, manifest_csv)
    write_manifest_json(records, manifest_json)
    selected = sum(1 for r in records if r.get("selected_phase1") == "true")
    print(f"Harvested {len(records)} records -> {manifest_csv}")
    print(f"Phase 1 selected: {selected}")
    return manifest_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="UK COVID-19 Inquiry data pipeline")
    parser.add_argument(
        "--config",
        default=str(ROOT / "configs" / "inquiry_corpus.json"),
        help="Path to inquiry corpus config JSON",
    )
    parser.add_argument(
        "--stage",
        choices=["harvest", "download", "text", "all"],
        default="all",
        help="Pipeline stage to run",
    )
    parser.add_argument("--quick", action="store_true", help="Limit harvest to 3 pages per source (smoke test)")
    parser.add_argument("--skip-pdf-urls", action="store_true", help="Skip resolving PDF URLs during harvest")
    parser.add_argument("--limit", type=int, default=None, help="Limit downloads/text conversions")
    parser.add_argument("--all-rows", action="store_true", help="Process all manifest rows, not only phase1")
    args = parser.parse_args()

    config_path = Path(args.config)
    config = load_config(config_path)
    manifest_csv = ROOT / config["manifest_csv"]
    raw_dir = ROOT / "data" / "raw" / "inquiry"
    processed_dir = ROOT / "data" / "processed" / "inquiry"
    only_phase1 = not args.all_rows
    delay = float(config.get("delay_seconds", 0.75))

    if args.stage in {"harvest", "all"}:
        manifest_csv = stage_harvest(
            config_path,
            resolve_pdfs=not args.skip_pdf_urls,
            quick=args.quick,
        )

    if args.stage in {"download", "all"}:
        if not manifest_csv.exists():
            raise SystemExit(f"Manifest not found: {manifest_csv}. Run --stage harvest first.")
        count = run_download(
            manifest_csv,
            raw_dir=raw_dir,
            only_phase1=only_phase1,
            limit=args.limit,
            delay_seconds=delay,
        )
        print(f"Downloaded {count} PDF(s)")

    if args.stage in {"text", "all"}:
        if not manifest_csv.exists():
            raise SystemExit(f"Manifest not found: {manifest_csv}")
        count = run_batch_text(
            manifest_csv,
            processed_dir=processed_dir,
            only_phase1=only_phase1,
            limit=args.limit,
        )
        print(f"Converted {count} PDF(s) to text")


if __name__ == "__main__":
    main()
