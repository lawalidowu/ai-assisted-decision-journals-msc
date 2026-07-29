"""Summarize manual annotation triangulation from manual_phase1.json."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = ROOT / "configs/annotations/manual_phase1.json"
OUT_MD = ROOT / "docs/TRIANGULATION_SUMMARY.md"

INQUIRY_RUNS = [
    ("28 Nov 2023", "outputs/run_20260608_005512_module2_2023-11-28", None),
    ("30 Nov 2023", "outputs/run_20260609_014425_module2_2023-11-30", "outputs/run_20260608_003318_module2_2023-11-30"),
    ("01 Dec 2023", "outputs/run_20260609_014914_module2_2023-12-01", "outputs/run_20260608_004107_module2_2023-12-01"),
    ("07 Dec 2023", "outputs/run_20260609_070847_module2_2023-12-07", None),
    ("11 Dec 2023", "outputs/run_20260609_071309_module2_2023-12-11", None),
    ("13 Dec 2023", "outputs/run_20260609_071809_module2_2023-12-13", None),
    ("14 Dec 2023", "outputs/run_20260609_072425_module2_2023-12-14", None),
    ("23 May 2024", "outputs/run_20260609_072813_module2_2024-05-23", None),
]


def load_manifest(rel: str) -> dict | None:
    p = ROOT / rel / "manifest.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> None:
    data = json.loads(WORKBOOK.read_text(encoding="utf-8"))
    excerpts = data["excerpts"]

    tri_counts: Counter = Counter()
    rows = []
    manual_total = 0
    llm_compared = 0
    semantic_yes = semantic_partial = semantic_no = 0
    grace_scores = {"interpretability": [], "actionability": [], "nuance": [], "redundancy": []}

    for ex in excerpts:
        eid = ex["excerpt_id"]
        md = len(ex.get("manual_decisions", []))
        manual_total += md
        for c in ex.get("comparisons", []):
            tri = c.get("triangulation", "unknown")
            tri_counts[tri] += 1
            llm_compared += 1
            sg = c.get("semantic_grounding")
            if sg == "yes":
                semantic_yes += 1
            elif sg == "partial":
                semantic_partial += 1
            elif sg == "no":
                semantic_no += 1
            grace = c.get("grace") or {}
            for k in grace_scores:
                if k in grace and isinstance(grace[k], (int, float)):
                    grace_scores[k].append(grace[k])
            rows.append(
                {
                    "excerpt": eid,
                    "manual_id": c.get("manual_id"),
                    "llm_item_id": c.get("llm_item_id"),
                    "triangulation": tri,
                    "semantic_grounding": sg,
                    "notes": (c.get("triangulation_notes") or "")[:80],
                }
            )

    def mean(xs: list) -> str:
        return f"{sum(xs)/len(xs):.2f}" if xs else "—"

    lines = [
        "# Triangulation summary (Phase 1 manual annotation)",
        "",
        f"**Annotator:** {data.get('annotator', '—')}",
        f"**Workbook:** `configs/annotations/manual_phase1.json`",
        f"**Definition:** `{data.get('decision_definition_ref', 'docs/ANNOTATION_SESSION_NOTES.md')}`",
        "",
        "## Overview",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Excerpts annotated | {len(excerpts)} |",
        f"| Manual decisions (total) | {manual_total} |",
        f"| Comparison rows | {llm_compared} |",
        f"| Agreement | {tri_counts.get('agreement', 0)} |",
        f"| Complementary | {tri_counts.get('complementary', 0)} |",
        f"| Dissonance | {tri_counts.get('dissonance', 0)} |",
        f"| Silence | {tri_counts.get('silence', 0)} |",
        "",
        "## Semantic grounding (LLM items reviewed)",
        "",
        f"| yes | {semantic_yes} |",
        f"| partial | {semantic_partial} |",
        f"| no | {semantic_no} |",
        "",
        "## GRACE means (where scored)",
        "",
        "| Dimension | Mean (1–5) | n |",
        "|-----------|------------|---|",
    ]
    for dim, vals in grace_scores.items():
        lines.append(f"| {dim.capitalize()} | {mean(vals)} | {len(vals)} |")

    lines.extend(
        [
            "",
            "## Per-excerpt manual decisions",
            "",
            "| Excerpt | Transcript | Manual count | Comparisons |",
            "|---------|------------|--------------|-------------|",
        ]
    )
    for ex in excerpts:
        slug = ex["transcript_slug"].split("-on-")[-1].replace("-2023", "-23").replace("-2024", "-24")[:12]
        lines.append(
            f"| {ex['excerpt_id']} | …{slug} | {len(ex.get('manual_decisions', []))} | {len(ex.get('comparisons', []))} |"
        )

    lines.extend(["", "## Comparison detail", "", "| Excerpt | Manual | LLM | Triangulation | Grounding | Notes |", "|---------|--------|-----|---------------|-----------|-------|"])
    for r in rows:
        lines.append(
            f"| {r['excerpt']} | {r['manual_id'] or '—'} | {r['llm_item_id'] or '—'} | {r['triangulation']} | {r['semantic_grounding'] or '—'} | {r['notes']} |"
        )

    lines.extend(
        [
            "",
            "## LLM extraction runs referenced",
            "",
            "| Run | Transcript | Note |",
            "|-----|------------|------|",
        ]
    )
    for run in data.get("llm_runs", []):
        lines.append(f"| `{run['run_id']}` | {run['transcript_slug'][-20:]} | {run.get('note', '')} |")

    lines.extend(
        [
            "",
            "## `--inquiry` extraction runs (full transcripts)",
            "",
            "| Transcript | Mode | Decisions | Traceability pass | Pass rate |",
            "|------------|------|-----------|-------------------|-----------|",
        ]
    )
    for label, inquiry_path, default_path in INQUIRY_RUNS:
        m = load_manifest(inquiry_path)
        if not m:
            continue
        dc = m.get("decision_count", 0)
        tp = m.get("traceability_pass_count", 0)
        rate = f"{100*tp/dc:.0f}%" if dc else "—"
        mode = "inquiry" if m.get("inquiry_mode") else "default"
        lines.append(f"| {label} | {mode} | {dc} | {tp}/{dc} | {rate} |")

    lines.extend(
        [
            "",
            "### Before/after `--inquiry` (30 Nov & 01 Dec)",
            "",
            "| Transcript | Default decisions | Inquiry decisions |",
            "|------------|-------------------|-------------------|",
        ]
    )
    for label, inquiry_path, default_path in INQUIRY_RUNS:
        if not default_path:
            continue
        mi = load_manifest(inquiry_path)
        md = load_manifest(default_path)
        if not mi or not md:
            continue
        lines.append(
            f"| {label} | {md.get('decision_count', '—')} (non-inquiry) | {mi.get('decision_count', '—')} (inquiry) |"
        )

    lines.append("")
    lines.append("*Generated by `scripts/summarize_triangulation.py`*")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_MD}")
    print(dict(tri_counts))


if __name__ == "__main__":
    main()
