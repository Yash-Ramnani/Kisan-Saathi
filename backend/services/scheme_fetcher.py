"""
Government Scheme Fetcher - Aggregates live farmer schemes from official sites.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from html import unescape
from typing import Any
from urllib.parse import urljoin
import re

import requests

CACHE_TTL_MINUTES = 30
REQUEST_TIMEOUT = 15
MAX_RESULTS = 24

_SOURCE_URLS = [
    "https://www.india.gov.in/topics/agriculture",
    "https://www.myscheme.gov.in/",
    "https://www.myscheme.gov.in/search?query=farmer",
    "https://pmkisan.gov.in/",
    "https://agricoop.gov.in/en/schemes",
]

_KEYWORDS = [
    "scheme",
    "yojana",
    "kisan",
    "farmer",
    "agri",
    "agriculture",
    "pm-kisan",
    "pmkisan",
    "kcc",
    "fasal",
    "insurance",
    "subsidy",
    "credit",
    "soil",
    "irrigation",
    "fertilizer",
    "seed",
]

_ALLOWED_HOST_MARKERS = [
    ".gov.in",
    "india.gov.in",
    "myscheme.gov.in",
    "pmkisan.gov.in",
]

_cache: dict[str, Any] = {
    "fetched_at": None,
    "data": None,
}


def _is_government_url(url: str) -> bool:
    lower = url.lower()
    return any(marker in lower for marker in _ALLOWED_HOST_MARKERS)


def _clean_title(raw: str) -> str:
    text = unescape(re.sub(r"\s+", " ", raw or "")).strip()
    text = re.sub(r"^[|\-:>\s]+", "", text)
    return text


def _extract_links(html: str, base_url: str) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []

    # Match simple anchor tags without running heavy parsers.
    pattern = re.compile(
        r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
        flags=re.IGNORECASE | re.DOTALL,
    )

    for match in pattern.finditer(html):
        href = match.group(1).strip()
        title_html = match.group(2)
        title = _clean_title(re.sub(r"<[^>]+>", "", title_html))

        if not href or href.startswith("javascript:") or href.startswith("#"):
            continue

        full_url = urljoin(base_url, href)
        if not full_url.startswith("http"):
            continue

        if not _is_government_url(full_url):
            continue

        haystack = f"{title} {full_url}".lower()
        if not any(keyword in haystack for keyword in _KEYWORDS):
            continue

        if len(title) < 8:
            continue

        links.append(
            {
                "title": title,
                "url": full_url,
                "source": base_url,
            }
        )

    return links


def _dedupe_and_rank(items: list[dict[str, str]]) -> list[dict[str, str]]:
    seen_urls: set[str] = set()
    deduped: list[dict[str, str]] = []

    for item in items:
        url = item["url"].rstrip("/")
        if url in seen_urls:
            continue
        seen_urls.add(url)
        deduped.append(item)

    # Prefer links that look more scheme-specific.
    def score(item: dict[str, str]) -> int:
        value = (item["title"] + " " + item["url"]).lower()
        points = 0
        for key in ["scheme", "yojana", "kisan", "farmer", "pm-kisan", "subsidy"]:
            if key in value:
                points += 1
        return points

    deduped.sort(key=score, reverse=True)
    return deduped[:MAX_RESULTS]


def fetch_live_farmer_schemes(force_refresh: bool = False) -> dict[str, Any]:
    now = datetime.utcnow()

    if not force_refresh and _cache["fetched_at"] and _cache["data"]:
        expiry = _cache["fetched_at"] + timedelta(minutes=CACHE_TTL_MINUTES)
        if now < expiry:
            return _cache["data"]

    collected: list[dict[str, str]] = []
    source_status: list[dict[str, str]] = []

    headers = {
        "User-Agent": "Kisan-Saathi/1.0 (+https://localhost)",
    }

    for source in _SOURCE_URLS:
        try:
            response = requests.get(source, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            html = response.text
            extracted = _extract_links(html, source)
            collected.extend(extracted)
            source_status.append({"source": source, "status": "ok"})
        except Exception as exc:
            source_status.append({"source": source, "status": f"error: {exc}"})

    schemes = _dedupe_and_rank(collected)

    payload = {
        "fetched_at": now.isoformat() + "Z",
        "total_schemes": len(schemes),
        "sources_checked": source_status,
        "schemes": schemes,
    }

    _cache["fetched_at"] = now
    _cache["data"] = payload

    return payload


def get_scheme_context_for_ai(max_items: int = 8) -> str:
    data = fetch_live_farmer_schemes(force_refresh=False)
    schemes = data.get("schemes", [])[:max_items]

    if not schemes:
        return "No live scheme links available right now from configured government sources."

    lines = []
    for idx, item in enumerate(schemes, start=1):
        title = item.get("title", "Untitled Scheme")
        url = item.get("url", "")
        lines.append(f"{idx}. {title} - {url}")

    return "Current government scheme links for farmers:\n" + "\n".join(lines)
