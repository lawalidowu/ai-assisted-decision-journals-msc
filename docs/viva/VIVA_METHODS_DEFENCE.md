# Methods defence

Use ≤2 minutes for complex items. Structure: rationale → evidence → alternative → limitation → effect.

## Cleaning and segmentation

- **Why:** Hearing PDFs/text mix procedure, questions and measures; cleaning reduces noise for chunking.  
- **Alt:** Full-document prompting — context limits / weaker localisation.  
- **Limit:** Cleaning choices can drop useful context.  
- **Effect:** Downstream quotes are chunk-local.

## Seven-sentence chunks, overlap two

- **Why:** Balance context vs localisation for quote anchoring (Ch3).  
- **Alt:** Paragraph / page chunks — coarser provenance.  
- **Limit:** Boundary effects; decisions spanning chunks.  
- **Effect:** Traceability is chunk-relative.

## Structured candidate schema

- **Why:** Forces decision / evidence / location fields for audit.  
- **Alt:** Free prose — harder to validate.  
- **Limit:** Schema may bias extraction toward “decision-shaped” text.  
- **Effect:** Enables mechanical checks + human rubrics.

## Temperature / prompt configuration

- **Why:** Low/zero temperature for Phase 1 reproducibility note in structural reliability production note.  
- **Alt:** Higher temperature creative extraction — less stable.  
- **Limit:** Configuration is model-specific.  
- **Effect:** Outputs frozen; live regen not guaranteed byte-identical.

## Stable IDs

- **Why:** `phase1-NNN` enables claim lineage across journal, samples, demo.  
- **Alt:** Unstable row indices.  
- **Limit:** IDs are study-local.  
- **Effect:** Examiner can follow one case end-to-end.

## Deduplication / flags

- **Why:** Non-destructive flags (e.g. procedural, possible_duplicate) for review navigation without rewriting generation.  
- **Alt:** Hard delete — loses audit trail.  
- **Limit:** Flags are heuristic.  
- **Effect:** Supports governance without silent deletion.

## `traceability_ok`

- **Why:** Mechanical check that generated statement links to source material in chunk.  
- **Not:** journal validity or semantic faithfulness.  
- **Evidence:** 351/414 in frozen journal.  
- **Limit:** Token/quote presence ≠ meaning preserved.

## Freeze before evaluation

- **Why:** Separate generation from evaluation; prevent moving targets.  
- **Evidence:** Fixed journal SHA `814cc7c4…`.  
- **Alt:** Live re-query during analysis — unreproducible.  
- **Limit:** Historical model snapshot only.

## Six manual excerpts

- **Why:** Bounded gold for triangulation / keyword baseline.  
- **Evidence:** App. A excerpts; 5/10/0.  
- **Limit:** Not full-corpus human labelling.

## Why n=42, n=50, n=60 differ

| Sample | Role |
| --- | --- |
| n=42 | Error taxonomy / false-positive characterisation |
| n=50 | Stratified Rubric A/B + confidence comparison |
| n=60 | Purposive JEE/DQ + faithfulness |

Different questions → different designs. Do not merge into one “accuracy”.

## Stratified n=50

- **Why:** Cover triangulation and wider strata; surface No × High.  
- **Limit:** Not a probability sample of all 414.

## Confidence separate from validity

- Automated signals compared to Rubric B; high confidence ≠ Rubric A yes.

## Clustering (20)

- Navigational organisation; group size ≠ policy importance.

## JEE / Decision Quality

- Interpretive frameworks after validated source; not performance scores.

## Report pilot / structural reliability

- Supplementary lenses (50/53; 49/50); not semantic validity.
