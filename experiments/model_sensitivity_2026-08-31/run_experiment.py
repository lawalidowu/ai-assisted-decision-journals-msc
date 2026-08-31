#!/usr/bin/env python3
"""Bounded model sensitivity experiment — isolated wrapper.

Does NOT modify production scripts, frozen artefacts, or chunk/overlap experiment outputs.
All outputs under experiments/model_sensitivity_2026-08-31/.
"""

from __future__ import annotations

import argparse
import csv
import json
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
    normalize_json_output,
    quote_found_in_text,
    validate_traceability,
)

EXPERIMENT_DIR = Path(__file__).resolve().parent
EXCERPT_DIR = ROOT / "configs/annotations/excerpts"
RAW_DIR = EXPERIMENT_DIR / "raw_responses"
LOG_DIR = EXPERIMENT_DIR / "logs"

BASELINE_MODEL = "gpt-4o-mini"
COMPARISON_MODEL = "gpt-4o"
MODELS = [BASELINE_MODEL, COMPARISON_MODEL]
CHUNK_SIZE = 7
OVERLAP = 2
TEMPERATURE = 0
REPETITIONS = 3
MANUAL_DECISION_TOTAL = 6

PRICE = {
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.00),
}


def overlaps(a: str, b: str, min_len: int = 25) -> bool:
    a, b = (a or "").lower(), (b or "").lower()
    if not a or not b:
        return False
    if a in b or b in a:
        return True
    for i in range(max(0, len(a) - min_len + 1)):
        if a[i : i + min_len] in b:
            return True
    return False


def mechanical_quote_match(candidate_quote: str, manual_quote: str) -> bool:
    if overlaps(candidate_quote, manual_quote):
        return True
    return quote_found_in_text(manual_quote, candidate_quote) or quote_found_in_text(
        candidate_quote, manual_quote
    )


def semantic_match(candidate: dict, manual: dict) -> bool:
    for c in [candidate.get("decision", ""), candidate.get("evidence", "")]:
        for m in [manual.get("decision", ""), manual.get("source_quote", "")]:
            if overlaps(c, m):
                return True
    return False


def assess_pair(candidate: dict, manual: dict) -> tuple[bool, str]:
    mech = mechanical_quote_match(
        str(candidate.get("source_quote", "")), str(manual.get("source_quote", ""))
    )
    sem = semantic_match(candidate, manual)
    if mech and sem:
        return True, "mechanical_and_semantic"
    if mech:
        return False, "mechanical_only"
    if sem:
        return False, "semantic_only"
    return False, "none"


@dataclass
class ApiUsage:
    calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    wall_seconds: float = 0.0
    api_failures: int = 0
    parse_failures: int = 0
    returned_models: list[str] = field(default_factory=list)

    def add(self, usage: Any, elapsed: float, returned_model: str = "") -> None:
        self.calls += 1
        self.wall_seconds += elapsed
        if returned_model:
            self.returned_models.append(returned_model)
        if usage:
            self.prompt_tokens += getattr(usage, "prompt_tokens", 0) or 0
            self.completion_tokens += getattr(usage, "completion_tokens", 0) or 0
            self.total_tokens += getattr(usage, "total_tokens", 0) or 0

    def estimated_usd(self, model: str) -> float:
        inp, out = PRICE.get(model, (0.15, 0.60))
        return (self.prompt_tokens * inp + self.completion_tokens * out) / 1_000_000


@dataclass
class RunMetrics:
    model: str
    repetition: int
    manual_recovered: int = 0
    manual_total: int = MANUAL_DECISION_TOTAL
    candidate_total: int = 0
    pre_dedupe_total: int = 0
    duplicate_removed: int = 0
    traceable_count: int = 0
    unmatched_candidates: int = 0
    api_usage: ApiUsage = field(default_factory=ApiUsage)
    returned_model_snapshots: str = ""

    @property
    def recall_pct(self) -> float:
        return 100.0 * self.manual_recovered / self.manual_total if self.manual_total else 0.0

    @property
    def traceability_pct(self) -> float:
        return 100.0 * self.traceable_count / self.candidate_total if self.candidate_total else 0.0


def load_excerpts() -> list[dict]:
    return [
        json.loads((EXCERPT_DIR / f"excerpt_{i:03d}.json").read_text(encoding="utf-8"))
        for i in range(1, 7)
    ]


def call_extractor(
    text: str,
    model: str,
    client,
    usage_acc: ApiUsage,
) -> tuple[str, list[dict], str, str]:
    prompt = INQUIRY_PROMPT_TEMPLATE.format(text=text)
    t0 = time.perf_counter()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=TEMPERATURE,
        )
    except Exception as exc:
        usage_acc.api_failures += 1
        return "", [], "api_failure", str(exc)
    returned = getattr(response, "model", "") or ""
    usage_acc.add(response.usage, time.perf_counter() - t0, returned)
    output = (response.choices[0].message.content or "").strip()
    normalized = normalize_json_output(output)
    try:
        parsed = json.loads(normalized)
        if not isinstance(parsed, list):
            usage_acc.parse_failures += 1
            return output, [], "invalid_json_shape", returned
        return output, parsed, "", returned
    except json.JSONDecodeError:
        usage_acc.parse_failures += 1
        return output, [], "invalid_json", returned


def extract_on_text(
    text: str,
    model: str,
    client,
    usage_acc: ApiUsage,
    raw_log: list[dict],
) -> tuple[list[dict], int, int]:
    text = clean_inquiry_text(text)
    chunks = chunk_text_by_sentences(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP)
    merged: list[dict] = []
    for chunk in chunks:
        raw, parsed, error, returned = call_extractor(chunk, model, client, usage_acc)
        raw_log.append(
            {
                "chunk_preview": chunk[:200],
                "raw_output": raw,
                "parse_error": error,
                "returned_model": returned,
                "parsed_count": len(parsed),
            }
        )
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


def build_alignment(
    excerpts: list[dict],
    candidates: list[dict],
    model: str,
    repetition: int,
) -> tuple[list[dict], int, int]:
    rows: list[dict] = []
    recovered_manuals: set[tuple[str, str]] = set()
    matched_keys: set[str] = set()

    for ex in excerpts:
        eid = ex["excerpt_id"]
        ex_cands = [c for c in candidates if c.get("_excerpt_id") == eid]
        for manual in ex.get("manual_decisions", []):
            mid = manual["manual_id"]
            for idx, cand in enumerate(ex_cands, start=1):
                rec, basis = assess_pair(cand, manual)
                rows.append(
                    {
                        "model": model,
                        "repetition": repetition,
                        "excerpt_id": eid,
                        "manual_decision_id": mid,
                        "candidate_id": f"c{idx}",
                        "match_outcome": "recovered" if rec else "not_recovered",
                        "matching_basis": basis,
                    }
                )
                if rec:
                    recovered_manuals.add((eid, mid))

        for idx, cand in enumerate(ex_cands, start=1):
            cid = f"c{idx}"
            aligned = any(assess_pair(cand, m)[0] for m in ex.get("manual_decisions", []))
            if aligned:
                matched_keys.add(f"{eid}:{cid}")
            else:
                rows.append(
                    {
                        "model": model,
                        "repetition": repetition,
                        "excerpt_id": eid,
                        "manual_decision_id": "",
                        "candidate_id": cid,
                        "match_outcome": "unmatched_candidate",
                        "matching_basis": "none",
                    }
                )

    unmatched = sum(
        1
        for ex in excerpts
        for idx, _ in enumerate(
            [c for c in candidates if c.get("_excerpt_id") == ex["excerpt_id"]], start=1
        )
        if f"{ex['excerpt_id']}:c{idx}" not in matched_keys
    )
    return rows, len(recovered_manuals), unmatched


def run_repetition(
    model: str,
    repetition: int,
    excerpts: list[dict],
    client,
) -> tuple[RunMetrics, list[dict], list[dict]]:
    usage = ApiUsage()
    metrics = RunMetrics(model=model, repetition=repetition)
    all_candidates: list[dict] = []
    all_alignment: list[dict] = []
    manifest_rows: list[dict] = []
    snapshots: set[str] = set()

    for ex in excerpts:
        eid = ex["excerpt_id"]
        raw_log: list[dict] = []
        cands, pre, dup = extract_on_text(
            ex["excerpt_text"], model, client, usage, raw_log
        )
        metrics.pre_dedupe_total += pre
        metrics.duplicate_removed += dup
        metrics.candidate_total += len(cands)
        for c in cands:
            c["_excerpt_id"] = eid
        all_candidates.extend(cands)

        raw_path = RAW_DIR / model / f"rep{repetition}" / f"{eid}.json"
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "model_requested": model,
            "repetition": repetition,
            "excerpt_id": eid,
            "chunk_size": CHUNK_SIZE,
            "overlap": OVERLAP,
            "temperature": TEMPERATURE,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "chunk_calls": raw_log,
            "candidates_post_dedupe": [
                {k: v for k, v in c.items() if not k.startswith("_")} for c in cands
            ],
        }
        raw_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        manifest_rows.append(
            {
                "model": model,
                "repetition": repetition,
                "excerpt_id": eid,
                "raw_path": str(raw_path.relative_to(EXPERIMENT_DIR)),
                "chunk_calls": len(raw_log),
                "candidates": len(cands),
            }
        )
        for entry in raw_log:
            if entry.get("returned_model"):
                snapshots.add(entry["returned_model"])

    align_rows, recovered, unmatched = build_alignment(
        excerpts, all_candidates, model, repetition
    )
    all_alignment.extend(align_rows)
    metrics.manual_recovered = recovered
    metrics.unmatched_candidates = unmatched
    metrics.traceable_count = sum(1 for c in all_candidates if c.get("traceability_ok"))
    metrics.api_usage = usage
    metrics.returned_model_snapshots = "; ".join(sorted(snapshots))
    return metrics, all_alignment, manifest_rows


def metrics_row(m: RunMetrics) -> dict:
    u = m.api_usage
    return {
        "model": m.model,
        "repetition": m.repetition,
        "chunk_size": CHUNK_SIZE,
        "overlap": OVERLAP,
        "temperature": TEMPERATURE,
        "manual_decisions_recovered": m.manual_recovered,
        "manual_decisions_total": m.manual_total,
        "manual_recall_pct": round(m.recall_pct, 1),
        "candidate_total": m.candidate_total,
        "traceable_candidates": m.traceable_count,
        "traceability_pct": round(m.traceability_pct, 1),
        "unmatched_candidates": m.unmatched_candidates,
        "pre_dedupe_candidates": m.pre_dedupe_total,
        "duplicate_removed": m.duplicate_removed,
        "parse_schema_failures": u.parse_failures,
        "api_runtime_failures": u.api_failures,
        "api_calls": u.calls,
        "prompt_tokens": u.prompt_tokens,
        "completion_tokens": u.completion_tokens,
        "total_tokens": u.total_tokens,
        "wall_seconds": round(u.wall_seconds, 2),
        "estimated_usd": round(u.estimated_usd(m.model), 4),
        "returned_model_snapshots": m.returned_model_snapshots,
    }


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Load excerpts only; no API calls")
    args = parser.parse_args()

    excerpts = load_excerpts()
    if args.dry_run:
        print(f"Loaded {len(excerpts)} excerpts; dry run OK")
        return

    client = get_client()
    run_rows: list[dict] = []
    manifest_rows: list[dict] = []
    alignment_rows: list[dict] = []

    t_start = datetime.now(timezone.utc).isoformat()
    for model in MODELS:
        for rep in range(1, REPETITIONS + 1):
            print(f"Running {model} repetition {rep}/{REPETITIONS}...", flush=True)
            metrics, align, manifest = run_repetition(model, rep, excerpts, client)
            run_rows.append(metrics_row(metrics))
            alignment_rows.extend(align)
            manifest_rows.extend(manifest)

    write_csv(
        EXPERIMENT_DIR / "02_RUN_RESULTS.csv",
        run_rows,
        list(run_rows[0].keys()) if run_rows else [],
    )
    write_csv(
        EXPERIMENT_DIR / "04_RAW_OUTPUT_MANIFEST.csv",
        manifest_rows,
        list(manifest_rows[0].keys()) if manifest_rows else [],
    )

    align_path = EXPERIMENT_DIR / "GOLD_DECISION_ALIGNMENT.csv"
    if alignment_rows:
        write_csv(align_path, alignment_rows, list(alignment_rows[0].keys()))

    # Model summary
    summary_rows: list[dict] = []
    for model in MODELS:
        model_runs = [r for r in run_rows if r["model"] == model]
        recs = [r["manual_decisions_recovered"] for r in model_runs]
        summary_rows.append(
            {
                "model": model,
                "repetitions_completed": len(model_runs),
                "recovery_rep1": recs[0] if len(recs) > 0 else "",
                "recovery_rep2": recs[1] if len(recs) > 1 else "",
                "recovery_rep3": recs[2] if len(recs) > 2 else "",
                "recovery_min": min(recs) if recs else "",
                "recovery_max": max(recs) if recs else "",
                "recovery_mean": round(sum(recs) / len(recs), 2) if recs else "",
                "recovery_identical_all_reps": len(set(recs)) == 1 if recs else "",
                "mean_candidates": round(
                    sum(r["candidate_total"] for r in model_runs) / len(model_runs), 2
                )
                if model_runs
                else "",
                "mean_traceability_pct": round(
                    sum(r["traceability_pct"] for r in model_runs) / len(model_runs), 1
                )
                if model_runs
                else "",
                "total_parse_failures": sum(r["parse_schema_failures"] for r in model_runs),
                "total_api_failures": sum(r["api_runtime_failures"] for r in model_runs),
                "returned_model_snapshots": model_runs[0]["returned_model_snapshots"]
                if model_runs
                else "",
            }
        )
    write_csv(
        EXPERIMENT_DIR / "03_MODEL_SUMMARY.csv",
        summary_rows,
        list(summary_rows[0].keys()) if summary_rows else [],
    )

    log = {
        "started_utc": t_start,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "models": MODELS,
        "repetitions_per_model": REPETITIONS,
        "runs_completed": len(run_rows),
    }
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    (LOG_DIR / "run_log.json").write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(json.dumps(log, indent=2))


if __name__ == "__main__":
    main()
