#!/usr/bin/env python3
"""Wave 4 offline smoke test — localhost only, no external network required."""
from __future__ import annotations

import functools
import http.server
import json
import re
import socket
import socketserver
import threading
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo"
EXTERNAL_ASSET_RE = re.compile(r"""(?i)(?:src|href)\s*=\s*["']https?://""")
SECRET_RE = re.compile(r"(?i)(openai_api_key\s*=\s*sk-|sk-(?:proj|live)-)")


def fetch(base: str, path: str) -> tuple[int, bytes]:
    with urllib.request.urlopen(base + path, timeout=5) as resp:
        return resp.status, resp.read()


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DEMO))

    class _Server(socketserver.TCPServer):
        allow_reuse_address = True

    httpd = _Server(("127.0.0.1", port), handler)
    assert httpd.server_address[0] == "127.0.0.1"
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{port}"
    print(f"BIND=127.0.0.1 PORT={port} URL={base}/index.html")

    report: dict = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "bind": "127.0.0.1",
        "port": port,
        "checks": {},
    }

    try:
        status, body = fetch(base, "/index.html")
        text = body.decode("utf-8")
        assert status == 200
        assert "AI-assisted decision journaling" in text
        assert "Frozen research artefact — no live model call" in text
        assert EXTERNAL_ASSET_RE.search(text) is None
        assert "case-082" in text
        assert "centrepiece" in text.lower() or "featured" in text
        report["checks"]["index_landing"] = "pass"
        report["checks"]["freeze_notice"] = "pass"
        report["checks"]["no_external_assets_index"] = "pass"
        report["checks"]["centrepiece_marked"] = "pass"

        status, body = fetch(base, "/print.html")
        ptext = body.decode("utf-8")
        assert status == 200
        assert "phase1-082" in ptext
        assert "Frozen research artefact" in ptext
        report["checks"]["print_html"] = "pass"

        for asset in ("/demo.css", "/demo.js", "/evidence_embed.js", "/DEMO_EVIDENCE_MANIFEST.json"):
            status, body = fetch(base, asset)
            assert status == 200
            text_asset = body.decode("utf-8", errors="ignore")
            assert EXTERNAL_ASSET_RE.search(text_asset) is None
            assert SECRET_RE.search(text_asset) is None

        cases = {}
        for jid, expect in {
            "016": {"rubric_a": "yes", "rubric_b": "high"},
            "082": {"rubric_a": "no", "rubric_b": "high"},
            "090": {"faithfulness_category": "materially_unsupported_or_altered"},
            "246": {"jee_primary": "P3", "dq_primary": "commitment_to_follow_through"},
        }.items():
            status, body = fetch(base, f"/evidence/phase1-{jid}.json")
            assert status == 200
            data = json.loads(body.decode("utf-8"))
            for key, val in expect.items():
                assert data.get(key) == val, (jid, key, data.get(key), val)
            cases[f"phase1-{jid}"] = {
                "status": status,
                "rubric_a": data.get("rubric_a"),
                "rubric_b": data.get("rubric_b"),
                "faithfulness_category": data.get("faithfulness_category"),
                "jee_primary": data.get("jee_primary"),
                "dq_primary": data.get("dq_primary"),
            }
        report["checks"]["cases"] = cases
        report["checks"]["cases_all"] = "pass"

        # Simulate file:// fallback: embed present and contains all four IDs
        embed = (DEMO / "evidence_embed.js").read_text(encoding="utf-8")
        for jid in ("016", "082", "090", "246"):
            assert f"phase1-{jid}" in embed
        report["checks"]["file_fallback_embed"] = "pass"

        # Launcher source bind check
        launch = (DEMO / "launch_demo.py").read_text(encoding="utf-8")
        assert 'TCPServer(("127.0.0.1"' in launch
        assert re.search(r'TCPServer\(\s*\(\s*["\']0\.0\.0\.0["\']', launch) is None
        report["checks"]["launcher_localhost_only"] = "pass"

        report["result"] = "SMOKE_PASS"
        print("SMOKE_PASS")
    finally:
        httpd.shutdown()
        httpd.server_close()

    out_dir = ROOT / "outputs" / "distinction_strategy" / "04_offline_demo" / "validation"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "OFFLINE_SMOKE_TEST.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_dir / 'OFFLINE_SMOKE_TEST.json'}")


if __name__ == "__main__":
    main()
