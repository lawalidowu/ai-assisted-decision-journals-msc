# Visual asset plan — Wave 5A (inventory only; no asset generation)

**Rule:** Do not edit or generate assets in Wave 5A. Wave 5B produces slides from this inventory.

---

## 1. Existing dissertation figures (reuse candidates)

| Asset (expected path) | Intended slide | Suitability | Action for Wave 5B |
| --- | --- | --- | --- |
| `outputs/figures/conceptual_framework.png` (Fig 3.1) | S04 | High — shows layered validation idea | Simplify labels; enlarge stage names; match machine/auto/human/source colours |
| `outputs/figures/implemented_pipeline.png` (Fig 3.2) | S04 alt | Medium — may be too dense | Prefer simplified redraw over full figure |
| `outputs/figures/figure4_9_rubric_crosstab.png` / Word table of Fig 4.9 | S06 | High — supports no×high 21/50 | Highlight **no×high** cell only; hide clutter |
| `outputs/figures/phase1_cluster_sizes.png` | S06 optional | Medium — 20 clusters | Use only if space; else numeric “20” callout |
| `outputs/figures/phase1_cluster_composition.png` | Appendix / skip | Low for viva slides | **Do not show** live — too dense |
| `outputs/figures/phase1_cluster_composition.md` | Reference | Text companion | Not a slide visual |

**Note:** Confirm PNGs exist on the presentation machine before Wave 5B. If missing, recreate from dissertation build scripts **offline** — do not invent substitute charts with different numbers.

---

## 2. Figures requiring simplification

| Source idea | Why simplify | Presentation version |
| --- | --- | --- |
| Full Fig 4.9 crosstab | 3×3 cells too small on projector | One highlighted cell + marginal notes |
| Full cluster composition | Many themes | Omit or single “largest groups ≠ importance” callout |
| Audit E table dumps | Spreadsheet aesthetics | Four fractions only |
| Faithfulness table | Four categories | Horizontal 8 \| 25 \| 20 \| 7 bar |

---

## 3. Offline demo screenshots (capture later, offline only)

| Shot | Slide | Capture rule |
| --- | --- | --- |
| Landing / workflow | S04 or backup | Crop chrome; show freeze banner |
| Case 082 full panel | S07 | Centrepiece; must include A=No B=High |
| Case 016 / 090 / 246 | S08 | Optional triptych |
| Hash panel | Backup appendix | Only if examiner asks reproducibility |

Do **not** include desktop wallpaper, personal files, or browser bookmark bars.

---

## 4. Diagrams to recreate for clarity (Wave 5B)

| Diagram | Slide | Spec |
| --- | --- | --- |
| Governed workflow | S04 | 7 nodes; colour tokens matching demo.css intent |
| Six distinctions strip | S01 / S04 footer | generation · traceability · strength · faithfulness · validity · interpretation |
| Evaluation layer strip | S05 | Named lenses + n sizes |
| Wrong-artefact schematic | S07 | “Quote OK” + “Journal type wrong” |

Prefer native PowerPoint/Libre shapes or SVG — **no** external CDN icons, **no** stock photography.

---

## 5. Tables that should **not** be shown directly

- Full `confidence_validation_sample.json` rows  
- Full Audit E CSVs  
- Full triangulation excerpt JSON  
- Dissertation Table 4.x as tiny pasted screenshots  
- Keyword baseline long tables  

Show **aggregates only**, sourced from the evidence map.

---

## 6. Assets requiring no change

| Asset | Use |
| --- | --- |
| Exact Chapter 1 **aim** sentence | S03 text |
| Wave 4 evidence JSON field wording for 016/082/090/246 | S07–S08 quotes — copy, do not edit |
| Freeze banner wording | S01 / footer |

---

## 7. Misleading-risk visuals

| Risk | Avoidance |
| --- | --- |
| Green “pass” badges on 351/414 | Label “mechanical traceability pass”, not “validated decision” |
| Gauge charts for κ | Prefer numeric κ with “moderate / not replace human” |
| JEE heatmaps implying WHO scores | Text labels + “interpretive aid” |
| Live fake typing animation of LLM | Forbidden — frozen artefact |
| Photo of Parliament / COVID imagery | Avoid emotive stock; stay analytical |

---

## 8. Wave 5B delivery checklist (future)

- [ ] Confirm figure files on disk  
- [ ] Capture demo screenshots offline  
- [ ] Build ≤12 slides matching storyboard  
- [ ] Verify every number against `SLIDE_EVIDENCE_MAP.csv`  
- [ ] Export PDF handout optional — **not** required by handbook search
