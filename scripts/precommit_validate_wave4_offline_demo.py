#!/usr/bin/env python3
"""Pre-commit validation for Wave 4 offline demo staging."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXT = re.compile(r"""(?i)(?:src|href)\s*=\s*["']https?://""")
SEC = re.compile(r"(?i)(openai_api_key\s*=\s*sk-|sk-(?:proj|live)-|BEGIN (?:RSA |OPENSSH )?PRIVATE KEY)")
UKHSA = re.compile(r"(?i)ukhsa.*(confidential|restricted)|personal correspondence")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    files = subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True, cwd=ROOT).splitlines()
    print("STAGED_COUNT", len(files))
    sizes = []
    for f in files:
        p = ROOT / f
        sz = p.stat().st_size if p.is_file() else 0
        sizes.append((sz, f))
    sizes.sort(reverse=True)
    print("LARGEST", sizes[0][0], sizes[0][1])
    print("PACKAGE_FILE_SIZES:")
    for sz, f in sizes:
        if f.startswith("outputs/distinction_strategy/04_offline_demo/"):
            print(f"  {sz:8d}  {f}")
    assert all(sz < 50 * 1024 * 1024 for sz, _ in sizes)

    issues = []
    for f in files:
        p = ROOT / f
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".html", ".css", ".js", ".md", ".json", ".py", ".txt"}:
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        if SEC.search(text):
            issues.append(("secret", f))
        if UKHSA.search(text):
            issues.append(("ukhsa", f))
        if p.suffix.lower() in {".html", ".css", ".js"} and EXT.search(text):
            issues.append(("cdn", f))

    launch = (ROOT / "demo" / "launch_demo.py").read_text(encoding="utf-8")
    assert 'TCPServer(("127.0.0.1"' in launch
    assert re.search(r'TCPServer\(\s*\(\s*["\']0\.0\.0\.0["\']', launch) is None

    man = json.loads((ROOT / "demo" / "DEMO_EVIDENCE_MANIFEST.json").read_text(encoding="utf-8"))
    for name, meta in man["files"].items():
        path = ROOT / "demo" / meta["path"]
        assert sha256(path) == meta["sha256"], name
        w3 = ROOT / "outputs/distinction_strategy/03_reproducibility_package/demos" / name
        assert path.read_bytes() == w3.read_bytes(), name

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

    for f in files:
        assert not f.startswith("dissertation/")
        assert "phase1_decision_journal" not in f

    pkg = ROOT / "outputs/distinction_strategy/04_offline_demo"
    for line in (pkg / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, rel = line.split("  ", 1)
        assert sha256(pkg / rel) == digest, rel

    html = (ROOT / "demo" / "index.html").read_text(encoding="utf-8")
    assert 'href="demo.css"' in html and 'src="demo.js"' in html and 'src="evidence_embed.js"' in html
    assert "http://" not in html and "https://" not in html

    print("SCAN_ISSUES", issues or "none")
    print("GITIGNORE_EXCEPTION: !outputs/distinction_strategy/04_offline_demo/")
    assert not issues
    print("PRECOMMIT_STATIC_PASS")


if __name__ == "__main__":
    main()
