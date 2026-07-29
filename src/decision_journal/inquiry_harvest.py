"""Harvest inquiry document metadata into a manifest."""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from decision_journal.inquiry_client import InquiryFeedClient, default_filters, parse_meta

MANIFEST_FIELDS = [
    "inquiry_id",
    "title",
    "slug",
    "doc_category",
    "doc_type",
    "module",
    "published",
    "page_url",
    "pdf_url",
    "local_pdf",
    "local_txt",
    "text_chars",
    "selected_phase1",
    "selected_for_manual_annotation",
    "download_ok",
    "text_ok",
    "harvested_at",
]


def slugify_filename(slug: str) -> str:
    safe = re.sub(r"[^\w\-]+", "_", slug).strip("_")
    return safe[:120] or "document"


def post_matches(post: dict, rules: dict) -> bool:
    meta = parse_meta(post)
    module = meta.get("Module") or meta.get("Modules", "")
    doc_type = meta.get("Type", "")
    title = post.get("post_title") or ""

    modules = rules.get("modules") or []
    if modules and not any(m in module for m in modules):
        return False

    doc_types = rules.get("doc_types") or []
    if doc_types and doc_type not in doc_types:
        return False

    title_prefixes = rules.get("title_prefixes") or []
    if title_prefixes and not any(title.startswith(p) for p in title_prefixes):
        return False

    title_contains = rules.get("title_contains") or []
    if title_contains and not any(s in title for s in title_contains):
        return False

    return True


def record_from_post(post: dict, doc_category: str) -> dict[str, str]:
    meta = parse_meta(post)
    slug = post.get("post_name") or ""
    inquiry_id = str(post.get("ID") or "")
    return {
        "inquiry_id": inquiry_id,
        "title": post.get("post_title") or "",
        "slug": slug,
        "doc_category": doc_category,
        "doc_type": meta.get("Type", ""),
        "module": meta.get("Module") or meta.get("Modules", ""),
        "published": meta.get("Published", ""),
        "page_url": post.get("pretty_url") or post.get("guid") or "",
        "pdf_url": "",
        "local_pdf": "",
        "local_txt": "",
        "text_chars": "",
        "selected_phase1": "false",
        "selected_for_manual_annotation": "false",
        "download_ok": "false",
        "text_ok": "false",
        "harvested_at": datetime.now(timezone.utc).isoformat(),
    }


def resolve_pdf_url(client: InquiryFeedClient, page_url: str) -> str:
    if not page_url:
        return ""
    response = client._client.get(page_url)
    response.raise_for_status()
    return extract_pdf_url_from_html(response.text)


def extract_pdf_url_from_html(html: str) -> str:
    uploads = re.findall(
        r"(https://covid19\.public-inquiry\.uk/wp-content/uploads/[^\s\"']+\.pdf)",
        html,
        flags=re.IGNORECASE,
    )
    if uploads:
        return uploads[0]
    for match in re.findall(r'href="([^"]+\.pdf[^"]*)"', html, flags=re.IGNORECASE):
        if match.startswith("http"):
            return match
        if match.startswith("/"):
            return f"https://covid19.public-inquiry.uk{match}"
    return ""


def parse_detail_page(html: str, page_url: str, slug: str) -> dict[str, str]:
    title_match = re.search(r"<title>([^<]+)</title>", html, flags=re.IGNORECASE)
    title = title_match.group(1).strip() if title_match else slug
    title = re.sub(r"\s*-\s*UK Covid-19 Inquiry\s*$", "", title, flags=re.IGNORECASE)
    doc_type = ""
    module = ""
    published = ""
    for label, key in [("Type", "doc_type"), ("Module", "module"), ("Published", "published")]:
        m = re.search(rf"{label}:\s*([^<\n]+)", html, flags=re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            if label == "Type":
                doc_type = val
            elif label == "Module":
                module = val
            else:
                published = val
    return {
        "inquiry_id": slug,
        "title": title,
        "slug": slug,
        "doc_category": "document",
        "doc_type": doc_type,
        "module": module,
        "published": published,
        "page_url": page_url,
        "pdf_url": extract_pdf_url_from_html(html),
        "local_pdf": "",
        "local_txt": "",
        "text_chars": "",
        "selected_phase1": "true",
        "selected_for_manual_annotation": "false",
        "download_ok": "false",
        "text_ok": "false",
        "harvested_at": datetime.now(timezone.utc).isoformat(),
    }


def harvest_from_seeds(seeds_path: Path, client: InquiryFeedClient) -> list[dict[str, str]]:
    seeds = json.loads(seeds_path.read_text(encoding="utf-8"))
    records: list[dict[str, str]] = []
    for seed in seeds:
        slug = seed["slug"]
        page_url = f"https://covid19.public-inquiry.uk/documents/{slug}/"
        response = client._client.get(page_url)
        if response.status_code == 404:
            continue
        response.raise_for_status()
        record = parse_detail_page(response.text, page_url, slug)
        record["doc_category"] = seed.get("doc_category", "document")
        if seed.get("doc_type"):
            record["doc_type"] = seed["doc_type"]
        records.append(record)
    return records


def harvest_corpus(config: dict, client: InquiryFeedClient) -> list[dict[str, str]]:
    seen_ids: set[str] = set()
    records: list[dict[str, str]] = []

    seeds_path = config.get("seeds")
    if seeds_path:
        root = Path(config.get("_root", "."))
        seed_file = root / seeds_path if not Path(seeds_path).is_absolute() else Path(seeds_path)
        if seed_file.exists():
            for row in harvest_from_seeds(seed_file, client):
                key = row.get("slug") or row.get("inquiry_id")
                if key in seen_ids:
                    continue
                seen_ids.add(key)
                records.append(row)

    for source in config.get("sources", []):
        doc_category = source.get("doc_category", "document")
        post_types = source.get("post_types") or ["document"]
        search = source.get("search") or ""
        order = source.get("order") or "date-desc"
        max_pages = source.get("max_pages")
        rules = source.get("match") or {}

        filters = default_filters(post_types=post_types, search=search, order=order)
        for _page, _payload, posts in client.iter_posts(filters, max_pages=max_pages):
            for post in posts:
                inquiry_id = str(post.get("ID") or "")
                if not inquiry_id or inquiry_id in seen_ids:
                    continue
                if not post_matches(post, rules):
                    continue
                seen_ids.add(inquiry_id)
                records.append(record_from_post(post, doc_category))

    return records


def apply_phase1_selection(records: list[dict[str, str]], config: dict) -> None:
    phase1 = config.get("phase1") or {}
    if phase1.get("skip_reselection") and any(r.get("selected_phase1") == "true" for r in records):
        manual_slots = int(phase1.get("manual_annotation_slots", 3))
        selected = [r for r in records if r.get("selected_phase1") == "true"]
        for row in selected[:manual_slots]:
            if row.get("doc_type") == "Transcript":
                row["selected_for_manual_annotation"] = "true"
        return

    max_transcripts = int(phase1.get("max_transcripts", 8))
    max_reports = int(phase1.get("max_reports", 2))
    max_consultation = int(phase1.get("max_consultation_transcripts", 2))
    max_analysis = int(phase1.get("max_analysis", 2))
    manual_slots = int(phase1.get("manual_annotation_slots", 3))

    buckets = {
        "Transcript": max_transcripts,
        "Consultation Transcripts": max_consultation,
        "Analysis": max_analysis,
    }
    counts = {k: 0 for k in buckets}
    report_count = 0
    selected: list[dict[str, str]] = []

    def sort_key(row: dict[str, str]) -> tuple:
        return (row.get("published") or "", row.get("title") or "")

    for row in sorted(records, key=sort_key):
        if row.get("doc_category") == "report":
            if report_count < max_reports:
                row["selected_phase1"] = "true"
                selected.append(row)
                report_count += 1
            continue

        doc_type = row.get("doc_type") or ""
        limit = buckets.get(doc_type)
        if limit is None:
            continue
        if counts[doc_type] < limit:
            row["selected_phase1"] = "true"
            selected.append(row)
            counts[doc_type] += 1

    for idx, row in enumerate(selected[:manual_slots]):
        if row.get("doc_type") == "Transcript":
            row["selected_for_manual_annotation"] = "true"


def enrich_pdf_urls(records: list[dict[str, str]], client: InquiryFeedClient) -> None:
    for row in records:
        if row.get("pdf_url"):
            continue
        row["pdf_url"] = resolve_pdf_url(client, row.get("page_url", ""))


def write_manifest(records: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(records)


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_manifest_json(records: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, indent=2), encoding="utf-8")


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
