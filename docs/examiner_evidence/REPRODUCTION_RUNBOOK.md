# Reproduction runbook (compact)

> **Primary guide:** [`docs/REPRODUCIBILITY_GUIDE.md`](../REPRODUCIBILITY_GUIDE.md) — full pipeline order, dissertation claim index, supplementary experiments, and adaptation notes for new researchers. This page is a short offline command checklist.

**Goal:** Inspect and validate the **frozen** dissertation evidence chain offline.  
**Never** regenerate the 414-entry journal to verify historical claims.

## 1. Environment setup (offline)

```powershell
cd "<repo-root>"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Do NOT copy secrets. If experimenting with API features later, copy .env.example locally only.
```

## 2. Offline integrity tests

```powershell
python -m pytest tests/test_appendix_a_excerpt_coordinates.py tests/test_phase2a_flag_counts_and_wordcount.py tests/test_leak_term_scan.py tests/test_examiner_evidence_package.py -q
```

**Class:** 1 · Offline.

## 3. Appendix A coordinate tests (21)

Covered by `tests/test_appendix_a_excerpt_coordinates.py` in the command above.

## 4. Flag / word-count tests

Covered by `tests/test_phase2a_flag_counts_and_wordcount.py`.

## 5. Leak-term tests

Covered by `tests/test_leak_term_scan.py` (legitimate JEE phrasing passes; foreign-author leaks still fail).

## 6. Recalculate analytical claims from frozen sources

```powershell
python - <<'PY'
import json, csv
from pathlib import Path
j=json.loads(Path('data/manifests/phase1_decision_journal.json').read_text(encoding='utf-8'))
print('totals', j['totals'])
s=json.loads(Path('configs/evaluation/confidence_validation_sample.json').read_text(encoding='utf-8'))
cells={}
for i in s['items']:
    key=(i['human_valid_decision'], i['human_confidence']); cells[key]=cells.get(key,0)+1
print('no_high', cells.get(('no','high')))
k=json.loads(Path('configs/evaluation/confidence_comparison_results.json').read_text(encoding='utf-8'))
print('rule_kappa', round(k['metrics']['rule_vs_human_b']['weighted_kappa'],2),
      'llm_kappa', round(k['metrics']['llm_vs_human_b']['weighted_kappa'],2))
m=json.loads(Path('outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/AUDIT_E_MANIFEST.json').read_text(encoding='utf-8'))
print('faith', {k:m[k] for k in m if k in ('exact_or_near_verbatim','substantively_faithful_paraphrase','materially_unsupported_or_altered','traceability_false')} or m.get('traceability_category_counts'))
print('clusters', json.loads(Path('data/manifests/phase1_clustering_report.json').read_text(encoding='utf-8'))['n_clusters'])
print('structural', json.loads(Path('configs/evaluation/structural_reliability_results.json').read_text(encoding='utf-8'))['summary'])
PY
```

**Class:** 1 · Offline. Uses frozen files only.

## 7. Evidence-map / package validation output

```powershell
python scripts/build_examiner_evidence_package.py
python -m pytest tests/test_examiner_evidence_package.py -q
```

Outputs refresh under `outputs/distinction_strategy/03_reproducibility_package/` (demos, SHA256SUMS, validation log).

## 8. Dissertation build (optional separate step)

```powershell
python scripts/build_submission_docx.py
```

**Class:** 1 + local Word. Does not change analytical JSON. Not required for evidence-map claim checks.

---

## Marked command classes

| Action | Offline | Public download | OpenAI API | Must not rerun for historical freeze |
| --- | --- | --- | --- | --- |
| pytest suite above | ✓ | | | |
| Recalculate from JSON | ✓ | | | |
| `run_pipeline.py --stage download/text` | | ✓ | | Optional only |
| `run_extraction.py --inquiry` | | | ✓ | **Must not** |
| `run_clustering.py` / LLM confidence | | | ✓ | **Must not** |
| `build_phase1_journal.py` | ✓ if runs present | | | **Must not overwrite freeze** |
