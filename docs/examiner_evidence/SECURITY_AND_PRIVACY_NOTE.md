# Security and privacy note

## Allowed content

- Public UK COVID-19 Inquiry transcript quotes already present in the frozen journal / evaluation files.
- Hashes, paths, and redacted demo snapshots.

## Forbidden in examiner package / docs

| Category | Rule |
| --- | --- |
| Secrets | Never include `.env`, API keys, or `sk-…` tokens. Only `.env.example` placeholders. |
| Private UKHSA material | Pilot uses **public Inquiry** sources only. Do not add restricted UKHSA documents. |
| Reviewer-identifying fields | Do not redistribute `reviewer_name`, emails, or session IDs from consistency CSVs in demo extracts (initials `AL` exist in source CSV — omit in package demos). |
| Correspondence | Meeting notes, supervisor email, personal drafts stay out of this pack. |
| Bulk trees | Do not track or zip `data/raw/**`, `data/processed/**`, or entire `outputs/run_*` trees into the package. |

## Package checks

Automated tests scan examiner docs + package files for likely key patterns and assert demo JSON lacks `reviewer_name`.
