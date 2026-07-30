"""Wave 4 offline examiner demo validation (no network dependencies beyond localhost)."""
from __future__ import annotations

import hashlib
import json
import re
import socket
import socketserver
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from urllib.request import urlopen

import pytest

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo"
EVIDENCE = DEMO / "evidence"
W3_DEMOS = ROOT / "outputs/distinction_strategy/03_reproducibility_package/demos"
MANIFEST = DEMO / "DEMO_EVIDENCE_MANIFEST.json"

IDS = ["phase1-016", "phase1-082", "phase1-090", "phase1-246"]
SECRET_RE = re.compile(r"(?i)(openai_api_key\s*=\s*sk-|sk-(?:proj|live)-[A-Za-z0-9]{10,}|https?://cdn\.|fonts\.googleapis|jsdelivr|unpkg)")
EXTERNAL_ASSET_RE = re.compile(
    r"""(?i)(?:src|href)\s*=\s*["']https?://"""
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def test_evidence_files_exist_with_exact_ids() -> None:
    for jid in IDS:
        path = EVIDENCE / f"{jid}.json"
        assert path.is_file()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["journal_id"] == jid


def test_evidence_matches_wave3_package_bytes() -> None:
    for jid in IDS:
        a = (EVIDENCE / f"{jid}.json").read_bytes()
        b = (W3_DEMOS / f"{jid}.json").read_bytes()
        assert a == b


def test_evidence_hashes_match_manifest() -> None:
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for name, meta in man["files"].items():
        path = DEMO / meta["path"]
        assert path.is_file()
        assert sha256(path) == meta["sha256"]
        assert meta["journal_id"] in IDS


def test_review_classifications() -> None:
    d016 = json.loads((EVIDENCE / "phase1-016.json").read_text(encoding="utf-8"))
    d082 = json.loads((EVIDENCE / "phase1-082.json").read_text(encoding="utf-8"))
    d090 = json.loads((EVIDENCE / "phase1-090.json").read_text(encoding="utf-8"))
    d246 = json.loads((EVIDENCE / "phase1-246.json").read_text(encoding="utf-8"))
    assert d016["rubric_a"] == "yes" and d016["rubric_b"] == "high" and d016["traceability_ok"] is True
    assert d082["rubric_a"] == "no" and d082["rubric_b"] == "high" and "procedural" in d082["review_flags"]
    assert d090["faithfulness_category"] == "materially_unsupported_or_altered"
    assert d246["jee_primary"] == "P3"
    assert d246["dq_primary"] == "commitment_to_follow_through"


def test_no_secrets_or_external_assets_in_demo() -> None:
    for path in DEMO.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".html", ".css", ".js", ".md", ".json", ".py"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        assert not SECRET_RE.search(text), path
        if path.suffix.lower() in {".html", ".css", ".js"}:
            assert not EXTERNAL_ASSET_RE.search(text), path


def test_no_full_transcript_or_pdf_in_demo() -> None:
    for path in DEMO.rglob("*"):
        if path.suffix.lower() in {".pdf", ".txt"} and "evidence" in path.parts:
            pytest.fail(f"unexpected bulk file {path}")
        if path.suffix == ".json" and path.parent == EVIDENCE:
            data = json.loads(path.read_text(encoding="utf-8"))
            assert "full_transcript" not in data
            assert len(data.get("source_quote", "")) < 2000


def test_evidence_embed_matches_json_files() -> None:
    embed_src = (DEMO / "evidence_embed.js").read_text(encoding="utf-8")
    m_ev = re.search(
        r"window\.__DEMO_EVIDENCE\s*=\s*(\{.*?\});\s*window\.__DEMO_MANIFEST\s*=\s*(\{.*?\});",
        embed_src,
        flags=re.S,
    )
    assert m_ev, "evidence_embed.js must define __DEMO_EVIDENCE and __DEMO_MANIFEST"
    bag = json.loads(m_ev.group(1))
    emb_man = json.loads(m_ev.group(2))
    for jid in IDS:
        file_data = json.loads((EVIDENCE / f"{jid}.json").read_text(encoding="utf-8"))
        assert bag[jid] == file_data
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert emb_man == man


def test_candidate_and_quote_match_wave3_authoritative_fields() -> None:
    d016 = json.loads((EVIDENCE / "phase1-016.json").read_text(encoding="utf-8"))
    assert d016["decision"] == "COBR decided to close schools from the 20th of March."
    assert d016["source_quote"] == (
        "On the 18th, COBR decided to close schools from the 20th, just in very general terms."
    )
    for jid in IDS:
        data = json.loads((EVIDENCE / f"{jid}.json").read_text(encoding="utf-8"))
        assert data["decision"].strip()
        assert data["source_quote"].strip()
        w3 = json.loads((W3_DEMOS / f"{jid}.json").read_text(encoding="utf-8"))
        assert data["decision"] == w3["decision"]
        assert data["source_quote"] == w3["source_quote"]
        for key in ("rubric_a", "rubric_b", "faithfulness_category", "jee_primary", "dq_primary"):
            if key in w3:
                assert data.get(key) == w3.get(key)


def test_print_html_and_walkthrough_exist() -> None:
    assert (DEMO / "print.html").is_file()
    assert (DEMO / "DEMO_WALKTHROUGH.md").is_file()
    assert (DEMO / "DEMO_FAILURE_RECOVERY.md").is_file()
    assert (DEMO / "DEMO_RUNBOOK.md").is_file()
    walk = (DEMO / "DEMO_WALKTHROUGH.md").read_text(encoding="utf-8")
    assert "phase1-082" in walk
    assert "governed workflow" in walk.lower() or "visibly separate" in walk.lower()


def test_index_references_local_assets_only() -> None:
    html = (DEMO / "index.html").read_text(encoding="utf-8")
    assert 'href="demo.css"' in html
    assert 'src="demo.js"' in html
    assert 'src="evidence_embed.js"' in html
    assert "Frozen research artefact" in html
    assert "http://" not in html and "https://" not in html
    assert (DEMO / "demo.css").is_file()
    assert (DEMO / "demo.js").is_file()

def test_launcher_required_files_and_localhost_bind_logic() -> None:
    # Import-free parse: inspect launch_demo.py for localhost binding
    src = (DEMO / "launch_demo.py").read_text(encoding="utf-8")
    assert 'TCPServer(("127.0.0.1"' in src
    assert re.search(r'bind\(\s*\(\s*["\']0\.0\.0\.0["\']', src) is None
    assert re.search(r'TCPServer\(\s*\(\s*["\']0\.0\.0\.0["\']', src) is None


def test_demo_http_server_serves_index() -> None:
    # Bind ephemeral localhost port and request index.html
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    handler = partial(SimpleHTTPRequestHandler, directory=str(DEMO))

    class _Server(socketserver.TCPServer):
        allow_reuse_address = True

    httpd = _Server(("127.0.0.1", port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        with urlopen(f"http://127.0.0.1:{port}/index.html", timeout=3) as resp:
            assert resp.status == 200
            body = resp.read()
            assert b"AI-assisted decision journaling" in body
            assert b"no live model call" in body.lower() or b"Frozen research artefact" in body
        with urlopen(f"http://127.0.0.1:{port}/evidence/phase1-082.json", timeout=3) as resp:
            assert resp.status == 200
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_analytical_and_wave2_hashes_unchanged() -> None:
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from active_formal_submission import active_docx, active_docx_sha256, active_pdf, active_pdf_sha256

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
    assert sha256(active_docx()) == active_docx_sha256() == "70df0ee0992cd55635053f00926923d1b39357312f820fe29883810a0d9e96b5"
    assert sha256(active_pdf()) == active_pdf_sha256() == "fa685483df8e19972d798dffd58801fbb14b48f1928e62af12153b971406c0b5"
