"""Phase 2c — thesis-oriented clustering figures.

Primary outputs (interpretable without low-variance PCA):
  - phase1_cluster_sizes.png          — theme distribution (main Results figure)
  - phase1_cluster_composition.png  — top clusters + example decisions (table)
  - phase1_clusters_flags_pca.png     — flags/traceability in embedding space

Optional appendix:
  - phase1_clusters_pca_appendix.png  (--appendix-pca only)

Also writes phase1_cluster_composition.md for direct paste into dissertation.

Usage:
  python scripts/visualize_clustering.py
  python scripts/visualize_clustering.py --appendix-pca
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from decision_journal.clustering import entry_embed_text, tfidf_embeddings  # noqa: E402

JOURNAL_PATH = ROOT / "data/manifests/phase1_decision_journal.json"
REPORT_PATH = ROOT / "data/manifests/phase1_clustering_report.json"
CACHE_PATH = ROOT / "data/manifests/phase1_embedding_cache.json"
FIG_DIR = ROOT / "outputs/figures"

CMAP = plt.colormaps.get_cmap("tab20")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_matrix(entries: list[dict], *, local: bool) -> tuple[np.ndarray, str]:
    if not local and CACHE_PATH.is_file():
        cache = load_json(CACHE_PATH)
        ids = [e["id"] for e in entries]
        missing = [eid for eid in ids if eid not in cache.get("embeddings", {})]
        if not missing:
            model = cache.get("model", "cached")
            matrix = np.asarray([cache["embeddings"][eid] for eid in ids], dtype=np.float64)
            return matrix, f"openai:{model}"

    texts = [entry_embed_text(e) for e in entries]
    return tfidf_embeddings(texts), "tfidf"


def truncate(text: str, max_len: int = 72) -> str:
    text = (text or "").strip()
    return text if len(text) <= max_len else text[: max_len - 1] + "…"


def sorted_clusters(report: dict) -> list[tuple[str, dict]]:
    clusters = report.get("clusters", {})
    rows = [(cid, block) for cid, block in clusters.items() if cid != "noise"]
    rows.sort(key=lambda x: x[1].get("size", 0), reverse=True)
    return rows


def plot_cluster_sizes(report: dict, out_path: Path) -> None:
    """Main thesis figure — theme sizes (no PCA)."""
    rows = sorted_clusters(report)
    if not rows:
        return

    n_total = report.get("n_entries", sum(b.get("size", 0) for _, b in rows))
    labels = [truncate(b.get("cluster_label") or f"Cluster {cid}") for cid, b in rows]
    sizes = [b.get("size", 0) for _, b in rows]
    pcts = [100.0 * s / n_total for s in sizes]

    fig, ax = plt.subplots(figsize=(10, max(5.5, 0.38 * len(rows))))
    colors = plt.colormaps["Blues"](np.linspace(0.35, 0.9, len(rows)))
    y_pos = np.arange(len(rows))
    ax.barh(y_pos, sizes, color=colors, edgecolor="white", linewidth=0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Number of decision-journal entries")
    ax.set_title(
        f"Thematic clusters in the Phase 1 journal (n={n_total}, k={len(rows)} themes)\n"
        "Agglomerative clustering on OpenAI embeddings — sizes only (full embedding space)"
    )
    xmax = max(sizes) * 1.15
    ax.set_xlim(0, xmax)
    for i, (n, pct) in enumerate(zip(sizes, pcts, strict=True)):
        ax.text(n + xmax * 0.01, i, f"{n}  ({pct:.0f}%)", va="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_composition_table(report: dict, out_path: Path, *, top_n: int = 8) -> None:
    """Table figure — top clusters with representative decisions."""
    rows = sorted_clusters(report)[:top_n]
    if not rows:
        return

    fig, ax = plt.subplots(figsize=(12, 0.55 + 0.65 * len(rows)))
    ax.axis("off")

    col_labels = ["Cluster", "Theme (candidate label)", "n", "Example decisions"]
    table_rows: list[list[str]] = []
    for cid, block in rows:
        examples = block.get("sample_decisions") or []
        ex_text = "\n".join(f"• {truncate(e, 68)}" for e in examples[:3])
        if not ex_text:
            ex_text = "—"
        table_rows.append(
            [
                str(cid),
                truncate(block.get("cluster_label") or f"cluster_{cid}", 48),
                str(block.get("size", 0)),
                ex_text,
            ]
        )

    table = ax.table(
        cellText=table_rows,
        colLabels=col_labels,
        loc="center",
        cellLoc="left",
        colLoc="left",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.8)

    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor("#2c3e50")
            cell.set_text_props(color="white", fontweight="bold")
        elif col == 0:
            cell.set_width(0.06)
        elif col == 2:
            cell.set_width(0.05)
        elif col == 3:
            cell.set_width(0.55)

    ax.set_title(
        f"Top {len(rows)} thematic clusters — representative extracted decisions\n"
        "(LLM-suggested labels pending Phase 2d human review)",
        fontsize=11,
        pad=12,
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def write_composition_markdown(report: dict, out_path: Path, *, top_n: int | None = None) -> None:
    rows = sorted_clusters(report)
    if top_n is not None:
        rows = rows[:top_n]

    lines = [
        "# Phase 1 journal — cluster composition",
        "",
        f"Total entries: {report.get('n_entries', '?')} · "
        f"Clusters: {report.get('n_clusters', '?')} · "
        f"Algorithm: {report.get('algorithm', '?')}",
        "",
        "| Cluster | n | Theme (candidate) | Example decisions |",
        "|---------|---|-------------------|-------------------|",
    ]
    for cid, block in rows:
        label = (block.get("cluster_label") or f"cluster_{cid}").replace("|", "/")
        examples = block.get("sample_decisions") or []
        ex = "; ".join(truncate(e, 60) for e in examples[:3]).replace("|", "/")
        lines.append(f"| {cid} | {block.get('size', 0)} | {label} | {ex} |")

    lines.append("")
    lines.append("*Labels pending Phase 2d supervisor review.*")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot_flags_overlay(
    xy: np.ndarray,
    entries: list[dict],
    out_path: Path,
    *,
    variance_note: str,
) -> None:
    categories: list[str] = []
    for e in entries:
        flags = e.get("phase2", {}).get("review_flags") or []
        if "procedural" in flags:
            categories.append("procedural")
        elif "possible_duplicate" in flags:
            categories.append("possible_duplicate")
        elif e.get("traceability_ok") is False:
            categories.append("traceability_fail")
        else:
            categories.append("unflagged_traceable")

    style = {
        "unflagged_traceable": ("#27ae60", "Unflagged, traceable"),
        "traceability_fail": ("#e67e22", "Traceability fail"),
        "possible_duplicate": ("#8e44ad", "Possible duplicate"),
        "procedural": ("#c0392b", "Procedural (flagged)"),
    }

    fig, ax = plt.subplots(figsize=(9, 7))
    for key in ("unflagged_traceable", "traceability_fail", "possible_duplicate", "procedural"):
        mask = np.array([c == key for c in categories])
        if not mask.any():
            continue
        color, label = style[key]
        ax.scatter(
            xy[mask, 0],
            xy[mask, 1],
            s=36,
            alpha=0.82,
            c=color,
            edgecolors="white",
            linewidths=0.35,
            label=f"{label} ({int(mask.sum())})",
        )

    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_title(
        "Review flags and traceability in embedding space (PCA projection)\n"
        f"{variance_note}\n"
        "Exploratory — connects Phase 2a flags to spatial concentration; not used for clustering."
    )
    ax.legend(loc="best", fontsize=9)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_pca_clusters_appendix(
    xy: np.ndarray,
    entries: list[dict],
    report: dict,
    out_path: Path,
    *,
    variance_note: str,
) -> None:
    id_to_label = {
        cid: block.get("cluster_label") or f"cluster_{cid}"
        for cid, block in report.get("clusters", {}).items()
    }
    cluster_ids = [e.get("phase2", {}).get("cluster_id", "?") for e in entries]
    unique = sorted(set(cluster_ids), key=lambda x: (x == "noise", str(x)))

    fig, ax = plt.subplots(figsize=(10, 7))
    for i, cid in enumerate(unique):
        mask = np.array([c == cid for c in cluster_ids])
        color = "#aaaaaa" if cid == "noise" else CMAP(i % 20)
        ax.scatter(
            xy[mask, 0],
            xy[mask, 1],
            s=22,
            alpha=0.65,
            c=[color],
            edgecolors="none",
        )

    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_title(
        f"Appendix — cluster-coloured PCA (low variance explained; interpret with caution)\n"
        f"{variance_note}"
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description="Thesis figures for Phase 2c clustering.")
    parser.add_argument("--local", action="store_true", help="TF-IDF if no embedding cache")
    parser.add_argument("--output-dir", default=str(FIG_DIR))
    parser.add_argument(
        "--appendix-pca",
        action="store_true",
        help="Also write low-information cluster-coloured PCA (appendix only)",
    )
    parser.add_argument("--top-n", type=int, default=8, help="Rows in composition table figure")
    args = parser.parse_args()

    if not JOURNAL_PATH.is_file() or not REPORT_PATH.is_file():
        print("Missing journal or clustering report — run run_clustering.py first.")
        return 1

    journal = load_json(JOURNAL_PATH)
    report = load_json(REPORT_PATH)
    entries = journal["entries"]

    if not any(e.get("phase2", {}).get("cluster_id") for e in entries):
        print("Journal has no cluster_id — run scripts/run_clustering.py first.")
        return 1

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    sizes_path = out_dir / "phase1_cluster_sizes.png"
    composition_path = out_dir / "phase1_cluster_composition.png"
    composition_md = out_dir / "phase1_cluster_composition.md"
    flags_path = out_dir / "phase1_clusters_flags_pca.png"

    plot_cluster_sizes(report, sizes_path)
    plot_composition_table(report, composition_path, top_n=args.top_n)
    write_composition_markdown(report, composition_md)

    matrix, embedding_name = load_matrix(entries, local=args.local)
    pca = PCA(n_components=2, random_state=42)
    xy = pca.fit_transform(matrix)
    var = pca.explained_variance_ratio_
    variance_note = (
        f"PCA for display only — {var[0]:.1%} + {var[1]:.1%} variance "
        f"({var[0] + var[1]:.1%} total); embedding: {embedding_name}"
    )

    plot_flags_overlay(xy, entries, flags_path, variance_note=variance_note)

    written = [sizes_path, composition_path, composition_md, flags_path]

    if args.appendix_pca:
        appendix_path = out_dir / "phase1_clusters_pca_appendix.png"
        plot_pca_clusters_appendix(xy, entries, report, appendix_path, variance_note=variance_note)
        written.append(appendix_path)

    # Remove legacy misleading default if present
    legacy = out_dir / "phase1_clusters_pca.png"
    if legacy.is_file() and not args.appendix_pca:
        legacy.unlink()

    print("Wrote thesis figures:")
    for p in written:
        print(f"  {p.relative_to(ROOT)}")
    if not args.appendix_pca:
        print("  (cluster-coloured PCA omitted — use --appendix-pca if needed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
