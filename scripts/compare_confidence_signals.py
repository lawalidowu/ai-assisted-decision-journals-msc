"""Phase 2b Q4 — compare rule + LLM confidence signals against human Rubric B.

Usage:
  python scripts/compare_confidence_signals.py
  python scripts/compare_confidence_signals.py --skip-llm
  python scripts/compare_confidence_signals.py --summary-only
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from decision_journal.confidence_signals import (  # noqa: E402
    call_llm_confidence,
    compare_signals,
    default_model,
    rule_based_confidence,
)
from decision_journal.extraction import get_client  # noqa: E402

SAMPLE_PATH = ROOT / "configs/evaluation/confidence_validation_sample.json"
OUTPUT_PATH = ROOT / "configs/evaluation/confidence_comparison_results.json"
LLM_CACHE_PATH = ROOT / "configs/evaluation/confidence_llm_cache.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def cache_key(item: dict) -> str:
    return str(item.get("journal_id") or f"sample_{item.get('sample_index')}")


def apply_signals(
    items: list[dict],
    *,
    skip_llm: bool,
    model: str,
    use_cache: bool,
) -> list[dict]:
    cache: dict[str, dict] = {}
    if use_cache and LLM_CACHE_PATH.is_file():
        cache = load_json(LLM_CACHE_PATH)

    client = None
    if not skip_llm:
        try:
            client = get_client()
        except RuntimeError as exc:
            print(f"Warning: {exc} — running rule baseline only.")
            skip_llm = True

    enriched: list[dict] = []
    for item in items:
        row = dict(item)
        row.update(rule_based_confidence(item))

        if skip_llm:
            row["llm_confidence"] = None
            row["llm_reasoning"] = None
            row["llm_error"] = "skipped"
        else:
            key = cache_key(item)
            if use_cache and key in cache:
                row.update(cache[key])
            else:
                llm_result = call_llm_confidence(
                    item.get("decision") or "",
                    item.get("source_quote"),
                    model=model,
                    client=client,
                )
                row.update(llm_result)
                cache[key] = {
                    "llm_confidence": row.get("llm_confidence"),
                    "llm_reasoning": row.get("llm_reasoning"),
                    "llm_error": row.get("llm_error"),
                }

        enriched.append(row)

    if not skip_llm and use_cache:
        save_json(LLM_CACHE_PATH, cache)

    return enriched


def calibration_table(items: list[dict], pred_key: str) -> dict[str, dict[str, float]]:
    """P(human_valid_decision | predicted confidence bin)."""
    bins: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for item in items:
        pred = item.get(pred_key)
        a = item.get("human_valid_decision")
        if pred not in ("low", "medium", "high") or not a:
            continue
        bins[pred][a] += 1

    out: dict[str, dict[str, float]] = {}
    for pred, counts in sorted(bins.items()):
        total = sum(counts.values())
        out[pred] = {
            k: round(v / total, 4) for k, v in sorted(counts.items())
        }
        out[pred]["n"] = total
    return out


def traceability_crosstab(items: list[dict], pred_key: str) -> dict[str, dict[str, int]]:
    table: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for item in items:
        pred = item.get(pred_key)
        if pred not in ("low", "medium", "high"):
            continue
        trace = item.get("traceability_ok")
        label = "pass" if trace is True else "fail" if trace is False else "na"
        table[pred][label] += 1
    return {k: dict(v) for k, v in table.items()}


def axb_human(items: list[dict], pred_key: str) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for item in items:
        a = item.get("human_valid_decision")
        p = item.get(pred_key)
        if a and p in ("low", "medium", "high"):
            counts[f"A={a}|pred={p}"] += 1
    return dict(counts)


def print_report(results: dict) -> None:
    print("=" * 72)
    print("PHASE 2b Q4 — CONFIDENCE SIGNAL COMPARISON (vs human Rubric B)")
    print("=" * 72)
    print(f"Rated items: {results['n_rated']}")
    print()

    for name in ("rule_vs_human_b", "llm_vs_human_b", "rule_vs_llm"):
        block = results["metrics"].get(name)
        if not block or block.get("n", 0) == 0:
            print(f"{name}: (not available)")
            continue
        print(f"{name}:")
        print(f"  n={block['n']}  exact_agreement={block['exact_agreement']}  weighted_kappa={block['weighted_kappa']}")
        print("  confusion (rows=human, cols=pred):")
        for row_label, row in block["confusion"].items():
            print(f"    {row_label}: {row}")
        print()

    print("Calibration P(A | pred bin) — Rubric A validity by signal:")
    for signal in ("rule_confidence", "llm_confidence"):
        cal = results.get("calibration_a", {}).get(signal)
        if cal:
            print(f"  {signal}:")
            for level, probs in cal.items():
                print(f"    {level}: {probs}")
    print()

    print("Traceability × rule_confidence:")
    for level, counts in results.get("traceability_rule", {}).items():
        print(f"  {level}: {counts}")
    print()

    llm_cal = results.get("calibration_a", {}).get("llm_confidence")
    if llm_cal:
        print("Traceability × llm_confidence:")
        for level, counts in results.get("traceability_llm", {}).items():
            print(f"  {level}: {counts}")


def build_results(items: list[dict], *, model: str, skip_llm: bool) -> dict:
    rated = [
        i
        for i in items
        if i.get("human_confidence") in ("low", "medium", "high")
        and i.get("human_valid_decision")
    ]

    metrics: dict[str, dict] = {
        "rule_vs_human_b": compare_signals(rated, pred_key="rule_confidence"),
    }
    if not skip_llm and any(i.get("llm_confidence") for i in rated):
        metrics["llm_vs_human_b"] = compare_signals(rated, pred_key="llm_confidence")
        metrics["rule_vs_llm"] = compare_signals(
            [i for i in rated if i.get("llm_confidence")],
            human_key="rule_confidence",
            pred_key="llm_confidence",
        )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(SAMPLE_PATH.relative_to(ROOT)).replace("\\", "/"),
        "model": model if not skip_llm else None,
        "n_rated": len(rated),
        "metrics": metrics,
        "calibration_a": {
            "rule_confidence": calibration_table(rated, "rule_confidence"),
            "llm_confidence": calibration_table(rated, "llm_confidence") if not skip_llm else {},
        },
        "traceability_rule": traceability_crosstab(rated, "rule_confidence"),
        "traceability_llm": traceability_crosstab(rated, "llm_confidence") if not skip_llm else {},
        "human_axb": axb_human(rated, "human_confidence"),
        "items": [
            {
                "sample_index": i.get("sample_index"),
                "journal_id": i.get("journal_id"),
                "human_valid_decision": i.get("human_valid_decision"),
                "human_confidence": i.get("human_confidence"),
                "rule_confidence": i.get("rule_confidence"),
                "rule_details": i.get("rule_details"),
                "llm_confidence": i.get("llm_confidence"),
                "llm_reasoning": i.get("llm_reasoning"),
                "llm_error": i.get("llm_error"),
                "traceability_ok": i.get("traceability_ok"),
                "stratum": i.get("stratum"),
            }
            for i in rated
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare confidence signals vs human Rubric B (Phase 2b Q4).")
    parser.add_argument("--skip-llm", action="store_true", help="Rule baseline only (no API calls)")
    parser.add_argument("--model", default="", help="OpenAI model (default: OPENAI_MODEL or gpt-4o-mini)")
    parser.add_argument("--no-cache", action="store_true", help="Do not read/write LLM cache")
    parser.add_argument("--summary-only", action="store_true", help="Print report from existing results JSON")
    parser.add_argument(
        "--output",
        default=str(OUTPUT_PATH),
        help="Results JSON path",
    )
    args = parser.parse_args()

    output_path = Path(args.output)

    if args.summary_only:
        if not output_path.is_file():
            parser.error(f"No results file: {output_path}")
        print_report(load_json(output_path))
        return

    if not SAMPLE_PATH.is_file():
        parser.error(f"Missing sample: {SAMPLE_PATH}")

    payload = load_json(SAMPLE_PATH)
    items = payload.get("items", [])
    model = args.model or default_model()

    enriched = apply_signals(
        items,
        skip_llm=args.skip_llm,
        model=model,
        use_cache=not args.no_cache,
    )

    results = build_results(enriched, model=model, skip_llm=args.skip_llm)
    save_json(output_path, results)
    print_report(results)
    print(f"\nWrote: {output_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
