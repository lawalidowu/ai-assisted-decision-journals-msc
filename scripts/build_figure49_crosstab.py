#!/usr/bin/env python3
"""Generate Figure 4.9 — Rubric A × Rubric B cross-tabulation heatmap (n = 50).

Usage:
    python scripts/build_figure49_crosstab.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "figures" / "figure4_9_rubric_crosstab.png"

# Rows: Rubric A (yes, no, unclear); Cols: Rubric B (high, medium, low)
MATRIX = np.array(
    [
        [11, 0, 0],
        [21, 11, 1],
        [5, 1, 0],
    ]
)
ROW_LABELS = ["yes", "no", "unclear"]
COL_LABELS = ["high", "medium", "low"]


def main() -> None:
    fig, ax = plt.subplots(figsize=(5.5, 4.2))
    im = ax.imshow(MATRIX, cmap="YlOrRd", vmin=0, vmax=21)

    ax.set_xticks(range(3))
    ax.set_yticks(range(3))
    ax.set_xticklabels(COL_LABELS)
    ax.set_yticklabels(ROW_LABELS)
    ax.set_xlabel("Rubric B — evidence strength")
    ax.set_ylabel("Rubric A — journal validity")

    for i in range(3):
        for j in range(3):
            val = int(MATRIX[i, j])
            color = "white" if val >= 11 else "black"
            ax.text(j, i, str(val), ha="center", va="center", fontsize=14, fontweight="bold", color=color)

    ax.set_title("Rubric A × Rubric B (n = 50)", fontsize=11, pad=10)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="Count")
    fig.tight_layout()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
