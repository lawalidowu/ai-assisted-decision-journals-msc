#!/usr/bin/env python3
"""Generate dissertation conceptual framework figure (Ch 3).

Usage:
    python scripts/build_conceptual_framework_figure.py
    python scripts/build_conceptual_framework_figure.py --output outputs/figures/conceptual_framework.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "outputs" / "figures" / "conceptual_framework.png"


def add_box(
    ax,
    x,
    y,
    w,
    h,
    title,
    subtitle,
    *,
    facecolor="#E8F0FE",
    edgecolor="#1A4480",
    title_size=9.0,
    subtitle_size=7.4,
):
    box = FancyBboxPatch(
        (x - w / 2, y - h / 2),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.05",
        linewidth=1.25,
        edgecolor=edgecolor,
        facecolor=facecolor,
    )
    ax.add_patch(box)
    if "\n" in title or "\n" in subtitle:
        ax.text(
            x,
            y,
            f"{title}\n{subtitle}",
            ha="center",
            va="center",
            fontsize=title_size,
            fontweight="bold",
            linespacing=1.25,
            color="#102A43",
            multialignment="center",
        )
    else:
        ax.text(
            x,
            y + 0.16,
            title,
            ha="center",
            va="center",
            fontsize=title_size,
            fontweight="bold",
            color="#102A43",
        )
        ax.text(
            x,
            y - 0.18,
            subtitle,
            ha="center",
            va="center",
            fontsize=subtitle_size,
            color="#334E68",
        )


def add_arrow(ax, x1, y1, x2, y2):
    ax.add_patch(
        FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            arrowstyle="-|>",
            mutation_scale=10,
            linewidth=1.1,
            color="#486581",
            shrinkA=1,
            shrinkB=1,
        )
    )


def build_figure(out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11.0, 11.8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 13.6)
    ax.axis("off")

    ax.add_patch(Rectangle((0.3, 6.55), 11.4, 6.65, linewidth=0, facecolor="#F5F7FA", zorder=0))
    ax.add_patch(Rectangle((0.3, 0.35), 11.4, 5.85, linewidth=0, facecolor="#F3FBF5", zorder=0))

    ax.text(
        0.5,
        12.9,
        "Phase 1 — extraction and source traceability",
        fontsize=11,
        fontweight="bold",
        color="#1A4480",
        ha="left",
        va="center",
    )
    ax.text(
        0.45,
        5.55,
        "Phase 2 — post-extraction\nreview and analysis",
        fontsize=10.5,
        fontweight="bold",
        color="#1B5E20",
        ha="left",
        va="center",
        linespacing=1.15,
    )

    cx = 6.0
    w_main = 5.2
    h_main = 0.88
    phase1 = [
        ("Public inquiry documents", "PDF hearing transcripts", "#F0F4F8"),
        ("LLM extraction", "Chunked inquiry prompt", "#E8F0FE"),
        ("Candidate decision objects", "Structured fields and provenance", "#E8F0FE"),
        ("Traceability check", "Source-quote verification", "#FFF4E5"),
        ("Fixed reference dataset", "414 candidate entries", "#FFE8CC"),
    ]

    y = 12.15
    step = 1.05
    ys = []
    for title, subtitle, color in phase1:
        add_box(ax, cx, y, w_main, h_main, title, subtitle, facecolor=color)
        ys.append(y)
        y -= step

    for i in range(len(ys) - 1):
        add_arrow(ax, cx, ys[i] - h_main / 2 - 0.02, cx, ys[i + 1] + h_main / 2 + 0.02)

    # Distribution rail under fixed reference dataset (single short drop, then fan-out)
    journal_y = ys[-1]
    rail_y = 5.15
    add_arrow(ax, cx, journal_y - h_main / 2 - 0.02, cx, rail_y + 0.06)
    xs = [1.7, 4.25, 7.75, 10.3]
    ax.plot([xs[0], xs[-1]], [rail_y, rail_y], color="#486581", linewidth=1.15, solid_capstyle="round")

    # Four independent Phase 2 branches in one row — no stacked connectors
    w_sub = 2.35
    h_sub = 1.35
    y_branch = 3.55
    phase2 = [
        (xs[0], "Review flags", "Procedural and\nduplicate risks", "#E6F4EA"),
        (xs[1], "n = 50 human\nvalidation", "Journal validity and\nevidence strength", "#E6F4EA"),
        (xs[2], "Exploratory\nclustering", "Navigation only", "#E8F5E9"),
        (xs[3], "n = 60 JEE/DQ\nmapping", "Preparedness and\nDecision Quality", "#E8F5E9"),
    ]
    for x, title, subtitle, color in phase2:
        add_box(
            ax,
            x,
            y_branch,
            w_sub,
            h_sub,
            title,
            subtitle,
            facecolor=color,
            edgecolor="#2E7D32",
            title_size=8.2,
            subtitle_size=6.8,
        )
        add_arrow(ax, x, rail_y - 0.02, x, y_branch + h_sub / 2 + 0.04)

    # Convergence rail and final human-review box
    conv_y = 1.95
    ax.plot([xs[0], xs[-1]], [conv_y, conv_y], color="#486581", linewidth=1.15, solid_capstyle="round")
    for x, *_ in phase2:
        add_arrow(ax, x, y_branch - h_sub / 2 - 0.03, x, conv_y + 0.04)

    y_final = 0.95
    add_box(
        ax,
        cx,
        y_final,
        5.8,
        0.95,
        "Human review and interpretation",
        "Final authority",
        facecolor="#FCE8E6",
        edgecolor="#8B1A1A",
        title_size=9.5,
        subtitle_size=8.0,
    )
    add_arrow(ax, cx, conv_y - 0.02, cx, y_final + 0.95 / 2 + 0.04)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=220, bbox_inches="tight", facecolor="white", pad_inches=0.25)
    plt.close(fig)
    print(f"Wrote {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build conceptual framework figure")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    build_figure(args.output)


if __name__ == "__main__":
    main()
