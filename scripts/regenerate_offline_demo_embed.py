#!/usr/bin/env python3
"""Regenerate demo/evidence_embed.js and demo/print.html from frozen evidence JSON."""
from __future__ import annotations

import html
import json
from pathlib import Path

DEMO = Path(__file__).resolve().parents[1] / "demo"
IDS = ["016", "082", "090", "246"]
TITLES = {
    "016": "Strong Yes × High — alignment",
    "082": "No × High — wrong-artefact (centrepiece)",
    "090": "Materially unsupported or altered",
    "246": "JEE P3 + Decision Quality interpretation",
}


def main() -> None:
    bag = {}
    for i in IDS:
        path = DEMO / "evidence" / f"phase1-{i}.json"
        bag[f"phase1-{i}"] = json.loads(path.read_text(encoding="utf-8"))
    man = json.loads((DEMO / "DEMO_EVIDENCE_MANIFEST.json").read_text(encoding="utf-8"))
    embed = (
        "/* Generated from demo/evidence/*.json and DEMO_EVIDENCE_MANIFEST.json — do not edit by hand. */\n"
        f"window.__DEMO_EVIDENCE = {json.dumps(bag, indent=2, ensure_ascii=False)};\n"
        f"window.__DEMO_MANIFEST = {json.dumps(man, indent=2, ensure_ascii=False)};\n"
    )
    (DEMO / "evidence_embed.js").write_text(embed, encoding="utf-8")

    parts = []
    for i in IDS:
        d = bag[f"phase1-{i}"]
        flags = ", ".join(d.get("review_flags") or []) or "none"
        parts.append(
            f"""
<section class="case">
  <h2>phase1-{i} — {html.escape(TITLES[i])}</h2>
  <p><strong>Hearing date:</strong> {html.escape(str(d.get("hearing_date", "")))}</p>
  <p><strong>Candidate decision:</strong> {html.escape(str(d.get("decision", "")))}</p>
  <p><strong>Source quotation:</strong> {html.escape(str(d.get("source_quote", "")))}</p>
  <p><strong>traceability_ok:</strong> {html.escape(str(d.get("traceability_ok")))}

     · flags: {html.escape(flags)}</p>
  <p><strong>Rubric A:</strong> {html.escape(str(d.get("rubric_a", "—")).upper())}

     · <strong>Rubric B:</strong> {html.escape(str(d.get("rubric_b", "—")).upper())}

     · <strong>Faithfulness:</strong> {html.escape(str(d.get("faithfulness_category", "—")))}

     · <strong>JEE:</strong> {html.escape(str(d.get("jee_primary", "—")))}

     · <strong>DQ:</strong> {html.escape(str(d.get("dq_primary", "—")))}</p>
  <p class="path">evidence/phase1-{i}.json</p>
</section>"""
        )
    hashes = "".join(
        f"<li><code>{html.escape(k)}</code> — {html.escape(v['sha256'])}</li>"
        for k, v in man["files"].items()
    )
    doc = f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
  <meta charset="utf-8">
  <title>Printable offline demo — AI-assisted decision journaling</title>
  <style>
    body {{ font-family: Georgia, "Times New Roman", serif; margin: 1.5rem; color: #182028; line-height: 1.4; }}
    h1 {{ font-size: 1.6rem; }}
    .banner {{ border: 1px solid #b9a46a; background: #fff6d8; padding: 0.6rem 0.8rem; font-weight: 650; }}
    .case {{ border-top: 1px solid #c9c2b4; padding: 1rem 0; page-break-inside: avoid; }}
    .path {{ color: #4a5560; font-size: 0.85rem; }}
    @media print {{ .noprint {{ display: none; }} }}
  </style>
</head>
<body>
  <p class="banner">Frozen research artefact — no live model call</p>
  <h1>AI-assisted decision journaling from public inquiry transcripts</h1>
  <p>An LLM can quote a source accurately while still extracting the wrong kind of artefact for a decision journal.</p>
  <p class="noprint">Print or Save as PDF from the browser. Prefer the interactive demo via <code>python demo/launch_demo.py</code>.</p>
  {"".join(parts)}
  <h2>Evidence SHA-256</h2>
  <ul>{hashes}</ul>
</body>
</html>
"""
    (DEMO / "print.html").write_text(doc, encoding="utf-8")
    print(f"Wrote {DEMO / 'evidence_embed.js'} and {DEMO / 'print.html'}")


if __name__ == "__main__":
    main()
