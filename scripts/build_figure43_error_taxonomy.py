#!/usr/bin/env python3
"""Generate Figure 4.3 from the committed error-taxonomy sample."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "configs" / "evaluation" / "error_taxonomy_sample.json"
DEFAULT_OUT = ROOT / "outputs" / "figures" / "error_taxonomy_distribution.png"

CATEGORY_LABELS = {
    "other": "Other",
    "valid_or_borderline": "Valid or borderline",
    "narrative_description": "Narrative description",
    "bundled_measures": "Bundled measures",
    "advocacy_urging": "Advocacy / urging",
    "future_recommendation": "Future recommendation",
    "traceability_fail": "Traceability failure",
    "duplicate": "Duplicate",
    "witness_opinion": "Witness opinion",
}


def load_sample(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON list in {path}")
    return data


def build_figure(source_path: Path, output_path: Path) -> None:
    sample = load_sample(source_path)
    counts = Counter(item["error_type"] for item in sample)
    unknown = set(counts) - set(CATEGORY_LABELS)
    if unknown:
        raise ValueError(f"Unlabelled taxonomy categories: {sorted(unknown)}")

    validation_counts = Counter(item["validation"] for item in sample)
    if len(sample) != 42:
        raise ValueError(f"Expected 42 taxonomy items, found {len(sample)}")
    if validation_counts != Counter({"heuristic_sample": 33, "author_triangulation": 9}):
        raise ValueError(f"Unexpected validation composition: {dict(validation_counts)}")

    source_order = list(CATEGORY_LABELS)
    ordered_categories = sorted(
        source_order,
        key=lambda category: (-counts[category], source_order.index(category)),
    )
    values = [counts[category] for category in ordered_categories]
    labels = [CATEGORY_LABELS[category] for category in ordered_categories]

    fig, ax = plt.subplots(figsize=(7.4, 5.4))
    bars = ax.barh(
        labels,
        values,
        color="#D5DCE2",
        edgecolor="#3D4A53",
        linewidth=0.9,
    )
    ax.invert_yaxis()
    ax.set_xlabel("Assigned items (count)")
    ax.set_title(
        f"Assigned taxonomy categories\nStratified extraction sample (n = {len(sample)})",
        fontsize=12,
        pad=11,
    )
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis="x", color="#D9D9D9", linewidth=0.7)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, max(values) + 2.0)

    for bar, value in zip(bars, values):
        ax.text(
            value + 0.25,
            bar.get_y() + bar.get_height() / 2,
            str(value),
            va="center",
            ha="left",
            fontsize=9.5,
            fontweight="bold",
        )

    fig.text(
        0.5,
        0.015,
        "Exactly one primary category per item (ordered first-match classification); "
        "9 author-validated and 33 heuristic-classified items.",
        ha="center",
        va="bottom",
        fontsize=8.5,
        color="#444444",
    )
    fig.tight_layout(rect=(0, 0.055, 1, 1))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Wrote {output_path}")
    print(f"Counts: {dict(counts)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Figure 4.3 taxonomy chart")
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    build_figure(args.source, args.output)


if __name__ == "__main__":
    main()
