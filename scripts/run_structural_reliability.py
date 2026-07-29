"""Structural reliability mini-test — repeated inquiry extractions on fixed chunks.

Build manifest (10 chunks: 6 triangulation excerpts + 4 validation anchors):
  python scripts/run_structural_reliability.py --build-manifest

Run test (default 10 chunks × 5 regenerations at temperature=0.3):
  python scripts/run_structural_reliability.py

Production Phase 1 used temperature=0; use --temperature 0 for determinism check.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from decision_journal.extraction import get_client  # noqa: E402
from decision_journal.structural_reliability import (  # noqa: E402
    build_default_manifest,
    run_structural_reliability,
)

MANIFEST_PATH = ROOT / "configs/evaluation/structural_reliability_chunks.json"
OUTPUT_PATH = ROOT / "configs/evaluation/structural_reliability_results.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Structural reliability regeneration test")
    parser.add_argument(
        "--build-manifest",
        action="store_true",
        help="Write fixed 10-chunk manifest and exit",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=MANIFEST_PATH,
        help="Path to chunk manifest JSON",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_PATH,
        help="Path for results JSON",
    )
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI model name")
    parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Regenerations per chunk (Emmanuel-style consistency test)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.3,
        help="Sampling temperature (0=deterministic; 0.3+ for regeneration variance)",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Print summary from existing results file",
    )
    args = parser.parse_args()

    if args.build_manifest:
        manifest = build_default_manifest(ROOT)
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {len(manifest['chunks'])} chunks -> {args.manifest}")
        return

    if args.summary_only:
        if not args.output.exists():
            print(f"No results at {args.output}", file=sys.stderr)
            sys.exit(1)
        data = json.loads(args.output.read_text(encoding="utf-8"))
        summary = data.get("summary", {})
        print(json.dumps(summary, indent=2))
        rate = summary.get("structural_consistency_rate")
        if rate is not None:
            print(f"\nStructural consistency rate: {rate:.1%} ({summary.get('structural_pass_count')}/{summary.get('total_outputs')})")
        return

    if not args.manifest.exists():
        print(f"Manifest missing; run with --build-manifest first.", file=sys.stderr)
        sys.exit(1)

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    client = get_client()
    results = run_structural_reliability(
        manifest,
        model=args.model,
        runs=args.runs,
        temperature=args.temperature,
        client=client,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    s = results["summary"]
    print(f"Structural consistency rate: {s['structural_consistency_rate']:.1%}")
    print(f"  ({s['structural_pass_count']}/{s['total_outputs']} outputs passed all checks)")
    print(f"Results -> {args.output}")
    if s.get("check_failure_counts"):
        print("Check failures:", json.dumps(s["check_failure_counts"], indent=2))


if __name__ == "__main__":
    main()
