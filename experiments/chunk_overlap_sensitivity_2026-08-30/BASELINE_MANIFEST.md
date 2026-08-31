# Baseline manifest — chunk/overlap sensitivity experiment

**Experiment directory:** `experiments/chunk_overlap_sensitivity_2026-08-30/`  
**Recorded:** 2026-08-30 (UTC+1)  
**Purpose:** Freeze authoritative dissertation artefacts before any supplementary sensitivity work.

---

## Git state at experiment start

| Field | Value |
|-------|-------|
| Branch | `main` |
| HEAD commit | `a42d93555e8619b567daf833a30528e84013f1d3` |
| Commit message | Freeze final September submission candidate |
| Remote tracking | `origin/main` (up to date) |
| Working tree | Uncommitted local edits present in dissertation markdown/build scripts (not modified by this experiment) |

**Non-destructive rule:** No files listed below were altered as part of experiment setup.

---

## Authoritative frozen artefacts

### Phase 1 source and preprocessing

| Role | Path |
|------|------|
| Processed transcripts (8 hearings) | `data/processed/inquiry/document/*.txt` |
| Corpus manifest | `data/manifests/inquiry_module2_phase1.json` |
| Phase 1 run registry | `configs/phase1_journal_runs.json` |
| PDF→text / cleaning | `src/decision_journal/pdf_text.py`, `extraction.clean_inquiry_text` |
| Sentence splitting / chunking | `src/decision_journal/extraction.py` (`split_sentences`, `chunk_text_by_sentences`) |

### Extraction pipeline

| Role | Path |
|------|------|
| Extraction logic | `src/decision_journal/extraction.py` |
| CLI wrapper | `scripts/run_extraction.py` |
| Inquiry-mode prompt | `INQUIRY_PROMPT_TEMPLATE` in `extraction.py` |
| Model default | `gpt-4o-mini` (alias; see IMPLEMENTATION_RECONSTRUCTION.md) |
| Temperature | `0` (`call_extractor`) |
| Deduplication | `dedupe_decisions` (key = lowered `decision\|evidence`) |
| Traceability | `validate_traceability`, `quote_found_in_text` |

### Fixed reference dataset and evaluation

| Role | Path | SHA-256 |
|------|------|---------|
| **414-record fixed journal** | `data/manifests/phase1_decision_journal.json` | `814cc7c47a9f75bfc0a6c7b693feec7073e59131398d89fab7c9111fbb2e5e06` |
| Manual triangulation workbook | `configs/annotations/manual_phase1.json` | `07ad64ebee6c4c0c378488927e3f945e3d8c04d77e6921e266884139b800581b` |
| n=50 validation sample | `configs/evaluation/confidence_validation_sample.json` | `9d74936c490de586c126bd4ad059cc20345702655a3a9f3b2455677d195d8169` |
| Six excerpt JSON files | `configs/annotations/excerpts/excerpt_001.json` … `excerpt_006.json` | see table below |
| Phase 1 run registry | `configs/phase1_journal_runs.json` | `1858a5935cfca85a889ca20855b792927abceea2ae609bca9425b252ccb97e91` |

### Six manually annotated excerpts (machine-readable)

| Excerpt | SHA-256 | Manual decisions |
|---------|---------|------------------|
| excerpt_001 | `135eca3f02cf9a0d0b817bca7ec3e60da552308466e34b71f2836e2d08b34c1c` | 1 |
| excerpt_002 | `1d9a16c4127d3c80a7b3cf555aca51186573da81900ff31a375ddbf58153df0a` | 2 |
| excerpt_003 | `60b2bd59cce9e1b4b415b6f2317f8431e147a5463db93920ba9b8da26d4dcd62` | 0 |
| excerpt_004 | `7ebf001f9728f1e081462e081e0c274b663ed9f5fafbad339b021f4eafdd6501` | 0 |
| excerpt_005 | `2634ce466ec06bd7153d863a825b27a3e1c1aae4d13643d855faa9c03e92baac` | 0 |
| excerpt_006 | `d399c06b2b04c9dd26eaaa819033f0846afdf32a722bca38836d606d1cbc7d3b` | 3 |
| **Total manual decisions** | | **6** |

### Canonical Phase 1 extraction outputs (local, not Git-tracked)

Eight run directories named in `configs/phase1_journal_runs.json` (e.g. `outputs/run_20260608_005512_module2_2023-11-28/`). Example manifest confirms `model=gpt-4o-mini`, `chunk_size=7`, `chunk_overlap=2`, `inquiry_mode=true`.

### Dissertation submission artefact (hash-only; not edited)

| File | SHA-256 (2026-08-30) |
|------|----------------------|
| `dissertation/Lawal_MSc_Dissertation_handbook_compliant.docx` | `d723976a060315639f35e6fc100725a8e9d105f8ba0f3363796231ccd6fd2511` |

### Extraction source code (frozen reference)

| File | SHA-256 |
|------|---------|
| `src/decision_journal/extraction.py` | `817814f80cc6e7ac5f8f8c93a4911d8528ac865f1e67a485fd68231d89976467` |

### Triangulation / comparison artefacts

| Role | Path |
|------|------|
| Triangulation summary generator | `scripts/summarize_triangulation.py` |
| Keyword baseline matcher | `scripts/keyword_baseline.py` (`overlaps` quote/decision alignment) |
| Appendix A coordinate tests | `tests/test_appendix_a_excerpt_coordinates.py` |
| Repository baseline manifest | `BASELINE_SHA256_MANIFEST.json` (Wave 1, 2026-07-29) |

---

## SHA-256 manifest (experiment baseline snapshot)

See `BASELINE_SHA256_SNAPSHOT.txt` in this directory for a machine-readable copy of the hashes above.

---

## Experiment isolation

All new scripts, API outputs, logs, CSV/MD reports, and derived JSON from this sensitivity study are confined to:

`experiments/chunk_overlap_sensitivity_2026-08-30/`

No production extraction scripts, frozen datasets, dissertation files, or original Phase 1 outputs are modified.
