# Demo case selection (validated)

Validated against the frozen journal, n=50 sample, Audit E faithfulness CSV, and consistency-corrected n=60 codes. **No UI built.**

## Selected four cases

| Role | ID | Hearing | Teaching point |
| --- | --- | --- | --- |
| Yes × High | **phase1-016** | 2023-11-28 | Clean journal candidate: COBR school-closure recall; Rubric A=yes, B=high; triangulation agreement |
| No × High wrong-artefact | **phase1-082** | 2023-11-30 | Procedural adjournment with strong quote support; A=no, B=high; `procedural` flag |
| Materially unsupported / altered | **phase1-090** | 2023-12-01 | Counsel **question** used as quote; decision asserts commissioning — faithfulness `materially_unsupported_or_altered` |
| JEE / DQ framework | **phase1-246** | 2023-12-13 | Exact/near-verbatim; human JEE=`replace` **P3**; DQ=`replace` **commitment_to_follow_through** |

### Evidence paths

| ID | Journal | Other |
| --- | --- | --- |
| phase1-016 | `data/manifests/phase1_decision_journal.json` | n=50 sample; excerpt triangulation |
| phase1-082 | same | n=50; faithfulness paraphrase; consistency JEE/DQ=`procedural_or_inquiry` |
| phase1-090 | same | n=50 A=no B=medium; Audit E faith CSV; consistency insufficient_evidence |
| phase1-246 | same | Audit E faith exact; consistency JEE P3 + DQ commitment |

Demo JSON snapshots (no reviewer fields):  
`outputs/distinction_strategy/03_reproducibility_package/demos/phase1-0*.json`

### Provenance (untracked runs / public PDFs)

| ID | Run ID | Public PDF | Local run decisions SHA-256 (if present) |
| --- | --- | --- | --- |
| 016 | `run_20260608_005512_module2_2023-11-28` | Inquiry Module 2 28 Nov 2023 PDF URL in source manifest | `e5136219…` |
| 082 | `run_20260609_014425_module2_2023-11-30` | 30 Nov 2023 | `9f7e376d…` |
| 090 | `run_20260609_014914_module2_2023-12-01` | 1 Dec 2023 | `e8fc743b…` |
| 246 | `run_20260609_071809_module2_2023-12-13` | 13 Dec 2023 | `1763cc9c…` |

Runs are **historical provenance** only. Claim verification uses the **frozen journal**, not re-extraction.

## Rejected alternatives

| ID | Considered for | Why rejected |
| --- | --- | --- |
| phase1-018 | Faithfulness | Also materially unsupported, but “belief as decision” is softer than the counsel-question vs asserted-commission contrast in **090** |
| phase1-182 | JEE/DQ | Valid R4 care-home staff-movement case; **246** clearer multi-agency P3 + commitment teaching with exact/near-verbatim faith |
| phase1-124 | JEE/DQ | Excellent **DQ without JEE** example (26/60 pattern) but selected slot requires a clear **mapped** framework interpretation case |
| phase1-252 | No×High | Strong counsel-recommendation wrong-artefact, but **082** is the crispest procedural adjournment exemplar already emphasised in methods |

## Risks and caveats

- **016 / 090 / 246** mention public political or agency actors — keep excerpts short; label as Inquiry testimony.
- **082** is low-sensitivity and examiner-friendly.
- Single-reviewer human codes; κ values are vs author Rubric B, not inter-rater reliability.
- Do not display `reviewer_name` from consistency CSV in public demos.
