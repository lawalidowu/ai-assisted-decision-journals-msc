"""Apply AI provisional Rubric A/B ratings to dev manifest only.

NOT for thesis — human must re-rate pristine sample before submission.
Ratings based on decision + evidence + source_quote only (audit package).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROVISIONAL = ROOT / "configs/evaluation/confidence_validation_sample_provisional.json"

# (sample_index, rubric_a, rubric_b, note)
# Rubric B from 2-check: quote readable + quote supports decision text
RATINGS: list[tuple[int, str, str, str]] = [
    (1, "yes", "high", "COBR school closure; quote explicit"),
    (2, "yes", "medium", "COBR measures bundled in recall testimony"),
    (3, "yes", "high", "COVID-O agreed package; trace fail mechanical"),
    (4, "yes", "medium", "PM/CDL asked departments — commissioning not full adoption"),
    (5, "no", "high", "Hindsight witness opinion not decision event"),
    (6, "yes", "medium", "Recalled mandatory lockdown 23rd in testimony"),
    (7, "no", "high", "Witness characterisation of period not policy decision"),
    (8, "yes", "high", "Decision to close schools 20th supported"),
    (9, "yes", "medium", "Full measures decision; quote fragmentary"),
    (10, "yes", "medium", "Go full measure; partial quote span"),
    (11, "no", "high", "Minister asked leaders to make case — not agreed policy"),
    (12, "no", "high", "Witness advocacy strategy narrative"),
    (13, "yes", "high", "PHE rapid/full reviews commissioned"),
    (14, "unclear", "low", "Quote is counsel question not decision statement"),
    (15, "unclear", "low", "Manual-only row; no usable source quote"),
    (16, "no", "high", "Procedural adjournment"),
    (17, "no", "high", "Procedural reconvene"),
    (18, "no", "high", "Procedural adjournment"),
    (19, "no", "high", "Procedural Module 3 scheduling"),
    (20, "yes", "medium", "Operational resilience measures implemented"),
    (21, "no", "high", "Inquiry submission rule not pandemic policy"),
    (22, "no", "high", "Invitation to Inquiry chair to recommend"),
    (23, "no", "medium", "Testimony on PM view not decision event"),
    (24, "yes", "medium", "Covid Taskforce internal governance actions"),
    (25, "no", "high", "Duplicate inquiry recommendation row"),
    (26, "yes", "high", "PM announced Sept 22 package decision"),
    (27, "yes", "medium", "Countermeasures ordered; isolation detail beyond quote"),
    (28, "yes", "high", "Non-essential retail shut 20th"),
    (29, "no", "high", "Economic analysis finding not decision"),
    (30, "no", "high", "Advocacy for statutory children's rights"),
    (31, "no", "medium", "Submission misgivings; decision text overstates quote"),
    (32, "no", "high", "Meta statement about Inquiry scrutiny"),
    (33, "yes", "high", "Leadership change implemented per recommendation"),
    (34, "no", "high", "Duplicate testimony narrative"),
    (35, "no", "high", "Critique of Long Covid communications"),
    (36, "no", "high", "Review panel recommendation not adopted measure"),
    (37, "no", "high", "Future consideration pledge not decision"),
    (38, "no", "medium", "Advocacy critique on DHSC video"),
    (39, "yes", "medium", "Shielding recommendation in note to PM"),
    (40, "yes", "medium", "Datastreams work confirmed in counsel question"),
    (41, "no", "low", "Witness opinion; quote does not support coordinating-role claim"),
    (42, "no", "low", "Decision/quote mismatch on testing vs WHO"),
    (43, "yes", "medium", "Asked for improved analytical function"),
    (44, "yes", "high", "Recorded policy on school contingency guidance"),
    (45, "yes", "medium", "Action plan commissioning indirect in quote"),
    (46, "no", "high", "Numbered recommendation in core participant submission"),
    (47, "no", "medium", "Cross-examination agreement not policy decision"),
    (48, "unclear", "medium", "Urging PM chair COBR mixed with outcome 2 March"),
    (49, "yes", "high", "Agreed Long Covid campaign July 2020"),
    (50, "yes", "high", "PPE approval process amended"),
]


def score_to_checks(confidence: str) -> dict:
    mapping = {
        "high": {"quote_usable": True, "quote_supports": True, "points": 2},
        "medium": {"quote_usable": True, "quote_supports": False, "points": 1},
        "low": {"quote_usable": False, "quote_supports": False, "points": 0},
    }
    # medium often has usable quote but partial support — fix for medium
    if confidence == "medium":
        return {"quote_usable": True, "quote_supports": False, "points": 1}
    if confidence == "high":
        return {"quote_usable": True, "quote_supports": True, "points": 2}
    return {"quote_usable": False, "quote_supports": False, "points": 0}


def main() -> None:
    by_index = {idx: (a, b, note) for idx, a, b, note in RATINGS}
    data = json.loads(PROVISIONAL.read_text(encoding="utf-8"))
    assert len(data["items"]) == 50
    assert len(by_index) == 50

    for item in data["items"]:
        idx = item["sample_index"]
        a, b, note = by_index[idx]
        item["human_valid_decision"] = a
        item["human_confidence"] = b
        item["human_notes"] = f"[ai_provisional] {note}"
        item["rating_source"] = "ai_provisional"
        item["human_checks"] = score_to_checks(b)

    data["rating_provenance"] = "ai_provisional_dev"
    data["provisional_rated_at"] = datetime.now(timezone.utc).isoformat()
    data["provisional_rated_by"] = "apply_provisional_ratings.py"

    PROVISIONAL.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Rated 50/50 -> {PROVISIONAL}")


if __name__ == "__main__":
    main()
