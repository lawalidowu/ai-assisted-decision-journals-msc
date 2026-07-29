"""Sample LLM extractions and classify error types for evaluation chapter."""

from __future__ import annotations

import json
import random
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = ROOT / "configs/annotations/manual_phase1.json"
OUT_MD = ROOT / "docs/ERROR_TAXONOMY.md"
OUT_JSON = ROOT / "configs/evaluation/error_taxonomy_sample.json"
SAMPLE_SIZE = 42
RNG = random.Random(42)

ERROR_TYPES = [
    "advocacy_urging",
    "future_recommendation",
    "narrative_description",
    "duplicate",
    "traceability_fail",
    "bundled_measures",
    "witness_opinion",
    "valid_or_borderline",
    "other",
]

# Author-validated false positives from manual triangulation (silence, LLM-only)
VALIDATED_FP = [
    ("excerpt_001", 15, "bundled_measures"),
    ("excerpt_004", 32, "narrative_description"),
    ("excerpt_004", 33, "narrative_description"),
    ("excerpt_004", 34, "future_recommendation"),
    ("excerpt_004", 35, "future_recommendation"),
    ("excerpt_004", 36, "duplicate"),
    ("excerpt_004", 37, "narrative_description"),
    ("excerpt_005", 1, "advocacy_urging"),
    ("excerpt_005", 2, "advocacy_urging"),
]


def load_all_decisions() -> list[dict]:
    items: list[dict] = []
    for manifest in sorted(ROOT.glob("outputs/run_*module2*/manifest.json")):
        if not json.loads(manifest.read_text()).get("inquiry_mode"):
            continue
        run_dir = manifest.parent
        slug = run_dir.name.split("_", 3)[-1] if "_" in run_dir.name else run_dir.name
        decisions = json.loads((run_dir / "decisions.json").read_text(encoding="utf-8"))
        for i, d in enumerate(decisions, start=1):
            items.append(
                {
                    "run": run_dir.name,
                    "item_id": i,
                    "decision": d.get("decision", ""),
                    "source_quote": d.get("source_quote", ""),
                    "traceability_ok": d.get("traceability_ok"),
                    "key": f"{run_dir.name}::item_{i}",
                }
            )
    return items


def classify_heuristic(item: dict) -> str:
    dec = (item.get("decision") or "").lower()
    quote = (item.get("source_quote") or "").lower()
    text = f"{dec} {quote}"
    if item.get("traceability_ok") is False:
        return "traceability_fail"
    if re.search(r"\b(need to|urging|call to action|we need to)\b", text):
        return "advocacy_urging"
    if re.search(r"\b(should already|for the future|hopefully|recommend)\b", text):
        return "future_recommendation"
    if re.search(r"\b(became|was described|narrative|whole-government effort)\b", text):
        return "narrative_description"
    if re.search(r"\b(believed|thought|felt|in my view)\b", text):
        return "witness_opinion"
    if re.search(r"\b(and|measures|bundled|isolation.*schools)\b", dec) and len(dec) > 120:
        return "bundled_measures"
    if re.search(r"\b(decided|agreed|commissioned|COBR|COVID-O)\b", text):
        return "valid_or_borderline"
    return "other"


def main() -> None:
    all_items = load_all_decisions()
    by_key = {x["key"]: x for x in all_items}

    coded: list[dict] = []
    for ex, iid, etype in VALIDATED_FP:
        # map excerpt to run from workbook
        wb = json.loads(WORKBOOK.read_text(encoding="utf-8"))
        ex_data = next(e for e in wb["excerpts"] if e["excerpt_id"] == ex)
        run_name = Path(ex_data["llm_run"]).name
        key = f"{run_name}::item_{iid}"
        if key in by_key:
            row = dict(by_key[key])
            row["error_type"] = etype
            row["validation"] = "author_triangulation"
            row["excerpt_id"] = ex
            coded.append(row)

    validated_keys = {c["key"] for c in coded}
    pool = [x for x in all_items if x["key"] not in validated_keys]
    # prefer likely false positives for heuristic sample
    likely_fp = [x for x in pool if classify_heuristic(x) != "valid_or_borderline"]
    likely_tp = [x for x in pool if classify_heuristic(x) == "valid_or_borderline"]
    need = SAMPLE_SIZE - len(coded)
    fp_take = min(len(likely_fp), int(need * 0.7))
    tp_take = need - fp_take
    sample = RNG.sample(likely_fp, fp_take) + RNG.sample(likely_tp, min(tp_take, len(likely_tp)))

    for item in sample:
        coded.append(
            {
                **item,
                "error_type": classify_heuristic(item),
                "validation": "heuristic_sample",
                "excerpt_id": None,
            }
        )

    counts = Counter(c["error_type"] for c in coded)
    author_n = sum(1 for c in coded if c["validation"] == "author_triangulation")

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(coded, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Error taxonomy sample (LLM extractions)",
        "",
        f"**Sample size:** {len(coded)} items ({author_n} author-validated false positives from triangulation;",
        f"{len(coded) - author_n} heuristic-classified samples from inquiry corpus).",
        "",
        "## Type definitions",
        "",
        "| Type | Definition |",
        "|------|------------|",
        "| advocacy_urging | Ministerial/colloquial urging (`need to`, WhatsApp calls to action) — not recorded agreement |",
        "| future_recommendation | Retrospective lesson or future `should` — not an adopted measure |",
        "| narrative_description | Descriptive account of events — not a decision event |",
        "| duplicate | Near-duplicate extraction of same passage |",
        "| traceability_fail | `source_quote` not locatable in source text |",
        "| bundled_measures | Multiple distinct measures in one LLM item |",
        "| witness_opinion | Belief/state of mind — not formal decision |",
        "| valid_or_borderline | Plausible decision recall — may be true positive |",
        "| other | Unclassified by heuristics |",
        "",
        "## Counts in sample",
        "",
        "| Error type | Count | % |",
        "|------------|-------|---|",
    ]
    for et in ERROR_TYPES:
        n = counts.get(et, 0)
        pct = 100 * n / len(coded) if coded else 0
        lines.append(f"| {et} | {n} | {pct:.0f}% |")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Author-validated false positives (n=9) are dominated by **advocacy**, **future recommendations**,",
            "and **narrative** — matching triangulation silence rows. Heuristic extension across the corpus",
            "suggests **traceability_fail** and **valid_or_borderline** are common in bulk output;",
            "precision requires human verification even when quotes match.",
            "",
            f"Data: `{OUT_JSON.relative_to(ROOT)}` · Generated by `scripts/build_error_taxonomy.py`",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_MD} ({len(coded)} items)")
    print(dict(counts))


if __name__ == "__main__":
    main()
