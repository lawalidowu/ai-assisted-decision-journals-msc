"""Wave 5A presentation storyboard validation (read-only checks)."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRES = ROOT / "docs" / "presentation"
STORY = PRES / "PRESENTATION_STORYBOARD.md"
MAP = PRES / "SLIDE_EVIDENCE_MAP.csv"
NOTES = PRES / "PRESENTATION_SPEAKER_NOTES.md"
VIS = PRES / "VISUAL_ASSET_PLAN.md"
VIVA = PRES / "PRESENTATION_VIVA_ALIGNMENT.md"
REPORT = ROOT / "docs" / "revision_control" / "WAVE_5A_PRESENTATION_STORYBOARD_REPORT.md"

DEMO_IDS = ["phase1-016", "phase1-082", "phase1-090", "phase1-246"]
DEMO_HASH = {
    "phase1-016": "e5d28326427f4108ed97922bf444a4467ce807e4aa198277e2ba46d6cd3a2953",
    "phase1-082": "9b131dc2b403f51a3a1de366ee56793c6ff255986a57e683d525297963cca2c0",
    "phase1-090": "7e94f16177c4ce820f956d64d27dfd9a1798e91627cb7e372ac43b0ba25ed430",
    "phase1-246": "30e2cf20540de86b618cc3790b006148fb50905e3c51b35c404dab88099440ee",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_storyboard_package_exists() -> None:
    for path in (STORY, MAP, NOTES, VIS, VIVA, REPORT):
        assert path.is_file(), path


def test_official_duration_documented_from_handbook() -> None:
    text = STORY.read_text(encoding="utf-8")
    assert "ProjectHandbook2025-26.pdf" in text
    assert "no longer than 20" in text or "no more than 12" in text
    assert "15–20" in text or "15-20" in text
    # Planning assumptions must be labelled — 15-minute must not be asserted alone as sole official duration
    assert "planning" in text.lower()
    assert "Preferred working target" in text or "preferred working target" in text.lower()


def test_ten_and_fifteen_models_present() -> None:
    text = STORY.read_text(encoding="utf-8")
    assert "15-minute" in text and "10-minute" in text
    assert "Optional / removed for 10-minute" in text or "Removed for 10-minute" in text or "removed for 10-minute" in text.lower()
    assert "S05" in text and "S08" in text and "S11" in text


def test_slide_count_within_official_max() -> None:
    text = STORY.read_text(encoding="utf-8")
    assert "≤12" in text or "no more than 12" in text
    # S01..S12 present
    for i in range(1, 13):
        assert f"S{i:02d}" in text or f"### S{i:02d}" in text or f"S{i:02d} —" in text


def test_central_claim_and_question() -> None:
    text = STORY.read_text(encoding="utf-8")
    assert "not an automatically verified policy catalogue" in text.lower() or "not an automatically verified policy catalogue" in text
    assert "governed" in text.lower()
    assert "without treating generated text as authoritative" in text.lower()
    assert "phase1-082" in text


def test_no_deployed_or_verified_decision_claims() -> None:
    story = STORY.read_text(encoding="utf-8")
    notes = NOTES.read_text(encoding="utf-8")
    assert "not deployed" in story.lower() or "Not live / not deployed" in story
    assert "Do not say the system is deployed" in notes or "not deployed" in notes.lower()
    assert "verified decisions" in notes.lower()  # appears in avoid list
    assert "automatically authoritative" in (story + notes).lower()


def test_numbers_match_frozen_evidence() -> None:
    journal = json.loads((ROOT / "data/manifests/phase1_decision_journal.json").read_text(encoding="utf-8"))
    assert journal["totals"]["decisions"] == 414
    assert journal["totals"]["traceability_pass"] == 351

    metrics = json.loads(
        (ROOT / "configs/evaluation/confidence_comparison_results.json").read_text(encoding="utf-8")
    )["metrics"]
    assert round(metrics["rule_vs_human_b"]["weighted_kappa"], 2) == 0.48
    assert round(metrics["llm_vs_human_b"]["weighted_kappa"], 2) == 0.39

    clusters = json.loads((ROOT / "data/manifests/phase1_clustering_report.json").read_text(encoding="utf-8"))
    assert clusters["n_clusters"] == 20

    sample = json.loads((ROOT / "configs/evaluation/confidence_validation_sample.json").read_text(encoding="utf-8"))
    items = sample["items"]
    no_high = sum(
        1
        for it in items
        if str(it.get("human_valid_decision", "")).lower() == "no"
        and str(it.get("human_confidence", "")).lower() == "high"
    )
    assert no_high == 21

    struct = json.loads(
        (ROOT / "configs/evaluation/structural_reliability_results.json").read_text(encoding="utf-8")
    )
    assert struct["summary"]["structural_pass_count"] == 49
    assert struct["summary"]["total_outputs"] == 50

    man = json.loads(
        (
            ROOT
            / "outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/AUDIT_E_MANIFEST.json"
        ).read_text(encoding="utf-8")
    )
    counts = man["traceability_category_counts"]
    assert counts["exact_or_near_verbatim"] == 8
    assert counts["substantively_faithful_paraphrase"] == 25
    assert counts["materially_unsupported_or_altered"] == 20
    assert counts["traceability_false"] == 7

    story = STORY.read_text(encoding="utf-8")
    for token in (
        "414",
        "351/414",
        "21/50",
        "0.48",
        "0.39",
        "11/60",
        "37/60",
        "26/60",
        "8/25/20/7",
        "50/53",
        "49/50",
        "1/6",
        "5/6",
    ):
        assert token in story
    assert "20" in story and "cluster" in story.lower()
    assert "5 agreement" in story or "5 / 10 / 0" in story or "5 agreement / 10 silence" in story

def test_evidence_map_covers_empirical_slides() -> None:
    with MAP.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows
    ids = {r["slide_id"] for r in rows}
    for need in ("S06a", "S06e", "S06f", "S07", "S08a", "S08b", "S08c"):
        assert need in ids
    for r in rows:
        if r["slide_id"].startswith("S06") or r["slide_id"] in {"S07", "S08a", "S08b", "S08c"}:
            assert r["authoritative_source"].strip()
            assert r["verification_status"].startswith("verified")


def test_wave4_demo_cases_unchanged() -> None:
    for jid, digest in DEMO_HASH.items():
        path = ROOT / "demo" / "evidence" / f"{jid}.json"
        assert sha256(path) == digest


def test_protected_artefact_hashes_unchanged() -> None:
    assert (
        sha256(ROOT / "data/manifests/phase1_decision_journal.json")
        == "814cc7c47a9f75bfc0a6c7b693feec7073e59131398d89fab7c9111fbb2e5e06"
    )
    wave2 = ROOT / "outputs/dissertation_integration/run_20260729_153931_wave2_final_integrity_fixes"
    assert (
        sha256(wave2 / "Lawal_Akeeb_Idowu_MSc_Dissertation_FINAL.docx")
        == "a829ff6d0b4a778f2a276f9fff45af05dbc47fa268f3a9b0b131a87099b0a2e2"
    )
    assert (
        sha256(wave2 / "Lawal_Akeeb_Idowu_MSc_Dissertation_FINAL.pdf")
        == "40c123b9743277d9083d3b66eb855e0fa7a57101017d08a7d8a2d94558a63519"
    )


def test_aim_not_rewritten_stronger() -> None:
    aim = (
        "To design and evaluate an LLM-assisted method for creating traceable "
        "candidate decision-journal entries from complex public records, using "
        "UK COVID-19 Inquiry Module 2 transcripts as a case study."
    )
    story = STORY.read_text(encoding="utf-8")
    assert "traceable candidate" in story.lower()
    ch1 = (ROOT / "dissertation/CHAPTER_1_INTRODUCTION.md").read_text(encoding="utf-8")
    assert aim in ch1
    # storyboard should reference exact aim file rather than invent RQs
    assert "No numbered RQs" in story or "no numbered RQs" in story.lower()


def test_demo_allocation_cap() -> None:
    text = STORY.read_text(encoding="utf-8") + NOTES.read_text(encoding="utf-8")
    assert re.search(r"≤\s*2|<=\s*2|no more than about 2|≤2", text)
    assert "complete without" in text.lower() or "complete without live demo" in text.lower()
