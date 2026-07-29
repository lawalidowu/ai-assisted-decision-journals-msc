#!/usr/bin/env python3
"""Launch the offline examiner demo on localhost (stdlib only)."""
from __future__ import annotations

import argparse
import functools
import http.server
import socket
import socketserver
import sys
import threading
import time
import webbrowser
from pathlib import Path

DEMO_DIR = Path(__file__).resolve().parent
REQUIRED = [
    DEMO_DIR / "index.html",
    DEMO_DIR / "demo.css",
    DEMO_DIR / "demo.js",
    DEMO_DIR / "evidence_embed.js",
    DEMO_DIR / "DEMO_EVIDENCE_MANIFEST.json",
    DEMO_DIR / "evidence" / "phase1-016.json",
    DEMO_DIR / "evidence" / "phase1-082.json",
    DEMO_DIR / "evidence" / "phase1-090.json",
    DEMO_DIR / "evidence" / "phase1-246.json",
]


def check_files() -> None:
    missing = [str(p.relative_to(DEMO_DIR)) for p in REQUIRED if not p.is_file()]
    if missing:
        raise SystemExit(
            "Demo cannot start — required files missing:\n  - "
            + "\n  - ".join(missing)
            + "\nRun from the repository so demo/ is intact."
        )


def find_free_port(preferred: int) -> int:
    candidates = [preferred] + list(range(preferred + 1, preferred + 30))
    for port in candidates:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    raise SystemExit("No free localhost port found near the preferred port.")


class LocalHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch offline examiner demo (localhost only).")
    parser.add_argument("--port", type=int, default=8765, help="Preferred localhost port")
    parser.add_argument("--no-browser", action="store_true", help="Do not open a browser")
    args = parser.parse_args()

    check_files()
    port = find_free_port(args.port)
    handler = functools.partial(LocalHandler, directory=str(DEMO_DIR))

    # Bind localhost only — never a public interface
    try:
        httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
    except OSError as exc:
        raise SystemExit(f"Could not start local server on 127.0.0.1:{port}: {exc}") from exc

    url = f"http://127.0.0.1:{port}/index.html"
    print("Offline examiner demo")
    print(f"Serving: {DEMO_DIR}")
    print(f"URL:     {url}")
    print("Bind:    127.0.0.1 (localhost only)")
    print("Stop:    press Ctrl+C in this terminal")
    print("Frozen research artefact — no live model call")

    if not args.no_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        httpd.server_close()
        time.sleep(0.05)


if __name__ == "__main__":
    main()
