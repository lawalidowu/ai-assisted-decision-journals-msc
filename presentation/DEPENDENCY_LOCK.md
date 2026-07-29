# Wave 5B dependency lock (no new installs)

Recorded from the build machine at generation time.

| Tool | Version | Role | Install action |
| --- | --- | --- | --- |
| Python | local environment | Runtime | Already present |
| python-pptx | **1.0.2** | PPTX generation | Already present — **no install** |
| pywin32 / win32com | already importable | PowerPoint COM PDF/PNG export | Already present — **no install** |
| Microsoft PowerPoint | **16.0** (COM) | PDF + 1920×1080 PNG render | Already installed Office |
| PptxGenJS | not present | Not used | Not installed |
| LibreOffice | not required | Not used | Not installed |

Selection reason: repository already uses python-pptx for slide generation;
python-pptx was verified available; PptxGenJS was not present locally.
