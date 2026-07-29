# Manual annotation rubric

Use this rubric to label **excerpts** from inquiry transcripts, compare your labels to LLM extractions, and score quality. Adapted from Towler et al. (2023) convergence triangulation and Bondaronek et al. (2026) GRACE framework.

**Scope:** 5–10 excerpts (~200–800 words each) from the three manual-flagged Module 2 transcripts (28 Nov, 30 Nov, 01 Dec 2023). Do not annotate full PDFs.

**Session notes (definitions + per-excerpt chat guidance):** [`ANNOTATION_SESSION_NOTES.md`](ANNOTATION_SESSION_NOTES.md)

---

## 1. What counts as a decision?

Use the **operational definition** in [`ANNOTATION_SESSION_NOTES.md`](ANNOTATION_SESSION_NOTES.md) (aligned with the dissertation). Summary:

Extract **pandemic-response agreements, adopted measures, and authoritative directions** with a verbatim quote. Exclude witness opinion and unresolved proposals.

The `--inquiry` LLM prompt is narrower (“announced during the hearing”); manual annotation follows the **dissertation** definition unless you document otherwise.

---

## 2. Annotation workflow

1. **Select excerpt** — copy a passage from `data/processed/inquiry/document/<slug>.txt`; note `char_start` / `char_end` or line range.
2. **Label independently** — record decisions you find **before** opening the LLM JSON for that region.
3. **Match LLM outputs** — link each manual decision to the nearest LLM item (by `llm_run_id` + `llm_item_id`), or mark LLM-only / manual-only.
4. **Triangulate** — assign a convergence category (Section 3).
5. **Score GRACE** (optional per matched LLM item) — Section 4.
6. **Save** — workbook: `configs/annotations/manual_phase1.json` (regenerate shells with `python scripts/build_annotation_excerpts.py`).

Pre-built excerpt shells live in `configs/annotations/excerpts/excerpt_*.json`. **You still fill in** `manual_decisions` and `comparisons`.

---

## 3. Convergence triangulation (MATA-style)

Compare each **manual decision** ↔ **matched LLM decision** pair. Use Towler et al. categories:

| Category | Definition | Example |
|----------|------------|---------|
| **agreement** | Same formal decision; meaning aligns | Both record chair directing witness to produce documents by date X |
| **complementary** | Shared essence; one side adds nuance or scope | LLM captures direction; you add conditional wording or actor |
| **dissonance** | Genuine disagreement on whether a decision exists or what it was | LLM treats testimony as decision; you judge it is not formal |
| **silence** | Present in one method only | You find a ruling LLM missed, or LLM extracts a false positive you reject |

**Rules:**

- One triangulation row per compared pair (or per unmatched item with category `silence`).
- Dissonance is about **method disagreement**, not disagreement within the witness sample.
- If LLM bundles two decisions into one, split into two manual rows and triangulate separately.

---

## 4. GRACE-adapted quality (LLM outputs only)

Score each **matched LLM extraction** on 1–5. Mean scores are illustrative; brief notes matter more (Bondaronek et al.).

### Interpretability

| Score | Criterion |
|-------|-----------|
| 1 | Decision statement unclear or mislabels testimony as decision |
| 2 | Vague; reader cannot tell who decided what |
| 3 | Understandable but needs editing |
| 4 | Clear decision statement; minor ambiguity |
| 5 | Precise, scoped, immediately usable in a decision journal |

### Actionability

| Score | Criterion |
|-------|-----------|
| 1 | Not auditable; no practical use |
| 2 | Weak link to accountability or next step |
| 3 | Somewhat useful for tracing decision-making |
| 4 | Useful for inquiry-style audit |
| 5 | Directly supports accountability review (who, what, when) |

### Nuance

| Score | Criterion |
|-------|-----------|
| 1 | Over-generalised or flattens context |
| 2 | Misses conditions, caveats, or agency |
| 3 | Captures main point; loses some detail |
| 4 | Preserves most qualifications |
| 5 | Retains conditions, scope limits, and dissent where present |

### Redundancy

| Score | Criterion |
|-------|-----------|
| 1 | Duplicate of another extraction in same run |
| 2 | Largely overlaps another item |
| 3 | Some overlap; still distinct |
| 4 | Mostly distinct |
| 5 | Clearly distinct decision unit |

Add **reflexive note** (1–3 sentences): what worked, what failed, quote/traceability issues.

---

## 5. Mechanical traceability (automated check)

Your pipeline already sets `traceability_ok` when `source_quote` fuzzy-matches source text.

| Field | Your check |
|-------|------------|
| `traceability_ok` (system) | Quote found in text after PDF cleanup |
| `semantic_grounding` (you) | Quote **supports** the stated decision (yes / no / partial) |

A passing mechanical check can still fail semantic grounding.

---

## 6. JSON workbook structure

Templates:

- Blank item: `configs/manual_annotation_template.json`
- Full example: `configs/manual_annotation_workbook.example.json`
- Your work: `configs/annotations/manual_phase1.json` (copy example and rename)

Top-level fields:

```json
{
  "annotator": "your name",
  "created_at": "YYYY-MM-DD",
  "llm_runs": [{ "run_id": "...", "transcript_slug": "...", "path": "outputs/..." }],
  "excerpts": [ ... ]
}
```

Each excerpt contains `manual_decisions[]` and `comparisons[]` (triangulation + GRACE).

---

## 7. Reporting for the dissertation

Summarise in a table:

| Metric | Source |
|--------|--------|
| Excerpts annotated | Count from workbook |
| Manual decisions | Sum of `manual_decisions` |
| Agreement / complementary / dissonance / silence | Count `comparisons.triangulation` |
| Mean GRACE per dimension | Mean of scores where LLM item matched |
| Traceability pass rate | From run manifest |
| Semantic grounding rate | Your `semantic_grounding == yes` / total LLM items reviewed |

Cite: Towler et al. (2023) for triangulation; Bondaronek et al. (2026) for GRACE.

---

## 8. Suggested excerpt sources (28 Nov transcript)

Pick passages likely to contain formal decisions:

- Chair opening / procedural rulings
- Counsel summaries requesting directions
- Closing segments where actions are agreed

Avoid long uninterrupted witness narrative unless you know it contains a recorded decision.
