# Report genre pilot — Module 2 “In Brief”

**Document:** Module 2, 2A, 2B, 2C Report *In Brief* (PDF, ~60 KB)  
**Slug:** `module-2-in-brief` · **Category:** `report` (not hearing transcript)

## Pipeline

| Step | Result |
|------|--------|
| Manifest seed | `configs/inquiry_phase1_seeds.json` |
| PDF | `data/raw/inquiry/report/module-2-in-brief.pdf` |
| Text | `data/processed/inquiry/module-2-in-brief.txt` (12,659 chars) |
| Extraction | `outputs/run_20260609_081454_module2_in_brief_report` |
| Mode | Default prompt (not `--inquiry` — report prose, not hearing dialogue) |

## Extraction summary

| Metric | Value |
|--------|-------|
| Decisions extracted | 53 |
| Traceability pass | 50/53 (94%) |
| Traceability fail | 3 |

## Notes for dissertation

- Demonstrates **second document genre** beyond hearing transcripts.
- Report text is structured narrative + recommendations — extraction yields more “decision-like” statements (incl. Inquiry recommendations) than dialogue-heavy transcripts.
- **No manual annotation** on report in Phase 1; use as corpus breadth example + limitations (genre-specific prompt tuning needed).
- Compare: 8 transcript inquiry runs = 414 decisions; one In Brief report = 53 decisions in ~13k chars.

*Generated after pre-meeting depth upgrade, May/Jun 2026.*
