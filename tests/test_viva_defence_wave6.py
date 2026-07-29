"""Wave 6 viva defence package validation."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIVA = ROOT / "docs" / "viva"
PKG = ROOT / "outputs" / "distinction_strategy" / "06_viva_defence"

JOURNAL = ROOT / "data" / "manifests" / "phase1_decision_journal.json"
SAMPLE = ROOT / "configs" / "evaluation" / "confidence_validation_sample.json"
KAPPA = ROOT / "configs" / "evaluation" / "confidence_comparison_results.json"
CLUSTER = ROOT / "data" / "manifests" / "phase1_clustering_report.json"
STRUCT = ROOT / "configs" / "evaluation" / "structural_reliability_results.json"
AUDIT_MANIFEST = (
    ROOT
    / "outputs"
    / "framework_mapping"
    / "run_20260727_133838_post60_analytical_audit_E_final"
    / "AUDIT_E_MANIFEST.json"
)

DOCX = (
    ROOT
    / "outputs"
    / "dissertation_integration"
    / "run_20260729_153931_wave2_final_integrity_fixes"
    / "Lawal_Akeeb_Idowu_MSc_Dissertation_FINAL.docx"
)
PDF = (
    ROOT
    / "outputs"
    / "dissertation_integration"
    / "run_20260729_153931_wave2_final_integrity_fixes"
    / "Lawal_Akeeb_Idowu_MSc_Dissertation_FINAL.pdf"
)
DOCX_HASH = "a829ff6d0b4a778f2a276f9fff45af05dbc47fa268f3a9b0b131a87099b0a2e2"
PDF_HASH = "40c123b9743277d9083d3b66eb855e0fa7a57101017d08a7d8a2d94558a63519"
JOURNAL_HASH = "814cc7c47a9f75bfc0a6c7b693feec7073e59131398d89fab7c9111fbb2e5e06"

DEMO_HASH = {
    "phase1-016": "e5d28326427f4108ed97922bf444a4467ce807e4aa198277e2ba46d6cd3a2953",
    "phase1-082": "9b131dc2b403f51a3a1de366ee56793c6ff255986a57e683d525297963cca2c0",
    "phase1-090": "7e94f16177c4ce820f956d64d27dfd9a1798e91627cb7e372ac43b0ba25ed430",
    "phase1-246": "30e2cf20540de86b618cc3790b006148fb50905e3c51b35c404dab88099440ee",
}

DECK_DIR = ROOT / "outputs" / "distinction_strategy" / "05_presentation_deck"
REQUIRED_DOCS = [
    "VIVA_DEFENCE_MAP.md",
    "VIVA_QUESTION_BANK.md",
    "VIVA_ANSWER_ANCHORS.md",
    "VIVA_EVIDENCE_INDEX.csv",
    "VIVA_LIMITATIONS_DEFENCE.md",
    "VIVA_METHODS_DEFENCE.md",
    "VIVA_TECHNICAL_DEFENCE.md",
    "VIVA_GOVERNANCE_AND_ETHICS.md",
    "VIVA_CONTRIBUTION_AND_NOVELTY.md",
    "VIVA_FAILURE_AND_RECOVERY.md",
    "VIVA_RAPID_REVIEW.md",
    "MOCK_VIVA_SCRIPT_01.md",
    "MOCK_VIVA_SCRIPT_02.md",
    "MOCK_VIVA_SCORING_RUBRIC.md",
    "REHEARSAL_LOG_TEMPLATE.csv",
]

HEADLINE_TOKENS = [
    "414",
    "351/414",
    "5/10/0",
    "1/6",
    "5/6",
    "21/50",
    "0.48",
    "0.39",
    "20",
    "11/60",
    "37/60",
    "26/60",
    "8/25/20/7",
    "50/53",
    "49/50",
]

SECRET_RE = re.compile(
    r"(?i)(openai_api_key\s*=\s*sk-|sk-(?:proj|live)-[A-Za-z0-9]{10,}|BEGIN (?:RSA |OPENSSH )?PRIVATE KEY)"
)
FORBIDDEN_CLAIM_RE = re.compile(
    r"(?i)("
    r"official\s+viva\s+(?:is|lasts|duration)|"
    r"byte[- ]identical\s+(?:llm\s+)?reproduc|"
    r"second\s+independent\s+reviewer\s+(?:existed|was\s+used|completed)|"
    r"multi[- ]model\s+generalis|"
    r"ready\s+for\s+(?:production\s+)?deployment|"
    r"automatically\s+verified\s+policy\s+catalogue|"
    r"supervisor\s+(?:was|acted\s+as)\s+(?:the\s+)?second\s+reviewer|"
    r"p\s*[<=>]\s*0\.\d+|confidence\s+interval\s+of\s+\d|"
    r"examiner\s+(?:said|wrote|scored|marked)\s+"
    r")"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def all_viva_text() -> str:
    parts = []
    for path in sorted(VIVA.glob("*")):
        if path.is_file() and path.suffix.lower() in {".md", ".csv", ".json", ".txt"}:
            parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    if PKG.exists():
        for path in sorted(PKG.rglob("*")):
            if path.is_file() and path.suffix.lower() in {".md", ".csv", ".json", ".txt"}:
                parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(parts)


def test_required_docs_exist() -> None:
    for name in REQUIRED_DOCS:
        assert (VIVA / name).is_file(), name


def test_question_bank_size_and_adversarial() -> None:
    rows = list(csv.DictReader((VIVA / "VIVA_QUESTION_BANK.csv").open(encoding="utf-8")))
    assert len(rows) >= 80
    assert sum(1 for r in rows if r["difficulty"] == "adversarial") >= 20
    cats = {r["category"] for r in rows}
    for needed in (
        "fundamentals",
        "methodology",
        "evaluation",
        "governance and ethics",
        "reproducibility",
        "limitations",
        "deployment",
        "presentation-specific",
        "statistics",
    ):
        assert needed in cats, needed


def test_mock_scripts_have_about_30_questions() -> None:
    for name in ("MOCK_VIVA_SCRIPT_01.md", "MOCK_VIVA_SCRIPT_02.md"):
        text = (VIVA / name).read_text(encoding="utf-8")
        qs = re.findall(r"^### Q\d+", text, flags=re.M)
        assert 28 <= len(qs) <= 35, (name, len(qs))
        assert "Training only" in text or "training only" in text.lower()


def test_evidence_index_covers_headline_numbers() -> None:
    rows = list(csv.DictReader((VIVA / "VIVA_EVIDENCE_INDEX.csv").open(encoding="utf-8")))
    blob = " ".join(r["answer_claim"] for r in rows)
    for token in HEADLINE_TOKENS:
        if token == "20":
            assert "20 cluster" in blob.lower() or "20 clusters" in blob.lower()
        else:
            assert token in blob, token
    cols = set(rows[0].keys())
    for col in (
        "topic",
        "question_id",
        "answer_claim",
        "dissertation_location",
        "authoritative_source",
        "source_key_or_row",
        "stable_id",
        "evidence_hash",
        "human_adjudicated",
        "limitation",
        "verification_status",
    ):
        assert col in cols


def test_headline_numbers_match_frozen_evidence() -> None:
    journal = json.loads(JOURNAL.read_text(encoding="utf-8"))
    assert journal["totals"]["decisions"] == 414
    assert journal["totals"]["traceability_pass"] == 351
    assert sha256(JOURNAL) == JOURNAL_HASH

    sample = json.loads(SAMPLE.read_text(encoding="utf-8"))
    items = sample["items"]
    no_high = sum(
        1
        for it in items
        if str(it.get("human_valid_decision", "")).lower() == "no"
        and str(it.get("human_confidence", "")).lower() == "high"
    )
    assert no_high == 21, no_high

    kappa = json.loads(KAPPA.read_text(encoding="utf-8"))
    metrics = kappa.get("metrics", kappa)
    assert round(metrics["rule_vs_human_b"]["weighted_kappa"], 2) == 0.48
    assert round(metrics["llm_vs_human_b"]["weighted_kappa"], 2) == 0.39

    cluster = json.loads(CLUSTER.read_text(encoding="utf-8"))
    assert cluster["n_clusters"] == 20

    struct = json.loads(STRUCT.read_text(encoding="utf-8"))
    assert struct["summary"]["structural_pass_count"] == 49

    faith = json.loads(AUDIT_MANIFEST.read_text(encoding="utf-8"))
    counts = faith["traceability_category_counts"]
    assert counts["exact_or_near_verbatim"] == 8
    assert counts["substantively_faithful_paraphrase"] == 25
    assert counts["materially_unsupported_or_altered"] == 20
    assert counts["traceability_false"] == 7


def test_demo_case_classifications() -> None:
    for sid, expected_hash in DEMO_HASH.items():
        path = ROOT / "demo" / "evidence" / f"{sid}.json"
        assert path.is_file()
        assert sha256(path) == expected_hash
        data = json.loads(path.read_text(encoding="utf-8"))
        if sid == "phase1-082":
            assert str(data.get("rubric_a", "")).lower() == "no"
            assert str(data.get("rubric_b", "")).lower() == "high"
        if sid == "phase1-090":
            blob = json.dumps(data).lower()
            assert "materially_unsupported" in blob or "altered" in blob
        if sid == "phase1-016":
            assert str(data.get("rubric_a", "")).lower() == "yes"
            assert str(data.get("rubric_b", "")).lower() == "high"
        if sid == "phase1-246":
            blob = json.dumps(data).lower()
            assert "p3" in blob or "jee" in blob


def test_no_forbidden_overclaims_or_secrets() -> None:
    text = all_viva_text()
    assert SECRET_RE.search(text) is None
    assert "official viva lasts" not in text.lower()
    assert "official viva is forty" not in text.lower()
    assert "confidence interval of" not in text.lower()
    assert "byte-identical llm reproducibility is expected" not in text.lower()
    assert "second independent reviewer existed" not in text.lower()
    assert "supervisor was the second reviewer" not in text.lower()
    assert "ready for production deployment" not in text.lower()
    low = text.lower()
    assert "automatically verified policy catalogue" in low or "verified policy catalogue" in low
    assert "not" in low


def test_package_manifest_and_sums() -> None:
    assert (PKG / "PACKAGE_MANIFEST.json").is_file()
    assert (PKG / "SHA256SUMS").is_file()
    assert (PKG / "candidate_pack" / "VIVA_RAPID_REVIEW.md").is_file()
    assert (PKG / "examiner_style_questions" / "VIVA_QUESTION_BANK.md").is_file()
    assert (PKG / "rehearsal" / "REHEARSAL_LOG_TEMPLATE.csv").is_file()
    assert (PKG / "validation" / "NUMBER_LOCK.json").is_file()
    # SHA256SUMS lines verify
    for line in (PKG / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, rel = line.split(None, 1)
        path = PKG / rel.strip()
        assert path.is_file(), rel
        assert sha256(path) == digest


def test_protected_dissertation_and_deck_hashes_unchanged() -> None:
    assert sha256(DOCX) == DOCX_HASH
    assert sha256(PDF) == PDF_HASH
    assert sha256(JOURNAL) == JOURNAL_HASH
    for sid, expected in DEMO_HASH.items():
        assert sha256(ROOT / "demo" / "evidence" / f"{sid}.json") == expected
    # presentation decks unchanged vs Wave 5B SHA256SUMS if present
    sums = DECK_DIR / "SHA256SUMS"
    if sums.is_file():
        for line in sums.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            digest, rel = line.split(None, 1)
            path = DECK_DIR / rel.strip()
            if path.is_file() and path.suffix.lower() in {".pptx", ".pdf"}:
                assert sha256(path) == digest, rel


def test_evidence_paths_exist_or_marked_hash_only() -> None:
    rows = list(csv.DictReader((VIVA / "VIVA_EVIDENCE_INDEX.csv").open(encoding="utf-8")))
    for row in rows:
        src = row["authoritative_source"].strip()
        eh = row["evidence_hash"].strip().lower()
        if eh.startswith("hash_only") or eh.startswith("see_") or src.endswith("/"):
            continue
        path = ROOT / src
        if not path.exists():
            # allow docs that exist
            assert "hash_only" in eh or "n/a" in eh or path.parent.exists(), src


def test_rehearsal_plan_and_rubric_thresholds() -> None:
    rubric = (VIVA / "MOCK_VIVA_SCORING_RUBRIC.md").read_text(encoding="utf-8")
    assert "Distinction-ready" in rubric
    assert "Acceptable but vulnerable" in rubric
    assert "High-risk response pattern" in rubric
    plan = VIVA / "PRESENTATION_REHEARSAL_PLAN.md"
    assert plan.is_file()
    text = plan.read_text(encoding="utf-8")
    assert "Never omit" in text
    assert "phase1-082" in text


def test_rapid_review_readable_markers() -> None:
    text = (VIVA / "VIVA_RAPID_REVIEW.md").read_text(encoding="utf-8")
    assert "phase1-082" in text
    assert "python demo/launch_demo.py" in text
    for token in ("414", "351/414", "21/50", "0.48", "0.39", "8/25/20/7"):
        assert token in text
