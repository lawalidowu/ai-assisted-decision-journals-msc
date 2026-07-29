# Visual inspection record — Wave 5B

**Method:** PowerPoint COM export to 1920×1080 PNG; manual inspection of each rendered image.  
**Tool:** Microsoft PowerPoint 16.0 via `win32com` · `python-pptx 1.0.2` source decks.

## Primary deck (12 slides)

| Slide | File | Status | Notes / corrections |
| --- | --- | --- | --- |
| 1 S01 | `rendered_slides/primary/slide_01.png` | Pass | Freeze banner readable; chips clear; no overflow |
| 2 S02 | `rendered_slides/primary/slide_02.png` | Pass | Speech-act chips + bullets readable |
| 3 S03 | `rendered_slides/primary/slide_03.png` | Pass | Exact aim intact; objectives grid aligned |
| 4 S04 | `rendered_slides/primary/slide_04.png` | Pass after fix | Stage kind labels clarified (processing vs machine vs human) |
| 5 S05 | `rendered_slides/primary/slide_05.png` | Pass | Evaluation layer chips |
| 6 S06 | `rendered_slides/primary/slide_06.png` | Pass | Three finding groups; required numbers present |
| 7 S07 | `rendered_slides/primary/slide_07.png` | Pass | Centrepiece comparison + A/B chips + teaching line |
| 8 S08 | `rendered_slides/primary/slide_08.png` | Pass | Three supporting cards |
| 9 S09 | `rendered_slides/primary/slide_09.png` | Pass | Four contribution blocks |
| 10 S10 | `rendered_slides/primary/slide_10.png` | Pass | Limitation → implication rows |
| 11 S11 | `rendered_slides/primary/slide_11.png` | Pass | Future-work list |
| 12 S12 | `rendered_slides/primary/slide_12.png` | Pass | Closing quote + questions |

## Fallback deck (8 slides)

| Slide | File | Status | Notes |
| --- | --- | --- | --- |
| 1 S01 | `rendered_slides/fallback/slide_01.png` | Pass | |
| 2 S02 | `rendered_slides/fallback/slide_02.png` | Pass | |
| 3 S03 | `rendered_slides/fallback/slide_03.png` | Pass | |
| 4 S04 | `rendered_slides/fallback/slide_04.png` | Pass | |
| 5 S06 | `rendered_slides/fallback/slide_05.png` | Pass | Compact eval cue in subtitle |
| 6 S07 | `rendered_slides/fallback/slide_06.png` | Pass | Centrepiece retained |
| 7 S09 | `rendered_slides/fallback/slide_07.png` | Pass | |
| 8 S12 | `rendered_slides/fallback/slide_08.png` | Pass | Limits folded into close; **8 / 8** |

## Issues found and corrected

| Rank | Finding | Action |
| --- | --- | --- |
| Medium | S04 stage sub-labels reused “automated validation” for chunking and traceability | Relabelled to “processing / automated check” vs “machine generation / freeze” and rebuilt |
| Low | Dense S06 number board | Acceptable at 1920×1080; supporting 5/10/0 etc. in footnote |
| Low | No Surrey logo (intentional) | Neutral academic theme; no unapproved branding |

## Automated geometry-only checks

Not used as sole validation. PNG renders + manual review required for pass.
