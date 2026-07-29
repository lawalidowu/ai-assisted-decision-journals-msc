"""Run decision extraction on a text file and save results under outputs/."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from decision_journal.extraction import extract_decisions, get_client, load_text_file  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract decisions from a text file")
    parser.add_argument("input", help="Path to .txt or .docx file")
    parser.add_argument("--model", default="", help="OpenAI model (default: OPENAI_MODEL or gpt-4o-mini)")
    parser.add_argument("--label", default="", help="Short label for the run folder name")
    parser.add_argument("--chunk-size", type=int, default=7)
    parser.add_argument("--chunk-overlap", type=int, default=2)
    parser.add_argument(
        "--inquiry",
        action="store_true",
        help="Inquiry transcript mode (stricter prompt, text normalization)",
    )
    args = parser.parse_args()

    import os

    model = args.model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    input_path = Path(args.input)
    text = load_text_file(input_path)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    label = args.label or input_path.stem
    run_dir = ROOT / "outputs" / f"run_{stamp}_{label}"
    run_dir.mkdir(parents=True, exist_ok=True)

    client = get_client()
    result = extract_decisions(
        text,
        model=model,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        client=client,
        inquiry_mode=args.inquiry,
        normalize_text=args.inquiry,
    )

    manifest = {
        "input_file": str(input_path.resolve()),
        "model": model,
        "chunk_size": args.chunk_size,
        "chunk_overlap": args.chunk_overlap,
        "inquiry_mode": args.inquiry,
        "chunk_count": result["chunk_count"],
        "decision_count": len(result["decisions"]),
        "chunk_errors": result["chunk_errors"],
        "traceability_issues": result["traceability_issues"],
        "traceability_pass_count": result["traceability_pass_count"],
        "traceability_fail_count": result["traceability_fail_count"],
    }

    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (run_dir / "decisions.json").write_text(
        json.dumps(result["decisions"], indent=2), encoding="utf-8"
    )
    if result["raw_outputs"]:
        (run_dir / "raw_llm_outputs.json").write_text(
            json.dumps(result["raw_outputs"], indent=2), encoding="utf-8"
        )

    print(f"Saved run to {run_dir}")
    print(f"Decisions extracted: {len(result['decisions'])}")
    if result["traceability_issues"]:
        issue_count = len(result["traceability_issues"])
        if issue_count > 10:
            print(
                f"Traceability: {result['traceability_pass_count']} pass, "
                f"{result['traceability_fail_count']} fail ({issue_count} issues)"
            )
        else:
            print("Traceability issues:", result["traceability_issues"])


if __name__ == "__main__":
    main()
