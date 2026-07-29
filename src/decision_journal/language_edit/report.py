"""Write language-edit run artefacts (audit, CSV, diff, validation report)."""

from __future__ import annotations

import csv
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from decision_journal.language_edit.validate import (
    REVIEW_APPROVED,
    REVIEW_PENDING,
    REVIEW_REJECTED,
    REVIEW_REJECTED_BY_HUMAN,
)


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_human_approvals_csv(path: Path, records: list[dict[str, Any]]) -> None:
    """Human approval worksheet. Only approved_by_human may enter a future apply/build."""
    fieldnames = [
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
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for rec in records:
            state = rec["review_state"]
            human_decision = rec.get("human_decision") or ""
            if not human_decision and state == REVIEW_REJECTED:
                human_decision = "rejected_by_validation"
            elif not human_decision and state == REVIEW_APPROVED:
                human_decision = REVIEW_APPROVED
            elif not human_decision and state == REVIEW_REJECTED_BY_HUMAN:
                human_decision = REVIEW_REJECTED_BY_HUMAN
            reasons = rec.get("human_edit_validation_reasons") or []
            if isinstance(reasons, list):
                reasons_s = ";".join(reasons)
            else:
                reasons_s = str(reasons)
            writer.writerow(
                {
                    "paragraph_id": rec["paragraph_id"],
                    "review_state": state,
                    "human_decision": human_decision,
                    "human_notes": rec.get("human_notes") or "",
                    "proposal_source": rec.get("proposal_source") or "",
                    "human_revised_text": rec.get("human_revised_text") or "",
                    "human_edit_validation_status": rec.get("human_edit_validation_status")
                    or "",
                    "human_edit_validation_reasons": reasons_s,
                    "change_summary": rec.get("change_summary") or "",
                    "unchanged": rec.get("unchanged", False),
                }
            )


def write_changes_csv(path: Path, records: list[dict[str, Any]]) -> None:
    fieldnames = [
        "paragraph_id",
        "review_state",
        "proposal_source",
        "unchanged",
        "meaning_changed",
        "new_claim_added",
        "methodological_qualifiers_preserved",
        "scope_preserved",
        "british_english_used",
        "technical_distinctions_preserved",
        "human_edit_validation_status",
        "change_summary",
        "reject_reasons",
        "human_edit_validation_reasons",
    ]
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for rec in records:
            he_reasons = rec.get("human_edit_validation_reasons") or []
            if isinstance(he_reasons, list):
                he_reasons_s = ";".join(he_reasons)
            else:
                he_reasons_s = str(he_reasons)
            writer.writerow(
                {
                    "paragraph_id": rec["paragraph_id"],
                    "review_state": rec["review_state"],
                    "proposal_source": rec.get("proposal_source") or "",
                    "unchanged": rec.get("unchanged", False),
                    "meaning_changed": rec.get("meaning_changed"),
                    "new_claim_added": rec.get("new_claim_added"),
                    "methodological_qualifiers_preserved": rec.get(
                        "methodological_qualifiers_preserved"
                    ),
                    "scope_preserved": rec.get("scope_preserved"),
                    "british_english_used": rec.get("british_english_used"),
                    "technical_distinctions_preserved": rec.get(
                        "technical_distinctions_preserved"
                    ),
                    "human_edit_validation_status": rec.get("human_edit_validation_status")
                    or "",
                    "change_summary": rec.get("change_summary") or "",
                    "reject_reasons": ";".join(rec.get("reject_reasons") or []),
                    "human_edit_validation_reasons": he_reasons_s,
                }
            )


def _esc(text: str | None) -> str:
    return html.escape(text or "")


def write_diff_html(
    path: Path,
    *,
    run_id: str,
    mode: str,
    records: list[dict[str, Any]],
) -> None:
    rows = []
    for rec in records:
        state = rec["review_state"]
        badge = {
            REVIEW_PENDING: "pending",
            REVIEW_REJECTED: "rejected",
            REVIEW_APPROVED: "approved",
            REVIEW_REJECTED_BY_HUMAN: "rejected-human",
        }.get(state, state)
        apply_text = rec.get("apply_text") or (
            rec.get("human_revised_text")
            if rec.get("proposal_source") == "human_edit"
            and rec.get("review_state") == REVIEW_APPROVED
            else rec.get("revised_text")
        )
        source = rec.get("proposal_source") or "llm"
        rows.append(
            f"""
<section class="item {badge}">
  <h2>{_esc(rec['paragraph_id'])} <span class="badge">{_esc(state)}</span></h2>
  <p class="summary"><strong>Summary:</strong> {_esc(rec.get('change_summary'))}</p>
  <p class="meta">source={_esc(source)} |
     unchanged={rec.get('unchanged')} |
     meaning_changed={rec.get('meaning_changed')} |
     new_claim_added={rec.get('new_claim_added')} |
     human_edit_validation={_esc(str(rec.get('human_edit_validation_status') or ''))} |
     reject={_esc(';'.join(rec.get('reject_reasons') or []))}</p>
  <div class="cols">
    <div><h3>Original</h3><pre>{_esc(rec.get('original_text'))}</pre></div>
    <div><h3>Approved / proposed text</h3><pre>{_esc(apply_text)}</pre></div>
  </div>
</section>
"""
        )

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>Language edit diff — {html.escape(run_id)}</title>
<style>
body {{ font-family: Georgia, serif; margin: 2rem; line-height: 1.4; }}
.badge {{ font-size: 0.75rem; padding: 0.15rem 0.45rem; border-radius: 4px;
          background: #ddd; text-transform: uppercase; }}
.item.pending .badge {{ background: #cfe8ff; }}
.item.rejected .badge {{ background: #ffd0d0; }}
.item.rejected-human .badge {{ background: #ffe0b3; }}
.item.approved .badge {{ background: #d4edda; }}
.cols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }}
pre {{ white-space: pre-wrap; background: #f7f7f7; padding: 0.75rem; border: 1px solid #ddd; }}
.note {{ background: #fff8e6; border: 1px solid #e6d8a8; padding: 0.75rem; }}
</style>
</head>
<body>
<h1>Language-edit proposals</h1>
<p>Run <code>{_esc(run_id)}</code> · mode <code>{_esc(mode)}</code></p>
<p class="note"><strong>Review rule:</strong> <code>validated_pending_review</code> means
automated checks passed. It does <em>not</em> include the text in a review manuscript.
Only <code>approved_by_human</code> revisions may be applied later.</p>
{''.join(rows)}
</body>
</html>
"""
    path.write_text(doc, encoding="utf-8")


def write_validation_report(
    path: Path,
    *,
    run_id: str,
    mode: str,
    dry_run: bool,
    records: list[dict[str, Any]],
    source_files: list[str],
    notes: list[str] | None = None,
) -> None:
    pending = sum(1 for r in records if r["review_state"] == REVIEW_PENDING)
    rejected = sum(1 for r in records if r["review_state"] == REVIEW_REJECTED)
    approved = sum(1 for r in records if r["review_state"] == REVIEW_APPROVED)
    rejected_human = sum(1 for r in records if r["review_state"] == REVIEW_REJECTED_BY_HUMAN)
    unchanged = sum(1 for r in records if r.get("unchanged"))

    lines = [
        f"# Language-edit validation report — `{run_id}`",
        "",
        f"- Generated (UTC): {datetime.now(timezone.utc).isoformat()}",
        f"- Mode: `{mode}`",
        f"- Dry run: **{dry_run}** (no Markdown apply; canonical MD and submitted DOCX untouched)",
        f"- Source files: {', '.join(f'`{s}`' for s in source_files)}",
        "",
        "## Review-state counts",
        "",
        f"- `{REVIEW_PENDING}`: {pending}",
        f"- `{REVIEW_REJECTED}`: {rejected}",
        f"- `{REVIEW_APPROVED}`: {approved}",
        f"- `{REVIEW_REJECTED_BY_HUMAN}`: {rejected_human}",
        f"- Unchanged proposals: {unchanged}",
        "",
        "## Inclusion rule",
        "",
        "Passing automated validation sets `validated_pending_review` only.",
        "Revised Markdown for build must include **only** `approved_by_human` revisions.",
        "If `human_revised_text` is present, it must pass protected-element, language-policy",
        "and structure checks before approval (`proposal_source=human_edit`).",
        f"`{REVIEW_REJECTED_BY_HUMAN}` retains original Markdown.",
        "",
        "## Per-paragraph outcomes",
        "",
    ]
    for rec in records:
        reasons = ", ".join(rec.get("reject_reasons") or []) or "—"
        he_reasons = ", ".join(rec.get("human_edit_validation_reasons") or []) or "—"
        lines.append(
            f"- `{rec['paragraph_id']}` — **{rec['review_state']}** — "
            f"source=`{rec.get('proposal_source') or '—'}` — "
            f"human_edit_validation=`{rec.get('human_edit_validation_status') or '—'}` — "
            f"{rec.get('change_summary') or '(no summary)'} — "
            f"rejects: {reasons} — human_edit_reasons: {he_reasons}"
        )

    lines.extend(
        [
            "",
            "## Safety",
            "",
            "- Submitted DOCX (`Lawal_MSc_Dissertation.docx`) was not modified.",
            "- Canonical Markdown under `dissertation/` was not modified.",
            "- No DOCX rebuild was performed in this stage.",
            "",
        ]
    )
    if notes:
        lines.append("## Notes")
        lines.append("")
        for note in notes:
            lines.append(f"- {note}")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def write_audit(
    path: Path,
    *,
    run_id: str,
    mode: str,
    model: str,
    dry_run: bool,
    config_snapshot: dict[str, Any],
    inventory: list[dict[str, Any]],
    records: list[dict[str, Any]],
    batches: list[dict[str, Any]],
) -> None:
    payload = {
        "run_id": run_id,
        "mode": mode,
        "model": model,
        "temperature": config_snapshot.get("temperature", 0),
        "dry_run": dry_run,
        "markdown_apply": False,
        "docx_rebuild": False,
        "review_states_legend": {
            REVIEW_REJECTED: "Failed automated validation; not eligible for approval without re-run",
            REVIEW_PENDING: "Passed automation; awaiting human decision",
            REVIEW_APPROVED: "Human approved for inclusion in review manuscript (later stage)",
            REVIEW_REJECTED_BY_HUMAN: "Human rejected after review; original Markdown retained",
        },
        "config_snapshot": config_snapshot,
        "inventory": inventory,
        "batches": batches,
        "revisions": records,
        "counts": {
            REVIEW_PENDING: sum(1 for r in records if r["review_state"] == REVIEW_PENDING),
            REVIEW_REJECTED: sum(1 for r in records if r["review_state"] == REVIEW_REJECTED),
            REVIEW_APPROVED: sum(1 for r in records if r["review_state"] == REVIEW_APPROVED),
            REVIEW_REJECTED_BY_HUMAN: sum(
                1 for r in records if r["review_state"] == REVIEW_REJECTED_BY_HUMAN
            ),
        },
    }
    write_json(path, payload)
