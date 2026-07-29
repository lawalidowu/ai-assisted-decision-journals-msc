"""Validate language-edit revisions and assign human-review states."""

from __future__ import annotations

from typing import Any, Iterable

from decision_journal.language_edit.protect import (
    compare_protected,
    language_policy_issues,
    markdown_structure_issues,
)

REVIEW_REJECTED = "rejected_by_validation"
REVIEW_PENDING = "validated_pending_review"
REVIEW_APPROVED = "approved_by_human"
REVIEW_REJECTED_BY_HUMAN = "rejected_by_human"

VALID_REVIEW_STATES = (
    REVIEW_REJECTED,
    REVIEW_PENDING,
    REVIEW_APPROVED,
    REVIEW_REJECTED_BY_HUMAN,
)

SELF_CHECK_FIELDS = (
    "methodological_qualifiers_preserved",
    "scope_preserved",
    "british_english_used",
    "technical_distinctions_preserved",
)


def _norm_ws(text: str) -> str:
    return " ".join((text or "").split())


def _as_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    return None


def validate_revision(
    *,
    paragraph_id: str,
    original_text: str,
    revision: dict[str, Any] | None,
    model_names: Iterable[str] | None = None,
    artefact_names: Iterable[str] | None = None,
    glossary: Iterable[str] | None = None,
    qualifiers: Iterable[str] | None = None,
    scope_phrases: Iterable[str] | None = None,
    us_to_uk: dict[str, str] | None = None,
    forbidden_faithful_substitutes: Iterable[str] | None = None,
    batch_error: str | None = None,
) -> dict[str, Any]:
    """Validate one revision. Passing automation => validated_pending_review only."""
    record: dict[str, Any] = {
        "paragraph_id": paragraph_id,
        "original_text": original_text,
        "revised_text": None,
        "change_summary": None,
        "meaning_changed": None,
        "new_claim_added": None,
        "methodological_qualifiers_preserved": None,
        "scope_preserved": None,
        "british_english_used": None,
        "technical_distinctions_preserved": None,
        "review_state": REVIEW_REJECTED,
        "reject_reasons": [],
        "protected_check": None,
        "language_policy_check": None,
        "structure_issues": [],
        "unchanged": False,
    }

    if batch_error:
        record["reject_reasons"].append(f"batch_error:{batch_error}")
        return record

    if not revision:
        record["reject_reasons"].append("missing_revision")
        return record

    revised = revision.get("revised_text")
    if revised is None:
        record["reject_reasons"].append("missing_revised_text")
        return record

    record["revised_text"] = revised
    record["change_summary"] = revision.get("change_summary")
    record["meaning_changed"] = bool(revision.get("meaning_changed"))
    record["new_claim_added"] = bool(revision.get("new_claim_added"))

    for field in SELF_CHECK_FIELDS:
        value = _as_bool(revision.get(field))
        record[field] = value
        if value is None:
            record["reject_reasons"].append(f"missing_self_check:{field}")
        elif value is False:
            record["reject_reasons"].append(f"self_check_false:{field}")

    claimed_original = revision.get("original_text")
    if claimed_original is not None and _norm_ws(claimed_original) != _norm_ws(original_text):
        record["reject_reasons"].append("original_text_mismatch")

    if record["meaning_changed"]:
        record["reject_reasons"].append("meaning_changed")
    if record["new_claim_added"]:
        record["reject_reasons"].append("new_claim_added")

    protected = compare_protected(
        original_text,
        revised,
        model_names=model_names,
        artefact_names=artefact_names,
        glossary=glossary,
    )
    record["protected_check"] = {
        "ok": protected["ok"],
        "mismatches": protected["mismatches"],
    }
    if not protected["ok"]:
        record["reject_reasons"].append("protected_mismatch")

    policy = language_policy_issues(
        original_text,
        revised,
        qualifiers=qualifiers,
        scope_phrases=scope_phrases,
        us_to_uk=us_to_uk,
        forbidden_faithful_substitutes=forbidden_faithful_substitutes,
    )
    record["language_policy_check"] = policy
    if not policy["ok"]:
        record["reject_reasons"].extend(policy["reasons"])

    structure_issues = markdown_structure_issues(original_text, revised)
    record["structure_issues"] = structure_issues
    if structure_issues:
        record["reject_reasons"].append("invalid_markdown_structure")

    record["unchanged"] = _norm_ws(original_text) == _norm_ws(revised)

    # Deduplicate reject reasons while preserving order
    seen: set[str] = set()
    deduped: list[str] = []
    for reason in record["reject_reasons"]:
        if reason not in seen:
            seen.add(reason)
            deduped.append(reason)
    record["reject_reasons"] = deduped

    if record["reject_reasons"]:
        record["review_state"] = REVIEW_REJECTED
    else:
        record["review_state"] = REVIEW_PENDING

    return record


def validate_batch(
    *,
    target_blocks: list[Any],
    parsed: dict[str, Any] | None,
    batch_error: str | None,
    model_names: Iterable[str] | None = None,
    artefact_names: Iterable[str] | None = None,
    glossary: Iterable[str] | None = None,
    qualifiers: Iterable[str] | None = None,
    scope_phrases: Iterable[str] | None = None,
    us_to_uk: dict[str, str] | None = None,
    forbidden_faithful_substitutes: Iterable[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Validate each target independently.

    Missing IDs are rejected per paragraph. Present IDs are validated even if
    siblings were missing (after optional per-ID retry upstream).
    Whole-batch errors (invalid JSON with no usable revisions) still reject all.
    """
    by_id: dict[str, dict[str, Any]] = {}
    if parsed and isinstance(parsed.get("revisions"), list):
        for item in parsed["revisions"]:
            if isinstance(item, dict) and item.get("paragraph_id"):
                by_id[str(item["paragraph_id"])] = item

    records: list[dict[str, Any]] = []
    fatal_batch = bool(batch_error) and not by_id

    for block in target_blocks:
        pid = block.paragraph_id
        if fatal_batch:
            records.append(
                validate_revision(
                    paragraph_id=pid,
                    original_text=block.text,
                    revision=None,
                    model_names=model_names,
                    artefact_names=artefact_names,
                    glossary=glossary,
                    qualifiers=qualifiers,
                    scope_phrases=scope_phrases,
                    us_to_uk=us_to_uk,
                    forbidden_faithful_substitutes=forbidden_faithful_substitutes,
                    batch_error=batch_error,
                )
            )
            continue

        revision = by_id.get(pid)
        item_error = None if revision else "missing_revision_after_retry"
        records.append(
            validate_revision(
                paragraph_id=pid,
                original_text=block.text,
                revision=revision,
                model_names=model_names,
                artefact_names=artefact_names,
                glossary=glossary,
                qualifiers=qualifiers,
                scope_phrases=scope_phrases,
                us_to_uk=us_to_uk,
                forbidden_faithful_substitutes=forbidden_faithful_substitutes,
                batch_error=item_error,
            )
        )
    return records
