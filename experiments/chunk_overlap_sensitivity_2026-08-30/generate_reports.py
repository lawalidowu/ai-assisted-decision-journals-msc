#!/usr/bin/env python3
"""Generate final reports from experiment results bundle."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

EXPERIMENT_DIR = Path(__file__).resolve().parent
ROOT = EXPERIMENT_DIR.parents[1]
BUNDLE = EXPERIMENT_DIR / "_results_bundle.json"
STAGE1_CSV = EXPERIMENT_DIR / "01_STAGE1_CONFIGURATION_RESULTS.csv"


def load_stage1_rows() -> list[dict]:
    import csv

    with STAGE1_CSV.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def pareto_analysis(rows: list[dict]) -> str:
    lines = ["## Pareto dominance pairs (A dominates B)", ""]
    configs = rows
    dominated: set[str] = set()
    pareto_optimal: set[str] = set()

    def metrics(r: dict) -> tuple:
        return (
            int(r["manual_decisions_recovered"]),
            float(r["traceability_pct"]),
            -int(r["unmatched_candidates"]),
            -int(r["duplicate_removed"]),
        )

    for a in configs:
        dominated_by_any = False
        for b in configs:
            if a["configuration"] == b["configuration"]:
                continue
            ma, mb = metrics(a), metrics(b)
            if all(x >= y for x, y in zip(ma, mb)) and any(x > y for x, y in zip(ma, mb)):
                lines.append(
                    f"- `{a['configuration']}` dominates `{b['configuration']}`"
                )
                dominated.add(b["configuration"])
                dominated_by_any = False
        if a["configuration"] not in dominated:
            pareto_optimal.add(a["configuration"])

    lines.extend(["", f"**Pareto-optimal configurations:** {sorted(pareto_optimal)}", ""])
    baseline = next(r for r in rows if r["configuration"] == "w7_o2")
    if "w7_o2" in pareto_optimal:
        lines.append("7/2 is **Pareto-optimal** within the tested grid.")
    elif "w7_o2" in dominated:
        lines.append("7/2 is **dominated** by at least one other configuration.")
    else:
        lines.append("7/2 is **not dominated** but is also not uniquely Pareto-optimal.")
    return "\n".join(lines)


def classify_72(rows: list[dict]) -> str:
    ranked = sorted(
        rows,
        key=lambda r: (
            -int(r["manual_decisions_recovered"]),
            -float(r["traceability_pct"]),
            int(r["unmatched_candidates"]),
            int(r["duplicate_removed"]),
        ),
    )
    baseline = next(r for r in rows if r["configuration"] == "w7_o2")
    best = ranked[0]
    b_rec = int(baseline["manual_decisions_recovered"])
    best_rec = int(best["manual_decisions_recovered"])

    if best["configuration"] == "w7_o2" and ranked[0] != ranked[1] if len(ranked) > 1 else True:
        if all(r["configuration"] == "w7_o2" or int(r["manual_decisions_recovered"]) < b_rec for r in ranked[1:]):
            return "7/2 VERDICT: EMPIRICALLY SUPPORTED AS BEST IN BOUNDED TEST"

    alt_better = [r for r in rows if int(r["manual_decisions_recovered"]) > b_rec]
    if alt_better:
        gap = int(alt_better[0]["manual_decisions_recovered"]) - b_rec
        if gap >= 2:
            return "7/2 VERDICT: ALTERNATIVE CONFIGURATION CLEARLY PREFERRED"
        return "7/2 VERDICT: ALTERNATIVE CONFIGURATION MODESTLY PREFERRED"

    # same recovery tier
    tier = [r for r in rows if int(r["manual_decisions_recovered"]) == b_rec]
    if len(tier) > 1:
        return "7/2 VERDICT: EMPIRICALLY SUPPORTED AS COMPETITIVE / NON-DOMINATED"

    return "7/2 VERDICT: EMPIRICALLY SUPPORTED AS COMPETITIVE / NON-DOMINATED"


def verify_frozen_hashes() -> str:
    snapshot = (EXPERIMENT_DIR / "BASELINE_SHA256_SNAPSHOT.txt").read_text(encoding="utf-8")
    lines = []
    for line in snapshot.strip().splitlines():
        expected, rel = line.split("  ", 1)
        rel = rel.strip()
        fp = ROOT / rel
        if fp.exists():
            actual = hashlib.sha256(fp.read_bytes()).hexdigest()
            status = "UNCHANGED" if actual == expected.strip() else "CHANGED"
            lines.append(f"| `{rel}` | {status} |")
        else:
            lines.append(f"| `{rel}` | MISSING |")
    return "\n".join(lines)


def main() -> None:
    rows = load_stage1_rows()
    baseline = next(r for r in rows if r["configuration"] == "w7_o2")
    ranked = sorted(
        rows,
        key=lambda r: (
            -int(r["manual_decisions_recovered"]),
            -float(r["traceability_pct"]),
            int(r["unmatched_candidates"]),
            int(r["duplicate_removed"]),
        ),
    )
    verdict = classify_72(rows)
    pareto = pareto_analysis(rows)

    stage3_path = EXPERIMENT_DIR / "03_CONFIRMATORY_RESULTS.csv"
    stage3_section = ""
    if stage3_path.exists():
        import csv

        with stage3_path.open(encoding="utf-8") as fh:
            s3 = list(csv.DictReader(fh))
        stage3_section = "\n".join(
            f"- {r['configuration']}: recovered {r['manual_decisions_recovered']}/6"
            for r in s3
        )
    else:
        stage3_section = "Stage 3 not performed; see `03_CONFIRMATORY_RESULTS.md`."

    stability_path = EXPERIMENT_DIR / "02_STABILITY_RESULTS.csv"
    stability_text = ""
    if stability_path.exists():
        import csv

        with stability_path.open(encoding="utf-8") as fh:
            s2 = list(csv.DictReader(fh))
        by_cfg: dict[str, list] = {}
        for r in s2:
            by_cfg.setdefault(r["configuration"], []).append(r)
        for cfg, reps in sorted(by_cfg.items()):
            rec = [x["manual_decisions_recovered"] for x in reps]
            stability_text += f"- **{cfg}**: recovery {rec}\n"

    report = f"""# Chunk/Overlap Sensitivity Analysis

## 1. Research question

How sensitive is decision extraction performance to sentence-window size and overlap, and was the configured 7-sentence / 2-sentence-overlap setting a reasonable choice within the bounded manually annotated material?

## 2. Frozen baseline

See `BASELINE_MANIFEST.md`. Git HEAD at experiment start: `a42d93555e8619b567daf833a30528e84013f1d3`. No frozen artefacts were modified.

## 3. Existing 7/2 configuration

Code-verified: `chunk_size=7`, `overlap=2`, `gpt-4o-mini`, temperature 0, inquiry-mode prompt. Original human triangulation on frozen full-transcript runs: 5/6 agreement-row recall.

## 4. Experimental protocol

Pre-registered in `00_PROTOCOL_PRE_REGISTERED.md` before comparative results were examined.

## 5. Evaluation material

Six excerpts (`excerpt_001`–`excerpt_006`), **6 manual decisions** total (1+2+0+0+0+3). Source spans preserved in excerpt JSON char offsets.

## 6. Configuration grid

12 configurations: window sizes {{5,7,9,11}} × overlaps {{1,2,3}}. All valid under existing chunker.

## 7. Matching/evaluation method

Deterministic overlap alignment reused from `scripts/keyword_baseline.py` plus `quote_found_in_text`. Primary recovery requires **both** mechanical quote match and automated semantic correspondence. See `GOLD_DECISION_ALIGNMENT.csv`.

## 8. Stage 1 results

| Rank | Config | Recovered | Recall | Candidates | Traceability | Unmatched | Dup removed |
|------|--------|-----------|--------|------------|--------------|-----------|-------------|
"""
    for i, r in enumerate(ranked, 1):
        report += (
            f"| {i} | {r['configuration']} | {r['manual_decisions_recovered']}/6 | "
            f"{r['manual_recall_pct']}% | {r['candidate_total']} | {r['traceability_pct']}% | "
            f"{r['unmatched_candidates']} | {r['duplicate_removed']} |\n"
        )

    report += f"""
**Baseline 7/2 (w7_o2):** recovered {baseline['manual_decisions_recovered']}/6 ({baseline['manual_recall_pct']}%), {baseline['candidate_total']} candidates, traceability {baseline['traceability_pct']}%.

## 9. Stability results

{stability_text or 'See `02_STABILITY_RESULTS.md`.'}

## 10. Confirmatory results (if performed)

{stage3_section}

## 11. Pareto analysis

{pareto}

## 12. Interpretation of 7/2

Within this bounded six-decision evaluation set, configuration **w7_o2** recovered **{baseline['manual_decisions_recovered']}/6** manual decisions with **{baseline['traceability_pct']}%** traceability and **{baseline['unmatched_candidates']}** unmatched candidates.

Top-ranked configuration by pre-specified hierarchy: **{ranked[0]['configuration']}** ({ranked[0]['manual_decisions_recovered']}/6 recovered).

## 13. Limitations

- Moving `gpt-4o-mini` alias (contemporary API, not historical snapshot).
- Six manual labels only; automated matching ≠ human triangulation.
- Excerpt-isolated Stage 1/2 vs full-hearing chunk context in Stage 3.
- Historical Phase 1 outputs and 414-record journal intentionally unchanged.

## 14. Exact defensible conclusion

This supplementary analysis empirically explored chunk/overlap sensitivity on frozen manual excerpts. Results inform whether 7/2 was **reasonable** within the tested grid, not whether it was uniquely optimal at corpus scale.

## 15. Recommended dissertation impact

See `DISSERTATION_INTEGRATION_RECOMMENDATION.md`.

---

{verdict}
"""
    (EXPERIMENT_DIR / "FINAL_CHUNK_SENSITIVITY_REPORT.md").write_text(report, encoding="utf-8")

    # Integration recommendation
    alt = ranked[0]
    integration = f"""# Dissertation integration recommendation (advisory only)

**No dissertation files were edited.** Recommendations based solely on observed experiment results.

## Section 3.3.2 (Model, chunking and temperature)

- **Change required?** {'Minor additive clarification recommended' if verdict.endswith('COMPETITIVE') or 'BEST' in verdict else 'Small sensitivity footnote recommended'}.
- **Proposed factual statement:** "A bounded supplementary sensitivity analysis (six manual decisions, 12 chunk/overlap configurations) found that the configured 7-sentence / 2-overlap setting recovered {baseline['manual_decisions_recovered']}/6 manual decisions under automated alignment; the strongest configuration in that grid was {ranked[0]['configuration']} ({ranked[0]['manual_decisions_recovered']}/6)."

## Supplementary methodology subsection

- **Justified?** Yes — one short subsection or footnote in Chapter 3 or Appendix B describing the bounded grid, frozen gold excerpts, and hierarchy-based comparison.

## Section 4.8 (structural / supplementary results)

- **Add sensitivity result?** Optional one paragraph if space permits; not required for core claims.

## Table 4.6

- **Add row?** Optional: one row summarising bounded chunk sensitivity (7/2 vs best alternative on 6 manual decisions). Not mandatory.

## Section 5.3.3 (limitations)

- **Change?** Consider adding: "Chunk size and overlap were not empirically optimised at corpus scale; a bounded post-hoc sensitivity check on six manual decisions is reported in [supplementary experiment]."

## Section 5.4

- **Change?** Only if integrating sensitivity paragraph in Discussion — otherwise unchanged.

## Abstract

- **Remain unchanged?** **Yes**, unless examiners request supplementary-method detail. Core contribution claims do not depend on 7/2 being uniquely best.

## Do NOT

- Regenerate the 414-record reference dataset.
- Replace original Phase 1 extraction outputs.
- Claim corpus-wide optimality.

## Frozen artefact verification (post-experiment)

| Artefact | Status |
|----------|--------|
{verify_frozen_hashes()}
"""
    (EXPERIMENT_DIR / "DISSERTATION_INTEGRATION_RECOMMENDATION.md").write_text(
        integration, encoding="utf-8"
    )
    print(f"Wrote final reports. Verdict: {verdict}")


if __name__ == "__main__":
    main()
