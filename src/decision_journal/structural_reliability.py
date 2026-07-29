"""Structural reliability checks for repeated extraction regenerations."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from decision_journal.extraction import (
    INQUIRY_PROMPT_TEMPLATE,
    call_extractor,
    chunk_text_by_sentences,
    clean_inquiry_text,
    quote_found_in_text,
    validate_traceability,
)

REQUIRED_FIELDS = ("decision", "evidence", "source_location", "source_quote")
LOCATION_PATTERN = re.compile(r"^sentence_\d+$|^sentences_\d+-\d+$")

VALIDATION_CHUNK_IDS = (
    "val_procedural_082",
    "val_closing_252",
    "val_wrong_artefact_067",
    "val_trace_fail_384",
)


def chunk_containing_quote(
    text: str,
    quote: str,
    chunk_size: int = 7,
    chunk_overlap: int = 2,
) -> str | None:
    """Return the pipeline chunk that contains quote, or None."""
    if not quote or not text:
        return None
    for chunk in chunk_text_by_sentences(text, chunk_size=chunk_size, overlap=chunk_overlap):
        if quote_found_in_text(quote, chunk):
            return chunk
    return None


def score_parsed_output(parsed: list[dict], chunk_text: str) -> dict[str, Any]:
    """Score one parsed extraction against the structural checklist."""
    checks: dict[str, bool] = {
        "valid_json_list": isinstance(parsed, list),
        "all_items_have_required_fields": True,
        "all_decisions_non_empty": True,
        "all_source_quotes_non_empty": True,
        "all_source_locations_valid": True,
        "all_items_traceable": True,
    }
    failures: list[str] = []

    if not isinstance(parsed, list):
        checks["valid_json_list"] = False
        failures.append("invalid_json_list")
        return _result(checks, failures)

    if len(parsed) == 0:
        # Empty list is valid JSON for inquiry mode (no decision in chunk).
        return _result(checks, failures)

    for idx, item in enumerate(parsed, start=1):
        if not isinstance(item, dict):
            checks["all_items_have_required_fields"] = False
            failures.append(f"item_{idx}:not_object")
            continue
        for field in REQUIRED_FIELDS:
            if field not in item:
                checks["all_items_have_required_fields"] = False
                failures.append(f"item_{idx}:missing_{field}")
        decision = str(item.get("decision", "")).strip()
        quote = str(item.get("source_quote", "")).strip()
        location = str(item.get("source_location", "")).strip()
        if not decision:
            checks["all_decisions_non_empty"] = False
            failures.append(f"item_{idx}:empty_decision")
        if not quote:
            checks["all_source_quotes_non_empty"] = False
            failures.append(f"item_{idx}:empty_source_quote")
        if location and not LOCATION_PATTERN.match(location):
            checks["all_source_locations_valid"] = False
            failures.append(f"item_{idx}:bad_source_location")
        item_issues = validate_traceability([item], chunk_text)
        if item_issues:
            checks["all_items_traceable"] = False
            for issue in item_issues:
                failures.append(f"item_{idx}:{issue.split(':', 1)[-1]}")

    return _result(checks, failures)


def _result(checks: dict[str, bool], failures: list[str]) -> dict[str, Any]:
    return {
        "checks": checks,
        "failures": failures,
        "structural_pass": all(checks.values()),
    }


def score_raw_extraction(
    raw: str,
    parsed: list[dict],
    parse_error: str,
    chunk_text: str,
) -> dict[str, Any]:
    """Score one regeneration including JSON parse stage."""
    checks: dict[str, bool] = {
        "valid_json_parse": not parse_error,
        "valid_json_list": False,
        "all_items_have_required_fields": False,
        "all_decisions_non_empty": False,
        "all_source_quotes_non_empty": False,
        "all_source_locations_valid": False,
        "all_items_traceable": False,
    }
    failures: list[str] = []

    if parse_error:
        failures.append(parse_error)
        return {
            "checks": checks,
            "failures": failures,
            "structural_pass": False,
            "item_count": 0,
        }

    checks["valid_json_parse"] = True
    item_score = score_parsed_output(parsed, chunk_text)
    checks.update(item_score["checks"])
    failures.extend(item_score["failures"])
    return {
        "checks": checks,
        "failures": failures,
        "structural_pass": all(checks.values()),
        "item_count": len(parsed) if isinstance(parsed, list) else 0,
    }


def build_default_manifest(root: Path) -> dict[str, Any]:
    """Build 10-chunk manifest: 6 triangulation excerpts + 4 validation anchors."""
    manual_path = root / "configs/annotations/manual_phase1.json"
    sample_path = root / "configs/evaluation/confidence_validation_sample.json"
    manual = json.loads(manual_path.read_text(encoding="utf-8"))
    sample = json.loads(sample_path.read_text(encoding="utf-8"))

    chunks: list[dict[str, Any]] = []

    for excerpt in manual.get("excerpts", []):
        excerpt_id = excerpt["excerpt_id"]
        text = clean_inquiry_text(excerpt.get("excerpt_text", ""))
        quote = ""
        for seed in excerpt.get("seed_llm_items") or []:
            quote = seed.get("source_quote") or ""
            if quote:
                break
        if not quote and excerpt.get("manual_decisions"):
            quote = excerpt["manual_decisions"][0].get("source_quote") or ""
        chunk = chunk_containing_quote(text, quote) if quote else None
        if not chunk:
            parts = chunk_text_by_sentences(text)
            chunk = parts[0] if parts else text[:2000]
        chunks.append(
            {
                "chunk_id": f"tri_{excerpt_id}",
                "source": "triangulation",
                "excerpt_id": excerpt_id,
                "transcript_slug": excerpt.get("transcript_slug"),
                "anchor_quote": quote[:120] if quote else None,
                "text": chunk,
            }
        )

    sample_by_id = {item["journal_id"]: item for item in sample.get("items", [])}
    id_map = {
        "val_procedural_082": "phase1-082",
        "val_closing_252": "phase1-252",
        "val_wrong_artefact_067": "phase1-067",
        "val_trace_fail_384": "phase1-384",
    }
    for chunk_id, journal_id in id_map.items():
        item = sample_by_id[journal_id]
        slug = item["slug"]
        txt_path = root / "data/processed/inquiry/document" / f"{slug}.txt"
        full_text = clean_inquiry_text(txt_path.read_text(encoding="utf-8", errors="replace"))
        quote = item.get("source_quote") or ""
        chunk = chunk_containing_quote(full_text, quote)
        if not chunk:
            raise RuntimeError(f"Could not locate chunk for {journal_id} quote in {slug}")
        chunks.append(
            {
                "chunk_id": chunk_id,
                "source": "validation_sample",
                "journal_id": journal_id,
                "stratum": item.get("stratum"),
                "transcript_slug": slug,
                "anchor_quote": quote[:120],
                "text": chunk,
            }
        )

    if len(chunks) != 10:
        raise RuntimeError(f"Expected 10 chunks, got {len(chunks)}")

    return {
        "description": "Fixed chunks for structural reliability mini-test (10 × N regenerations)",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "chunk_size": 7,
        "chunk_overlap": 2,
        "note": "Phase 1 production extraction uses temperature=0; regeneration test uses higher temperature.",
        "chunks": chunks,
    }


def summarize_results(run_records: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate structural pass rates across all regenerations."""
    total = len(run_records)
    passes = sum(1 for r in run_records if r["structural_pass"])
    check_counts: dict[str, int] = {}
    failure_counts: dict[str, int] = {}

    for record in run_records:
        for name, ok in record["checks"].items():
            if not ok:
                check_counts[name] = check_counts.get(name, 0) + 1
        for failure in record.get("failures", []):
            failure_counts[failure] = failure_counts.get(failure, 0) + 1

    per_chunk: dict[str, dict[str, Any]] = {}
    for record in run_records:
        cid = record["chunk_id"]
        bucket = per_chunk.setdefault(
            cid,
            {"chunk_id": cid, "runs": 0, "passes": 0, "consistency_rate": 0.0},
        )
        bucket["runs"] += 1
        if record["structural_pass"]:
            bucket["passes"] += 1
        bucket["consistency_rate"] = round(bucket["passes"] / bucket["runs"], 3)

    return {
        "total_outputs": total,
        "structural_pass_count": passes,
        "structural_consistency_rate": round(passes / total, 3) if total else 0.0,
        "check_failure_counts": dict(sorted(check_counts.items())),
        "failure_tag_counts": dict(sorted(failure_counts.items(), key=lambda x: -x[1])[:20]),
        "per_chunk": [per_chunk[k] for k in sorted(per_chunk)],
    }


def run_structural_reliability(
    manifest: dict[str, Any],
    *,
    model: str,
    runs: int,
    temperature: float,
    client,
) -> dict[str, Any]:
    """Run N regenerations per manifest chunk and return full results."""
    run_records: list[dict[str, Any]] = []

    for chunk in manifest["chunks"]:
        chunk_id = chunk["chunk_id"]
        chunk_text = chunk["text"]
        for run_idx in range(1, runs + 1):
            raw, parsed, error = call_extractor(
                chunk_text,
                model=model,
                client=client,
                prompt_template=INQUIRY_PROMPT_TEMPLATE,
                temperature=temperature,
            )
            score = score_raw_extraction(raw, parsed, error, chunk_text)
            run_records.append(
                {
                    "chunk_id": chunk_id,
                    "run_index": run_idx,
                    "model": model,
                    "temperature": temperature,
                    "item_count": score["item_count"],
                    "checks": score["checks"],
                    "failures": score["failures"],
                    "structural_pass": score["structural_pass"],
                }
            )

    summary = summarize_results(run_records)
    return {
        "description": "Structural reliability mini-test — automated checklist on repeated extractions",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "temperature": temperature,
        "runs_per_chunk": runs,
        "production_note": "Phase 1 corpus extraction used temperature=0 for reproducibility.",
        "checklist": [
            "valid_json_parse",
            "valid_json_list",
            "all_items_have_required_fields",
            "all_decisions_non_empty",
            "all_source_quotes_non_empty",
            "all_source_locations_valid",
            "all_items_traceable",
        ],
        "summary": summary,
        "runs": run_records,
    }
