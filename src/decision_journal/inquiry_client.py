"""HTTP client for the UK COVID-19 Inquiry document feed API."""

from __future__ import annotations

import json
import time
from typing import Any
from urllib.parse import urlencode

import httpx

FEED_URL = "https://covid19.public-inquiry.uk/wp-json/c19inquiry/v1/feed/"
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://covid19.public-inquiry.uk/documents/",
    "Cache-Control": "no-cache, no-store, must-revalidate",
}


def serialize_axios_params(obj: Any, prefix: str | None = None) -> list[tuple[str, str]]:
    """Match axios default query serialization for nested objects."""
    parts: list[tuple[str, str]] = []
    if isinstance(obj, dict):
        for key, val in obj.items():
            full = f"{prefix}[{key}]" if prefix else str(key)
            parts.extend(serialize_axios_params(val, full))
    elif isinstance(obj, list):
        for idx, val in enumerate(obj):
            parts.extend(serialize_axios_params(val, f"{prefix}[{idx}]"))
    elif isinstance(obj, bool):
        parts.append((prefix or "", "true" if obj else "false"))
    elif obj is None:
        parts.append((prefix or "", ""))
    else:
        parts.append((prefix or "", str(obj)))
    return parts


def build_feed_url(filters: dict[str, Any]) -> str:
    query = urlencode(serialize_axios_params({"data": filters}))
    return f"{FEED_URL}?{query}"


def default_filters(
    *,
    post_types: list[str] | None = None,
    search: str = "",
    page: int = 1,
    order: str = "date-desc",
    taxonomies: dict | None = None,
) -> dict[str, Any]:
    return {
        "taxonomies": taxonomies or {},
        "date_range_from": "",
        "date_range_to": "",
        "post_types": post_types or ["document"],
        "query_post_types": False,
        "search": search,
        "page": page,
        "order": order,
    }


def parse_meta(post: dict) -> dict[str, str]:
    meta: dict[str, str] = {}
    for item in post.get("meta", []):
        if isinstance(item, dict):
            meta.update({str(k): str(v) for k, v in item.items()})
    return meta


class InquiryFeedClient:
    def __init__(self, delay_seconds: float = 0.5, max_retries: int = 4) -> None:
        self.delay_seconds = delay_seconds
        self.max_retries = max_retries
        self._client = httpx.Client(headers=DEFAULT_HEADERS, timeout=60.0, follow_redirects=True)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> InquiryFeedClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def fetch_page(self, filters: dict[str, Any]) -> dict[str, Any]:
        url = build_feed_url(filters)
        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            if attempt:
                time.sleep(self.delay_seconds * (attempt + 1))
            try:
                response = self._client.get(url)
                if response.status_code == 403:
                    last_error = httpx.HTTPStatusError(
                        "Rate limited by CDN", request=response.request, response=response
                    )
                    continue
                response.raise_for_status()
                time.sleep(self.delay_seconds)
                return response.json()
            except httpx.HTTPError as exc:
                last_error = exc
        raise RuntimeError(f"Feed request failed after {self.max_retries} attempts: {last_error}")

    def iter_posts(
        self,
        filters: dict[str, Any],
        *,
        max_pages: int | None = None,
    ):
        page = int(filters.get("page", 1))
        pages_fetched = 0
        total_pages = 1
        while page <= total_pages:
            if max_pages is not None and pages_fetched >= max_pages:
                break
            payload = self.fetch_page({**filters, "page": page})
            total_pages = int(payload.get("total_pages") or 1)
            posts = payload.get("posts") or []
            yield page, payload, posts
            page += 1
            pages_fetched += 1
            if not posts:
                break
