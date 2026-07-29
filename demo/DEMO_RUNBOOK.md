# Demo runbook

## One-command launch

From the repository root:

```powershell
python demo/launch_demo.py
```

Or from the `demo/` folder:

```powershell
python launch_demo.py
```

The launcher:

- checks required files;
- binds **127.0.0.1** only;
- picks a free port near 8765;
- opens the default browser when possible;
- prints the local URL.

Stop with **Ctrl+C**.

## Without launching a browser

```powershell
python demo/launch_demo.py --no-browser
```

Then open the printed `http://127.0.0.1:<port>/index.html` manually.

## Direct file open (fallback)

If the local server cannot start, open `demo/index.html` in Edge/Chrome.  
Case data is also embedded in `evidence_embed.js`, so interactive cases work without `fetch`
under `file://` when scripts are allowed. Printable fallback: `demo/print.html`.

## Offline requirements

- No internet.
- No API key.
- System fonts only.
- Evidence is frozen under `demo/evidence/` (SHA-256 in the footer hash panel and `DEMO_EVIDENCE_MANIFEST.json`).
