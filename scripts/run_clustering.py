"""Phase 2c — run embedding clustering on the canonical decision journal (414 entries).

Usage:
  python scripts/run_clustering.py --local
  python scripts/run_clustering.py
  python scripts/run_clustering.py --skip-labels
  python scripts/run_clustering.py --summary-only
  python scripts/visualize_clustering.py
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from decision_journal.clustering import (  # noqa: E402
    HAS_HDBSCAN,
    assign_clusters_to_entries,
    build_cluster_report,
    cluster_embeddings,
    default_chat_model,
    default_embedding_model,
    entry_embed_text,
    label_clusters,
    openai_embeddings,
    tfidf_embeddings,
)
from decision_journal.extraction import get_client  # noqa: E402

JOURNAL_PATH = ROOT / "data/manifests/phase1_decision_journal.json"
REPORT_PATH = ROOT / "data/manifests/phase1_clustering_report.json"
EMBEDDING_CACHE_PATH = ROOT / "data/manifests/phase1_embedding_cache.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def get_embeddings(
    entries: list[dict],
    *,
    local: bool,
    embedding_model: str,
    use_cache: bool,
) -> tuple[np.ndarray, str]:
    texts = [entry_embed_text(e) for e in entries]
    ids = [e["id"] for e in entries]

    if local:
        return tfidf_embeddings(texts), "tfidf"

    cache: dict = {}
    if use_cache and EMBEDDING_CACHE_PATH.is_file():
        cache = load_json(EMBEDDING_CACHE_PATH)

    missing_idx = [i for i, eid in enumerate(ids) if eid not in cache]
    if missing_idx:
        client = get_client()
        missing_texts = [texts[i] for i in missing_idx]
        vectors = openai_embeddings(missing_texts, model=embedding_model, client=client)
        for i, vec in zip(missing_idx, vectors, strict=True):
            cache[ids[i]] = vec.tolist()
        if use_cache:
            save_json(
                EMBEDDING_CACHE_PATH,
                {
                    "model": embedding_model,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "embeddings": cache,
                },
            )

    matrix = np.asarray([cache[eid] for eid in ids], dtype=np.float64)
    return matrix, f"openai:{embedding_model}"


def print_summary(report: dict, algorithm: str, embedding: str) -> None:
    print("=" * 72)
    print("PHASE 2c — CLUSTERING SUMMARY")
    print("=" * 72)
    print(f"Entries: {report['n_entries']}")
    print(f"Clusters (excl. noise): {report['n_clusters']}")
    print(f"Noise / unclustered: {report['n_noise']}")
    print(f"Embedding: {embedding}")
    print(f"Algorithm: {algorithm}")
    print(f"HDBSCAN available: {HAS_HDBSCAN}")
    print()
    print(f"{'ID':<8} {'size':>5}  {'trace':>5}  label")
    print("-" * 72)
    for cid, block in sorted(
        report["clusters"].items(),
        key=lambda x: (-x[1]["size"], x[0]),
    ):
        trace = block.get("traceability_pass", 0)
        label = block.get("cluster_label") or "(pending 2d review)"
        print(f"{cid:<8} {block['size']:>5}  {trace:>5}  {label}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 2c clustering on phase1_decision_journal.json")
    parser.add_argument("--local", action="store_true", help="TF-IDF embeddings (no OpenAI API)")
    parser.add_argument("--skip-labels", action="store_true", help="Skip LLM cluster label suggestions (2d)")
    parser.add_argument("--embedding-model", default="", help="OpenAI embedding model")
    parser.add_argument("--label-model", default="", help="OpenAI chat model for cluster labels")
    parser.add_argument("--min-cluster-size", type=int, default=5)
    parser.add_argument(
        "--algorithm",
        choices=("auto", "agglomerative", "dbscan", "hdbscan"),
        default="auto",
    )
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Report only; do not update journal")
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args()

    if args.summary_only:
        if not REPORT_PATH.is_file():
            print(f"Missing report: {REPORT_PATH}")
            return 1
        report = load_json(REPORT_PATH)
        print_summary(report, report.get("algorithm", "?"), report.get("embedding", "?"))
        return 0

    if not JOURNAL_PATH.is_file():
        print(f"Missing journal: {JOURNAL_PATH}")
        return 1

    journal = load_json(JOURNAL_PATH)
    entries = journal["entries"]
    embedding_model = args.embedding_model or default_embedding_model()
    label_model = args.label_model or default_chat_model()

    try:
        matrix, embedding_name = get_embeddings(
            entries,
            local=args.local,
            embedding_model=embedding_model,
            use_cache=not args.no_cache,
        )
    except RuntimeError as exc:
        if args.local:
            raise
        print(f"OpenAI embeddings unavailable ({exc}); falling back to --local TF-IDF.")
        matrix, embedding_name = get_embeddings(
            entries,
            local=True,
            embedding_model=embedding_model,
            use_cache=False,
        )

    labels, algorithm = cluster_embeddings(
        matrix,
        algorithm=args.algorithm,
        min_cluster_size=args.min_cluster_size,
    )

    cluster_meta: dict[int, dict] = {}
    if not args.skip_labels and not args.local:
        try:
            cluster_meta = label_clusters(entries, labels, model=label_model)
        except RuntimeError as exc:
            print(f"Warning: cluster labelling skipped ({exc})")
    elif not args.skip_labels and args.local:
        # Generic labels from top TF-IDF terms could be added later; keep IDs for 2d review.
        for label in set(int(x) for x in labels if x != -1):
            cluster_meta[label] = {
                "cluster_label": f"cluster_{label}",
                "cluster_label_notes": "Auto placeholder — human review required (Phase 2d)",
                "cluster_label_error": None,
            }

    report = build_cluster_report(entries, labels, cluster_meta)
    report["generated_at"] = datetime.now(timezone.utc).isoformat()
    report["embedding"] = embedding_name
    report["algorithm"] = algorithm
    report["min_cluster_size"] = args.min_cluster_size
    report["label_model"] = None if args.skip_labels else label_model

    save_json(REPORT_PATH, report)
    print_summary(report, algorithm, embedding_name)

    if args.dry_run:
        print("\nDry run — journal not updated.")
        return 0

    assign_clusters_to_entries(entries, labels, cluster_meta)

    journal["version"] = "1.2"
    journal["schema_note"] = (
        "v1.2 = Phase 2c clustering applied. Re-run build_phase1_journal.py resets cluster fields."
    )
    steps = journal.get("phase2_steps", [])
    if "2c_clustering" not in steps:
        steps.append("2c_clustering")
    journal["phase2_steps"] = steps
    journal["phase2c_applied_at"] = datetime.now(timezone.utc).isoformat()
    journal["clustering"] = {
        "embedding": embedding_name,
        "algorithm": algorithm,
        "n_clusters": report["n_clusters"],
        "n_noise": report["n_noise"],
        "report": str(REPORT_PATH.relative_to(ROOT)).replace("\\", "/"),
    }

    save_json(JOURNAL_PATH, journal)
    print(f"\nUpdated journal: {JOURNAL_PATH.relative_to(ROOT)}")
    print(f"Wrote report: {REPORT_PATH.relative_to(ROOT)}")
    print("Phase 2d: review cluster_label values in report before thesis finalisation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
