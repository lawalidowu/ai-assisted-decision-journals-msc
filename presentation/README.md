# Examiner presentation builder (Wave 5B)

## Selected production method

**python-pptx 1.0.2** (already installed; used by existing repo builders such as
`scripts/build_meeting_17_slide.py` and `scripts/build_covid_deck_v5.py`).

Selection verification:

1. Existing presentation builders in `scripts/` use `python-pptx` — pattern reused.  
2. `python-pptx` import succeeds locally (**1.0.2**).  
3. Local `pptxgenjs` package is **not** present under `node_modules`.  
4. No new packages were installed.

PDF/PNG rendering uses **Microsoft PowerPoint COM** (Office 16) via `pywin32`
(`win32com`), already available locally — no internet install.

## Regenerate

From repository root:

```powershell
python presentation/build_presentation.py
```

Outputs land in `outputs/distinction_strategy/05_presentation_deck/`.

Skip PowerPoint export (PPTX only):

```powershell
python presentation/build_presentation.py --skip-render
```

## Tracked sources

| File | Role |
| --- | --- |
| `presentation/build_presentation.py` | Deck builder + package docs + render |
| `presentation/presentation_content.py` | Slide text, timing, case quotes |
| `presentation/presentation_theme.py` | 16:9 theme, colours, helpers |
| `presentation/DEPENDENCY_LOCK.md` | Tool versions |

## Decks

- Primary: 15-minute planning target, **exactly 12 slides** (S01–S12)  
- Fallback: 10-minute planning target, **exactly 8 slides** (S01–S04, S06, S07, S09, S12)

Official handbook envelope remains 15–20 minutes / ≤12 slides / ≤20 hard cap.
