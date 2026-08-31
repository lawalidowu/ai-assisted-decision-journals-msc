# Raw data

Place source files here. Nothing in this folder is committed to git (except this README).

## Automated pipeline (recommended)

From the repo root:

```powershell
# 1) Harvest metadata + build manifest (smoke test: --quick)
python scripts/run_pipeline.py --stage harvest --quick

# 2) Full Phase 1 harvest (~200 API pages, several minutes)
python scripts/run_pipeline.py --stage harvest

# 3) Download selected PDFs + convert to text
python scripts/run_pipeline.py --stage download
python scripts/run_pipeline.py --stage text

# Or all stages:
python scripts/run_pipeline.py
```

Manifest: `data/manifests/inquiry_module2_phase1.csv` (committed — audit trail).  
PDFs: `data/raw/inquiry/` · Text: `data/processed/inquiry/` (gitignored).

Config: `configs/inquiry_corpus.json` (Module 2, Phase 1 selection rules).

## Manual fallback

Download PDFs from the [UK COVID-19 Inquiry archive](https://covid19.public-inquiry.uk/documents/) into `data/raw/inquiry/` and run:

```powershell
python scripts/pdf_to_text.py data/raw/inquiry/your-file.pdf
```

## Pilot transcript (PEGASUS-era exploratory work)

`Transcript0.txt` at the repo root is from early exploratory testing. It is not part of the inquiry case study.
