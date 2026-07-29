"""Download inquiry PDFs listed in the manifest."""

from __future__ import annotations

import csv
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

from decision_journal.inquiry_client import DEFAULT_HEADERS
from decision_journal.inquiry_harvest import MANIFEST_FIELDS, read_manifest, slugify_filename


def download_pdf(url: str, dest: Path, delay_seconds: float = 0.5) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with httpx.Client(headers=DEFAULT_HEADERS, timeout=120.0, follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()
        dest.write_bytes(response.content)
    time.sleep(delay_seconds)


def run_download(
    manifest_path: Path,
    *,
    raw_dir: Path,
    only_phase1: bool = True,
    limit: int | None = None,
    delay_seconds: float = 0.5,
) -> int:
    rows = read_manifest(manifest_path)
    downloaded = 0
    for row in rows:
        if only_phase1 and row.get("selected_phase1") != "true":
            continue
        if row.get("download_ok") == "true" and row.get("local_pdf"):
            pdf_path = Path(row["local_pdf"])
            if pdf_path.exists():
                continue
        pdf_url = row.get("pdf_url") or ""
        if not pdf_url:
            continue
        if limit is not None and downloaded >= limit:
            break

        category = row.get("doc_category") or "document"
        subdir = raw_dir / category
        filename = f"{slugify_filename(row.get('slug') or row.get('inquiry_id', 'doc'))}.pdf"
        dest = subdir / filename
        download_pdf(pdf_url, dest, delay_seconds=delay_seconds)
        row["local_pdf"] = str(dest.as_posix())
        row["download_ok"] = "true"
        downloaded += 1

    with manifest_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return downloaded
