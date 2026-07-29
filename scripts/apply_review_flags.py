"""Phase 2a — apply review flags to the canonical decision journal."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from decision_journal.review_flags import apply_review_flags  # noqa: E402

JOURNAL_PATH = ROOT / "data/manifests/phase1_decision_journal.json"


def main() -> int:
    journal = json.loads(JOURNAL_PATH.read_text(encoding="utf-8"))
    if journal.get("artifact_type") != "canonical_decision_journal":
        print("FAIL: not a canonical_decision_journal file")
        return 1

    entries = journal["entries"]
    counts = apply_review_flags(entries)

    journal["version"] = "1.1"
    journal["schema_note"] = (
        "v1.1 = Phase 2a review flags applied. Re-run build_phase1_journal.py resets to v1.0."
    )
    journal["phase2_steps"] = journal.get("phase2_steps", [])
    if "2a_review_flags" not in journal["phase2_steps"]:
        journal["phase2_steps"].append("2a_review_flags")
    journal["phase2a_applied_at"] = datetime.now(timezone.utc).isoformat()

    JOURNAL_PATH.write_text(
        json.dumps(journal, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    flagged = sum(1 for e in entries if e["phase2"]["review_flags"])
    print(f"Updated {JOURNAL_PATH}")
    print(f"  {len(entries)} entries, {flagged} with at least one flag")
    for key in sorted(counts):
        print(f"  {key}: {counts[key]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
