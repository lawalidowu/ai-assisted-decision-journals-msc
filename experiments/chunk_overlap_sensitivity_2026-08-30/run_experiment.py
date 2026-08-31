#!/usr/bin/env python3
"""Bounded chunk/overlap sensitivity experiment — isolated wrapper.

Does NOT modify production scripts or frozen artefacts.
All outputs written under experiments/chunk_overlap_sensitivity_2026-08-30/.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from decision_journal.extraction import (  # noqa: E402
    INQUIRY_PROMPT_TEMPLATE,
    chunk_text_by_sentences,
    clean_inquiry_text,
    dedupe_decisions,
    get_client,
    load_text_file,
    normalize_json_output,
    quote_found_in_text,
    validate_traceability,
)

EXPERIMENT_DIR = Path(__file__).resolve().parent
EXCERPT_DIR = ROOT / "configs/annotations/excerpts"
STAGE3_HEARINGS = {
    "2023-11-28": ROOT
    / "data/processed/inquiry/document/transcript-of-module-2-public-hearing-on-28-november-2023.txt",
    "2023-11-30": ROOT
    / "data/processed/inquiry/document/transcript-of-module-2-public-hearing-on-30-november-2023.txt",
    "2023-12-01": ROOT
    / "data/processed/inquiry/document/transcript-of-module-2-public-hearing-on-01-december-2023.txt",
}

CONFIG_GRID = [(w, o) for w in (5, 7, 9, 11) for o in (1, 2, 3)]
MODEL = "gpt-4o-mini"
TEMPERATURE = 0
MANUAL_DECISION_TOTAL = 6
# gpt-4o-mini approximate pricing (USD per 1M tokens) — experiment accounting only
PRICE_INPUT_PER_M = 0.15
PRICE_OUTPUT_PER_M = 0.60


def config_label(chunk_size: int, overlap: int) -> str:
    return f"w{chunk_size}_o{overlap}"


def overlaps(a: str, b: str, min_len: int = 25) -> bool:
    """Deterministic alignment from scripts/keyword_baseline.py."""
    a, b = (a or "").lower(), (b or "").lower()
    if not a or not b:
        return False
    if a in b or b in a:
        return True
    for i in range(max(0, len(a) - min_len + 1)):
        sub = a[i : i + min_len]
        if sub in b:
            return True
    return False


def mechanical_quote_match(candidate_quote: str, manual_quote: str) -> bool:
    if overlaps(candidate_quote, manual_quote):
        return True
    return quote_found_in_text(manual_quote, candidate_quote) or quote_found_in_text(
        candidate_quote, manual_quote
    )


def semantic_match(candidate: dict, manual: dict) -> bool:
    fields_c = [candidate.get("decision", ""), candidate.get("evidence", "")]
    fields_m = [manual.get("decision", ""), manual.get("source_quote", "")]
    for c in fields_c:
        for m in fields_m:
            if overlaps(c, m):
                return True
    return False


def assess_pair(candidate: dict, manual: dict) -> tuple[bool, bool, str]:
    mech = mechanical_quote_match(
        str(candidate.get("source_quote", "")), str(manual.get("source_quote", ""))
    )
    sem = semantic_match(candidate, manual)
    if mech and sem:
        basis = "mechanical_and_semantic"
    elif mech:
        basis = "mechanical_only"
    elif sem:
        basis = "semantic_only"
    else:
        basis = "none"
    recovered = mech and sem
    return recovered, mech, basis


@dataclass
class ApiUsage:
    calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    wall_seconds: float = 0.0

    def add(self, usage: Any, elapsed: float) -> None:
        self.calls += 1
        self.wall_seconds += elapsed
        if usage:
            self.prompt_tokens += getattr(usage, "prompt_tokens", 0) or 0
            self.completion_tokens += getattr(usage, "completion_tokens", 0) or 0
            self.total_tokens += getattr(usage, "total_tokens", 0) or 0

    def estimated_usd(self) -> float:
        return (
            self.prompt_tokens * PRICE_INPUT_PER_M + self.completion_tokens * PRICE_OUTPUT_PER_M
        ) / 1_000_000


@dataclass
class RunMetrics:
    chunk_size: int
    overlap: int
    stage: str
    repetition: int = 1
    scope: str = "excerpts"
    manual_recovered: int = 0
    manual_total: int = MANUAL_DECISION_TOTAL
    candidate_total: int = 0
    pre_dedupe_total: int = 0
    duplicate_removed: int = 0
    traceable_count: int = 0
    unmatched_candidates: int = 0
    api_usage: ApiUsage = field(default_factory=ApiUsage)
    per_excerpt_candidates: dict[str, int] = field(default_factory=dict)
    invalid_config: bool = False
    invalid_reason: str = ""

    @property
    def recall(self) -> float:
        return self.manual_recovered / self.manual_total if self.manual_total else 0.0

    @property
    def traceability_pct(self) -> float:
        return 100.0 * self.traceable_count / self.candidate_total if self.candidate_total else 0.0

    @property
    def duplicate_pct(self) -> float:
        return (
            100.0 * self.duplicate_removed / self.pre_dedupe_total if self.pre_dedupe_total else 0.0
        )


def load_excerpts() -> list[dict]:
    excerpts = []
    for i in range(1, 7):
        path = EXCERPT_DIR / f"excerpt_{i:03d}.json"
        excerpts.append(json.loads(path.read_text(encoding="utf-8")))
    return excerpts


def call_extractor_with_usage(
    text: str,
    model: str,
    client,
    usage_acc: ApiUsage,
) -> tuple[str, list[dict], str]:
    prompt = INQUIRY_PROMPT_TEMPLATE.format(text=text)
    t0 = time.perf_counter()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=TEMPERATURE,
    )
    usage_acc.add(response.usage, time.perf_counter() - t0)
    output = (response.choices[0].message.content or "").strip()
    normalized = normalize_json_output(output)
    try:
        parsed = json.loads(normalized)
        if not isinstance(parsed, list):
            return output, [], "invalid_json_shape"
        return output, parsed, ""
    except json.JSONDecodeError:
        return output, [], "invalid_json"


def extract_on_text(
    text: str,
    chunk_size: int,
    overlap: int,
    client,
    usage_acc: ApiUsage,
) -> tuple[list[dict], int, int]:
    text = clean_inquiry_text(text)
    chunks = chunk_text_by_sentences(text, chunk_size=chunk_size, overlap=overlap)
    merged: list[dict] = []
    for chunk in chunks:
        _, parsed, error = call_extractor_with_usage(chunk, MODEL, client, usage_acc)
        if error:
            continue
        for item in parsed:
            item = dict(item)
            item["_source_chunk"] = chunk
            merged.append(item)

    pre_count = len(merged)
    deduped = dedupe_decisions(merged)
    dup_removed = pre_count - len(deduped)

    final: list[dict] = []
    for item in deduped:
        chunk_text = item.pop("_source_chunk", "")
        issues = validate_traceability([item], chunk_text)
        item["traceability_ok"] = not issues
        final.append(item)

    return final, pre_count, dup_removed


def run_excerpt_extraction(
    excerpts: list[dict],
    chunk_size: int,
    overlap: int,
    client,
    usage_acc: ApiUsage,
) -> tuple[list[dict], RunMetrics]:
    if overlap >= chunk_size or chunk_size - overlap < 1:
        m = RunMetrics(chunk_size, overlap, stage="invalid")
        m.invalid_config = True
        m.invalid_reason = f"overlap {overlap} >= chunk_size {chunk_size} or step < 1"
        return [], m

    metrics = RunMetrics(chunk_size, overlap, stage="screen")
    all_candidates: list[dict] = []

    for ex in excerpts:
        eid = ex["excerpt_id"]
        cands, pre, dup = extract_on_text(
            ex["excerpt_text"], chunk_size, overlap, client, usage_acc
        )
        metrics.pre_dedupe_total += pre
        metrics.duplicate_removed += dup
        metrics.candidate_total += len(cands)
        metrics.per_excerpt_candidates[eid] = len(cands)
        for c in cands:
            c["_excerpt_id"] = eid
        all_candidates.extend(cands)

    metrics.traceable_count = sum(1 for c in all_candidates if c.get("traceability_ok"))
    metrics.api_usage = usage_acc
    return all_candidates, metrics


def build_alignment_rows(
    config: str,
    excerpts: list[dict],
    candidates: list[dict],
    stage: str,
    repetition: int,
) -> tuple[list[dict], int, int]:
    rows: list[dict] = []
    recovered_manuals: set[tuple[str, str]] = set()
    matched_candidate_keys: set[str] = set()

    for ex in excerpts:
        eid = ex["excerpt_id"]
        ex_cands = [c for c in candidates if c.get("_excerpt_id") == eid]
        manuals = ex.get("manual_decisions", [])

        for manual in manuals:
            mid = manual["manual_id"]
            best = None
            for idx, cand in enumerate(ex_cands, start=1):
                recovered, mech, basis = assess_pair(cand, manual)
                row = {
                    "stage": stage,
                    "repetition": repetition,
                    "configuration": config,
                    "excerpt_id": eid,
                    "manual_decision_id": mid,
                    "manual_decision_text": manual.get("decision", ""),
                    "candidate_id": f"c{idx}",
                    "candidate_decision_text": cand.get("decision", ""),
                    "candidate_quote": cand.get("source_quote", ""),
                    "traceability_status": cand.get("traceability_ok"),
                    "match_outcome": "recovered" if recovered else "not_recovered",
                    "matching_basis": basis,
                }
                rows.append(row)
                if recovered and (best is None or basis == "mechanical_and_semantic"):
                    best = (mid, eid, f"c{idx}")
                    row["match_outcome"] = "recovered"
            if best:
                recovered_manuals.add((best[1], best[0]))

        # unmatched candidates
        for idx, cand in enumerate(ex_cands, start=1):
            cid = f"c{idx}"
            aligned = False
            for manual in manuals:
                rec, _, _ = assess_pair(cand, manual)
                if rec:
                    aligned = True
                    matched_candidate_keys.add(f"{eid}:{cid}")
                    break
            if not aligned:
                rows.append(
                    {
                        "stage": stage,
                        "repetition": repetition,
                        "configuration": config,
                        "excerpt_id": eid,
                        "manual_decision_id": "",
                        "manual_decision_text": "",
                        "candidate_id": cid,
                        "candidate_decision_text": cand.get("decision", ""),
                        "candidate_quote": cand.get("source_quote", ""),
                        "traceability_status": cand.get("traceability_ok"),
                        "match_outcome": "unmatched_candidate",
                        "matching_basis": "none",
                    }
                )

    unmatched_count = sum(
        1
        for ex in excerpts
        for idx, _ in enumerate(
            [c for c in candidates if c.get("_excerpt_id") == ex["excerpt_id"]], start=1
        )
        if f"{ex['excerpt_id']}:c{idx}" not in matched_candidate_keys
    )

    return rows, len(recovered_manuals), unmatched_count


def finalize_metrics(
    metrics: RunMetrics,
    recovered: int,
    unmatched: int,
    stage: str,
    repetition: int = 1,
    scope: str = "excerpts",
) -> RunMetrics:
    metrics.manual_recovered = recovered
    metrics.unmatched_candidates = unmatched
    metrics.stage = stage
    metrics.repetition = repetition
    metrics.scope = scope
    return metrics


def rank_configs(results: list[RunMetrics]) -> list[RunMetrics]:
    return sorted(
        results,
        key=lambda m: (
            -m.manual_recovered,
            -m.traceability_pct,
            m.unmatched_candidates,
            m.duplicate_removed,
            m.chunk_size,
            m.overlap,
        ),
    )


def pareto_dominance(a: RunMetrics, b: RunMetrics) -> bool:
    dims_a = [
        a.manual_recovered,
        a.traceability_pct,
        -a.unmatched_candidates,
        -a.duplicate_removed,
    ]
    dims_b = [
        b.manual_recovered,
        b.traceability_pct,
        -b.unmatched_candidates,
        -b.duplicate_removed,
    ]
    no_worse = all(x >= y for x, y in zip(dims_a, dims_b))
    strictly_better = any(x > y for x, y in zip(dims_a, dims_b))
    return no_worse and strictly_better


def metrics_to_row(m: RunMetrics) -> dict:
    return {
        "configuration": config_label(m.chunk_size, m.overlap),
        "chunk_size": m.chunk_size,
        "overlap": m.overlap,
        "manual_decisions_recovered": m.manual_recovered,
        "manual_decisions_total": m.manual_total,
        "manual_recall_pct": round(100 * m.recall, 1),
        "candidate_total": m.candidate_total,
        "candidates_per_excerpt_mean": round(m.candidate_total / 6, 2),
        "candidates_per_recovered_manual": round(
            m.candidate_total / m.manual_recovered if m.manual_recovered else 0, 2
        ),
        "traceable_candidates": m.traceable_count,
        "traceability_pct": round(m.traceability_pct, 1),
        "unmatched_candidates": m.unmatched_candidates,
        "pre_dedupe_candidates": m.pre_dedupe_total,
        "duplicate_removed": m.duplicate_removed,
        "duplicate_pct": round(m.duplicate_pct, 1),
        "api_calls": m.api_usage.calls,
        "prompt_tokens": m.api_usage.prompt_tokens,
        "completion_tokens": m.api_usage.completion_tokens,
        "total_tokens": m.api_usage.total_tokens,
        "wall_seconds": round(m.api_usage.wall_seconds, 2),
        "estimated_usd": round(m.api_usage.estimated_usd(), 4),
        "invalid_config": m.invalid_config,
    }


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def write_stage1_md(path: Path, rows: list[dict]) -> None:
    headers = [
        "configuration",
        "recovered",
        "recall%",
        "candidates",
        "traceability%",
        "unmatched",
        "dup_removed",
        "api_calls",
        "est_usd",
    ]
    lines = [
        "# Stage 1 — configuration screen results",
        "",
        "Six annotated excerpts; 6 manual decisions total.",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for r in rows:
        lines.append(
            f"| {r['configuration']} | {r['manual_decisions_recovered']}/6 | "
            f"{r['manual_recall_pct']} | {r['candidate_total']} | {r['traceability_pct']} | "
            f"{r['unmatched_candidates']} | {r['duplicate_removed']} | "
            f"{r['api_calls']} | ${r['estimated_usd']:.4f} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def extract_span_from_full_hearing(
    full_text: str,
    char_start: int,
    char_end: int,
    chunk_size: int,
    overlap: int,
    client,
    usage_acc: ApiUsage,
) -> list[dict]:
    """Extract on full hearing but keep only candidates whose quote appears in annotated span."""
    text = clean_inquiry_text(full_text)
    cands, _, _ = extract_on_text(text, chunk_size, overlap, client, usage_acc)
    span = text[char_start:char_end]
    span_norm = re.sub(r"[^a-z0-9]+", "", span.lower())
    filtered = []
    for c in cands:
        q = str(c.get("source_quote", ""))
        nq = re.sub(r"[^a-z0-9]+", "", q.lower())
        if nq and nq in span_norm:
            filtered.append(c)
        elif quote_found_in_text(q, span):
            filtered.append(c)
    return filtered


def run_stage3(
    excerpts: list[dict],
    configs: list[tuple[int, int]],
    client,
    api_manifest: list[dict],
) -> tuple[list[RunMetrics], list[dict]]:
    results: list[RunMetrics] = []
    all_alignments: list[dict] = []

    for chunk_size, overlap in configs:
        cfg = config_label(chunk_size, overlap)
        usage = ApiUsage()
        all_cands: list[dict] = []
        metrics = RunMetrics(chunk_size, overlap, stage="stage3", scope="full_hearings")

        # cache loaded transcripts
        transcript_cache: dict[str, str] = {}

        for ex in excerpts:
            slug = ex["transcript_slug"]
            if slug not in transcript_cache:
                src = ROOT / ex["source_file"]
                transcript_cache[slug] = load_text_file(src)

            cands = extract_span_from_full_hearing(
                transcript_cache[slug],
                ex["char_start"],
                ex["char_end"],
                chunk_size,
                overlap,
                client,
                usage,
            )
            eid = ex["excerpt_id"]
            metrics.candidate_total += len(cands)
            metrics.per_excerpt_candidates[eid] = len(cands)
            for c in cands:
                c["_excerpt_id"] = eid
            all_cands.extend(cands)

            api_manifest.append(
                {
                    "stage": "stage3",
                    "configuration": cfg,
                    "scope": slug,
                    "excerpt_id": eid,
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                }
            )

        metrics.traceable_count = sum(1 for c in all_cands if c.get("traceability_ok"))
        metrics.api_usage = usage
        align_rows, recovered, unmatched = build_alignment_rows(cfg, excerpts, all_cands, "stage3", 1)
        all_alignments.extend(align_rows)
        results.append(finalize_metrics(metrics, recovered, unmatched, "stage3", scope="full_hearings"))

    return results, all_alignments


def estimate_stage3_cost() -> dict:
    estimates = []
    total_chunks = 0
    for label, path in STAGE3_HEARINGS.items():
        text = clean_inquiry_text(load_text_file(path))
        for cs, ov in [(7, 2)]:
            chunks = chunk_text_by_sentences(text, chunk_size=cs, overlap=ov)
            total_chunks += len(chunks)
            estimates.append({"hearing": label, "chunks_at_7_2": len(chunks), "chars": len(text)})
    # 3 configs
    est_calls = total_chunks * 3
    est_input_tokens = est_calls * 900
    est_output_tokens = est_calls * 250
    est_usd = (
        est_input_tokens * PRICE_INPUT_PER_M + est_output_tokens * PRICE_OUTPUT_PER_M
    ) / 1_000_000
    return {
        "hearings": estimates,
        "configs": 3,
        "estimated_api_calls": est_calls,
        "estimated_input_tokens": est_input_tokens,
        "estimated_output_tokens": est_output_tokens,
        "estimated_usd": round(est_usd, 2),
        "proceed_recommendation": est_usd < 5.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["all", "1", "2", "3"], default="all")
    parser.add_argument("--skip-stage3", action="store_true")
    args = parser.parse_args()

    excerpts = load_excerpts()
    client = get_client()
    api_manifest: list[dict] = []
    all_alignments: list[dict] = []
    stage1_metrics: list[RunMetrics] = []

    out_dir = EXPERIMENT_DIR
    runs_dir = out_dir / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    # --- Stage 1 ---
    if args.stage in ("all", "1"):
        print("=== Stage 1: 12 configurations on 6 excerpts ===")
        for chunk_size, overlap in CONFIG_GRID:
            cfg = config_label(chunk_size, overlap)
            print(f"  Running {cfg}...")
            usage = ApiUsage()
            t0 = time.perf_counter()
            cands, metrics = run_excerpt_extraction(excerpts, chunk_size, overlap, client, usage)
            align_rows, recovered, unmatched = build_alignment_rows(
                cfg, excerpts, cands, "stage1", 1
            )
            all_alignments.extend(align_rows)
            metrics = finalize_metrics(metrics, recovered, unmatched, "stage1")
            stage1_metrics.append(metrics)

            run_path = runs_dir / f"stage1_{cfg}.json"
            run_path.write_text(
                json.dumps(
                    {
                        "configuration": cfg,
                        "metrics": metrics_to_row(metrics),
                        "candidates": [
                            {k: v for k, v in c.items() if not k.startswith("_")}
                            for c in cands
                        ],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            api_manifest.append(
                {
                    "stage": "stage1",
                    "configuration": cfg,
                    "repetition": 1,
                    "api_calls": usage.calls,
                    "total_tokens": usage.total_tokens,
                    "estimated_usd": round(usage.estimated_usd(), 4),
                    "wall_seconds": round(time.perf_counter() - t0, 2),
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                }
            )

        stage1_rows = [metrics_to_row(m) for m in stage1_metrics]
        write_csv(
            out_dir / "01_STAGE1_CONFIGURATION_RESULTS.csv",
            stage1_rows,
            list(stage1_rows[0].keys()),
        )
        write_stage1_md(out_dir / "01_STAGE1_CONFIGURATION_RESULTS.md", stage1_rows)

    # --- Stage 2 ---
    stage2_results: list[dict] = []
    alt_configs: list[tuple[int, int]] = []

    if args.stage in ("all", "2", "3") and stage1_metrics:
        ranked = rank_configs(stage1_metrics)
        baseline = next(m for m in stage1_metrics if m.chunk_size == 7 and m.overlap == 2)
        alternatives = [
            m
            for m in ranked
            if not (m.chunk_size == 7 and m.overlap == 2)
        ][:2]
        stage2_configs = [(7, 2)] + [(m.chunk_size, m.overlap) for m in alternatives]
        alt_configs = [(m.chunk_size, m.overlap) for m in alternatives]

        selection = {
            "baseline": "w7_o2",
            "alternative_1": config_label(alternatives[0].chunk_size, alternatives[0].overlap)
            if len(alternatives) > 0
            else None,
            "alternative_2": config_label(alternatives[1].chunk_size, alternatives[1].overlap)
            if len(alternatives) > 1
            else None,
            "selection_rule": "pre-registered hierarchy on Stage 1 metrics",
            "stage1_rank_order": [config_label(m.chunk_size, m.overlap) for m in ranked],
        }
        (out_dir / "STAGE2_CONFIG_SELECTION.json").write_text(
            json.dumps(selection, indent=2), encoding="utf-8"
        )

        if args.stage in ("all", "2"):
            print("=== Stage 2: stability (3 reps × 3 configs) ===")
            for chunk_size, overlap in stage2_configs:
                cfg = config_label(chunk_size, overlap)
                for rep in range(1, 4):
                    print(f"  {cfg} rep {rep}...")
                    usage = ApiUsage()
                    cands, metrics = run_excerpt_extraction(
                        excerpts, chunk_size, overlap, client, usage
                    )
                    align_rows, recovered, unmatched = build_alignment_rows(
                        cfg, excerpts, cands, "stage2", rep
                    )
                    all_alignments.extend(align_rows)
                    metrics = finalize_metrics(
                        metrics, recovered, unmatched, "stage2", repetition=rep
                    )
                    stage2_results.append({**metrics_to_row(metrics), "repetition": rep})

    if stage2_results:
        write_csv(
            out_dir / "02_STABILITY_RESULTS.csv",
            stage2_results,
            list(stage2_results[0].keys()),
        )
        # summary md
        lines = ["# Stage 2 — stability results", ""]
        for cfg in sorted(set(r["configuration"] for r in stage2_results)):
            reps = [r for r in stage2_results if r["configuration"] == cfg]
            rec = [r["manual_decisions_recovered"] for r in reps]
            cand = [r["candidate_total"] for r in reps]
            lines.append(f"## {cfg}")
            lines.append(f"- Recovery across reps: {rec}")
            lines.append(f"- Candidates across reps: {cand}")
            lines.append(
                f"- Traceability %: {[r['traceability_pct'] for r in reps]}"
            )
            lines.append("")
        (out_dir / "02_STABILITY_RESULTS.md").write_text("\n".join(lines), encoding="utf-8")

    # --- Stage 3 ---
    stage3_est = estimate_stage3_cost()
    (out_dir / "STAGE3_COST_ESTIMATE.md").write_text(
        "# Stage 3 cost estimate\n\n```json\n"
        + json.dumps(stage3_est, indent=2)
        + "\n```\n",
        encoding="utf-8",
    )

    if (
        args.stage in ("all", "3")
        and not args.skip_stage3
        and stage3_est["proceed_recommendation"]
        and alt_configs
    ):
        print("=== Stage 3: confirmatory full-hearing check ===")
        stage3_configs = [(7, 2)] + alt_configs[:2]
        stage3_metrics, stage3_align = run_stage3(excerpts, stage3_configs, client, api_manifest)
        all_alignments.extend(stage3_align)
        stage3_rows = [metrics_to_row(m) for m in stage3_metrics]
        write_csv(
            out_dir / "03_CONFIRMATORY_RESULTS.csv",
            stage3_rows,
            list(stage3_rows[0].keys()),
        )
        lines = ["# Stage 3 — confirmatory full-hearing results", ""]
        for r in stage3_rows:
            lines.append(
                f"- **{r['configuration']}**: recovered {r['manual_decisions_recovered']}/6, "
                f"candidates {r['candidate_total']}, traceability {r['traceability_pct']}%"
            )
        (out_dir / "03_CONFIRMATORY_RESULTS.md").write_text("\n".join(lines), encoding="utf-8")
    elif args.skip_stage3 or not stage3_est["proceed_recommendation"]:
        skip_reason = "skipped by flag" if args.skip_stage3 else "cost gate / missing alternatives"
        (out_dir / "03_CONFIRMATORY_RESULTS.md").write_text(
            f"# Stage 3 — not performed\n\nReason: {skip_reason}.\n\n"
            "Stages 1 and 2 constitute the completed bounded sensitivity analysis.\n",
            encoding="utf-8",
        )

    # --- Alignment + API manifest ---
    if all_alignments:
        write_csv(
            out_dir / "GOLD_DECISION_ALIGNMENT.csv",
            all_alignments,
            list(all_alignments[0].keys()),
        )

    write_csv(
        out_dir / "API_RUN_MANIFEST.csv",
        api_manifest,
        list(api_manifest[0].keys()) if api_manifest else ["stage"],
    )

    # Save intermediate for report generator
    bundle = {
        "stage1": [metrics_to_row(m) for m in stage1_metrics],
        "stage2": stage2_results,
        "stage3_estimate": stage3_est,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "_results_bundle.json").write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    print("Experiment run complete.")


if __name__ == "__main__":
    main()
