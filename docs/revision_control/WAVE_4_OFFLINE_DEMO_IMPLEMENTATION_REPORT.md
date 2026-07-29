# Wave 4 — Offline Demo Implementation Report

**Branch:** `distinction/offline-demo`  
**Starting commit (exact parent):** `7b270854ddbb7b8c21e06de6711d90b856d95859` (Wave 3)  
**HEAD during implementation:** still `7b270854ddbb7b8c21e06de6711d90b856d95859` (no commit yet)  
**Status:** Implementation + validation complete. **Not committed. Not pushed.**

## Objective delivered

A self-contained, offline examiner demonstration that explains the project’s main technical contribution in ≤5 minutes: candidate generation is separate from validation; mechanical traceability, evidence strength, semantic faithfulness and journal validity are distinct. Centrepiece teaching case: **phase1-082** (No × High wrong-artefact).

## Files created

### `demo/` (self-contained demo)

| Path | Role |
| --- | --- |
| `index.html` | Landing + case panels; freeze banner |
| `demo.css` | Presentation layout; machine / auto / human / source distinction; system fonts |
| `demo.js` | Navigation; 7-section case layout; 090 side-by-side; 246 warning; hash panel |
| `evidence_embed.js` | Embedded frozen evidence + manifest (enables `file://` without fetch) |
| `print.html` | Printable static HTML fallback (no PowerPoint) |
| `launch_demo.py` | Stdlib localhost HTTP server + browser open |
| `DEMO_RUNBOOK.md` | One-command launch instructions |
| `DEMO_WALKTHROUGH.md` | Timed 5-minute examiner script |
| `DEMO_FAILURE_RECOVERY.md` | Failure modes and fallbacks |
| `DEMO_EVIDENCE_MANIFEST.json` | SHA-256 lock of the four evidence files |
| `evidence/phase1-016.json` | Wave 3 byte-identical copy |
| `evidence/phase1-082.json` | Wave 3 byte-identical copy (centrepiece) |
| `evidence/phase1-090.json` | Wave 3 byte-identical copy |
| `evidence/phase1-246.json` | Wave 3 byte-identical copy |

### Package + tooling + tests

| Path | Role |
| --- | --- |
| `outputs/distinction_strategy/04_offline_demo/` | Complete package (demo copy + manifests + validation) |
| `scripts/build_offline_demo_package.py` | Package assembler |
| `scripts/regenerate_offline_demo_embed.py` | Rebuilds `evidence_embed.js` + `print.html` from evidence JSON |
| `tests/test_offline_demo.py` | Offline / integrity / privacy / HTTP smoke tests |
| `.gitignore` | Allow-list for `04_offline_demo/` |
| `docs/revision_control/WAVE_4_OFFLINE_DEMO_IMPLEMENTATION_REPORT.md` | This report |

## Evidence source for each case

All four files are **byte-identical** to Wave 3 package demos under  
`outputs/distinction_strategy/03_reproducibility_package/demos/`.

| Case | Role | Source SHA-256 |
| --- | --- | --- |
| phase1-016 | Yes × High alignment | `e5d28326427f4108ed97922bf444a4467ce807e4aa198277e2ba46d6cd3a2953` |
| phase1-082 | No × High wrong-artefact (centrepiece) | `9b131dc2b403f51a3a1de366ee56793c6ff255986a57e683d525297963cca2c0` |
| phase1-090 | Materially unsupported / altered | `7e94f16177c4ce820f956d64d27dfd9a1798e91627cb7e372ac43b0ba25ed430` |
| phase1-246 | JEE P3 + DQ `commitment_to_follow_through` | `30e2cf20540de86b618cc3790b006148fb50905e3c51b35c404dab88099440ee` |

Hashes are reported in `DEMO_EVIDENCE_MANIFEST.json` and displayed on the demo hash panel.

## Launcher behaviour

Command: `python demo/launch_demo.py`

- Stdlib only (`http.server`, `socketserver`, `webbrowser`)
- Binds **`127.0.0.1` only** (never public interfaces)
- Chooses preferred port 8765 or the next free nearby port
- Opens browser when possible (`--no-browser` to skip)
- Prints local URL and Ctrl+C shutdown instruction
- Hard-fails with readable message if required demo files are absent

## Supported browsers

Verified design target: current **Microsoft Edge** and **Google Chrome** on Windows.  
System fonts only (`Segoe UI` / Georgia / Consolas). No CDN fonts or scripts.

Interactive demo also works from `file://` via `evidence_embed.js` where script loading is permitted. Prefer the launcher for viva presentation.

## Test results

```
61 passed
```

Composition:

- Prior Wave 3 suite (Appendix A excerpt + Phase 2a flags/wordcount + leak scan + examiner package): **48**
- New `tests/test_offline_demo.py`: **13** additional checks

Covered:

- Four evidence files exist; IDs exactly `016`, `082`, `090`, `246`
- Byte identity with Wave 3 demos; displayed decision/quote/rubric fields match
- Evidence SHA-256 matches manifest; embed matches JSON
- No API-key / CDN asset patterns in demo assets
- No full transcript / PDF bulk files in demo
- Local-only asset references in `index.html`
- Launcher localhost bind
- HTTP 200 smoke for `index.html` and centrepiece evidence JSON
- Frozen journal + Wave 2 DOCX/PDF hashes unchanged

## Offline validation

| Check | Result |
| --- | --- |
| No remote URLs required for rendering | Pass |
| System fonts only | Pass |
| Relative CSS/JS only | Pass |
| Evidence frozen copies (no write path to analytical sources) | Pass |
| Visible “Frozen research artefact — no live model call” | Pass |
| Printable fallback without PowerPoint (`print.html`) | Pass |

### Manual offline smoke test (pre-commit)

Command: `python demo/launch_demo.py --no-browser --port 8765`  
Log: `outputs/distinction_strategy/04_offline_demo/validation/OFFLINE_SMOKE_TEST.json`

| Check | Result |
| --- | --- |
| Bind address | `127.0.0.1` only |
| `index.html` HTTP 200 + landing | Pass |
| Freeze notice exact text | Pass |
| phase1-016 Yes × High | Pass |
| phase1-082 No × High centrepiece | Pass |
| phase1-090 materially unsupported/altered | Pass |
| phase1-246 JEE P3 + Decision Quality | Pass |
| No external network resources requested | Pass |
| `print.html` | Pass |
| `file://` / embed fallback assets present | Pass |

Overall: **SMOKE_PASS**. Screenshots not bundled (no capture dependency).

## Security / privacy

| Check | Result |
| --- | --- |
| No OpenAI / external API calls | Pass |
| No secrets / `sk-` patterns in demo tree | Pass |
| Launcher localhost-only | Pass |
| No complete raw transcripts or PDFs in demo | Pass |
| `public_pdf_url` present as provenance text in JSON only (not loaded by UI) | Accepted / Low residual |

## Package path and hashes

Package: `outputs/distinction_strategy/04_offline_demo/`

Contents: `demo/` (full self-contained copy), `PACKAGE_MANIFEST.json`, `SHA256SUMS`, `validation/OFFLINE_DEMO_VALIDATION.json`, `validation/PYTEST_LOG.txt`.

Evidence file hashes (as packaged) match the manifest table above. Full file inventory: see package `SHA256SUMS`.

## Confirmation: protected artefacts unchanged

| Artefact | Expected SHA-256 | Verified |
| --- | --- | --- |
| Frozen journal `data/manifests/phase1_decision_journal.json` | `814cc7c47a9f75bfc0a6c7b693feec7073e59131398d89fab7c9111fbb2e5e06` | Yes |
| Wave 2 DOCX | `a829ff6d0b4a778f2a276f9fff45af05dbc47fa268f3a9b0b131a87099b0a2e2` | Yes |
| Wave 2 PDF | `40c123b9743277d9083d3b66eb855e0fa7a57101017d08a7d8a2d94558a63519` | Yes |

Dissertation Markdown, DOCX, PDF, annotations, and analytical JSON/CSV were **not modified** in this wave.

## Unresolved issues

| Rank | Issue | Notes |
| --- | --- | --- |
| Critical | None | — |
| High | None introduced by Wave 4 | Pre-existing Wave 3 High gap (large Phase 1 `outputs/run_*` / raw PDFs untracked) remains out of scope |
| Medium | Screenshots not bundled | Avoided adding capture dependencies; use live demo or `print.html` |
| Low | Provenance `https://…pdf` strings in evidence JSON | Not used for rendering; UI never fetches them |
| Low | Cream/serif presentation styling | Research demo readability over brand redesign |

## Stop condition

Implementation, validation and this report are complete. **Awaiting approval before any commit or push.**
