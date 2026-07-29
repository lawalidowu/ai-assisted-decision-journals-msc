# Demo failure recovery

## Browser does not open automatically

1. Read the URL printed by `launch_demo.py` (e.g. `http://127.0.0.1:8765/index.html`).
2. Paste it into Edge or Chrome.
3. Or relaunch with `python demo/launch_demo.py --no-browser` and open manually.

## Selected port is unavailable

The launcher tries nearby ports on **127.0.0.1**. If all fail:

```powershell
python demo/launch_demo.py --port 8890
```

## JavaScript is disabled

Use `DEMO_WALKTHROUGH.md` plus the JSON files in `evidence/`. The overview still shows the proposition when noscript styles apply; case boards need JS or printed walkthrough.

## Display scaling makes text too small

- Set browser zoom to 100–125% on a 1920×1080 display.
- Use full-screen (F11).
- Prefer Edge/Chrome; avoid extreme OS scaling above 150% without zoom adjust.

## Local server cannot start

1. Confirm Python 3 is available: `python --version`.
2. Confirm you are launching `demo/launch_demo.py` and the `demo/` folder is intact.
3. Check firewall prompts for localhost Python — allow for private networks if asked.
4. Fallback: open `demo/index.html` directly (see below).

## Full fallback using index.html

Open `demo/index.html` directly in Edge or Chrome. Case boards load from
`evidence_embed.js` (no network). Prefer the launcher when possible so paths and
console logging are consistent.

If the page is blank or scripts are blocked:

1. Use `DEMO_WALKTHROUGH.md` verbally;
2. Open each `evidence/phase1-*.json` beside it;
3. Or open `demo/print.html` (printable static HTML view — no PowerPoint).

Manual server fallback:

```powershell
cd demo
python -m http.server 8765 --bind 127.0.0.1
```

## Printable / offline viewing without PowerPoint

- Open `demo/print.html` and Print / Save as PDF from the browser.
- Or print / PDF-save `DEMO_WALKTHROUGH.md` from your editor.
- Keep `evidence/*.json` available for hash verification.
- Do **not** depend on PowerPoint for this demonstration.

## Still blocked

Show `DEMO_EVIDENCE_MANIFEST.json` hashes and cite Wave 3 package paths from the examiner evidence README. The verbal centrepiece remains phase1-082 No × High.
