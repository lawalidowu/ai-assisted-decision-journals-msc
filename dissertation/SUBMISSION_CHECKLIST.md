# Submission checklist

**Status:** Dissertation content is complete. Protect mode — no rewrites, no new experiments.

**Working file:** `dissertation/Lawal_MSc_Dissertation.docx` (generate with `python scripts/build_submission_docx.py` from official `MScDissertationTemplate2026.docx` + frozen markdown chapters).

**Do not use:** prior `Lawal_MSc_Dissertation_build.docx` / `_rebuilt.docx` (template merge artefacts). Text source of truth: `ABSTRACT.md`, `CHAPTER_*.md`, `REFERENCES.md` only.

**Frozen numbers (do not change):** 414 entries · 351 traceability pass · 84.8% · 21/50 no×high · 11/50 yes×high · 36 flagged · 20 clusters

---

## 1. References

- [ ] Every in-text citation appears in the bibliography
- [ ] Every bibliography entry is cited at least once
- [ ] Harvard style is consistent throughout
- [ ] URLs and access dates are consistent
- [ ] No duplicate entries

---

## 2. Figures

Five figures required: **3.1**, **3.2**, **4.3**, **4.9**, **4.10a** (embedded by submission build). Dense former Figure 4.10b is replaced by Appendix C Tables C.1–C.2.

- [ ] Each figure is introduced in the text before it appears
- [ ] Caption beneath figure, centred
- [ ] Readable at 100% zoom
- [ ] Not split awkwardly across pages
- [ ] List of Figures matches (four entries)

---

## 3. Surrey formatting

Use `MScDissertationTemplate2026.docx` (official template). Build with `python scripts/build_submission_docx.py`.

- [ ] Title page (title, name, programme, supervisor: Dr Joaquin Prada, date)
- [ ] Declaration of originality (signed) — text in `DECLARATION_OF_ORIGINALITY.md`
- [ ] Abstract pasted from `ABSTRACT.md` (check word limit)
- [ ] Table of Contents (auto-generate, update fields)
- [ ] List of Figures
- [ ] List of Tables
- [ ] Page numbering: roman front matter, arabic from Chapter 1

---

## 4. Final consistency audit

One read — confirm only, do not rewrite:

- [ ] Objectives match the work performed
- [ ] Figures introduced before they appear
- [ ] Terminology consistent (*candidate entries*, *journal validity*, *evidence strength*, *layered validation framework*)
- [ ] Frozen numerical results unchanged
- [ ] Discussion does not overclaim beyond reported results

---

## 5. PDF — read once, beginning to end

Export PDF. Read the **PDF**, not Word. Formatting fixes only.

**Print check before submit:**

- [ ] Page numbers correct
- [ ] No unexpected blank pages
- [ ] No bad widows/orphans on headings
- [ ] Figures readable
- [ ] Tables fit on one page where possible
- [ ] Hyperlinks removed (unless programme requires them)
- [ ] PDF opens correctly on another device

---

## 6. Submit

- [ ] Upload PDF via Surrey portal
- [ ] JISC originality check (declaration references this)
- [ ] Optional: short note to Dr Prada that submission is complete

---

## Do not do

- Rewrite chapters or abstract
- Add literature or experiments
- Re-run extraction or change frozen numbers
- Add new figures to the main body

---

*Engineering/build details archived in `SUBMISSION_ENGINEERING.md` and `.cursor/plans/dissertation_submission_engineering_58afb5ed.plan.md`.*
