# Public GitHub release safety check

**Date:** 2026-08-31  
**Repository:** `https://github.com/lawalidowu/ai-assisted-decision-journals-msc` (private)  
**Original reproducibility tag:** `msc-dissertation-reproducibility-2026-08-31` → commit `9e4452ac3c03c8fdd400228a9a7fbec6d2634cf3` (preserved, not retargeted)  
**Public-release tag:** `msc-dissertation-public-release-2026-08-31` → post-cleanup commit (see below)  
**Scope:** Committed contents at the public-release tag (not untracked local files).

---

## Step 1 — Push verification

| Check | Result |
|-------|--------|
| `main` pushed | **Yes** — reproducibility release `a42d935..9e4452a`; public cleanup pushed after path sanitisation |
| Original reproducibility tag | **Preserved** — `msc-dissertation-reproducibility-2026-08-31` still points to `9e4452a` |
| Public-release tag | **Yes** — `msc-dissertation-public-release-2026-08-31` on cleanup commit |

---

## Step 2 — Security and privacy audit (public-release commit)

### Passed checks

| Category | Finding |
|----------|---------|
| **API keys / secrets** | No live keys found. Only placeholder `sk-your-key-here` in `.env.example`. No `.env` committed. |
| **Credentials files** | None committed. |
| **Meeting / supervisor transcripts** | **Not present** in committed tree (`Meeing 4.txt`, `Meeting *.md` untracked locally only). |
| **Other students' work** | **Not present** (`Jesutomiwa_*`, `Lohit_*` untracked locally only). |
| **Private correspondence** | No supervisor meeting notes or email threads in committed files. |
| **Large raw API archives** | `raw_responses_extended/` **not** committed. Model experiment includes only minimum Terra JSON + Sol invalidated/incomplete transparency files. |
| **Sol full-hearing evidence handling** | **Correct.** `17_FULL_HEARING_CONFIRMATION_REPORT.md` labels Sol as **INCOMPLETE — execution failure**; `15_FULL_HEARING_RUN_RESULTS.csv` contains Terra row only; invalidated/incomplete Sol JSON filenames are explicit. |
| **Frozen vs supplementary distinction** | **Clear** in `README.md` and `docs/REPRODUCIBILITY_GUIDE.md` (414-entry journal vs Aug 2026 `experiments/`). |
| **README as landing page** | **Suitable** — plain-language overview, links to reproducibility guide and architecture; release tag and journal SHA documented. |
| **Reproducibility guide reachable** | **Yes** — linked from README “Start here” section; states minimum dissertation-supporting experiment evidence is committed. |
| **Command paths** | Referenced scripts exist in tagged tree. |
| **Local path exposure (cleanup)** | **Resolved** — `C:/SURREY/...` and `C:\SURREY\...` removed from all six cleanup-target files (see below). |

### Remaining low-severity notes (not blockers)

| Severity | File(s) | Issue |
|----------|---------|-------|
| **Low — reviewer initials** | `outputs/framework_mapping/run_20260727_094015_post60_coding_consistency_audit/CONSISTENCY_CORRECTED_REFERENCE.csv` | `reviewer_name` column contains initials `AL` only (not full name). Acceptable for public release. |
| **Low — navigation clutter** | `outputs/distinction_strategy/**`, `docs/viva/**` | Internal development / viva-prep terminology; retained as audit history; README demotes these from primary navigation. |
| **Low — superseded dissertation artefacts** | `outputs/dissertation_integration/run_*_wave*/` | Historical July integration builds. Authoritative submission is `dissertation/Submission/final submission/Lawal_MSc_Dissertation_handbook_compliant.{docx,pdf}`. |

### UK COVID-19 Inquiry transcript redistribution

| Item | Assessment |
|------|------------|
| `data/processed/inquiry/document/*.txt` (8 hearings) | Public Inquiry material (~3.3 MB text). Reproducibility-justified; each row in `inquiry_module2_phase1.csv` includes official `pdf_url` / document URL. |
| `data/processed/inquiry/report/module-2-in-brief.txt` | Same assessment. |

No copyrighted third-party material beyond public Inquiry documents and the author's own dissertation was identified in the committed tree.

---

## Step 3 — Cleanup verification (items 1–7)

| Priority | File | Status |
|----------|------|--------|
| **1** | `data/manifests/inquiry_module2_phase1.csv` | **Done** — absolute paths replaced with repository-relative paths; substantive metadata preserved. |
| **2** | `outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/AUDIT_E_MANIFEST.json` | **Done** — repo-relative paths; hashes, counts, and audit content unchanged. |
| **3** | `outputs/framework_mapping/run_20260727_131920_audit_E_human_approval_check/AUDIT_E_HUMAN_APPROVAL_MANIFEST.json` | **Done** — same. |
| **4** | `outputs/framework_mapping/run_20260727_133838_post60_analytical_audit_E_final/AUDIT_E_SHA256SUMS.txt` | **Done** — relative paths; checksum values for unchanged artefacts preserved; manifest checksum updated to reflect sanitised manifest. |
| **5** | `outputs/framework_mapping/run_20260727_131920_audit_E_human_approval_check/AUDIT_E_HUMAN_APPROVAL_SHA256SUMS.txt` | **Done** — same. |
| **6** | `README.md` | **Done** — experiments now documented as committed in release tag; journal SHA and public-release tag noted. |
| **7** | `docs/REPRODUCIBILITY_GUIDE.md` | **Done** — gitignored/untracked experiment claims removed; minimum evidence set stated as committed. |

**Frozen journal integrity:** `data/manifests/phase1_decision_journal.json` SHA-256 unchanged at `814cc7c47a9f75bfc0a6c7b693feec7073e59131398d89fab7c9111fbb2e5e06` (414 entries).

**Offline tests:** 129 passed (includes 48 examiner-evidence / reproducibility guard tests).

---

## Step 4 — Documentation suitability summary

| Requirement | Status |
|-------------|--------|
| README is primary navigation | **Pass** |
| Reproducibility guide linked | **Pass** |
| Commands reference real files | **Pass** |
| 414 frozen vs supplementary experiments | **Pass** |
| Sol failure not performance evidence | **Pass** |
| Release tag documented for public users | **Pass** |
| No local workstation paths in release artefacts | **Pass** |

---

## Final verdict

## **SAFE_TO_MAKE_PUBLIC**

No confirmed secrets, private correspondence, meeting transcripts, or other students' work are in the public-release commit. All medium-severity local path exposure items have been sanitised. README and reproducibility guide are accurate for the committed release. The repository **is safe to make public** when the author chooses to change GitHub visibility.

**Do not make public until visibility is intentionally changed** — this audit does not alter repository settings.

---

*Audit performed 2026-08-31. Pre-cleanup audit on `9e4452a`; post-cleanup re-audit on public-release tag `msc-dissertation-public-release-2026-08-31`.*
