"""Wave 3 examiner evidence package validation (offline)."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "examiner_evidence"
PKG = ROOT / "outputs" / "distinction_strategy" / "03_reproducibility_package"
AUDIT_E = ROOT / "outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final"
CONSISTENCY = (
    ROOT
    / "outputs/framework_mapping/run_20260727_094015_post60_coding_consistency_audit/CONSISTENCY_CORRECTED_REFERENCE.csv"
)
JOURNAL = ROOT / "data/manifests/phase1_decision_journal.json"

MANDATORY_DOC_FILES = [
    "README.md",
    "ARTEFACT_MANIFEST.csv",
    "DATA_LINEAGE.md",
    "REPRODUCTION_RUNBOOK.md",
    "REPRODUCIBILITY_LIMITS.md",
    "EXAMINER_EVIDENCE_MAP.md",
    "COMMAND_REFERENCE.md",
    "DEMO_CASE_SELECTION.md",
    "AUDIT_E_CANONICAL_LOCATOR.md",
    "SECURITY_AND_PRIVACY_NOTE.md",
]

DEMO_IDS = ["phase1-016", "phase1-082", "phase1-090", "phase1-246"]

CLAIM_MARKERS = [
    "414",
    "351/414",
    "5 agreement",
    "10 silence",
    "0 dissonance",
    "1/6",
    "5/6",
    "21/50",
    "0.48",
    "0.39",
    "20 clusters",
    "11/60",
    "37/60",
    "26/60",
    "8/25/20/7",
    "50/53",
    "49/50",
]

SECRET_RE = re.compile(
    r"(?i)(openai_api_key\s*=\s*sk-|sk-(?:proj|live)-[A-Za-z0-9]{10,}|BEGIN RSA PRIVATE KEY)"
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _sums() -> dict[str, str]:
    path = DOCS / "SHA256SUMS"
    if not path.exists():
        path = PKG / "SHA256SUMS"
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        digest, _, rel = line.partition("  ")
        if rel:
            out[rel.replace("\\", "/")] = digest.strip()
    return out


def test_examiner_docs_exist() -> None:
    for name in MANDATORY_DOC_FILES:
        assert (DOCS / name).is_file(), f"missing {name}"


def test_evidence_map_mentions_mandatory_claims() -> None:
    text = (DOCS / "EXAMINER_EVIDENCE_MAP.md").read_text(encoding="utf-8")
    for marker in CLAIM_MARKERS:
        assert marker in text, f"evidence map missing claim marker {marker!r}"


def test_artefact_manifest_has_required_columns() -> None:
    rows = list(csv.DictReader((DOCS / "ARTEFACT_MANIFEST.csv").open(encoding="utf-8")))
    required = {
        "artefact_id",
        "stage",
        "description",
        "authoritative_path",
        "source_or_parent",
        "input_hash",
        "output_hash",
        "git_status",
        "reproducibility_class",
        "requires_api",
        "human_adjudicated",
        "dissertation_claims_supported",
        "notes",
    }
    assert rows and required <= set(rows[0].keys())
    # Guard: human-adjudicated rows must not be class 1 offline fully auto
    for row in rows:
        if row["human_adjudicated"].lower() == "true":
            assert row["reproducibility_class"].strip() in {"5", "5/1", "1/5", "4", "5/4"}, row


def test_sha256sums_match_files() -> None:
    sums = _sums()
    assert sums, "SHA256SUMS empty"
    for rel, digest in sums.items():
        path = ROOT / rel
        assert path.is_file(), f"hashed path missing: {rel}"
        assert sha256(path) == digest, f"hash mismatch: {rel}"


def test_audit_e_single_authoritative_per_claim() -> None:
    loc = (DOCS / "AUDIT_E_CANONICAL_LOCATOR.md").read_text(encoding="utf-8")
    # Exactly one "Use this path only" table with required claims
    for claim in ("JEE = 11/60", "DQ = 37/60", "Combined = 26/60", "Faithfulness 8/25/20/7"):
        assert claim in loc
    # Precedence rule present
    assert "Exactly **one** authoritative path per dissertation claim" in loc
    # Aggregate counts resolve
    jee = list(csv.DictReader((AUDIT_E / "AUDIT_E_JEE_SUMMARY.csv").open(encoding="utf-8")))
    assert any(r.get("label") == "mapped" and r.get("count") == "11" for r in jee)
    dq = list(csv.DictReader((AUDIT_E / "AUDIT_E_DQ_SUMMARY.csv").open(encoding="utf-8")))
    assert any(r.get("count") == "37" for r in dq)
    ct = list(
        csv.DictReader((AUDIT_E / "crosstabs/AUDIT_E_jee_vs_dq_mapped.csv").open(encoding="utf-8"))
    )
    assert any(
        r.get("jee_outcome") == "unmapped"
        and r.get("dq_outcome") == "mapped"
        and r.get("count") == "26"
        for r in ct
    )
    man = json.loads((AUDIT_E / "AUDIT_E_MANIFEST.json").read_text(encoding="utf-8"))
    tc = man["traceability_category_counts"]
    assert tc.get("exact_or_near_verbatim") == 8
    assert tc.get("substantively_faithful_paraphrase") == 25
    assert tc.get("materially_unsupported_or_altered") == 20
    assert tc.get("traceability_false") == 7
    assert man.get("jee_mapped") == 11
    assert man.get("dq_mapped") == 37


def test_demo_ids_exist_in_journal_and_have_quotes() -> None:
    journal = json.loads(JOURNAL.read_text(encoding="utf-8"))
    by = {e["id"]: e for e in journal["entries"]}
    for jid in DEMO_IDS:
        assert jid in by
        assert by[jid]["source_quote"].strip()
        assert by[jid]["decision"].strip()
        snap = PKG / "demos" / f"{jid}.json"
        assert snap.is_file(), f"missing demo snapshot {snap}"
        data = json.loads(snap.read_text(encoding="utf-8"))
        assert data["journal_id"] == jid
        assert data["source_quote"] == by[jid]["source_quote"]
        assert data["decision"] == by[jid]["decision"]
        assert "reviewer_name" not in data


def test_demo_teaching_points() -> None:
    sample = json.loads(
        (ROOT / "configs/evaluation/confidence_validation_sample.json").read_text(encoding="utf-8")
    )
    sby = {i["journal_id"]: i for i in sample["items"]}
    assert sby["phase1-016"]["human_valid_decision"] == "yes"
    assert sby["phase1-016"]["human_confidence"] == "high"
    assert sby["phase1-082"]["human_valid_decision"] == "no"
    assert sby["phase1-082"]["human_confidence"] == "high"
    faith = {
        r["entry_id"]: r["approved_traceability_category"]
        for r in csv.DictReader(
            (AUDIT_E / "AUDIT_E_TRACEABILITY_HUMAN_CLASSIFICATION.csv").open(encoding="utf-8")
        )
    }
    assert faith["phase1-090"] == "materially_unsupported_or_altered"
    corr = {
        r["entry_id"]: r
        for r in csv.DictReader(CONSISTENCY.open(encoding="utf-8"))
    }
    assert corr["phase1-246"]["human_primary_JEE"] == "P3"
    assert corr["phase1-246"]["human_primary_DQ"] == "commitment_to_follow_through"


def test_no_secrets_in_examiner_pack() -> None:
    roots = [DOCS, PKG]
    for root in roots:
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() in {".docx", ".pdf", ".png"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            assert not SECRET_RE.search(text), f"secret-like pattern in {path}"


def test_no_private_ukhsa_bundle_paths() -> None:
    # Package must not reference private UKHSA trees
    blob = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in DOCS.glob("*.md"))
    assert "ukhsa_restricted" not in blob.lower()
    assert "data/raw/ukhsa" not in blob.lower()


def test_raw_processed_trees_not_tracked_by_mistake() -> None:
    # Soft check: package demos must not embed multi-kilobyte full transcripts
    for path in (PKG / "demos").glob("phase1-*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len(data.get("source_quote", "")) < 2000
        assert "full_transcript" not in data


def test_human_claims_not_labelled_fully_offline_in_limits() -> None:
    limits = (DOCS / "REPRODUCIBILITY_LIMITS.md").read_text(encoding="utf-8")
    assert "Human judgements are not auto-reproducible" in limits
    assert "No byte-identical LLM regeneration" in limits


def test_package_manifest_present() -> None:
    assert (PKG / "PACKAGE_MANIFEST.json").is_file()
    assert (PKG / "validation" / "PACKAGE_VALIDATION_LOG.json").is_file()
