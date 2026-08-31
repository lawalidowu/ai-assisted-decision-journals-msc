# Chunk Sensitivity Dissertation Integration Report

## 1. Source of truth
Only `dissertation/Submission/Lawal_MSc_Dissertation_handbook_compliant.docx` was used as dissertation content authority. No Markdown rebuild.

## 2. Baseline
- source DOCX path: `dissertation/Submission/Lawal_MSc_Dissertation_handbook_compliant.docx`
- backup path: `dissertation/Submission/Lawal_MSc_Dissertation_PRE_CHUNK_SENSITIVITY_INTEGRATION_2026-08-30.docx`
- starting SHA-256: `216a66ddfbb4fbb4627ade9d0a210b87f71c1fa30e02feb3261dd7ffd9c11408`
- starting displayed word count: Number of Words: 9,767
- starting displayed page count: Number of Pages: 65

## 3. Sections changed
- Table 3.1
- 3.3.2
- new 3.5.5
- Table 4.6
- 4.8
- 4.9
- 5.3.3
- 5.4
- new B.9 / Table B.9
- front-matter word and page counts

## 4. Exact text changes
- 3.3.2: added frozen-dataset chronology paragraph (7/2 production config; post-freeze sensitivity test).
- 3.5.5: new subsection describing supplementary protocol and bounded design.
- Table 3.1 / 4.6: one row each for chunk/overlap sensitivity.
- 4.8: results paragraph with 4/6 vs 3/6 excerpt comparison, stability, 2/6 full-hearing tie, and 5/6 safeguard.
- 4.9: one summary sentence.
- 5.3.3: replaced single-sentence chunking limitation with expanded note preserving no corpus-scale model/prompt ablation.
- 5.4: one sentence on pre-scale chunk/overlap testing.
- B.9: appendix table and stability paragraph.

## 5. Safeguards
- 5/6 historical triangulation result unchanged in Chapter 4.3.
- 414-record dataset unchanged.
- No claim that 5/3 is optimal.
- Abstract unchanged.
- No research artefacts regenerated.

## 6. Word count
- previous = 9,767 (displayed)
- final = 9,976
- exact counting method = Body Text style paragraphs from Chapter 1 through Chapter 5 (pre-Appendix); regex word tokens; excludes Abstract, appendices, references, captions, headings and table cells.

## 7. Page count
- previous displayed = 65
- actual final PDF page count = 73
- final displayed Number of Pages = 73

## 8. TOC / LoF / LoT
- TOC/LoF/LoT fields updated via Word COM during integration run.
- Manual spot-check of Table 4.4 LoT page and pagination recommended.

## 9. Visual QA
Automated structural checks confirm §3.5.5, B.9, Table 3.1/4.6 rows, §4.8 results paragraph, and front-matter counts. Manual spot-check of pagination and B.9 table layout recommended.

## 10. Research artefact hash verification
- `data/manifests/phase1_decision_journal.json`: PASS
- `configs/annotations/manual_phase1.json`: PASS
- `configs/evaluation/confidence_validation_sample.json`: PASS
- `src/decision_journal/extraction.py`: PASS
- `configs/phase1_journal_runs.json`: PASS
- `configs/annotations/excerpts/excerpt_001.json`: PASS
- `configs/annotations/excerpts/excerpt_002.json`: PASS
- `configs/annotations/excerpts/excerpt_003.json`: PASS
- `configs/annotations/excerpts/excerpt_004.json`: PASS
- `configs/annotations/excerpts/excerpt_005.json`: PASS
- `configs/annotations/excerpts/excerpt_006.json`: PASS

## 11. Final files
- DOCX: `dissertation/Submission/Lawal_MSc_Dissertation_handbook_compliant_chunk_sensitivity_integrated.docx`
- PDF: `dissertation/Submission/Lawal_MSc_Dissertation_handbook_compliant_chunk_sensitivity_integrated.pdf`

## 12. Warnings
- Initial integration run failed at final copy due to file lock (WinError 32); resolved after closing Word/Cursor tabs.

CHUNK SENSITIVITY INTEGRATION: PASS
