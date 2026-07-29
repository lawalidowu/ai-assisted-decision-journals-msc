# Command reference

Work from repository root. Never put a real API key in commands or docs.

## Offline (class 1)

```powershell
python -m pytest tests/test_appendix_a_excerpt_coordinates.py tests/test_phase2a_flag_counts_and_wordcount.py tests/test_leak_term_scan.py tests/test_examiner_evidence_package.py -q
python scripts/build_examiner_evidence_package.py
```

Recalculate headline totals from frozen journal (read-only):

```powershell
python -c "import json; j=json.load(open('data/manifests/phase1_decision_journal.json',encoding='utf-8')); print(j['totals'])"
```

## Public download (class 2) — optional; not required to verify frozen numbers

```powershell
python scripts/run_pipeline.py --stage download
python scripts/run_pipeline.py --stage text
```

## Requires OpenAI API (class 3) — **do not rerun to verify historical freeze**

```powershell
# NOT for historical claim verification
python scripts/run_extraction.py data/processed/inquiry/document/<slug>.txt --inquiry --label demo
python scripts/run_clustering.py
python scripts/compare_confidence_signals.py
```

## Dissertation build (optional; class 1 + local Word)

```powershell
python scripts/build_submission_docx.py
```

Does not alter analytical JSON. Requires Microsoft Word for field finalization on Windows.
