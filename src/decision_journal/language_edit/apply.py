"""Apply approved language-edit revisions to run-directory Markdown copies only."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from decision_journal.language_edit.human_review import text_for_later_apply
from decision_journal.language_edit.inventory import inventory_file
from decision_journal.language_edit.validate import (
    REVIEW_APPROVED,
    REVIEW_REJECTED_BY_HUMAN,
    validate_revision,
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _norm_ws(text: str) -> str:
    return " ".join((text or "").split())


def apply_approved_to_markdown_copy(
    *,
    run_dir: Path,
    canonical_md: Path,
    output_md: Path,
    config: dict[str, Any],
    submitted_docx: Path | None = None,
    file_slug_filter: str | None = "abstract",
    immutable_extra: dict[str, Path] | None = None,
    source_md: Path | None = None,
    preserve_section_keys: list[str] | None = None,
    preserve_prefix_until: str | None = None,
    write_manifest: bool = True,
    manifest_filename: str = "apply_manifest.json",
) -> dict[str, Any]:
    """
    Write approved apply_text into a run-directory Markdown copy.

    Reads from source_md (defaults to canonical_md). Never modifies source_md
    or canonical_md. Only approved_by_human rows with apply_text are written.
    rejected_by_human rows retain the original line.
    """
    audit_path = run_dir / "audit.json"
    inventory_path = run_dir / "inventory.json"
    if not audit_path.is_file():
        raise FileNotFoundError(f"Missing audit.json: {audit_path}")
    if not canonical_md.is_file():
        raise FileNotFoundError(f"Missing canonical Markdown: {canonical_md}")

    source = source_md if source_md is not None else canonical_md
    if not source.is_file():
        raise FileNotFoundError(f"Missing source Markdown: {source}")

    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    records = audit.get("revisions") or []

    canonical_hash_before = sha256_file(canonical_md)
    source_hash_before = sha256_file(source)
    submitted_hash_before = (
        sha256_file(submitted_docx) if submitted_docx and submitted_docx.is_file() else None
    )
    extra_before = {
        name: (sha256_file(path) if path.is_file() else None)
        for name, path in (immutable_extra or {}).items()
    }
    source_lines = source.read_text(encoding="utf-8").splitlines()

    def _extract_numbered_sections(lines_in: list[str], keys: list[str]) -> str:
        import re

        heading_re = re.compile(r"^(#{2})\s+(\d+(?:\.\d+)*)\b")
        wanted = set(keys)
        capturing = False
        captured: list[str] = []
        for line in lines_in:
            m = heading_re.match(line)
            if m:
                key = m.group(2)
                if key in wanted:
                    capturing = True
                    captured.append(line)
                    continue
                if capturing:
                    capturing = False
                continue
            if capturing:
                captured.append(line)
        return "\n".join(captured)

    def _extract_prefix_until(lines_in: list[str], stop_section: str) -> str:
        import re

        heading_re = re.compile(r"^(#{2})\s+(\d+(?:\.\d+)*)\b")
        captured: list[str] = []
        for line in lines_in:
            m = heading_re.match(line)
            if m and m.group(2) == stop_section:
                break
            captured.append(line)
        return "\n".join(captured)

    # Optional: hash preserved sections (e.g. 1.1–1.2) from the source baseline
    preserved_before: dict[str, Any] | None = None
    if preserve_section_keys:
        preserved_text = _extract_numbered_sections(source_lines, preserve_section_keys)
        preserved_before = {
            "section_keys": list(preserve_section_keys),
            "sha256": _sha256_text(preserved_text),
            "text_len": len(preserved_text),
        }

    prefix_before: dict[str, Any] | None = None
    if preserve_prefix_until:
        prefix_text = _extract_prefix_until(source_lines, preserve_prefix_until)
        if not prefix_text.strip():
            raise RuntimeError(
                f"Could not extract prefix before ## {preserve_prefix_until} from source."
            )
        prefix_before = {
            "stop_section": preserve_prefix_until,
            "label": "Opening and sections before " + preserve_prefix_until,
            "sha256": _sha256_text(prefix_text),
            "text_len": len(prefix_text),
        }

    # Map paragraph_id -> line span from inventory (preferred) or re-parse source
    id_to_span: dict[str, tuple[int, int]] = {}
    if inventory_path.is_file():
        inv = json.loads(inventory_path.read_text(encoding="utf-8"))
        for file_info in inv.get("files") or []:
            if file_slug_filter and file_info.get("slug") != file_slug_filter:
                continue
            for block in file_info.get("blocks") or []:
                pid = block.get("paragraph_id")
                if pid and block.get("editable"):
                    id_to_span[pid] = (int(block["start_line"]), int(block["end_line"]))
    if not id_to_span:
        parsed = inventory_file(source)
        for block in parsed.editable_blocks:
            assert block.paragraph_id
            id_to_span[block.paragraph_id] = (block.start_line, block.end_line)

    lines = list(source_lines)
    applied: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    post_validation: list[dict[str, Any]] = []

    applied_line_indexes: set[int] = set()
    retained: list[dict[str, Any]] = []

    for rec in records:
        pid = rec.get("paragraph_id")
        if file_slug_filter and pid and not str(pid).startswith(file_slug_filter + "/"):
            skipped.append({"paragraph_id": pid, "reason": "outside_file_filter"})
            continue
        if rec.get("review_state") == REVIEW_REJECTED_BY_HUMAN:
            retained.append({"paragraph_id": pid, "reason": "retained_original_rejected_by_human"})
            continue
        if rec.get("review_state") != REVIEW_APPROVED:
            skipped.append({"paragraph_id": pid, "reason": f"not_approved:{rec.get('review_state')}"})
            continue
        apply_text = text_for_later_apply(rec) or rec.get("apply_text")
        if not apply_text:
            skipped.append({"paragraph_id": pid, "reason": "no_apply_text"})
            continue
        if pid not in id_to_span:
            skipped.append({"paragraph_id": pid, "reason": "missing_inventory_span"})
            continue

        start, end = id_to_span[pid]
        if start != end:
            skipped.append({"paragraph_id": pid, "reason": "multi_line_span_unsupported"})
            continue
        idx = start - 1
        if idx < 0 or idx >= len(lines):
            skipped.append({"paragraph_id": pid, "reason": "line_out_of_range"})
            continue

        original_line = lines[idx]
        if _norm_ws(original_line) != _norm_ws(rec.get("original_text") or ""):
            skipped.append({"paragraph_id": pid, "reason": "source_line_mismatch"})
            continue

        lines[idx] = apply_text
        applied_line_indexes.add(idx)
        applied.append(
            {
                "paragraph_id": pid,
                "proposal_source": rec.get("proposal_source"),
                "start_line": start,
                "end_line": end,
                "human_edit_validation_status": rec.get("human_edit_validation_status"),
            }
        )

        # Post-apply validation against original inventory text
        gate = validate_revision(
            paragraph_id=pid,
            original_text=rec["original_text"],
            revision={
                "paragraph_id": pid,
                "original_text": rec["original_text"],
                "revised_text": apply_text,
                "change_summary": "post_apply_check",
                "meaning_changed": False,
                "new_claim_added": False,
                "methodological_qualifiers_preserved": True,
                "scope_preserved": True,
                "british_english_used": True,
                "technical_distinctions_preserved": True,
            },
            model_names=config.get("protected_model_names"),
            artefact_names=config.get("protected_artefact_names"),
            glossary=config.get("protected_glossary"),
            qualifiers=config.get("methodological_qualifiers"),
            scope_phrases=config.get("scope_boundary_phrases"),
            us_to_uk=config.get("us_to_uk_spelling"),
            forbidden_faithful_substitutes=config.get("forbidden_faithful_substitutes"),
        )
        post_validation.append(
            {
                "paragraph_id": pid,
                "ok": gate["review_state"] == "validated_pending_review"
                and not gate["reject_reasons"],
                "reject_reasons": gate.get("reject_reasons") or [],
                "protected_check_ok": (gate.get("protected_check") or {}).get("ok"),
                "language_policy_ok": (gate.get("language_policy_check") or {}).get("ok"),
                "structure_issues": gate.get("structure_issues") or [],
            }
        )

    if any(not v["ok"] for v in post_validation):
        raise RuntimeError(
            "Post-apply validation failed: "
            + json.dumps([v for v in post_validation if not v["ok"]], ensure_ascii=False)
        )
    if skipped and any(s["reason"] not in {"outside_file_filter"} for s in skipped):
        # Hard-fail on unexpected skips for the requested apply set
        bad = [s for s in skipped if s["reason"] != "outside_file_filter"]
        if bad:
            raise RuntimeError(f"Apply skipped unexpected rows: {bad}")

    # Non-target block integrity: every line NOT deliberately applied must be
    # byte-identical between the source baseline and the output copy.
    non_target_issues: list[dict[str, Any]] = []
    if len(source_lines) != len(lines):
        non_target_issues.append(
            {"reason": "line_count_changed", "source": len(source_lines), "output": len(lines)}
        )
    else:
        for i, (a, b) in enumerate(zip(source_lines, lines)):
            if i in applied_line_indexes:
                continue
            if a != b:
                non_target_issues.append({"reason": "non_target_line_modified", "line": i + 1})
    if non_target_issues:
        raise RuntimeError(f"Non-target block integrity failed: {non_target_issues}")

    non_target_source = "\n".join(
        line for i, line in enumerate(source_lines) if i not in applied_line_indexes
    )
    non_target_output = "\n".join(
        line for i, line in enumerate(lines) if i not in applied_line_indexes
    )
    non_target_hash_before = _sha256_text(non_target_source)
    non_target_hash_after = _sha256_text(non_target_output)
    if non_target_hash_before != non_target_hash_after:
        raise RuntimeError("Non-target block hash mismatch — aborting.")

    output_md.parent.mkdir(parents=True, exist_ok=True)
    # Preserve trailing newline convention
    text_out = "\n".join(lines)
    if source.read_text(encoding="utf-8").endswith("\n"):
        text_out += "\n"
    output_md.write_text(text_out, encoding="utf-8")

    # Preserved-section check on output
    preserved_after: dict[str, Any] | None = None
    if preserve_section_keys and preserved_before is not None:
        preserved_text_after = _extract_numbered_sections(lines, preserve_section_keys)
        preserved_after = {
            "section_keys": list(preserve_section_keys),
            "sha256": _sha256_text(preserved_text_after),
            "text_len": len(preserved_text_after),
            "byte_identical": _sha256_text(preserved_text_after) == preserved_before["sha256"],
        }
        if not preserved_after["byte_identical"]:
            raise RuntimeError(
                f"Preserved sections {preserve_section_keys} are not byte-identical after apply."
            )

    prefix_after: dict[str, Any] | None = None
    if preserve_prefix_until and prefix_before is not None:
        prefix_text_after = _extract_prefix_until(lines, preserve_prefix_until)
        prefix_after = {
            "stop_section": preserve_prefix_until,
            "label": prefix_before["label"],
            "sha256": _sha256_text(prefix_text_after),
            "text_len": len(prefix_text_after),
            "byte_identical": _sha256_text(prefix_text_after) == prefix_before["sha256"],
        }
        if not prefix_after["byte_identical"]:
            raise RuntimeError(
                f"Preserved prefix before ## {preserve_prefix_until} is not byte-identical after apply."
            )

    canonical_hash_after = sha256_file(canonical_md)
    source_hash_after = sha256_file(source)
    submitted_hash_after = (
        sha256_file(submitted_docx) if submitted_docx and submitted_docx.is_file() else None
    )
    output_hash = sha256_file(output_md)

    if canonical_hash_before != canonical_hash_after:
        raise RuntimeError("Canonical Markdown changed during apply — aborting safety invariant.")
    if source_hash_before != source_hash_after:
        raise RuntimeError("Source baseline Markdown changed during apply — aborting.")
    if (
        submitted_docx
        and submitted_hash_before is not None
        and submitted_hash_after != submitted_hash_before
    ):
        raise RuntimeError("Submitted DOCX changed during apply — aborting safety invariant.")

    extra_after = {
        name: (sha256_file(path) if path.is_file() else None)
        for name, path in (immutable_extra or {}).items()
    }
    for name in extra_before:
        if extra_before[name] != extra_after.get(name):
            raise RuntimeError(f"Immutable file '{name}' changed during apply — aborting.")

    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "applied_count": len(applied),
        "rejected_count": len(retained),
        "retained_original": retained,
        "paragraphs": applied,
        "post_apply_validation": post_validation,
        "line_count": {
            "source": len(source_lines),
            "output": len(lines),
            "unchanged": len(source_lines) == len(lines),
        },
        "non_target_block_check": {
            "ok": True,
            "sha256_before": non_target_hash_before,
            "sha256_after": non_target_hash_after,
            "applied_lines": sorted(i + 1 for i in applied_line_indexes),
        },
        "sections_preserved": {
            "before": preserved_before,
            "after": preserved_after,
            "byte_identical": (preserved_after or {}).get("byte_identical")
            if preserved_after
            else None,
        },
        "prefix_preserved": {
            "before": prefix_before,
            "after": prefix_after,
            "byte_identical": (prefix_after or {}).get("byte_identical")
            if prefix_after
            else None,
        },
        "historical_validation_failures": [
            {
                "paragraph_id": rec.get("paragraph_id"),
                "review_state": rec.get("review_state"),
                "llm_reject_reasons_history": rec.get("llm_reject_reasons_history") or [],
                "active_reject_reasons": rec.get("reject_reasons") or [],
            }
            for rec in records
            if rec.get("llm_reject_reasons_history")
        ],
        "original_source": {
            "path": str(source),
            "sha256": source_hash_before,
            "unchanged": True,
            "role": "approved_baseline" if source.resolve() != canonical_md.resolve() else "canonical",
        },
        "canonical_markdown": {
            "path": str(canonical_md),
            "sha256": canonical_hash_before,
            "unchanged": True,
        },
        "approved_output": {
            "path": str(output_md),
            "sha256": output_hash,
        },
        "submitted_docx": {
            "path": str(submitted_docx) if submitted_docx else None,
            "sha256": submitted_hash_before,
            "unchanged": True if submitted_hash_before is not None else None,
        },
        "immutable_extra": {
            name: {
                "path": str((immutable_extra or {}).get(name)),
                "sha256": extra_before.get(name),
                "unchanged": extra_before.get(name) == extra_after.get(name),
            }
            for name in (immutable_extra or {})
        },
        "markdown_apply": True,
        "docx_rebuild": False,
        "skipped": skipped,
    }

    # Annotate audit
    audit["markdown_apply"] = True
    approved_paths = list(audit.get("markdown_approved_paths") or [])
    if str(output_md) not in approved_paths:
        approved_paths.append(str(output_md))
    audit["markdown_approved_paths"] = approved_paths
    audit["markdown_approved_path"] = str(output_md)
    if write_manifest:
        audit["apply_manifest_path"] = str(run_dir / manifest_filename)
    for rec in records:
        for item in applied:
            if rec.get("paragraph_id") == item["paragraph_id"]:
                rec["applied_to_markdown_copy"] = True
                rec["applied_output_path"] = str(output_md)
        for item in retained:
            if rec.get("paragraph_id") == item["paragraph_id"]:
                rec["applied_to_markdown_copy"] = False
                rec["retained_original_on_apply"] = True
    audit_path.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if write_manifest:
        (run_dir / manifest_filename).write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    return manifest
