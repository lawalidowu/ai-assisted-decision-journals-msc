#!/usr/bin/env python3
"""Limited full-hearing confirmation — GPT-5.6 Terra vs Sol.

Does NOT modify legacy or excerpt-level outputs.
See 14_FULL_HEARING_CONFIRMATION_PROTOCOL.md.
"""

from __future__ import annotations

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
RAW_DIR = EXPERIMENT_DIR / "raw_responses_full_hearing"

MODELS = ["gpt-5.6-terra", "gpt-5.6-sol"]
CHUNK_SIZE = 7
OVERLAP = 2
REASONING_EFFORT = "none"
ENDPOINT = "chat.completions"
MANUAL_DECISION_TOTAL = 6


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


def assess_pair(candidate: dict, manual: dict) -> bool:
    mech = mechanical_quote_match(
        str(candidate.get("source_quote", "")), str(manual.get("source_quote", ""))
    )
    sem = semantic_match(candidate, manual)
    return mech and sem


@dataclass
class ApiUsage:
    calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    reasoning_tokens: int = 0
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
            details = getattr(usage, "completion_tokens_details", None)
            if details:
                self.reasoning_tokens += getattr(details, "reasoning_tokens", 0) or 0


def load_excerpts() -> list[dict]:
    return [
        json.loads((EXCERPT_DIR / f"excerpt_{i:03d}.json").read_text(encoding="utf-8"))
        for i in range(1, 7)
    ]


def call_extractor(
    text: str, model: str, client, usage_acc: ApiUsage, failure_samples: list[str]
) -> tuple[str, list[dict], str]:
    prompt = INQUIRY_PROMPT_TEMPLATE.format(text=text)
    last_exc = ""
    for attempt in range(4):
        t0 = time.perf_counter()
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                reasoning_effort=REASONING_EFFORT,
            )
            break
        except Exception as exc:
            last_exc = str(exc)
            if attempt < 3:
                time.sleep(min(2**attempt * 2, 30))
                continue
            usage_acc.api_failures += 1
            if len(failure_samples) < 20:
                failure_samples.append(last_exc)
            return "", [], f"api_failure:{last_exc}"
    else:
        usage_acc.api_failures += 1
        return "", [], f"api_failure:{last_exc}"
    returned = getattr(response, "model", "") or ""
    usage_acc.add(response.usage, time.perf_counter() - t0, returned)
    output = (response.choices[0].message.content or "").strip()
    normalized = normalize_json_output(output)
    try:
        parsed = json.loads(normalized)
        if not isinstance(parsed, list):
            usage_acc.parse_failures += 1
            return output, [], "invalid_json_shape"
        return output, parsed, ""
    except json.JSONDecodeError:
        usage_acc.parse_failures += 1
        return output, [], "invalid_json"


def extract_on_full_text(
    full_text: str,
    model: str,
    client,
    usage_acc: ApiUsage,
    chunk_log: list[dict],
    failure_samples: list[str],
) -> list[dict]:
    text = clean_inquiry_text(full_text)
    chunks = chunk_text_by_sentences(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP)
    merged: list[dict] = []
    for chunk in chunks:
        raw, parsed, error = call_extractor(chunk, model, client, usage_acc, failure_samples)
        chunk_log.append(
            {
                "chunk_index": len(chunk_log),
                "chunk_preview": chunk[:120],
                "parse_error": error,
                "parsed_count": len(parsed),
            }
        )
        if error:
            continue
        for item in parsed:
            item = dict(item)
            item["_source_chunk"] = chunk
            merged.append(item)
    pre = len(merged)
    deduped = dedupe_decisions(merged)
    final: list[dict] = []
    for item in deduped:
        chunk_text = item.pop("_source_chunk", "")
        issues = validate_traceability([item], chunk_text)
        item["traceability_ok"] = not issues
        final.append(item)
    chunk_log.append({"pre_dedupe": pre, "post_dedupe": len(final), "duplicates_removed": pre - len(deduped)})
    return final


def filter_to_span(candidates: list[dict], full_text: str, char_start: int, char_end: int) -> list[dict]:
    text = clean_inquiry_text(full_text)
    span = text[char_start:char_end]
    span_norm = re.sub(r"[^a-z0-9]+", "", span.lower())
    filtered = []
    for c in candidates:
        q = str(c.get("source_quote", ""))
        nq = re.sub(r"[^a-z0-9]+", "", q.lower())
        if nq and nq in span_norm:
            filtered.append(c)
        elif quote_found_in_text(q, span):
            filtered.append(c)
    return filtered


def run_model_confirmation(model: str, excerpts: list[dict], client, run_label: str = "") -> dict:
    usage = ApiUsage()
    transcript_cache: dict[str, str] = {}
    hearing_logs: dict[str, list] = {}
    span_candidates: list[dict] = []
    per_excerpt_counts: dict[str, int] = {}
    failure_samples: list[str] = []

    for slug in sorted({ex["transcript_slug"] for ex in excerpts}):
        src = ROOT / next(ex["source_file"] for ex in excerpts if ex["transcript_slug"] == slug)
        full_text = load_text_file(src)
        transcript_cache[slug] = full_text
        chunk_log: list[dict] = []
        t0 = time.perf_counter()
        all_cands = extract_on_full_text(
            full_text, model, client, usage, chunk_log, failure_samples
        )
        hearing_logs[slug] = {
            "wall_seconds": round(time.perf_counter() - t0, 2),
            "total_candidates_pre_span_filter": len(all_cands),
            "chunk_log_summary": chunk_log[-1] if chunk_log else {},
            "api_calls_this_hearing": len([x for x in chunk_log if "chunk_index" in x]),
        }

        for ex in excerpts:
            if ex["transcript_slug"] != slug:
                continue
            eid = ex["excerpt_id"]
            filtered = filter_to_span(all_cands, full_text, ex["char_start"], ex["char_end"])
            per_excerpt_counts[eid] = len(filtered)
            for c in filtered:
                c = dict(c)
                c["_excerpt_id"] = eid
                span_candidates.append(c)

    # per manual decision recovery
    alignment_rows: list[dict] = []
    recovered_keys: set[str] = set()

    for ex in excerpts:
        eid = ex["excerpt_id"]
        ex_cands = [c for c in span_candidates if c.get("_excerpt_id") == eid]
        for manual in ex.get("manual_decisions", []):
            mid = manual["manual_id"]
            key = f"{eid}:{mid}"
            recovered = any(assess_pair(c, manual) for c in ex_cands)
            if recovered:
                recovered_keys.add(key)
            alignment_rows.append(
                {
                    "model": model,
                    "excerpt_id": eid,
                    "manual_decision_id": mid,
                    "manual_decision_text": manual.get("decision", "")[:120],
                    "recovered": recovered,
                    "candidates_in_span": len(ex_cands),
                }
            )

    traceable = sum(1 for c in span_candidates if c.get("traceability_ok"))
    total_cands = len(span_candidates)

    suffix = f"_{run_label}" if run_label else ""
    raw_path = RAW_DIR / model / f"full_hearing_confirmation{suffix}.json"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    run_valid = usage.api_failures == 0
    raw_path.write_text(
        json.dumps(
            {
                "model_requested": model,
                "run_label": run_label or "primary",
                "run_valid": run_valid,
                "endpoint": ENDPOINT,
                "reasoning_effort": REASONING_EFFORT,
                "temperature": "omitted_api_default",
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "hearing_logs": hearing_logs,
                "per_excerpt_span_candidate_counts": per_excerpt_counts,
                "span_filtered_candidates_total": total_cands,
                "manual_decisions_recovered": len(recovered_keys),
                "api_failures": usage.api_failures,
                "api_failure_samples": failure_samples,
                "returned_model_snapshots": sorted(set(usage.returned_models)),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return {
        "model": model,
        "endpoint": ENDPOINT,
        "reasoning_effort": REASONING_EFFORT,
        "temperature": "omitted_api_default",
        "manual_decisions_recovered": len(recovered_keys),
        "manual_decisions_total": MANUAL_DECISION_TOTAL,
        "manual_recall_pct": round(100.0 * len(recovered_keys) / MANUAL_DECISION_TOTAL, 1),
        "span_filtered_candidates_total": total_cands,
        "traceable_candidates": traceable,
        "traceability_pct": round(100.0 * traceable / total_cands, 1) if total_cands else 0.0,
        "parse_schema_failures": usage.parse_failures,
        "api_runtime_failures": usage.api_failures,
        "api_calls": usage.calls,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "reasoning_tokens_total": usage.reasoning_tokens,
        "total_tokens": usage.total_tokens,
        "wall_seconds": round(usage.wall_seconds, 2),
        "returned_model_snapshots": "; ".join(sorted(set(usage.returned_models))),
        "run_valid": run_valid,
        "recovered_decision_keys": sorted(recovered_keys),
        "alignment_rows": alignment_rows,
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="*", default=MODELS)
    parser.add_argument("--run-label", default="")
    args = parser.parse_args()

    excerpts = load_excerpts()
    client = get_client()
    results: list[dict] = []
    all_align: list[dict] = []

    for model in args.models:
        print(f"Full-hearing confirmation: {model}...", flush=True)
        res = run_model_confirmation(model, excerpts, client, run_label=args.run_label)
        row = {k: v for k, v in res.items() if k not in ("alignment_rows", "recovered_decision_keys")}
        row["recovered_decision_keys"] = "; ".join(res["recovered_decision_keys"])
        results.append(row)
        all_align.extend(res["alignment_rows"])

    if args.models != MODELS:
        existing = {}
        for p in (EXPERIMENT_DIR / "15_FULL_HEARING_RUN_RESULTS.csv",):
            if p.exists():
                for r in csv.DictReader(p.open(encoding="utf-8")):
                    existing[r["model"]] = r
        for r in results:
            existing[r["model"]] = r
        results = [existing[m] for m in MODELS if m in existing]
        existing_align = list(csv.DictReader((EXPERIMENT_DIR / "16_FULL_HEARING_ALIGNMENT.csv").open(encoding="utf-8"))) if (EXPERIMENT_DIR / "16_FULL_HEARING_ALIGNMENT.csv").exists() else []
        rerun_models = set(args.models)
        all_align = [a for a in existing_align if a["model"] not in rerun_models] + all_align

    write_csv(EXPERIMENT_DIR / "15_FULL_HEARING_RUN_RESULTS.csv", results)
    write_csv(EXPERIMENT_DIR / "16_FULL_HEARING_ALIGNMENT.csv", all_align)

    terra_row = next((r for r in results if r["model"] == "gpt-5.6-terra"), {})
    sol_row = next((r for r in results if r["model"] == "gpt-5.6-sol"), {})
    terra_keys = set((terra_row.get("recovered_decision_keys") or "").split("; "))
    sol_keys = set((sol_row.get("recovered_decision_keys") or "").split("; "))
    terra_keys.discard("")
    sol_keys.discard("")

    comparison = {
        "both": sorted(terra_keys & sol_keys),
        "terra_only": sorted(terra_keys - sol_keys),
        "sol_only": sorted(sol_keys - terra_keys),
        "neither": [],
    }
    all_keys = set()
    for ex in excerpts:
        for m in ex.get("manual_decisions", []):
            all_keys.add(f"{ex['excerpt_id']}:{m['manual_id']}")
    comparison["neither"] = sorted(all_keys - terra_keys - sol_keys)

    (EXPERIMENT_DIR / "logs" / "full_hearing_comparison.json").write_text(
        json.dumps(comparison, indent=2), encoding="utf-8"
    )
    print(json.dumps({"terra_recovered": len(terra_keys), "sol_recovered": len(sol_keys), "comparison": comparison}, indent=2))


if __name__ == "__main__":
    main()
