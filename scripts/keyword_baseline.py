"""Keyword-based decision baseline vs manual labels and LLM on annotated excerpts."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = ROOT / "configs/annotations/manual_phase1.json"
OUT_MD = ROOT / "docs/BASELINE_KEYWORD.md"

# Simple patterns for formal decision language in inquiry text
PATTERNS = [
    re.compile(r"\bCOBR\s+decided\b", re.I),
    re.compile(r"\b(?:was|were)\s+decided\b", re.I),
    re.compile(r"\bdecided\s+to\b", re.I),
    re.compile(r"\bagreed\s+(?:to|that)\b", re.I),
    re.compile(r"\bannounced\b", re.I),
    re.compile(r"\bcommissioned\b", re.I),
    re.compile(r"\bordained\b", re.I),
    re.compile(r"\bdirected\b", re.I),
    re.compile(r"\bconfirmed\b", re.I),
    re.compile(r"\bthe\s+decision\b", re.I),
]


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text.strip())
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def extract_keyword_candidates(text: str) -> list[dict]:
    hits: list[dict] = []
    seen: set[str] = set()
    for sent in split_sentences(text):
        for pat in PATTERNS:
            if pat.search(sent):
                key = sent[:80].lower()
                if key not in seen:
                    seen.add(key)
                    hits.append({"sentence": sent, "pattern": pat.pattern})
                break
    return hits


def overlaps(a: str, b: str, min_len: int = 25) -> bool:
    a, b = a.lower(), b.lower()
    if not a or not b:
        return False
    if a in b or b in a:
        return True
    # shared substring
    for i in range(len(a) - min_len):
        sub = a[i : i + min_len]
        if sub in b:
            return True
    return False


def main() -> None:
    data = json.loads(WORKBOOK.read_text(encoding="utf-8"))
    excerpts = data["excerpts"]

    rows = []
    manual_total = 0
    manual_matched_kw = 0
    manual_matched_llm = 0
    kw_candidates_total = 0
    kw_tp = 0

    for ex in excerpts:
        eid = ex["excerpt_id"]
        text = ex.get("excerpt_text", "")
        manual = ex.get("manual_decisions", [])
        candidates = extract_keyword_candidates(text)

        # LLM items linked to this excerpt (comparisons + seeds)
        llm_ids = set()
        for c in ex.get("comparisons", []):
            if c.get("llm_item_id"):
                llm_ids.add(c["llm_item_id"])
        for s in ex.get("seed_llm_items", []):
            llm_ids.add(s["llm_item_id"])

        llm_agree = sum(
            1 for c in ex.get("comparisons", []) if c.get("triangulation") == "agreement"
        )

        manual_total += len(manual)
        manual_matched_llm += llm_agree

        ex_kw_match = 0
        for m in manual:
            quote = m.get("source_quote", "")
            dec = m.get("decision", "")
            if any(overlaps(c["sentence"], quote) or overlaps(c["sentence"], dec) for c in candidates):
                ex_kw_match += 1
        manual_matched_kw += ex_kw_match

        # keyword precision: candidate matches any manual decision in excerpt
        ex_tp = 0
        for c in candidates:
            if any(
                overlaps(c["sentence"], m.get("source_quote", ""))
                or overlaps(c["sentence"], m.get("decision", ""))
                for m in manual
            ):
                ex_tp += 1
        kw_candidates_total += len(candidates)
        kw_tp += ex_tp

        rows.append(
            {
                "excerpt": eid,
                "manual": len(manual),
                "llm_agreement": llm_agree,
                "kw_candidates": len(candidates),
                "kw_recall_manual": f"{ex_kw_match}/{len(manual)}" if manual else "—",
            }
        )

    kw_recall = manual_matched_kw / manual_total if manual_total else 0
    llm_recall = manual_matched_llm / manual_total if manual_total else 0
    kw_precision = kw_tp / kw_candidates_total if kw_candidates_total else 0

    lines = [
        "# Keyword baseline vs manual labels (annotated excerpts)",
        "",
        "Simple pattern matcher on decision language (`decided`, `agreed`, `COBR decided`,",
        "`commissioned`, etc.) applied to the **6 annotated excerpt texts**.",
        "",
        "## Per-excerpt",
        "",
        "| Excerpt | Manual decisions | LLM agreement rows | Keyword candidates | KW recall (manual) |",
        "|---------|------------------|--------------------|--------------------|---------------------|",
    ]
    for r in rows:
        lines.append(
            f"| {r['excerpt']} | {r['manual']} | {r['llm_agreement']} | {r['kw_candidates']} | {r['kw_recall_manual']} |"
        )

    lines.extend(
        [
            "",
            "## Aggregate (6 manual decisions across 6 excerpts)",
            "",
            f"| Metric | Keyword baseline | LLM (`--inquiry`, agreement rows) |",
            f"|--------|------------------|----------------------------------|",
            f"| Recall vs manual | **{manual_matched_kw}/{manual_total} ({100*kw_recall:.0f}%)** | **{manual_matched_llm}/{manual_total} ({100*llm_recall:.0f}%)** |",
            f"| Candidate precision* | {kw_tp}/{kw_candidates_total} ({100*kw_precision:.0f}%) | — |",
            "",
            "\\*Precision = keyword candidates that align with a manual decision in the same excerpt.",
            "Keyword baseline produces many spurious hits on non-decision sentences that mention",
            "'decided' in narrative or quoted material; LLM agreement rows are fewer but semantically filtered.",
            "",
            f"*Generated by `scripts/keyword_baseline.py`*",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_MD}")
    print(f"KW recall {manual_matched_kw}/{manual_total}, LLM recall {manual_matched_llm}/{manual_total}")


if __name__ == "__main__":
    main()
