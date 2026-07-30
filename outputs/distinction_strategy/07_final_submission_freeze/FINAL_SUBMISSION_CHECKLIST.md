# Final submission checklist

**Status:** Candidate freeze only. Dissertation is **not** marked submitted.  
**Head:** `c1feba145bdc46164b5daae79ec1a0d3901e97d0` · Branch: `distinction/final-submission-freeze`

## 1. Completed automatically

- [x] Wave 2–6 linear ancestry verified; `origin/main` still at baseline; FF to main possible (not performed)
- [x] Wave 2 DOCX/PDF hashes verified (`a829ff6d…` / `40c123b9…`)
- [x] PDF physical pages = 77
- [x] Page-by-page automated inspection recorded (77 pages; FAIL=0, WARNING=0)
- [x] Presentation 12/8 slide and PDF page counts verified
- [x] Deck SHA256SUMS match approved files
- [x] Demo evidence hashes match; launch binds `127.0.0.1`
- [x] Demo smoke test executed (see `validation/DEMO_SMOKE.json`)
- [x] Viva bank 102 / 28 adversarial; mocks 30/30
- [x] Pytest suite: 109 passed
- [x] Secret scan on tracked support trees: PASS
- [x] GitHub repository privacy confirmed PRIVATE
- [x] Freeze package assembled under `outputs/distinction_strategy/07_final_submission_freeze/`

## 2. Requires author visual confirmation

- [ ] Confirm title page shows **September 2026** (Wave 7A month gate closed)
- [ ] Spot-check PDF pages (especially title, word-count, Ch4 §4.4, Appendix A excerpt_002, references)
- [ ] Confirm tables/figures remain legible on your display/printer
- [ ] Confirm presentation slides in desktop PowerPoint (prior Wave 5B desktop verification: PASS — reconfirm if machine changed)
- [ ] Confirm offline demo landing page and phase1-082 centrepiece on viva machine

## 3. Requires author signature/date

- [ ] Sign and date the Declaration of originality (template requires author signature/date)
- [ ] Do **not** fabricate signature or submission date in files before you submit

## 4. Requires portal action

- [ ] Await/use emailed SurreyLearn submission-folder instructions (not stored in this repository)
- [ ] Upload electronic A4 dissertation (≤20 MB) by **1 Sep 2026** (handbook)
- [ ] Confirm whether portal wants PDF, DOCX, or both — **NO OFFICIAL RULE FOUND IN THE AVAILABLE REPOSITORY SOURCES** beyond electronic submission
- [ ] Upload presentation files **only if** emailed instructions require — otherwise viva-use only
- [ ] Provide separate code/web-link copy if examiners request bulky code (template guidance) — not as appendix listings

## 5. Requirement not found or unresolved

- Dissertation filename pattern: **NO OFFICIAL RULE FOUND IN THE AVAILABLE REPOSITORY SOURCES.**
- Presentation portal upload: **NO OFFICIAL RULE FOUND IN THE AVAILABLE REPOSITORY SOURCES.**
- Presentation filename rule: **NO OFFICIAL RULE FOUND IN THE AVAILABLE REPOSITORY SOURCES.**
- Mandatory examiner-evidence / demo package upload: **NO OFFICIAL RULE FOUND IN THE AVAILABLE REPOSITORY SOURCES.**
- Mandatory GitHub examiner access: **NO OFFICIAL RULE FOUND IN THE AVAILABLE REPOSITORY SOURCES.**
- Anonymisation: **NO OFFICIAL RULE FOUND…** (template is named submission)

## 6. Do not upload

- Raw/processed transcript trees (`data/raw`, `data/processed`)
- Historical `outputs/run_*` trees unless explicitly requested
- `.env` / credentials / Office `~$` temps / browser caches
- Completed personal rehearsal logs or audio/video recordings
- Untracked local drafts outside this freeze package
- Baseline/historical Wave 6C binaries as the active submission (use Wave 2 FINAL)

## 7. Day-of-presentation checklist

- [ ] Primary 12-slide deck + fallback 8-slide deck available offline
- [ ] `PRESENTER_RUNBOOK.md` + `DEMO_CUE_CARD.md`
- [ ] Optional: `python demo/launch_demo.py` (or `demo/print.html` fallback)
- [ ] `docs/viva/VIVA_RAPID_REVIEW.md` + evidence map path ready
- [ ] Centrepiece phase1-082 ready; talk complete even if demo skipped
- [ ] Timing: handbook 15–20 min, ≤20 hard, ≤12 slides

## 8. Recovery instructions

- Dissertation binaries: Wave 2 package hashes in `provenance/` and `formal_submission/`
- Decks: `outputs/distinction_strategy/05_presentation_deck/` (+ copies here)
- Demo fail: use `print.html` / evidence JSON; do not call live APIs
- Claim check: `docs/examiner_evidence/EXAMINER_EVIDENCE_MAP.md` + Audit E locator
- Repo recovery: branch `distinction/final-submission-freeze` @ `c1feba145bdc46164b5daae79ec1a0d3901e97d0` (after approval commit of Wave 7A artefacts)

**Do not treat this checklist as proof of portal upload, supervisor approval, examiner access, or viva attendance.**
