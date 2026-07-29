# Wave 6 — Viva defence implementation report

**Branch:** `distinction/viva-defence`  
**Starting commit (Wave 5B):** `cb34b144a49064b18939d37ea06b22ff936086af`  
**Status:** Implementation complete — **not committed / not pushed** (awaiting approval)

---

## Objective

Evidence-led viva defence and timed rehearsal package enabling clear explanation, methods defence, limitation honesty, frozen-evidence answers, contribution boundaries, safe recovery, and presentation rehearsal under time pressure.

Training materials only — **not** official examiner questions, mark schemes, or fabricated feedback.

---

## Files created

### `docs/viva/`

| File | Role |
| --- | --- |
| `VIVA_DEFENCE_MAP.md` | Hierarchy, skeleton, contribution lock, assets |
| `VIVA_QUESTION_BANK.md` / `.csv` | 102 rehearsal questions |
| `VIVA_ANSWER_ANCHORS.md` | Short anchors for probing/adversarial items |
| `VIVA_EVIDENCE_INDEX.csv` | 21 numerical/evidence rows with hashes |
| `VIVA_METHODS_DEFENCE.md` | Design choices with alternatives/limits |
| `VIVA_TECHNICAL_DEFENCE.md` | Reproducibility + statistical defence |
| `VIVA_GOVERNANCE_AND_ETHICS.md` | Prototype / oversight / deployment gates |
| `VIVA_CONTRIBUTION_AND_NOVELTY.md` | Four contribution layers |
| `VIVA_LIMITATIONS_DEFENCE.md` | Major limits with mitigations |
| `VIVA_FAILURE_AND_RECOVERY.md` | Non-bluffing recovery phrases |
| `VIVA_RAPID_REVIEW.md` | ~10-minute final-day sheet |
| `MOCK_VIVA_SCRIPT_01.md` | Balanced ~30Q mock |
| `MOCK_VIVA_SCRIPT_02.md` | Adversarial ~30Q mock |
| `MOCK_VIVA_SCORING_RUBRIC.md` | 10 dimensions × 1–5 + thresholds |
| `PRESENTATION_REHEARSAL_PLAN.md` | Six rehearsal models + checkpoints |
| `REHEARSAL_LOG_TEMPLATE.csv` | Timed rehearsal log columns |

### Scripts

| Script | Role |
| --- | --- |
| `scripts/generate_viva_question_bank.py` | Generate bank, anchors, evidence index |
| `scripts/build_viva_defence_package.py` | Assemble package + refresh SHA256SUMS |
| `scripts/validate_viva_defence_wave6.py` | Hash / secret / path / claim validation |

### Package

`outputs/distinction_strategy/06_viva_defence/`

- `candidate_pack/`
- `examiner_style_questions/`
- `rehearsal/`
- `validation/` (`NUMBER_LOCK.json`, `WAVE6_VALIDATION_REPORT.json`)
- `PACKAGE_MANIFEST.json`
- `SHA256SUMS`

### Tests / ignore

- `tests/test_viva_defence_wave6.py` (12 tests)
- `.gitignore` allow-list for `06_viva_defence/**`

---

## Question-bank size and distribution

| Metric | Count |
| --- | --- |
| Total unique questions | **102** (≥80) |
| Adversarial | **28** (≥20) |
| Foundational | 40 |
| Probing | 34 |

**By category:** methodology 16 · evaluation 15 · fundamentals 9 · adversarial 8 · traceability 7 · reproducibility 7 · AI/LLM design 6 · faithfulness 6 · governance and ethics 6 · statistics 5 · contribution and novelty 4 · limitations 4 · presentation-specific 4 · deployment 3 · data quality 2

---

## Mock-viva coverage

| Script | Style | Questions |
| --- | --- | --- |
| `MOCK_VIVA_SCRIPT_01` | Balanced examiner | 30 |
| `MOCK_VIVA_SCRIPT_02` | Sceptical / adversarial | 30 |

Each item includes expected answer components, follow-up trigger, evidence anchor, scoring notes.

---

## Evidence-index coverage

21 rows covering all locked headline numbers and four demo cases, including:

414 · 351/414 · 5/10/0 · 1/6 · 5/6 · 21/50 · κ 0.48/0.39 · exact agreement 0.80/0.76 · 20 clusters · 11/60 · 37/60 · 26/60 · 8/25/20/7 · 50/53 · 49/50 · phase1-016/082/090/246

Columns: topic, question_id, answer_claim, dissertation_location, authoritative_source, source_key_or_row, stable_id, evidence_hash, human_adjudicated, limitation, verification_status.

---

## Rehearsal models

1. Primary 12-slide (~15 min)  
2. Fallback 8-slide (~10 min)  
3. Primary without demo  
4. Primary + ≤2 min demo  
5. Interrupted presentation  
6. Immediate talk → viva transition  

Never omit: contribution, phase1-082, non-claims, limitations.

---

## Validation results

`scripts/validate_viva_defence_wave6.py` → **ok: true**

| Check | Result |
| --- | --- |
| Protected hashes (Wave 2 DOCX/PDF, journal, 4 demos) | PASS |
| Presentation PPTX/PDF vs Wave 5B SHA256SUMS | PASS |
| Secret / privacy scan on `docs/viva` | PASS |
| Evidence paths exist or hash-only marked | PASS |
| Claim tokens present | PASS |
| Forbidden overclaims absent | PASS |

### Pytest

```
109 passed
```

(= prior distinction-suite files previously reported as 85 at Wave 5B close, now 97 collected on those same module files + **12** Wave 6 tests → **109**)

Modules: examiner evidence, offline demo, storyboard, decks, leak-term, phase2a/wordcount, appendix A, post60 integrity, viva defence.

---

## Protected artefacts unchanged

| Artefact | SHA-256 | Status |
| --- | --- | --- |
| Wave 2 DOCX | `a829ff6d0b4a778f2a276f9fff45af05dbc47fa268f3a9b0b131a87099b0a2e2` | Unchanged |
| Wave 2 PDF | `40c123b9743277d9083d3b66eb855e0fa7a57101017d08a7d8a2d94558a63519` | Unchanged |
| Frozen journal | `814cc7c47a9f75bfc0a6c7b693feec7073e59131398d89fab7c9111fbb2e5e06` | Unchanged |
| Demo 016/082/090/246 | Wave 4 hashes | Unchanged |
| Presentation PPTX/PDF | Wave 5B SHA256SUMS | Unchanged |

**Not modified:** dissertation Markdown/DOCX/PDF content, analytical datasets/annotations/frozen journal, examiner-evidence package, offline demo, presentation decks. No new experiments. No external LLM API calls.

---

## Unresolved issues

| Rank | Issue | Notes |
| --- | --- | --- |
| Medium | Working copy `dissertation/Lawal_MSc_Dissertation.pdf` hash differs from Wave 2 FINAL PDF | Expected; protected verification uses Wave 2 package FINAL paths. Do not confuse the two. |
| Low | Evidence-index question_id aliases (`Q036b`, `demo-016`) | Stable claim coverage; not 1:1 with every Q id in the bank. |
| Low | `docs/viva/VIVA_QUESTION_BANK.csv` companion to markdown | Extra helper for tests/package; markdown remains the human-readable bank. |
| Low | Prior “85 passed” baseline vs current 97 on same modules | Suite grew or collection differs; Wave 6 adds 12; full current suite **109 passed**. |

No Critical or High blockers for Wave 6 delivery.

---

## How to use (candidate)

1. Read `VIVA_RAPID_REVIEW.md` (~10 min).  
2. Rehearse with `PRESENTATION_REHEARSAL_PLAN.md` + log template.  
3. Run mock scripts 01 then 02; score with rubric.  
4. Drill No×High / 082 / faithfulness / single-reviewer / one-model.  
5. Keep `docs/examiner_evidence/EXAMINER_EVIDENCE_MAP.md` open during viva.

---

## Stop point

Implementation, validation and this report are complete.  
**Do not commit or push until explicit approval.**
