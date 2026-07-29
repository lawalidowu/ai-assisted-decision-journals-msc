"""Phase 2c — embedding-based clustering for the canonical decision journal."""

from __future__ import annotations

import json
import os
from collections import Counter, defaultdict, defaultdict
from typing import Any

import numpy as np
from sklearn.cluster import AgglomerativeClustering, DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_distances
from sklearn.preprocessing import normalize

from decision_journal.extraction import get_client, normalize_json_output

try:
    import hdbscan  # type: ignore

    HAS_HDBSCAN = True
except ImportError:
    HAS_HDBSCAN = False


def entry_embed_text(entry: dict[str, Any]) -> str:
    parts = [
        entry.get("decision") or "",
        entry.get("evidence") or "",
        entry.get("source_quote") or "",
    ]
    text = "\n".join(p.strip() for p in parts if p and p.strip())
    return text or "(empty)"


def tfidf_embeddings(texts: list[str]) -> np.ndarray:
    vectorizer = TfidfVectorizer(
        max_features=6000,
        ngram_range=(1, 2),
        min_df=2,
        stop_words="english",
    )
    matrix = vectorizer.fit_transform(texts)
    dense = normalize(matrix, norm="l2").toarray()
    return dense


def openai_embeddings(
    texts: list[str],
    *,
    model: str,
    client: Any | None = None,
    batch_size: int = 100,
) -> np.ndarray:
    client = client or get_client()
    vectors: list[list[float]] = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        response = client.embeddings.create(input=batch, model=model)
        vectors.extend(item.embedding for item in response.data)
    return np.asarray(vectors, dtype=np.float64)


def cluster_embeddings(
    matrix: np.ndarray,
    *,
    algorithm: str = "auto",
    min_cluster_size: int = 5,
) -> tuple[np.ndarray, str]:
    """Return cluster labels (-1 = noise) and algorithm used."""
    if matrix.shape[0] < 2:
        return np.zeros(matrix.shape[0], dtype=int), "singleton"

    if algorithm in ("auto", "hdbscan") and HAS_HDBSCAN:
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=max(2, min_cluster_size // 2),
            metric="euclidean",
            cluster_selection_method="eom",
        )
        labels = clusterer.fit_predict(matrix)
        noise_ratio = float(np.sum(labels == -1)) / len(labels)
        if noise_ratio <= 0.45:
            return labels, "hdbscan"

    if algorithm == "dbscan":
        labels = DBSCAN(
            eps=0.42,
            min_samples=min_cluster_size,
            metric="cosine",
        ).fit_predict(matrix)
        return labels, "dbscan"

    # Agglomerative default (sklearn) — tuned for ~12–25 themes on n≈400.
    dist = cosine_distances(matrix)
    agg = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=0.68,
        metric="precomputed",
        linkage="average",
    )
    labels = agg.fit_predict(dist)
    return labels, "agglomerative"


CLUSTER_LABEL_PROMPT = """
You are labelling a cluster of UK COVID-19 inquiry decision-journal entries.

Given representative DECISION lines from one unsupervised cluster, propose ONE short theme label (3–7 words).
The label should describe the policy/governance theme, not extraction quality.
If the cluster is mixed procedural/inquiry noise, say so plainly.

Return JSON only:
{{"cluster_label": "...", "notes": "one sentence"}}

DECISIONS:
{decisions}
"""


def suggest_cluster_label(
    decisions: list[str],
    *,
    model: str,
    client: Any | None = None,
) -> dict[str, str | None]:
    client = client or get_client()
    sample = decisions[:8]
    prompt = CLUSTER_LABEL_PROMPT.format(decisions="\n".join(f"- {d}" for d in sample))
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    raw = (response.choices[0].message.content or "").strip()
    try:
        parsed = json.loads(normalize_json_output(raw))
        return {
            "cluster_label": str(parsed.get("cluster_label", "")).strip() or None,
            "cluster_label_notes": str(parsed.get("notes", "")).strip() or None,
            "cluster_label_error": None,
        }
    except json.JSONDecodeError as exc:
        return {
            "cluster_label": None,
            "cluster_label_notes": None,
            "cluster_label_error": str(exc),
        }


def label_clusters(
    entries: list[dict[str, Any]],
    labels: np.ndarray,
    *,
    model: str,
    client: Any | None = None,
) -> dict[int, dict]:
    by_cluster: dict[int, list[str]] = defaultdict(list)
    for entry, label in zip(entries, labels, strict=True):
        if label == -1:
            continue
        by_cluster[int(label)].append(entry.get("decision") or "")

    meta: dict[int, dict] = {}
    client = client or get_client()
    for label in sorted(by_cluster):
        result = suggest_cluster_label(by_cluster[label], model=model, client=client)
        meta[label] = result
    return meta


def build_cluster_report(
    entries: list[dict[str, Any]],
    labels: np.ndarray,
    cluster_meta: dict[int | str, dict[str, Any]],
) -> dict[str, Any]:
    clusters: dict[str, dict[str, Any]] = {}
    for label in sorted(set(labels), key=lambda x: (x == -1, x)):
        key = "noise" if label == -1 else str(int(label))
        members = [e for e, lab in zip(entries, labels, strict=True) if lab == label]
        flag_counts: Counter[str] = Counter()
        trace_pass = 0
        for entry in members:
            for flag in entry.get("phase2", {}).get("review_flags") or []:
                flag_counts[flag] += 1
            if entry.get("traceability_ok"):
                trace_pass += 1

        meta = cluster_meta.get(label, {})
        clusters[key] = {
            "cluster_id": key,
            "size": len(members),
            "cluster_label": meta.get("cluster_label"),
            "cluster_label_notes": meta.get("cluster_label_notes"),
            "label_pending_review": True,
            "traceability_pass": trace_pass,
            "review_flag_counts": dict(flag_counts),
            "sample_decisions": [m.get("decision", "")[:200] for m in members[:5]],
            "member_ids": [m["id"] for m in members],
        }

    return {
        "n_entries": len(entries),
        "n_clusters": sum(1 for k in clusters if k != "noise"),
        "n_noise": clusters.get("noise", {}).get("size", 0),
        "clusters": clusters,
    }


def assign_clusters_to_entries(
    entries: list[dict[str, Any]],
    labels: np.ndarray,
    cluster_meta: dict[int | str, dict[str, Any]],
) -> None:
    for entry, label in zip(entries, labels, strict=True):
        entry.setdefault("phase2", {})
        if label == -1:
            entry["phase2"]["cluster_id"] = "noise"
            entry["phase2"]["cluster_label"] = "Unclustered / noise"
        else:
            cid = str(int(label))
            entry["phase2"]["cluster_id"] = cid
            meta = cluster_meta.get(int(label), {})
            entry["phase2"]["cluster_label"] = meta.get("cluster_label") or f"cluster_{cid}"


def default_embedding_model() -> str:
    return os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")


def default_chat_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")
