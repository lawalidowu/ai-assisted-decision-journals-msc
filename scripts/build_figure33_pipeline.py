#!/usr/bin/env python3
"""Generate Figure 3.2: technical implementation pipeline (methodology only)."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "outputs" / "figures" / "implemented_pipeline.png"


def add_box(
    ax,
    x: float,
    y: float,
    width: float,
    height: float,
    text: str,
    *,
    facecolor: str,
    edgecolor: str = "#333333",
    fontsize: float = 9.2,
    linewidth: float = 1.1,
) -> None:
    patch = FancyBboxPatch(
        (x - width / 2, y - height / 2),
        width,
        height,
        boxstyle="round,pad=0.025,rounding_size=0.05",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=linewidth,
    )
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize, linespacing=1.15)


def add_arrow(ax, start, end, *, dashed: bool = False) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=11,
            linewidth=1.05,
            linestyle="--" if dashed else "-",
            color="#444444",
            shrinkA=1,
            shrinkB=1,
        )
    )


def build_figure(output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10.2, 12.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 14.5)
    ax.axis("off")

    ax.add_patch(Rectangle((0.3, 7.55), 11.4, 6.55, linewidth=0, facecolor="#F5F7FA", zorder=0))
    ax.add_patch(Rectangle((0.3, 0.35), 11.4, 6.85, linewidth=0, facecolor="#F4FBF5", zorder=0))

    ax.text(0.5, 13.75, "A. Ingestion and extraction", fontsize=12, fontweight="bold", color="#1A4480")
    cx = 4.0
    stages = [
        (12.95, "Eight Phase 1 inquiry transcripts"),
        (12.15, "Metadata harvest  →  source manifest"),
        (11.35, "PDF download"),
        (10.55, "PDF-to-text and inquiry-aware normalisation"),
        (9.65, "Seven-sentence chunks; overlap two"),
        (8.75, "gpt-4o-mini inquiry-mode extraction\ntemperature = 0"),
        (7.75, "Structured decision objects\nand mechanical source-quote traceability"),
    ]
    prev = None
    for y, label in stages:
        add_box(ax, cx, y, 6.2, 0.68 if "\n" not in label else 0.85, label, facecolor="#EEF2F5", edgecolor="#465866")
        if prev is not None:
            add_arrow(ax, (cx, prev - 0.38), (cx, y + 0.38))
        prev = y

    # Manual evaluation side branch
    add_box(
        ax,
        9.55,
        10.35,
        3.8,
        2.35,
        "Manual Phase 1 evaluation\n"
        "• triangulation\n"
        "• GRACE-adapted assessment\n"
        "• error taxonomy\n"
        "• keyword baseline",
        facecolor="#FAFAFA",
        edgecolor="#666666",
        fontsize=8.8,
    )
    add_arrow(ax, (7.15, 9.65), (7.55, 10.0), dashed=True)

    ax.text(0.5, 6.95, "B. Fixed reference dataset", fontsize=12, fontweight="bold", color="#705E22")
    add_box(
        ax,
        6.0,
        6.15,
        8.4,
        1.05,
        "Fixed reference dataset\n414 candidate entries\nStable identifiers and provenance",
        facecolor="#FFF4D6",
        edgecolor="#705E22",
        fontsize=10.0,
        linewidth=1.3,
    )
    add_arrow(ax, (cx, 7.28), (6.0, 6.72))

    ax.text(0.5, 5.25, "C. Post-extraction review and analysis", fontsize=12, fontweight="bold", color="#1B5E20")

    # Distribution rail
    rail_y = 4.55
    add_arrow(ax, (6.0, 5.58), (6.0, rail_y + 0.05))
    ax.plot([1.4, 10.6], [rail_y, rail_y], color="#3F6544", linewidth=1.15)

    boxes = [
        (2.55, 3.35, "Non-destructive\nreview flags"),
        (5.0, 3.35, "n = 50 journal-validity\nand evidence-strength\nevaluation"),
        (7.45, 3.35, "Exploratory clustering\nfor navigation"),
        (9.9, 3.35, "n = 60 JEE/DQ\nframework-mapping\npilot"),
    ]
    for x, y, label in boxes:
        add_box(ax, x, y, 2.25, 1.55, label, facecolor="#E7F1E8", edgecolor="#3F6544", fontsize=8.6)
        add_arrow(ax, (x, rail_y - 0.02), (x, y + 0.82))

    conv_y = 1.85
    ax.plot([1.4, 10.6], [conv_y, conv_y], color="#3F6544", linewidth=1.15)
    for x, y, _ in boxes:
        add_arrow(ax, (x, y - 0.82), (x, conv_y + 0.04))

    add_box(
        ax,
        6.0,
        0.95,
        6.4,
        0.95,
        "Human review and interpretation\nFinal authority",
        facecolor="#FCE8E6",
        edgecolor="#8B1A1A",
        fontsize=9.5,
    )
    add_arrow(ax, (6.0, conv_y - 0.02), (6.0, 1.48))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight", facecolor="white", pad_inches=0.25)
    plt.close(fig)
    print(f"Wrote {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build technical implementation pipeline figure")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    build_figure(args.output)


if __name__ == "__main__":
    main()
