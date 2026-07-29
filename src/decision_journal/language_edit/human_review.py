"""Human-review finalisation with optional validated human edits."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from decision_journal.language_edit.validate import (
    REVIEW_APPROVED,
    REVIEW_PENDING,
    REVIEW_REJECTED,
    REVIEW_REJECTED_BY_HUMAN,
    validate_revision,
)

PROPOSAL_LLM = "llm"
PROPOSAL_HUMAN = "human_edit"

HUMAN_APPROVAL_FIELDS = [
    "paragraph_id",
    "review_state",
    "human_decision",
    "human_notes",
    "proposal_source",
    "human_revised_text",
    "human_edit_validation_status",
    "human_edit_validation_reasons",
    "change_summary",
    "unchanged",
]


def _norm_ws(text: str) -> str:
    return " ".join((text or "").split())


def validate_human_replacement(
    *,
    paragraph_id: str,
    original_text: str,
    human_revised_text: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    """Run the full automated gate on human-edited text vs original."""
    synthetic = {
        "paragraph_id": paragraph_id,
        "original_text": original_text,
        "revised_text": human_revised_text,
        "change_summary": "human_edit",
        "meaning_changed": False,
        "new_claim_added": False,
        # Self-checks are asserted true by the human editor; automation still
        # re-validates via protected/policy/structure gates below.
        "methodological_qualifiers_preserved": True,
        "scope_preserved": True,
        "british_english_used": True,
        "technical_distinctions_preserved": True,
    }
    record = validate_revision(
        paragraph_id=paragraph_id,
        original_text=original_text,
        revision=synthetic,
        model_names=config.get("protected_model_names"),
        artefact_names=config.get("protected_artefact_names"),
        glossary=config.get("protected_glossary"),
        qualifiers=config.get("methodological_qualifiers"),
        scope_phrases=config.get("scope_boundary_phrases"),
        us_to_uk=config.get("us_to_uk_spelling"),
        forbidden_faithful_substitutes=config.get("forbidden_faithful_substitutes"),
    )
    ok = record["review_state"] == REVIEW_PENDING and not record["reject_reasons"]
    return {
        "ok": ok,
        "status": "passed" if ok else "failed",
        "reasons": list(record.get("reject_reasons") or []),
        "validation_record": record,
    }


def text_for_later_apply(record: dict[str, Any]) -> str | None:
    """Return text eligible for a future Markdown apply, or None if not approved."""
    if record.get("review_state") != REVIEW_APPROVED:
        return None
    human_text = (record.get("human_revised_text") or "").strip()
    if (
        record.get("proposal_source") == PROPOSAL_HUMAN
        and human_text
        and record.get("human_edit_validation_status") == "passed"
    ):
        return human_text
    if record.get("proposal_source") == PROPOSAL_LLM:
        revised = record.get("revised_text")
        if revised is None:
            return None
        # Never apply previously rejected LLM text
        if record.get("llm_review_state_before_approval") == REVIEW_REJECTED:
            return None
        return revised
    # Approved with human text path
    if human_text and record.get("human_edit_validation_status") == "passed":
        return human_text
    return record.get("revised_text")


def apply_human_decisions(
    records: list[dict[str, Any]],
    decisions: dict[str, dict[str, Any]],
    *,
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Update revision records from human decisions.

    decisions[paragraph_id] keys:
      - human_decision: approved_by_human | rejected_by_human
      - human_revised_text: optional replacement (validated before approval)
      - human_notes: optional
    """
    updated: list[dict[str, Any]] = []
    by_id = {r["paragraph_id"]: dict(r) for r in records}

    for pid, rec in by_id.items():
        decision = decisions.get(pid, {})
        human_decision = (decision.get("human_decision") or "").strip()
        human_notes = decision.get("human_notes") or ""
        human_text_raw = decision.get("human_revised_text")
        human_text = None
        if human_text_raw is not None:
            human_text = _norm_ws(str(human_text_raw)) if str(human_text_raw).strip() else ""

        # Preserve the original automated outcome across repeated finalisation.
        # Older artefacts may have had this field overwritten by a second run;
        # reconstruct that outcome from the retained LLM validation history.
        llm_initial_state = rec.get("llm_original_review_state")
        if llm_initial_state not in (REVIEW_PENDING, REVIEW_REJECTED):
            prior_recorded = rec.get("llm_review_state_before_approval")
            if prior_recorded in (REVIEW_PENDING, REVIEW_REJECTED):
                llm_initial_state = prior_recorded
            elif rec.get("llm_reject_reasons_history"):
                llm_initial_state = REVIEW_REJECTED
            # Fall back to the record's current review_state when the LLM history
            # fields are missing (required for test cases built from minimal records).
            elif rec.get("review_state") in (REVIEW_PENDING, REVIEW_REJECTED):
                llm_initial_state = rec.get("review_state")
            else:
                llm_initial_state = REVIEW_PENDING
        rec["llm_original_review_state"] = llm_initial_state
        rec["llm_review_state_before_approval"] = llm_initial_state
        rec["llm_validation_outcome_history"] = {
            "review_state": llm_initial_state,
            "reject_reasons": list(rec.get("llm_reject_reasons_history") or []),
        }
        rec["human_decision"] = human_decision or rec.get("human_decision") or ""
        rec["human_notes"] = human_notes
        rec["human_revised_text"] = human_text if human_text else None
        rec["proposal_source"] = None
        rec["human_edit_validation_status"] = None
        rec["human_edit_validation_reasons"] = []
        rec["apply_text"] = None

        if not human_decision:
            updated.append(rec)
            continue

        if human_decision == REVIEW_REJECTED_BY_HUMAN:
            rec["review_state"] = REVIEW_REJECTED_BY_HUMAN
            rec["proposal_source"] = PROPOSAL_LLM
            # Preserve prior automated failures as history; clear active rejects.
            prior_reasons = [
                r
                for r in (rec.get("reject_reasons") or [])
                if r and not str(r).startswith("unknown_human_decision:")
            ]
            if prior_reasons or rec.get("llm_review_state_before_approval") == REVIEW_REJECTED:
                hist = list(rec.get("llm_reject_reasons_history") or [])
                for reason in prior_reasons:
                    if reason not in hist:
                        hist.append(reason)
                if (
                    rec.get("llm_review_state_before_approval") == REVIEW_REJECTED
                    and not prior_reasons
                    and not hist
                ):
                    # Still record that an automated rejection existed
                    if "rejected_by_validation" not in hist:
                        hist.append("rejected_by_validation")
                if any(reason != "rejected_by_validation" for reason in hist):
                    hist = [
                        reason for reason in hist if reason != "rejected_by_validation"
                    ]
                rec["llm_reject_reasons_history"] = hist
                rec["llm_validation_outcome_history"] = {
                    "review_state": rec["llm_review_state_before_approval"],
                    "reject_reasons": list(hist),
                }
            rec["reject_reasons"] = []
            rec["apply_text"] = None
            updated.append(rec)
            continue

        if human_decision != REVIEW_APPROVED:
            rec["reject_reasons"] = list(rec.get("reject_reasons") or [])
            rec["reject_reasons"].append(f"unknown_human_decision:{human_decision}")
            updated.append(rec)
            continue

        # Approval path
        if human_text:
            gate = validate_human_replacement(
                paragraph_id=pid,
                original_text=rec["original_text"],
                human_revised_text=human_text,
                config=config,
            )
            rec["proposal_source"] = PROPOSAL_HUMAN
            rec["human_revised_text"] = human_text
            rec["human_edit_validation_status"] = gate["status"]
            rec["human_edit_validation_reasons"] = gate["reasons"]
            # Merge detailed checks from the human-edit validation pass
            vrec = gate["validation_record"]
            rec["human_edit_protected_check"] = vrec.get("protected_check")
            rec["human_edit_language_policy_check"] = vrec.get("language_policy_check")
            rec["human_edit_structure_issues"] = vrec.get("structure_issues")
            if gate["ok"]:
                rec["review_state"] = REVIEW_APPROVED
                rec["apply_text"] = human_text
                # Align self-check fields with validated human edit
                for field in (
                    "methodological_qualifiers_preserved",
                    "scope_preserved",
                    "british_english_used",
                    "technical_distinctions_preserved",
                ):
                    rec[field] = True
            else:
                # Do not approve failed human edits
                rec["review_state"] = REVIEW_REJECTED_BY_HUMAN
                rec["human_decision"] = REVIEW_REJECTED_BY_HUMAN
                rec["human_notes"] = (
                    (human_notes + " | " if human_notes else "")
                    + "human_edit_failed_validation; original Markdown retained"
                )
                rec["apply_text"] = None
        else:
            # Approve LLM proposal as-is — only if it had passed automation
            prior = rec.get("llm_review_state_before_approval")
            if prior != REVIEW_PENDING:
                rec["review_state"] = REVIEW_REJECTED_BY_HUMAN
                rec["human_decision"] = REVIEW_REJECTED_BY_HUMAN
                rec["proposal_source"] = PROPOSAL_LLM
                rec["human_notes"] = (
                    (human_notes + " | " if human_notes else "")
                    + f"cannot_approve_llm_from_state:{prior}"
                )
                rec["apply_text"] = None
            else:
                rec["review_state"] = REVIEW_APPROVED
                rec["proposal_source"] = PROPOSAL_LLM
                rec["human_edit_validation_status"] = "not_applicable"
                rec["human_edit_validation_reasons"] = []
                rec["apply_text"] = rec.get("revised_text")

        updated.append(rec)

    # Preserve original order
    order = [r["paragraph_id"] for r in records]
    by_new = {r["paragraph_id"]: r for r in updated}
    return [by_new[pid] for pid in order if pid in by_new]


def load_decisions_csv(path: Path) -> dict[str, dict[str, Any]]:
    decisions: dict[str, dict[str, Any]] = {}
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            pid = (row.get("paragraph_id") or "").strip()
            if not pid:
                continue
            decisions[pid] = {
                "human_decision": (row.get("human_decision") or "").strip(),
                "human_notes": row.get("human_notes") or "",
                "human_revised_text": row.get("human_revised_text") or None,
            }
    return decisions


def write_decisions_template_csv(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=HUMAN_APPROVAL_FIELDS)
        writer.writeheader()
        for rec in records:
            state = rec["review_state"]
            human_decision = ""
            if state == REVIEW_REJECTED:
                human_decision = "rejected_by_validation"
            writer.writerow(
                {
                    "paragraph_id": rec["paragraph_id"],
                    "review_state": state,
                    "human_decision": human_decision,
                    "human_notes": "",
                    "proposal_source": "",
                    "human_revised_text": "",
                    "human_edit_validation_status": "",
                    "human_edit_validation_reasons": "",
                    "change_summary": rec.get("change_summary") or "",
                    "unchanged": rec.get("unchanged", False),
                }
            )
