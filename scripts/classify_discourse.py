"""Exploratory discourse tags for Phase 2b validation sample (n=50 pilot).

Adds heuristic quote_speaker and utterance_domain fields. Does NOT modify the
pristine gold file (confidence_validation_sample.json).

Usage:
  python scripts/classify_discourse.py --validate
  python scripts/classify_discourse.py --validate --no-write
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = ROOT / "configs/evaluation/confidence_validation_sample.json"
PILOT_OUTPUT_PATH = ROOT / "configs/evaluation/confidence_validation_discourse_pilot.json"

SPEAKERS = ("witness", "counsel", "chair", "inquiry_official", "unknown")
DOMAINS = (
    "pandemic_policy",
    "inquiry_admin",
    "inquiry_procedure",
    "closing_submissions",
    "witness_narrative",
    "unknown",
)


def _text(*parts: str | None) -> str:
    return " ".join(p for p in parts if p).strip()


def classify_quote_speaker(quote: str | None, decision: str, evidence: str) -> tuple[str, str]:
    """Return (quote_speaker, confidence)."""
    q = (quote or "").strip()
    ql = q.lower()
    combined = _text(decision, quote, evidence).lower()

    if not q:
        return "unknown", "low"

    counsel_patterns = [
        r"\bdid you\b",
        r"\bcan we agree\b",
        r"\bso can we agree\b",
        r"\byou said that\b",
        r"\byou agreed that\b",
        r"\byou confirmed that\b",
        r"\byou stated that\b",
        r"\byou have told us\b",
        r"\bi put it to you\b",
        r"\byou accepted that\b",
        r"\bit'?s obvious from your witness statement\b",
        r"\byou requested\b",
        r"\byou will recall\b",
        r"\bare you aware\b",
        r"\bmy lady,?\s+we invite\b",
    ]
    if q.endswith("?") or any(re.search(p, ql) for p in counsel_patterns):
        return "counsel", "high"

    chair_patterns = [
        r"\badjourn",
        r"\bthe hearing (is|will be) adjourned\b",
        r"\bhearing adjourned\b",
        r"\blady hallett\b",
        r"\bthe chair\b",
        r"\bnext substantive hearings will commence\b",
    ]
    if any(re.search(p, ql) for p in chair_patterns):
        return "chair", "high"

    admin_patterns = [
        r"\bwritten submissions\b",
        r"\bcore participants\b",
        r"\bposition that has now been reached\b",
    ]
    if any(re.search(p, combined) for p in admin_patterns):
        return "inquiry_official", "medium"

    witness_patterns = [
        r"\b(i|we) (decided|agreed|implemented|ordered|chose|took the step|made sure|set up|corralled)\b",
        r"\b(i|we) (went|pushed|tasked|asked departments)\b",
        r"\bcobr decided\b",
        r"\bthe committee agreed\b",
        r"\bprime minister announced\b",
    ]
    if any(re.search(p, ql) for p in witness_patterns):
        return "witness", "high"

    if re.search(r"\b(he confirmed|they recommended).*\b(which i did|which we did)\b", combined):
        return "witness", "medium"

    return "unknown", "low"


def classify_utterance_domain(
    quote: str | None,
    decision: str,
    evidence: str,
    speaker: str,
) -> tuple[str, str]:
    """Return (utterance_domain, confidence). Order: specific inquiry genres first."""
    q = (quote or "").strip()
    ql = q.lower()
    combined = _text(decision, quote, evidence).lower()

    procedure_patterns = [
        r"\badjourn",
        r"\bhearing (will|is) (resume|reconvene|adjourned)\b",
        r"\bnext substantive hearings will commence\b",
        r"\bmodule\s*[23]\b.*\bhearing",
        r"\b10 o'?clock\b.*\b(wednesday|friday|tomorrow)\b",
    ]
    if any(re.search(p, combined) for p in procedure_patterns):
        return "inquiry_procedure", "high"

    admin_patterns = [
        r"\bwritten submissions\b.*\bpublished\b",
        r"\bcore participants\b.*\brefer to documents\b",
        r"\bposition that has now been reached\b",
    ]
    if any(re.search(p, combined) for p in admin_patterns):
        return "inquiry_admin", "high"

    closing_patterns = [
        r"\binvite you to recommend\b",
        r"\bmy lady,?\s+we invite\b",
        r"\blook forward to the same robust scrutiny\b",
        r"\bexecutive office has some misgivings\b",
        r"\bunacceptable absence in communications\b",
        r"\bsimply not enough\b",
        r"\bpublic health information and messaging should be\b",
        r"^\s*(one|two|three|four|five),?\s+",
        r"\bthey need the enforceability of their rights\b",
        r"\bwill consider closely the findings and recommendations that the inquiry makes\b",
    ]
    if any(re.search(p, combined) for p in closing_patterns):
        return "closing_submissions", "high"

    narrative_patterns = [
        r"\bwith hindsight\b",
        r"\bi see the period\b",
        r"\bessentially a ratcheting\b",
        r"\bhe confirmed that he had recognised\b",
        r"\btook the view\b",
        r"\bwe needed to\b",
        r"\bthe sense that i had\b",
        r"\banalysis showed\b",
        r"\breflects that\b",
        r"\bcorralled the voices\b",
        r"\bpolitical strategy\b",
    ]
    if any(re.search(p, combined) for p in narrative_patterns):
        return "witness_narrative", "high"

    if speaker == "counsel" and q.endswith("?"):
        return "pandemic_policy", "medium"

    if re.search(
        r"\b(cobr|covid-o|cabinet|committee|prime minister|minister|government) (decided|agreed|announced|ordered|asked)\b",
        combined,
    ):
        return "pandemic_policy", "high"

    if re.search(r"\b(i|we) (decided|agreed|implemented|ordered|tasked|asked)\b", ql):
        return "pandemic_policy", "high"

    if re.search(r"\bshould\b|\bneed to\b|\bmust\b|\brecommend\b", combined):
        return "witness_narrative", "medium"

    return "unknown", "low"


def classify_item(item: dict[str, Any]) -> dict[str, str]:
    decision = item.get("decision") or ""
    quote = item.get("source_quote")
    evidence = item.get("evidence") or ""

    speaker, speaker_conf = classify_quote_speaker(quote, decision, evidence)
    domain, domain_conf = classify_utterance_domain(quote, decision, evidence, speaker)

    return {
        "quote_speaker": speaker,
        "quote_speaker_confidence": speaker_conf,
        "utterance_domain": domain,
        "utterance_domain_confidence": domain_conf,
    }


def _axb_key(a: str | None, b: str | None) -> str:
    return f"A={a or '?'}|B={b or '?'}"


def print_cross_tabs(items: list[dict[str, Any]]) -> None:
    domain_a: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    domain_b: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    speaker_a: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    domain_axb: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    no_high_domains: dict[str, int] = defaultdict(int)

    for item in items:
        domain = item.get("utterance_domain", "unknown")
        speaker = item.get("quote_speaker", "unknown")
        a = item.get("human_valid_decision")
        b = item.get("human_confidence")

        if a:
            domain_a[domain][a] += 1
            speaker_a[speaker][a] += 1
        if b:
            domain_b[domain][b] += 1
        domain_axb[domain][_axb_key(a, b)] += 1

        if a == "no" and b == "high":
            no_high_domains[domain] += 1

    print("=" * 72)
    print("DOMAIN x RUBRIC A (n=50 exploratory heuristics)")
    print("=" * 72)
    print(f"{'utterance_domain':<28} | yes | no  | unclear | total")
    print("-" * 72)
    for domain in sorted(domain_a.keys()):
        counts = domain_a[domain]
        total = sum(counts.values())
        print(
            f"{domain:<28} | {counts.get('yes', 0):<3} | {counts.get('no', 0):<3} | "
            f"{counts.get('unclear', 0):<7} | {total}"
        )

    print("\n" + "=" * 72)
    print("SPEAKER x RUBRIC A")
    print("=" * 72)
    print(f"{'quote_speaker':<28} | yes | no  | unclear | total")
    print("-" * 72)
    for speaker in sorted(speaker_a.keys()):
        counts = speaker_a[speaker]
        total = sum(counts.values())
        print(
            f"{speaker:<28} | {counts.get('yes', 0):<3} | {counts.get('no', 0):<3} | "
            f"{counts.get('unclear', 0):<7} | {total}"
        )

    print("\n" + "=" * 72)
    print("DOMAIN x RUBRIC B")
    print("=" * 72)
    print(f"{'utterance_domain':<28} | high | med | low | total")
    print("-" * 72)
    for domain in sorted(domain_b.keys()):
        counts = domain_b[domain]
        total = sum(counts.values())
        print(
            f"{domain:<28} | {counts.get('high', 0):<4} | {counts.get('medium', 0):<3} | "
            f"{counts.get('low', 0):<3} | {total}"
        )

    print("\n" + "=" * 72)
    print("no x high BY DOMAIN (genre-blindness check — human gold)")
    print("=" * 72)
    for domain, count in sorted(no_high_domains.items(), key=lambda x: -x[1]):
        print(f"  {domain}: {count}")
    print(f"  TOTAL no×high: {sum(no_high_domains.values())} (expected 21)")


def run_validate(*, write: bool = True) -> dict[str, Any]:
    if not SAMPLE_PATH.is_file():
        raise FileNotFoundError(f"Missing validation sample: {SAMPLE_PATH}")

    payload = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    items = payload.get("items", [])

    enriched: list[dict[str, Any]] = []
    for item in items:
        row = dict(item)
        row.update(classify_item(item))
        enriched.append(row)

    print_cross_tabs(enriched)

    out = {
        "description": "Phase 2b discourse pilot — heuristic tags on validation sample only",
        "source": str(SAMPLE_PATH.relative_to(ROOT)).replace("\\", "/"),
        "classification_version": "1.0-heuristic-pilot",
        "note": "Exploratory; does not modify pristine gold ratings file",
        "items": enriched,
    }

    if write:
        PILOT_OUTPUT_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\nWrote pilot artefact: {PILOT_OUTPUT_PATH.relative_to(ROOT)}")

    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Exploratory discourse tags for Phase 2b n=50 pilot.")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Classify validation sample and print cross-tabs vs human A/B",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Print cross-tabs only; do not write pilot JSON",
    )
    args = parser.parse_args()

    if not args.validate:
        parser.error("Use --validate for the n=50 pilot (full 414 enrichment is out of scope).")

    run_validate(write=not args.no_write)


if __name__ == "__main__":
    main()
