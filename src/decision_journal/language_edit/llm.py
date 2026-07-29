"""LLM calls for language-edit (temperature 0, structured JSON)."""

from __future__ import annotations

import json
from typing import Any

from decision_journal.extraction import get_client, normalize_json_output
from decision_journal.language_edit.prompts import build_batch_prompt


def call_language_edit_batch(
    *,
    mode: str,
    targets: list[dict[str, Any]],
    context_by_id: dict[str, dict[str, list[dict]]],
    model: str,
    temperature: float = 0,
    client=None,
) -> dict[str, Any]:
    client = client or get_client()
    prompt = build_batch_prompt(mode=mode, targets=targets, context_by_id=context_by_id)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    raw = (response.choices[0].message.content or "").strip()
    normalized = normalize_json_output(raw)
    result: dict[str, Any] = {
        "raw": raw,
        "normalized": normalized,
        "parsed": None,
        "error": None,
        "prompt": prompt,
    }
    try:
        parsed = json.loads(normalized)
    except json.JSONDecodeError as exc:
        result["error"] = f"invalid_json:{exc}"
        return result

    if not isinstance(parsed, dict) or "revisions" not in parsed:
        result["error"] = "invalid_json_shape"
        return result
    if not isinstance(parsed["revisions"], list):
        result["error"] = "invalid_revisions_type"
        return result

    result["parsed"] = parsed
    return result


def _revision_ids(parsed: dict[str, Any] | None) -> set[str]:
    if not parsed or not isinstance(parsed.get("revisions"), list):
        return set()
    ids: set[str] = set()
    for item in parsed["revisions"]:
        if isinstance(item, dict) and item.get("paragraph_id"):
            ids.add(str(item["paragraph_id"]))
    return ids


def merge_parsed_revisions(
    base: dict[str, Any] | None,
    additions: list[dict[str, Any]],
    *,
    mode: str,
) -> dict[str, Any]:
    by_id: dict[str, dict[str, Any]] = {}
    if base and isinstance(base.get("revisions"), list):
        for item in base["revisions"]:
            if isinstance(item, dict) and item.get("paragraph_id"):
                by_id[str(item["paragraph_id"])] = item
    for item in additions:
        if isinstance(item, dict) and item.get("paragraph_id"):
            by_id[str(item["paragraph_id"])] = item
    return {"mode": mode, "revisions": list(by_id.values())}


def call_language_edit_batch_with_missing_id_retry(
    *,
    mode: str,
    targets: list[dict[str, Any]],
    context_by_id: dict[str, dict[str, list[dict]]],
    model: str,
    temperature: float = 0,
    client=None,
) -> dict[str, Any]:
    """
    Call the batch once. If any target IDs are missing from the JSON, retry each
    missing ID individually once at temperature 0. Still-missing IDs are left
    absent for per-ID rejection (do not reject the whole batch).
    """
    client = client or get_client()
    primary = call_language_edit_batch(
        mode=mode,
        targets=targets,
        context_by_id=context_by_id,
        model=model,
        temperature=temperature,
        client=client,
    )

    expected = [t["paragraph_id"] for t in targets]
    expected_set = set(expected)
    retries: list[dict[str, Any]] = []
    merged = primary.get("parsed")

    # Fatal batch parse errors: still attempt individual retries for all targets
    if primary.get("error") and not merged:
        missing = list(expected)
    else:
        present = _revision_ids(merged)
        missing = [pid for pid in expected if pid not in present]

    target_by_id = {t["paragraph_id"]: t for t in targets}
    recovered: list[dict[str, Any]] = []

    for pid in missing:
        target = target_by_id[pid]
        single_ctx = {pid: context_by_id.get(pid, {"before": [], "after": []})}
        retry = call_language_edit_batch(
            mode=mode,
            targets=[target],
            context_by_id=single_ctx,
            model=model,
            temperature=0,
            client=client,
        )
        retry_log = {
            "paragraph_id": pid,
            "error": retry.get("error"),
            "raw": retry.get("raw"),
            "normalized": retry.get("normalized"),
            "parsed": retry.get("parsed"),
        }
        retries.append(retry_log)
        if retry.get("parsed") and _revision_ids(retry["parsed"]) == {pid}:
            # take the single revision object
            for item in retry["parsed"]["revisions"]:
                if item.get("paragraph_id") == pid:
                    recovered.append(item)
                    break

    if recovered or merged:
        merged = merge_parsed_revisions(merged, recovered, mode=mode)

    still_missing = sorted(expected_set - _revision_ids(merged))
    return {
        "raw": primary.get("raw"),
        "normalized": primary.get("normalized"),
        "parsed": merged,
        "error": primary.get("error") if not merged else None,
        "primary_error": primary.get("error"),
        "missing_after_primary": missing,
        "retries": retries,
        "still_missing": still_missing,
    }
